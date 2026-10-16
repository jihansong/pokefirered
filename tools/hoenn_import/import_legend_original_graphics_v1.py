#!/usr/bin/env python3
"""Import only the original Emerald KYOGRE/RAYQUAZA graphics; keep existing IDs."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess
from PIL import Image
r=Path.cwd();em=Path('/root/src/pokeemerald')
revision=subprocess.check_output(['git','-C',str(em),'rev-parse','HEAD'],text=True).strip()
assert revision.startswith('5eff78649'),('Unexpected Emerald source revision',revision)
d='src/data/object_events/'
infos=(em/d/'object_event_graphics_info.h').read_text()
ptr=(em/d/'object_event_graphics_info_pointers.h').read_text()
pic=(em/d/'object_event_pic_tables.h').read_text()
gfx=(em/d/'object_event_graphics.h').read_text()
anims=(em/d/'object_event_anims.h').read_text()
movement=(em/'src/event_object_movement.c').read_text()
info_of=dict(re.findall(r'\[(OBJ_EVENT_GFX_\w+)\]\s*=\s*&gObjectEventGraphicsInfo_(\w+)',ptr))
info=dict(re.findall(r'const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_(\w+)\s*=\s*\{(.*?)\};',infos,re.S))
tables=dict(re.findall(r'static const struct SpriteFrameImage sPicTable_(\w+)\[\]\s*=\s*\{(.*?)\};',pic,re.S))
pngs={m[0]:(m[1],m[2],m[3]) for m in re.findall(
 r'const u32 gObjectEventPic_(\w+)\[\]\s*=\s*INCGFX_U32\("([^"]+)", "\.4bpp"(?:, "-mwidth (\d+) -mheight (\d+)")?\);',gfx)}
pals=dict(re.findall(r'const u16 gObjectEventPal_(\w+)\[\]\s*=\s*INC(?:BIN|GFX)_U16\("([^"]+)"(?:, "\.gbapal")?\);',gfx))
tagpals={tag:sym for sym,tag in re.findall(r'\{gObjectEventPal_(\w+),\s*(OBJ_EVENT_PAL_TAG_\w+)\}',movement)}
animdefs={re.search(r'(sAnim(?:Table)?_\w+)\s*\[\]',z).group(1):z for z in re.findall(
 r'static const union AnimCmd(?:\s*\*const)?\s+sAnim(?:Table)?_\w+\s*\[\]\s*=\s*\{.*?\};',anims,re.S)}
pending={};graphics=[];frames=[];animout=[];rules=[];sources={};images={};done=set()
infofile=r/d/'object_event_graphics_info.h'
newinfo=infofile.read_text()
newinfo=newinfo.replace("// KYOGRE: LUGIA's sprite recolored deep blue with red markings",'// KYOGRE: original Emerald front frames and palette.')
newinfo=newinfo.replace("// RAYQUAZA: HO-OH's sprite recolored green",'// RAYQUAZA: original Emerald frames and palette.')
for kind,width in [('Kyogre',32),('Rayquaza',64)]:
 name=info_of['OBJ_EVENT_GFX_KYOGRE_FRONT' if kind=='Kyogre' else 'OBJ_EVENT_GFX_RAYQUAZA']
 body=info[name]
 assert re.search(r'\.width = '+str(width)+r'\b',body)
 assert re.search(r'\.height = '+str(width)+r'\b',body)
 table=re.search(r'\.images = sPicTable_(\w+)',body).group(1)
 row=tables[table]
 syms=list(dict.fromkeys(re.findall(r'(?:overworld_frame|obj_frame_tiles)\(gObjectEventPic_(\w+)[,)]',row)))
 assert syms,(kind,'No native image sources')
 for sym in syms:
  source,mw,mh=pngs[sym]
  with Image.open(em/source) as image:
   assert image.mode=='P' and max(image.getdata())<16,('not native indexed 4bpp',source)
   assert image.width%8==0 and image.height%8==0,('unaligned native tiles',source)
   images[source]={'size':list(image.size),'mode':image.mode}
   for fw,fh,index in re.findall(r'overworld_frame\(gObjectEventPic_'+sym+r',\s*(\d+),\s*(\d+),\s*(\d+)\)',row):
    frame_pixels=int(fw)*int(fh)*64
    assert image.width*image.height%frame_pixels==0
    assert int(index)<image.width*image.height//frame_pixels,('native frame outside PNG',sym,index)
  dest='graphics/object_events/pics/hoenn/legend_'+re.sub(r'(?<!^)(?=[A-Z])','_',sym).lower()+'.png'
  pending[r/dest]=(em/source).read_bytes()
  sources[source]=hashlib.sha256(pending[r/dest]).hexdigest()
  graphics.append('const u32 gObjectEventPic_ThunderLegend'+sym+'[] = INCBIN_U32("'+dest[:-4]+'.4bpp");')
  row=row.replace('gObjectEventPic_'+sym,'gObjectEventPic_ThunderLegend'+sym)
  if mw:rules.append('$(OBJEVENTGFXDIR)/hoenn/'+Path(dest).stem+'.4bpp: %.4bpp: %.png\n\t$(GFX) $< $@ -mwidth '+mw+' -mheight '+mh)
 frames.append('static const struct SpriteFrameImage sPicTable_ThunderLegend'+table+'[] = {'+row+'};')
 tag=re.search(r'\.paletteTag = (\w+)',body).group(1)
 pal=pals[tagpals[tag]]
 target=r/'graphics/object_events/palettes'/('kyogre.pal' if kind=='Kyogre' else 'rayquaza.pal')
 pending[target]=(em/pal).read_bytes();sources[pal]=hashlib.sha256(pending[target]).hexdigest()
 anim=re.search(r'\.anims = (sAnimTable_\w+)',body).group(1)
 def visit(symbol):
  if symbol in done:return
  done.add(symbol);assert symbol in animdefs,('missing native animation',symbol)
  text=animdefs[symbol]
  refs=set(re.findall(r'\bsAnim(?:Table)?_\w+\b',text))-{symbol}
  for dep in sorted(refs):visit(dep)
  text=re.sub(r'\bsAnim(?:Table)?_\w+\b',lambda m:'sThunderLegend_'+m.group(0),text)
  animout.append(text)
 visit(anim)
 out=body.replace('.images = sPicTable_'+table,'.images = sPicTable_ThunderLegend'+table)
 out=out.replace('.anims = '+anim,'.anims = sThunderLegend_'+anim)
 out=re.sub(r'\.paletteTag = \w+', '.paletteTag = OBJ_EVENT_PAL_TAG_'+kind.upper(),out)
 out=re.sub(r'\.paletteSlot = \w+', '.paletteSlot = PALSLOT_NPC_SPECIAL',out)
 out=re.sub(r'\.reflectionPaletteTag = \w+', '.reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE',out)
 out=out.replace('.disableReflectionPaletteLoad = FALSE','.disableReflectionPaletteLoad = TRUE')
 out=re.sub(r'\.affineAnims = \w+', '.affineAnims = gDummySpriteAffineAnimTable',out)
 out=out.replace('.subspriteTables = sOamTables_','.subspriteTables = gObjectEventSpriteOamTables_')
 pattern=r'const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+kind+r'\s*=\s*\{.*?\};'
 assert len(re.findall(pattern,newinfo,re.S))==1
 newinfo=re.sub(pattern,lambda m:'const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+kind+' = {'+out+'};',newinfo,flags=re.S)
pending[infofile]=newinfo.encode()
for filename,blocks in [('object_event_graphics.h',graphics),('object_event_pic_tables.h',frames),('object_event_anims.h',animout)]:
 f=r/d/filename;s=f.read_text()
 assert 'BEGIN THUNDER YELLOW ORIGINAL HOENN LEGENDS' not in s,('already imported',f)
 pending[f]=(s.rstrip()+'\n\n// BEGIN THUNDER YELLOW ORIGINAL HOENN LEGENDS\n'+'\n\n'.join(blocks)+'\n// END THUNDER YELLOW ORIGINAL HOENN LEGENDS\n').encode()
f=r/'spritesheet_rules.mk';s=f.read_text()
assert 'BEGIN THUNDER YELLOW ORIGINAL HOENN LEGENDS' not in s
pending[f]=(s.rstrip()+'\n\n# BEGIN THUNDER YELLOW ORIGINAL HOENN LEGENDS\n'+'\n\n'.join(rules)+'\n# END THUNDER YELLOW ORIGINAL HOENN LEGENDS\n').encode()
backup=r/'work/original-hoenn-legends-backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
original={}
for f in pending:
 key=str(f.relative_to(r));original[key]=hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None
 if f.exists():
  target=backup/key;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
backup.mkdir(parents=True,exist_ok=True)
for f,b in pending.items():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
receipt={'emerald_revision':revision,'source_files':sources,'source_images':images,'original_files':original,
 'graphics_ids_unchanged':True,'source_dimensions':{'Kyogre':[32,32],'Rayquaza':[64,64]},
 'frame_animation_sources_imported':True,'native_runtime_validated':False,
 'save_layout_changed':False}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
