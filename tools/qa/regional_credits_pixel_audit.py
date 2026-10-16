"""Read-only native credits camera/monster pixels audit during one capture."""
import hashlib,json,struct
from pathlib import Path
from gamedata import const,map_info
from PIL import Image
sha=lambda b:hashlib.sha256(b).hexdigest()

class CreditsPixelAudit:
    def __init__(self,region,rom,syms,out,scenes=None):
        assert region in ('johto','hoenn')
        self.region=region;self.rb=Path(rom).read_bytes();self.S=syms
        self.out=Path(out);self.ages=[0]*13;self.cameras={};self.mons={}
        self.pending={};self.manual_visual_review_required=True
        if region=='johto':
            assert scenes and len(scenes)==13
            self.maps=[s['name'] for s in scenes]
            self.species=['TYPHLOSION','MEGANIUM','FERALIGATR','HO_OH']
        else:
            self.maps=['SlateportCity','Route101','LittlerootTown_ProfessorBirchsLab',
                'MauvilleCity','MtChimney','Route119_WeatherInstitute_2F',
                'SeafloorCavern_Room9','SkyPillar_Top','SootopolisCity',
                'EverGrandeCity','EverGrandeCity_ChampionsRoom',
                'EverGrandeCity_HallOfFame','SlateportCity']
            self.species=['BLAZIKEN','SCEPTILE','SWAMPERT','RAYQUAZA']
        title='Johto' if region=='johto' else 'Hoenn'
        self.ptrs={syms['s'+title+'CreditsScene%d'%i]:i for i in range(13)}
        assert len(self.ptrs)==13
        self.pairs=[(map_info(n)['group'],map_info(n)['num']) for n in self.maps]

    def romread(self,addr,n):
        p=addr-0x08000000
        assert 0<=p and p+n<=len(self.rb),'ROM data bounds'
        return self.rb[p:p+n]

    def pointer(self,addr):
        return struct.unpack('<I',self.romread(addr,4))[0]

    def unlz(self,addr):
        raw=self.romread(addr,min(0x20000,len(self.rb)-(addr-0x08000000)))
        assert raw[0]==16
        n=int.from_bytes(raw[1:4],'little');pos=4;d=bytearray()
        assert 0<n<=0x20000
        while len(d)<n:
            f=raw[pos];pos+=1
            for bit in range(7,-1,-1):
                if len(d)>=n:break
                if f&(1<<bit):
                    z=(raw[pos]<<8)|raw[pos+1];pos+=2
                    length=(z>>12)+3;dist=(z&4095)+1
                    assert dist<=len(d)
                    for _ in range(length):d.append(d[-dist])
                else:d.append(raw[pos]);pos+=1
        return bytes(d[:n])

    def picture(self,raw,name):
        assert len(raw)==240*160*3
        Image.frombytes('RGB',(240,160),raw).save(self.out/(name+'.png'))

    def check_mon(self,e,i):
        assert 0<=i<4
        w=e.read(self.S['gWindows'],12)
        assert tuple(w[:6])==(0,11,6,8,8,10),'unexpected regional mon window'
        base=struct.unpack_from('<H',w,6)[0]
        got=e.read(struct.unpack_from('<I',w,8)[0],2048)
        sp=const('SPECIES_'+self.species[i])
        expected=self.unlz(self.pointer(self.S['gMonFrontPicTable']+sp*8))[:2048]
        assert len(expected)==2048 and got==expected,'wrong species window graphics'
        reg=e.u16(0x04000008);charbase=((reg>>2)&3)*0x4000
        mapbase=((reg>>8)&31)*0x800
        assert e.read(0x06000000+charbase+base*32,2048)==expected,'mon VRAM differs'
        for y in range(8):
            row=struct.unpack('<8H',e.read(0x06000000+mapbase+((y+6)*32+11)*2,16))
            assert row==tuple(0xa000|base+y*8+x for x in range(8))
        pal=self.unlz(self.pointer(self.S['gMonPaletteTable']+sp*8))[:32]
        assert e.read(0x05000000+10*32,32)==pal,'mon palette differs'
        cols=struct.unpack('<16H',pal);pixels=e.screen();visible=matched=0
        for y in range(64):
            for x in range(64):
                v=expected[((y//8)*8+x//8)*32+(y%8)*4+(x%8)//2]
                c=(v>>(4*(x&1)))&15
                if not c:continue
                visible+=1;rgb=[((cols[c]>>s)&31)*255//31 for s in (0,5,10)]
                p=((y+48)*240+x+88)*3;got=pixels[p:p+3]
                if max(abs(got[k]-rgb[k]) for k in range(3))<=8:matched+=1
        assert visible>100 and matched/visible>.995,'native mon not visible'
        name='native-mon-%d-%s'%(i,self.species[i]);self.picture(pixels,name)
        self.mons[str(i)]={'species':self.species[i],'vram_sha256':sha(expected),
             'palette_sha256':sha(pal),'visible_pixels':visible,
             'screen_matching_pixels':matched,'frame':e.frame(),'file':name+'.png'}

    def feed(self,e,mgr):
        start=e.frame();main=e.u8(mgr);sub=e.u8(mgr+1)
        which=e.u8(mgr+9);timer=e.u16(mgr+12)
        assert e.u8(mgr+16)==(1 if self.region=='johto' else 2)
        active=e.u32(self.S['sCreditsOverworld_Script'])
        if active in self.ptrs and main in (6,7,8,9,20):
            i=self.ptrs[active]
            assert e.location()[:2]==self.pairs[i],('wrong region scene',i,e.location())
            self.ages[i]+=1
            if self.ages[i] in (80,480):
                tag='start' if self.ages[i]==80 else 'late'
                name='native-map-%02d-%s'%(i,tag)
                raw=e.screen();self.picture(raw,name)
                self.cameras.setdefault(str(i),{'map':self.maps[i],'shots':{}})
                self.cameras[str(i)]['shots'][tag]={'file':name+'.png',
                    'frame':e.frame(),'location':e.location(),'sha256':sha(raw)}
            if self.ages[i]>=80 and self.ages[i]%120==0:
                self.pending[i]=(e.frame(),e.screen())
        if main==14 and sub==8 and timer<=110 and str(which) not in self.mons:
            self.check_mon(e,which)
        assert e.frame()==start,'pixel audit advanced the emulator'

    def finish(self):
        for i in range(13):
            assert str(i) in self.cameras,('scene never visible',i,self.maps[i])
            if 'late' not in self.cameras[str(i)]['shots']:
                assert i in self.pending,('scene too brief',i,self.ages[i])
                fr,raw=self.pending[i];name='native-map-%02d-late'%i
                self.picture(raw,name)
                self.cameras[str(i)]['shots']['late']={
                    'file':name+'.png','frame':fr,'sha256':sha(raw)}
        assert len(self.mons)==4,'not all regional species were rendered'
        report={'pass':True,'region':self.region,'cameras':self.cameras,
                'pokemon':self.mons,'native_device_fps_measured':False,
                'manual_visual_review_required':True,
                'scripted_story_beats_completion_proven':False,
                'runtime_ram_pokes_by_pixel_audit':0}
        (self.out/'native-pixel-audit.json').write_text(json.dumps(report,indent=2)+'\n')
        return {'pass':True,'cameras':13,'pokemon':4,
                'manual_visual_review_required':True,
                'scripted_story_beats_completion_proven':False}
