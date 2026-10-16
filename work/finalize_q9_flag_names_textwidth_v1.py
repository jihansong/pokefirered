from pathlib import Path
import hashlib,json,datetime,ast
r=Path('/workspaces/pokefirered');out=r/'outputs/regions-q9-review-v1/source-finalize-flags-textwidth';out.mkdir(exist_ok=False)
sha=lambda x:hashlib.sha256(x).hexdigest();changes={}
p=r/'include/constants/flags.h';s=p.read_text();assert sha(s.encode())=='f11e40150aa0f45bd5608e613f972711482860a450f6101c917fad8fe9464773'
t=s
for old,name in [('FLAG_0x223','FLAG_MISTY_COMPANION_JOINED'),('FLAG_0x224','FLAG_HIDE_MISTY_PALLET')]:
 import re
 direct=re.search(r'^#define '+old+r's+(0x[0-9a-fA-F]+)s*$',t,re.M);assert direct
 t=t[:direct.start()]+'#define '+name+' '+direct.group(1)+t[direct.end():]
 alias='#define '+name+' '+old;assert t.count(alias)==1;t=t.replace(alias,'// '+name+' uses its named, allocated flag above.',1)
for root in ['src','data']:
 for x in (r/root).rglob('*'):
  if x.is_file()and x.suffix in ['.c','.h','.inc','.s','.json']:
   v=x.read_text(errors='replace');assert 'FLAG_0x223'not in v and 'FLAG_0x224'not in v,('unexpected old free flag reference',str(x))
changes[str(p.relative_to(r))]=(s,t)
for name,old,new in [('Route110',"BRENDAN: Your title won't decide this.","BRENDAN: A title won't decide this."),('Route119','MAY: You saved the WEATHER INSTITUTE!','MAY: You saved the institute!')]:
 for p in [r/'data/maps'/name/'text.inc',r/'tools/hoenn_import/patches'/(name+'.text.inc')]:
  s=p.read_text();assert s.count(old)==1;changes[str(p.relative_to(r))]=(s,s.replace(old,new,1))
manifest=[]
for name,(s,t)in changes.items():
 p=r/name;assert p.read_text()==s;dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s);p.write_text(t);manifest.append({'path':name,'before':sha(s.encode()),'after':sha(t.encode())})
(out/'manifest.json').write_text(json.dumps({'changes':manifest,'numeric_flags_and_SaveABI_unchanged':True,'only_two_overwidth_lines_reworded':True},indent=2));print('SOURCE_FINALIZE_APPLIED',json.dumps(manifest),flush=True)
