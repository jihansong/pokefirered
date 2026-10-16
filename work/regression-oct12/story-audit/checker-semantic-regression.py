from pathlib import Path
from types import SimpleNamespace
import ast,sys,tempfile,json,re,hashlib,importlib.util
r=Path('/workspaces/pokefirered');p=Path(sys.argv[1]);out=Path(sys.argv[2]);sys.path.insert(0,str(r/'tools'))
spec=importlib.util.spec_from_file_location('event_wiring_test_target',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
raw=lambda s:'.string "'+s+'"\n'
cases=[('elm_report',raw('ELM received your report.$'),False),('elm_from_player',raw('The elder studies the notes\\nthat ELM received from you.$'),False),('player',raw('{PLAYER} received an ITEM!$'),True),('split_player','.string "{PLAYER}\\n"\n.string "received {ITEM}!$"\n',True),('you',raw('You received an ITEM!$'),True),('buffer1',raw('{BUFFER1} received an ITEM!$'),True),('strvar',raw('{STR_VAR_1} received an ITEM!$'),True),('i',raw('I received your report.$'),False),('someone',raw('Someone received your report.$'),False),('implicit',raw('Received an ITEM!$'),True),('unknown_named',raw('RED received an ITEM!$'),True),('second_promise',raw('ELM received your report. Here you go!$'),True),('joint_subject',raw('You and ELM received the ITEM!$'),True),('invalid_assembly','.string "You received',True)]
promise=[]
for name,s,want in cases:
 got=m.has_reward_promise(s) if hasattr(m,'has_reward_promise') else bool(m.PROMISE.search(s));promise.append({'case':name,'pass':got==want,'actual':got,'expected':want})
with tempfile.TemporaryDirectory() as td:
 f=Path(td)/'scripts.inc';text='Root::\n    call PlainGive\n    goto_if_set FLAG_DONE, AfterReport\n    end\nPlainGive::\n    giveitem ITEM_TM29\n    return\nAfterReport::\n    msgbox TextReport\n    end\nSingleRoot::\n    end\nUnrelated:\n    giveitem ITEM_MEW\n    end\nFallRoot::\n    msgbox TextIntro\nPlainFall::\n    giveitem ITEM_TM40\n    end\nCycleA::\n    call CycleB\n    return\nCycleB::\n    call CycleA\n    return\n';f.write_text(text)
 def rec(label,refs=(),nxt=None):
  line=next(i for i,s in enumerate(text.splitlines(),1) if s in [label+':',label+'::'])
  return dict(file=str(f),line=line,refs=set(refs),next=nxt)
 labs={'Root':rec('Root',['PlainGive','AfterReport']),'PlainGive':rec('PlainGive'),'AfterReport':rec('AfterReport'),'SingleRoot':rec('SingleRoot'),'Unrelated':rec('Unrelated'),'FallRoot':rec('FallRoot',nxt='PlainFall'),'PlainFall':rec('PlainFall'),'CycleA':rec('CycleA',['CycleB']),'CycleB':rec('CycleB',['CycleA'])}
 ix=SimpleNamespace(labels=labs);original=m.C;m.C=SimpleNamespace(rel=lambda x:x,LABEL_RE=original.LABEL_RE)
 b=m.script_body(ix,'Root');c=m.script_body(ix,'CycleA')
 graph={'plain_call':'giveitem ITEM_TM29' in b,'plain_goto':'msgbox TextReport' in b,'single_colon_boundary':'giveitem' not in m.script_body(ix,'SingleRoot'),'fallthrough':'giveitem ITEM_TM40' in m.script_body(ix,'FallRoot'),'cycle_shared_seen':c.count('call CycleB')==1 and c.count('call CycleA')==1,'missing_label':m.script_body(ix,'MISSING')==''}
result={'all_pass':all(z['pass'] for z in promise) and all(graph.values()),'promise_cases':promise,'graph_cases':graph,'checker_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'game_files_changed':False}
out.write_text(json.dumps(result,indent=2));print(json.dumps(result));sys.exit(0 if result['all_pass'] else 1)
