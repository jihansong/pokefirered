#!/usr/bin/env python3
"""Export save-layout constants from a freshly compiled GBA ARM object, without executing it."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import shlex
import struct
import subprocess
import tempfile
from build_delta_host import checked_directory, output_path


def sha(raw):return hashlib.sha256(raw).hexdigest()


class ArmObject:
    def __init__(self,path):
        self.raw=Path(path).read_bytes()
        assert self.raw[:6]==b'\x7fELF\x01\x01','Little-endian ELF32 required'
        header=struct.unpack_from('<HHIIIIIHHHHHH',self.raw,16)
        assert header[0]==1 and header[1]==40,'Relocatable ARM object required'
        self.sections=[struct.unpack_from('<IIIIIIIIII',self.raw,header[5]+i*header[10]) for i in range(header[11])]
        self.symbols={}
        for section in self.sections:
            if section[1]!=2:continue
            strings=self.sections[section[6]];names=self.raw[strings[4]:strings[4]+strings[5]]
            for offset in range(section[4],section[4]+section[5],section[9]):
                name,value,size,info,other,index=struct.unpack_from('<IIIBBH',self.raw,offset)
                if not name or not size or index<=0 or index>=len(self.sections):continue
                label=names[name:names.index(b'\0',name)].decode('ascii')
                target=self.sections[index]
                if target[1]==8:continue
                begin=target[4]+value-target[3]
                self.symbols[label]=self.raw[begin:begin+size]

    def get(self,name):return self.symbols[name]


def declaration(text,name):
    match=re.search(r'^[^\n;{}]*\b'+re.escape(name)+r'\b[^;]*?=\s*\{.*?^\};',text,re.M|re.S)
    if not match:raise ValueError('Missing source data declaration: '+name)
    return match.group()


def function(text,name):
    match=re.search(r'^[^\n;{}]*\b'+re.escape(name)+r'\([^;]*?\)\s*\n\{.*?^\}',text,re.M|re.S)
    if not match:raise ValueError('Missing source function: '+name)
    return match.group()


BITFIELDS={
    'BoxPokemon':['hasSpecies','isEgg','isBadEgg','isStarterPikachu','isSnagged'],
    'PokemonSubstruct3':['metLevel','metGame','pokeball','otGender','hpIV','attackIV','defenseIV','speedIV','spAttackIV','spDefenseIV','isEgg','abilityNum','modernFatefulEncounter'],
    'SaveBlock2':['optionsTextSpeed','optionsWindowFrameType','optionsSound','optionsBattleStyle','optionsBattleSceneOff','regionMapZoom'],
    'ObjectEvent':['active','currentElevation','facingDirection'],
}
PREFIXES=('FLAG_','VAR_','ITEM_','MOVE_','SPECIES_','MAP_','HOENN_','BAG_','VARS_','FLAGS_',
          'SPECIAL_FLAGS','SPECIAL_VARS','SECTOR_','SECTORS_','EXPANDED_SAVE_','POCKET_',
          'OPTIONS_','STAT_','GROWTH_','NATURE_','VERSION_','MAX_','NUM_NATURE','NATIONAL_DEX_','LAYOUT_')
EXACT={'LEGACY_BOXES_COUNT','TOTAL_BOXES_COUNT','EXTRA_BOXES_COUNT','IN_BOX_COUNT','BOX_NAME_LENGTH',
       'NUM_BAG_POCKETS','PARTY_SIZE','LANGUAGE_ENGLISH','GAME_VERSION','GAME_LANGUAGE','EOS','MAIL_NONE',
       'PLAYER_NAME_LENGTH','POKEMON_NAME_LENGTH','TRAINER_ID_LENGTH','DEX_FLAGS_NO','NUM_FLAG_BYTES',
       'NUM_SECTORS_PER_SLOT','MAX_DEFAULT_WALLPAPER','WARP_ID_NONE','NUM_SPECIES','MOVES_COUNT','ITEMS_COUNT','CONTINUE_GAME_WARP','MAP_OFFSET'}


def derive(source,artifact_dir,output,compiler):
    if platform.system()!='Linux':raise RuntimeError('ARM schema compilation is Linux-only')
    source=source.resolve(strict=True);root=checked_directory(artifact_dir);dest=output_path(root,output)
    inputs={}
    def read(relative):
        raw=(source/relative).read_bytes();inputs[relative]=sha(raw)
        return raw.decode('utf-8')
    global_header=read('include/global.h');pokemon_header=read('include/pokemon.h')
    pokemon=read('src/pokemon.c');item=read('src/item.c');event=read('src/event_data.c')
    read('src/save.c');read('include/expanded_save.h')
    work=Path(tempfile.mkdtemp(prefix='ty28-schema-',dir=root));assert work.parent==root
    # These definitions are copied from the supplied source, not from a save.
    bag_defines='\n'.join(re.findall(r'^#define BAG_(?:EXTRA_|EXTENSION_)[^\n]+',item,re.M))
    bag_struct=re.search(r'^struct BagExtensionHeader\s*\{.*?^\};',item,re.M|re.S).group()
    (work/'fixture_bag_schema.inc').write_text(bag_defines+'\n'+bag_struct+'\n',encoding='utf-8')
    names=set(EXACT)
    header_files=['include/global.h','include/pokemon.h','include/save.h','include/expanded_save.h',
                  'include/pokemon_storage_system.h','include/constants/global.h','include/constants/flags.h',
                  'include/constants/vars.h','include/constants/species.h','include/constants/pokemon.h',
                  'include/constants/items.h','include/constants/moves.h','include/constants/maps.h',
                  'include/constants/map_groups.h','include/constants/pokedex.h','include/fieldmap.h','include/save_location.h']
    header_files+=sorted(p.relative_to(source).as_posix() for p in (source/'include/constants').glob('*.h'))
    for path in header_files:
        text=read(path)
        for match in re.finditer(r'^#define[ \t]+([A-Za-z_]\w*)([^\n]*)',text,re.M):
            name,rest=match.groups()
            if rest.startswith('('):continue
            if name.startswith(PREFIXES):names.add(name)
    names.update(re.findall(r'^#define\s+(BAG_(?:EXTRA_|EXTENSION_)\w+)',bag_defines,re.M))
    assert max(len('constant.'+name) for name in names)<96
    (work/'fixture_constants.inc').write_text('\n'.join('#ifdef '+name+'\nCONSTANT('+name+'),\n#endif' for name in sorted(names))+'\n',encoding='utf-8')
    probes=[]
    for type_name,fields in BITFIELDS.items():
        header=global_header if type_name=='SaveBlock2' else read('include/global.fieldmap.h') if type_name=='ObjectEvent' else pokemon_header
        block=re.search(r'^struct '+type_name+r'\s*\{.*?^\};',header,re.M|re.S).group()
        for field in fields:
            width=int(re.search(r'\b'+field+r'\s*:\s*(\d+)',block).group(1))
            probes.append('const struct '+type_name+' gTyBit_'+type_name+'_'+field+' = {.'+field+' = '+str((1<<width)-1)+'};')
    (work/'fixture_bitfields.inc').write_text('\n'.join(probes)+'\n',encoding='utf-8')
    nature=declaration(pokemon,'sNatureStatTable').replace('static const','const',1).replace('sNatureStatTable','gTyNatureStatTable')
    (work/'fixture_natures.inc').write_text(nature+'\n',encoding='utf-8')
    national=declaration(pokemon,'sSpeciesToNationalPokedexNum').replace('static const','const',1).replace('sSpeciesToNationalPokedexNum','gTySpeciesToNational')
    national_macro=re.search(r'^#define SPECIES_TO_NATIONAL[^\n]+',pokemon,re.M).group()
    (work/'fixture_species_to_national.inc').write_text(national_macro+'\n'+national+'\n',encoding='utf-8')
    generator=Path(__file__).with_name('derive_save_schema.c')
    obj=work/'schema.o';dep=work/'schema.d'
    command=[compiler,'-std=gnu11','-c','-O0','-mcpu=arm7tdmi','-mthumb','-mabi=apcs-gnu',
             '-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=0','-iquote',str(source/'include'),
             '-iquote',str(source/'src'),'-I'+str(work),'-MMD','-MF',str(dep),str(generator),'-o',str(obj)]
    target=subprocess.check_output([compiler,'-dumpmachine'],text=True).strip()
    if not target.startswith('arm-none-eabi'):raise ValueError('Native GBA ARM cross-compiler required')
    result=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (work/'compile.log').write_text(result.stdout,encoding='utf-8')
    if result.returncode:raise RuntimeError('GBA ABI export failed; see '+str((work/'compile.log').relative_to(root)))
    elf=ArmObject(obj);records=elf.get('gTyFixtureSchema');values={}
    assert len(records)%100==0
    for offset in range(0,len(records),100):
        name=records[offset:offset+96].split(b'\0',1)[0].decode('ascii')
        assert name and name not in values
        values[name]=struct.unpack_from('<I',records,offset+96)[0]
    bitfields={}
    for type_name,fields in BITFIELDS.items():
        for field in fields:
            raw=elf.get('gTyBit_'+type_name+'_'+field);indices=[i for i,v in enumerate(raw) if v]
            assert indices
            first,last=min(indices),max(indices);mask=int.from_bytes(raw[first:last+1],'little')
            shift=(mask&-mask).bit_length()-1;maximum=mask>>shift
            assert maximum&(maximum+1)==0
            bitfields[type_name+'.'+field]={'offset':first,'size':last-first+1,'mask':mask,'shift':shift,'maximum':maximum}
    species_raw=elf.get('gSpeciesInfo');species_size=values['sizes.SpeciesInfo'];species=[]
    assert len(species_raw)%species_size==0
    for begin in range(0,len(species_raw),species_size):
        species.append({field:species_raw[begin+values['offset.SpeciesInfo.'+field]] for field in ['baseHP','baseAttack','baseDefense','baseSpeed','baseSpAttack','baseSpDefense','friendship','growthRate']})
    level_count=values['constant.MAX_LEVEL']+1
    experience=struct.unpack('<'+str(len(elf.get('gExperienceTables'))//4)+'I',elf.get('gExperienceTables'))
    experience=[list(experience[i:i+level_count]) for i in range(0,len(experience),level_count)]
    raw=elf.get('gTyNatureStatTable');nature_width=values['constant.NUM_NATURE_STATS']
    natures=struct.unpack('<'+str(len(raw))+'b',raw)
    natures=[list(natures[i:i+nature_width]) for i in range(0,len(natures),nature_width)]
    permutations={int(n):list(map(int,(a,b,c,d))) for n,a,b,c,d in re.findall(r'SUBSTRUCT_CASE\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',pokemon)}
    assert set(permutations)==set(range(24)) and all(sorted(v)==[0,1,2,3] for v in permutations.values())
    moves=read('src/data/battle_moves.h');move_pp={}
    for name,body in re.findall(r'\[(MOVE_\w+)\]\s*=\s*\{(.*?)\}',moves,re.S):
        pp=re.search(r'\.pp\s*=\s*(\d+)',body)
        if pp:move_pp[str(values['constant.'+name])]=int(pp[1])
    items=json.loads(read('src/data/items.json'))['items']
    pockets={str(values['constant.'+entry['itemId']]):values['constant.'+entry['pocket']]-1 for entry in items}
    charmap={}
    for label,byte in re.findall(r"^'([^']+)'\s*=\s*([0-9A-Fa-f]{2})\s*$",read('charmap.txt'),re.M):
        if len(label)==1 and label not in charmap:charmap[label]=int(byte,16)
    national_fn=function(event,'EnableNationalPokedex') if re.search(r'\bEnableNationalPokedex\(',event) else function(event,'EnableNationalPokedex_RSE')
    national_settings={'magic':int(re.search(r'nationalMagic\s*=\s*(0x[\dA-Fa-f]+|\d+)',national_fn)[1],0),
                       'var_value':int(re.search(r'\*nationalDexVar\s*=\s*(0x[\dA-Fa-f]+|\d+)',national_fn)[1],0)}
    raw=elf.get('gTySpeciesToNational');national=list(struct.unpack('<'+str(len(raw)//2)+'H',raw))
    for path in ['src/data/pokemon/species_info.h','src/data/pokemon/experience_tables.h','data/maps/map_groups.json','data/layouts/layouts.json']:
        read(path)
    # Compiler dependency output also binds transitive project headers to this schema.
    dependencies=shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1])
    for name in dependencies:
        path=Path(name)
        try:relative=path.resolve().relative_to(source).as_posix()
        except ValueError:continue
        if path.is_file():inputs[relative]=sha(path.read_bytes())
    report={'format':'TY28_ARM_SOURCE_SCHEMA_V1','target':target,'object_sha256':sha(obj.read_bytes()),
            'abi':{'elf_machine':40,'pointer_bytes':4,'BoxPokemon_bytes':values['sizes.BoxPokemon'],'Pokemon_bytes':values['sizes.Pokemon']},
            'values':values,'bitfields':bitfields,'species':species,'experience':experience,'natures':natures,
            'substruct_positions':permutations,'move_pp':move_pp,'item_pockets':pockets,'charmap':charmap,
            'species_to_national':national,'national_dex_settings':national_settings,
            'source_sha256':dict(sorted(inputs.items())),'generator_sha256':{'derive_save_schema.c':sha(generator.read_bytes()),'derive_schema.py':sha(Path(__file__).read_bytes())},
            'save_inputs_read':0,'game_runs':0,'scope':'Target ARM compile/object inspection only; no target code execution'}
    with dest.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':'ARM_SCHEMA_EXPORTED_NO_GAME_RUN','output':dest.name,'sha256':sha(dest.read_bytes()),'records':len(values)}))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--artifact-dir',type=Path,required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--arm-cc',default='arm-none-eabi-gcc')
    args=parser.parse_args();derive(args.source,args.artifact_dir,args.output,args.arm_cc)


if __name__=='__main__':main()
