from pathlib import Path
import json,hashlib,shutil,zipfile,datetime
r=Path('/workspaces/pokefirered');o=r/'work/save-edit-v125-20261013';m=json.loads((o/'edit-manifest.json').read_text());n=json.loads((o/'native/validation.json').read_text());a=json.loads((o/'independent-raw-audit.json').read_text())
assert n['pass'] and a['pass'] and m['candidate_sha256']==n['candidate_sha256']=='158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5'
assert hashlib.sha256((r/'pokemonthyl.gba').read_bytes()).hexdigest()==n['rom_sha256']
assert hashlib.sha256((r/'saves/pokemonthyl_v1.25.sav').read_bytes()).hexdigest()==m['input_sha256']
dst=r/'saves/pokemonthyl_v1.25-items99-iv2x.sav';shutil.copyfile(Path(m['candidate']),dst)
m.update(native_verified=True,independent_raw_verified=True,independent_stats_verified=True,installed_edited_copy=str(dst),original_preserved=True)
(o/'edit-manifest.json').write_text(json.dumps(m,indent=2))
delivery=r/'outputs/save-v125-items99-iv2x-20261013';delivery.mkdir(exist_ok=True)
shutil.copyfile(dst,delivery/'pokemonthyl_v1.25.sav')
readme='''Thunder Yellow  1.25  
99, 99.
  /// (HP/////)   ,  31.
       .
//////  / /PC//  .
 ROM f31b2eea  Continue,   ,    .  Bad Egg .
   BOX2 22       .

DELTA   Save File(  )  pokemonthyl_v1.25.sav .
 Save State     /   ,  SAV  Continue    .
  Save State .
 work/save-edit-v125-20261013/pokemonthyl_v1.25-original.sav   .
SHA256: 53d923bf4668373724b19c9d3c8526b002701606ab7ac082d657ee990e23d7b3
SHA256: 158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5
'''
(delivery/'README.txt').write_text(readme,encoding='utf-8')
for filename in ['edit-manifest.json','independent-raw-audit.json']:shutil.copyfile(o/filename,delivery/filename)
shutil.copyfile(o/'native/validation.json',delivery/'native-validation.json')
private=r/'work/regression-oct12/deliverables';private.mkdir(exist_ok=True);z=private/'pokemonthyl-v1.25-items99-iv2x-20261013.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in delivery.iterdir():f.write(p,p.name)
with zipfile.ZipFile(z) as f:
 assert f.read('pokemonthyl_v1.25.sav')==dst.read_bytes() and f.testzip() is None
shutil.copyfile(z,delivery/z.name)
status=r/'work/animation-recreation-status.json';old=status.read_bytes();(o/'status-before-edit.json').write_bytes(old);j=json.loads(old)
j['save_edit_20261013']={'status':'INSTALLED_SEPARATE_EDITED_COPY_NATIVE_SAVE_COLD_VERIFIED','input':m['input'],'input_sha256':m['input_sha256'],'edited_save':str(dst),'edited_sha256':m['candidate_sha256'],'backup':m['backup'],'items99':True,'owned_species':['BLASTOISE','CHARIZARD','VENUSAUR','DRAGONAIR'],'iv_rule':'individual IV min(31,old*2)','rom_unchanged':True,'rom_sha256':n['rom_sha256'],'native_menu_save_cold_verified':True,'original_and_existing_bad_egg_preserved':True,'proof':str(o)}
j['save_current']['latest_user_sav_v125_original_sha256']=m['input_sha256'];j['save_current']['latest_edited_save']=str(dst);j['save_current']['latest_edited_save_sha256']=m['candidate_sha256']
j['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
status.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
receipt={'installed_copy':str(dst),'delivery':str(delivery),'zip':str(z),'zip_bytes':z.stat().st_size,'zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'original_input_unchanged':True,'rom_unchanged':True,'native_pass':True}
(o/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
