from pathlib import Path
import subprocess,sys,json,os,hashlib,datetime
root=Path('/workspaces/pokefirered');os.chdir(root)
out=root/'reference/audio/pikachu-gF1FJRM8Wck';out.mkdir(parents=True,exist_ok=True)
log=root/'work/public-pikachu-audio-extract.log'
report={'source_url':'https://www.youtube.com/watch?v=gF1FJRM8Wck','source_video_id':'gF1FJRM8Wck','synthesized':False,'download_complete':False,'decode_verified':False,'title_integrated':False}
report_path=root/'work/public-pikachu-audio-extract-result.json'
def write():report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
write()
try:
 target=root/'work/public-audio-tools'
 with log.open('w') as f:
  install=subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--target',str(target),'yt-dlp'],stdout=f,stderr=subprocess.STDOUT,timeout=120)
  report['package_install_exit']=install.returncode;write()
  if install.returncode:raise RuntimeError('Audio tool installation failed; see log')
  env=os.environ.copy();env['PYTHONPATH']=str(target)
  cmd=[sys.executable,'-m','yt_dlp','--ignore-config','--no-playlist','--no-overwrites','--socket-timeout','20','--retries','1','--fragment-retries','1','--write-info-json','--keep-video','-f','bestaudio','-x','--audio-format','mp3','--audio-quality','0','-o',str(out/'pikachu-original.%(ext)s'),report['source_url']]
  r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
  report['extract_exit']=r.returncode;write()
  if r.returncode:raise RuntimeError('Public source audio extraction failed; see log')
 mp3=out/'pikachu-original.mp3';assert mp3.is_file() and mp3.stat().st_size>0
 info=json.loads((out/'pikachu-original.info.json').read_text())
 assert info['id']=='gF1FJRM8Wck';assert 0<float(info['duration'])<=15
 probe=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp3)],capture_output=True,text=True,check=True)
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(mp3),'-f','null','-'],capture_output=True,text=True)
 assert decode.returncode==0,decode.stderr
 report.update(download_complete=True,decode_verified=True,title=info.get('title'),uploader=info.get('uploader'),source_duration_seconds=info['duration'],mp3_probe=json.loads(probe.stdout),files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and not p.name.endswith('.part')])
 (out/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
except Exception as e:report['error']=str(e)
report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write()
