from pathlib import Path
q=Path('work/followup-20261013/doors-dex.py').read_text()
old="entries=e.u16(p+72);assert 0<entries<=count+1"
new="""entries=e.u16(p+72);assert 0<entries<=count+1
 states=blocks(e)
 if region==0:national_order=list(range(1,152))
 elif region==1:national_order=list(struct.unpack('<251H',e.read(syms['sJohtoToNationalOrder'],502)))
 else:national_order=list(struct.unpack('<202H',e.read(syms['sHoennToNationalOrder'],404)))
 expected_rows=max([i for i,n in enumerate(national_order,1) if all(states.dex_state(n)[1:])] or [0])
 assert entries==expected_rows,('native row count differs from last seen regional number',label,entries,expected_rows)
 lp=e.u32(p+68);assert 0x02000000<=lp and lp+entries*8<=0x02040000
 decoded=[]
 for i,n in enumerate(national_order[:entries]):
  packed=e.u32(lp+i*8+4);species=packed&65535
  assert 0<species<const('NUM_SPECIES'),(label,i,species)
  national=e.u16(syms['sSpeciesToNationalPokedexNum']+2*(species-1))
  owned,seen,seen1,seen2=states.dex_state(n)
  assert national==n and packed>>16==int(all((seen,seen1,seen2)))+2*int(owned),(label,i,packed,n,national)
  decoded.append(national)
 assert decoded==national_order[:entries]
 report.setdefault('native_list_order_checks',[]).append({'label':label,'count':count,'rows':entries,'expected_last_seen':expected_rows,'exact_regional_species_order':True,'seen_caught_bits_match':True,'trailing_unseen_trim_is_existing_UX':True})"""
assert q.count(old)==1
q=q.replace(old,new).replace("out=root/'work/followup-20261013/doors-dex'","out=root/'work/followup-20261013/dex-list-order'")
exec(compile(q,'<native-readonly-list-order-addendum>','exec'))
