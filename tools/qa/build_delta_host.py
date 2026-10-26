#!/usr/bin/env python3
"""Clean-build the pinned official Delta GBA core on Linux; never run a game."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile

CORE_COMMIT = '453fa0decf179360926fb417725a794aa496d6e3'
GBA_UNITS = ['agbprint','bios','Cheats','CheatSearch','EEprom','ereader','Flash',
             'GBA','GBAGfx','GBALink','GBA-thumb','GBA-arm','gbafilter','Globals',
             'Mode0','Mode1','Mode2','Mode3','Mode4','Mode5','RTC','Sound','Sram']
APU_UNITS = ['Blip_Buffer','Effects_Buffer','Gb_Apu','Gb_Apu_State','Gb_Oscs','Multi_Buffer']
CORE_UNITS = ['src/gba/'+name+'.cpp' for name in GBA_UNITS]
CORE_UNITS += ['src/apu/'+name+'.cpp' for name in APU_UNITS]
CORE_UNITS += ['src/gba/BreakpointStructures.cpp']
DEFINES = ['NO_LINK','NO_DEBUGGER','NO_PNG','C_CORE','FINAL_VERSION','BKPT_SUPPORT','__AMD64__']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_directory(path):
    if '..' in path.parts:
        raise ValueError('Parent path components are forbidden')
    absolute=path.absolute()
    for p in [absolute,*absolute.parents]:
        if p.is_symlink():raise ValueError('Symlink directories are forbidden')
    if not absolute.is_dir():raise ValueError('Artifact directory must already exist')
    mode=absolute.stat()
    if mode.st_uid!=os.geteuid() or mode.st_mode&0o077:
        raise ValueError('Artifact directory must be caller-owned mode 0700')
    return absolute


def output_path(root,name):
    if not name or name in ('.','..') or Path(name).name!=name or '/' in name or '\\' in name:
        raise ValueError('Output must be a new basename')
    path=root/name
    if path.exists() or path.is_symlink():raise FileExistsError('Output already exists')
    return path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True,help='Clean official VBA-M Git checkout')
    parser.add_argument('--artifact-dir',type=Path,required=True)
    parser.add_argument('--output',required=True,help='New Linux executable basename')
    parser.add_argument('--cxx',default='g++')
    parser.add_argument('--jobs',type=int,default=4)
    args=parser.parse_args()
    if platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64'):
        raise SystemExit('This builder permits Linux x86_64 only; no Windows build or execution')
    source=args.source.resolve(strict=True)
    root=checked_directory(args.artifact_dir)
    output=output_path(root,args.output)
    receipt=output_path(root,args.output+'.build.json')
    actual=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if actual!=CORE_COMMIT:raise ValueError('Core commit does not match the official Delta pin')
    if subprocess.check_output(['git','-C',str(source),'status','--porcelain','--untracked-files=all','--','src'],text=True).strip():
        raise ValueError('Core source must be unchanged and clean')
    target=subprocess.check_output([args.cxx,'-dumpmachine'],text=True).strip()
    if 'linux' not in target:raise ValueError('A native Linux compiler is required')
    host=Path(__file__).with_name('delta_host.cpp').resolve()
    flags=['-std=gnu++11','-O2','-ffunction-sections','-fdata-sections','-fno-strict-aliasing']
    flags+=['-D'+name for name in DEFINES]+['-I'+str(source/'src')]
    work=Path(tempfile.mkdtemp(prefix='delta-host-build-',dir=root))
    assert work.parent==root
    inputs=[source/path for path in CORE_UNITS]+[host]
    assert len(inputs)==31
    def compile_one(pair):
        index,path=pair;obj=work/(str(index).zfill(2)+'.o')
        command=[args.cxx,*flags,'-c',str(path),'-o',str(obj)]
        result=subprocess.run(command,cwd=source,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log=work/(str(index).zfill(2)+'.log');log.write_text(result.stdout,encoding='utf-8')
        if result.returncode:raise RuntimeError('Compilation failed; see '+log.name)
        return {'source':CORE_UNITS[index] if index<len(CORE_UNITS) else 'delta_host.cpp',
                'source_sha256':digest(path),'object':str(obj.relative_to(root)),
                'object_sha256':digest(obj),'log':str(log.relative_to(root))}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.jobs,8))) as pool:
        results=list(pool.map(compile_one,enumerate(inputs)))
    linked=work/'delta-core-host'
    link=[args.cxx,*[str(root/item['object']) for item in results],'-Wl,--gc-sections','-lz','-o',str(linked)]
    result=subprocess.run(link,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (work/'link.log').write_text(result.stdout,encoding='utf-8')
    if result.returncode:raise RuntimeError('Host link failed; see link.log')
    raw=linked.read_bytes()
    if raw[:5]!=b'\x7fELF\x02' or int.from_bytes(raw[18:20],'little')!=62:
        raise ValueError('The linked host is not native Linux x86_64 ELF')
    # Atomic no-replace publication inside the already-validated private directory.
    os.link(linked,output);os.chmod(output,0o700)
    report={'status':'BUILT_HOST_NO_GAME_EXECUTION','core_commit':actual,'translation_units':31,
            'core_translation_units':30,'defines':DEFINES,'compile_flags':flags,
            'compiler_target':target,'compiler':subprocess.check_output([args.cxx,'--version'],text=True).splitlines()[0],
            'sources':results,'executable':output.name,'executable_sha256':digest(output),
            'framebuffer_capacity_bytes':4*241*162,'core_modifications':0,'game_runs':0,
            'scope':'Official pinned CPU/BIOS/DMA/GPU/APU with a Linux protocol/file-I/O host'}
    with receipt.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':report['status'],'output':output.name,'sha256':report['executable_sha256'],'translation_units':31}))


if __name__=='__main__':main()
