정"""Native-key scene6 SAVE -> Dewford boat -> Brawly -> Badge02/TM08.
Resumes an unedited natural QA battery checkpoint; inherited earlier eligibility
fixture is disclosed. No RAM writes, save edits, forced scripts/results or warps.
Only the prior ongoing parcel reward is inspected, not replayed.
"""
import argparse, ast, hashlib, json, os, struct, sys, traceback
from collections import deque
from pathlib import Path
R6='0eee66671ba7af7309117d098296a233a58985f9da881b4d4a8a479780f1ea1a'
PRIOR='37966a11833191dc2ad6cb0ee26df2a4226db9f3d7c673c2fe11bd7a66601641'
SEED='888f205f324d696415e9206e55ea2f8dc73d71a7141ff06c3030392270898fb4'
USER='917c24715ca1dd78b22d6350182648fa81f307b771fa5524595d157a0b6a6604'
BASE='work/misty-followup-20261014/'
CHECKPOINT='work/hoenn-resume-20261014/native-dewford-r2/failed-native-continuation-native-QA-only.sav'
CHECKPOINT_SHA=None  # Required CLI hash must equal the preserved natural SAVE74.
CHECKPOINT_REPORT='work/hoenn-resume-20261014/native-dewford-r2/validation.json'
CHECKPOINT_REPORT_SHA='3a9ff1556a8a9771b7df2aee998d0924f1e04457c9e020ed117355d946e7fc80'
SOURCE_HASHES={'data/maps/PetalburgWoods/scripts.inc': 'fe6b8eef9c01cd6b87cc956b705b5aded3cfb558d413c29d78a4758d2b1480b9', 'data/maps/RustboroCity_DevonCorp_3F/map.json': '04ea081e3cd15a31bc2fd2a284f3d40075f157ebdd8d6a678144421c42cb75c3', 'data/maps/SlateportCity_Harbor/scripts.inc': 'b2662fae38a01e75163a736b4f9a0e05db05e3e505276b8d052cf146503ced95', 'data/layouts/HoennRoute104/border.bin': 'aa298641e3346d9c7ac51454222ff057768946e61980fd82e4db65912df412fe', 'data/maps/RustboroCity_DevonCorp_2F/scripts.inc': '91d529b3199102d53817c6d6449ddd7fe58d82a5db9853f63e2551e72c5e8c0a', 'data/maps/SlateportCity/map.json': '4e768ba910ba8767b99d5c3ce29a02c8e9aaf7d66dd09a703f91edb5cbb33fe4', 'work/hoenn-resume-20261014/native-continuation-r4/validation.json': '090fa55d12da7bf45cb7e769503201208dc25a53fb464afbeda677f582e9298c', 'data/maps/PetalburgWoods/map.json': 'b3ec7e0535734e4abdad38ec298c4a4b695161545d5afb4d7567ae4ba48bdd0e', 'data/maps/RustboroCity_DevonCorp_2F/map.json': 'c76414777e7fea26acccb13c9db35b4ad63b7bafbd0b10963521356a9ff9410b', 'data/layouts/HoennSlateportCity/border.bin': '0c2871e576a63043efd779a5664d84741cc6512c07b03ae39e8deb07b064d3a4', 'data/maps/SlateportCity_Harbor/map.json': '31d2a3475249aaaac9325492938dc572520dfcde2398c8091ea1f59c13e99ae7', 'data/maps/Route104/scripts.inc': '7bf2c88a24b3b77c36836b09264a35e3ea25bcecc35d700f15d3ea59d74d6844', 'data/layouts/HoennHarbor/map.bin': 'ec418c60c4f5cac3eb4ee9e2a29e1f48709e552411f67086a5352945001afcbc', 'src/field_specials.c': 'f8448fb911ce7fb8d16a28bd58aeda8890d11c1d7f60211793cb279661331a87', 'data/layouts/HoennPetalburgWoods/map.bin': '053fc2e64d7065edaf0bfaa4b7504fef15ad808dc458f8b937cb3a2604495442', 'work/hoenn-resume-20261014/native_devon_continuation_r4.py': '7232e75f505432b542ecaa28310c3ddb4a257958a6f5c826b4711b6718b12978', 'data/layouts/HoennRustboroCity_DevonCorp_1F/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRustboroCity_DevonCorp_2F/map.bin': '2b6356ff72f7a014080fb98be0a9d59f7c8ecb16264af571d41436d82efec11e', 'data/layouts/HoennRustboroCity_DevonCorp_3F/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRustboroCity/map.bin': '5d1838e9e5c8f8a3bd519b0f7adaf1f01ef556deb9f8d5b46ec5996b26d51c4d', 'work/hoenn-resume-20261014/native-continuation-r3/pre-Stone-continuous-native-QA-only.sav': '9dbb27eb6951a1f62af50f35c4411b8a49adcf5cf8b682f9231db333ce4ebf93', 'data/maps/Route104/map.json': '113e20ea3e11db734eb88f5b894ed994986e516a4c482ffc4919ef2167f624d8', 'data/layouts/HoennRoute109/map.bin': '4f6c0180928cdc3268eaef6331137696f24626c9e618361b937a1d0b9a664d23', 'work/hoenn-resume-20261014/native-continuation-r4/continuous-Stone-request-native-QA-only.sav': '6db6e30c011568151cbb647be4d4dd92b78489f7c025150c6236df7a0937404c', 'data/maps/RustboroCity/scripts.inc': '70f4a1df10854a9ebe202de377b4a693e3bf9f8e5bf866d377712a1116d7a990', 'data/layouts/layouts.json': '98bf104f2682e018439f22092d0321c3c75b7cb1a0c5d1a45e3135a9076ba75c', 'data/maps/RustboroCity_DevonCorp_1F/scripts.inc': '0b8f42c5311d986a17d2c65fddb19a43e13b48fd53519a1048ac6e3b526c4e7e', 'work/hoenn-resume-20261014/native-continuation-r3/validation.json': 'b3d98bacf4a83f192e6a8a18ae2cafc29cd52ba87c9cfc99e3e80f218ac0a2e1', 'data/maps/Route109/scripts.inc': 'd3543f7f44b7609612e4240cb9e85c7c770fa7e46126f5471658fb29d8e3ded9', 'data/maps/RustboroCity/map.json': 'f0271bcea1cf27c09c8e4b659c07fcc011825ee60f885d904d22f5962e2a3d92', 'data/layouts/HoennHarbor/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRoute104/map.bin': '4dcbb4276d1010228e45ebe2dd1e3c9c2bd5843ba127ae108968c646d41f4329', 'work/hoenn-resume-20261014/abi-profile/devon-v7-abi.json': 'fb95943ada51c72d99456b5127fe147878593e166c2e9d12a9b46d0a4fb6ffac', 'data/layouts/HoennPetalburgWoods/border.bin': 'aa298641e3346d9c7ac51454222ff057768946e61980fd82e4db65912df412fe', 'data/maps/RustboroCity_DevonCorp_1F/map.json': '1e62fe59520f4e18e98f95140297e7668ed6ac41cae0b2072daf97acd56139bd', 'data/maps/Route109/map.json': '158c191d3c17391be4e8b4ebb4bf772682331ea590180959b11cb7fbc535114d', 'data/layouts/HoennRustboroCity_DevonCorp_2F/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRustboroCity/border.bin': 'aa298641e3346d9c7ac51454222ff057768946e61980fd82e4db65912df412fe', 'data/layouts/HoennSlateportCity/map.bin': '7094d5feff9cdd39816b71b7aaa31cf9c099c0d06f0a85e9b048d3a801cec136', 'data/layouts/HoennRoute109/border.bin': '0c2871e576a63043efd779a5664d84741cc6512c07b03ae39e8deb07b064d3a4', 'data/maps/RustboroCity_DevonCorp_3F/scripts.inc': 'e5832efa342f5554cbbcf8c46f39d166099c3883baaaed6482707386cd895ba4', 'data/maps/SlateportCity/scripts.inc': 'd824178a79762249d651aa0cbbb01e42c7d5b1d42b6413895ab6b1bd9be53934', 'data/layouts/HoennRustboroCity_DevonCorp_1F/map.bin': '4c5ad76bd2fb5a4d65914978338551c240f2e966c6f8f5a91346db1118bf6cbc', 'data/layouts/HoennRustboroCity_DevonCorp_3F/map.bin': '9805c919da40c085f1347a6b5f22ea3f928d3801204c7fe2aa0a63c4e46b2129', 'src/script_menu.c': '2db6f57f7626596dbe535e0822df38e1dbd5be683e5bda480fd4b7f8b00099d5', 'include/constants/menu.h': '1e4da1925ac7c158c1009ea99f30e85c864ef6bc5bbe6e22b23bc43d7d0f8e42', 'src/battle_controller_player.c': '7b06dd00b081fc88caa550b6533f191a14c2f3f2164cf3e334c31794c1b8d277', 'include/battle_controllers.h': '051ebf096d6538d1cc7ea321dacf5d3e9e54f0d4edc9ddeb29996242de618120', 'include/constants/party_menu.h': 'fc481059b8088c9e64d8a813e93232bd11b0ae31e7853e269c982372b682283f', 'include/battle.h': '9b774f757d1e5aa72f3ebcf4ced3a12c165c28ff848e2bb529d228534a4b206d', 'src/battle_main.c': '2a39e045ff105b9c265173de81d5a88c6ab2146052d5a918a63112b0e3562920', 'work/hoenn-resume-20261014/native_double_controller_r2.py': '30346bab00d76d1b553c6aaffa89212909042fc11a24624c6715a23f850073ec', 'data/layouts/HoennDewfordTown/border.bin': '558c2fc1783459a6a4687e1fea767e8d4e30bc4ece5f37a0433fd5f7f58e5e9c', 'data/layouts/HoennDewfordTown/map.bin': 'f99942a2f630ca1fc16d7d84f7f831485934962c4477e8b1fa88cfbe30c61f74', 'data/layouts/HoennDewfordTown_Gym/border.bin': 'efef8d5a9f8dbe5bb218e6b0cc452583eb9d1452b615b1c7ab66ad49c82e9d70', 'data/layouts/HoennDewfordTown_Gym/map.bin': 'b4b06558fc3ada623e51389ea679dae72c17cf8111b6054c7b2436a4dff09d9e', 'data/layouts/HoennGraniteCave_1F/border.bin': 'a8fb987bcf19f3554623d70e41906b5eb019ae568cb1b0d5eed634c70b24f12a', 'data/layouts/HoennGraniteCave_1F/map.bin': '6e8e5420747a9e2c18c9ecc04e43e028cac70e6030a8015a52edcac739459bbf', 'data/layouts/HoennGraniteCave_B1F/border.bin': 'a8fb987bcf19f3554623d70e41906b5eb019ae568cb1b0d5eed634c70b24f12a', 'data/layouts/HoennGraniteCave_B1F/map.bin': 'b9598bdd24ac4358679e255dc07052b2687c2babef091ff6174115c19409c7c5', 'data/layouts/HoennGraniteCave_B2F/border.bin': 'a8fb987bcf19f3554623d70e41906b5eb019ae568cb1b0d5eed634c70b24f12a', 'data/layouts/HoennGraniteCave_B2F/map.bin': 'a4937ea8f0329dd8f6512f893cda7280327044d1af0f99e1fee14ef03d05475b', 'data/layouts/HoennGraniteCave_StevensRoom/border.bin': 'a8fb987bcf19f3554623d70e41906b5eb019ae568cb1b0d5eed634c70b24f12a', 'data/layouts/HoennGraniteCave_StevensRoom/map.bin': 'ddf261937693159207733f50eabcbc29a90accc6653a82ebf013701e5774f270', 'data/maps/DewfordTown/map.json': '5ab22b4d46ff4aa9e44e73af54bb51e00c3339ebb2761dd98aa03165e50e2350', 'data/maps/DewfordTown/scripts.inc': 'fd4e70b1595f1ba543fc4c9d491aa11d9aa2e5c9768248b1fff6f8c3bf106248', 'data/maps/DewfordTown/text.inc': '2ff3f0d46d64621d55374ad5212f3c3af253bfa7dd09634646c20a2303810545', 'data/maps/DewfordTown_Gym/map.json': '368c368a5db3822d4279cff2423d3d02f1998d1cfb4de6e5196ab625ecc013e6', 'data/maps/DewfordTown_Gym/scripts.inc': '6229087286390685b8599cb55fcd5b96e0407ae4252aa9bf7771229544b8cf06', 'data/maps/DewfordTown_Gym/text.inc': '43ec3eb1f3159a95620bb5ae7c0a0729655db56e751dd2001ac431b3c91cdd0a', 'data/maps/GraniteCave_1F/map.json': '902c84870a4655ed0b8bccf760f738bd4a4927aa4a14bb4803f99d792c9659c5', 'data/maps/GraniteCave_1F/scripts.inc': 'ece96d165cb2947a5d87a8a2843a12a776400ebbce875c9271a7a28229d98a90', 'data/maps/GraniteCave_1F/text.inc': '64ba768b4b939ff5a0e96c8c29843b8c69f08efaf437d9032e64971450a66cd2', 'data/maps/GraniteCave_B1F/map.json': '7701e721e1225aac3289d5fedcadda1c3a1b8e9709dba187718a3141cc23f91f', 'data/maps/GraniteCave_B1F/scripts.inc': 'd46e4ce51bc5609d67e67c3750b366e0504c9782326875b01a407c975d2b1029', 'data/maps/GraniteCave_B1F/text.inc': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'data/maps/GraniteCave_B2F/map.json': '8b7b90633e44e89bede23bf4edb89aa50d29f36fcebac5d0f66897572d9e81b9', 'data/maps/GraniteCave_B2F/scripts.inc': '658ec3088dddb6a43db9346b42c1f39cd0fbc5741c13eb8d5adaf8b127cc9129', 'data/maps/GraniteCave_B2F/text.inc': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'data/maps/GraniteCave_StevensRoom/map.json': '44043d1e52d9dfccf059ff6408884a147e6605f19cf0b6a9b488a950fc0daf6d', 'data/maps/GraniteCave_StevensRoom/scripts.inc': '022782f64af3aacf5b6ac9c765f2498e54b1cb55281303a7c6ab43dc09208e33', 'data/maps/GraniteCave_StevensRoom/text.inc': '4c94c399e221e39a14bd95fc55c76de4377316e4698d708c4d864aee733d733c', 'include/constants/flags.h': '6645d8d43ad378b3f6707c8c3af2cc7da1f5acca7cfb48917b94631ec18f5d29', 'include/constants/flags_hoenn_story.h': '493679980358d6b5a5f98d1cd7283ec211f20240e435b91711baa8c1a0debb1f', 'include/constants/vars.h': 'c3c27b43a9db279da766aa9d94af0b28aa8c42a49a87fabca1b4a1ec20ade947', 'include/constants/vars_hoenn.h': '49c049d9554ebaecc6c69a05aa4ec635a43f5d7675b9ccc3b2636ae5e3d45b65', 'include/pokedex.h': 'a7ea835c8327b5f17c5a766090829e49e694e5439b796634d1e1746867b29e8a', 'include/pokedex_area_markers.h': '244b866c83476824d8f407f4b4b681a210a292e056b49c3ce60f6b66a0e3e341', 'include/pokedex_screen.h': '62151ddb84111da7ae854403335fe7f2ddc7dce45e947a445713f6d70447d9d4', 'src/pokedex.c': 'aac08b88d35a69cab82df72d6f759cf3d7f4c1620935657f5450ed7f197ba3e4', 'src/pokedex_area_markers.c': 'af38f08aec2f388b6833d69c49ab10248dee3da4c17a33b7ae9fa27e97110aca', 'src/pokedex_screen.c': 'd7cd34bed4bdee8a2e76950636a093f726eb79268b2aed6b96bf31139c1ea4c7', 'src/event_object_movement.c': '241a15df4e9977c0fb3a8e84507623476470f18de0a1862a8457bb96fbf6a420'}
KEYS={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}
FLAGS=['FLAG_HOENN_GOT_DEVON_GOODS','FLAG_HOENN_PEEKO_RESCUED','FLAG_HIDE_HOENN_RUSTURF_GRUNT',
       'FLAG_HIDE_HOENN_RUSTURF_PEEKO','FLAG_HOENN_DEVON_GOODS_DELIVERED','FLAG_HOENN_GOT_EXP_SHARE']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for n in ['root','rom','elf','sav','abi-json','out']:p.add_argument('--'+n,required=True,type=Path)
 for n in ['rom','elf','abi','checkpoint']:p.add_argument('--expect-'+n+'-sha',required=True)
 p.add_argument('--confirmed-dock-report',required=True,type=Path)
 p.add_argument('--expect-dock-report-sha',required=True)
 global CHECKPOINT_SHA
 args=p.parse_args();CHECKPOINT_SHA=args.expect_checkpoint_sha;assert CHECKPOINT_SHA=='fc6ab5663fc0384f31a18c2eac3218434c07d71dae33faae586d994b13cc5342'
 root=args.root.resolve(strict=True);os.chdir(root)
 args.out=args.out.resolve();assert not args.out.exists() and args.out.is_relative_to(root/'work')
 for n in ['rom','elf','sav','abi_json']:setattr(args,n,getattr(args,n).resolve(strict=True))
 ctl=root/(BASE+'r2-tools/native-devon-v7-r6.py');prior=root/(BASE+'native-v7-r6/validation.json');seed=root/(BASE+'native-v7-r6/scene1-Devon-native-QA-only.sav')
 checkpoint=root/CHECKPOINT;checkpoint_report=root/CHECKPOINT_REPORT
 inputs={ctl:R6,prior:PRIOR,seed:SEED,checkpoint:CHECKPOINT_SHA,checkpoint_report:CHECKPOINT_REPORT_SHA,args.sav:USER,args.rom:args.expect_rom_sha,args.elf:args.expect_elf_sha,args.abi_json:args.expect_abi_sha}
 inputs.update({root/rel:h for rel,h in SOURCE_HASHES.items()})
 dock_report=args.confirmed_dock_report.resolve(strict=True);assert dock_report.is_relative_to(root/'work')
 inputs[dock_report]=args.expect_dock_report_sha
 inputs[root/'work/hoenn-resume-20261014/native-dewford-dock-r5/validation.json']='665ba27317565cf0aded40e334b349457a3e3816fcdb602647926b42a5757798'
 inputs[root/'work/hoenn-resume-20261014/native-dewford-r4/validation.json']='268f81ef7d901ed2ec6a0d83386a0dfd65e4dee35af9a3723847a9667cfdfa01'
 inputs[root/'work/hoenn-resume-20261014/native-dewford-r1/validation.json']='ee95905a4626aca3552e5afe0fb76440e2c1e3b3b5229153d8afcc225e5aedd1'
 for f,h in inputs.items():assert len(h)==64 and sha(f)==h,('Input changed',str(f))
 old=json.loads(prior.read_text());case=[c for c in old['cases'] if c['scene_at_boot']==1]
 assert old['pass'] and old['protected_original_inputs_unchanged'] and old['SAV_sha256']==USER
 assert len(case)==1 and case[0]['pass'] and case[0]['actual_Roxanne_win'] and case[0]['continuous_Gym_exit_and_City_coord'] and case[0]['expected_theft']
 assert Path(case[0]['SAVE_cold']['qa_save']).resolve()==seed.resolve()
 previous=json.loads(checkpoint_report.read_text())
 assert not previous['pass'] and previous['status']=='failed' and previous['protected_original_inputs_unchanged']
 assert previous['ROM_sha256']=='0845f8cbc1afa5d957a64f76a4ae2700606175dd55bcd101184e6ba2a650b7fa' and previous['ELF_sha256']=='e625069ea9379ea3dc2f83e3014fb741a2e0b7383f41f6d56bc37fc0eae6f17b' and previous['SAV_sha256']==USER
 proof=json.loads(dock_report.read_text())
 assert not proof['pass'] and proof['status']=='confirmed_gameplay_blocker' and proof['native_four_direction_dock_trap_confirmed'] and proof['protected_original_inputs_unchanged']
 assert proof['ROM_sha256']==previous['ROM_sha256'] and proof['ELF_sha256']==previous['ELF_sha256']
 assert all(proof[k]==0 for k in ['RAM_writes','direct_script_calls','forced_battle_outcomes'])
 probes=proof['dock_direction_probes'];assert len(probes)==4 and {p['key']for p in probes}=={'DOWN','UP','RIGHT','LEFT'}
 assert all(p['blocked'] and p['actual_keys'] and p['start']==[43,11,13,9] and p['finish']==p['start'] and p['field_idle'] for p in probes)
 assert args.expect_rom_sha!=previous['ROM_sha256'] and args.expect_elf_sha!=previous['ELF_sha256'], 'This runner requires the rebuilt dock-fix candidate'
 assert all(previous[k]==0 for k in ['RAM_writes','direct_script_calls','forced_battle_outcomes'])
 assert previous['error']=="AssertionError(('No actual collision/elevation-valid path', (13, 9, 3), (8, 18), [(7, 12), (12, 8), (12, 9), (12, 14)]))"
 arrival=[r for r in previous['stages']if r['stage']=='03-native-Dewford-arrival'];assert len(arrival)==1
 assert arrival[0]['location']==[43,11,13,9] and arrival[0]['scene']==6 and arrival[0]['briney']==1 and arrival[0]['Dewford_visible'] and arrival[0]['idle']
 assert previous['boat_menus'][-1]['destination']=='DewfordTown' and previous['boat_menus'][-1]['actual_keys']
 saved_checkpoint=previous['failure_native_SAVE_cold']
 assert Path(saved_checkpoint['qa_save']).resolve()==checkpoint.resolve()
 assert saved_checkpoint['counter']==[73,74] and saved_checkpoint['checksummed_sectors']==14
 text=ctl.read_text();tree=ast.parse(text);tries=[n for n in tree.body if isinstance(n,ast.Try)];assert len(tries)==1
 prefix=tree.body[:tree.body.index(tries[0])];body=[];removed=0
 for n in tries[0].body:
  if isinstance(n,ast.FunctionDef) and n.name=='fixture':break
  if isinstance(n,ast.Assert) and n.msg and isinstance(n.msg,ast.Constant) and n.msg.value=='This v7 is prepared for the approved e156 ROM':removed+=1;continue
  body.append(n)
 assert removed==1 and any(isinstance(n,ast.FunctionDef) and n.name=='native_send_out' for n in body)
 sys.argv=['continuation','--root',str(root),'--rom',str(args.rom),'--elf',str(args.elf),'--sav',str(args.sav),'--expect-rom-sha',args.expect_rom_sha,'--expect-elf-sha',args.expect_elf_sha,'--expect-sav-sha',USER,'--abi-json',str(args.abi_json),'--out',str(args.out)]
 ctx={'__file__':str(ctl),'__name__':'verified_continuation_controller'};e=None;report=None
 try:
  exec(compile(ast.Module(body=prefix+body,type_ignores=[]),'<verified-r6-preflight-controller>','exec'),ctx)
  report=ctx['report'];report.update({'pass':False},status='running',runner_version=9,runner_revision=6,cases=[],stages=[],steps=[],battles=[],
   scope='Narrow dock repair only: unmodified natural SAVE74 legacy recovery, real land movement, actual return/reboard boat, safe new landing and native SAVE/cold; Brawly loss retained and progression not claimed',prior_preboot_eligibility_fixture=True,
   this_test_preboot_save_edits=0,full_Hoenn_campaign_tested=False,actual_device_fps_measured=False,Brawly_completed=False,earlier_parcel_route_replayed=False,
   continuation_seed_sha256=CHECKPOINT_SHA,prior_route_seed_sha256=SEED,prior_validation_sha256=PRIOR,prior_native_SAVE=case[0]['SAVE_cold'])
  ctx['protected'].update({f.resolve():h for f,h in inputs.items()});gd,off,const,syms=[ctx[n]for n in ['gd','off','const','syms']]
  for h in ['fieldmap.h','constants/metatile_behaviors.h','constants/menu.h','constants/party_menu.h']:
   if h not in gd.CONST_HEADERS:gd.CONST_HEADERS.append(h)
  for typ,fields in {'MapHeader':['mapLayout','events'],'MapLayout':['width','height','primaryTileset','secondaryTileset'],
   'BackupMapLayout':['Xsize','Ysize','map'],'MapEvents':['warpCount','warps'],'WarpEvent':['x','y','mapNum','mapGroup'],
   'Tileset':['isEmerald','metatileAttributes']}.items():
   for f in fields:gd.FIELDS['next.'+typ+'.'+f]=(typ,f)
  gd.FIELDS.update({'next.WarpEvent':('WarpEvent',None),
                   'next.BackupMapLayout':('BackupMapLayout',None),
                   'next.MapHeader':('MapHeader',None)})
  gd._OFFSETS=None
  report['compiler_map_offsets']={k:off(k)for k in gd.FIELDS if k.startswith('next.')}
  map_bindings={}
  sizes={'VMap':off('next.BackupMapLayout'),
         'gMapHeader':off('next.MapHeader'),
         'gObjectEvents':off('misty_obj')*const('OBJECT_EVENTS_COUNT')}
  assert const('OBJECT_EVENTS_COUNT')==16
  for name,wanted_size in sizes.items():
   rows=ctx['actual_rows'].get(name,[])
   assert len(rows)==1,('Missing/ambiguous current ELF map symbol',name,rows)
   row=rows[0]
   assert (row['info']&15)==1 and row['size']==wanted_size,('Map symbol type/size mismatch',name,row,wanted_size)
   value=row['value']
   in_ram=(0x02000000<=value and value+wanted_size<=0x02040000) or (0x03000000<=value and value+wanted_size<=0x03008000)
   assert in_ram,('Map symbol is not RAM data',name,row)
   sec=ctx['sections'][row['section']]
   assert sec[2]&3==3 and sec[3]<=value and value+wanted_size<=sec[3]+sec[5],('Map symbol section containment failed',name,row,sec)
   syms[name]=value
   map_bindings[name]=row
  report['current_ELF_map_symbol_bindings']=map_bindings
  report.update(checkpoint_sha256=CHECKPOINT_SHA,checkpoint_validation_sha256=CHECKPOINT_REPORT_SHA,prior_partial_Dewford_checkpoints=previous['stages'],prior_checkpoint_SAVE_cold=saved_checkpoint,current_Dewford_route_and_battles_replayed_this_run=True,previous_failed_r1_report_sha256='ee95905a4626aca3552e5afe0fb76440e2c1e3b3b5229153d8afcc225e5aedd1')
  seedfile=ctx['SaveFile'](str(checkpoint))
  assert len(seedfile.layout)==14 and seedfile.counter==74
  for _,sid,size in seedfile.layout:
   pos=seedfile.where[sid]*4096
   assert ctx['checksum'](seedfile.raw[pos:pos+size])==struct.unpack_from('<H',seedfile.raw,pos+0xff6)[0],('Checkpoint sector checksum',sid)
  assert seedfile.var('VAR_HOENN_SCENE_DEVON')==6 and seedfile.flag('FLAG_HOENN_BADGE01_GET')
  assert not seedfile.flag('FLAG_HOENN_BADGE02_GET') and not seedfile.flag('FLAG_HOENN_GOT_TM08_FROM_BRAWLY')
  assert not seedfile.trainer_beaten('TRAINER_HOENN_BRAWLY_1'), 'Brawly already beaten; this checkpoint cannot prove a new native fight'
  assert seedfile.trainer_beaten('TRAINER_HOENN_ROXANNE_1') and seedfile.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL')
  assert seedfile.item_count('ITEM_DEVON_GOODS')==0 and all(seedfile.flag(f)for f in FLAGS)
  e=ctx['ReadOnlyEmu'](str(args.rom),str(checkpoint),sym='');ctx['e']=e;e.syms=syms;e.boot_continue();ctx['settle'](e);before=ctx['snapshot'](e)
  assert e.location()==(43,11,11,9),('Legacy SAVE did not automatically recover to the legal land side',e.location())
  assert before['party']==bytes(seedfile.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
  assert before['party_count']==seedfile.party_count() and before['pc']==bytes(seedfile.blocks['storage'])
  assert before['dex']==[seedfile.dex_state(i)for i in range(1,387)]
  assert all(ctx['blocks'](e).flag(f)==seedfile.flag(f) for f in before['flags'])
  assert all(ctx['blocks'](e).trainer_beaten('TRAINER_JOHTO_'+n)==seedfile.trainer_beaten('TRAINER_JOHTO_'+n) for n in before['trainers'])
  hvo=off('sb2.hoennVars');hvs=2*(const('HOENN_VARS_END')-const('HOENN_VARS_START')+1)
  hfo=off('sb2.hoennFlags');hfs=(const('HOENN_FLAGS_COUNT')+7)//8
  assert ctx['blocks'](e).sb2[hvo:hvo+hvs]==seedfile.sb2[hvo:hvo+hvs]
  assert ctx['blocks'](e).sb2[hfo:hfo+hfs]==seedfile.sb2[hfo:hfo+hfs]
  report['automatic_legacy_recovery']={'old_position':[43,11,13,9],'new_position':list(e.location()),'checkpoint_untouched':True,'party_600_PC_33744_dex_Hoenn_flags_vars_preserved':True,'confirmed_old_trap_report_sha256':args.expect_dock_report_sha}
  def state():
   b=ctx['blocks'](e)
   return dict(location=list(e.location()),scene=b.var('VAR_HOENN_SCENE_DEVON'),briney=b.var('VAR_HOENN_BRINEY_STATE'),flags={f:b.flag(f)for f in FLAGS},Goods=b.item_count('ITEM_DEVON_GOODS'),DiveBalls=b.item_count('ITEM_DIVE_BALL'),ExpShare=b.item_count('ITEM_EXP_SHARE'),grunt_won=b.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL'),twins_won=b.trainer_beaten('TRAINER_HOENN_GINA_AND_MIA_1'),Badge02=b.flag('FLAG_HOENN_BADGE02_GET'),TM08_reward=b.flag('FLAG_HOENN_GOT_TM08_FROM_BRAWLY'),TM08=b.item_count('ITEM_TM08'),Brawly_won=b.trainer_beaten('TRAINER_HOENN_BRAWLY_1'),stage1_progress=b.var('VAR_HOENN_STAGE1_PROGRESS'),Dewford_visible=b.flag('FLAG_HOENN_WORLD_MAP_DEWFORD_TOWN'),Pikachu_gym_seen=b.flag('FLAG_HOENN_PIKACHU_GYM_SEEN'),idle=bool(e.field_idle()))
  ctx['state']=state
  def stage(label):
   image=args.out/(label+'.png');e.shot(str(image),scale=3);report['stages'].append(dict(stage=label,frame=e.frame(),image=str(image),**state()));ctx['emit']()
  controller_path=root/'work/hoenn-resume-20261014/native_double_controller_r2.py'
  controller_scope={'__file__':str(controller_path)}
  exec(compile(controller_path.read_text(),str(controller_path),'exec'),controller_scope)
  controller_scope['install'](ctx)
  def fight():return ctx['fight_native_indexed']()
  def idle():
   for _ in range(1800):
    ctx['safe'](e)
    if e.in_battle() or ctx['is_party_menu']():fight();continue
    if e.field_idle():return
    e.press('B',hold=2,after=14)
   raise AssertionError(('Native field event timeout',state()))
  ctx['idle']=idle
  def matches(name):
   m=ctx['map_info'](name);return e.location()[:2]==(m['group'],m['num'])
  def geom():
   layout=e.u32(syms['gMapHeader']+off('next.MapHeader.mapLayout'));w=e.u32(layout+off('next.MapLayout.width'));h=e.u32(layout+off('next.MapLayout.height'))
   bk=syms['VMap'];stride=e.u32(bk+off('next.BackupMapLayout.Xsize'));rows=e.u32(bk+off('next.BackupMapLayout.Ysize'));ptr=e.u32(bk+off('next.BackupMapLayout.map'))
   assert 1<=w<=256 and 1<=h<=256 and stride>=w+14 and rows>=h+14 and 0x02000000<=ptr and ptr+stride*rows*2<=0x02040000
   return layout,w,h,stride,rows,ptr
  def tile(x,y):
   l,w,h,stride,rows,ptr=geom();pad=const('MAP_OFFSET');assert pad==7 and 0<=x+pad<stride and 0<=y+pad<rows
   return e.u16(ptr+2*((y+pad)*stride+x+pad))
  def behavior(x,y):
   l=geom()[0];primary=e.u32(l+off('next.MapLayout.primaryTileset'));secondary=e.u32(l+off('next.MapLayout.secondaryTileset'))
   split=const('EMERALD_NUM_METATILES_IN_PRIMARY'if e.u8(primary+off('next.Tileset.isEmerald'))else'NUM_METATILES_IN_PRIMARY')
   mid=tile(x,y)&1023;ts,index=(primary,mid)if mid<split else(secondary,mid-split);attr=e.u32(ts+off('next.Tileset.metatileAttributes'));assert 0x08000000<=attr<0x0a000000
   return e.u32(attr+4*index)&511
  def warps():
   events=e.u32(syms['gMapHeader']+off('next.MapHeader.events'));n=e.u8(events+off('next.MapEvents.warpCount'));ptr=e.u32(events+off('next.MapEvents.warps'));assert n<=64;rows=[]
   for i in range(n):
    q=ptr+i*off('next.WarpEvent');rows.append(dict(x=struct.unpack('<h',e.read(q+off('next.WarpEvent.x'),2))[0],y=struct.unpack('<h',e.read(q+off('next.WarpEvent.y'),2))[0],group=e.u8(q+off('next.WarpEvent.mapGroup')),num=e.u8(q+off('next.WarpEvent.mapNum'))))
   return rows
  def actors():
   occupied=set()
   for i in range(16):
    q=syms['gObjectEvents']+i*off('misty_obj');flags=e.u32(q)
    if flags&1 and not flags&(1<<16) and e.u8(q+off('misty_obj.local'))not in[253,254]:
     x,y=struct.unpack('<hh',e.read(q+off('misty_obj.coords'),4));occupied.add((x-7,y-7))
   return occupied
  native_step=ctx['step']
  def step(key,dest=None):
   start=e.location()
   try:native_step(key,warp=bool(dest))
   except AssertionError as blocked:
    reason=blocked.args[0] if blocked.args else None
    # A fixed solid tile remains a failure. Non-idle fade, pending real wild
    # battle or native field dialogue gets its real keys before one retry.
    if not isinstance(reason,tuple) or reason[0]!='Native step blocked' or e.field_idle():raise
    ctx['safe'](e)
    assert e.location()==start,('Blocked-step interruption changed coordinates',start,e.location())
    pending=dict(key=key,location=list(e.location()),field_idle=bool(e.field_idle()),frame=e.frame(),callback=hex(e.callback2()),in_overworld=bool(e.in_overworld()),in_battle=bool(e.in_battle()),battle_count_before=len(report['battles']))
    idle();assert e.location()==start,('Pending native field/battle event moved player',start,state())
    pending.update(after_actual_keys=list(e.location()),after_frame=e.frame(),after_callback=hex(e.callback2()),battle_count_after=len(report['battles']),actual_battles_during_wait=report['battles'][pending['battle_count_before']:],retried_once=True)
    report.setdefault('pending_native_event_retries',[]).append(pending);ctx['emit']()
    native_step(key,warp=bool(dest))
   idle()
   if e.location()[:2]!=start[:2]:assert dest and matches(dest),('Unexpected map',start,key,state())
   report['steps'].append(dict(key=key,start=list(start),finish=list(e.location()),frame=e.frame()))
  movement_source=(root/'src/event_object_movement.c').read_text()
  assert 'if (elevation == 0)' in movement_source and 'if (mapElevation == 0 || mapElevation == 15)' in movement_source
  assert 'objEvent->currentElevation = curElevation;' in movement_source
  def player_elevation():
   rows=[]
   for i in range(16):
    q=syms['gObjectEvents']+i*off('misty_obj');flags=e.u32(q)
    if flags&1 and flags&(1<<16):rows.append(e.u8(q+11)&15)
   assert len(rows)==1;return rows[0]
  def walk(goal,allowed=None,dest=None):
   initial=e.location()[:2]
   for _ in range(700):
    idle()
    if e.location()[:2]!=initial:assert dest and matches(dest);return
    start_xy=e.location()[2:]
    if start_xy==goal:return
    l,w,h,st,rows,ptr=geom();grid=e.read(ptr,st*rows*2);occupied=actors();excluded={(v['x'],v['y'])for v in warps()}-({allowed}if allowed else set())
    start=(*start_xy,player_elevation());queue=deque([start]);parents={start:None};found=None
    while queue:
     at=queue.popleft()
     if at[:2]==goal:found=at;break
     for key,(dx,dy)in KEYS.items():
      xy=(at[0]+dx,at[1]+dy)
      if xy in occupied or xy in excluded or not(0<=xy[0]<w and 0<=xy[1]<h):continue
      v=struct.unpack_from('<H',grid,2*((xy[1]+7)*st+xy[0]+7))[0];height=v>>12
      if ((v>>10)&3)or(v&1023)==1023:continue
      if at[2]!=0 and height not in [0,15,at[2]]:continue
      q=(*xy,at[2]if height==15 else height)
      if q in parents:continue
      parents[q]=(at,key);queue.append(q)
    assert found is not None,('No actual collision/elevation-valid path',start,goal,sorted(occupied))
    nxt=found
    while parents[nxt][0]!=start:nxt=parents[nxt][0]
    step(parents[nxt][1],dest)
   raise AssertionError(('Bounded walking did not finish',goal,state()))
  def transition(key,dest):
   start=e.location();e.hold(key)
   try:
    for _ in range(180):
     ctx['safe'](e);e.run(1)
     if e.location()!=start or not e.field_idle():break
    else:raise AssertionError(('Native transition ignored',start,key))
   finally:e.hold()
   idle();e.run(20);idle();assert matches(dest),('Native warp absent',dest,state())
   report['steps'].append(dict(key=key,transition=True,start=list(start),finish=list(e.location()),frame=e.frame()))
  def warp(xy,dest):
   m=ctx['map_info'](dest);rows=[v for v in warps()if(v['x'],v['y'])==xy];assert len(rows)==1 and(rows[0]['group'],rows[0]['num'])==(m['group'],m['num'])
   mb=behavior(*xy);initial=e.location()[:2]
   if mb==const('MB_WARP_DOOR'):walk((xy[0],xy[1]+1));transition('UP',dest);return
   walk(xy,allowed=xy,dest=dest)
   if e.location()[:2]!=initial:assert matches(dest);return
   directions={const('MB_EAST_ARROW_WARP'):'RIGHT',const('MB_WEST_ARROW_WARP'):'LEFT',const('MB_NORTH_ARROW_WARP'):'UP',const('MB_SOUTH_ARROW_WARP'):'DOWN',const('MB_UP_RIGHT_STAIR_WARP'):'RIGHT',const('MB_DOWN_RIGHT_STAIR_WARP'):'RIGHT',const('MB_UP_LEFT_STAIR_WARP'):'LEFT',const('MB_DOWN_LEFT_STAIR_WARP'):'LEFT'}
   assert mb in directions,('Warp tile did not activate',xy,hex(mb),state());transition(directions[mb],dest)
  def interaction_diag(label,local):
   assert off('misty_obj.coords')==16 and off('misty_obj.local')==8
   rows=[]
   for i in range(const('OBJECT_EVENTS_COUNT')):
    q=syms['gObjectEvents']+i*off('misty_obj');raw=e.read(q,off('misty_obj'));flags=struct.unpack_from('<I',raw)[0]
    if not(flags&1):continue
    is_player=bool(flags&(1<<16))
    if not is_player and raw[8]!=local:continue
    x,y=struct.unpack_from('<hh',raw,16);x-=7;y-=7
    rows.append(dict(slot=i,local=raw[8],player=is_player,graphics=raw[5],map=[raw[10],raw[9]],
     xy=[x,y],flags=hex(flags),visible=not bool(flags&((1<<13)|(1<<14))),
     current_elevation=raw[11]&15,previous_elevation=raw[11]>>4,direction=raw[24]&15,
     single_movement_active=bool(flags&(1<<1)),held_movement_active=bool(flags&(1<<6)),
     tile=hex(tile(x,y)),behavior=hex(behavior(x,y))))
   report.setdefault('interaction_diagnostics',[]).append(dict(label=label,frame=e.frame(),requested_local=local,
    location=list(e.location()),LastTalked=e.u16(syms['gSpecialVar_LastTalked']),objects=rows))
   ctx['emit']()
   return rows
  def talk(key,local):
   at=e.location();interaction_diag('before-turn',local)
   e.press(key,hold=4,after=30);rows=interaction_diag('after-turn',local)
   assert e.location()==at,('Turn unexpectedly moved player',at,e.location())
   player=[r for r in rows if r['player']];npc=[r for r in rows if not r['player']]
   assert len(player)==1 and len(npc)==1 and npc[0]['visible'],('Requested NPC absent/invisible',local,rows)
   wanted=const({'LEFT':'DIR_WEST','RIGHT':'DIR_EAST','UP':'DIR_NORTH','DOWN':'DIR_SOUTH'}[key])
   assert player[0]['direction']==wanted,('Native turn not settled',key,rows)
   e.press('A',hold=3,after=12);interaction_diag('after-actual-A',local)
   for _ in range(300):
    ctx['safe'](e)
    if not e.field_idle()or e.in_battle():break
    e.run(1)
   else:raise AssertionError(('Native A did not activate NPC',local,state(),rows))
   assert e.u16(syms['gSpecialVar_LastTalked'])==local;idle()
  menu_rows=[v for v in ctx['actual_rows'].get('Task_MultichoiceMenu_HandleInput',[]) if Path(v['translation_unit']).name in ['script_menu.o','script_menu.c']]
  assert len(menu_rows)==1;menu_row=menu_rows[0];menu_sec=ctx['sections'][menu_row['section']];menu_func=menu_row['value']&~1
  assert (menu_row['info']&15)==2 and menu_row['size']>0 and menu_sec[2]&6==6 and menu_sec[3]<=menu_func and menu_func+menu_row['size']<=menu_sec[3]+menu_sec[5]
  assert 0x08000000<=menu_func<0x0a000000
  report['boat_task_symbol_binding']=menu_row
  AF=ctx['AF'];assert AF['Task.size']==40 and ctx['ABI']['task_count']==16 and AF['Menu.cursorPos']==2
  def menu_tasks():
   return [i for i in range(ctx['ABI']['task_count']) if e.u8(syms['gTasks']+i*AF['Task.size']+AF['Task.isActive']) and (e.u32(syms['gTasks']+i*AF['Task.size']+AF['Task.func'])&~1)==menu_func]
  def boat(key,local,choice,dest,wanted_state):
   at=e.location();e.press(key,hold=4,after=30);assert e.location()==at
   e.press('A',hold=3,after=12)
   for _ in range(600):
    ctx['safe'](e)
    if menu_tasks():break
    assert not e.in_battle() and not ctx['is_party_menu']();e.run(1)
   else:raise AssertionError(('Real Briney menu did not open',local,state()))
   assert len(menu_tasks())==1 and e.u16(syms['gSpecialVar_LastTalked'])==local
   tag='boat-menu-'+str(len(report.get('boat_menus',[])));e.shot(str(args.out/(tag+'.png')),scale=3)
   cursor=lambda:e.u8(syms['sMenu']+AF['Menu.cursorPos']);trace=[]
   for _ in range(5):
    assert len(menu_tasks())==1;cur=cursor();trace.append(cur);assert 0<=cur<3
    if cur==choice:break
    e.press('DOWN' if cur<choice else 'UP',hold=2,after=14)
   else:raise AssertionError(('Real boat cursor did not select requested dock',choice,trace))
   assert cursor()==choice;e.press('A',hold=3,after=1)
   for _ in range(120):
    if not menu_tasks():break
    ctx['safe'](e);e.run(1)
   else:raise AssertionError('Real boat menu did not accept A')
   idle();assert matches(dest) and ctx['blocks'](e).var('VAR_HOENN_BRINEY_STATE')==const(wanted_state)
   report.setdefault('boat_menus',[]).append(dict(start=list(at),local=local,choice=choice,cursor_trace=trace,destination=dest,finish=list(e.location()),actual_keys=True));ctx['emit']()
  def scene(expected,goods,delivered,reward):
   b=ctx['blocks'](e)
   assert b.var('VAR_HOENN_SCENE_DEVON')==expected and b.item_count('ITEM_DEVON_GOODS')==goods
   assert all(b.flag(f)for f in FLAGS[:4]) and b.flag(FLAGS[4])==delivered and b.flag(FLAGS[5])==reward
  prior_loss=json.loads((root/'work/hoenn-resume-20261014/native-dewford-r4/validation.json').read_text())
  assert not prior_loss['pass']and prior_loss['protected_original_inputs_unchanged']and prior_loss['battles'][-1]['outcome']==const('B_OUTCOME_LOST')
  report['prior_Brawly_loss_retained']={'report_sha256':'268f81ef7d901ed2ec6a0d83386a0dfd65e4dee35af9a3723847a9667cfdfa01','actual_battle_outcome':2,'not_reclassified_as_pass':True}
  assert matches('DewfordTown')and e.location()[2:]==(11,9)
  scene(6,0,True,True);assert state()['briney']==const('BRINEY_AT_DEWFORD')and state()['Dewford_visible']
  baseline=state();assert not baseline['Badge02']and not baseline['TM08_reward']and not baseline['Brawly_won']
  report['resumed_natural_SAVE74']=saved_checkpoint;report['forest_delivery_Brawly_replayed_this_run']=False
  stage('00-natural-SAVE74-legacy-dock-recovery')
  step('LEFT');assert e.location()[2:]==(10,9);stage('01-legacy-dock-walks-onto-land')
  step('RIGHT');assert e.location()[2:]==(11,9)and len(ctx['object_rows'](e,5))==1
  boat('RIGHT',5,0,'Route104','BRINEY_AT_ROUTE104');scene(6,0,True,True);stage('02-actual-Briney-return104')
  assert e.location()[2:]==(12,52);step('RIGHT');step('UP');assert e.location()[2:]==(13,51)
  boat('LEFT',21,0,'DewfordTown','BRINEY_AT_DEWFORD');scene(6,0,True,True)
  assert e.location()[2:]==(11,9)and len(ctx['object_rows'](e,5))==1;stage('03-new-native-boat-safe-landing')
  step('LEFT');assert e.location()[2:]==(10,9);stage('04-new-dock-walks-onto-land')
  wanted=dict(baseline);wanted['location']=[43,11,10,9]
  assert state()==wanted,'Dock-only roundtrip changed story, items or rewards'
  assert ctx['snapshot'](e)==before,'Dock-only roundtrip changed party/PC/dex/checked progress'
  assert ctx['blocks'](e).sb2[hvo:hvo+hvs]==seedfile.sb2[hvo:hvo+hvs]
  assert ctx['blocks'](e).sb2[hfo:hfo+hfs]==seedfile.sb2[hfo:hfo+hfs]
  assert not report['battles'],'Unexpected battle in the narrow dock-only route'
  live=ctx['snapshot'](e);story=state();report['native_SAVE_cold']=ctx['flash_reload'](e,'continuous-Dewford-dock-only')
  report['native_save_counter_runtime_type']=type(report['native_SAVE_cold']['counter']).__name__
  report['prior_failed_R5_retained']={'report_sha256':'665ba27317565cf0aded40e334b349457a3e3816fcdb602647926b42a5757798','counter_JSON_values':[74,75],'checksummed_sectors':14,'helper_native_save_return_type':'tuple','failure_not_overwritten':True}
  assert list(report['native_SAVE_cold']['counter'])==[74,75]and report['native_SAVE_cold']['checksummed_sectors']==14
  assert ctx['snapshot'](e)==live and state()==story;report['final_party_ledger']=ctx['preserve'](before);stage('05-native-SAVE-cold-no-teleport-loop')
  report['cases'].append({'case':'Unmodified-natural-SAVE74-native-legacy-and-new-dock-release-check','pass':True,'Brawly_progression_tested':False,'native_SAVE_cold':report['native_SAVE_cold']})
  report.update({'pass':True},status='complete',native_old_and_new_dock_escape_verified=True,PC_33744_bytes_preserved=True,entire_party_bytes_preserved=True,story_items_Hoenn_flags_vars_preserved=True,Brawly_completed=False,Brawly_progression_tested=False,full_Hoenn_campaign_tested=False,actual_device_fps_measured=False)
 except Exception as error:
  if report is None:report={'pass':False,'status':'failed','stages':[]};args.out.mkdir(parents=True,exist_ok=True)
  report.update({'pass':False},status='failed',error=repr(error),traceback=traceback.format_exc())
  if e is not None:
   try:
    report['failure_location']=list(e.location());report['failure_callback']=hex(e.callback2());e.shot(str(args.out/'failure.png'),scale=3)
    if 'tile' in locals():
     x,y=e.location()[2:];rows=[]
     for i in range(const('OBJECT_EVENTS_COUNT')):
      q=syms['gObjectEvents']+i*off('misty_obj');raw=e.read(q,off('misty_obj'));flags=struct.unpack_from('<I',raw)[0]
      if not(flags&1):continue
      xx,yy=struct.unpack_from('<hh',raw,16)
      rows.append(dict(slot=i,local=raw[8],xy=[xx-7,yy-7],flags=hex(flags),elevation=[raw[11]&15,raw[11]>>4],direction=raw[24]&15))
     report['live_failure_before_SAVE']=dict(field_idle=bool(e.field_idle()),objects=rows,tiles={str((xx,yy)):dict(tile=hex(tile(xx,yy)),behavior=hex(behavior(xx,yy)))for xx,yy in [(x,y),(x,y-1),(x+1,y)]})
    if e.in_overworld() and e.field_idle():report['failure_native_SAVE_cold']=ctx['flash_reload'](e,'failed-native-continuation')
   except Exception as diagnostic:report['diagnostic_error']=repr(diagnostic)
 finally:
  if e is not None:e.close()
  protected={**inputs,**ctx.get('protected',{})};unchanged=all(f.exists()and sha(f)==h for f,h in protected.items());report['protected_original_inputs_unchanged']=unchanged
  if not unchanged:report.update({'pass':False},status='failed',preservation_error='Protected input changed')
  (args.out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(pass_all=report['pass'],stages=len(report['stages']),error=report.get('error'))),flush=True)
 return 0 if report['pass']else 1
if __name__=='__main__':raise SystemExit(main())
