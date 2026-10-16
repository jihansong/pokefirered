#!/usr/bin/env python3
"""Read-only health/identity audit of an existing native capture SAV artifact."""
import argparse,hashlib,json,pathlib,struct
from savefile import SaveFile
from gamedata import const,off
p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('--species',required=True);p.add_argument('--result');p.add_argument('--case')
a=p.parse_args();beforepath=pathlib.Path(a.before).resolve();afterpath=pathlib.Path(a.after).resolve()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
originals={path:digest(path) for path in (beforepath,afterpath)}
before=SaveFile(str(beforepath));after=SaveFile(str(afterpath));expected=const('SPECIES_'+a.species.upper());new=[]
assert off('pokemon')==100 and len(before.blocks['storage'])==len(after.blocks['storage'])==33744
assert 0<=before.party_count()<=after.party_count()<=6
if after.party_count()==before.party_count()+1:
 slot=before.party_count();m=after.party_mon(slot);raw=bytes(m.blk[m.o:m.o+100]);new.append(('party',slot,m,raw))
else:assert after.party_count()==before.party_count()
start=off('storage.boxes');count=const('TOTAL_BOXES_COUNT')*const('IN_BOX_COUNT')
for slot in range(count):
 b=bytes(before.blocks['storage'][start+slot*80:start+(slot+1)*80]);r=bytes(after.blocks['storage'][start+slot*80:start+(slot+1)*80])
 if not b[19]&2 and r[19]&2:
  from savefile import Mon
  m=Mon(bytearray(r),0);new.append(('pc',slot,m,r))
assert len(new)==1,('expected exactly one newly acquired slot',[(x[0],x[1]) for x in new])
where,slot,m,raw=new[0];subs=m.subs();calc=sum(v[0] for sub in subs.values() for v in struct.iter_unpack('<H',sub))&65535
stored=struct.unpack_from('<H',raw,28)[0]
assert calc==stored,'captured BoxPokemon checksum mismatch'
assert raw[19]&2 and not(raw[19]&1),'captured Bad Egg or missing hasSpecies bit'
assert not(raw[19]&4) and not m.is_egg(),'captured wild Pokemon has Egg flag'
assert m.species()==expected,('captured species',m.species(),expected)
ot=struct.unpack_from('<I',after.sb2,off('sb2.playerTrainerId'))[0]
assert m.otid==ot,('captured OT differs from player',m.otid,ot)
assert struct.unpack_from('<I',before.sb2,off('sb2.playerTrainerId'))[0]==ot,'player ID changed across capture'
proof=None
if a.result:
 assert a.case,'select an exact native capture case when binding proof'
 resultpath=pathlib.Path(a.result).resolve();originals[resultpath]=digest(resultpath);result=json.loads(resultpath.read_text())
 row=next(v for v in result['cases'] if v.get('case')==a.case)
 assert pathlib.Path(row['save']['qa_save']).resolve()==afterpath,'native result does not name audited SAV'
 assert row.get('native_capture') is True and row.get('outcome')==7,'not a successful native capture proof'
 assert row['forced_memory_writes']==row['forced_battle_outcomes']==0
 proof={'case':a.case,'rom_sha256':result['rom_sha256'],'save_sectors':row['save']['checksummed_sectors'],'cold_reload_proof':'existing native flash_reload compared full party600B plus PC/dex/flags; this auditor does not run an emulator'}
assert all(digest(path)==h for path,h in originals.items()),'audited file changed'
print(json.dumps({'pass_all':True,'before_sha256':originals[beforepath],'after_sha256':originals[afterpath],
 'location':where,'slot_zero_based':slot,'species_internal':m.species(),'pid':m.personality,'ot_id':m.otid,'player_ot_id':ot,
 'checksum_stored':stored,'checksum_calculated':calc,'bad_egg':False,'egg':False,'box80_sha256':hashlib.sha256(raw[:80]).hexdigest(),
 'party100_sha256':hashlib.sha256(raw).hexdigest() if where=='party' else None,'native_proof':proof,
 'read_only':True,'other_rom_save_state_tested':False,'original_damaged_box_repaired':False}),flush=True)
