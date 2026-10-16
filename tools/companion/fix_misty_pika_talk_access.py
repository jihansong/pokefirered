#!/usr/bin/env python3
"""Dry by default. Preserve original PIKACHU emotion and add explicit Misty dialogue access."""
import argparse,base64,datetime,hashlib,json
from pathlib import Path
CFG=json.loads(base64.b64decode('eyJwcmVpbWFnZXMiOnsiZGF0YS9zY3JpcHRzL2ZvbGxvd2VyX3Bpa2FjaHUuaW5jIjoiODllNmU1YWIyZDZhZWUxYWEzODNhNjdiNjkwZTJhZWMzNWI4NWQwZjFkZDZiNTZkNTg1OGI0NzEzNzY5ZGMyOCIsInNyYy9jb21wYW5pb25fbWlzdHkuYyI6ImRmYWEwZmEzMmQxZGQwMTI4MTMyZTZkNGQ3YWM5ODZjODc0YTAyZmRlZDJjMDZiOWQ2YTFhM2YyMjZmOWI0MDIiLCJpbmNsdWRlL2NvbXBhbmlvbl9taXN0eS5oIjoiNzllNzk5NWU2ZmQ5OTc2MzY5MmNjYzIzMzVhN2I5NTNjZDI0NzRiMDBlYTA3NDhiODZkMjcwMDAzZmY5MDMyNyIsImRhdGEvc3BlY2lhbHMuaW5jIjoiMWMwMzNmMzhiMThlOGNlY2E1ZDE2OTcxNjg1YzI5MTllYTAxMDcyNzE2MGM5Njc0Yjg0NWMyMzFkNzI4M2ZjZSIsInRvb2xzL2NvbXBhbmlvbi9taXN0eV9zb3VyY2VfcGF5bG9hZC5qc29uIjoiOGYwNGU2OGIxOGFmZTI5MzBlMDNkOGMzMDQ2MTZkMDkwZTczYmQ0ZTk0YzhkYTc4YjE0NGU4OGFlM2ZkYzhjNiIsIm91dHB1dHMvbWlzdHktY29tcGFuaW9uLXYxL2FwcGxpZWQtc3RhdGUuanNvbiI6IjAyYjIxOGQxMDA2MTEwMmU5ZmYwODE5NWYxM2YyM2FkY2M4OTFkMjA2ZmNkZDg4ZmU5Mzc1NWRlOTkzNTY1MGQifSwiY2FkZCI6IlxuLy8gS2VlcCBQSUtBQ0hVJ3Mgb3JpZ2luYWwgcmVhY3Rpb24sIHRoZW4gb2ZmZXIgYSB2aXNpYmxlIG5lYXJieSBjb21wYW5pb24ncyBkaWFsb2d1ZS5cbnUxNiBDYW5UYWxrVG9NaXN0eUZyb21QaWthY2h1KHZvaWQpXG57XG4gICAgc3RydWN0IE9iamVjdEV2ZW50ICptaXN0eSA9IEdldE1pc3R5Q29tcGFuaW9uT2JqZWN0KCk7XG4gICAgc3RydWN0IE9iamVjdEV2ZW50ICpwbGF5ZXIgPSAmZ09iamVjdEV2ZW50c1tnUGxheWVyQXZhdGFyLm9iamVjdEV2ZW50SWRdO1xuICAgIHMxNiBkeCwgZHk7XG4gICAgaWYgKG1pc3R5ID09IE5VTEwgfHwgc01pc3R5SGlkZGVuQnlTY3JpcHQgfHwgIVNob3VsZE1pc3R5RXhpc3QoKVxuICAgICAgICB8fCBtaXN0eS0+aW52aXNpYmxlIHx8IG1pc3R5LT5vZmZTY3JlZW4gfHwgbWlzdHktPnNwcml0ZUlkID49IE1BWF9TUFJJVEVTXG4gICAgICAgIHx8IGdTcHJpdGVzW21pc3R5LT5zcHJpdGVJZF0uaW52aXNpYmxlKVxuICAgICAgICByZXR1cm4gRkFMU0U7XG4gICAgaWYgKGdTZWxlY3RlZE9iamVjdEV2ZW50ID49IE9CSkVDVF9FVkVOVFNfQ09VTlRcbiAgICAgICAgfHwgIUlzRm9sbG93ZXJQaWthY2h1T2JqZWN0KCZnT2JqZWN0RXZlbnRzW2dTZWxlY3RlZE9iamVjdEV2ZW50XSkpXG4gICAgICAgIHJldHVybiBGQUxTRTtcbiAgICBkeCA9IG1pc3R5LT5jdXJyZW50Q29vcmRzLnggLSBwbGF5ZXItPmN1cnJlbnRDb29yZHMueDtcbiAgICBkeSA9IG1pc3R5LT5jdXJyZW50Q29vcmRzLnkgLSBwbGF5ZXItPmN1cnJlbnRDb29yZHMueTtcbiAgICBpZiAoZHggPCAwKSBkeCA9IC1keDtcbiAgICBpZiAoZHkgPCAwKSBkeSA9IC1keTtcbiAgICByZXR1cm4gZHggKyBkeSA+IDAgJiYgZHggKyBkeSA8PSAzO1xufVxuXG51MTYgU2VsZWN0TWlzdHlDb21wYW5pb25Gb3JUYWxrKHZvaWQpXG57XG4gICAgc3RydWN0IE9iamVjdEV2ZW50ICptaXN0eTtcbiAgICBpZiAoIUNhblRhbGtUb01pc3R5RnJvbVBpa2FjaHUoKSkgcmV0dXJuIEZBTFNFO1xuICAgIG1pc3R5ID0gR2V0TWlzdHlDb21wYW5pb25PYmplY3QoKTtcbiAgICBnU2VsZWN0ZWRPYmplY3RFdmVudCA9IG1pc3R5IC0gZ09iamVjdEV2ZW50cztcbiAgICBnU3BlY2lhbFZhcl9MYXN0VGFsa2VkID0gTE9DQUxJRF9NSVNUWV9DT01QQU5JT047XG4gICAgZ1NwZWNpYWxWYXJfRmFjaW5nID0gR2V0UGxheWVyRmFjaW5nRGlyZWN0aW9uKCk7XG4gICAgcmV0dXJuIFRSVUU7XG59XG4iLCJwaWthX29sZCI6IkV2ZW50U2NyaXB0X1RhbGtUb0ZvbGxvd2VyUGlrYWNodTo6XG5cdGxvY2tcblx0ZmFjZXBsYXllclxuXHRzcGVjaWFsIERvU3RhcnRlclBpa2FjaHVFbW90aW9uXG5cdHdhaXRzdGF0ZVxuXHRyZWxlYXNlXG5cdGVuZFxuIiwicGlrYV9uZXciOiJFdmVudFNjcmlwdF9UYWxrVG9Gb2xsb3dlclBpa2FjaHU6OlxuXHRsb2NrXG5cdGZhY2VwbGF5ZXJcblx0c3BlY2lhbCBEb1N0YXJ0ZXJQaWthY2h1RW1vdGlvblxuXHR3YWl0c3RhdGVcblx0c3BlY2lhbHZhciBWQVJfUkVTVUxULCBDYW5UYWxrVG9NaXN0eUZyb21QaWthY2h1XG5cdGdvdG9faWZfZXEgVkFSX1JFU1VMVCwgRkFMU0UsIEZvbGxvd2VyUGlrYWNodV9FdmVudFNjcmlwdF9GaW5pc2hUYWxrXG5cdG1zZ2JveCBGb2xsb3dlclBpa2FjaHVfVGV4dF9UYWxrVG9NaXN0eSwgTVNHQk9YX1lFU05PXG5cdGdvdG9faWZfZXEgVkFSX1JFU1VMVCwgTk8sIEZvbGxvd2VyUGlrYWNodV9FdmVudFNjcmlwdF9GaW5pc2hUYWxrXG5cdHNwZWNpYWx2YXIgVkFSX1JFU1VMVCwgU2VsZWN0TWlzdHlDb21wYW5pb25Gb3JUYWxrXG5cdGdvdG9faWZfZXEgVkFSX1JFU1VMVCwgRkFMU0UsIEZvbGxvd2VyUGlrYWNodV9FdmVudFNjcmlwdF9GaW5pc2hUYWxrXG5cdGdvdG8gRXZlbnRTY3JpcHRfVGFsa1RvTWlzdHlDb21wYW5pb25cblxuRm9sbG93ZXJQaWthY2h1X0V2ZW50U2NyaXB0X0ZpbmlzaFRhbGs6OlxuXHRyZWxlYXNlXG5cdGVuZFxuXG5Gb2xsb3dlclBpa2FjaHVfVGV4dF9UYWxrVG9NaXN0eTo6XG5cdC5zdHJpbmcgXCJUYWxrIHRvIE1JU1RZLCB0b28/JFwiXG4iLCJoZWFkZXJfYW5jaG9yIjoidTE2IE1pc3R5R2V0R3Jvd3RoU3RhZ2Uodm9pZCk7XG4iLCJoZWFkZXJfbmV3X2RlY2wiOiJ1MTYgTWlzdHlHZXRHcm93dGhTdGFnZSh2b2lkKTtcbnUxNiBDYW5UYWxrVG9NaXN0eUZyb21QaWthY2h1KHZvaWQpO1xudTE2IFNlbGVjdE1pc3R5Q29tcGFuaW9uRm9yVGFsayh2b2lkKTtcbiIsInNwZWNpYWxzX2FkZCI6Ilx0ZGVmX3NwZWNpYWwgQ2FuVGFsa1RvTWlzdHlGcm9tUGlrYWNodVxuXHRkZWZfc3BlY2lhbCBTZWxlY3RNaXN0eUNvbXBhbmlvbkZvclRhbGtcbiIsInBheWxvYWRfYWZ0ZXJfc2hhMjU2IjoiMWJjZGYxNTk2NWUyMDQ1MDRlMDkzNTZhYjUzYTlmMzU0YzZmYTYwMjEyYzUwZjFhOTU0MjVhZTVjZjI0ZmM3YiIsInNvdXJjZV9hZnRlcl9zaGEyNTYiOiIxYWI4MzE5Mjk1MDNkYzc4Yzg4OTcxMDYzYjg4ZjIyMWM2OWMxMWE2ODk4ZTRhMzQ5ZjI3ZDYyMDVmZTM4NTZmIiwiaGVhZGVyX2FmdGVyX3NoYTI1NiI6IjE0ODQzMzM4NzM2YjgzMGI1Njk5ZGQwMjIxODk0NmMxYjBiOTMyNjllN2JhZTU5ZDIzNmM2NmJmMmJhNTYyMWYiLCJwaWthX2FmdGVyX3NoYTI1NiI6ImUyZTdkYTE3MGMzZTMxZjNhY2M1OTBhYjExMGI3MDUyNWViMzdlODM0ZDE5MWIzODA2M2MwODI4MjIxZTUwYjQifQ=='))
p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
root=Path('/workspaces/pokefirered').resolve();H=lambda b:hashlib.sha256(b).hexdigest()
paths=['src/companion_misty.c','include/companion_misty.h','data/scripts/follower_pikachu.inc','data/specials.inc','tools/companion/misty_source_payload.json','outputs/misty-companion-v1/applied-state.json']
def target(path):
 q=(root/path).resolve();assert q.is_relative_to(root) and q.is_file();return q
before={s:target(s).read_bytes() for s in paths};state=json.loads(before[paths[5]])
post={paths[0]:CFG['source_after_sha256'],paths[1]:CFG['header_after_sha256'],paths[2]:CFG['pika_after_sha256'],paths[4]:CFG['payload_after_sha256']}
if all(H(before[s])==h for s,h in post.items()):
 assert before[paths[3]].decode().count(CFG['specials_add'])==1
 assert all(state['hashes'][s]==H(before[s]) for s in paths[:4])
 print(json.dumps(dict(already_applied=True,changed=[],save_fields_added=0,new_static_ram_bytes=0)));raise SystemExit(0)
for s in paths:assert H(before[s])==CFG['preimages'][s],('preimage changed',s,H(before[s]))
cp=before[paths[0]].decode();header=before[paths[1]].decode();pika=before[paths[2]].decode();specials=before[paths[3]].decode();payload=json.loads(before[paths[4]])
assert payload['files'][paths[0]]==cp and payload['files'][paths[1]]==header
assert pika==CFG['pika_old'] and header.count(CFG['header_anchor'])==1
assert cp.count('EWRAM_DATA')==1 and 'CanTalkToMistyFromPikachu' not in cp and 'gPlayerParty[' not in cp
assert specials.count('gSpecialsEnd::\n')==1 and 'def_special CanTalkToMistyFromPikachu' not in specials
wanted={paths[0]:(cp+CFG['cadd']).encode(),paths[1]:header.replace(CFG['header_anchor'],CFG['header_new_decl']).encode(),paths[2]:CFG['pika_new'].encode(),paths[3]:specials.replace('gSpecialsEnd::\n',CFG['specials_add']+'gSpecialsEnd::\n').encode()}
payload['files'][paths[0]]=wanted[paths[0]].decode();payload['files'][paths[1]]=wanted[paths[1]].decode()
rows=[r for r in payload['recipes'] if r['path']==paths[3]];assert len(rows)==1 and rows[0]['new'].count('gSpecialsEnd::')==1
rows[0]['new']=rows[0]['new'].replace('gSpecialsEnd::',CFG['specials_add']+'gSpecialsEnd::')
assert not any(r['path']==paths[2] for r in payload['recipes'])
payload['recipes'].append(dict(path=paths[2],old=CFG['pika_old'],new=CFG['pika_new']));payload['preimages'][paths[2]]=CFG['preimages'][paths[2]]
wanted[paths[4]]=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()
for s,h in post.items():assert H(wanted[s])==h,('postimage mismatch',s)
for s in paths[:4]:state['hashes'][s]=H(wanted[s])
state['files']=len(state['hashes']);state['ordinary_pika_misty_dialogue_access']=True
if paths[2] not in state['changed']:state['changed'].append(paths[2])
wanted[paths[5]]=(json.dumps(state,indent=2)+'\n').encode()
assert wanted[paths[0]].decode().count('EWRAM_DATA')==1 and 'CreateTask(' not in wanted[paths[0]].decode()
assert wanted[paths[2]].decode().startswith(CFG['pika_old'].split('\trelease\n')[0]),'original PIKA emotion prefix changed'
assert wanted[paths[2]].decode().count('special DoStarterPikachuEmotion')==1
report=dict(dry_pass=True,applied=False,changed=list(wanted),original_pika_emotion_preserved=True,conditional_explicit_yesno=True,new_static_ram_bytes=0,save_fields_added=0,actual_native_verified=False,shared_preimages_rebased=False,files={s:dict(before_sha256=H(before[s]),after_sha256=H(b)) for s,b in wanted.items()})
if a.apply:
 for s,b in before.items():assert target(s).read_bytes()==b,('concurrent edit',s)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');backup=root/'outputs/misty-companion-v1/pika-talk-backups'/stamp
 for s,b in before.items():q=backup/s;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 for s,b in wanted.items():target(s).write_bytes(b)
 report.update(applied=True,backup=str(backup))
print(json.dumps(report,indent=2))
