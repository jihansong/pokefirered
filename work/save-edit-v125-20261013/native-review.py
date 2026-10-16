from pathlib import Path
import sys,json,struct,hashlib,shutil
root=Path('/workspaces/pokefirered');osource=root/'work/save-edit-v125-20261013'
candidate=osource/'pokemonthyl_v1.25-items99-iv2x.sav';out= osource/'native';out.mkdir(exist_ok=True)
testsave=out/'native-input-only.sav';shutil.copyfile(candidate,testsave)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf'
sys.argv=['native-save-review','--rom',str(rom),'--elf',str(elf),'--sav',str(testsave),'--out',str(out)]
prefix=(root/'tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(prefix.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
assert prefix.count('\nresults=[];rows=[]\n')==1
exec(compile(prefix.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-native-definitions>','exec'))
s=SaveFile(str(candidate));expectedparty=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);expectedpc=bytes(s.blocks['storage']);expectedDex=[s.dex_state(i) for i in range(1,387)]
beforehash=digest(candidate.read_bytes());inputhash=digest((root/'saves/pokemonthyl_v1.25.sav').read_bytes())
with ReadOnlyEmu(str(rom),str(testsave),sym='') as e:
 e.syms=syms;e.boot_continue();settle(e)
 b=record(e)
 assert b['count']==s.party_count() and b['party']==expectedparty
 assert b['pc']==expectedpc and b['dex']==expectedDex
 for item in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY']:
  assert blocks(e).item_count(item)==99
  slots=blocks(e)._slots(item);iid=const(item);key=blocks(e)._key()&65535
  found=[struct.unpack_from('<HH',blocks(e).sb1,o) for o in slots if struct.unpack_from('<H',blocks(e).sb1,o)[0]==iid]
  assert len(found)==1 and found[0][1]^key==99
 e.shot(str(out/'current-save-before-native-save.png'))
 loadedlocation=e.location()
 receipt=flash_reload(e,'edited-v125')
 same_records(e,b)
 for item in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY']:assert blocks(e).item_count(item)==99
 e.shot(str(out/'after-native-save-cold-continue.png'))
 profiles=[]
 for i in range(s.party_count()):
  m=Mon(bytearray(record(e)['party']),i*100);w=struct.unpack_from('<I',m.subs()['M'],4)[0]
  profiles.append({'slot':i,'species':m.species(),'pid':m.personality,'ot':m.otid,'iv':[(w>>(5*k))&31 for k in range(6)],'stats':list(struct.unpack_from('<7H',record(e)['party'],i*100+86))})
 assert digest(candidate.read_bytes())==beforehash
 assert digest((root/'saves/pokemonthyl_v1.25.sav').read_bytes())==inputhash
result={'pass':True,'rom_sha256':digest(rom.read_bytes()),'candidate_sha256':beforehash,'input_sha256':inputhash,'native_actual_menu_save_cold_reload':receipt,'party_and_all_PC_and_dex_identical':True,'items99_single_stack':True,'new_bad_eggs':0,'profiles':profiles,'location':loadedlocation,'readonly_emulator_memory':True}
(out/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
