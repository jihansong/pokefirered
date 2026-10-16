#!/usr/bin/env python3
"""Add eight story-unlocked Johto Fly destinations, using existing saves and heal IDs."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
MARK='JOHTO_FLY_DESTINATIONS_V1'
ROWS=[
 ('NEW_BARK_TOWN','FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_JOHTO_ELM_REPORT_DELIVERED','MAP_NEW_BARK_TOWN','HEAL_LOCATION_NONE',11,10),
 ('CHERRYGROVE_CITY','FLAG_JOHTO_MET_CHERRYGROVE_GUIDE','FLAG_JOHTO_ELM_REPORT_DELIVERED','MAP_CHERRYGROVE_CITY','HEAL_LOCATION_CHERRYGROVE_CITY',26,9),
 ('VIOLET_CITY','FLAG_JOHTO_SPROUT_TOWER_CLEARED','FLAG_JOHTO_BADGE01_GET','MAP_VIOLET_CITY','HEAL_LOCATION_VIOLET_CITY',7,27),
 ('AZALEA_TOWN','FLAG_JOHTO_KURT_RESCUE_REQUESTED','FLAG_JOHTO_BADGE02_GET','MAP_AZALEA_TOWN','HEAL_LOCATION_AZALEA_TOWN',7,23),
 ('GOLDENROD_CITY','FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED','FLAG_JOHTO_BADGE03_GET','MAP_GOLDENROD_CITY','HEAL_LOCATION_GOLDENROD_CITY',8,29),
 ('ECRUTEAK_CITY','FLAG_JOHTO_BURNED_TOWER_INVESTIGATED','FLAG_JOHTO_BADGE04_GET','MAP_ECRUTEAK_CITY','HEAL_LOCATION_ECRUTEAK_CITY',8,29),
 ('OLIVINE_CITY','FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED','FLAG_JOHTO_BADGE06_GET','MAP_OLIVINE_CITY','HEAL_LOCATION_OLIVINE_CITY',7,20),
 ('CIANWOOD_CITY','FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED','FLAG_JOHTO_BADGE05_GET','MAP_CIANWOOD_CITY','HEAL_LOCATION_CIANWOOD_CITY',5,25)]
TABLE='''// JOHTO_FLY_DESTINATIONS_V1
struct JohtoFlyDestination
{
    u16 mapsec;
    u16 visitFlag;
    u16 alternateVisitFlag;
    u8 destination[3];
    s8 x;
    s8 y;
};

static const struct JohtoFlyDestination sJohtoFlyDestinations[] = {
'''+''.join('    {MAPSEC_'+sec+', '+flag+', '+alt+', {MAP('+city+'), '+heal+'}, '+str(x)+', '+str(y)+'},\n' for sec,flag,alt,city,heal,x,y in ROWS)+'''};

static const struct JohtoFlyDestination *GetJohtoFlyDestination(u16 mapsec)
{
    u32 i;
    for (i = 0; i < NELEMS(sJohtoFlyDestinations); i++)
        if (sJohtoFlyDestinations[i].mapsec == mapsec)
            return &sJohtoFlyDestinations[i];
    return NULL;
}

static bool8 JohtoFlyDestinationWasVisited(const struct JohtoFlyDestination *destination)
{
    return FlagGet(destination->visitFlag)
        || FlagGet(destination->alternateVisitFlag);
}

'''
def sha(b):return hashlib.sha256(b).hexdigest()
def once(t,old,new,label):
 if new in t:
  assert t.count(new)==1,(label,'duplicate new anchor')
  return t
 assert t.count(old)==1,(label,'original anchor differs')
 return t.replace(old,new,1)
def function(t,name):
 pat=re.compile(r'(?:static\s+)?(?:const\s+)?[A-Za-z_][A-Za-z0-9_]*(?:\s*\*)?\s+'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{')
 hits=list(pat.finditer(t));assert len(hits)==1,(name,'function count')
 m=hits[0];depth=1;i=m.end()
 while depth:
  assert i<len(t),(name,'unterminated body')
  if t[i]=='{':depth+=1
  elif t[i]=='}':depth-=1
  i+=1
 return t[m.start():i]
def change_function(t,name,edit):
 old=function(t,name);new=edit(old);assert old!=new,(name,'no delta')
 assert t.count(old)==1;return t.replace(old,new,1)
def build(root):
 path=root/'src/region_map.c';raw=path.read_bytes();t=raw.decode()
 assert 'REGIONMAP_JOHTO_ENTRY' in t and 'MAPSEC_CIANWOOD_CITY' in t
 heals=json.loads((root/'src/data/heal_locations.json').read_text())['heal_locations']
 for sec,flag,alt,city,heal,x,y in ROWS:
  if heal!='HEAL_LOCATION_NONE':
   hits=[v for v in heals if v.get('id')==heal];assert len(hits)==1
   assert (hits[0]['map'],hits[0]['x'],hits[0]['y'])==(city,x,y),('heal target changed',heal)
 groups=json.loads((root/'data/maps/map_groups.json').read_text());towns=[x for x in groups['gMapGroup_JohtoEntry'] if x in ['NewBarkTown','CherrygroveCity','VioletCity','AzaleaTown','GoldenrodCity','EcruteakCity','OlivineCity','CianwoodCity']]
 assert len(towns)==8
 section_ids={x['id'] for x in json.loads((root/'src/data/region_map/region_map_sections.json').read_text())['map_sections'] if x.get('id')}
 flag_defs=(root/'include/constants/flags_johto_story.h').read_text()
 for sec,flag,alt,*_ in ROWS:assert 'MAPSEC_'+sec in section_ids and re.search(r'^#define\s+'+flag+r'\b',flag_defs,re.M) and re.search(r'^#define\s+'+alt+r'\b',flag_defs,re.M)
 newbark=json.loads((root/'data/maps/NewBarkTown/map.json').read_text());layouts=json.loads((root/'data/layouts/layouts.json').read_text())['layouts']
 layout=next(v for v in layouts if v.get('id')==newbark['layout']);b=(root/layout['blockdata_filepath']).read_bytes()
 import struct
 tile=struct.unpack_from('<H',b,2*(10*layout['width']+11))[0]
 assert (tile>>10)&3==0 and tile>>12==3,('NewBark safe landing changed',hex(tile))
 for key in ['object_events','warp_events','coord_events','bg_events']:
  assert not any((v.get('x'),v.get('y'))==(11,10) for v in newbark[key]),('NewBark landing has event',key)
 if MARK in t:
  assert TABLE in t,'different Johto Fly table'
  assert 'JOHTO_FLY_ICON_SCOPE_V1' in t and 'johtoDestination->destination[2]' in t
  return raw,raw,{'already_synchronized':True}
 if '#include "constants/flags_johto_story.h"' not in t:
  t=once(t,'#include "constants/maps.h"','#include "constants/maps.h"\n#include "constants/flags_johto_story.h"','Johto Fly flags include')
 t=once(t,'static const u8 sMapFlyDestinations[][3] = {',TABLE+'static const u8 sMapFlyDestinations[][3] = {','Johto Fly table')
 def maptype(f):
  return once(f,'{\n    // Hoenn',"{\n    const struct JohtoFlyDestination *johtoDestination = GetJohtoFlyDestination(mapsec);\n\n    if (johtoDestination != NULL)\n        return JohtoFlyDestinationWasVisited(johtoDestination) ? MAPSECTYPE_VISITED : MAPSECTYPE_NOT_VISITED;\n\n    // Hoenn",'Johto map type')
 t=change_function(t,'GetMapsecType',maptype)
 def destination(f):
  old='    u16 idx;\n'
  new='''    u16 idx;
    const struct JohtoFlyDestination *johtoDestination = GetJohtoFlyDestination(mapsec);

    if (johtoDestination != NULL)
    {
        if (!JohtoFlyDestinationWasVisited(johtoDestination))
            return;
        if (johtoDestination->destination[2] != HEAL_LOCATION_NONE)
            SetWarpDestinationToHealLocation(johtoDestination->destination[2]);
        else
            SetWarpDestination(johtoDestination->destination[0], johtoDestination->destination[1], -1, johtoDestination->x, johtoDestination->y);
        SetUsedFlyQuestLogEvent(johtoDestination->destination);
        ReturnToFieldFromFlyMapSelect();
        return;
    }
'''
  f=once(f,old,new,'Johto Fly destination')
  return once(f,'    idx = mapsec - KANTO_MAPSEC_START;','    idx = mapsec - KANTO_MAPSEC_START;\n    if (idx >= NELEMS(sMapFlyDestinations))\n        return;','Kanto Fly table bounds')
 t=change_function(t,'SetFlyWarpDestination',destination)
 def flyicons(f):
  old='''        for (i = 0; i < REGIONMAP_COUNT; i++)
        {
'''
  new=old+'''            // JOHTO_FLY_ICON_SCOPE_V1: Johto has no cross-region switch.
            if ((GetSelectedRegionMap() == REGIONMAP_JOHTO_ENTRY) != (i == REGIONMAP_JOHTO_ENTRY))
                continue;
'''
  f=once(f,old,new,'Johto Fly icon scope')
  f=once(f,'                        CreateFlyIconSprite(i, numIcons, x, y, numIcons + 100, 10);','                        if (numIcons >= NELEMS(sMapIcons->flyIcons))\n                            return;\n                        CreateFlyIconSprite(i, numIcons, x, y, numIcons + 100, 10);','Fly icon capacity')
  return once(f,'                        numIcons++;','                        if (sMapIcons->flyIcons[numIcons].sprite != NULL)\n                            numIcons++;','Fly icon allocation count')
 t=change_function(t,'CreateFlyIcons',flyicons)
 def dungeonicons(f):
  f=once(f,'    u8 mapsec;\n','    u8 mapsec;\n    if (GetSelectedRegionMap() == REGIONMAP_JOHTO_ENTRY)\n        return;\n','Johto has no dungeon layer')
  f=once(f,'                CreateDungeonIconSprite(i, numIcons, x, y, numIcons + 35, 10);','                if (numIcons >= NELEMS(sMapIcons->dungeonIcons))\n                    return;\n                CreateDungeonIconSprite(i, numIcons, x, y, numIcons + 35, 10);\n                if (sMapIcons->dungeonIcons[numIcons].sprite == NULL)\n                    continue;','Dungeon icon capacity')
  return f
 t=change_function(t,'CreateDungeonIcons',dungeonicons)
 for name in ['CreateFlyIconSprite','CreateDungeonIconSprite']:
  def spriteguard(f):
   matches=list(re.finditer(r'(    spriteId = CreateSprite\([\s\S]*?\);\n)',f));assert len(matches)==1,(name,'CreateSprite anchor')
   old=matches[0].group(1);new=old+'''    if (spriteId == MAX_SPRITES)
    {
        FreeSpriteTilesByTag(tileTag);
        return;
    }
'''
   return once(f,old,new,'CreateSprite failure guard')
  t=change_function(t,name,spriteguard)
 for name,member in [('SetFlyIconInvisibility','flyIcons'),('SetDungeonIconInvisibility','dungeonIcons')]:
  def invisibleguard(f):
   f=once(f,'if (sMapIcons->'+member+'[i].region == whichMap || whichMap == 0xFF)','if (sMapIcons->'+member+'[i].sprite != NULL && (sMapIcons->'+member+'[i].region == whichMap || whichMap == 0xFF))','all icon NULL guard')
   op='==' if member=='flyIcons' else '!='
   return once(f,'if (sMapIcons->'+member+'[iconNum].region '+op+' whichMap)','if (iconNum < NELEMS(sMapIcons->'+member+') && sMapIcons->'+member+'[iconNum].sprite != NULL && sMapIcons->'+member+'[iconNum].region '+op+' whichMap)','single icon NULL guard')
  t=change_function(t,name,invisibleguard)
 # Heap struct, global pointers, region layouts, palette and established maps remain exact.
 for name in ['MapIcons','MapIconSprite','FlyMap']:
  pat=r'struct '+name+r'\s*\{[^{}]*\};';assert re.search(pat,raw.decode()).group()==re.search(pat,t).group()
 assert raw.decode().count('static EWRAM_DATA')==t.count('static EWRAM_DATA')
 return raw,t.encode(),{'destinations':8,'existing_heal_ids':7,'new_save_fields':0,'new_flags':0,'new_EWRAM_globals':0,'newbark_landing':{'x':11,'y':10,'raw':hex(tile)},'icon_scope':'Johto8 separate from old44; fixed arrays preserved','native_status':'PENDING'}
def apply(root,mutate):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 before,after,stats=build(root);print(json.dumps({'apply':mutate,'before':sha(before),'after':sha(after),'validation':stats},indent=2))
 if not mutate or before==after:return
 path=root/'src/region_map.c';assert path.read_bytes()==before,'concurrent region map edit'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=root/'outputs/johto-fly-destinations-v1'/stamp;dest.mkdir(parents=True,exist_ok=False)
 (dest/'region_map.c.before').write_bytes(before);(dest/'manifest.json').write_text(json.dumps(stats,indent=2)+'\n')
 tmp=path.with_name(path.name+'.johto-fly.tmp');assert not tmp.exists();tmp.write_bytes(after);tmp.replace(path)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
