from pathlib import Path
import subprocess,sys,json,hashlib,datetime,os
os.chdir('/workspaces/pokefirered')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=Path('work/title-publisher-native-validation-'+stamp);out.mkdir();Path('work/title-publisher-native-latest.txt').write_text(str(out))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
saves={str(p):sha(p)for p in Path('saves').glob('*.sav')};report={'steps':[],'source_url':'https://www.youtube.com/watch?v=gF1FJRM8Wck','all_pass':False,'delta_device_tested':False,'audio_auditioned':False};rp=out/'result.json'
def save():rp.write_text(json.dumps(report,indent=2))
def step(name,cmd):
 with (out/(name+'.log')).open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 report['steps'].append({'name':name,'exit_code':r.returncode,'log':str(out/(name+'.log'))});save();assert r.returncode==0,name+' failed'
save()
try:
 args=['--repo','.','--source','reference/audio/pikachu-gF1FJRM8Wck/publisher-original/pokemon-video-game-pikachu-voice-sound-effect.wav','--archive','reference/audio/pikachu-gF1FJRM8Wck/publisher-original.zip','--expect-source','10a2a254c12eed24a7e4d7a4db9ffff3f318ae20c17a5b15dbe53bbcf4c50734','--source-url','https://www.youtube.com/watch?v=gF1FJRM8Wck','--expect-title','c2521f842e2f7385f429465330c50c663a88b24da7d419e6dbe77362643f56d5','--expect-table','6cd7d3816144d1a6e5e982549928ce266eb011b0e3e0afaeee78920f4c1aa597']
 step('apply',[sys.executable,'work/apply_title_publisher_voice.py']+args+['--write'])
 step('review-build',['make','GAME_VERSION=LEAFGREEN','BUILD_NAME=titlevoiceqa','-W','src/rocket_trainer_portrait.c','-j2','rom','syms'])
 step('review-runtime',[sys.executable,'tools/qa/title_publisher_voice_check.py','--rom','poketitlevoiceqa.gba','--out',str(out/'review-runtime'),'--expect-source','10a2a254c12eed24a7e4d7a4db9ffff3f318ae20c17a5b15dbe53bbcf4c50734'])
 step('main-build',['make','leafgreen','-W','src/rocket_trainer_portrait.c','-j2'])
 step('main-syms',['make','GAME_VERSION=LEAFGREEN','syms'])
 step('main-runtime',[sys.executable,'tools/qa/title_publisher_voice_check.py','--rom','pokemonthyl.gba','--out',str(out/'main-runtime'),'--expect-source','10a2a254c12eed24a7e4d7a4db9ffff3f318ae20c17a5b15dbe53bbcf4c50734'])
 report.update(all_pass=True,main_rom_sha256=sha('pokemonthyl.gba'),review_rom_sha256=sha('poketitlevoiceqa.gba'))
except Exception as e:report['error']=type(e).__name__+': '+str(e)
report['original_saves_unchanged']=all(Path(p).is_file()and sha(p)==h for p,h in saves.items());report['protected_save_count']=len(saves);report['all_pass']=report['all_pass']and report['original_saves_unchanged'];report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
