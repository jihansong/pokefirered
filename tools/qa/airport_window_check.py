#!/usr/bin/env python3
"""Verify airport actor/plane draw ordering in a disposable copy of a save."""
import argparse, hashlib, json, os, struct, subprocess, tempfile
from pathlib import Path
from emu import Emu
import gamedata, savedit

REPO = Path(__file__).resolve().parents[2]
os.chdir(REPO)

def offsets():
    fields = {'object_size':'sizeof(struct ObjectEvent)', 'sprite_size':'sizeof(struct Sprite)',
        'sprite_id':'offsetof(struct ObjectEvent, spriteId)', 'local_id':'offsetof(struct ObjectEvent, localId)',
        'coords':'offsetof(struct ObjectEvent, currentCoords)', 'subpriority':'offsetof(struct Sprite, subpriority)'}
    gcc, nm = gamedata._gcc()
    with tempfile.TemporaryDirectory() as td:
        src = Path(td)/'offsets.c'; obj = Path(td)/'offsets.o'
        src.write_text('#include "global.h"\n#include "sprite.h"\n' + '\n'.join('char qa_'+k+'['+v+'+1];' for k,v in fields.items()))
        subprocess.check_call([gcc,'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t','-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(obj),str(src)])
        result = {}
        for line in subprocess.check_output([nm,'-S',str(obj)],text=True).splitlines():
            p=line.split()
            if len(p)==4 and p[3].startswith('qa_'): result[p[3][3:]]=int(p[1],16)-1
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--save',default='saves/hoenn.sav')
    ap.add_argument('--shots',required=True)
    a=ap.parse_args(); out=Path(a.shots); out.mkdir(parents=True,exist_ok=True)
    original=Path(a.save).read_bytes(); off=offsets(); observations=[]
    with tempfile.TemporaryDirectory() as td:
        sav=str(Path(td)/'airport.sav')
        assert savedit.run([a.save,'-o',sav,'warp','KantoAirport','28','3','flag','FLAG_SAW_AIRPORT_PLANE_TAXI','1','noquestlog'])==0
        with Emu(str(REPO/'pokemonthyl.gba'),sav) as e:
            e.boot_continue(); e.run(60)
            def record(label, indoor):
                rows=[]
                for i in range(16):
                    ob=e.sym('gObjectEvents')+i*off['object_size']
                    if not e.u8(ob)&1: continue
                    sid=e.u8(ob+off['sprite_id']); sp=e.sym('gSprites')+sid*off['sprite_size']
                    xy=struct.unpack('<hh',e.read(ob+off['coords'],4))
                    rows.append({'local_id':e.u8(ob+off['local_id']),'x':xy[0]-7,'y':xy[1]-7,'priority':(e.u16(sp+4)>>10)&3,'subsprite_table':e.u8(sp+off['subpriority']-1)&63})
                player=next(r for r in rows if r['local_id']==255)
                npc=next(r for r in rows if (r['x'],r['y'])==(30,2))
                plane=next(r for r in rows if (r['x'],r['y'])==(27,1))
                assert player['priority']==(1 if indoor else 2),(label,player)
                assert npc['priority']==1,(label,npc)
                assert plane['priority']==2,(label,plane)
                if indoor:
                    assert player['subsprite_table']==2,(label,player)
                    assert npc['subsprite_table']==2,(label,npc)
                follower=next((r for r in rows if r['local_id']==254),None)
                if label=='window_left' and follower is not None:
                    assert (follower['x'],follower['y'])==(28,2),follower
                    assert follower['priority']==1 and follower['subsprite_table']==2,follower
                e.shot(str(out/(label+'.png')),scale=3)
                observations.append({'scene':label,'objects':rows,'follower_present':follower is not None})
                print('PASS',label,'player',player['priority'],'npc',npc['priority'],'plane',plane['priority'],'follower',follower,flush=True)
            e.walk('UP'); e.run(30); record('window_up',True)
            e.walk('LEFT'); e.run(30); record('window_left',True)
            e.walk('DOWN',5); e.run(30); record('away_from_window',False)
    assert Path(a.save).read_bytes()==original, 'Original save was changed'
    result={'save':a.save,'save_sha256':hashlib.sha256(original).hexdigest(),'original_unchanged':True,'observations':observations}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS original save unchanged',flush=True)
if __name__=='__main__': main()
