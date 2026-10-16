#!/usr/bin/env python3
"""Guarded cold-PC Union Room name safety repair. Saved structs and valid names stay unchanged."""
from pathlib import Path
import argparse,datetime,hashlib,json
digest=lambda b:hashlib.sha256(b).hexdigest()
DECL='static EWRAM_DATA u8 sUnionRoomPlayerName[12] = {};'
NEWDECL='static EWRAM_DATA u8 sUnionRoomPlayerName[12] = {EOS};'
OLD='''bool16 BufferUnionRoomPlayerName(void)
{
    if (sUnionRoomPlayerName[0] != EOS)
'''
NEW='''bool16 BufferUnionRoomPlayerName(void)
{
    // COLD_PC_UNION_NAME_BOUND_V1: custom centers may never initialize RFU.
    // An uninitialized, unterminated name must not escape its fixed buffer.
    u32 length;
    for (length = 0; length < ARRAY_COUNT(sUnionRoomPlayerName); length++)
    {
        if (sUnionRoomPlayerName[length] == EOS)
            break;
    }
    if (length == ARRAY_COUNT(sUnionRoomPlayerName))
    {
        sUnionRoomPlayerName[0] = EOS;
        return FALSE;
    }
    if (sUnionRoomPlayerName[0] != EOS)
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--expect',required=True)
 p.add_argument('--apply',action='store_true');a=p.parse_args();root=Path(a.root)
 path=root/'src/union_room.c';b=path.read_bytes();assert digest(b)==a.expect,'union source changed'
 t=b.decode();assert t.count(DECL)==t.count(OLD)==1
 new=t.replace(DECL,NEWDECL,1).replace(OLD,NEW,1).encode()
 assert new.count(b'COLD_PC_UNION_NAME_BOUND_V1')==1
 # Both exact replacements preserve all original return branches and RFU update code.
 assert new.replace(NEWDECL.encode(),DECL.encode(),1).replace(NEW.encode(),OLD.encode(),1)==b
 report={'path':'src/union_room.c','before_sha256':digest(b),'after_sha256':digest(new),
  'before_bytes':len(b),'after_bytes':len(new),'apply':a.apply,'storage_and_save_structures_changed':False,
  'array_size_and_link_globals_changed':False,'valid_terminated_name_logic_preserved':True,
  'wireless_service_and_map_hooks_changed':False,'native_validation_pending':True}
 print(json.dumps(report,indent=2))
 if not a.apply:return
 assert path.read_bytes()==b,'concurrent union source edit'
 target=root/'outputs/nurse-union-name-safety-v1'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 target.mkdir(parents=True,exist_ok=False);(target/'union_room-before.c').write_bytes(b)
 (target/'manifest.json').write_text(json.dumps(report,indent=2));path.write_bytes(new)
if __name__=='__main__':main()
