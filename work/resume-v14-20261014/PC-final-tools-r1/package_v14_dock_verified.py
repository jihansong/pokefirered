"""Package only hash-bound, native-verified dock fix and the unchanged v1.4 sync."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, zipfile

ROM = 'af2677993a75979fb36f0768c390d1bad7424e61f2d569b5054d40702250d2e8'
ELF = '2549852a48935c680e06e81719b54663b9c0efa7fdaccd31d1f4683886c5d64e'
SAV = 'c06ad0536f1ee13fd88a3cf36346b52d3d5ca0cae7e729723acf6047d916feb8'
SOURCE = '32f46c05aa5b606f924eb0b0ed4bdefc08b8025e4ff63e5f970cc8ec75b99ec4'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--root', type=Path, required=True)
    a.add_argument('--dock-report', type=Path, required=True)
    a.add_argument('--expect-dock-sha', required=True)
    x = a.parse_args(); r = x.root.resolve(); dockpath = x.dock_report.resolve()
    assert dockpath.is_relative_to(r) and sha(dockpath) == x.expect_dock_sha
    assert sha(r/'pokemonthyl.gba') == ROM and sha(r/'pokemonthyl.elf') == ELF
    assert sha(r/'saves/pokemonthyl_v1.4-synced.sav') == '99f4100d09961196706282a02e96ee9017a0a591777aa3ca0b40249ec8ae89e8'
    savpath=r/'work/resume-v14-20261014/PC-final-tools-r1/pokemonthyl_v1.4-recovered-PCsorted.sav'
    assert sha(savpath) == SAV
    assert sha(r/'saves/pokemonthyl_v1.4.sav') == SOURCE
    originals = {str(p.relative_to(r)): sha(p) for p in (r/'saves').rglob('*') if p.is_file()}
    dock = read(dockpath)
    assert dock['pass'] and dock['status'] == 'complete'
    assert dock['native_old_and_new_dock_escape_verified']
    assert dock['protected_original_inputs_unchanged']
    assert dock['entire_party_bytes_preserved'] and dock['PC_33744_bytes_preserved']
    assert dock['story_items_Hoenn_flags_vars_preserved']
    assert dock['native_SAVE_cold']['counter'] == [74,75]
    assert dock['native_SAVE_cold']['checksummed_sectors'] == 14
    assert not dock['Brawly_completed'] and not dock['full_Hoenn_campaign_tested']
    assert all(dock[k] == 0 for k in ['RAM_writes','direct_script_calls','forced_battle_outcomes'])
    assert len(dock['boat_menus']) == 2 and all(v['actual_keys'] for v in dock['boat_menus'])
    nativepath = r/'work/resume-v14-20261014/native-v14-recovered-r1/validation.json'
    native = read(nativepath)
    assert native['pass_all'] and native['status'] == 'complete'
    assert native['ROM_sha256'] == ROM and native['ELF_sha256'] == ELF
    assert native['original_SAV_sha256'] == SAV and native['all_original_inputs_unchanged']
    assert all(native[k] == 0 for k in ['preboot_fixture_edits','RAM_writes','state_loads','direct_engine_calls'])
    assert native['initial_load_exact']['SaveBlock1'] and native['initial_load_exact']['PC']
    assert native['stages'][-1]['counter'] == [78,79]
    pcproof=read(r/'work/resume-v14-20261014/PC-final-tools-r1/PC-recovered-independent-validation.json')
    assert pcproof['status']=='FINAL_PC_RECOVERED_SORTED_INDEPENDENT_AUDIT_PASS'
    assert pcproof['candidate_sha256']==SAV and pcproof['all_28_sector_checksums_valid']
    assert pcproof['active_healthy_records']==138 and pcproof['invalid_PC_records_in_both_banks']==0
    assert pcproof['entire_candidate_matches_independently_constructed_expected_file']
    assert pcproof['entire_SB1_SB2_party_bag_PP_IV_dex_story_location_unchanged']
    assert pcproof['original_and_prior_sync_SAV_unchanged']
    ui = read(r/'work/resume-v14-20261014/regional-ui-native-r2/validation.json')
    assert ui['pass_all'] and ui['all_original_inputs_unchanged']
    assert not ui['all_three_regions_tested'] and not ui['full_campaign_tested']
    obs = read(r/'work/resume-v14-20261014/dex-scroll-observe-r1/validation.json')
    assert obs['pass_all'] and obs['original_inputs_unchanged'] and obs['protected_player_records_preserved']
    now = datetime.datetime.now(datetime.timezone.utc)
    kst = now.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    out = r/'outputs/v14-sync-dockfix-20261014'; out.mkdir(exist_ok=False)
    old = r/'outputs/v14-sync-20261014'
    copies = {
        'pokemonthyl_v1.4.gba': r/'pokemonthyl.gba',
        'pokemonthyl_v1.4.sav': savpath,
        'native-v14-new-ROM-validation.json': nativepath,
        'native-dock-validation.json': dockpath,
        'regional-UI-validation-baseline.json': r/'work/resume-v14-20261014/regional-ui-native-r2/validation.json',
        'dex-scroll-observation-baseline.json': r/'work/resume-v14-20261014/dex-scroll-observe-r1/validation.json',
        'edit-manifest.json': old/'edit-manifest.json',
        'physical-PC-recovery-edit-manifest.json': r/'work/resume-v14-20261014/PC-final-tools-r1/v14-recovered-PCsorted-edit-manifest.json',
        'physical-PC-independent-validation.json': r/'work/resume-v14-20261014/PC-final-tools-r1/PC-recovered-independent-validation.json',
        'BadEgg-inferred-minimal-repair-spec.json': r/'work/resume-v14-20261014/PC-final-tools-r1/lickitung-inferred-minimal-repair-spec.json',
        'independent-raw-audit.json': old/'independent-raw-audit.json',
        'BadEgg-forensic-report.json': old/'BadEgg-forensic-report.json',
        'v14-actual-cold-continue.png': old/'v14-actual-cold-continue.png',
        'Dewford-safe-land-actual.png': dockpath.parent/'04-new-dock-walks-onto-land.png',
    }
    for name,p in copies.items():
        assert p.is_file(), str(p)
        shutil.copyfile(p,out/name)
        assert sha(out/name) == sha(p)
    readme = f'''Thunder Yellow v1.4 sync + verified Dewford dock fix
Created UTC: {now.isoformat()}
Created Korea time: {kst.isoformat()}
ZIP display timestamps are explicitly written in Korea time; ZIP itself has no timezone field.

Use pokemonthyl_v1.4.gba with the included pokemonthyl_v1.4.sav.
Original saves/pokemonthyl_v1.4.sav and previous sync99f4100d are preserved.
The SAV c06ad053 reapplies physical PC sorting and opens BOX1 instead of BOX5.
It repairs the remaining damaged Lickitung in both banks using the unique plausible minimum-bit model.
All other Pokemon records match99f4. The deployed copy is saves/pokemonthyl_v1.4-synced-recovered.sav.
The GBA is newer (af267799...).
In DELTA, import the battery save and use the game's CONTINUE. An older Save State may replace these edits.

Confirmed: v1.4 native CONTINUE/SAVE/cold restart (counter78 to79), party/PC/dex/story preserved;
old stranded Dewford counter74 automatically resumes on land, actual boat roundtrip/new land arrival,
native SAVE/cold restart (counter74 to75), all original user saves unchanged.
The supplied SAV is the user's synced v1.4; no QA progression SAV is substituted.

Save edits: Master Ball/Rare Candy/TinyMushroom/PP UP 99; prior player-owned doubled IVs retained,
not doubled again. Dragonair evolved to Dragonite with its retained IVs. Healthy PC entries sorted
by National number and duplicate level. Authenticated Lapras restoration; healthy Togepi egg preserved.
Lickitung is reconstructed as Lv39/EXP59319 by reversing one primary bit plus engine Bad Egg markings.
Its original checksum30838, identity, IVs/EVs, moves, PP and capture data are preserved. No checksum masking.
There is no healthy same-identity donor, so this is an inferred reconstruction within a single-bit model,
not a donor-authenticated exact-original restoration. Multi-bit corruption/checksum collisions remain possible.
Both banks contain zero invalid PC Pokemon records after recovery; the healthy Togepi egg is preserved.
Bad Egg corruption's exact DELTA Save State cause is not proven without that State/matching ROM.

Regional UI and scroll evidence use the preserved pre-dock ROM0845. Current v1.4 is Kanto-unlocked;
no Johto/Hoenn story flags were forced. All three regions/full campaign/physical DELTA FPS remain unverified.
Brawly progression is not certified by the dock-only test. Previous actual QA battle loss is preserved.
Only the dock scripts and their importer mirrors changed in this GBA; existing art and save layout remain.
'''
    (out/'README.txt').write_text(readme,encoding='utf-8')
    files = {p.name:sha(p) for p in out.iterdir() if p.is_file()}
    release = dict(status='V14_SYNC_AND_NATIVE_DOCK_FIX_PASS',created_utc=now.isoformat(),
        created_korea=kst.isoformat(),ZIP_display_timezone='Asia/Seoul',
        original=dict(path='saves/pokemonthyl_v1.4.sav',sha256=SOURCE),
        synced_sav=str(r/'saves/pokemonthyl_v1.4-synced-recovered.sav'),synced_sha256=SAV,
        ROM_sha256=ROM,ELF_sha256=ELF,files=files,unresolved_bad_records=0,
        Lickitung_recovery='Inferred unique minimum-bit model; exact original not donor authenticated',
        full_campaign_complete=False,DELTA_device_FPS_measured=False,
        dock_native_pass=True,v14_new_ROM_native_save_cold_pass=True,
        regional_UI_observed_on_preserved_baseline=True,Brawly_progression_tested=False)
    (out/'release.json').write_text(json.dumps(release,indent=2)+'\n')
    z = out/'Thunder-Yellow-v1.4-dockfix-20261014.zip'
    stamp = tuple(kst.timetuple()[:6])
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as q:
        for p in sorted(out.iterdir()):
            if p == z or not p.is_file(): continue
            info=zipfile.ZipInfo(p.name,date_time=stamp);info.compress_type=zipfile.ZIP_DEFLATED
            q.writestr(info,p.read_bytes())
    assert all((r/p).exists() and sha(r/p)==h for p,h in originals.items())
    promoted=r/'saves/pokemonthyl_v1.4-synced-recovered.sav';assert not promoted.exists()
    shutil.copyfile(savpath,promoted);assert sha(promoted)==SAV
    statuspath=r/'work/animation-recreation-status.json';statusbackup=out/'status-before-dockfix.json'
    shutil.copyfile(statuspath,statusbackup);status=read(statuspath)
    status['previous_verified_ROM_before_dockfix']=status.get('current_rom')
    status['previous_save_current_before_PC_resort']=status.get('save_current')
    status['save_current']=dict(path=str(promoted),sha256=SAV,source_original='saves/pokemonthyl_v1.4.sav',
        source_sha256=SOURCE,native_SAVE_cold_PASS=True,unresolved_bad_records=0,
        Lickitung_inferred_recovery=True,healthy_PC_count=138,
        PC_physical_sort_reapplied=True,PC_current_box_1based=1)
    status['current_rom']=dict(path=str(r/'pokemonthyl.gba'),sha256=ROM,bytes=(r/'pokemonthyl.gba').stat().st_size,
        provenance=str(out/'release.json'),verified_delivery_folder=str(out))
    status['v14_dockfix_release_20261014']={**release,'ZIP_path':str(z),'ZIP_sha256':sha(z),
        'protected_save_files':len(originals),'old_verified_package_preserved':str(old)}
    status['hoenn_dewford_20261014']=dict(status='NATIVE_DOCK_FIX_PASS',report=str(dockpath),
        report_sha256=sha(dockpath),Brawly_progression_complete=False,full_Hoenn_campaign_complete=False)
    status['regional_dex_native_ui_20261014']=dict(status=ui['status'],report=str(r/'work/resume-v14-20261014/regional-ui-native-r2/validation.json'),
        ROM_sha256=ui['ROM_sha256'],all_three_regions_tested=False)
    status['dex_scroll_observation_20261014']=dict(status='READ_ONLY_UI_OBSERVED',report=str(r/'work/resume-v14-20261014/dex-scroll-observe-r1/validation.json'),
        hardware_frames=1080,observed_key_heartbeat_anomalies=3,DELTA_device_FPS_measured=False,product_patch_written=False)
    statuspath.write_text(json.dumps(status,indent=2,ensure_ascii=False)+'\n')
    export=r/'outputs/resume-v14-input-20261014'/z.name;assert not export.exists()
    shutil.copyfile(z,export);assert sha(export)==sha(z)
    print(json.dumps(dict(status=release['status'],ZIP=str(z),ZIP_sha256=sha(z),ZIP_bytes=z.stat().st_size,
        ROM_sha256=ROM,SAV_sha256=SAV,created_utc=now.isoformat(),created_korea=kst.isoformat()),indent=2))

if __name__ == '__main__': main()
