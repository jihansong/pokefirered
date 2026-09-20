#!/usr/bin/env python3
"""Append pokeemerald's wild encounter tables (Hoenn maps) to pokefirered's gWildMonHeaders."""
import json
EM = '/root/src/pokeemerald'; FR = '/workspaces/pokefirered'
RENAME_ID = {'MAP_VICTORY_ROAD_1F': 'MAP_HOENN_VICTORY_ROAD_1F', 'MAP_SAFARI_ZONE_NORTH': 'MAP_HOENN_SAFARI_ZONE_NORTH'}
em = json.load(open(EM + '/src/data/wild_encounters.json'))
fr = json.load(open(FR + '/src/data/wild_encounters.json'))
emg = next(g for g in em['wild_encounter_groups'] if g['label'] == 'gWildMonHeaders')
frg = next(g for g in fr['wild_encounter_groups'] if g['label'] == 'gWildMonHeaders')
frg['encounters'] = [e for e in frg['encounters'] if not e['base_label'].startswith('sHoenn')]
n = 0
for e in emg['encounters']:
    e = dict(e)
    e['map'] = RENAME_ID.get(e['map'], e['map'])
    e['base_label'] = 'sHoenn' + e['base_label'][1:]
    frg['encounters'].append(e); n += 1
open(FR + '/src/data/wild_encounters.json', 'w').write(json.dumps(fr, indent=2, ensure_ascii=False) + '\n')
print(n, 'Hoenn encounter tables')
