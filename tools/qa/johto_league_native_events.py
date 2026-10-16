#!/usr/bin/env python3
"""Native Johto League gates and retained/restarted challenge state."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_league_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='474c1ff4a38f7c8b77b8ef4bc826b9762a5a92ba09977a7616ffda6ad5aec136'
exec(compile(_boot_text,str(_boot),'exec'),globals())

cases=[]
def add(name,where,marker,**kw):cases.append(dict(name=name,where=where,marker=marker,**kw))
R27='JohtoRoute27';VR='JohtoVictoryRoad_1F';PC='JohtoLeague_PokemonCenter_1F'
PLATEAU='JohtoIndigoPlateau';HOF='JohtoLeague_HallOfFame'
for label,flags in [('kanto_champion_required',{SYS:False}),('johto_badge8_required',{B8:False}),('radio_rescue_required',{RADIO:False})]:
 add('east_road_'+label,(R27,0,20),R27+'_Text_NotReady',direction='RIGHT',step=True,flags=flags)
add('east_road_open_consumes_trigger',(R27,0,20),None,direction='RIGHT',step=True,open_gate=True)
add('victory_road_waits_for_silver',(VR,15,4),VR+'_Text_SilverWaiting',step=True)
add('victory_road_silver_opens_plateau',(VR,15,4),None,step=True,flags={SILVER_L:True},dest=PLATEAU,expect_flags={L_ARRIVED:True})
for label,flags in [('kanto',{SYS:False}),('badge8',{B8:False}),('radio',{RADIO:False}),('silver',{SILVER_L:False})]:
 baseflags={SILVER_L:True};baseflags.update(flags)
 add('reception_requires_'+label,(PC,4,8),PC+'_Text_NotReady',flags=baseflags)
finished={SILVER_L:True,L_CLEAR:True,**{f:True for f in ELITE_FLAGS}}
won={n:True for n in ELITE_ACTORS}
add('reception_no_keeps_wins_and_first_clear',(PC,4,8),PC+'_Text_Later',flags=finished,trainers=won,answer='NO')
add('reception_new_challenge_resets_only_elite',(PC,4,8),None,flags=finished,trainers=won,answer='YES',
 question=PC+'_Text_Challenge',dest=ROOMS['WILL'],expect_flags={f:False for f in ELITE_FLAGS},expect_trainers={n:False for n in ELITE_ACTORS})
for name in ELITE_ACTORS:
 room=ROOMS[name]
 add(name.lower()+'_saved_win_callback_reenters',POSITIONS[name],room+'_Text_After',
  flags=PRIOR[name],trainers={name:True},expect_flags={WINS[name]:True})
for i,name in enumerate(ELITE_ACTORS[1:],1):
 add(name.lower()+'_previous_elite_required',POSITIONS[name],ROOMS[name]+'_Text_PriorNotReady')
for i,name in enumerate(ELITE_ACTORS):
 room=ROOMS[name];dest=ROOMS[ELITE_ACTORS[i+1]] if i+1<len(ELITE_ACTORS) else HOF
 add(name.lower()+'_next_room_locked',(room,6,3),room+'_Text_GateClosed',step=True,flags=PRIOR[name])
 add(name.lower()+'_next_room_opens',(room,6,3),None,step=True,flags={**PRIOR[name],WINS[name]:True},dest=dest)
all_elite={f:True for f in ELITE_FLAGS}
for label,flags in [('kanto',{SYS:False}),('champion',{LANCE:False}),('first_elite',{WILL:False})]:
 baseflags=dict(all_elite);baseflags.update(flags)
 add('hof_requires_'+label,(HOF,6,6),HOF+'_Text_NotReady',flags=baseflags)
add('hof_no_defers_registration',(HOF,6,6),HOF+'_Text_Later',flags=all_elite,answer='NO')
add('plateau_before_registration',(PLATEAU,9,11),PLATEAU+'_Text_Challenge')
add('plateau_recognizes_registered_champion',(PLATEAU,9,11),PLATEAU+'_Text_Champion',flags={L_CLEAR:True})
assert len(cases)==37
_league_base_interaction=interaction
def interaction(e,c):
 if c.get('answer')!='YES' or not c.get('dest'):return _league_base_interaction(e,c)
 # Challenge YES warps immediately and does not have a post-answer dialogue.
 native_step(e,c.get('direction','UP'))
 question=e.read(syms[c['question']],256).split(b'\xff')[0][:24]
 seen=False
 for _ in range(200):
  if question in e.sym_read('gStringVar4',256):seen=True
  if yes_no_ready(e):break
  e.press('A',hold=1,after=8)
 assert seen and yes_no_ready(e),(c['name'],'challenge question not ready')
 e.press('A',hold=1,after=12);settle(e)
 assert e.in_overworld() and not e.in_battle()
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='johto-league-native-events-') as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav');prepared=fixture(target,c)
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c)
    if c.get('open_gate'):
     native_step(e,'RIGHT');assert e.location()[2:]==(2,20),'road coord trigger repeats after allowing travel'
    after=snapshot(e);expected_trainers=dict(before['trainers']);expected_trainers.update(c.get('expect_trainers',{}))
    assert after['flags']==existing_flags(before,c),(c['name'],'story flags',after['flags'],existing_flags(before,c))
    assert after['trainers']==expected_trainers,(c['name'],'trainer progress')
    for item in ITEMS:assert after['items'][item]==before['items'][item],(c['name'],item)
    assert_preserved(before,after,c['name'])
    if c.get('dest'):
     d=map_info(c['dest']);assert e.location()[:2]==(d['group'],d['num']),(c['name'],'native warp',e.location())
    e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
    row={'case':c['name'],'native_dialogue':c['marker'],'save':saved,'party_pc_dex_preserved':True,
     'fixture_kanto_clear_explicit':prepared.flag(SYS),'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==37
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,
 'eligible_initial_test_fixture_explicitly_sets_kanto_champion_flag':True,'campaign_playthrough_claimed':False,
 'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
