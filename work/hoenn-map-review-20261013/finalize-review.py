from pathlib import Path
import json,hashlib,datetime,re
r=Path('/workspaces/pokefirered');o=r/'work/hoenn-map-review-20261013'
m=json.loads((o/'result.json').read_text());structural=json.loads((o/'rom-tileset-structural-audit-v2.json').read_text());dark=json.loads((o/'puzzle6-darkness-controls/validation.json').read_text());edge=json.loads((o/'native-tileset-edges-all/validation.json').read_text())
assert m['map_count']==457 and m['static_integrity_exit']==0 and structural['pass'] and structural['maps_checked']==457 and not structural['failures']
assert dark['pass'] and all(not c['reset'] and c['field_idle'] for c in dark['cases'])
assert edge['cases'][0]['actual_visible_colors_match'] and all(c['nonzero_pixels']==0 for c in edge['cases'][0]['tiles']) and edge['cases'][1]['all_zero_transparent']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'pokemonthyl.gba')==m['rom_sha256'] and sha(r/'saves/pokemonthyl_v1.25.sav')==m['source_sav_sha256']
text=(o/'mapsmoke.log').read_text();assert '457 maps: BLACK 1, OK 456' in text
summary={'rom_sha256':m['rom_sha256'],'expected_maps':457,'quick_entry_walk_OK':456,'initial_BLACK':1,'reset_error_timeout':0,'black_classification':'unlit requires_flash room; negative/positive preboot flash flag controls verify native dark mask and actual key movement','actual_menu_Flash_tested':False,'structural_rom_source_maps_pass':457,'tilesets':63,'initial_graphics_edge_maps':2,'edge_result':'all 11 referenced out-of-payload tile slots read as zero/transparent in actual VRAM; palette14 references have no visible nonzero pixels','native_no_memory_writes':True,'whole_story_playthrough_complete':False,'all_door_warp_traversal_complete':False,'manual_visual_art_approval_complete':False,'inputs_preserved':True,'proof_dir':str(o)}
(o/'review-summary.json').write_text(json.dumps(summary,indent=2))
status=r/'work/animation-recreation-status.json';j=json.loads(status.read_text())
j['hoenn_map_review_20261013']={'status':'CURRENT_ROM_457_MAP_ENTRY_AND_STRUCTURE_CHECKS_COMPLETE_SCOPED','summary':summary,'limitations':['not whole natural story traversal','not all door/warp traversal','not all visual art approval','Flash controls used preboot flags, not an actual menu field-move execution']}
j['save_edit_20261013']['local_download_sav']="C:/Users/seren/Documents/Codex/2026-10-01/https-effective-meme-v6pxvx5qx6vghwj56-github-dev/outputs/pokemonthyl_v1.25-items99-iv2x.sav"
j['save_edit_20261013']['local_download_zip']="C:/Users/seren/Documents/Codex/2026-10-01/https-effective-meme-v6pxvx5qx6vghwj56-github-dev/outputs/pokemonthyl-v1.25-items99-iv2x-20261013.zip"
j['save_edit_20261013']['local_download_sav_sha256']='158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5'
j['save_edit_20261013']['delivery_verified_bytes']=131072
j['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
status.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
note='''# 2026-10-13  1.25 SAV    ROM   

##  SAV 
: saves/pokemonthyl_v1.25.sav, 53d923bf4668373724b19c9d3c8526b002701606ab7ac082d657ee990e23d7b3.
: saves/pokemonthyl_v1.25-items99-iv2x.sav, 158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5.
   work/save-edit-v125-20261013/pokemonthyl_v1.25-original.sav .
199, 2499,  Live bag  stack99 .
Lv52 ///  IV min(31,old*2).      .
 OT2839214970    . ROM /    .
PID/OT/EXP/EV////  //PC//  , HP native CalculateMonStats  maxHP  .
  4/4, 12u32 XOR/checksum/byte 4/4 .
 f31ROM readonly native Continue SAVE6768coldContinue , party600/PC33744/Dex .
 BOX2slot22 Lickitung  record   .  Bad Egg .
   draft 2        .
 v1.2     .

##   
 main ROM f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d, ROM   .
gMapGroup_Hoenn*  457   . QA  SAV preboot warp/Lv100 /Repel , 240frames   .
 SAV/ROM   quick 456OK/BLACK1. RESET/ERROR/TIMEOUT0.
Puzzle6 BLACK requires_flash  nativeflashLevel4  97.7578% black. preboot FLASH_ACTIVE onlevel0/70.7891%,   UP/RIGHT , field_idle , reset .
 script marker   :  OnWarp      .
ROM/source layout pointer/flags/map+border bytes/Emerald512 split/metatile/u32 attribute  457 .
  gfx/palette    Littleroot586/587 palette14 8tile  PokemonSchool791/792/793 3tile nativeVRAM zero/transparent .
   exit0,  WARN static-integrity.txt  .
   ,   ,    ,   Flash , DELTA       .
/      .

## 
work/save-edit-v125-20261013/edit-manifest.json, independent-raw-audit.json, native/validation.json, delivery-receipt.json.
work/hoenn-map-review-20261013/result.json, review-summary.json, rom-tileset-structural-audit-v2.json, puzzle6-darkness-controls/validation.json, native-tileset-edges-all/validation.json, static-integrity.txt, mapsmoke.log, shots/.
'''
docs=r/'docs/team/qa/codex-save-hoenn-review-20261013';docs.mkdir(exist_ok=True);(docs/'QA.md').write_text(note,encoding='utf-8')
log=r/'docs/team/log.md';entry='\n### 2026-10-13  1.25 IV/   ROM   \n\n 99,  /// IV 31  SAV. nativeSAVE/cold  /byte . 457quick456OK+darkroom1 , 457 . /  .  docs/team/qa/codex-save-hoenn-review-20261013/QA.md. ROM f31 , SAV   .\n'
if '2026-10-13  1.25 IV/' not in log.read_text():log.write_text(log.read_text()+entry,encoding='utf-8')
print(json.dumps({'summary':summary,'edited_sav_sha256':sha(r/'saves/pokemonthyl_v1.25-items99-iv2x.sav'),'local_delivery_verified':True,'status_written':True}))
