from pathlib import Path
import hashlib,json,re,shutil,sys,struct,difflib
r=Path('/workspaces/pokefirered');w=r/'work/save-inventory-pp-20261013';facts=json.loads((w/'facts.json').read_text());before=w/'before';before.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
paths=list(facts['source']);original={f:(r/f).read_text() for f in paths}
for f in paths:assert sha((r/f).read_bytes())==facts['source'][f],('changed source',f)
for f in paths:
 p=before/f;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes((r/f).read_bytes())
for name in ['pokemonthyl.gba','pokemonthyl.elf','pokemonthyl.sym','pokemonthyl.map']:
 p=r/name
 if p.exists():shutil.copy2(p,before/name)
assert sha((r/'pokemonthyl.gba').read_bytes())==facts['rom_sha']
def calls(s,replacer):
 name='CalculatePPWithBonus(';positions=[];start=0
 while True:
  a=s.find(name,start)
  if a<0:break
  p=a+len(name);depth=1;j=p
  while depth:
   if s[j]=='(':depth+=1
   elif s[j]==')':depth-=1
   j+=1
  arg=s[p:j-1];parts=[];dep=0;beg=0
  for k,c in enumerate(arg):
   if c=='(':dep+=1
   elif c==')':dep-=1
   elif c==',' and dep==0:parts.append(arg[beg:k].strip());beg=k+1
  parts.append(arg[beg:].strip());assert len(parts)==3
  replacement=replacer(a,parts)
  if replacement:positions.append((a,j,replacement))
  start=j
 for a,j,v in reversed(positions):s=s[:a]+v+s[j:]
 return s,len(positions)
def once(s,a,b):
 assert s.count(a)==1,('expected one',a,s.count(a));return s.replace(a,b)
p=original['src/pokemon.c'];boxrestore=p.index('void BoxMonRestorePP(')
p,n=calls(p,lambda a,x:None if x[0].startswith('u16 ') else ('CalculateBoxMonPPWithBonus(boxMon, '+', '.join(x)+')' if a>boxrestore else 'CalculateMonPPWithBonus(mon, '+', '.join(x)+')'))
assert n==16,('pokemon calls',n)
helpers='''
// Keep the stock move table unchanged: only owned, permanent moves get this rule.
u8 CalculateBoxMonPPWithBonus(struct BoxPokemon *boxMon, u16 move, u8 ppBonuses, u8 moveIndex)
{
    u8 pp, basePP, ups;
    u8 otName[PLAYER_NAME_LENGTH + 1];
    u32 address = (u32)boxMon;

    if (move == MOVE_NONE || move >= MOVES_COUNT || moveIndex >= MAX_MON_MOVES)
        return 0;
    basePP = gBattleMoves[move].pp;
    pp = CalculatePPWithBonus(move, ppBonuses, moveIndex);
    // Wild and NPC parties can also have the player's original trainer ID.
    if (address >= (u32)gEnemyParty && address < (u32)(gEnemyParty + PARTY_SIZE))
        return pp;
    if (GetBoxMonData(boxMon, MON_DATA_IS_BAD_EGG, NULL)
     || GetBoxMonData(boxMon, MON_DATA_IS_EGG, NULL))
        return pp;
    GetBoxMonData(boxMon, MON_DATA_OT_NAME, otName);
    if (IsOtherTrainer(GetBoxMonData(boxMon, MON_DATA_OT_ID, NULL), otName))
        return pp;
    ups = (ppBonuses >> (2 * moveIndex)) & 3;
    if (GetBoxMonData(boxMon, MON_DATA_SPECIES, NULL) == SPECIES_PIKACHU)
    {
        // Apply the normal PP Up increments to the raised base, with no plateau.
        if (basePP < 15)
            basePP = 15;
        return basePP + basePP * ups / 5;
    }
    if (ups == 3 && basePP >= 5 && pp < 15)
        return 15;
    return pp;
}

u8 CalculateMonPPWithBonus(struct Pokemon *mon, u16 move, u8 ppBonuses, u8 moveIndex)
{
    return CalculateBoxMonPPWithBonus(&mon->box, move, ppBonuses, moveIndex);
}

u8 CalculateBattleMonMaxPP(u8 battler, u8 moveIndex)
{
    struct Pokemon *mon;
    u16 move;
    if (battler >= MAX_BATTLERS_COUNT || moveIndex >= MAX_MON_MOVES)
        return 0;
    move = gBattleMons[battler].moves[moveIndex];
    if (move == MOVE_NONE)
        return 0;
    if (GetBattlerSide(battler) == B_SIDE_PLAYER && MOVE_IS_PERMANENT(battler, moveIndex))
    {
        mon = &gPlayerParty[gBattlerPartyIndexes[battler]];
        if (move == GetMonData(mon, MON_DATA_MOVE1 + moveIndex, NULL))
            return CalculateMonPPWithBonus(mon, move, gBattleMons[battler].ppBonuses, moveIndex);
    }
    return CalculatePPWithBonus(move, gBattleMons[battler].ppBonuses, moveIndex);
}
'''
p=once(p,'void RemoveMonPPBonus(struct Pokemon *mon, u8 moveIndex)',helpers+'
void RemoveMonPPBonus(struct Pokemon *mon, u8 moveIndex)')
p=once(p,'            SetBoxMonData(boxMon, MON_DATA_PP1 + i, &gBattleMoves[move].pp);','            {
                u8 pp = CalculateBoxMonPPWithBonus(boxMon, move, GetBoxMonData(boxMon, MON_DATA_PP_BONUSES, NULL), i);
                SetBoxMonData(boxMon, MON_DATA_PP1 + i, &pp);
            }')
p=once(p,'    SetMonData(mon, MON_DATA_PP1 + slot, &gBattleMoves[move].pp);','    {
        u8 pp = CalculateMonPPWithBonus(mon, move, 0, slot);
        SetMonData(mon, MON_DATA_PP1 + slot, &pp);
    }')
# New final move has zero bonus bits after shifting; calculate with its own owner.
needle='    pp[MAX_MON_MOVES - 1] = gBattleMoves[move].pp;';assert p.count(needle)==2
p=p.replace(needle,'    pp[MAX_MON_MOVES - 1] = CalculateMonPPWithBonus(mon, move, 0, MAX_MON_MOVES - 1);',1)
p=p.replace(needle,'    pp[MAX_MON_MOVES - 1] = CalculateBoxMonPPWithBonus(boxMon, move, 0, MAX_MON_MOVES - 1);',1)
p=once(p,'            mon->pp[i] = gBattleMoves[move].pp;','            mon->pp[i] = CalculateBattleMonMaxPP(mon - gBattleMons, i);')
p=once(p,'    mon->pp[slot] = gBattleMoves[move].pp;','    mon->pp[slot] = CalculateBattleMonMaxPP(mon - gBattleMons, slot);')
updated={'src/pokemon.c':p}
h=original['include/pokemon.h'];a='u8 CalculatePPWithBonus(u16 move, u8 ppBonuses, u8 moveIndex);'
updated['include/pokemon.h']=once(h,a,a+'
u8 CalculateBoxMonPPWithBonus(struct BoxPokemon *boxMon, u16 move, u8 ppBonuses, u8 moveIndex);
u8 CalculateMonPPWithBonus(struct Pokemon *mon, u16 move, u8 ppBonuses, u8 moveIndex);
u8 CalculateBattleMonMaxPP(u8 battler, u8 moveIndex);')
p,n=calls(original['src/battle_main.c'],lambda a,x:'CalculateBattleMonMaxPP(gActiveBattler, i)');assert n==1;updated['src/battle_main.c']=p
p,n=calls(original['src/battle_util.c'],lambda a,x:'CalculateBattleMonMaxPP(battlerId, i)');assert n==1;updated['src/battle_util.c']=p
p,n=calls(original['src/script_pokemon_util.c'],lambda a,x:'CalculateMonPPWithBonus(&gPlayerParty[i], '+', '.join(x)+')');assert n==1;updated['src/script_pokemon_util.c']=p
p,n=calls(original['src/pokemon_summary_screen.c'],lambda a,x:'PokeSum_GetMaxPP(i)');assert n==2
p=once(p,'static u16 GetMonPpByMoveSlot(struct Pokemon * mon, u8 moveSlot);','static u16 GetMonPpByMoveSlot(struct Pokemon * mon, u8 moveSlot);
static u8 PokeSum_GetMaxPP(u8 i);')
preview='gBattleMoves[sMonSummaryScreen->moveIds[i]].pp, STR_CONV_MODE_LEFT_ALIGN, 3);';assert p.count(preview)==2;p=p.replace(preview,'PokeSum_GetMaxPP(i), STR_CONV_MODE_LEFT_ALIGN, 3);')
summ='''static u8 PokeSum_GetMaxPP(u8 i)
{
    u16 move = sMonSummaryScreen->moveIds[i];
    u8 slot = i < MAX_MON_MOVES ? i : 0;
    u8 bonus = i < MAX_MON_MOVES ? GetMonData(&sMonSummaryScreen->currentMon, MON_DATA_PP_BONUSES) : 0;
    if (move == MOVE_NONE)
        return 0;
    if (sMonSummaryScreen->isEnemyParty)
        return CalculatePPWithBonus(move, bonus, slot);
    return CalculateMonPPWithBonus(&sMonSummaryScreen->currentMon, move, bonus, slot);
}

'''
p=once(p,'static void PokeSum_PrintMoveName(u8 i)
{',summ+'static void PokeSum_PrintMoveName(u8 i)
{');updated['src/pokemon_summary_screen.c']=p
# Validate every edit before writing any source file.
patch=''.join(''.join(difflib.unified_diff(original[f].splitlines(True),updated[f].splitlines(True),fromfile=f,tofile=f)) for f in paths)
(w/'player-pp.patch').write_text(patch)
for f,t in updated.items():(r/f).write_text(t)
(w/'source-edit.json').write_text(json.dumps({'pass':True,'source_before':facts['source'],'source_after':{f:sha((r/f).read_bytes()) for f in paths},'changed_files':paths,'stock_gBattleMoves_untouched':True},indent=2))
# Edit only the explicitly selected player's SAV, never the existing original.
sys.path.insert(0,str(r/'tools/qa'));import gamedata as gd
from savefile import SaveFile,checksum
source=r/'saves/pokemonthyl_v1.25-items99-iv2x.sav';expected='158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5'
assert sha(source.read_bytes())==expected
s=SaveFile(str(source));assert s.party_count()==6
old={k:bytes(v) for k,v in s.blocks.items()};orig_raw=bytes(s.raw)
for name,sid,size in s.layout:
 phys=s.where[sid];base=phys*4096;data=orig_raw[base:base+size];assert checksum(data)==struct.unpack_from('<H',orig_raw,base+0xff6)[0],('source checksum',sid)
protected={str(x):sha(x.read_bytes()) for x in (r/'saves').rglob('*.sav')}
changed_items=[];allowed=set()
for item in ['ITEM_TINY_MUSHROOM','ITEM_PP_UP']:
 iid=gd.const(item);slots=s._slots(item);matches=[o for o in slots if struct.unpack_from('<H',s.sb1,o)[0]==iid]
 assert len(matches)<=1,('duplicate requested item',item)
 o=matches[0] if matches else next(o for o in slots if struct.unpack_from('<H',s.sb1,o)[0]==0)
 before_qty=s.item_count(item);struct.pack_into('<HH',s.sb1,o,iid,99^(s._key()&65535));allowed.update(range(o,o+4));changed_items.append({'item':item,'before':before_qty,'after':99,'slot_offset':o})
rom=gd.Rom();stride=facts['offsets']['battlemove'];ledger=[]
for i in range(6):
 m=s.party_mon(i);subs=m.subs();o=m.o
 assert m.otid==struct.unpack_from('<I',s.sb2,gd.off('sb2.playerTrainerId'))[0]
 assert not m.is_egg() and not (s.sb1[o+19]&1)
 assert (sum(z[0] for b in subs.values() for z in struct.iter_unpack('<H',b))&65535)==struct.unpack_from('<H',s.sb1,o+28)[0]
 before_subs={k:bytes(v) for k,v in subs.items()};species=m.species();before_bonus=subs['G'][8]
 for j,move in enumerate(struct.unpack_from('<4H',subs['A'],0)):
  if not move:continue
  base=rom.at(rom.syms['gBattleMoves']+move*stride+4,1)[0];oldpp=subs['A'][8+j];ups=(subs['G'][8]>>(2*j))&3
  if oldpp>=15:continue
  newups=3 if base<15 else ups
  subs['G'][8]=(subs['G'][8]&~(3<<(2*j)))|(newups<<(2*j));subs['A'][8+j]=15
  newmax=(max(base,15)*(5+newups)//5 if species==25 else max(base*(5+newups)//5,15) if newups==3 and base>=5 else base*(5+newups)//5)
  assert 15<=newmax
  ledger.append({'party_slot':i,'species':species,'move_slot':j,'move':move,'base_PP':base,'before_current_PP':oldpp,'before_PP_Up_count':ups,'after_PP_Up_count':newups,'after_current_PP':15,'after_max_PP':newmax})
 m.put_subs(subs)
 assert bytes(subs['E'])==before_subs['E'] and bytes(subs['M'])==before_subs['M']
 assert subs['G'][:8]==before_subs['G'][:8] and subs['G'][9:]==before_subs['G'][9:]
 assert subs['A'][:8]==before_subs['A'][:8]
 allowed.update(range(o+28,o+30));allowed.update(range(o+32,o+80))
assert len(ledger)==12
assert s.blocks['sb2']==old['sb2'] and s.blocks['storage']==old['storage']
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old['sb1'],s.sb1)))
for item in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY','ITEM_TINY_MUSHROOM','ITEM_PP_UP']:assert s.item_count(item)==99
candidate=w/'candidate';candidate.mkdir(exist_ok=True);output=candidate/'pokemonthyl_v1.25-items99-iv2x-pp15.sav';assert not output.exists();s.save(str(output));v=SaveFile(str(output))
assert v.counter==s.counter and v.slot==s.slot
for name,sid,size in v.layout:
 base=v.where[sid]*4096;assert checksum(v.raw[base:base+size])==struct.unpack_from('<H',v.raw,base+0xff6)[0]
assert v.blocks==s.blocks
inactive=(1-s.slot)*14*4096;assert v.raw[inactive:inactive+14*4096]==orig_raw[inactive:inactive+14*4096]
assert all(sha(Path(p).read_bytes())==h for p,h in protected.items())
report={'pass':True,'source':str(source),'source_sha256':expected,'candidate':str(output),'candidate_sha256':sha(output.read_bytes()),'counter':s.counter,'party_count':6,'adjusted_moves':ledger,'items':changed_items,'MasterBall_and_RareCandy_99_preserved':True,'party_IVs_and_EVs_and_moves_and_identity_preserved':True,'SB2_and_entire_PC_storage_unchanged':True,'other_SB1_bytes_unchanged':True,'inactive_save_slot_unchanged':True,'all_original_SAVs_unchanged':True,'active_14_sector_checksums_valid':True,'existing_BadEgg_repaired':False,'needs_matching_new_ROM':True}
(w/'save-validation.json').write_text(json.dumps(report,indent=2));print('PP_SOURCE_AND_SAV_READY',output,flush=True)
