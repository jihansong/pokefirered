#!/usr/bin/env python3
"""Prepare a distinct Johto native credits review profile using existing maps.

This profile is a review draft: it does not add a Johto League/HOF, a clear
flag, an automatic playback trigger, missing story locations or new artwork.
Existing Kanto/Hoenn scripts, original music/staff/closing cards and Save ABI
are kept. Apply only after the supplied 13 scenes match live map metadata.
"""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
sha=lambda b:hashlib.sha256(b).hexdigest()
CREDITS_SHA='3d2505328dbe43f4d15c9a63ac4868f07981b48feca2b18560835d5ce39f0a18'
HEADER_SHA='bcde46054969d89e44053de52b88e8ef3f2fa6f694d2edca63239af0677b36ca'
MARK='THYL_JOHTO_CREDITS_REVIEW_V1'

def once(s,old,new):
    assert s.count(old)==1,('unexpected source anchor',old)
    return s.replace(old,new,1)

def validate_scenes(root,scenes):
    assert len(scenes)==13,'native staff script requires exactly 13 scene slots'
    assert len({s['name'] for s in scenes})==13,'distinct regional maps required'
    layouts=json.loads((root/'data/layouts/layouts.json').read_text())['layouts']
    for s in scenes:
        p=root/'data/maps'/s['name']/'map.json'
        m=json.loads(p.read_text())
        rows=[x for x in layouts if x.get('id')==m['layout']]
        assert len(rows)==1,('layout must be unique',s['name'])
        l=rows[0]
        assert m['id']==s['map'],('map constant mismatch',s['name'])
        assert [l['width'],l['height']]==s['size'],('geometry changed',s['name'])
        x,y=s['start'];dx,dy,frames=s['scroll']
        assert 0<=x<l['width'] and 0<=y<l['height']
        assert -127<=dx<=127 and -127<=dy<=127 and 1<=frames<=255
        # Restrict drafts to slow native pans and avoid inventing unsupported cameras.
        assert abs(dx)<=1 and abs(dy)<=1
        assert 0<=x*16+dx*frames<l['width']*16
        assert 0<=y*16+dy*frames<l['height']*16
        s['map_sha256']=sha(p.read_bytes())
    return scenes

def patch(c,h,scenes):
    assert sha(c.encode())==CREDITS_SHA,'credits preimage changed; review it first'
    assert sha(h.encode())==HEADER_SHA,'credits header preimage changed'
    assert MARK not in c and 'DoJohtoCredits' not in h
    protected={}
    for name in ['sCreditsScript','sOverworldMapScenes','sHoennOverworldMapScenes',
                 'sCreditsTexts']:
        block=re.search(r'\b'+name+r'\[\]\s*=\s*\{.*?\n\};',c,re.S)
        assert block,name;protected[name]=block.group()
    resources=re.search(r'struct CreditsResources\s*\{.*?\n\};',c,re.S).group()
    enum='''enum CreditsRegion
{
    CREDITS_REGION_KANTO = 0,
    CREDITS_REGION_JOHTO = 1,
    CREDITS_REGION_HOENN = 2
};

'''
    c=once(c,'enum CreditsSceneIdx\n',enum+'enum CreditsSceneIdx\n')
    arrays='\n/* '+MARK+': existing maps only; no automatic clear trigger. */\n'
    for i,s in enumerate(scenes):
        x,y=s['start'];dx,dy,frames=s['scroll']
        arrays+=('static const struct CreditsOverworldCmd sJohtoCreditsScene%d[] = {\n'
                 '    CREDITSOVWLDLOADMAP(%s, %d, %d, 1),\n'
                 '    CREDITSOVWLDSCROLL(%d, %d, %d),\n'
                 '    CREDITSOVWLDEND,\n};\n')%(i,s['map'],x,y,dx,dy,frames)
    arrays+='static const struct CreditsOverworldCmd *const sJohtoOverworldMapScenes[] = {\n'
    arrays+=''.join('    sJohtoCreditsScene%d,\n'%i for i in range(13))
    arrays+='};\n'
    arrays+='static const u8 sJohtoCreditsTitle[] = _("POK\u00e9MON THUNDER YELLOW\\nJOHTO STAFF");'+'\n'
    c=once(c,'static const struct CreditsTextHeader sCreditsTexts[] = {',
           arrays+'\nstatic const struct CreditsTextHeader sCreditsTexts[] = {')
    helper='''static const struct CreditsOverworldCmd *const *GetRegionalCreditsMapScenes(void)
{
    switch (sCreditsMgr->filler_10[0])
    {
    case CREDITS_REGION_JOHTO:
        return sJohtoOverworldMapScenes;
    case CREDITS_REGION_HOENN:
        return sHoennOverworldMapScenes;
    default:
        return sOverworldMapScenes;
    }
}

static const u8 *GetRegionalCreditsTitle(void)
{
    switch (sCreditsMgr->filler_10[0])
    {
    case CREDITS_REGION_JOHTO:
        return sJohtoCreditsTitle;
    case CREDITS_REGION_HOENN:
        return sHoennCreditsTitle;
    default:
        return TITLE_TEXT;
    }
}

'''
    c=once(c,'static void StartRegionalCredits(u8 region)\n',
           helper+'static void StartRegionalCredits(u8 region)\n')
    c=once(c,'    if (region == 2)\n','    if (region != CREDITS_REGION_KANTO)\n')
    c=once(c,'    StartRegionalCredits(0);','    StartRegionalCredits(CREDITS_REGION_KANTO);')
    c=once(c,'    StartRegionalCredits(2);','    StartRegionalCredits(CREDITS_REGION_HOENN);')
    after='''void DoJohtoCredits(void)
{
    StartRegionalCredits(CREDITS_REGION_JOHTO);
}

'''
    c=once(c,'void DoHoennCredits(void)\n',after+'void DoHoennCredits(void)\n')
    c=once(c,'(sCreditsMgr->filler_10[0] == 2 ? sHoennOverworldMapScenes : sOverworldMapScenes)',
           'GetRegionalCreditsMapScenes()')
    c=once(c,'sCreditsMgr->filler_10[0] == 2 ? sHoennCreditsTitle : TITLE_TEXT',
           'GetRegionalCreditsTitle()')
    c=once(c,'    if (sCreditsMgr->filler_10[0] == 2)\n    {\n        InitWindows',
           '    if (sCreditsMgr->filler_10[0] != CREDITS_REGION_KANTO)\n    {\n        InitWindows')
    johto='''    if (sCreditsMgr->filler_10[0] == CREDITS_REGION_JOHTO)
    {
        static const u16 species[] = {SPECIES_TYPHLOSION, SPECIES_MEGANIUM, SPECIES_FERALIGATR, SPECIES_HO_OH};
        return whichMon < ARRAY_COUNT(species) ? species[whichMon] : SPECIES_NONE;
    }
'''
    c=once(c,'    if (sCreditsMgr->filler_10[0] == 2)\n    {\n        static const u16 species[]',
           johto+'    if (sCreditsMgr->filler_10[0] == CREDITS_REGION_HOENN)\n    {\n        static const u16 species[]')
    c=once(c,'if (sCreditsMgr->filler_10[0] != 2)',
           'if (sCreditsMgr->filler_10[0] == CREDITS_REGION_KANTO)')
    h=once(h,'void DoHoennCredits(void);','void DoHoennCredits(void);\nvoid DoJohtoCredits(void);')
    assert resources in c,'credits heap object layout changed'
    assert all(v in c for v in protected.values()),'original scripts/tables changed'
    assert c.count('PlayBGM(MUS_CREDITS);')==1
    assert 'CREDITS_THEENDGFX(ALLRIGHTSRESERVED' in c and 'CREDITS_THEENDGFX(THEEND' in c
    return c,h

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scenes',type=Path,required=True)
    p.add_argument('--apply',action='store_true')
    a=p.parse_args();r=Path.cwd()
    scenes=validate_scenes(r,json.loads(a.scenes.read_text(encoding='utf-8')))
    paths=['src/credits.c','include/credits.h']
    before={n:(r/n).read_bytes() for n in paths}
    c,h=patch(before[paths[0]].decode(),before[paths[1]].decode(),scenes)
    after=dict(zip(paths,[c.encode(),h.encode()]))
    protected_saves={str(x):sha(x.read_bytes()) for x in (r/'saves').rglob('*.sav')}
    report={'applied':a.apply,'region':'johto','profile_stage':'native review draft',
            'automatic_regional_clear_trigger':False,'league_hof_implemented':False,
            'film_captured':False,'visual_review_required':True,'new_music':False,
            'original_music':'MUS_CREDITS','new_artwork':False,
            'credits_object_layout_changed':False,'save_layout_changed':False,
            'original_staff_map_tables_preserved':True,
            'scene_slots':scenes,'manual_entrypoint':'DoJohtoCredits',
            'missing_required_story_beats':['Ruins of Alph','Bell Tower',
                'Whirl Islands','Dragon Den','Johto League and Hall of Fame'],
            'files':{n:{'before':sha(before[n]),'after':sha(after[n])} for n in paths}}
    if a.apply:
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup=r/'work/backups'/('johto-credits-review-'+stamp)
        for n in paths:assert (r/n).read_bytes()==before[n],'concurrent edit'
        for n in paths:
            q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[n])
        for n in paths:(r/n).write_bytes(after[n])
        report['backup']=str(backup.relative_to(r))
    assert all(sha(Path(x).read_bytes())==v for x,v in protected_saves.items())
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
