"""Rebind an existing compiler-derived ABI after a script-only ROM rebuild.
Offsets are retained only when their source hashes and all RAM symbols match.
All symbol rows are selected again from the new ELF, including private owners.
This does not claim a new compiler probe or native test execution.
"""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,hashlib,json,struct,copy
OLD_ROM='0845f8cbc1afa5d957a64f76a4ae2700606175dd55bcd101184e6ba2a650b7fa'
OLD_ELF='e625069ea9379ea3dc2f83e3014fb741a2e0b7383f41f6d56bc37fc0eae6f17b'
OLD_ABI='fb95943ada51c72d99456b5127fe147878593e166c2e9d12a9b46d0a4fb6ffac'
SAVE_NAMES=['gSaveBlock1','gSaveBlock2','gPokemonStorage','gSaveBlock1Ptr','gSaveBlock2Ptr','gPokemonStoragePtr']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse(path):
 raw=Path(path).read_bytes();assert len(raw)>=52 and raw[:7]==b'\x7fELF\x01\x01\x01'
 h=struct.unpack_from('<16sHHIIIIIHHHHHH',raw);assert h[1]==2 and h[2]==40 and h[8]>=52 and h[11]==40
 assert h[6]+h[12]*40<=len(raw) and h[13]<h[12]
 sections=[struct.unpack_from('<10I',raw,h[6]+i*40)for i in range(h[12])]
 def data(s):
  assert s[4]+s[5]<=len(raw);return raw[s[4]:s[4]+s[5]]
 def cstr(b,p):
  assert 0<=p<len(b);end=b.find(b'\0',p);assert end>=p;return b[p:end].decode('utf-8')
 names_data=data(sections[h[13]]);section_names=[cstr(names_data,s[0])for s in sections]
 rows=defaultdict(list);flat=[]
 for symsec in sections:
  if symsec[1]!=2:continue
  assert symsec[9]==16 and symsec[5]%16==0 and symsec[6]<len(sections)
  strings=data(sections[symsec[6]]);owner=None
  for offset in range(0,symsec[5],16):
   no,value,size,info,other,index=struct.unpack_from('<IIIBBH',raw,symsec[4]+offset)
   name=cstr(strings,no)
   if info&15==4:owner=name;continue
   if not name or not index:continue
   row={'value':value,'size':size,'section':index,'info':info,'translation_unit':owner,'symbol_index':offset//16}
   label='ABS'if index==0xfff1 else'COMMON'if index==0xfff2 else section_names[index]if index<len(sections)else hex(index)
   rows[name].append(row);flat.append((name,value,size,label,info))
 return raw,sections,rows,flat
def ram_rows(flat):return Counter((n,v,z,s)for n,v,z,s,i in flat if 0x02000000<=v<=0x02040000 or 0x03000000<=v<=0x03008000)
def owner(s):return Path(s or '').name.removesuffix('.o').removesuffix('.c')
def validate_row(row,sections):
 kind=row['info']&15;v=row['value'];size=row['size'];assert row['section']<len(sections)
 q=sections[row['section']];lo=v&~1 if kind==2 else v
 assert kind in[1,2] and size>0 and q[2]&2 and q[3]<=lo and lo+size<=q[3]+q[5]
 if kind==2:assert q[2]&4 and 0x08000000<=lo and lo+size<=0x0a000000
 elif q[2]&1:assert(0x02000000<=v and v+size<=0x02040000)or(0x03000000<=v and v+size<=0x03008000)
 else:assert 0x08000000<=v and v+size<=0x0a000000
def main():
 p=argparse.ArgumentParser()
 for arg in['root','baseline-elf','old-abi','rom','elf','out']:p.add_argument('--'+arg,required=True,type=Path)
 p.add_argument('--expect-rom-sha',required=True);p.add_argument('--expect-elf-sha',required=True)
 a=p.parse_args();root=a.root.resolve(strict=True);a.out=a.out.resolve();assert a.out.is_relative_to(root/'work')and not a.out.exists()
 for arg in['baseline_elf','old_abi','rom','elf']:setattr(a,arg,getattr(a,arg).resolve(strict=True))
 assert sha(a.baseline_elf)==OLD_ELF and sha(a.old_abi)==OLD_ABI
 assert sha(a.rom)==a.expect_rom_sha and sha(a.elf)==a.expect_elf_sha
 assert a.expect_rom_sha!=OLD_ROM and a.expect_elf_sha!=OLD_ELF
 old=json.loads(a.old_abi.read_text());assert old['rom_sha256']==OLD_ROM and old['elf_sha256']==OLD_ELF
 protected={f:sha(f)for f in set((root/'saves').rglob('*.sav'))|{a.baseline_elf,a.old_abi,a.rom,a.elf}}
 for rel,wanted in old['source_sha256'].items():
  f=(root/rel).resolve(strict=True);assert f.is_relative_to(root)and sha(f)==wanted,('Compiler-derived offset source changed',rel)
  protected[f]=wanted
 _,bs,br,bf=parse(a.baseline_elf);raw,sections,rows,flat=parse(a.elf)
 before,after=ram_rows(bf),ram_rows(flat);assert before==after,('RAM addresses/sizes/duplicate symbols changed',list((before-after).elements()),list((after-before).elements()))
 assert sum(before.values())==1179,'Baseline does not have the1179 verified RAM symbols'
 save=[]
 for name in SAVE_NAMES:
  assert len(br[name])==len(rows[name])==1
  oldrow,newrow=br[name][0],rows[name][0];validate_row(oldrow,bs);validate_row(newrow,sections)
  assert oldrow['value']==newrow['value']and oldrow['size']==newrow['size']and oldrow['size']>0
  save.append({'name':name,'address':hex(newrow['value']),'size':newrow['size'],'unchanged':True})
 rom=a.rom.read_bytes();loaded=[]
 for i,q in enumerate(sections):
  if q[1]==8 or not q[2]&2 or not q[5]or not 0x08000000<=q[3]<0x0a000000:continue
  start=q[3]-0x08000000;assert q[4]+q[5]<=len(raw)and start+q[5]<=len(rom)
  assert raw[q[4]:q[4]+q[5]]==rom[start:start+q[5]],('New ELF/ROM section mismatch',i)
  loaded.append({'section_index':i,'bytes':q[5],'address':hex(q[3])})
 assert loaded
 new=copy.deepcopy(old);new['rom_sha256']=a.expect_rom_sha;new['elf_sha256']=a.expect_elf_sha;bindings={}
 for name,wanted in old['symbol_bindings'].items():
  options=[r for r in rows[name]if r['info']==wanted['info']and r['size']==wanted['size']]
  if len(rows[name])>1:options=[r for r in options if owner(r['translation_unit'])==owner(wanted['translation_unit'])]
  assert len(options)==1,('Missing/ambiguous rebuilt source-owned ABI symbol',name,options)
  row=options[0];validate_row(row,sections);bindings[name]=row
 new['symbol_bindings']=bindings
 new['native_qa_executed']=False
 new['method']=str(old.get('method',''))+'; current ELF rows rebound after verified script-only rebuild; existing compiler offsets retained under unchanged-source/full-RAM guards'
 new['symbol_binding_method']='Current rebuilt ELF STT_FILE ownership, exact type/size, unique row, section containment; all1179 baseline RAM rows unchanged'
 new['script_only_rebinding']={'prior_ABI_sha256':OLD_ABI,'prior_ELF_sha256':OLD_ELF,'compiler_offsets_reprobed':False,'compiler_offset_sources_unchanged':True,'full_RAM_symbol_count':1179,'SaveBlock_storage_layout_unchanged':save,'new_ELF_ROM_section_match':loaded}
 assert all(f.exists()and sha(f)==h for f,h in protected.items()),'Protected input changed during ABI rebinding'
 new['protected_inputs_unchanged']=True;a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(new,indent=2)+'\n')
 print(json.dumps({'status':'ELF_REBOUND_NOT_NATIVE_TESTED','output':str(a.out),'ABI_sha256':sha(a.out),'RAM_symbols_unchanged':1179,'SaveBlock_storage_layout_unchanged':save,'native_QA_executed':False},indent=2))
if __name__=='__main__':main()
