"""Explicit player/NPC pose domains and narrowly typed native foot occlusion.

No image, game, executable or file mutation occurs here. Domain construction
reads the selected source only. No reachable head/face occlusion is accepted.
"""
from collections import deque
import json
import re
import struct


_NON_MOVING = {
    'Common_Movement_ExclamationMark': ['emote_exclamation_mark', 'step_end'],
    'Common_Movement_WalkInPlaceFasterUp': ['walk_in_place_faster_up', 'step_end'],
}
_LOUNGE_STAFF = {x:n for x,n in zip(range(6,13), (708,711,692,693,694,710,788))}
_NPC_COUNTERS = {
    ('HoennSpacecraftCabin',3): ((3,2),'OBJ_EVENT_GFX_NURSE',('league',519)),
    ('HoennSpacecraftCabin',8): ((16,2),'OBJ_EVENT_GFX_CLERK',('league',553)),
    ('HoennSpacecraftLounge',1): ((9,3),'OBJ_EVENT_GFX_GENTLEMAN',('game',693)),
}


def _flood(floor, seeds):
    seen = set(seeds) & floor
    queue = deque(sorted(seen))
    while queue:
        x,y = queue.popleft()
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if p in floor and p not in seen:
                seen.add(p); queue.append(p)
    return seen


def domains(source, contract):
    layouts = json.loads((source/'data/layouts/layouts.json').read_bytes())['layouts']
    movement = (source/'data/scripts/movement.inc').read_text('utf8')
    for label, expected in _NON_MOVING.items():
        body = re.search(r'^'+label+r'::\s*\n(.*?\bstep_end\b)', movement, re.M|re.S).group(1)
        actual = [x.strip() for x in body.splitlines() if x.strip() and not x.strip().startswith('@')]
        assert actual == expected, ('Literal movement now changes position',label,actual)
    result = {}
    for room in contract['maps']:
        name=room['map']; definition=json.loads((source/'data/maps'/name/'map.json').read_bytes())
        layout=next(x for x in layouts if x.get('id')==definition['layout'])
        w,h=room['size']; raw=(source/layout['blockdata_filepath']).read_bytes()
        cells=struct.unpack('<%dH'%(w*h),raw)
        floor={(i%w,i//w) for i,v in enumerate(cells) if v&0xc00==0}
        seeds={tuple(room['safe_anchor'])}
        for warp in room['warps']:
            x,y=warp['xy']; dx,dy={'N':(0,1),'S':(0,-1),'W':(1,0),'E':(-1,0)}[warp['outward']]
            seeds.update(((x,y),(x+dx,y+dy)))
        assert seeds <= floor, ('A normal arrival seed is blocked',name,seeds-floor)
        reachable=_flood(floor,seeds)
        assert {tuple(x) for x in room['must_reachable']} <= reachable
        npcs=[]
        for index,obj in enumerate(definition['object_events'],1):
            local=int(obj.get('local_id',index)); origin=(obj['x'],obj['y'])
            assert origin in floor, ('NPC spawn is blocked',name,local,origin)
            kind=obj['movement_type']; rx=obj['movement_range_x']; ry=obj['movement_range_y']
            if kind in ('MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT','MOVEMENT_TYPE_WANDER_RIGHT_AND_LEFT'):
                allowed={(x,origin[1]) for x in range(origin[0]-rx,origin[0]+rx+1)}
            elif kind in ('MOVEMENT_TYPE_WANDER_UP_AND_DOWN','MOVEMENT_TYPE_WANDER_DOWN_AND_UP'):
                allowed={(origin[0],y) for y in range(origin[1]-ry,origin[1]+ry+1)}
            else:
                assert not any(x in kind for x in ('WANDER','WALK')), ('New NPC movement needs an explicit domain',name,local,kind)
                allowed={origin}
            points=_flood(floor&allowed,{origin})
            npcs.append({'local_id':local,'object':obj,'points':points})
        scripts=(source/'data/maps'/name/'scripts.inc').read_text('utf8')
        literals=[]
        for target,label in re.findall(r'\bapplymovement\s+(\w+),\s*(\w+)',scripts):
            assert label in _NON_MOVING, ('Unmodelled script movement',name,target,label)
            assert target.isdigit() and int(target) in {x['local_id'] for x in npcs}
            literals.append({'target':int(target),'label':label,'coordinate_displacement':[0,0]})
        assert not re.search(r'\b(?:setobjectxy|setobjectxyperm|moveobjectoffscreen)\b',scripts), ('New literal position mutation needs a domain',name)
        result[name]={'player':reachable,'seeds':seeds,'floor':floor,'excluded':floor-reachable,
                      'npcs':npcs,'literal_movements':literals}
    return result


def allowed_foot(room, xy, gfx, height, bbox, source_ref, local_id=None):
    """Only named native counters may cover the last four sprite rows."""
    if bbox is None:
        return None
    if bbox[1] < height-4 or bbox[3] > height:
        return None
    if local_id is None:
        if room!='HoennSpacecraftLounge' or xy[1]!=3 or xy[0] not in _LOUNGE_STAFF:
            return None
        expected=('game',_LOUNGE_STAFF[xy[0]])
        label='original_GameCorner_counter_staff_floor'
    else:
        entry=_NPC_COUNTERS.get((room,local_id))
        if entry is None or tuple(xy)!=entry[0] or gfx!=entry[1]:
            return None
        expected=entry[2];label='native_service_counter_hides_feet_only'
    if tuple(source_ref[:2])!=expected:
        return None
    return {'map':room,'xy':list(xy),'gfx':gfx,'local_id':local_id,
            'kind':label,'source_ref':list(source_ref),'maximum_hidden_rows':4,
            'sprite_height':height,'observed_bbox':list(bbox),
            'head_face_hidden':False}
