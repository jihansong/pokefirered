"""Read-only GBA ELF/ROM/native-sprite verification; writes JSON to stdout only."""
import argparse, hashlib, json, struct, sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
ROM_BASE, ROM_END = 0x08000000, 0x0A000000
SAVE_NAMES = ('gSaveBlock1', 'gSaveBlock2', 'gPokemonStorage',
              'gSaveBlock1Ptr', 'gSaveBlock2Ptr', 'gPokemonStoragePtr')
NATIVE_SHA = 'd4c139c593480d915ef2052fe47b427f46dc266f6230942da96384336791a31d'
def sha(data): return hashlib.sha256(data).hexdigest()
def cstr(data, offset):
    if not 0 <= offset < len(data): raise ValueError('ELF string offset outside table')
    end=data.find(b'\0',offset)
    if end < 0: raise ValueError('unterminated ELF string')
    return data[offset:end].decode('utf-8',errors='replace')
@dataclass(frozen=True)
class Symbol:
    name:str; addr:int; size:int; section:str; binding:int; kind:int; unit:str
    def key(self): return (self.name,self.addr,self.size,self.section)
class Elf:
    def __init__(self,path):
        self.path=Path(path); self.data=self.path.read_bytes()
        if len(self.data)<52 or self.data[:7]!=b'\x7fELF\x01\x01\x01':
            raise ValueError('expected ELF32 little-endian')
        h=struct.unpack_from('<HHIIIIIHHHHHH',self.data,16)
        etype,machine,_,_,phoff,shoff,_,ehsize,phsize,phnum,shsize,shnum,names=h
        if etype!=2 or machine!=40 or ehsize<52 or shsize<40:
            raise ValueError('expected linked ARM ET_EXEC with section headers')
        first=self.unpack('<10I',shoff)
        shnum=shnum or first[5]
        names=first[6] if names==0xffff else names
        phnum=first[7] if phnum==0xffff else phnum
        if not 0<shnum<65536 or not 0<=names<shnum: raise ValueError('invalid section table')
        self.sections=[self.unpack('<10I',shoff+i*shsize) for i in range(shnum)]
        strings=self.section_data(self.sections[names])
        self.section_names=[cstr(strings,s[0]) for s in self.sections]
        if phnum and phsize<32: raise ValueError('invalid program header stride')
        self.segments=[self.unpack('<8I',phoff+i*phsize) for i in range(phnum)]
        self.symbols=[]
        for section in self.sections:
            if section[1]!=2: continue # Full SHT_SYMTAB, including locals.
            _,_,_,_,offset,size,link,_,_,stride=section
            if stride<16 or size%stride or not 0<=link<shnum: raise ValueError('invalid symbol table')
            names_data=self.section_data(self.sections[link]); unit=''
            for i in range(size//stride):
                nameoff,addr,length,info,_,index=self.unpack('<IIIBBH',offset+i*stride)
                name=cstr(names_data,nameoff); kind,binding=info&15,info>>4
                if kind==4: unit=name; continue
                if not name or index==0: continue
                label='ABS' if index==0xfff1 else 'COMMON' if index==0xfff2 else self.section_names[index] if index<shnum else hex(index)
                self.symbols.append(Symbol(name,addr,length,label,binding,kind,unit))
        if not self.symbols: raise ValueError('ELF has no full defined symbol table')
    def unpack(self,fmt,offset):
        if offset<0 or offset+struct.calcsize(fmt)>len(self.data): raise ValueError('ELF structure outside file')
        return struct.unpack_from(fmt,self.data,offset)
    def section_data(self,section):
        offset,length=section[4],section[5]
        if section[1]==8: return b''
        if offset+length>len(self.data): raise ValueError('ELF section outside file')
        return self.data[offset:offset+length]
    def ram(self):
        return [s for s in self.symbols if 0x02000000<=s.addr<=0x02040000 or 0x03000000<=s.addr<=0x03008000]
    def unique(self,name):
        found=[s for s in self.symbols if s.name==name]
        if len(found)!=1: raise ValueError(f'{name}: expected one defined symbol, found {len(found)}')
        return found[0]
def records(counter):
    return [{'name':k[0],'addr':hex(k[1]),'size':k[2],'section':k[3],'count':n} for k,n in sorted(counter.items())]
def compare_ram(baseline,candidate):
    old=Counter(s.key() for s in baseline.ram()); new=Counter(s.key() for s in candidate.ram())
    missing,added=old-new,new-old; dup=Counter(s.name for s in baseline.ram()); save=[]
    for name in SAVE_NAMES:
        before,after=baseline.unique(name),candidate.unique(name)
        save.append({'name':name,'baseline':{'addr':hex(before.addr),'size':before.size,'section':before.section},
                     'candidate':{'addr':hex(after.addr),'size':after.size,'section':after.section},
                     'pass':before.key()==after.key() and before.size>0})
    return {'pass':not missing and not added and all(s['pass'] for s in save),
            'baseline_symbol_count':sum(old.values()),'candidate_symbol_count':sum(new.values()),
            'baseline_duplicate_local_names':{k:v for k,v in sorted(dup.items()) if v>1},
            'removed_or_changed':records(missing),'added_or_changed':records(added),'save_abi':save}
def segment_match(elf,rom):
    checks=[]
    for index,segment in enumerate(elf.segments):
        kind,offset,_,physical,filesz,_,_,_=segment
        if kind!=1 or filesz==0 or not ROM_BASE<=physical<ROM_END: continue
        if offset+filesz>len(elf.data): raise ValueError('ELF load segment outside file')
        start=physical-ROM_BASE; expected=elf.data[offset:offset+filesz]; actual=rom[start:start+filesz]
        checks.append({'index':index,'physical_addr':hex(physical),'bytes':filesz,
                       'pass':len(actual)==filesz and actual==expected,'elf_sha256':sha(expected),'rom_sha256':sha(actual)})
    return {'pass':bool(checks) and all(c['pass'] for c in checks),'segments':checks}
def symbol_rom(elf,rom,name):
    symbol=elf.unique(name)
    if symbol.size<=0 or not ROM_BASE<=symbol.addr<ROM_END: raise ValueError(f'{name}: not sized ROM data')
    start=symbol.addr-ROM_BASE; data=rom[start:start+symbol.size]
    if len(data)!=symbol.size: raise ValueError(f'{name}: ROM range truncated')
    return symbol,data
def encode_png(path,pal_path):
    from PIL import Image
    image=Image.open(path)
    if image.mode!='P' or image.size!=(144,32) or image.info.get('transparency')!=0:
        raise ValueError('sprite must be indexed 144x32, index0 transparent')
    pixels=image.tobytes()
    if any(p>=16 for p in pixels): raise ValueError('sprite exceeds 4bpp indexes')
    lines=Path(pal_path).read_text(encoding='ascii').splitlines()
    if lines[:3]!=['JASC-PAL','0100','16'] or len(lines)!=19: raise ValueError('expected JASC-PAL16')
    colors=[tuple(map(int,line.split())) for line in lines[3:]]
    if any(len(c)!=3 or any(v<0 or v>255 for v in c) for c in colors): raise ValueError('invalid palette')
    if image.getpalette()[:48]!=[v for c in colors for v in c]: raise ValueError('PNG is not indexed to player palette')
    output=bytearray()
    for frame in range(9):
        for ty in range(4):
            for tx in range(2):
                for y in range(8):
                    row=(ty*8+y)*144+frame*16+tx*8
                    for x in range(0,8,2): output.append(pixels[row+x]|(pixels[row+x+1]<<4))
    frames=[image.crop((i*16,0,i*16+16,32)).tobytes() for i in range(9)]
    if len(set(frames))!=9: raise ValueError('nine distinct walk poses required')
    palette=b''.join(struct.pack('<H',(r>>3)|((g>>3)<<5)|((b>>3)<<10)) for r,g,b in colors)
    return bytes(output),palette
def run(args):
    baseline,candidate=Elf(args.baseline_elf),Elf(args.candidate_elf)
    before_rom,after_rom=Path(args.baseline_rom).read_bytes(),Path(args.candidate_rom).read_bytes()
    png=Path(args.png)
    if sha(png.read_bytes())!=args.expected_png_sha: raise ValueError('PNG hash differs from reviewed v4')
    native,palette=encode_png(png,args.palette)
    symbol,installed=symbol_rom(candidate,after_rom,'gObjectEventPic_MistyCompanion')
    _,installed_palette=symbol_rom(candidate,after_rom,'gObjectEventPal_Player')
    built,regenerated=Path(args.built_4bpp).read_bytes(),Path(args.regenerated_4bpp).read_bytes()
    sprite={'pass':installed==native==built==regenerated and installed_palette==palette,
            'rom_symbol_addr':hex(symbol.addr),'rom_symbol_bytes':symbol.size,'expected_bytes':len(native),
            'unique_frames':9,'png_sha256':sha(png.read_bytes()),'png_independent_4bpp_sha256':sha(native),
            'built_4bpp_sha256':sha(built),'clean_regenerated_4bpp_sha256':sha(regenerated),'rom_4bpp_sha256':sha(installed),
            'player_palette_exact_in_rom':installed_palette==palette}
    preserve=[]
    for name in args.preserve_symbol or ['gObjectEventPic_Misty','gObjectEventPal_Player']:
        old,old_data=symbol_rom(baseline,before_rom,name); new,new_data=symbol_rom(candidate,after_rom,name)
        preserve.append({'name':name,'pass':old_data==new_data,'bytes':old.size,
                         'baseline_addr':hex(old.addr),'candidate_addr':hex(new.addr),
                         'baseline_sha256':sha(old_data),'candidate_sha256':sha(new_data)})
    report={'check':'READ_ONLY_GBA_RAM_ABI_AND_MISTY_NATIVE_V4',
            'files':{label:{'path':str(path),'sha256':sha(Path(path).read_bytes())} for label,path in
                     [('baseline_elf',args.baseline_elf),('candidate_elf',args.candidate_elf),
                      ('baseline_rom',args.baseline_rom),('candidate_rom',args.candidate_rom)]},
            'ram':compare_ram(baseline,candidate),'baseline_rom_elf':segment_match(baseline,before_rom),
            'candidate_rom_elf':segment_match(candidate,after_rom),'native_sprite':sprite,'preserved_rom_assets':preserve,
            'limitations':['RAM/save object address and size preservation does not prove identical save field offsets.',
                           'Byte-for-byte save loads, emulator walk/tint/collision tests and DELTA tests are separate.']}
    report['pass']=all(report[k]['pass'] for k in ['ram','baseline_rom_elf','candidate_rom_elf','native_sprite']) and all(p['pass'] for p in preserve)
    return report
def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ['baseline-elf','candidate-elf','baseline-rom','candidate-rom','png','palette','built-4bpp','regenerated-4bpp']:
        p.add_argument('--'+flag,required=True)
    p.add_argument('--expected-png-sha',default=NATIVE_SHA)
    p.add_argument('--preserve-symbol',action='append',help='ROM symbol bytes to preserve; repeatable')
    return p
if __name__=='__main__':
    try: report=run(parser().parse_args())
    except Exception as exc:
        print(json.dumps({'pass':False,'error':f'{type(exc).__name__}: {exc}'},indent=2)); sys.exit(2)
    print(json.dumps(report,indent=2)); sys.exit(0 if report['pass'] else 1)
