#!/usr/bin/env python3
"""Native Norman reward regression. Disposable saves; exact negative controls."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,struct,sys,tempfile,traceback

def sha(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def make_cases(x,y,first_text):
 N='PetalburgCity_Gym';T='TRAINER_HOENN_NORMAN_1'
 B='FLAG_HOENN_BADGE05_GET';F='FLAG_HOENN_GOT_TM42_FROM_NORMAN';W='VAR_HOENN_SCENE_WALLY'
 cases=[]
 def add(name,edits,steps,mode='strong',failure=None):
  initial=[f'warp {N} {x} {y}','noquestlog',f'var {W} 2',f'trainer {T} 1',f'flag {B} 0',f'flag {F} 0','item ITEM_TM42 0','money 10000','fastbattle']
  initial += [f'flag FLAG_HOENN_BADGE{i:02d}_GET {int(i<=4)}' for i in (1,2,3,4,6,7,8)]
  c={'name':'norman_'+name,'edit':initial+edits,'steps':steps,'mode':mode}
  if failure:c['expected_failure']=failure
  cases.append(c)
 talk=['UP','A','mash 240','expect overworld']
 paid=[f'expect trainer {T} = 1',f'expect flag {B} = 1',f'expect flag {F} = 1']
 unpaid=[f'expect trainer {T} = 0',f'expect flag {B} = 0',f'expect flag {F} = 0','expect item ITEM_TM42 = 0']
 again=['A','mash 240','expect overworld','expect item ITEM_TM42 = 1']
 add('new_victory',[f'trainer {T} 0'],['UP','A','mashbattle 180','expect battle','expect enemycount = 4']+unpaid+['mash 1200','expect overworld']+paid+['expect item ITEM_TM42 = 1','shot reward']+again)
 add('old_winner',[],talk+paid+['expect item ITEM_TM42 = 1','expect money = 10000']+again)
 add('three_badges_wait',[f'trainer {T} 0','flag FLAG_HOENN_BADGE04_GET 0'],['UP','watch '+N+'_Text_NormanAfter','A','mash 240','expect overworld','expect saw '+N+'_Text_NormanAfter = 1']+unpaid+[f'expect var {W} = 2'])
 add('new_wally_intro',[f'trainer {T} 0',f'var {W} 0'],['UP','watch '+first_text,'A','mash 240','expect overworld','expect saw '+first_text+' = 1']+unpaid)
 add('new_wally_waiting',[f'trainer {T} 0',f'var {W} 1'],['UP','watch '+N+'_Text_NormanWallyWaiting','A','mash 240','expect overworld','expect saw '+N+'_Text_NormanWallyWaiting = 1']+unpaid+[f'expect var {W} = 1'])
 add('before_win',[f'trainer {T} 0'],['UP','A','mashbattle 180','expect battle']+unpaid)
 add('loss',[f'trainer {T} 0'],['UP','A','mashbattle 180','expect battle','mash 1200','expect overworld']+unpaid,mode='weak')
 add('other_source_tm',['item ITEM_TM42 1'],talk+paid+['expect item ITEM_TM42 = 2','A','mash 240','expect item ITEM_TM42 = 2'])
 add('full_stack',['item ITEM_TM42 999'],['UP','watch '+N+'_Text_NormanNoRoom','A','mash 240','expect overworld','expect saw '+N+'_Text_NormanNoRoom = 1',f'expect flag {B} = 1',f'expect flag {F} = 0','expect item ITEM_TM42 = 999','expect money = 10000','A','mash 240',f'expect flag {F} = 0','expect item ITEM_TM42 = 999'])
 add('retry_room',[f'flag {B} 1','item ITEM_TM42 998'],talk+paid+['expect item ITEM_TM42 = 999','A','mash 240','expect item ITEM_TM42 = 999'])
 add('already_received',[f'flag {B} 1',f'flag {F} 1','item ITEM_TM42 1'],talk+paid+['expect item ITEM_TM42 = 1']+again)
 add('received_but_used',[f'flag {B} 1',f'flag {F} 1'],talk+paid+['expect item ITEM_TM42 = 0','A','mash 240','expect item ITEM_TM42 = 0'])
 add('receipt_missing_badge',[f'flag {F} 1'],talk+paid+['expect item ITEM_TM42 = 0'])
 add('badge_not_reannounced',[f'flag {B} 1'],['UP','watch '+N+'_Text_ReceivedBalanceBadge','A','mash 240','expect overworld','expect saw '+N+'_Text_ReceivedBalanceBadge = 0']+paid+['expect item ITEM_TM42 = 1'])
 others={'FLAG_BADGE01_GET':0,'FLAG_BADGE02_GET':1,'FLAG_HOENN_BADGE01_GET':0,'FLAG_HOENN_BADGE02_GET':1,'FLAG_HOENN_BADGE03_GET':0,'FLAG_HOENN_BADGE04_GET':1,'FLAG_HOENN_BADGE06_GET':0,'FLAG_HOENN_BADGE07_GET':1,'FLAG_HOENN_BADGE08_GET':0}
 add('other_badges_unchanged',[f'flag {k} {v}' for k,v in others.items()],talk+paid+['expect item ITEM_TM42 = 1']+[f'expect flag {k} = {v}' for k,v in others.items()])
 add('duplicate_negative_control',[f'flag {B} 1',f'flag {F} 1'],talk+['expect item ITEM_TM42 = 1'],failure='expect item ITEM_TM42 = 1: item ITEM_TM42 is 0')
 add('full_negative_control',['item ITEM_TM42 999'],talk+[f'expect flag {F} = 1'],failure=f'expect flag {F} = 1: flag {F} is 0, expected 1')
 for scene in (0,1):
  add('old_winner_wally_'+str(scene),[f'var {W} {scene}']+[f'flag FLAG_HOENN_BADGE{i:02d}_GET 0' for i in (1,2,3,4)],talk+paid+['expect item ITEM_TM42 = 1',f'expect var {W} = {scene}','expect money = 10000']+again+[f'expect var {W} = {scene}'])
 assert len(cases)==19 and len({c['name'] for c in cases})==19
 return cases

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',default='/workspaces/pokefirered');p.add_argument('--base',default='saves/hoenn.sav');p.add_argument('--only')
 a=p.parse_args();r=Path(a.root);sys.path.insert(0,str(r/'tools/qa'))
 import gamedata as gd,eventcheck as ec
 from savefile import SaveFile
 base=(r/a.base).resolve();rompath=r/'pokemonthyl.gba';romsha=sha(rompath)
 originals={str(p.resolve()):sha(p) for p in (r/'saves').glob('*.sav')};originals[str(base)]=sha(base)
 n='PetalburgCity_Gym';src=(r/f'data/maps/{n}/scripts.inc').read_text()
 assert gd.const('FLAG_HOENN_GOT_TM42_FROM_NORMAN')==0x1265
 entry=re.search(r'^'+n+r'_EventScript_Norman::\n(?:[ \t].*\n)+',src,re.M)
 assert entry and entry.group().index('checktrainerflag')<entry.group().index('goto_if_eq VAR_HOENN_SCENE_WALLY')
 first=re.search(r'^'+n+r'_EventScript_NormanFirst::\n(?:[ \t].*\n)+',src,re.M)
 assert first,'Wally introduction missing'
 msg=re.search(r'\bmsgbox (\w+)',first.group());assert msg,'No first introduction dialogue'
 meta=gd.map_info(n)['json'];leaders=[o for o in meta['object_events'] if o.get('script')==n+'_EventScript_Norman']
 assert len(leaders)==1,'Norman object missing/ambiguous'
 x,y=leaders[0]['x'],leaders[0]['y']+1
 cases=make_cases(x,y,msg.group(1))
 if a.only:
  cases=[c for c in cases if c['name']==a.only];assert len(cases)==1,'Unknown case name'
 out=r/'work'/('norman-native-qa-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir(parents=True,exist_ok=False)
 results=[];report={'rom_sha256':romsha,'original_save_sha256':originals,'native_save_reload_tested':False,'delta_device_tested':False,'expected_cases':len(cases)}
 try:
  with tempfile.TemporaryDirectory(prefix='norman-fixture-') as td:
   paths={};rom=gd.Rom()
   for mode in ('strong','weak'):
    s=SaveFile(str(base));assert s.party_count()>=1
    s.keep_party(1);m=s.party_mon(0);assert not m.is_egg(),'Fixture lead is an egg'
    m.set_species(gd.const('SPECIES_MEWTWO' if mode=='strong' else 'SPECIES_MAGIKARP'),rom)
    m.set_starter_bit(False);m.set_snagged(False);m.set_held(gd.const('ITEM_LUM_BERRY' if mode=='strong' else 'ITEM_NONE'))
    m.set_otid(struct.unpack_from('<I',s.sb2,gd.off('sb2.playerTrainerId'))[0])
    m.blk[m.o+20:m.o+27]=s.sb2[gd.off('sb2.playerName'):gd.off('sb2.playerName')+7]
    sub=m.subs();sub['A'][:]=struct.pack('<4H4B',gd.const('MOVE_PSYCHIC' if mode=='strong' else 'MOVE_SPLASH'),0,0,0,10 if mode=='strong' else 40,0,0,0);m.put_subs(sub)
    m.make_strong(100 if mode=='strong' else 1,rom);m.blk[m.o+80:m.o+84]=b'\0'*4
    if mode=='weak':struct.pack_into('<H',m.blk,m.o+86,1)
    path=Path(td)/(mode+'.sav');s.save(str(path));paths[mode]=str(path)
   for c in cases:
    c['base']=paths[c['mode']]
    try:
     ok,errors=ec.run_case(c,str(rompath),str(out))
     valid=(not ok and errors==[c['expected_failure']]) if c.get('expected_failure') else (ok and not errors)
     row={'name':c['name'],'ok':valid,'native_ok':ok,'errors':errors,'negative_control':bool(c.get('expected_failure'))}
    except Exception as ex:row={'name':c['name'],'ok':False,'error':repr(ex),'trace':traceback.format_exc()}
    results.append(row);print(json.dumps(row),flush=True)
 except Exception as ex:report.update(error=repr(ex),trace=traceback.format_exc())
 finally:
  report.update(results=results,passed=sum(bool(c['ok']) for c in results),total=len(results),original_saves_preserved=all(Path(p).exists() and sha(p)==h for p,h in originals.items()),rom_unchanged=sha(rompath)==romsha)
  report['ok']=report['original_saves_preserved'] and report['rom_unchanged'] and len(results)==len(cases) and all(c['ok'] for c in results) and 'error' not in report
  (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps({'report':str(out/'result.json'),'passed':report['passed'],'total':report['total'],'ok':report['ok']}),flush=True)
 return 0 if report['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
