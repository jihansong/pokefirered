from pathlib import Path
import hashlib,json,re,struct,shutil,datetime,os
r=Path('/workspaces/pokefirered');q=r/'outputs/ecruteak-wallace-review-v2';old=r/'outputs/rom-regions-update-20261005T163907Z';p=json.loads((old/'provenance.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
rom=(q/'pokemonthyl.gba').read_bytes(); elf=(q/'pokemonthyl.elf').read_bytes()
assert sha(rom)=='c139724c9b8d94a1195cb0386ced634a0012377f2ee7f3e86b6267259cf8068b'
assert sha(elf)=='2e187bd051b902ab268d718c5cc02f9b32b16f99c0f81f8d1a88a425282855a3'
assert sha((r/'pokemonthyl.gba').read_bytes())==p['rom_sha256']
def symbols(path):
 d={}
 for line in path.read_text().splitlines():
  x=line.split()
  if len(x)==4:
   try:d[x[3]]=(int(x[0],16),int(x[2],16))
   except ValueError:pass
 return d
s=symbols(q/'pokemonthyl.sym');so=symbols(old/'pokemonthyl.sym');ro=(old/'pokemonthyl.gba').read_bytes()
def at(name,data=rom,syms=s):
 a,n=syms[name];assert 0x08000000<=a<0x0a000000
 return data[a-0x08000000:a-0x08000000+n]
def lz(b):
 assert b[0]==16;n=int.from_bytes(b[1:4],'little');i=4;o=bytearray()
 while len(o)<n:
  flag=b[i];i+=1
  for bit in range(7,-1,-1):
   if len(o)>=n:break
   if flag&(1<<bit):
    a,c=b[i:i+2];i+=2;length=(a>>4)+3;disp=((a&15)<<8|c)+1
    assert disp<=len(o)
    for _ in range(length):o.append(o[-disp])
   else:o.append(b[i]);i+=1
 return bytes(o[:n])
assets={}
for name,expected in p['assets'].items():
 b=at(name)
 if name in ('gTrainerFrontPic_JessieJames','gTrainerPalette_JessieJames'):b=lz(b)
 assert len(b)==expected['bytes'] and sha(b)==expected['sha256'],name
 assets[name]={'bytes':len(b),'sha256':sha(b)}
extra={}
for name in s.keys()&so.keys():
 if re.search(r'Title.*(Tile|Pal|Map|Frame|Bolt|Lightning)|Pika.*Voice',name,re.I) and s[name][1]>0 and 0x08000000<=s[name][0]<0x0a000000:
  b=at(name);bo=at(name,ro,so)
  if b==bo:extra[name]={'bytes':len(b),'sha256':sha(b)}
  elif name.startswith(('s','gGraphics')):raise AssertionError(('title asset changed',name))
layout={'blocks':{name:s[name][1] for name in p['save_layout']['blocks']}}
assert layout['blocks']==p['save_layout']['blocks']
b=at('sSaveSlotLayout');pairs=[list(x) for x in struct.iter_unpack('<HH',b)]
assert pairs==p['save_layout']['sector_layout'] and sha(b)==p['save_layout']['sector_layout_sha256']
layout.update(sector_layout=pairs,sector_layout_sha256=sha(b))
h=struct.unpack_from('<16sHHIIIIIHHHHHH',elf);sections=[]
for i in range(h[12]):
 x=struct.unpack_from('<IIIIIIIIII',elf,h[6]+i*h[11]);typ,flags,addr,off,n=x[1:6]
 if flags&2 and typ!=8 and n and 0x08000000<=addr<0x0a000000:
  assert rom[addr-0x08000000:addr-0x08000000+n]==elf[off:off+n],('section mismatch',i)
  sections.append({'index':i,'bytes':n})
assert sections


validations={}
def load(rel):
 path=q/rel;j=json.loads(path.read_text());assert j['rom_sha256']==sha(rom),rel
 validations[rel]={'path':str(path),'sha256':sha(path.read_bytes())};return j
events=load('ecruteak-events/result.json');assert len(events['cases'])==31 and events['original_files_unchanged']
assert all(x['pc_party_preserved'] and x['save']['checksummed_sectors']==14 and x['forced_memory_writes']==x['forced_battle_outcomes']==0 for x in events['cases'])
battles=load('ecruteak-battles/result.json');assert battles['all_pass'] and battles['case_count']==9 and battles['original_files_unchanged']
assert all(x['pc_preserved'] and x['save']['checksummed_sectors']==14 and x['forced_memory_writes']==x['forced_battle_outcomes']==0 for x in battles['cases'])
wild=load('ecruteak-wild-rerun/result.json');assert wild['all_pass'] and len(wild['cases'])==4 and wild['original_files_unchanged']
assert all(x['pc_preserved'] and x['save']['checksummed_sectors']==14 and x['forced_memory_writes']==x['forced_battle_outcomes']==0 for x in wild['cases'])
chain=load('ecruteak-chapter-chain/chapter-chain-result.json');assert chain['pass_all'] and len(chain['sequence'])==5 and chain['native_save_cold_reopens']==5 and chain['original_files_unchanged']
assert chain['forced_story_flags_after_setup']==chain['forced_trainer_flags_after_setup']==chain['forced_memory_writes']==chain['forced_battle_outcomes']==0
assert '26/26 cases passed' in (q/'ecruteak-map-links-run.log').read_text()
performance=load('ecruteak-performance/result.json');assert performance['pass_all'] and performance['party_pc_dex_preserved'] and performance['ram_pokes_original']==0
samples=[]
for line in (q/'ecruteak-performance-run.log').read_text().splitlines():
 try:j=json.loads(line)
 except ValueError:continue
 if 'land_performance' in j:samples.append(j['land_performance'])
assert len(samples)==4 and all(x['pass_all'] and x['hardware']==x['vblank']==x['callbacks']==x['visible_frames']==360 and x['missed']==0 and not x['irregular'] and x['follower_objects']==x['follower_tasks']==1 and x['party_pc_dex_preserved'] for x in samples)
habitat=load('habitat-pages/result.json');assert habitat['pass_all'] and habitat['select_cycle'] and len(habitat['pages'])==3 and habitat['negative_egg_regions']==3
compiled_wild=json.loads((q/'wild-header-regions-run.log').read_text());assert compiled_wild['pass_all'] and compiled_wild['rom_sha256']==sha(rom) and compiled_wild['tables']==3 and compiled_wild['headers_per_table']==274
capture=json.loads((q/'capture-identity-audit.json').read_text());assert capture['pass_all'] and capture['native_proof']['rom_sha256']==sha(rom) and not capture['bad_egg'] and not capture['egg'] and capture['checksum_stored']==capture['checksum_calculated'] and capture['ot_id']==capture['player_ot_id']
wallace_names=['wallace-'+x+'-rerun' for x in ['first','bag','pc','history','done','early','storm','legacy','full-retry']]
water_names=['waterfall-a','waterfall-no-rain-a','waterfall-no-move-a','waterfall-menu-native-option-rerun']+['waterfall-'+x+'-native-option-rerun' for x in ['no-rain-menu','kanto-badge','kanto-rain-only','johto-badge','johto-rain-only']]
for name in wallace_names+water_names:
 j=load(name+'/validation.json');assert j['pass'] and j['original_saves_unchanged'] and j['save_sha256']=='73733902ec36e7ec13fc74d734c773b66077620d63febe1399cae9f759ef6a85' and j['elf_sha256']==sha(elf),name
 assert j['ram_writes']==j['forced_battle_outcomes']==0,name
 if name in wallace_names or name in ['waterfall-a','waterfall-menu-native-option-rerun']:
  assert j['native_save']['valid_sectors']==14 and j['native_save']['cold_reopen'],name
 if name in ['waterfall-a','waterfall-menu-native-option-rerun']:
  assert len(j['stages'])==2 and len(j['follower_checks'])==8 and all(x['visible'] and x['native_sprite_active'] for x in j['follower_checks']) and j['full_original_storage_unchanged']
assert len(validations)==24
print('ECRUTEAK_WALLACE_PREFLIGHT_PASS',len(validations),sha(rom),flush=True)
sv=r/'saves/pokemonthyl_v1.2.sav';ss=sha(sv.read_bytes());assert ss=='73733902ec36e7ec13fc74d734c773b66077620d63febe1399cae9f759ef6a85'
saves={str(x.relative_to(r)):sha(x.read_bytes()) for x in (r/'saves').rglob('*.sav')}
now=datetime.datetime.now(datetime.timezone.utc);stamp=now.strftime('%Y%m%dT%H%M%SZ');out=r/('outputs/rom-regions-update-'+stamp);out.mkdir(exist_ok=False)
for ext in ('gba','elf','sym','map'):
 src=r/('pokemonthyl.'+ext);assert src.exists();shutil.copy2(src,out/('pokemonthyl.'+ext+'.before-ecruteak-wallace'))
 shutil.copy2(q/('pokemonthyl.'+ext),out/('pokemonthyl.'+ext))
shutil.copy2(sv,out/'pokemonthyl.sav');shutil.copy2(q/'native-story-contact.png',out/'native-story-contact.png')
statuspath=r/'work/animation-recreation-status.json';shutil.copy2(statuspath,out/'animation-status.before.json')
proof=dict(p);proof.update(time_utc=now.isoformat(),rom_sha256=sha(rom),elf_sha256=sha(elf),bytes=len(rom),resident_sections_match=True,resident_sections=sections,save_layout_unchanged=True,save_layout=layout,assets=assets,additional_title_assets_unchanged=extra,johto_existing_maps=59,johto_ecruteak_integrated=True,johto_ecruteak_native_events=31,johto_ecruteak_native_battles=9,johto_ecruteak_native_wild_outcomes=4,johto_ecruteak_native_map_links=26,johto_ecruteak_same_save_chain=chain,hoenn_wallace_hm07_integrated=True,hoenn_wallace_native_cases=9,waterfall_shared_region_badge_gate=True,waterfall_native_cases=9,evidence_root=str(q),native_validations=validations,save_delivery=str(out/'pokemonthyl.sav'),save_sha256=ss,all_original_saves_unchanged=True,known_existing_bad_egg_repaired=False)
proof['performance']['ecruteak_burned_tower']={'samples':samples,'loads':performance['maps'],'instrumentation':'separate emulator clone only','original_core_manual_ram_writes':0,'delta_device_fps_measured':False}
proof['wild_encounters_compiled_audit']=compiled_wild;proof['habitat_region_page_audit']=habitat;proof['new_capture_identity']=capture
proof['remaining']={'johto_full_story_complete':False,'hoenn_full_story_complete':False,'johto_next':'Olivine/Cianwood fifth-sixth gym source prepared; gyms5-8, later radio tower and league remain','hoenn_next':'VictoryRoad Wally original party source prepared; native integration and natural full VictoryRoad/League route audit remain','three_region_natural_playthrough_complete':False,'johto_habitat_classifier_audit_pending':False,'delta_old_save_state_corruption_cause_proven':False}
proof['visual_review']={'contact':str(out/'native-story-contact.png'),'checked':True,'limits':['Johto uses native Kanto tilesets and placeholder portraits; complete original region art is not finished.']}
(out/'provenance.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
(out/'README-ko.txt').write_text('이번 추가 반영: 성도 35·36·37번도로·자연공원·인주시티·불탄탑 등 15개 맵(성도 누적59개), 꼬지모와 실버 사건·세 전설 포켓몬 발견·유빈 4번째 배지·기모노5인 전투와 SURF 중복 시 TM35 대체. 호연 윤진 HM07 폭포 수령·이미 수령한 경우 TM26 지진 대체, 지역 배지에 맞춘 폭포 A/파티 메뉴와 피카츄 동행. 이벤트31개·트레이너 승패9개·야생 승패도주포획4개·왕복26개·동일 SAV 스토리5단계·윤진9개·폭포9개·3지역 서식지·야생조우 테이블 통과. 인주시티/불탄탑 idle·walk 4검사에서360프레임 누락0. 승인 오프닝V7/타이틀V8/로이로사V11 유지. 세이브는 사용자 원본 복사본이며 진행 강제 완료 없음. 성도5~8체육관·후반 라디오탑·리그와 호연 민진 최종전·전체 자연 진행 통합 검증은 미완료. 기존 Bad Egg는 복원되지 않았고 DELTA 기기 FPS/다른 ROM의 이전 Save State는 미검증.\n')
for ext in ('gba','elf','sym','map'):
 temp=r/('pokemonthyl.'+ext+'.next');assert not temp.exists();shutil.copy2(out/('pokemonthyl.'+ext),temp);os.replace(temp,r/('pokemonthyl.'+ext))
assert sha((r/'pokemonthyl.gba').read_bytes())==proof['rom_sha256'];assert saves=={str(x.relative_to(r)):sha(x.read_bytes()) for x in (r/'saves').rglob('*.sav')}
status=json.loads(statuspath.read_text());status['updated_at']=now.isoformat();status['verified_by']='root native battle/wild/map/menu/save/chain/performance QA and ELF/ROM provenance';status['current_rom']={'path':str(r/'pokemonthyl.gba'),'sha256':sha(rom),'bytes':len(rom),'provenance':str(out/'provenance.json'),'verified_delivery_folder':str(out)}
remaining=status.setdefault('regional_story_remaining',{});remaining.update(johto_full_story_complete=False,hoenn_full_story_complete=False,johto_ecruteak='integrated:15newmaps/31events/9nativebattles/4wildoutcomes/26links; sameSAV five-stage chain and native14sectorcold saves passed',hoenn_wallace_hm07_waterfall='integrated:9rewardcases/9A-menu-regioncases, genuine Pikachu follower and cold saves passed',johto_next='Olivine/Cianwood fifth-sixth gym source prepared, not ROM applied; gyms5-8/laterRadio/League remain',hoenn_next='VictoryRoad Wally source prepared, not ROM applied; full natural League route audit remains',johto_habitat_classifier_audit_pending=False,owners={'johto':'johto_resume','hoenn':'dive_hm_resume','performance':'performance_resume'})
status.setdefault('performance_current',{})['ecruteak_burned_tower']={'cases':4,'hardware_frames_per_case':360,'processing_misses':0,'single_follower':True,'evidence_root':str(q),'instrumentation':'separate emulator clone','delta_device_fps_measured':False}
statuspath.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n');(r/'work/current-regions-release-path.txt').write_text(str(out)+'\n')
with (r/'work/regional-integration-progress.jsonl').open('a') as f:f.write(json.dumps({'time':now.isoformat(),'stage':'ecruteak-wallace-hm07-waterfall-current-rom','delivery':str(out),'rom_sha256':sha(rom),'full_regions_complete':False})+'\n')
print('PUBLISH_ECRUTEAK_WALLACE_PASS',str(out),sha(rom),'SAV_UNCHANGED',ss,'APPROVED_ASSETS',len(assets),'TITLE_EXTRA',len(extra),'RESIDENT_SECTIONS',len(sections),flush=True)
