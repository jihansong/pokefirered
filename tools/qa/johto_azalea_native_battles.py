#!/usr/bin/env python3
"""Eight native Azalea battles using the verified Violet QA bootstrap.
Usage: python SCRIPT VERIFIED_VIOLET_QA --rom ROM --elf ELF --sav SAV --out NEWDIR
Only temporary copies of the supplied save are played; no game-memory writes.
"""
from pathlib import Path
import ast,hashlib,sys
base=Path(sys.argv.pop(1))
text=base.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb','Violet helper differs; inspect before reuse'
assert text.count('\nresults=[]\n')==1
exec(compile(text.split('\nresults=[]\n')[0],str(base),'exec'),globals())
_violet_fixture=fixture
_violet_snapshot=snapshot
Q='FLAG_JOHTO_KURT_RESCUE_REQUESTED'
W='FLAG_JOHTO_SLOWPOKE_WELL_CLEARED'
R='FLAG_JOHTO_KURT_REPORT_DELIVERED'
N='FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT'
G='FLAG_JOHTO_BADGE02_GET'
U='FLAG_JOHTO_GOT_TM06_FROM_BUGSY'
AZFLAGS=[Q,W,R,N,G,U]
ACTORS=['WELL_GRUNT_A','WELL_GRUNT_B','WELL_COMMANDER','BUGSY']
TEAMS={
 'WELL_GRUNT_A':['RATTATA','RATTATA'],
 'WELL_GRUNT_B':['ZUBAT','EKANS'],
 'WELL_COMMANDER':['KOFFING'],
 'BUGSY':['METAPOD','KAKUNA','SCYTHER']}
POSITIONS={'WELL_GRUNT_A':('SlowpokeWell_1F',4,13),
 'WELL_GRUNT_B':('SlowpokeWell_1F',18,14),
 'WELL_COMMANDER':('SlowpokeWell_1F',12,7),
 'BUGSY':('AzaleaTown_Gym',6,5)}
def fixture(path,name,loss):
 s=_violet_fixture(path,'FALKNER',loss)
 for f in [T,H,B,M]:s.set_flag(f,True)
 for tr in ['LI','FALKNER']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 for f in AZFLAGS:s.set_flag(f,False)
 s.set_flag(Q,True)
 for tr in ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,False)
 if name in ['WELL_COMMANDER','BUGSY']:
  for tr in ACTORS[:2]:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 if name=='BUGSY':
  s.set_trainer_beaten('TRAINER_JOHTO_WELL_COMMANDER',True)
  s.set_flag(W,True);s.set_flag(R,True)
 for item in ['ITEM_HM05','ITEM_TM40','ITEM_TM_CASE']:s.set_item(item,1)
 for item in ['ITEM_NET_BALL','ITEM_TM06']:s.set_item(item,0)
 s.warp(*POSITIONS[name]);s.save(str(path))
 return s
def snapshot(e):
 data=_violet_snapshot(e);b=blocks(e)
 data['flags'].update({f:b.flag(f) for f in AZFLAGS})
 data['trainers'].update({n:b.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS})
 return data
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='azalea-native-') as td:
  for name in ACTORS:
   for loss in [False,True]:
    tag=name.lower()+('_loss' if loss else '_win')
    target=Path(td)/(tag+'.sav');prepared=fixture(target,name,loss)
    expected=[const('SPECIES_'+n) for n in TEAMS[name]]
    with ReadOnlyEmu(str(rom),str(target),sym='') as e:
     e.syms=syms;e.boot_continue();settle(e);e.run(60)
     baseline=snapshot(e)
     e.walk('UP',1);e.run(30);e.press('A',hold=3,after=12)
     mash_until(e,e.in_battle,300);assert menu(e)
     assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const('TRAINER_JOHTO_'+name)
     raw=e.read(e.sym('gEnemyParty'),600)
     actual=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
     assert actual==expected,(name,actual,expected)
     turns=0
     while menu(e):
      assert turns<90,'battle did not finish'
      fight_one_turn(e,loss=loss);turns+=1
     outcome=e.u8(e.sym('gBattleOutcome'))
     assert outcome==(2 if loss else 1),(name,loss,'native outcome',outcome)
     settle(e);after=snapshot(e)
     wantflags=dict(baseline['flags']);wanttrainers=dict(baseline['trainers'])
     wanttrainers[name]=not loss
     if not loss and name=='WELL_COMMANDER':wantflags[W]=True
     if not loss and name=='BUGSY':wantflags[G]=True;wantflags[U]=True
     assert after['flags']==wantflags,(tag,after['flags'],wantflags)
     assert after['trainers']==wanttrainers,(tag,after['trainers'],wanttrainers)
     assert after['pc']==baseline['pc']==bytes(prepared.blocks['storage'])
     for old,new in zip(baseline['dex'],after['dex']):
      assert old[0]==new[0] and all(not x or y for x,y in zip(old,new))
     assert blocks(e).item_count('ITEM_NET_BALL')==0
     assert blocks(e).item_count('ITEM_TM06')==(1 if name=='BUGSY' and not loss else 0)
     row={'case':tag,'turns':turns,'native_outcome':outcome,'enemies':actual,
      'pc_preserved':True,'kanto_and_first_johto_badges_preserved':True,
      'location_after':e.location()}
     e.shot(str(out/(tag+'.png')),scale=3)
     if not loss:row['save']=flash_reload(e,tag)
     results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),
 'violet_helper_sha256':digest(text.encode()),'input_sav_sha256':originals[sav],
 'cases':results,'all_pass':len(results)==8},indent=2))
