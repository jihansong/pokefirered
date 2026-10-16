from pathlib import Path
import json,hashlib,shutil,datetime,os
r=Path('/workspaces/pokefirered');o=r/'outputs/blackthorn-review-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
new={'gba':'111d4e1ae7e6572845e5eb31ed33a1216fff8aa3d3e11466f287b74419abe682','elf':'1540cd67af00365cf8212a91cc147ef120365d51deeaf7626546687f529e4d43','sym':'6d5ea01e8b421b5625625b2ec562002fd2c0440043869430f5e384207d058929','map':'5e4d6e9572bb197c58750a0da0baf39b1292511638a4bd31ad019c65a388f197'}
old={'gba':'f3b4e13df998d1832544218a88cd0c4845a9b7ebd184628e00c1e9595434204c','elf':'fcffe85e76e5404f15e552fa84ca18f91e883c0a0613b2678e7ceb27e4d42e47','sym':'122cad2ba9d871f54b838734e7ede1466685960a1bcddfa5ac7c6d9b55a8b5f8','map':'810567524b2ac8c4fd40f74c7faf55d9ab2821cf84c0fb3cdda3fa7eb4816848'}
for ext,h in new.items():assert sha(o/('pokemonthyl-blackthorn-lg-isolated.'+ext))==h
for ext,h in old.items():assert sha(r/('pokemonthyl.'+ext))==h
raw=(o/'pokemonthyl-blackthorn-lg-isolated.gba').read_bytes();assert len(raw)==33554432 and raw[0xAC:0xB0]==b'BPGE'
run=json.loads((o/'native-q8-lg-run.json').read_text());assert run['all_pass'] and run['original_saves_unchanged'] and run['main_not_replaced'] and run['candidate_sha256']==new['gba'] and len(run['results'])==41
expected_names={'events','battles','maps','chain','habitat'}|{'waterfall-'+s for s in ['a','menu','no-badge-a','no-badge-menu','kanto-only-a','kanto-only-menu','hoenn-only-a','hoenn-only-menu']}|{'fly-'+s for s in ['town-blackthorn_city','town-blackthorn_badge8','town-locked-blackthorn','town-all-visited']}|{'hm-'+who+'-'+state for who in ['wanda','dad','flash'] for state in ['fresh','bag','pc','history','done','full-retry']}|{'hm-'+s for s in ['wanda-before-open','wanda-referral','dad-before-wally','dad-before-norman','dad-badge-only','dad-trainer-only']}
assert {x['name'] for x in run['results']}==expected_names
proofs=[]
for row in run['results']:
 assert row['exit']==0
 p=o/('native-lg-'+row['name'])/('validation.json' if row['name'].startswith(('hm-','fly-','waterfall-')) else 'result.json');d=json.loads(p.read_text());assert d.get('all_pass',d.get('pass')) is True and d['rom_sha256']==new['gba'],str(p)
 assert d.get('original_files_unchanged',d.get('original_saves_unchanged',d.get('original_saves_preserved'))) is True,str(p)
 proofs.append(str(p.relative_to(o)))
for name,count,key in [('events',25,'cases'),('battles',7,'cases'),('maps',24,'cases'),('chain',16,'stages'),('habitat',3,'cases')]:assert len(json.loads((o/('native-lg-'+name)/'result.json').read_text())[key])==count
wild=json.loads((o/'native-lg-wild-rtc/result.json').read_text());assert wild['all_pass'] and wild['original_files_unchanged'] and wild['rom_sha256']==new['gba'] and len(wild['native_cases'])==8 and len(wild['compiled_table_checks'])==18 and wild['forced_game_memory_writes']==0
proofs.append('native-lg-wild-rtc/result.json')
audit=json.loads((o/'native-lg-binary-preservation-audit.json').read_text());assert audit['pass'] and audit['candidate_rom_sha256']==new['gba'] and audit['candidate_elf_sha256']==new['elf'] and audit['approved_asset_count']==24 and audit['save_layout_unchanged'] and audit['original_v12_save_unchanged'] and audit['main_rom_unchanged']
sv=r/'saves/pokemonthyl_v1.2.sav';assert sha(sv)=='73733902ec36e7ec13fc74d734c773b66077620d63febe1399cae9f759ef6a85';originals={str(p):sha(p) for p in (r/'saves').glob('*.sav')};assert shutil.disk_usage(r).free>250000000
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');delivery=r/'outputs'/('rom-regions-update-q8-'+stamp);delivery.mkdir();backup=delivery/'previous-main';backup.mkdir()
for ext in new:
 shutil.copy2(r/('pokemonthyl.'+ext),backup/('pokemonthyl.'+ext));shutil.copy2(o/('pokemonthyl-blackthorn-lg-isolated.'+ext),delivery/('pokemonthyl.'+ext))
shutil.copy2(sv,delivery/'pokemonthyl.sav')
provenance={'new_main':new,'previous_main':old,'candidate':str(o),'delivery':str(delivery),'native_cases':119,'compiled_wild_tables':18,'evidence':proofs,'binary_preservation_evidence':str(o/'native-lg-binary-preservation-audit.json'),'johto_maps':112,'johto_badges':8,'league_not_yet_integrated':True,'same_native_save_chain_stages':16,'approved_media':{'opening':'v7','title':'v8','rocket':'v11','distinct_asset_payloads_unchanged':24},'save_structs_and_sector_layout_unchanged':True,'original_saves':originals,'user_save_copied_without_editing':True,'qa_progress_not_written_to_original_user_save':True,'existing_bad_egg_repaired':False,'full_three_region_campaign_complete':False,'delta_real_device_fps_measured':False}
(delivery/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
try:
 for ext in new:
  temp=r/('pokemonthyl.'+ext+'.q8-new');shutil.copy2(delivery/('pokemonthyl.'+ext),temp);os.replace(temp,r/('pokemonthyl.'+ext))
 for ext,h in new.items():assert sha(r/('pokemonthyl.'+ext))==h
except Exception:
 for ext in old:shutil.copy2(backup/('pokemonthyl.'+ext),r/('pokemonthyl.'+ext))
 raise
assert originals=={p:sha(Path(p)) for p in originals};p=r/'work/animation-recreation-status.json';s=json.loads(p.read_text());shutil.copy2(p,delivery/'status-before.json');s['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();s['current_rom']={'path':str(r/'pokemonthyl.gba'),'sha256':new['gba'],'bytes':33554432,'provenance':str(delivery/'provenance.json'),'verified_delivery_folder':str(delivery)}
s['regions'].update(status='PARTIAL_NATIVE_VERIFIED_NOT_WHOLE_CAMPAIGN_COMPLETE',johto='Main ROM: 112 maps, badges 1-8 including Blackthorn/Clair/DragonDen; independent Johto League remains',hoenn_next='HM03/04/05 chapter-gated sharing integrated; Route110/119 rival and Weather Institute bridge prerequisite prepared, not applied',main_rom_sha256=new['gba'])
s['radio_tower_current_rom'].update(main_rom_sha256=new['gba'],blackthorn_and_league_pending=False,league_pending=True)
s['blackthorn_current_rom']={'native_pass':True,'maps_added':11,'johto_maps':112,'johto_badges':8,'native_cases':119,'compiled_wild_tables':18,'RTC_game_clock_UI_tested':True,'main_rom_sha256':new['gba'],'proof_folder':str(o)}
s['hm_alternate_current_rom'].update(Hoenn_HM03='TM03 when received in Kanto or already bag/PC; Wanda reunion prerequisite',Hoenn_HM04='TM08 when received in Kanto or already bag/PC; Norman and Wally prerequisites',Hoenn_HM05='TM70 when received in Kanto or already bag/PC; Granite Cave prerequisite',Blackthorn_HM07='TM50 when already obtained; Clair/DragonDen elder trial prerequisite',q8_native_cases=24,all_hm_recipients_complete=False)
rem=s['regional_story_remaining'];rem.update(johto_maps_integrated=112,johto_native_story_through_badge=8,johto_fly_towns_integrated=10,johto_next='Route27/Tohjo/Route26/VictoryRoad/Johto Indigo League prepared, native validation pending',hoenn_next='Route110/119 May/Brendan reconnection and Weather Institute bridge gate; full natural story traversal',three_region_natural_playthrough_complete=False,full_three_region_campaign_verified=False)
rem['remaining']=['Independent Johto League and natural Kanto-Johto-Hoenn whole-campaign traversal','Route110/119 Hoenn rivals and Weather Institute bridge prerequisite','Misty post-champion companion, N continuity and space expansion','Three separate final regional ending movies; DELTA real-device frame timing','Original boxed Bad Egg identity recovery and old DELTA Save State cause reproduction']
s['regional_candidate']={'status':'NEXT_GENERATORS_AND_QA_STAGED_NOT_APPLIED','johto_league':'tools/johto/build_johto_league.py','hoenn_rival':'work/patch_hoenn_rival_110_119_v1.py','misty':'tools/companion/build_misty.py','planned_johto_maps':124}
s['regional_next_candidate']={'status':'Q8_PROMOTED_NEXT_Q9_SOURCE_PREPARED','main_rom_sha256':new['gba']}
s['endings']['johto_native_profile']={'status':'PROFILE_IN_MAIN_MANUAL_PREVIEW_NOT_LEAGUE_DISPATCH','region_mode':1,'scene_count':13,'league_clear_dispatch_pending':True,'full_native_capture_pending':True,'bespoke_final_film_complete':False}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');(r/'work/current-regions-release-path.txt').write_text(str(delivery)+'\n')
with (r/'work/regional-integration-progress.jsonl').open('a') as f:f.write(json.dumps({'time':s['updated_at'],'event':'Q8_MAIN_PROMOTED_BLACKTHORN_AND_GATED_HM','main_sha256':new['gba'],'delivery':str(delivery),'native_cases':119,'wild_tables':18,'original_saves_unchanged':True,'all_regions_complete':False})+'\n')
result={'pass':True,'root_four_files_match':True,'main_rom_sha256':new['gba'],'delivery':str(delivery),'native_cases':119,'compiled_wild_tables':18,'original_saves_unchanged':True,'title_v8_rocket_v11_opening_v7_preserved':True,'whole_regions_complete':False};(delivery/'promotion-result.json').write_text(json.dumps(result,indent=2)+'\n');print('Q8_PROMOTED',json.dumps(result),flush=True)
