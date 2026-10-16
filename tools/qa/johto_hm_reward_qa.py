#!/usr/bin/env python3
"""Native Sprout reward and save/reload cases.
Usage: python SCRIPT VERIFIED_VIOLET_QA --rom ROM --elf ELF --sav SAV --out NEWDIR
"""
from pathlib import Path
import hashlib,sys
base=Path(sys.argv.pop(1));text=base.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb'
assert text.count('\nresults=[]\n')==1
exec(compile(text.split('\nresults=[]\n')[0],str(base),'exec'),globals())
_base_fixture=fixture;_base_snapshot=snapshot
KH='FLAG_GOT_HM05'
def pcitems(b):
 o=off('sb1.pcItems');return bytes(b.sb1[o:o+4*const('PC_ITEMS_COUNT')])
def set_pc_hm(s,quantity):
 o=off('sb1.pcItems');count=const('PC_ITEMS_COUNT');hm=const('ITEM_HM05')
 rows=[struct.unpack_from('<HH',s.sb1,o+4*i) for i in range(count)]
 rows=[v for v in rows if v[0] and v[0]!=hm]
 if quantity:rows.append((hm,quantity))
 assert len(rows)<=count,'PC items fixture has no free slot'
 rows += [(0,0)]*(count-len(rows))
 for i,v in enumerate(rows):struct.pack_into('<HH',s.sb1,o+4*i,*v)
def teach_flash(m):
 d=m.subs();mid=const('MOVE_FLASH');struct.pack_into('<H',d['A'],0,mid)
 d['A'][8]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
 m.put_subs(d)
def prepare(path,c):
 if 'from_saved' in c:
  s=SaveFile(c['from_saved']);s.set_item('ITEM_TM10',998)
 else:
  s=_base_fixture(path,'LI',False)
  s.set_flag(T,True);s.set_trainer_beaten('TRAINER_JOHTO_LI',True)
  s.set_flag(H,c.get('done',False));s.set_flag(KH,c.get('kanto',False))
  s.set_item('ITEM_HM05',c.get('bag_hm',0));set_pc_hm(s,c.get('pc_hm',0))
  s.set_item('ITEM_TM10',c.get('tm',0));s.set_item('ITEM_TM_CASE',c.get('case',1))
  if c.get('party_move'):teach_flash(s.party_mon(0))
  if c.get('box_move'):
   allowed={const('SPECIES_'+x) for x in ['BULBASAUR','IVYSAUR','VENUSAUR','PIKACHU','RAICHU','ABRA','KADABRA','ALAKAZAM','MEWTWO','MEW']}
   candidates=[m for m in s.box_mons() if m.has_species() and not m.is_egg() and m.species() in allowed and not (m.blk[m.o+19]&1)]
   assert candidates,'No compatible existing PC mon for FLASH fixture'
   teach_flash(candidates[0])
 s.warp('SproutTower_3F',6,9);s.save(str(path));return s
def snapshot(e):
 result=_base_snapshot(e);b=blocks(e);result['flags'][KH]=b.flag(KH)
 result['items']={n:b.item_count(n) for n in ['ITEM_HM05','ITEM_TM10','ITEM_TM_CASE']}
 result['pc_items']=pcitems(b)
 return result
def interact(e):
 e.walk('UP',1);e.run(30);e.press('A',hold=3,after=20)
 settle(e);assert not e.in_battle()
def verify(e,before,c,prepared):
 after=snapshot(e)
 expected_hm=c.get('expect_hm',c.get('bag_hm',0))
 expected_tm=c.get('expect_tm',c.get('tm',0))
 expected_done=c.get('expect_done',True)
 assert after['items']['ITEM_HM05']==expected_hm,(c['name'],after['items'])
 assert after['items']['ITEM_TM10']==expected_tm,(c['name'],after['items'])
 assert after['items']['ITEM_TM_CASE']==1,(c['name'],'TM CASE missing')
 assert after['flags'][H]==expected_done,(c['name'],'reward complete',after['flags'][H])
 assert after['flags'][T] and after['flags'][KH]==before['flags'][KH]
 assert all(after['flags'][k]==before['flags'][k] for k in K)
 assert after['party']==before['party']
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 assert after['pc_items']==before['pc_items']==pcitems(prepared)
 assert after['dex']==before['dex'] and after['trainers']==before['trainers']
 return after
cases=[
 {'name':'new_hm','expect_hm':1},
 {'name':'bag_hm','bag_hm':1,'expect_tm':1},
 {'name':'pc_item_hm','pc_hm':1,'expect_tm':1},
 {'name':'kanto_history_only','kanto':True,'expect_tm':1},
 {'name':'party_move_only','party_move':True,'expect_hm':1},
 {'name':'pc_mon_move_only','box_move':True,'expect_hm':1},
 {'name':'legacy_completed','done':True,'kanto':True},
 {'name':'completed_with_current_tm','done':True,'bag_hm':1,'tm':1},
 {'name':'alternate_full','bag_hm':1,'tm':999,'expect_done':False},
 {'name':'no_tm_case_auto_created','case':0,'expect_hm':1}
]
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='tower-reward-') as td:
  for c in cases:
   tag=c['name'];f=Path(td)/(tag+'.sav');prepared=prepare(f,c)
   with ReadOnlyEmu(str(rom),str(f),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60)
    before=snapshot(e);interact(e);first=verify(e,before,c,prepared)
    interact(e);assert snapshot(e)==first,'repeat changed completed reward'
    saved=flash_reload(e,tag);interact(e)
    assert snapshot(e)==first,'cold revisit reissued or changed reward'
    e.shot(str(out/(tag+'.png')),scale=3)
    row={'case':tag,'items':first['items'],'reward_complete':first['flags'][H],
     'kanto_hm_history':first['flags'][KH],'party_pc_and_dex_preserved':True,
     'native_save':saved}
    results.append(row);print(json.dumps(row),flush=True)
   if tag=='alternate_full':
    cases.append({'name':'retry_after_space','from_saved':saved['qa_save'],
      'bag_hm':1,'tm':998,'expect_tm':999})
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
assert len(results)==11
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),
 'input_sav_sha256':originals[sav],'cases':results,'all_pass':True,
 'limits':'Test setup edits only temporary copies; all interactions and saves use native UI.'},indent=2))
