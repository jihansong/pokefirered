from pathlib import Path
import argparse,datetime,hashlib,json,struct,sys,tempfile,traceback
P=argparse.ArgumentParser();P.add_argument('--root',default='/workspaces/pokefirered');P.add_argument('--base',default='saves/hoenn.sav');P.add_argument('--only');a=P.parse_args();R=Path(a.root)
sys.path.insert(0,str(R/'tools/qa'))
import gamedata as gd,eventcheck as ec
from savefile import SaveFile
from emu import Emu as NativeEmu
gd.FIELDS.update({'dock.obj':('ObjectEvent',None),'dock.local':('ObjectEvent','localId'),'dock.map':('ObjectEvent','mapNum'),'dock.group':('ObjectEvent','mapGroup'),'dock.grid':('BackupMapLayout','map'),'dock.width':('BackupMapLayout','Xsize')});gd._OFFSETS=None
base=R/a.base;before=hashlib.sha256(base.read_bytes()).hexdigest();out=R/'work'/('dock-mew-qa-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir(parents=True,exist_ok=False)
rom=str(R/'pokemonthyl.gba');cases=[];current={};F='FLAG_FOUGHT_MEW';E='FLAG_GOT_MEW_EGG';V='VAR_VERMILION_CITY_TRUCK_PUSHED'
prefix=['warp SSAnne_Exterior 58 3','noquestlog','var VAR_MAP_SCENE_VERMILION_CITY 3','var '+V+' 0','flag '+F+' 0','flag '+E+' 0','fastbattle']
def case(name,edits,steps,weak=False,xfail=False):
 c={'name':'dock_'+name,'edit':prefix+edits,'steps':steps,'weak':weak}
 if xfail:c['xfail']=True
 cases.append(c)
talk=['LEFT','A','mash 180','expect overworld'];pending=['expect flag '+F+' = 0','expect var '+V+' = 0'];offer=['LEFT','A','mashtext VermilionCity_Text_TruckLooksHeavy 80','wait 120'];encounter=offer+['A','mashbattle 160','expect battle','expect enemy MEW = 1','expect flag '+F+' = 1','expect var '+V+' = 3']
case('no_strength',[],['LEFT','watch VermilionCity_Text_TruckWontBudge','A','mash 180','expect saw VermilionCity_Text_TruckWontBudge = 1','expect overworld']+pending,True)
case('ship_not_departed',['var VAR_MAP_SCENE_VERMILION_CITY 0'],talk+pending)
case('decline',[],offer+['B','mash 180','expect overworld']+pending)
case('encounter_flee',[],encounter+['shot native_run','mash 180','expect overworld','expect flag '+F+' = 1','expect var '+V+' = 3','LEFT','A','mash 180','expect overworld','shot after_flee'])
case('capture',[],encounter+['throw ITEM_MASTER_BALL','mashtext sText_GiveNicknameCaptured 180','wait 120','B','mash 180','expect overworld','expect flag '+F+' = 1','expect var '+V+' = 3','shot captured'])
case('legacy_egg',['flag '+E+' 1','flag '+F+' 1'],talk+['expect flag '+E+' = 1','expect flag '+F+' = 1','expect var '+V+' = 0'])
case('legacy_encounter',['flag '+F+' 1'],talk+['expect flag '+F+' = 1','expect var '+V+' = 0'])
for d in range(1,5):case('legacy_pushed_'+str(d),['var '+V+' '+str(d)],talk+['expect flag '+F+' = 0','expect var '+V+' = '+str(d),'shot shifted'])
case('roadside_saved',['warp VermilionCity 27 30'],['wait 60','expect overworld','expect map VermilionCity','shot roadside'])
case('ship_departure',['warp SSAnne_Exterior 32 13','var VAR_MAP_SCENE_VERMILION_CITY 1','flag FLAG_HIDE_SS_ANNE 0','flag FLAG_ROCKET_SS_ANNE 1'],['wait 1200','mash 300','expect overworld','expect map VermilionCity','expect var VAR_MAP_SCENE_VERMILION_CITY = 3'])
case('no_strength_negative',[],talk+['expect battle'],True,True)
class CheckedEmu(NativeEmu):
 def shot(self,path):
  if path.endswith('_native_run.png'):
   assert ec.wait_action_menu(self,rom),'Battle action menu missing';self.press('RIGHT');self.press('DOWN');self.press('A')
  return super().shot(path)
 def __exit__(self,typ,value,tb):
  try:
   if typ is None:
    b=ec.live_blocks(self);g,n=struct.unpack_from('<bb',b.sb1,gd.off('sb1.location'));info=gd.map_info('SSAnne_Exterior')
    if (g,n)==(info['group'],info['num']):
     grid=self.sym('VMap');w=self.u32(grid+gd.off('dock.width'));ptr=self.u32(grid+gd.off('dock.grid'));shift=b.var(V)!=0
     def tile(x,y):return self.u16(ptr+2*((y+7)*w+x+7))&0x3FF
     assert w==85,('unexpected map width',w);assert tile(55,2)==(0x316 if shift else 0x315),('truck tile',tile(55,2),shift);assert tile(57,3)==(0x1C1 if shift else 0x31A),('exposed tile',tile(57,3),shift)
    if current['name']=='dock_roadside_saved':
     z=self.sym('gObjectEvents');size=gd.off('dock.obj')
     for i in range(gd.const('OBJECT_EVENTS_COUNT')):
      q=z+i*size
      if self.u8(q)&1 and self.u8(q+gd.off('dock.group'))==g and self.u8(q+gd.off('dock.map'))==n:assert self.u8(q+gd.off('dock.local')) not in (10,11),'Roadside truck/Mew still active'
  finally:super().__exit__(typ,value,tb)
ec.Emu=CheckedEmu;results=[]
with tempfile.TemporaryDirectory(prefix='dock-fixtures-') as td:
 for weak in (False,True):
  s=SaveFile(str(base));assert s.party_count()>0;s.keep_party(1);m=s.party_mon(0);m.set_species(gd.const('SPECIES_PIKACHU'));m.make_strong(80);m.set_starter_bit(False)
  subs=m.subs();moves=[gd.const('MOVE_TACKLE' if weak else 'MOVE_STRENGTH'),gd.const('MOVE_TACKLE'),0,0];subs['A'][:]=struct.pack('<4H4B',*moves,15,35,0,0);m.put_subs(subs);s.set_item('ITEM_MASTER_BALL',10);s.save(str(Path(td)/('weak.sav' if weak else 'strong.sav')))
 for c in cases:
  c['base']=str(Path(td)/('weak.sav' if c.pop('weak') else 'strong.sav'))
  if a.only and c['name']!=a.only:continue
  if c['name']=='dock_capture':
   s=SaveFile(c['base']);count=sum(m.has_species() and not m.is_egg() and m.species()==gd.const('SPECIES_MEW') for m in s.box_mons());fateful=sum(m.has_species() and m.species()==gd.const('SPECIES_MEW') and m.fateful() for m in s.box_mons());c['steps']+=['expect mons MEW = '+str(count+1),'expect fateful MEW = '+str(fateful+1),'expect item ITEM_MASTER_BALL = 9']
  current=c
  try:ok,errors=ec.run_case(c,rom,str(out))
  except Exception:ok=False;errors=[traceback.format_exc()]
  expected=c.get('xfail',False);passed=(not ok and errors==['expect battle: not in a battle']) if expected else ok;results.append({'name':c['name'],'pass':passed,'negative_control':expected,'errors':errors});print(json.dumps(results[-1]),flush=True)
 (out/'cases.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cases))
assert hashlib.sha256(base.read_bytes()).hexdigest()==before,'Original save changed'
summary={'results':results,'original_save_preserved':True,'save_reload_tested':False,'delta_device_tested':False};(out/'result.json').write_text(json.dumps(summary,indent=2)+'\n');print(str(out));raise SystemExit(0 if results and all(x['pass'] for x in results) else 1)
