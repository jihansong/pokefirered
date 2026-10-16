from pathlib import Path
import sys,json,hashlib,struct,traceback
root=Path('/workspaces/pokefirered');work=root/'work/save-inventory-pp-20261013';out=work/'native-ux-v1';out.mkdir(exist_ok=True)
rom=work/'candidate/pokemonthyl.gba';elf=work/'candidate/pokemonthyl.elf';sav=work/'candidate/pokemonthyl_v1.25-items99-iv2x-pp15.sav'
sys.argv=['pp','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split(chr(10)+'results=[];rows=[]'+chr(10))[0],'<verified-native-definitions>','exec'))
s=SaveFile(str(sav));s.set_lead(3);s.warp('PewterCity_PokemonCenter_1F',7,4)
for z in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+z*off('questlogscene')]=0
s.put_item_first('ITEM_TM_CASE',1);s.put_item_first('ITEM_TM17_PROTECT',1);p=out/'TM17-QA-only.sav';s.save(str(p))
e=ReadOnlyEmu(str(rom),str(p),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(30)
def snap(tag):
 e.shot(str(out/(tag+'.png')),scale=3)
 raw=e.read(syms['gPlayerParty'],100);m=Mon(bytearray(raw),0);s=m.subs();data={'callback':hex(e.callback2()),'species':m.species(),'moves':struct.unpack_from('<4H',s['A'],0),'PP':list(s['A'][8:12]),'bonus':s['G'][8]};(out/(tag+'.json')).write_text(json.dumps(data,indent=2));print(tag,data,flush=True)
e.press('START',hold=2,after=50);e.press('DOWN',hold=2,after=12);e.press('A',hold=2,after=80);e.press('A',hold=2,after=30);e.press('A',hold=2,after=80);e.press('RIGHT',hold=2,after=25);e.press('RIGHT',hold=2,after=40);snap('01-pika-summary')
print('PP_UX_READY',flush=True)
