#!/usr/bin/env python3
"""Only remove pre-static wild-tile walking from the scripted Gyarados QA."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,datetime
p=argparse.ArgumentParser();p.add_argument('--root',default='/workspaces/pokefirered');p.add_argument('--apply',action='store_true');a=p.parse_args()
root=Path(a.root).resolve()
H=lambda b:hashlib.sha256(b).hexdigest()
records=[{"path":"tools/qa/johto_mahogany_native_static.py","old_sha256":"7da8efbc2747d17d17e0cba2c68a75d0c0456c271c202173804b707e6c3ab052","new_sha256":"15a260f9ecf02bef3c933b71f7779bf0a19f15144d4eb90a177262542891f984"},{"path":"tools/qa/johto_mahogany_native_chain.py","old_sha256":"85614b72738f99c4b42b5806b5c568a62ccf20645ee46e668dbd9e0d7e045ddf","new_sha256":"46630cb2cab57945ee4117993ffa598bc0f9b60793ed428b17490c2599f9d794"}]
OLD="v=STATIC[key];native_step(e,'UP');e.press('A',hold=3,after=12)"
NEW="v=STATIC[key]\n if key=='gyarados':\n  native_face(e,'UP');assert e.location()[2:]==v['where'][1:],('scripted Gyarados facing moved onto a wild tile',e.location())\n else:native_step(e,'UP')\n e.press('A',hold=3,after=12)"
writes=[]
for row in records:
 path=root/row['path'];before=path.read_bytes();text=before.decode()
 assert H(before)==row['old_sha256'],(row['path'],'QA source changed')
 assert text.count(OLD)==1 and text.count("where=('LakeOfRage',20,19)")==1
 after=text.replace(OLD,NEW,1).replace("where=('LakeOfRage',20,19)","where=('LakeOfRage',20,18)",1).encode()
 ast.parse(after.decode(),filename=str(path))
 assert H(after)==row['new_sha256']
 writes.append((path,before,after))
if a.apply:
 backup=root/'work'/('mahogany-static-adjacent-backup-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));backup.mkdir()
 for path,before,after in writes:
  assert path.read_bytes()==before,'source changed after validation'
  rel=path.relative_to(root);saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(before)
 for path,before,after in writes:
  assert path.read_bytes()==before
  tmp=path.with_name(path.name+'.adjacent.tmp');tmp.write_bytes(after);tmp.replace(path)
 print(json.dumps({'applied':True,'backup':str(backup),'files':records}))
else:print(json.dumps({'dry_run':True,'files':records,'product_files_changed':0}))
