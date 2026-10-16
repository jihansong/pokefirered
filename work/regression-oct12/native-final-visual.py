from pathlib import Path
p=Path('tools/qa/hoenn_gauntlet_save_qa.py').read_text().split('tmp=None; e=None\ntry:',1)[0]
p=p.replace('len(p)>=6','len(p)>=5')
exec(compile(p,'tools/qa/hoenn_gauntlet_save_qa.py','exec'))
report.update(mode='cold-native-map-visual',fixture='temporary position-only save copy; original party retained')
from PIL import Image,ImageDraw
e=None
rows=[]
assert struct.unpack('<II',r.at(syms['MtMortar_1F_Layout']+16,8))==(syms['gTileset_General'],syms['gTileset_RockTunnel'])
try:
 for name,x,y in [('JohtoCherrygroveAirstrip',22,12),('JohtoRoute29',18,12),('NewBarkTown',17,12),('NewBarkTown_ElmsLab',5,6),('PalletTown',9,10),('PalletTown_ProfessorOaksLab',5,6),('MtMortar_1F',18,36),('RockTunnel_1F',18,28)]:
  with tempfile.TemporaryDirectory(prefix='johto-visual-fixture-') as td:
   s=SaveFile(str(sav));party0=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
   for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
   s.warp(name,x,y);tmp=Path(td)/'fixture.sav';s.save(str(tmp))
   e=ReadOnlyEmu(str(rom),str(tmp),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(120);safe(e)
   assert loc_is(e,name),(name,e.location())
   assert pc(e)==source_pc,'PC changed'
   assert e.read(e.ptr('gSaveBlock1Ptr')+off('sb1.playerParty'),600)==party0,'party changed'
   assert digest_dex(blocks(e))==digest_dex(source),'dex changed'
   photo(e,name);rows.append({'map':name,'location':e.location(),'frame':e.frame(),'screenshot':str(out/(name+'.png'))})
   e.close();e=None
 tiles=Image.new('RGB',(720*2,500*4),'#111')
 draw=ImageDraw.Draw(tiles)
 for i,row in enumerate(rows):
  x=(i%2)*720;y=(i//2)*500;draw.text((x+5,y+5),row['map'],fill='white')
  tiles.paste(Image.open(row['screenshot']).convert('RGB'),(x,y+20))
 tiles.save(out/'contact-sheet.png');report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:photo(e,'failure')
finally:
 if e:e.close()
 report['maps']=rows;report['original_saves_unchanged']=before=={p:sha(Path(p).read_bytes()) for p in before}
 report['scope']='Independent position-only cold SAV fixtures; native pixels, no continuous airport journey tested'
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report),flush=True)
