#!/usr/bin/env python3
"""Produce an immutable Linux ROM-build evidence bundle from a sparse source tree.

Run only in a fresh isolated Linux checkout. This program never starts a game,
creates a save, runs mGBA, performs Git writes, deletes inputs or calls make clean.
Importing this file does not execute build commands.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback

from space_source_checks import check_source
from verify_space_candidate import AGBCC, CONTAINER, REQUIRED_UNITS


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path,root):
    path=Path(path)
    return dict(path=path.relative_to(root).as_posix(),bytes=path.stat().st_size,sha256=sha(path))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--reference-manifest',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--jobs',type=int,default=max(1,min(4,os.cpu_count() or 1)))
    a=ap.parse_args(); source=a.source.resolve(); out=a.out.resolve(); refpath=a.reference_manifest.resolve()
    assert sys.platform.startswith('linux'),'Linux-only producer; no Windows fallback'
    assert not out.exists() and not out.is_relative_to(source) and 1<=a.jobs<=16
    assert not (source/'build').exists(),'Fresh isolated source checkout required; no prebuilt object reuse'
    assert os.environ.get('AGBCC_REV')==AGBCC,'Explicit external agbcc revision pin required'
    devkit=Path(os.environ['DEVKITARM']).resolve()
    ld=devkit/'bin/arm-none-eabi-ld'; gcc=devkit/'bin/arm-none-eabi-gcc'
    assert ld.is_file() and gcc.is_file(),'Use DEVKITARM absolute tools; do not infer outer shell PATH'
    for tool in ('agbcc','agbcc_arm','old_agbcc'):
        path=source/'tools/agbcc/bin'/tool
        assert path.is_file() and path.read_bytes()[:4]==b'\x7fELF',('Pinned native Linux compiler missing',tool)
    reference=json.loads(refpath.read_text('utf8'))
    check_source(source,reference,with_poses=False)
    before={n:sha(source/n) for n in reference['files']}
    assert before=={n:v['sha256'] for n,v in reference['files'].items()}
    git=['git','-c','safe.directory='+str(source)]
    commit=subprocess.check_output(git+['rev-parse','HEAD'],cwd=source,text=True).strip()
    assert re.fullmatch('[0-9a-f]{40}',commit)
    out.mkdir(parents=True); (out/'logs').mkdir(); steps=[]; diagnostic_steps=[]
    env=dict(os.environ); env['PATH']=str(devkit/'bin')+os.pathsep+env.get('PATH','')
    for key in ('MAKEFLAGS','MFLAGS','MAKELEVEL'): env.pop(key,None)
    # Touch only validated raw payload timestamps in this disposable checkout.
    # Their bytes are checked before and after; source media is never rewritten.
    touched=[]
    for rel in reference['files']:
        if rel.endswith(('.1bpp','.4bpp','.8bpp','.gbapal','.lz','.rl','.pcm','.fwjpnfont','.hwjpnfont','.fwlatfont','.hwlatfont')):
            (source/rel).touch(); touched.append(rel)

    def run(name,command,diagnostic=False,allow_known_rwx=False):
        log=out/'logs'/(name+'.log')
        with log.open('wb') as stream:
            stream.write(('COMMAND '+json.dumps(command)+'\n').encode()); stream.flush()
            result=subprocess.run(command,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        row=dict(name=name,command=command,returncode=result.returncode,log=pin(log,out))
        (diagnostic_steps if diagnostic else steps).append(row)
        assert result.returncode==0,('Build command failed',name,result.returncode)
        text=log.read_text('utf8',errors='replace')
        warnings=[line for line in text.splitlines() if re.search(r'\bwarning\s*:',line,re.I)]
        if allow_known_rwx:
            assert len(warnings)==1 and re.search(r'warning:\s+.*pokemonthyl\.elf has a LOAD segment with RWX permissions\s*$',warnings[0]),warnings
        else: assert not warnings,('Unexpected build warning',name,warnings)
        return len(steps)-1

    def capture(folder):
        rows={}; destination=out/folder; destination.mkdir(parents=True,exist_ok=True)
        for ext,key in (('gba','rom'),('elf','elf'),('map','map'),('sym','sym')):
            p=source/('pokemonthyl.'+ext); q=destination/p.name; shutil.copyfile(p,q); rows[key]=pin(q,out)
        return rows

    def bytes_equal(left,right):
        assert {k:(v['bytes'],v['sha256']) for k,v in left.items()}=={k:(v['bytes'],v['sha256']) for k,v in right.items()}

    def relink_touch():
        obj=source/'build/leafgreen/src/tilesets.o'; expected=sha(obj)
        # Earlier snapshots have already taken time after the completed link.
        # Use real clock time so make never receives a future-dated input.
        if time.time_ns()<= (source/'pokemonthyl.elf').stat().st_mtime_ns: time.sleep(0.02)
        obj.touch(); assert sha(obj)==expected

    try:
        run('tools-serial',['make','tools','-j1'])
        run('generated',['make','generated','GAME_VERSION=LEAFGREEN','COMPARE=0','SETUP_PREREQS=0','NODEP=1'])
        normal_ld='LD='+str(ld)+' --no-warn-rwx-segments'
        common=['COMPARE=0','SETUP_PREREQS=0','KEEP_TEMPS=1']
        compile_index=run('leafgreen',['make','--trace','leafgreen','-j'+str(a.jobs),*common,normal_ld])
        run('symbols',['make','GAME_VERSION=LEAFGREEN',*common,'syms'])
        generated_drift=[]
        for rel,row in reference['required_generated_sources'].items():
            actual=source/rel
            if actual.stat().st_size!=row['bytes'] or sha(actual)!=row['sha256']:
                dest=out/'generated'/rel; dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(actual,dest)
                generated_drift.append(dict(source=rel,expected=row,actual=pin(dest,out)))
        # A built candidate may be recorded for inspection while the independent
        # linked verifier still rejects any unqualified generated-source drift.
        # This does not turn that strict final verification into a PASS.
        baseline=capture('diagnostics/baseline-no-warning')
        object_hashes={unit:sha(source/'build/leafgreen'/unit) for unit in REQUIRED_UNITS}
        relink_touch()
        run('known-rwx-positive-control',['make','leafgreen','-j1',*common,'LD='+str(ld)+' --warn-rwx-segments'],diagnostic=True,allow_known_rwx=True)
        run('known-rwx-symbols',['make','GAME_VERSION=LEAFGREEN',*common,'syms'],diagnostic=True)
        control=capture('diagnostics/warning-control'); bytes_equal(baseline,control)
        relink_touch()
        run('final-no-warning-link',['make','leafgreen','-j1',*common,normal_ld])
        run('final-symbols',['make','GAME_VERSION=LEAFGREEN',*common,'syms'])
        final=capture('.'); bytes_equal(baseline,final)
        assert object_hashes=={unit:sha(source/'build/leafgreen'/unit) for unit in REQUIRED_UNITS}
        run('target-ABI-probe',[str(gcc),'-std=gnu11','-mthumb','-mcpu=arm7tdmi','-mabi=apcs-gnu','-iquote','include',
                                '-DLEAFGREEN','-DENGLISH','-DREVISION=0','-DMODERN=0','-c','tools/qa/space_abi_probe.c','-o',str(out/'space-abi-probe.o')])
        objects=[]
        for unit in REQUIRED_UNITS:
            obj=source/'build/leafgreen'/unit; dest=out/'build/leafgreen'/unit; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(obj,dest)
            rel=unit[:-2]+('.c' if unit.startswith('src/') else '.s')
            if unit.startswith('sound/'): rel=unit[:-2]+'.s'
            expected=reference['files'].get(rel) or reference['required_generated_sources'].get(rel)
            assert expected,('Unbound compile source',unit,rel)
            if sha(source/rel)!=expected['sha256']:
                assert rel in reference['required_generated_sources'],('Non-generated compile source drift',unit,rel)
            objects.append(dict(unit=unit,source=rel,source_sha256=sha(source/rel),compile_log=compile_index,**pin(dest,out)))
            for suffix in ('.i','.s','.d'):
                temporary=obj.with_suffix(suffix)
                if temporary.exists(): shutil.copyfile(temporary,dest.with_suffix(suffix))
        final['abi_probe']=pin(out/'space-abi-probe.o',out)
        after={n:sha(source/n) for n in reference['files']}
        changed_inputs=[n for n in before if after[n]!=before[n]]
        assert set(changed_inputs)<=set(reference['required_generated_sources']),'Non-generated source/media input bytes changed'
        receipt=dict(schema='TY_SPACE_LINUX_BUILD_V1',platform='linux',source_commit=commit,
                     reference_manifest_sha256=sha(refpath),source_tree_verified_before_build=True,source_file_hashes=before,
                     source_file_hashes_after=after,generated_source_drift=generated_drift,inspection_only_generated_drift=bool(generated_drift or changed_inputs),toolchain=dict(agbcc_commit=AGBCC,container_digest=env.get('SPACE_CONTAINER_DIGEST',CONTAINER),
                       tool_hashes={str(p.relative_to(source)) if p.is_relative_to(source) else p.name:sha(p) for p in [ld,gcc,*(source/'tools/agbcc/bin'/n for n in ('agbcc','agbcc_arm','old_agbcc'))]},
                       container_identity_scope='Declared pinned workflow image; exact executable hashes recorded separately'),
                     steps=steps,artifacts=final,objects=objects,abi_probe_source_sha256=reference['files']['tools/qa/space_abi_probe.c']['sha256'],
                     raw_timestamp_only_inputs=touched,warning_control=dict(steps=diagnostic_steps,baseline_artifacts=baseline,
                       warning_artifacts=control,final_artifacts={k:v for k,v in final.items() if k!='abi_probe'},
                       exactly_one_known_warning=True,all_four_outputs_byte_exact=True,object_bytes_unchanged=True),
                     boundary='Only declared sparse source inputs. No claim about unrelated Git files/history.',
                     operations=dict(game_runs=0,mGBA_runs=0,save_inputs=0,source_byte_edits=0,Git_writes=0,make_clean=0))
        (out/'provenance.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
        print(json.dumps(dict(status='BUILD_BUNDLE_READY_INDEPENDENT_LINK_AND_GAMEPLAY_PENDING',provenance_sha256=sha(out/'provenance.json'))))
    except Exception as error:
        (out/'build-error.json').write_text(json.dumps(dict(status='BUILD_STOP_NO_PASS',error=repr(error),traceback=traceback.format_exc(),steps=steps,diagnostics=diagnostic_steps),indent=2)+'\n',encoding='utf8')
        raise


if __name__=='__main__': main()
