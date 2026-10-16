from pathlib import Path
import json, struct, argparse
p=argparse.ArgumentParser()
p.add_argument('--base',default='saves/pokemonthyl_v1.2.sav')
p.add_argument('--out',default='tools/qa/cases/johto_cherrygrove_route30.jsonl')
a=p.parse_args();r=Path('.').resolve();out=r/a.out
assert (r/a.base).exists()
cases=[]
G='FLAG_JOHTO_MET_CHERRYGROVE_GUIDE';M='FLAG_JOHTO_MR_POKEMON_BRIEFED'
E='FLAG_JOHTO_ELM_REPORT_DELIVERED';L='FLAG_JOHTO_MET_LAB_ASSISTANT'
A='FLAG_JOHTO_ARRIVAL_BRIEFED';C='FLAG_GOT_CYNDAQUIL_FROM_AIDE'
def add(name,where,steps,flags=None,extra=None):
 f={A:1,L:1,G:0,M:0,E:0,C:1};f.update(flags or {})
 cases.append({'name':'johto_cherrygrove_'+name,'base':a.base,
 'edit':['warp '+where,'noquestlog']+[f'flag {k} {v}' for k,v in f.items()]+(extra or []),'steps':steps})
def ex(k,v):return f'expect flag {k} = {v}'
def talk(d,label,after):
 return ['watch '+label,d,'A','mash','expect saw '+label+' = 1','expect overworld']+after
add('guide_requires_lab','CherrygroveCity 30 14',talk('RIGHT','CherrygroveCity_Text_GuideBeforeLab',[ex(G,0),ex(M,0),ex(E,0)]),{L:0})
add('guide_first_and_repeat','CherrygroveCity 30 14',talk('RIGHT','CherrygroveCity_Text_GuideRequest',[ex(G,1),ex(M,0),'A','mash',ex(G,1),'expect overworld']))
add('guide_after_report','CherrygroveCity 30 14',talk('RIGHT','CherrygroveCity_Text_GuideReportDone',[ex(E,1)]),{G:1,M:1,E:1})
add('mr_pokemon_requires_referral','JohtoRoute30_MrPokemonsHouse 4 6',talk('UP','JohtoRoute30_MrPokemonsHouse_Text_BeforeReferral',[ex(M,0),ex(E,0)]))
add('mr_pokemon_first_and_repeat','JohtoRoute30_MrPokemonsHouse 4 6',talk('UP','JohtoRoute30_MrPokemonsHouse_Text_ResearchReport',[ex(M,1),ex(E,0),'A','mash',ex(M,1),'expect overworld']),{G:1})
add('mr_pokemon_after_report','JohtoRoute30_MrPokemonsHouse 4 6',talk('UP','JohtoRoute30_MrPokemonsHouse_Text_AfterReport',[ex(M,1),ex(E,1)]),{G:1,M:1,E:1})
add('oak_aide_links_regions','JohtoRoute30_MrPokemonsHouse 7 6',talk('UP','JohtoRoute30_MrPokemonsHouse_Text_OaksAide',[ex(M,0),ex(E,0)]),{G:1})
mp=json.loads((r/'data/maps/NewBarkTown_ElmsLab/map.json').read_text())
npc=next(o for o in mp['object_events'] if o.get('script')=='NewBarkTown_ElmsLab_Researcher')
layout=next(x for x in json.loads((r/'data/layouts/layouts.json').read_text())['layouts'] if x.get('id')==mp['layout'])
w,h=layout['width'],layout['height'];raw=struct.unpack('<'+'H'*(w*h),(r/layout['blockdata_filepath']).read_bytes())
occupied={(o['x'],o['y']) for o in mp['object_events']}
adj=[(npc['x'],npc['y']+1,'UP'),(npc['x']-1,npc['y'],'RIGHT'),(npc['x']+1,npc['y'],'LEFT'),(npc['x'],npc['y']-1,'DOWN')]
valid=[(x,y,d) for x,y,d in adj if 0<=x<w and 0<=y<h and not ((raw[y*w+x]>>10)&3) and (x,y) not in occupied]
assert valid,'inspect assistant counter interaction fixture'
x,y,d=valid[0];where=f'NewBarkTown_ElmsLab {x} {y}'
add('elm_requires_report',where,[d,'A','mash','expect overworld',ex(E,0),ex(C,1)],{G:1})
add('elm_report_once_preserves_gift',where,talk(d,'NewBarkTown_ElmsLab_Text_ResearchReportDelivered',[ex(E,1),ex(C,1),'A','mash','expect overworld',ex(E,1),ex(C,1)]),{G:1,M:1})
add('elm_report_independent_of_gift_decline',where,['watch NewBarkTown_ElmsLab_Text_ResearchReportDelivered',d,'A','mashtext NewBarkTown_ElmsLab_Text_CyndaquilOffer 100','wait 60','B','mash','expect overworld',ex(E,1),ex(C,0),'expect saw NewBarkTown_ElmsLab_Text_ResearchReportDelivered = 1'],{G:1,M:1,C:0})
add('airstrip_north_connection','JohtoCherrygroveAirstrip 23 1',['UP 2','wait 60','expect map CherrygroveCity','expect overworld','shot airport_to_city'])
add('city_south_connection','CherrygroveCity 23 26',['DOWN 2','wait 60','expect map JohtoCherrygroveAirstrip','expect overworld'])
add('city_route30_connection','CherrygroveCity 19 1',['UP 2','wait 60','expect map JohtoRoute30','expect overworld','shot city_to_route30'])
add('route30_city_connection','JohtoRoute30 7 46',['DOWN 2','wait 60','expect map CherrygroveCity','expect overworld'])
for tag,src,xy,dst in [('center','CherrygroveCity','26 9','CherrygroveCity_PokemonCenter_1F'),('mart','CherrygroveCity','28 22','CherrygroveCity_Mart'),('guide_house','CherrygroveCity','13 22','CherrygroveCity_GuideHouse'),('mr_house','JohtoRoute30','15 7','JohtoRoute30_MrPokemonsHouse')]:
 add(tag+'_door_roundtrip',src+' '+xy,['UP','wait 90','expect map '+dst,'expect overworld','shot '+tag,('DOWN 3' if tag=='center' else 'DOWN'),'wait 90','expect map '+src,'expect overworld'])
add('center_heals','CherrygroveCity_PokemonCenter_1F 7 4',['watch Text_WelcomeWantToHealPkmn', 'wait 60', 'UP', 'wait 30', 'A', 'mashtext Text_WelcomeWantToHealPkmn 40', 'wait 60', 'A', 'mash', 'expect saw Text_WelcomeWantToHealPkmn = 1', 'expect overworld', 'expect hp 0 = full', 'shot healed'],extra=['hp 0 1'])
negative=dict(cases[0]);negative['name']='johto_cherrygrove_negative_gate_control';negative['steps']=negative['steps'][:-3]+[ex(G,1)];negative['xfail']=True;cases.append(negative)
assert len(cases)==20
out.parent.mkdir(parents=True,exist_ok=True)
data=''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases)
assert not out.exists() or out.read_text()==data,'existing cases differ'
out.write_text(data,encoding='utf8')
print(json.dumps({'cases':len(cases),'assistant_fixture':[x,y,d],'path':str(out),'native_execution':'pending'}))
