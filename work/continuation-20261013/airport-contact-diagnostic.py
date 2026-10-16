from pathlib import Path
import sys,json,hashlib,struct
root=Path('/workspaces/pokefirered');out=root/'work/continuation-20261013/airport-contact-diagnostic';out.mkdir(exist_ok=True)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf';sav=root/'work/continuation-20261013/johto-continuous-walk-input/champion-airport-QA-only.sav'
sys.argv=['diag','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<readonly-definitions>','exec'))
with ReadOnlyEmu(str(rom),str(sav),sym='') as e:
 e.syms=syms;e.boot_continue();settle(e);rows=[]
 for i in range(16):
  p=syms['gObjectEvents']+36*i
  if e.u8(p)&1:
   xy=struct.unpack('<hh',e.read(p+off('misty_obj.coords'),4))
   rows.append({'slot':i,'local':e.u8(p+off('misty_obj.local')),'coords_raw':xy,'xy':[x-7 for x in xy],'raw':e.read(p,36).hex()})
 d={'location':e.location(),'objects':rows,'field_idle':e.field_idle()};(out/'objects.json').write_text(json.dumps(d));print(json.dumps(d))
