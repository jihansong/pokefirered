#!/usr/bin/env python3
"""Construct a public CI_TEST TY28 flash image from zero buffers and source-derived ARM ABI.

There is deliberately no input-save, save-state, old-save editor, RAM-write or
game-execution option. Recipe changes are preboot synthetic test setup only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
from build_delta_host import checked_directory,output_path


def sha(raw):return hashlib.sha256(raw).hexdigest()


class Schema:
    def __init__(self,data):
        assert data['format']=='TY28_ARM_SOURCE_SCHEMA_V1'
        assert data['abi']=={'elf_machine':40,'pointer_bytes':4,'BoxPokemon_bytes':80,'Pokemon_bytes':100}
        self.data=data;self.values=data['values']

    def c(self,name):return self.values['constant.'+name]
    def size(self,name):return self.values['sizes.'+name]
    def offset(self,type_name,field):return self.values['offset.'+type_name+'.'+field]
    def width(self,type_name,field):return self.values['size.'+type_name+'.'+field]
    def resolve(self,value):
        if isinstance(value,int):return value
        key='constant.'+value
        return self.values[key] if key in self.values else int(value,0)

    def put(self,buffer,type_name,field,value,base=0):
        offset=base+self.offset(type_name,field);width=self.width(type_name,field)
        assert offset+width<=len(buffer)
        buffer[offset:offset+width]=(int(value)&((1<<(8*width))-1)).to_bytes(width,'little')

    def get(self,buffer,type_name,field,base=0):
        offset=base+self.offset(type_name,field);width=self.width(type_name,field)
        return int.from_bytes(buffer[offset:offset+width],'little')

    def bits(self,buffer,type_name,field,value,base=0):
        probe=self.data['bitfields'][type_name+'.'+field];assert 0<=value<=probe['maximum']
        offset=base+probe['offset'];width=probe['size'];before=int.from_bytes(buffer[offset:offset+width],'little')
        buffer[offset:offset+width]=((before&~probe['mask'])|(value<<probe['shift'])).to_bytes(width,'little')

    def text(self,value,width):
        raw=bytes(self.data['charmap'][char] for char in value)
        assert len(raw)<width or len(raw)==width
        return raw+bytes([self.data['charmap']['$']])*(width-len(raw))


def word_sum(raw):
    assert len(raw)%4==0
    return sum(struct.unpack('<'+str(len(raw)//4)+'I',raw))&0xffffffff


def sector_checksum(raw):
    total=word_sum(raw)
    return ((total>>16)+total)&0xffff


def mon_checksum(raw):
    assert len(raw)%2==0
    return sum(struct.unpack('<'+str(len(raw)//2)+'H',raw))&0xffff


def encode_mon(schema,recipe,index,trainer_id):
    s=schema;species=s.resolve(recipe['species']);level=int(recipe.get('level',100))
    assert 0<species<len(s.data['species']) and 1<=level<=s.c('MAX_LEVEL')
    info=s.data['species'][species];assert info['baseHP']>0
    pid=s.resolve(recipe.get('pid',0x51a70001+index*17))&0xffffffff
    ot=s.resolve(recipe.get('ot_id',trainer_id))&0xffffffff
    ivs=recipe.get('ivs',[31]*6);evs=recipe.get('evs',[0]*6)
    assert len(ivs)==len(evs)==6 and all(0<=v<=31 for v in ivs) and all(0<=v<=255 for v in evs) and sum(evs)<=510
    sub=[bytearray(s.size('PokemonSubstruct'+str(i))) for i in range(4)]
    assert all(len(part)==12 for part in sub)
    exp=s.data['experience'][info['growthRate']][level]
    s.put(sub[0],'PokemonSubstruct0','species',species)
    s.put(sub[0],'PokemonSubstruct0','heldItem',s.resolve(recipe.get('held_item','ITEM_NONE')))
    s.put(sub[0],'PokemonSubstruct0','experience',exp)
    s.put(sub[0],'PokemonSubstruct0','friendship',recipe.get('friendship',info['friendship']))
    moves=[s.resolve(move) for move in recipe.get('moves',['MOVE_TACKLE'])]
    assert 1<=len(moves)<=s.c('MAX_MON_MOVES');moves+= [s.c('MOVE_NONE')]*(s.c('MAX_MON_MOVES')-len(moves))
    for slot,move in enumerate(moves):
        assert str(move) in s.data['move_pp']
        base=s.offset('PokemonSubstruct1','moves')+slot*2;sub[1][base:base+2]=move.to_bytes(2,'little')
        sub[1][s.offset('PokemonSubstruct1','pp')+slot]=s.data['move_pp'][str(move)]
    ev_fields=['hpEV','attackEV','defenseEV','speedEV','spAttackEV','spDefenseEV']
    iv_fields=['hpIV','attackIV','defenseIV','speedIV','spAttackIV','spDefenseIV']
    for field,value in zip(ev_fields,evs):s.put(sub[2],'PokemonSubstruct2',field,value)
    for field,value in zip(iv_fields,ivs):s.bits(sub[3],'PokemonSubstruct3',field,value)
    s.put(sub[3],'PokemonSubstruct3','metLocation',recipe.get('met_location',0))
    for field,value in [('metLevel',level),('metGame',s.c('VERSION_LEAF_GREEN')),('pokeball',s.resolve(recipe.get('ball','ITEM_POKE_BALL'))),('otGender',0),('abilityNum',int(recipe.get('ability_slot',0))),('modernFatefulEncounter',int(recipe.get('fateful',False)))]:
        s.bits(sub[3],'PokemonSubstruct3',field,value)
    plaintext=bytearray(sum(map(len,sub)));positions=s.data['substruct_positions'][str(pid%24)]
    for logical,physical in enumerate(positions):plaintext[physical*12:(physical+1)*12]=sub[logical]
    card=bytearray(s.size('BoxPokemon'))
    s.put(card,'BoxPokemon','personality',pid);s.put(card,'BoxPokemon','otId',ot)
    nickname=recipe.get('nickname','CI'+str(index+1).zfill(3))
    start=s.offset('BoxPokemon','nickname');card[start:start+s.width('BoxPokemon','nickname')]=s.text(nickname,s.width('BoxPokemon','nickname'))
    start=s.offset('BoxPokemon','otName');card[start:start+s.width('BoxPokemon','otName')]=s.text('CI TEST',s.width('BoxPokemon','otName'))
    s.put(card,'BoxPokemon','language',s.c('LANGUAGE_ENGLISH'));s.bits(card,'BoxPokemon','hasSpecies',1)
    s.put(card,'BoxPokemon','checksum',mon_checksum(plaintext))
    encrypted=b''.join((word^pid^ot).to_bytes(4,'little') for word in struct.unpack('<12I',plaintext))
    start=s.offset('BoxPokemon','secure');card[start:start+len(encrypted)]=encrypted
    party=bytearray(s.size('Pokemon'));party[:len(card)]=card
    s.put(party,'Pokemon','level',level);s.put(party,'Pokemon','mail',s.c('MAIL_NONE'))
    bases=[info[field] for field in ['baseHP','baseAttack','baseDefense','baseSpeed','baseSpAttack','baseSpDefense']]
    stats=[((2*base+iv+ev//4)*level)//100 for base,iv,ev in zip(bases,ivs,evs)]
    stats[0]=1 if info['baseHP']==1 else stats[0]+level+10
    nature=s.data['natures'][pid%len(s.data['natures'])]
    for i,modifier in enumerate(nature,1):stats[i]=((stats[i]+5)*(110 if modifier>0 else 90 if modifier<0 else 100))//100
    for field,value in zip(['maxHP','attack','defense','speed','spAttack','spDefense'],stats):s.put(party,'Pokemon',field,value)
    s.put(party,'Pokemon','hp',stats[0])
    return bytes(card),bytes(party),{'species':species,'level':level,'pid':pid,'ot_id':ot,'moves':moves,'experience':exp,'checksum':s.get(card,'BoxPokemon','checksum')}


def set_flag(s,sb1,sb2,flag,value):
    flag=s.resolve(flag);assert flag>0
    if s.c('HOENN_FLAGS_START')<=flag<=s.c('HOENN_FLAGS_END'):
        target=sb2;index=flag-s.c('HOENN_FLAGS_START');base=s.offset('SaveBlock2','hoennFlags');capacity=s.width('SaveBlock2','hoennFlags')
    else:
        target=sb1;index=flag;base=s.offset('SaveBlock1','flags');capacity=s.width('SaveBlock1','flags')
    assert index//8<capacity,'Temporary/out-of-range flag is not serialized'
    mask=1<<(index&7);offset=base+index//8
    target[offset]=(target[offset]|mask) if value else (target[offset]&~mask)


def set_var(s,sb1,sb2,var,value):
    var=s.resolve(var);value=s.resolve(value);assert 0<=value<=65535
    if s.c('HOENN_VARS_START')<=var<=s.c('HOENN_VARS_END'):
        target=sb2;index=var-s.c('HOENN_VARS_START');base=s.offset('SaveBlock2','hoennVars');capacity=s.width('SaveBlock2','hoennVars')
    else:
        target=sb1;index=var-s.c('VARS_START');base=s.offset('SaveBlock1','vars');capacity=s.width('SaveBlock1','vars')
    assert 0<=index<capacity//2,'Special/out-of-range variable is not serialized'
    target[base+index*2:base+index*2+2]=value.to_bytes(2,'little')


def map_setup(s,source,recipe,sb1,sb2):
    token=recipe['map'];map_id=s.resolve(token)
    matches=[]
    for path in (source/'data/maps').glob('*/map.json'):
        item=json.loads(path.read_text(encoding='utf-8'))
        if item.get('id')==token:matches.append((path,item))
    assert len(matches)==1,'Map must be a unique source-defined MAP_* token'
    path,metadata=matches[0]
    layouts=json.loads((source/'data/layouts/layouts.json').read_text(encoding='utf-8'))['layouts']
    layout=next(item for item in layouts if item.get('id')==metadata['layout'])
    x,y=int(recipe['x']),int(recipe['y']);assert 0<=x<int(layout['width']) and 0<=y<int(layout['height'])
    for field in ['location','continueGameWarp','dynamicWarp','lastHealLocation','escapeWarp']:
        base=s.offset('SaveBlock1',field)
        for key,value in [('mapGroup',map_id>>8),('mapNum',map_id&255),('warpId',s.c('WARP_ID_NONE')),('x',x),('y',y)]:s.put(sb1,'WarpData',key,value,base)
    s.put(sb1,'Coords16','x',x,s.offset('SaveBlock1','pos'));s.put(sb1,'Coords16','y',y,s.offset('SaveBlock1','pos'))
    s.put(sb1,'SaveBlock1','mapLayoutId',s.c(metadata['layout']))
    if recipe.get('continue_warp',True):s.put(sb2,'SaveBlock2','specialSaveWarpFlags',s.c('CONTINUE_GAME_WARP'))
    return {path.relative_to(source).as_posix():sha(path.read_bytes())}


def initialize_bag(s,sb1,sb2,key,items):
    suffixes=['ITEMS','KEYITEMS','POKEBALLS','TMHM','BERRIES']
    fields=['bagPocket_Items','bagPocket_KeyItems','bagPocket_PokeBalls','bagPocket_TMHM','bagPocket_Berries']
    legacy=[s.c('BAG_'+name+'_COUNT_LEGACY') for name in suffixes]
    capacities=[s.c('BAG_'+name+'_COUNT') for name in suffixes]
    extra_offsets=[];running=0
    for count in legacy:extra_offsets.append(running);running+=count
    def slot(pocket,index):
        if index<legacy[pocket]:return sb1,s.offset('SaveBlock1',fields[pocket])+index*s.size('ItemSlot')
        extra=extra_offsets[pocket]+index-legacy[pocket]
        if extra<s.c('BAG_EXTRA_SB1_SLOTS'):return sb1,s.offset('SaveBlock1','unused_348C')+extra*s.size('ItemSlot')
        return sb2,s.offset('SaveBlock2','filler_DA0')+(extra-s.c('BAG_EXTRA_SB1_SLOTS'))*s.size('ItemSlot')
    for pocket,capacity in enumerate(capacities):
        for index in range(capacity):
            target,base=slot(pocket,index);s.put(target,'ItemSlot','quantity',key&65535,base)
    used=[set() for _ in capacities]
    for item in items:
        item_id=s.resolve(item['item']);quantity=int(item['quantity']);assert 0<item_id<s.c('ITEMS_COUNT') and 1<=quantity<=999
        pocket=s.data['item_pockets'][str(item_id)];assert 0<=pocket<len(capacities)
        index=int(item.get('slot',next((i for i in range(capacities[pocket]) if i not in used[pocket]),-1)))
        assert 0<=index<capacities[pocket] and index not in used[pocket];used[pocket].add(index)
        target,base=slot(pocket,index);s.put(target,'ItemSlot','itemId',item_id,base);s.put(target,'ItemSlot','quantity',quantity^(key&65535),base)
    base=s.offset('SaveBlock2','filler_DA0')+s.c('BAG_EXTRA_SB2_SLOTS')*s.size('ItemSlot')
    for field,value in [('magic1',s.c('BAG_EXTENSION_MAGIC1')),('magic2',s.c('BAG_EXTENSION_MAGIC2')),('quantityKey',key),('version',s.c('BAG_EXTENSION_VERSION')),('totalSlots',s.c('BAG_EXTRA_SLOT_COUNT'))]:s.put(sb2,'BagExtensionHeader',field,value,base)
    for i,capacity in enumerate(capacities):
        offset=base+s.offset('BagExtensionHeader','pocketCapacity')+i*2;sb2[offset:offset+2]=capacity.to_bytes(2,'little')


def payload_sizes(s):
    result=[];chunk=s.c('SECTOR_DATA_SIZE')
    for name,count in [('SaveBlock2',1),('SaveBlock1',s.c('SECTOR_ID_SAVEBLOCK1_END')-s.c('SECTOR_ID_SAVEBLOCK1_START')+1),('PokemonStorage',s.c('SECTOR_ID_PKMN_STORAGE_END')-s.c('SECTOR_ID_PKMN_STORAGE_START')+1),('PokemonStorageExtra',s.c('EXPANDED_SAVE_SECTOR_COUNT')-s.c('EXPANDED_SAVE_EXTRA_START'))]:
        for i in range(count):result.append(min(chunk,s.size(name)-i*chunk))
    assert len(result)==s.c('EXPANDED_SAVE_SECTOR_COUNT') and all(value>0 and value%4==0 for value in result)
    return result


def write_flash(s,blocks,counter):
    sector_size=s.c('SECTOR_SIZE');flash=bytearray([255])*(sector_size*s.c('SECTORS_COUNT'))
    payload=[];chunk=s.c('SECTOR_DATA_SIZE')
    for block in blocks:payload.extend(block[i:i+chunk] for i in range(0,len(block),chunk))
    assert list(map(len,payload))==payload_sizes(s)
    def sector(number,identifier,data):
        raw=bytearray(sector_size);raw[:len(data)]=data
        for field,value in [('id',identifier),('checksum',sector_checksum(data)),('signature',s.c('EXPANDED_SAVE_SIGNATURE')),('counter',counter)]:s.put(raw,'SaveSector',field,value)
        flash[number*sector_size:(number+1)*sector_size]=raw
    for i,data in enumerate(payload):sector(i,i,data)
    commit=bytearray(s.size('ExpandedSaveCommit'))
    aggregate=sum(word_sum(data) for data in payload)&0xffffffff
    for field,value in [('magic',s.c('EXPANDED_SAVE_COMMIT_MAGIC')),('version',s.c('EXPANDED_SAVE_VERSION')),('sectorCount',s.c('EXPANDED_SAVE_SECTOR_COUNT')),('counter',counter),('state',s.c('EXPANDED_SAVE_COMMIT_COMPLETE')),('aggregateSum',aggregate),('legacySize',s.c('EXPANDED_SAVE_LEGACY_PC_SIZE')),('extraSize',s.c('EXPANDED_SAVE_EXTRA_PC_SIZE'))]:s.put(commit,'ExpandedSaveCommit',field,value)
    sector(s.c('EXPANDED_SAVE_COMMIT_SECTOR'),s.c('EXPANDED_SAVE_COMMIT_ID'),commit)
    return bytes(flash)


def validate_ty28(raw,schema):
    s=schema if isinstance(schema,Schema) else Schema(schema);sector_size=s.c('SECTOR_SIZE')
    assert len(raw)==sector_size*s.c('SECTORS_COUNT')
    def read_sector(number,identifier,size,counter=None):
        sector=raw[number*sector_size:(number+1)*sector_size];data=sector[:size]
        assert s.get(sector,'SaveSector','id')==identifier
        assert s.get(sector,'SaveSector','signature')==s.c('EXPANDED_SAVE_SIGNATURE')
        assert s.get(sector,'SaveSector','checksum')==sector_checksum(data)
        if counter is not None:assert s.get(sector,'SaveSector','counter')==counter
        return data,sector
    commit,header=read_sector(s.c('EXPANDED_SAVE_COMMIT_SECTOR'),s.c('EXPANDED_SAVE_COMMIT_ID'),s.size('ExpandedSaveCommit'))
    counter=s.get(commit,'ExpandedSaveCommit','counter');assert counter==s.get(header,'SaveSector','counter')
    for field,value in [('magic',s.c('EXPANDED_SAVE_COMMIT_MAGIC')),('version',s.c('EXPANDED_SAVE_VERSION')),('sectorCount',s.c('EXPANDED_SAVE_SECTOR_COUNT')),('state',s.c('EXPANDED_SAVE_COMMIT_COMPLETE')),('legacySize',s.c('EXPANDED_SAVE_LEGACY_PC_SIZE')),('extraSize',s.c('EXPANDED_SAVE_EXTRA_PC_SIZE'))]:assert s.get(commit,'ExpandedSaveCommit',field)==value
    data=[read_sector(i,i,size,counter)[0] for i,size in enumerate(payload_sizes(s))]
    assert sum(word_sum(part) for part in data)&0xffffffff==s.get(commit,'ExpandedSaveCommit','aggregateSum')
    joined=b''.join(data);blocks=[];position=0
    for name in ['SaveBlock2','SaveBlock1','PokemonStorage','PokemonStorageExtra']:
        size=s.size(name);blocks.append(joined[position:position+size]);position+=size
    sb2,sb1,pc,extra=blocks;assert position==len(joined)
    assert s.get(pc,'PokemonStorage','currentBox')<s.c('TOTAL_BOXES_COUNT')
    assert 1<=s.get(sb1,'SaveBlock1','playerPartyCount')<=s.c('PARTY_SIZE')
    mons=[]
    def check_mon(card):
        pid=s.get(card,'BoxPokemon','personality');ot=s.get(card,'BoxPokemon','otId')
        offset=s.offset('BoxPokemon','secure');encrypted=card[offset:offset+s.width('BoxPokemon','secure')]
        plain=b''.join((word^pid^ot).to_bytes(4,'little') for word in struct.unpack('<12I',encrypted))
        assert mon_checksum(plain)==s.get(card,'BoxPokemon','checksum')
        position=s.data['substruct_positions'][str(pid%24)][0]*12
        species=s.get(plain[position:position+12],'PokemonSubstruct0','species')
        assert species<len(s.data['species'])
        return species
    for i in range(s.get(sb1,'SaveBlock1','playerPartyCount')):
        offset=s.offset('SaveBlock1','playerParty')+i*s.size('Pokemon');card=sb1[offset:offset+s.size('BoxPokemon')]
        species=check_mon(card);assert species>0;mons.append(species)
    count=0
    for block,type_name,boxes in [(pc,'PokemonStorage',s.c('LEGACY_BOXES_COUNT')),(extra,'PokemonStorageExtra',s.c('EXTRA_BOXES_COUNT'))]:
        for i in range(boxes*s.c('IN_BOX_COUNT')):
            offset=s.offset(type_name,'boxes')+i*s.size('BoxPokemon');count+=bool(check_mon(block[offset:offset+s.size('BoxPokemon')]))
    key=s.get(sb2,'SaveBlock2','encryptionKey');base=s.offset('SaveBlock2','filler_DA0')+s.c('BAG_EXTRA_SB2_SLOTS')*s.size('ItemSlot')
    for field,value in [('magic1',s.c('BAG_EXTENSION_MAGIC1')),('magic2',s.c('BAG_EXTENSION_MAGIC2')),('quantityKey',key),('version',s.c('BAG_EXTENSION_VERSION')),('totalSlots',s.c('BAG_EXTRA_SLOT_COUNT'))]:assert s.get(sb2,'BagExtensionHeader',field,base)==value
    for i,name in enumerate(['ITEMS','KEYITEMS','POKEBALLS','TMHM','BERRIES']):
        offset=base+s.offset('BagExtensionHeader','pocketCapacity')+i*2;assert int.from_bytes(sb2[offset:offset+2],'little')==s.c('BAG_'+name+'_COUNT')
    return {'status':'PASS','payload_sectors':len(data),'commit_sector':s.c('EXPANDED_SAVE_COMMIT_SECTOR'),'counter':counter,'party_species':mons,'pc_nonempty':count,'boxes':s.c('TOTAL_BOXES_COUNT'),'bag_global_key_consistent':True}


def construct(source,schema,recipe):
    s=Schema(schema);assert recipe.get('fixture_id')=='CI_TEST' and recipe.get('trainer_name','CI TEST')=='CI TEST'
    assert not recipe.get('parent_save_inputs',[]),'No save ancestry is accepted'
    for relative,digest in schema['source_sha256'].items():assert sha((source/relative).read_bytes())==digest,'Stale source schema: '+relative
    sb1=bytearray(s.size('SaveBlock1'));sb2=bytearray(s.size('SaveBlock2'))
    pc=bytearray(s.size('PokemonStorage'));extra=bytearray(s.size('PokemonStorageExtra'))
    trainer=s.resolve(recipe.get('trainer_id','0xC17E57A1'));key=s.resolve(recipe.get('encryption_key','0xC15E0F42'))
    start=s.offset('SaveBlock2','playerName');sb2[start:start+s.width('SaveBlock2','playerName')]=s.text('CI TEST',s.width('SaveBlock2','playerName'))
    s.put(sb2,'SaveBlock2','playerTrainerId',trainer);s.put(sb2,'SaveBlock2','encryptionKey',key)
    s.put(sb2,'SaveBlock2','playerGender',int(recipe.get('gender',0)));s.put(sb2,'SaveBlock2','unkFlag1',1)
    s.bits(sb2,'SaveBlock2','optionsTextSpeed',s.c('OPTIONS_TEXT_SPEED_FAST'))
    additional=map_setup(s,source,recipe,sb1,sb2)
    for type_name,base in [('lastBerryTreeUpdate',s.offset('SaveBlock2','lastBerryTreeUpdate')),('localTimeOffset',s.offset('SaveBlock2','localTimeOffset'))]:
        for field in ['days','hours','minutes','seconds']:s.put(sb2,'Time',field,recipe.get('clock',{}).get(field,0) if type_name=='lastBerryTreeUpdate' else 0,base)
    for flag,value in recipe.get('flags',{}).items():set_flag(s,sb1,sb2,flag,bool(value))
    for var,value in recipe.get('vars',{}).items():set_var(s,sb1,sb2,var,value)
    if recipe.get('pokedex',{}).get('national',False):
        settings=s.data['national_dex_settings'];s.put(sb2,'Pokedex','nationalMagic',settings['magic'],s.offset('SaveBlock2','pokedex'))
        set_flag(s,sb1,sb2,'FLAG_SYS_NATIONAL_DEX',True);set_var(s,sb1,sb2,'VAR_NATIONAL_DEX',settings['var_value'])
    for field,value in [('money',recipe.get('money',100000)^key),('coins',recipe.get('coins',0)^(key&65535)),('registeredItem',s.resolve(recipe.get('registered_item','ITEM_NONE')))]:s.put(sb1,'SaveBlock1',field,value)
    initialize_bag(s,sb1,sb2,key,recipe.get('items',[]))
    party=recipe['party'];assert 1<=len(party)<=s.c('PARTY_SIZE');s.put(sb1,'SaveBlock1','playerPartyCount',len(party));details=[]
    for i,entry in enumerate(party):
        card,mon,detail=encode_mon(s,entry,i,trainer);offset=s.offset('SaveBlock1','playerParty')+i*s.size('Pokemon');sb1[offset:offset+len(mon)]=mon;details.append(detail)
        if recipe.get('pokedex',{}).get('register_party',True):
            national=s.data['species_to_national'][detail['species']-1];assert national>0
            index,bit=divmod(national-1,8);mask=1<<bit;pokedex=s.offset('SaveBlock2','pokedex')
            for field in ['owned','seen']:sb2[pokedex+s.offset('Pokedex',field)+index]|=mask
            for field in ['seen1','seen2']:sb1[s.offset('SaveBlock1',field)+index]|=mask
    state=recipe.get('pc',{});s.put(pc,'PokemonStorage','currentBox',state.get('current_box',0))
    assert 0<=state.get('current_box',0)<s.c('TOTAL_BOXES_COUNT')
    for box in range(s.c('TOTAL_BOXES_COUNT')):
        block,type_name,index=(pc,'PokemonStorage',box) if box<s.c('LEGACY_BOXES_COUNT') else (extra,'PokemonStorageExtra',box-s.c('LEGACY_BOXES_COUNT'))
        width=s.c('BOX_NAME_LENGTH')+1;offset=s.offset(type_name,'boxNames')+index*width;block[offset:offset+width]=s.text('CI BOX'+str(box+1),width)
    pc_mons=list(state.get('mons',[]))
    if state.get('fill_all',False):
        assert not pc_mons
        pc_mons=[dict(state.get('fill_mon',{'species':'SPECIES_RATTATA','level':5}),box=box,slot=slot) for box in range(s.c('TOTAL_BOXES_COUNT')) for slot in range(s.c('IN_BOX_COUNT'))]
    occupied=set()
    for i,entry in enumerate(pc_mons):
        box,slot=int(entry['box']),int(entry['slot']);assert 0<=box<s.c('TOTAL_BOXES_COUNT') and 0<=slot<s.c('IN_BOX_COUNT') and (box,slot) not in occupied;occupied.add((box,slot))
        block,type_name,index=(pc,'PokemonStorage',box) if box<s.c('LEGACY_BOXES_COUNT') else (extra,'PokemonStorageExtra',box-s.c('LEGACY_BOXES_COUNT'))
        card,_,_=encode_mon(s,entry,i+1000,trainer);offset=s.offset(type_name,'boxes')+(index*s.c('IN_BOX_COUNT')+slot)*s.size('BoxPokemon');block[offset:offset+len(card)]=card
    counter=int(recipe.get('counter',1));assert 0<counter<0xffffffff
    raw=write_flash(s,[sb2,sb1,pc,extra],counter);report=validate_ty28(raw,s)
    corrupted=bytearray(raw);corrupted[0]^=1
    try:validate_ty28(corrupted,s)
    except AssertionError:report['negative_payload_checksum_control']='REJECTED'
    else:raise AssertionError('Validator accepted damaged payload')
    return raw,report,details,additional


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--artifact-dir',type=Path,required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--schema',type=Path,required=True)
    parser.add_argument('--recipe',type=Path,required=True)
    args=parser.parse_args()
    assert args.schema.suffix==args.recipe.suffix=='.json','Only schema/recipe JSON inputs are accepted'
    source=args.source.resolve(strict=True);root=checked_directory(args.artifact_dir);dest=output_path(root,args.output)
    assert dest.suffix=='.sav'
    provenance=output_path(root,args.output+'.provenance.json')
    schema_raw=args.schema.read_bytes();recipe_raw=args.recipe.read_bytes()
    schema=json.loads(schema_raw);recipe=json.loads(recipe_raw)
    raw,validation,party,additional=construct(source,schema,recipe)
    record={'status':'SYNTHETIC_TY28_CONSTRUCTED_NOT_BOOT_VERIFIED','fixture_id':'CI_TEST','parents':[],
            'save_inputs_read':0,'origin':'Zero buffers, source-defined GBA ABI/data and public recipe only',
            'trainer_label':'CI_TEST','in_game_trainer_name':'CI TEST','recipe':recipe,
            'recipe_sha256':sha(recipe_raw),'schema_sha256':sha(schema_raw),'source_sha256':schema['source_sha256'],
            'additional_map_source_sha256':additional,'output':dest.name,'bytes':len(raw),'sha256':sha(raw),
            'validation':validation,'party':party,'game_runs':0,'normal_SAVE_or_cold_Continue_verified':False}
    fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    with provenance.open('x',encoding='utf-8') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':record['status'],'output':dest.name,'sha256':record['sha256'],'validation':validation}))


if __name__=='__main__':main()
