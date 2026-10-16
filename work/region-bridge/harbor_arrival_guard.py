from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
EXPECTED={'tools/hoenn_import/patches/SlateportCity_Harbor.scripts.inc':'3325a971516543ceb8c37e7455299e1a1cb1795b4c8ba1f84987e6309528a9d4','data/maps/SlateportCity_Harbor/scripts.inc':'96777927b96b09c23ab24f235c9066d54c128b5abb1246f966eb48271e3ea9ab'}
P='SlateportCity_Harbor_EventScript_';RESUME,DONE=P+'ResumeArrival',P+'ArrivalDone'
def sha(b):return hashlib.sha256(b).hexdigest()
def one(pattern,text):
 hits=list(re.finditer(pattern,text,re.M))
 if len(hits)!=1:raise ValueError('Expected one exact arrival anchor: '+pattern)
 return hits[0]
def add(text):
 if RESUME in text or DONE in text:raise ValueError('Partial or unknown prior patch')
 start=one(r'^'+P+r'ArrivalScene::(?P<n>\r?\n)(?P<i>[ \t]+)lockall[ \t]*(?P=n)',text)
 tail=one(r'^(?P<f>[ \t]+setflag FLAG_HOENN_MET_STERN[ \t]*\r?\n)(?P<h>[ \t]+setvar VAR_HOENN_SCENE_HARBOR,[ \t]*1[ \t]*\r?\n)(?P<s>(?P<i>[ \t]+)setvar VAR_HOENN_STAGE1_PROGRESS,[ \t]*1[ \t]*\r?\n)(?P<e>[ \t]+releaseall[ \t]*\r?\n[ \t]+end[ \t]*\r?\n)',text)
 if tail.start()<=start.end():raise ValueError('Unexpected arrival control flow')
 middle=text[start.end():tail.start()]
 if re.search(r'^[A-Za-z_]\w*::',middle,re.M):raise ValueError('Tail belongs to another event')
 n,i=start['n'],start['i']
 tail_new=tail['f']+RESUME+'::'+n+tail['h']+tail['i']+'goto_if_ge VAR_HOENN_STAGE1_PROGRESS, 1, '+DONE+n+tail['s']+DONE+'::'+n+tail['e']
 return text[:start.end()]+i+'goto_if_set FLAG_HOENN_MET_STERN, '+RESUME+n+middle+tail_new+text[tail.end():]
def remove(text):
 out=text
 for pat in [r'^[ \t]+goto_if_set FLAG_HOENN_MET_STERN, '+RESUME+r'\r?\n',r'^'+RESUME+r'::\r?\n',r'^[ \t]+goto_if_ge VAR_HOENN_STAGE1_PROGRESS, 1, '+DONE+r'\r?\n',r'^'+DONE+r'::\r?\n']:
  m=one(pat,out);out=out[:m.start()]+out[m.end():]
 if add(out)!=text:raise ValueError('Unknown prior content')
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 before={p:Path(p).read_bytes() for p in EXPECTED};after={}
 for p,b in before.items():
  text=b.decode('utf-8')
  if sha(b)==EXPECTED[p]:after[p]=add(text).encode('utf-8')
  else:
   old=remove(text).encode('utf-8')
   if sha(old)!=EXPECTED[p]:raise ValueError('Fresh source hash mismatch: '+p)
   after[p]=b
 changed=[p for p in before if before[p]!=after[p]]
 report={'changed':changed,'before':{p:sha(b) for p,b in before.items()},'after':{p:sha(b) for p,b in after.items()},'applied':False,'save_layout_changed':False,'build_or_emulator_verified':False}
 if args.write and changed:
  backup=Path('work/region-bridge-backup')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');backup.mkdir(parents=True,exist_ok=False)
  for p in changed:
   q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
  (backup/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
  if any(Path(p).read_bytes()!=b for p,b in before.items()):raise ValueError('Source changed during backup')
  for p in changed:Path(p).write_bytes(after[p])
  if any(Path(p).read_bytes()!=b for p,b in after.items()):raise ValueError('Write verification failed')
  report.update(applied=True,backup=str(backup))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
