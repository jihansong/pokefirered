from pathlib import Path
import json,hashlib,shutil,os,zipfile,datetime
r=Path('/workspaces/pokefirered');root=r/'work/regression-oct12';cand=root/'final-candidate';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
frozen=json.loads((cand/'baseline.json').read_text());expected={k:row['sha256'] for k,row in frozen['artifacts'].items()}
assert all(sha(p)==h for p,h in expected.items())
assert all(sha(p)==h for p,h in frozen['saves'].items())
reports={}
paths={'MistyAirport':root/'final-misty-native/misty-airport-result.json','MistyPallet':root/'final-pallet-legal-path/validation.json','ProfessorElm':root/'final-elm-native/validation.json','ContinuousFlightWalk':root/'final-johto-walk-observed/validation.json','ColdMapVisual':root/'final-native-visual/validation.json','AssetABI':cand/'final-binary-preservation-audit.json','ColdNurse':root/'final-cold-nurse-chain115/result.json','TohjoNatural':root/'final-tohjo-native-correct-cli/validation.json'}
for k,p in paths.items():
 j=json.loads(p.read_text());assert j.get('all_pass',j.get('pass')) is True,(k,j.get('error'));assert j.get('rom_sha256',j.get('candidate_rom_sha256'))=='2bafd6478fef5bbda56c6b4bec9c8dec1a4e0f060252fc219dbcc834411509f7';reports[k]={'path':str(p),'sha256':sha(p),'pass':True}
g=json.loads((root/'final-gates/result.json').read_text());assert g['original_all_saves_unchanged'];assert all(v['exit_code']==0 for v in g['checks'] if v['check']!='event-wiring-global-existing')
assert (root/'final-gates/event-wiring-global-existing.log').read_bytes()==(r/'outputs/regions-q9-review-v1/required-gates-phase5/event-wiring.log').read_bytes()
assert sha(r/'pokemonthyl.gba')==frozen['main_sha256']
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');delivery=r/('outputs/rom-johto-misty-repair-'+stamp);delivery.mkdir(exist_ok=False);rollback=delivery/'rollback-q8';rollback.mkdir()
old={}
for ext in ['gba','elf','sym','map']:
 p=r/('pokemonthyl.'+ext);old[str(p)]=sha(p);q=rollback/p.name;shutil.copy2(p,q);assert sha(q)==old[str(p)]
for ext in ['gba','elf','sym','map']:
 p=cand/('pokemonthyl-oct12-repair.'+ext);q=delivery/('pokemonthyl.'+ext);shutil.copy2(p,q);assert sha(q)==expected[str(p)]
statuspath=r/'work/animation-recreation-status.json';shutil.copy2(statuspath,rollback/statuspath.name)
raw=(delivery/'pokemonthyl.gba').read_bytes();assert len(raw)==33554432 and raw[0xac:0xb0]==b'BPGE'
manifest={'created_utc':stamp,'scope':'Oct12 Johto and Misty regression repair; whole Johto/Hoenn campaign remains incomplete','gba_sha256':sha(delivery/'pokemonthyl.gba'),'files':{p.name:{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in delivery.glob('pokemonthyl.*')},'original_q8_files':old,'rollback_path':str(rollback),'evidence':reports,'gates':g,'known_global_event_findings':96,'global_event_findings_identical_to_previous_candidate':True,'all_original_saves_unchanged':True,'user_save_rewritten':False,'approved_assets_preserved':24,'professor_art':'Temporary Scientist sprite, named Elm dialog verified','user_reported_initial_tile_failure_reproduced':False,'Delta_device_tested':False,'BadEgg_original_repaired':False,'whole_regions_complete':False,'source_basis':'Current working Q9 sources plus Oct12 source repairs; not a full-campaign release'}
readme='''Thunder Yellow 2026-10-12 repair
Changes: Misty invitation after Oak/national-dex events and airport fallback; persistent decline/manual join; named Professor Elm dialogue and report continuity; MtMortar General+RockTunnel tileset pairing.
Validated on native mGBA: actual airplane + continuous walk airport->Route29->NewBark->ElmLab; Elm 4 branches; Misty airport 4 and Pallet 2 branches including native SAVE/cold load; original 8 saves load identically; all 14 original/backup saves untouched; title/opening/Rocket 24 approved assets and existing save layout preserved.
This is a regression repair. Full Johto/Hoenn story, 96 preexisting event-wiring findings, Misty allied battle, original Bad Egg recovery, and actual DELTA device performance remain incomplete/unverified.
The reported airport/town tile corruption was not reproduced in the verified main Q8 or this candidate. Exact player ROM/startup condition still needs confirmation.
Preserve original .sav and Save States. Use the game's CONTINUE with an existing battery .sav to match the tested startup path. Old ROM Save State compatibility is not established. This download contains no player save.
'''
(delivery/'READ-ME.txt').write_text(readme,encoding='utf-8')
(delivery/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Stage exact four-file replacement; swap GBA last and restore all four if any step fails.
staged={}
try:
 for ext in ['elf','sym','map','gba']:
  q=r/('pokemonthyl.'+ext+'.oct12-staged');assert not q.exists();shutil.copy2(delivery/('pokemonthyl.'+ext),q);assert sha(q)==sha(delivery/('pokemonthyl.'+ext));staged[ext]=q
 for ext in ['elf','sym','map','gba']:os.replace(staged[ext],r/('pokemonthyl.'+ext))
 assert all(sha(r/('pokemonthyl.'+e))==sha(delivery/('pokemonthyl.'+e)) for e in ['gba','elf','sym','map'])
 assert all(sha(p)==h for p,h in frozen['saves'].items())
except Exception:
 for ext in ['elf','sym','map','gba']:shutil.copy2(rollback/('pokemonthyl.'+ext),r/('pokemonthyl.'+ext))
 raise
j=json.loads(statuspath.read_text());j['updated_at']=stamp;j['current_rom']={'path':str(r/'pokemonthyl.gba'),'sha256':manifest['gba_sha256'],'bytes':33554432,'provenance':str(delivery/'provenance.json'),'verified_delivery_folder':str(delivery)}
j['johto_misty_repair_20261012']={'status':'SCOPED_REPAIR_PROMOTED','evidence':reports,'main_rom_sha256':manifest['gba_sha256'],'original_saves_unchanged':True,'first_four_maps_native_visual_pass':True,'actual_flight_continuous_walk_to_professor_pass':True,'user_tile_failure_reproduced':False,'whole_Johto_Hoenn_story_complete':False,'existing_global_event_findings':96,'temporary_Elm_graphic':True,'BadEgg_original_repaired':False}
for key in ['regional_candidate','regional_next_candidate']:
 if isinstance(j.get(key),dict):j[key].update(status='SCOPED_OCT12_REPAIR_PROMOTED_FULL_CAMPAIGN_INCOMPLETE',misty_native_retest_pending=False,main_rom_unchanged_q8=False,current_repair_provenance=str(delivery/'provenance.json'),all_regions_complete=False)
if isinstance(j.get('q9_validation_checkpoint'),dict):j['q9_validation_checkpoint'].update(historical_checkpoint=True,superseded_by_current_rom_sha256=manifest['gba_sha256'])
statuspath.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
public=root/'deliverables';public.mkdir(exist_ok=True)
zipname='pokemonthyl-oct12-repair.zip'
with zipfile.ZipFile(public/zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in ['pokemonthyl.gba','READ-ME.txt','provenance.json']:z.write(delivery/name,name)
shutil.copy2(delivery/'pokemonthyl.gba',public/'pokemonthyl-oct12-repair.gba')
receipt={'promoted':True,'delivery':str(delivery),'current_sha256':sha(r/'pokemonthyl.gba'),'rollback':str(rollback),'download_zip':str(public/zipname),'download_gba':str(public/'pokemonthyl-oct12-repair.gba'),'original_all_saves_unchanged':all(sha(p)==h for p,h in frozen['saves'].items())}
(root/'promotion-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
