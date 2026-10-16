import pathlib,subprocess,json
base=pathlib.Path('outputs/regional-dex-story-v1/regional_ui_qa.py').read_text().split(' pristine=e.save_state()')[0]
base=base.replace("b=rom.with_suffix('.elf').read_bytes();","b=pathlib.Path(sys.argv[3]).read_bytes();")
tail=r'''
 pristine=e.save_state()
 for f in (0x1208,0x1236,0x1500,0x1501):call('FlagClear',f)
 for n in range(1,387):
  call('GetSetPokedexFlag',n,2);call('GetSetPokedexFlag',n,3)
 call('CB2_OpenPokedexFromStartMenu');wait('Task_PokedexScreen',6)
 e.press('A');p=wait('Task_DexScreen_NumericalOrder',6)
 assert e.u8(p+66)==0 and e.u16(p+72)==151
 start=e.save_state()
 for label,keys in [('idle',()),('down',('DOWN',)),('idle_repeat',())]:
  e.load_state(start);p=dex();a=S+128;backup=e.read(a,24)
  e.write(a,struct.pack('<10HI',0x1c01,0x0080,0x1840,0x00c0,0x4902,0x1840,0x8801,0x3101,0x8001,0x4770,sy['gTasks']+8))
  tid=call('CreateTask',a|1,255);assert tid<16
  ta=sy['gTasks']+40*tid;c=e.u16(ta+8);v=e.u32(sy['gMain']+36);f=e.frame()
  try:
   e.hold(*keys);e.run(360);e.hold()
   active=e.u8(ta+4) and (e.u32(ta)&~1)==a
   dc=(e.u16(ta+8)-c)&65535;dv=(e.u32(sy['gMain']+36)-v)&0xffffffff;df=e.frame()-f
   emit('kanto_comparison',dict(case=label,rom_sha=h(rb),hardware=df,vblank=dv,tasks=dc,missed=max(0,df-dc),counter_survived=bool(active),task_data_sha=h(e.read(ta+8,32)),scope='same copied v1.2/all-seen/Kanto151/default numeric menu'))
   assert active and df==360 and abs(df-dv)<=1
  finally:
   e.hold()
   if e.u8(ta+4) and (e.u32(ta)&~1)==a:call('DestroyTask',tid)
   e.write(a,backup)
 e.load_state(pristine)
'''
p=pathlib.Path('outputs/regional-dex-story-v1/kanto-old-new-comparison.py');p.write_text(base+tail)
out=pathlib.Path('work/current-integration-v8-path.txt').read_text().strip()
for label,rom,elf in [('old',out+'/pokemonthyl.gba.before-v8',out+'/pokemonthyl.elf.before-v8'),('new','pokemonthyl.gba','pokemonthyl.elf')]:
 log=pathlib.Path('outputs/regional-dex-story-v1/comparison-'+label+'.log')
 with log.open('w') as f:r=subprocess.run(['python3','-B',str(p),rom,'saves/pokemonthyl_v1.2.sav',elf],stdout=f,stderr=subprocess.STDOUT)
 print('PERF_COMPARE',label,r.returncode,log.read_text()[-5500:],flush=True)
