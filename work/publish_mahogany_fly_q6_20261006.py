from pathlib import Path
import hashlib,json,datetime,shutil,os
r=Path('/workspaces/pokefirered');q=r/'outputs/mahogany-east-gate-fixed-review-v1';q5=r/'outputs/mahogany-fly-capacity-review-v1';old=r/'outputs/rom-regions-update-20261005T191140Z'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'gba':'ab47fb761ae2d93e0008c98172f9dee4e89bd034037efa9abef2d86b436f6f81','elf':'584f0b0f22574a06f1e00d78815bf95fe6f00681814089fd0767edfa0619ec3d','sym':'0046cb1bdf61cd2b2d2452b5829c2ef0abf973f4d07a710ca9e834eee9d6cfb7','map':'383689e0ab29733a52aa1e776e5bdd2b8298c533d8e02994a4fc77ac2415f395'}
previous={'gba':'6185cd53db214dd18cf8229726633f75a455353bfc202ac6d88c127477a6ca19','elf':'18f46287e0b1152dfc4aa100f656d1e80bdd5c0e14df5607d3ecb8bb4b9a5666','sym':'83a6c7d78c3e8ba442e1fb00088712f62a8ab0e4dcde4231e2ccabacfcb3607c','map':'038d3e5135eb841ab3c102a71c9bbbad62a1995319fb2ba8fea671eb60f47e42'}
for ext,h in expected.items():assert sha(q/('pokemonthyl.'+ext))==h
for ext,h in previous.items():assert sha(r/('pokemonthyl.'+ext))==h
sv=r/'saves/pokemonthyl_v1.2.sav';assert sha(sv)=='73733902ec36e7ec13fc74d734c773b66077620d63febe1399cae9f759ef6a85';saves={str(p):sha(p) for p in (r/'saves').rglob('*.sav')}
evidence={}
def proof(root,rel):
 p=root/rel;d=json.loads(p.read_text());assert d.get('pass',d.get('all_pass',d.get('pass_all',False))),(rel,'failed')
 assert d['rom_sha256']==(expected['gba'] if root==q else '6df50d9dd6a4b859f086f38264e915cc88ed620889fd28137f4d2fdbfd1d80b7')
 evidence[str(p)]={'sha256':sha(p),'rom_sha256':d['rom_sha256']};return d
events=proof(q,'mahogany-events/result.json');battles=proof(q,'mahogany-battles/result.json');static=proof(q,'mahogany-static/result.json');chain=proof(q,'mahogany-chain/result.json');fly=proof(q,'mahogany-fly-results.json');performance=proof(q,'performance/result.json')
assert len(events['cases'])==32 and len(battles['cases'])==11 and len(static['cases'])==10 and len(chain['stages'])==15 and len(fly['cases'])==4
assert chain['same_native_save_chain'] and chain['qa_position_only_warps']==15 and chain['original_files_unchanged']
assert chain['forced_story_flags_after_initial_fixture']==chain['forced_trainer_flags_after_initial_fixture']==chain['forced_memory_writes']==chain['forced_battle_outcomes']==0
assert chain['stages'][0]['save']['counter'][0]==60 and chain['stages'][-1]['save']['counter'][1]==75
assert all(s['save']['checksummed_sectors']==14 for s in chain['stages'])
assert performance['workload_count']==4 and performance['party_pc_dex_preserved'] and performance['regional_story_trainer_flags_preserved'] and performance['ram_pokes_original']==0 and not performance['actual_device_fps_measured']
raw=[]
for line in (q/'performance-measurement-run.log').read_text().splitlines():
 try:d=json.loads(line)
 except ValueError:continue
 if 'land_performance' in d:raw.append(d['land_performance'])
assert len(raw)==4 and all(s['pass_all'] and s['hardware']==s['vblank']==s['callbacks']==s['visible_frames']==360 and s['missed']==0 and not s['irregular'] and s['follower_objects']==s['follower_tasks']==1 and s['party_pc_dex_preserved'] for s in raw)
audit=json.loads((q/'native-binary-preservation-audit.json').read_text());assert audit['rom_sha256']==expected['gba'] and audit['elf_sha256']==expected['elf'] and audit['save_layout_unchanged'] and audit['original_v12_save_unchanged']
assert len(audit['approved_assets_unchanged'])==21 and len(audit['additional_title_assets_unchanged'])==19 and len(audit['rom_resident_sections_match'])==10
assert audit['additional_title_assets_unchanged']['PikachuVoice_Title']['sha256']=='aa35fbe68154fe5118ed6b298f18d8c1785d9a06c2109d54f1e818092719c9e6'
assert audit['additional_title_assets_unchanged']['sThunderYellowStartRoiTiles']['sha256']=='65f31390c8c1065dc28a3ea36a2990a8c351cd121d4be5c3e2f2d17c266d1e33'
maplinks=proof(q5,'mahogany-map-links/result.json');assert len(maplinks['cases'])==28
legacy_paths=['legacy-fly-kanto/validation.json','legacy-fly-hoenn/validation.json','legacy-fly-layoutfix-sevii123/validation.json','legacy-fly-layoutfix-sevii45/validation.json','legacy-fly-layoutfix-sevii67/validation.json']
for rel in legacy_paths:proof(q5,rel)
leaguepath=q/'league-route-final/validation.json';league=proof(q,str(leaguepath.relative_to(q)));assert league['ram_writes']==league['forced_battle_outcomes']==0 and league['original_saves_unchanged']
groups=json.loads((r/'data/maps/map_groups.json').read_text());johto=next(v for v in groups.values() if isinstance(v,list) and 'MahoganyTown' in v);assert len(johto)==94
now=datetime.datetime.now(datetime.timezone.utc);dest=r/'outputs'/('rom-regions-update-'+now.strftime('%Y%m%dT%H%M%SZ'));dest.mkdir(exist_ok=False);backup=dest/'previous-main';backup.mkdir()
for ext in expected:
 shutil.copy2(r/('pokemonthyl.'+ext),backup/('pokemonthyl.'+ext));shutil.copy2(q/('pokemonthyl.'+ext),dest/('pokemonthyl.'+ext))
shutil.copy2(sv,dest/'pokemonthyl.sav');assert sha(dest/'pokemonthyl.sav')==sha(sv)
statusp=r/'work/animation-recreation-status.json';shutil.copy2(statusp,backup/'animation-recreation-status.before.json');pointer=r/'work/current-regions-release-path.txt'
if pointer.exists():shutil.copy2(pointer,backup/'current-regions-release-path.before.txt')
prior=json.loads((old/'provenance.json').read_text())
remaining=['Johto RadioTower7maps prepared but not in this ROM; Route44/IcePath/Blackthorn/Clair/DragonDen/League','Hoenn duplicate-HM rewards at several original NPCs and legacy Brawly/Wattson badge resume prepared but not in this ROM','Complete three-region campaign, three separate final regional ending movies, DELTA real-device frame timing','Original existing boxed Bad Egg identity recovery and old DELTA Save State cause reproduction']
release={'time_utc':now.isoformat(),'rom_sha256':expected['gba'],'elf_sha256':expected['elf'],'bytes':33554432,'files':{e:{'sha256':h,'bytes':(q/('pokemonthyl.'+e)).stat().st_size} for e,h in expected.items()},'previous_provenance':str(old/'provenance.json'),'previous_provenance_sha256':sha(old/'provenance.json'),'previous_rom_sha256':previous['gba'],'evidence_root':str(q),'native_validations':evidence,'new_native_cases':63,'same_save_chain_stages':15,'same_save_chain_counter':[60,75],'reused_q5_map_links':28,'reused_q5_legacy_fly_regions':5,'legacy_fly_destinations_verified':44,'reuse_scope':'q5 map geometry and selected-region Fly logic unchanged in q6; the only product change since q5 was EastGate TEMP0 consumption and its generator synchronization, verified by q6 native events. Prior results retain their original q5 hash.','title_version':'v8','rocket_version':'v11','opening_version':'v7','approved_assets_unchanged':audit['approved_assets_unchanged'],'additional_title_assets_unchanged':audit['additional_title_assets_unchanged'],'save_layout_unchanged':True,'save_layout':audit['save_layout'],'rom_resident_sections_match':audit['rom_resident_sections_match'],'johto_maps_integrated':94,'johto_story_verified_through_badge':7,'johto_fly_towns_integrated':9,'mahogany_chapter':{'gyarados_lance_hq_pryce':True,'events':32,'trainer_outcomes':11,'static_outcomes':10,'position_only_QA_warps':15,'natural_whole_campaign_verified':False},'performance':dict(performance,raw_samples=raw),'hoenn_league_approach_native_verified':True,'save_delivery':str(dest/'pokemonthyl.sav'),'save_sha256':sha(sv),'original_save_progress_not_modified':True,'all_original_saves_unchanged':True,'known_existing_bad_egg_repaired':False,'full_johto_story_complete':False,'full_hoenn_story_complete':False,'full_three_region_campaign_verified':False,'remaining':remaining,'visual_limits':prior.get('visual_review',{}),'failed_attempts_retained':True}
(dest/'provenance.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
(dest/'README-ko.txt').write_text('성도 황토마을·분노의 호수·로켓단 기지·류옹 7번째 배지까지 추가했습니다. 성도 누적94맵/공중날기9도시. 관문 반복 이벤트 수정, 성도53개 이벤트·전투·고정포켓몬 검증과 동일 세이브15단계 저장을 통과했습니다. 새 공중날기4건·성능4표본·호연 원본 트레이너 자동 전투와 동굴 출구→리그 입구를 검증했습니다. 타이틀v8·로이로사v11·오프닝v7과 세이브 구조는 보존했습니다. pokemonthyl.sav는 사용자 원본 v1.2의 그대로인 복사본이며 진행을 강제 완료하지 않았습니다. 방송국 이후 성도 후반·호연 누락 보상·세 지역 전체 자연 진행·3개 별도 엔딩·DELTA 실기 성능은 미완료입니다. 기존 Bad Egg는 아직 복원되지 않았습니다.\n')
assert saves=={str(p):sha(p) for p in (r/'saves').rglob('*.sav')}
for ext,h in previous.items():assert sha(r/('pokemonthyl.'+ext))==h
for ext,h in expected.items():
 t=r/('pokemonthyl.'+ext+'.q6.tmp');assert not t.exists();shutil.copy2(dest/('pokemonthyl.'+ext),t);assert sha(t)==h;os.replace(t,r/('pokemonthyl.'+ext))
status=json.loads(statusp.read_text());status['updated_at']=now.isoformat();status['current_rom']={'path':str(r/'pokemonthyl.gba'),'sha256':expected['gba'],'bytes':33554432,'provenance':str(dest/'provenance.json'),'verified_delivery_folder':str(dest)}
status['regional_candidate']={'path':str(q/'pokemonthyl.gba'),'sha256':expected['gba'],'promoted_to_main':True,'new_native_cases':63,'full_regions_complete':False}
s=status.setdefault('regional_story_remaining',{});s.update(johto_maps_integrated=94,johto_native_story_through_badge=7,johto_fly_towns_integrated=9,mahogany='ROM integrated: 13 maps, 32events, 11trainer, 10static, sameSAV15stages60-75; Gate TEMP0 once fix',johto_next='RadioTower7maps source and QA preparation, then Route44/IcePath/Blackthorn/Clair/DragonDen/League',hoenn_next='Original HM rewards and legacy gym badge resume; whole-story natural traversal',full_three_region_campaign_verified=False,remaining=remaining,owners={'johto':'johto_resume','hoenn':'dive_hm_resume','performance':'performance_resume'})
status.setdefault('performance_current',{})['mahogany']={'cases':4,'hardware_frames_per_case':360,'processing_misses':0,'single_follower':True,'evidence_root':str(q),'delta_device_fps_measured':False}
t=statusp.with_suffix('.q6.tmp');t.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n');os.replace(t,statusp);pointer.write_text(str(dest)+'\n')
with (r/'work/regional-integration-progress.jsonl').open('a') as f:f.write(json.dumps({'time_utc':now.isoformat(),'event':'mahogany-fly-native-main-ROM-update','rom_sha256':expected['gba'],'delivery':str(dest),'new_native_cases':63,'original_save_unchanged':True,'full_regions_complete':False})+'\n')
assert saves=={str(p):sha(p) for p in (r/'saves').rglob('*.sav')}
for ext,h in expected.items():assert sha(r/('pokemonthyl.'+ext))==h
receipt={'pass':True,'main_rom_sha256':expected['gba'],'delivery':str(dest),'original_save_sha256':sha(sv),'backup':str(backup),'johto_maps_integrated':94,'johto_story_through_badge':7,'full_regions_complete':False};(dest/'promotion-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Q6_MAIN_PROMOTED',json.dumps(receipt),flush=True)
