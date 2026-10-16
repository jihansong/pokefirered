"""Actual Continue/SAVE/cold Continue of the updated v1.4 battery copy.

No fixture, state load, RAM write, forced script or story progression. The
original battery file is protected. This does not certify a full campaign.
"""
from pathlib import Path
import argparse, ast, hashlib, json, os, struct, sys, traceback

parser = argparse.ArgumentParser()
for name in ('root', 'rom', 'elf', 'sav', 'out', 'abi-json'):
    parser.add_argument('--' + name, type=Path, required=True)
parser.add_argument('--expect-sav-sha', required=True)
cfg = parser.parse_args()
root = cfg.root.resolve(strict=True)
os.chdir(root)
rom, elf, sav, out, abi = [getattr(cfg, n).resolve() for n in ('rom', 'elf', 'sav', 'out', 'abi_json')]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert out.is_relative_to(root / 'work') and not out.exists()
expected = json.loads(abi.read_text())
assert sha(rom) == expected['rom_sha256'] and sha(elf) == expected['elf_sha256']
assert sha(sav) == cfg.expect_sav_sha
for rel, digest in expected['source_sha256'].items():
    assert sha(root / rel) == digest, ('Stale ABI dependency', rel)
out.mkdir(parents=True)
protected = {p.resolve(): sha(p) for p in set((root / 'saves').rglob('*.sav')) | {rom, elf, sav, abi}}
sys.path.insert(0, str(root / 'tools/qa'))
import gamedata as gd
gd.CACHE = str(out / 'compiler-cache')
gd._OFFSETS = None
bootstrap = root / 'tools/qa/johto_violet_native_bootstrap_v1.py'
assert sha(bootstrap) == '83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb'
text = bootstrap.read_text()
assert text.count('\nresults=[]\n') == 1
sys.argv = ['v14-save', '--rom', str(rom), '--elf', str(elf), '--sav', str(sav), '--out', str(out)]
scope = {'__name__': 'definitions_only', '__file__': str(bootstrap)}
exec(compile(text.split('\nresults=[]\n')[0], '<verified-save-definitions>', 'exec'), scope)
Emu, SaveFile, Mon, Blocks, checksum, off, const, syms, settle, native_save = [scope[n] for n in
    ('ReadOnlyEmu', 'SaveFile', 'Mon', 'Blocks', 'checksum', 'off', 'const', 'syms', 'settle', 'native_save')]
# Old helper defines a fixture; refuse every direct RAM/engine method too.
def forbidden(*args, **kwargs):
    raise AssertionError('No fixture or direct engine call permitted')
scope['fixture'] = forbidden
assert off('pokemon') == 100 and off('boxmon') == 80 and off('storage') == 33744
report = dict(pass_all=False, scope='v1.4 actual Continue, idle, native SAVE and cold Continue',
              original_SAV_sha256=cfg.expect_sav_sha, ROM_sha256=sha(rom), ELF_sha256=sha(elf),
              preboot_fixture_edits=0, RAM_writes=0, state_loads=0, direct_engine_calls=0,
              full_campaign_tested=False, DELTA_device_FPS_measured=False, stages=[])
e = None

def snapshot(emu):
    sb1 = emu.read(emu.ptr('gSaveBlock1Ptr'), off('sb1'))
    sb2 = emu.read(emu.ptr('gSaveBlock2Ptr'), off('sb2'))
    b = Blocks(sb1, sb2)
    party = emu.read(emu.sym('gPlayerParty'), 600)
    count = emu.u8(emu.sym('gPlayerPartyCount'))
    pc = emu.read(emu.ptr('gPokemonStoragePtr'), off('storage'))
    assert count <= 6
    for i in range(count):
        m = Mon(bytearray(party), i * 100)
        total = sum(x[0] for sub in m.subs().values() for x in struct.iter_unpack('<H', sub)) & 65535
        assert total == struct.unpack_from('<H', party, i * 100 + 28)[0]
        assert not party[i * 100 + 19] & 1
    return {'party': party, 'count': count, 'pc': pc,
            'flags': sb1[off('sb1.flags'):off('sb1.vars')],
            'vars': sb1[off('sb1.vars'):off('sb1.vars') + const('VARS_COUNT') * 2],
            'dex': [b.dex_state(i) for i in range(1, 387)],
            'location': sb1[:12], 'sb1': sb1, 'sb2': sb2}

def compact(s):
    return {k: (hashlib.sha256(v).hexdigest() if isinstance(v, bytes) else v)
            for k, v in s.items() if k not in ('sb1', 'sb2')}

def invariant(a, b):
    for k in ('party', 'count', 'pc', 'flags', 'vars', 'dex', 'location'):
        assert a[k] == b[k], ('Native save changed', k)

try:
    e = Emu(str(rom), str(sav), sym='')
    e.syms = syms
    e.boot_continue()
    settle(e)
    before = snapshot(e)
    e.shot(str(out / 'v14-continue.png'), scale=4)
    e.run(180)
    assert e.field_idle()
    after_idle = snapshot(e)
    invariant(before, after_idle)
    report['stages'].append({'stage': 'Continue-and-idle', 'pass': True, 'snapshot': compact(before)})
    counters = native_save(e)
    assert counters == (78, 79), counters
    live = snapshot(e)
    invariant(before, live)
    e.run(30)
    e.lib.qa_close(e.h)
    e.h = None
    stored = SaveFile(e.sav_path)
    assert stored.counter == 79
    for _, sid, size in stored.layout:
        pos = stored.where[sid] * 4096
        assert checksum(stored.raw[pos:pos + size]) == struct.unpack_from('<H', stored.raw, pos + 0xff6)[0]
    assert len(stored.layout) == 14
    assert bytes(stored.blocks['storage']) == live['pc']
    assert bytes(stored.sb1[off('sb1.playerParty'):off('sb1.playerParty') + 600]) == live['party']
    assert stored.party_count() == live['count']
    assert [stored.dex_state(i) for i in range(1, 387)] == live['dex']
    q = out / 'v14-save-cold-native-QA-only.sav'
    q.write_bytes(Path(e.sav_path).read_bytes())
    e.h = e.lib.qa_open(str(rom).encode(), str(e.sav_path).encode())
    assert e.h
    e.boot_continue()
    settle(e)
    cold = snapshot(e)
    invariant(live, cold)
    e.shot(str(out / 'v14-cold-continue.png'), scale=4)
    report['stages'].append({'stage': 'native-SAVE-cold-Continue', 'pass': True,
                             'counter': list(counters), 'checksummed_sectors': 14,
                             'qa_save': str(q), 'qa_save_sha256': sha(q), 'snapshot': compact(cold)})
    report.update(pass_all=True, status='complete')
except Exception as error:
    report.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    if e and e.h:
        e.shot(str(out / 'failure.png'), scale=4)
finally:
    if e:
        e.close()
    unchanged = all(sha(p) == h for p, h in protected.items())
    report['all_original_inputs_unchanged'] = unchanged
    assert unchanged
    (out / 'validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: report.get(k) for k in ('pass_all', 'status', 'error', 'all_original_inputs_unchanged')}))
sys.exit(0 if report['pass_all'] else 1)
