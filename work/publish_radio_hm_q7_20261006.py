import pathlib,json,hashlib,shutil,datetime,os
r=pathlib.Path('/workspaces/pokefirered');candidate=r/'outputs/radio-tower-review-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
new={'gba':'f3b4e13df998d1832544218a88cd0c4845a9b7ebd184628e00c1e9595434204c','elf':'fcffe85e76e5404f15e552fa84ca18f91e883c0a0613b2678e7ceb27e4d42e47','sym':'122cad2ba9d871f54b838734e7ede1466685960a1bcddfa5ac7c6d9b55a8b5f8','map':'810567524b2ac8c4fd40f74c7faf55d9ab2821cf84c0fb3cdda3fa7eb4816848'}
old={'gba':'ab47fb761ae2d93e0008c98172f9dee4e89bd034037efa9abef2d86b436f6f81','elf':'584f0b0f22574a06f1e00d78815bf95fe6f00681814089fd0767edfa0619ec3d','sym':'0046cb1bdf61cd2b2d2452b5829c2ef0abf973f4d07a710ca9e834eee9d6cfb7','map':'383689e0ab29733a52aa1e776e5bdd2b8298c533d8e02994a4fc77ac2415f395'}
for ext,digest in new.items():assert sha(candidate/('pokemonthyl.'+ext))==digest
for ext,digest in old.items():assert sha(r/('pokemonthyl.'+ext))==digest
assert (candidate/'pokemonthyl.gba').stat().st_size==33554432
radio=json.loads((candidate/'native-radio-run.json').read_text());hm=json.loads((candidate/'native-hoenn-hm-native-retry-run.json').read_text());audit=json.loads((candidate/'native-binary-preservation-audit.json').read_text())
assert radio['all_pass'] and radio['original_files_unchanged'] and radio['rom_sha256']==new['gba']
assert {v['name']:v['cases'] for v in radio['cases']}=={'events':35,'battles':12,'maps':16,'chain':21}
for v in radio['cases']:
 d=json.loads(pathlib.Path(v['result']).read_text());assert v['exit']==0 and v['pass'] and d['all_pass'] and d['original_files_unchanged'] and d['rom_sha256']==new['gba']
assert hm['all_pass'] and hm['original_saves_unchanged'] and hm['main_unchanged'] and len(hm['cases'])==18 and hm['rom_sha256']==new['gba']
for v in hm['cases']:
 d=json.loads((pathlib.Path(v['output'])/'validation.json').read_text());assert v['pass'] and v['exit']==0 and d['pass'] and d['original_saves_unchanged']
assert audit['rom_sha256']==new['gba'] and audit['elf_sha256']==new['elf'] and audit['save_layout_unchanged'] and audit['original_v12_save_unchanged'] and len(audit['approved_assets_unchanged'])==21 and len(audit['additional_title_assets_unchanged'])==19 and len(audit['rom_resident_sections_match'])==10
save=r/'saves/pokemonthyl_v1.2.sav';assert sha(save)=='73733902ec36e7ec13fc74d734c773b66077620d63febe1399cae9f759ef6a85'
originals={str(p):sha(p) for p in (r/'saves').glob('*.sav')};assert shutil.disk_usage(r).free>250000000
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');delivery=r/'outputs'/('rom-regions-update-q7-'+stamp);delivery.mkdir();backup=delivery/'previous-main';backup.mkdir()
for ext in new:
 shutil.copy2(r/('pokemonthyl.'+ext),backup/('pokemonthyl.'+ext));shutil.copy2(candidate/('pokemonthyl.'+ext),delivery/('pokemonthyl.'+ext))
shutil.copy2(save,delivery/'pokemonthyl.sav')
proof={'current_rom':new,'previous_main':old,'delivery_folder':str(delivery),'candidate_folder':str(candidate),'native_checks':{'radio_events':35,'radio_battles':12,'radio_map_links':16,'same_save_chain_stages':21,'hoenn_reward_cases':18,'total':102},'approved_media_assets_unchanged':21,'additional_title_assets_unchanged':19,'save_layout_unchanged':True,'original_saves':originals,'native_radio_source_counter_chain':[75,96],'qa_story_progress_not_copied_to_user_save':True,'save_file_copied_without_editing':True,'opening_version':'v7','title_version':'v8','rocket_version':'v11','johto_maps':101,'johto_badges':7,'whole_regions_complete':False,'old_bad_egg_repaired':False,'misty_n_space_added_to_scope_not_implemented':True,'evidence':{'radio':'native-radio-run.json','hm':'native-hoenn-hm-native-retry-run.json','binary':'native-binary-preservation-audit.json'}}
(delivery/'provenance.json').write_text(json.dumps(proof,indent=2)+chr(10))
try:
 for ext in new:
  temp=r/('pokemonthyl.'+ext+'.q7-new');shutil.copy2(delivery/('pokemonthyl.'+ext),temp);os.replace(temp,r/('pokemonthyl.'+ext))
 for ext,digest in new.items():assert sha(r/('pokemonthyl.'+ext))==digest
except Exception:
 for ext in old:shutil.copy2(backup/('pokemonthyl.'+ext),r/('pokemonthyl.'+ext))
 raise
assert originals=={p:sha(pathlib.Path(p)) for p in originals}
p=r/'work/animation-recreation-status.json';s=json.loads(p.read_text());s['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();s['current_rom']={'path':str(r/'pokemonthyl.gba'),'sha256':new['gba'],'bytes':33554432,'provenance':str(delivery/'provenance.json'),'verified_delivery_folder':str(delivery)}
s['regions'].update(status='PARTIAL_NATIVE_VERIFIED_NOT_WHOLE_CAMPAIGN_COMPLETE',johto='Main ROM: 101 maps, badges 1-7, Radio Tower rescue; Blackthorn and League remain',hoenn_next='HM03/04/05 chapter-gated sharing staged, May/Brendan Route110/119 reconnection pending',main_rom_sha256=new['gba'])
s['radio_tower_current_rom']={'native_pass':True,'maps_added':7,'checks':84,'same_native_save_chain':[75,96],'blackthorn_and_league_pending':True,'main_rom_sha256':new['gba']}
s['hm_alternate_current_rom']['Hoenn_HM01']='TM31 if HM already received in Kanto or held in bag/PC';s['hm_alternate_current_rom']['Hoenn_HM06']='TM23 if HM already received in Kanto or held in bag/PC';s['hm_alternate_current_rom']['legacy_brawly_wattson_badge_reward_resume']=True;s['hm_alternate_current_rom']['q7_native_cases']=18;s['hm_alternate_current_rom']['all_hm_recipients_complete']=False
s['regional_candidate']={'status':'NEXT_SOURCE_STAGED_NOT_APPLIED','planned_johto_maps':112,'blackthorn_generator':'tools/johto/build_blackthorn.py','gated_hm_generator':'work/patch_hoenn_shared_hm_gated_v1.py','johto_credits_profile':'tools/animation/prepare_johto_native_credits.py'}
s['endings']['hoenn_native_review']={'status':'NATIVE_CAPTURE_VERIFIED','folder':'outputs/ending-hoenn-native-v1','frames':15742,'duration_seconds':263.563682556,'original_frlg_music':True,'bespoke_storyboard_film_complete':False,'capture_fixture_not_whole_story_walkthrough':True}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+chr(10));(r/'work/current-regions-release-path.txt').write_text(str(delivery)+chr(10))
with (r/'work/regional-integration-progress.jsonl').open('a') as f:f.write(json.dumps({'time':s['updated_at'],'event':'Q7_MAIN_PROMOTED_102_NATIVE_CHECKS','main_sha256':new['gba'],'delivery':str(delivery),'original_saves_unchanged':True,'all_regions_complete':False})+chr(10))
result={'pass':True,'root_four_files_match':True,'main_rom_sha256':new['gba'],'delivery':str(delivery),'native_checks':102,'original_saves_unchanged':True,'title_v8_rocket_v11_opening_v7_preserved':True,'whole_regions_complete':False};(delivery/'promotion-result.json').write_text(json.dumps(result,indent=2)+chr(10));print('Q7_PROMOTED',json.dumps(result),flush=True)
