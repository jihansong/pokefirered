"""Episode-one opening study, composed from existing FR/LG graphics.

No character or environment pixels are drawn by this renderer. Geometry is used
only to position native sprites, move the camera, and change palette colours.
This is a visual prototype, not a ROM capture or a validated GBA implementation.
Strike expressions use manually edited user-reference vector cels; they are not new original poses.
"""
from pathlib import Path
from functools import lru_cache
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'native-opening' / 'vendor'))
import official_gfx as gfx

ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, default=HERE.parent / 'pokefirered')
ap.add_argument('--output', type=Path, default=HERE.parents[1] / 'outputs/opening-hooh-color-v5')
ap.add_argument('--stills-only', action='store_true')
args = ap.parse_args()
gfx.ROOT = str(args.repo.resolve())
OUT = args.output.resolve()
OUT.mkdir(parents=True, exist_ok=True)
NEAREST = Image.Resampling.NEAREST
W, H, FPS, COUNT = 240, 160, 60, 600
PIKACHU_SCALE = 1.5
MEETING_VISIBLE_HEIGHT = 38
MEETING_FOOT_ANCHOR = (183, 83)
sources = set()

def source(path):
    sources.add(path)
    return path

@lru_cache(maxsize=1024)
def spr(path, frame=0, w=64, h=64, flip=False, scale=1):
    im = gfx.sprite(source(path), frame, w, h)
    if flip:
        im = ImageOps.mirror(im)
    if scale != 1:
        im = im.resize((round(im.width*scale), round(im.height*scale)), NEAREST)
    return im

@lru_cache(maxsize=256)
def recolour(path, frame, w, h, mode):
    im = spr(path, frame, w, h).copy()
    pixels = []
    for r,g,b,a in im.getdata():
        if mode == 'gold':
            v = (r+g+b)//3
            rgb = (255,248,176) if v > 180 else (248,208,64) if v > 90 else (176,112,32)
        elif mode == 'electric':
            v = max(r,g,b)
            rgb = (255,255,224) if min(r,g,b)>170 else (255,232,64) if v>155 else (168,120,24)
        elif mode == 'silhouette':
            rgb = (35,43,58)
        pixels.append((*rgb,a))
    im.putdata(pixels)
    return im

@lru_cache(maxsize=32)
def bg(path, width=32):
    pal = path+'.pal' if Path(gfx.path(path+'.pal')).exists() else path+'.png'
    source(pal)
    return gfx.render_map(source(path+'.png'),source(path+'.bin'),gfx.read_pal(pal),width=width)

def put(dst, image, x, y):
    dst.alpha_composite(image, (round(x), round(y)))

def pika_geometry(image, x, y, airborne=False):
    # Scale around the visible feet, or the centre during the leap. Back-view
    # shots retain their bottom-of-screen framing without cutting off the ears.
    left,top,right,bottom=image.getbbox()
    ax=(left+right)/2
    ay=(top+bottom)/2 if airborne else min(bottom,96-y)
    return x+ax*(1-PIKACHU_SCALE), y+ay*(1-PIKACHU_SCALE)

def put_pikachu(dst, image, x, y, airborne=False):
    px,py=pika_geometry(image,x,y,airborne)
    enlarged=image.resize((round(image.width*PIKACHU_SCALE),round(image.height*PIKACHU_SCALE)),NEAREST)
    put(dst,enlarged,px,py)
    return px,py

def pika_electricity(im,px,py,local_x,local_y,t):
    # Keep the centre of each attached spark aligned with the enlarged sprite.
    electricity(im,px+(local_x+16)*PIKACHU_SCALE-16,
                py+(local_y+16)*PIKACHU_SCALE-16,t)

def wash(im, rgb, alpha):
    if not alpha:
        return im
    return Image.blend(im, Image.new('RGBA', im.size, (*rgb,255)), max(0,min(1,alpha)))

def tint_sprite(im, amount):
    if not amount: return im
    a=im.getchannel('A')
    out=wash(im,(20,30,58),amount)
    out.putalpha(a)
    return out

def forest(scroll=0, dark=0):
    # Scene 3's authored 256x96 viewport: canopy, trunks, shrubs and ground.
    layer=bg('graphics/intro/scene_3/bg').crop((0,32,256,128))
    im=Image.new('RGBA',(240,96),(27,48,47,255))
    x=-round(scroll)%256-256
    put(im,layer,x,0);put(im,layer,x+256,0)
    return wash(im,(16,25,51),dark)

def grass(im, t, dark=0, speed=2.6, y=61):
    tile=spr('graphics/intro/scene_3/grass.png',int(t//9)%2,64,32)
    tile=tint_sprite(tile,dark)
    off=round(t*speed)%112
    for x in range(-112,353,112):
        put(im,tile,x-off,y)

RED='graphics/trainers/back_pics/red_back_pic.png'
RUN='graphics/credits/player_male.png'
PIKA='graphics/pokemon/pikachu/front.png'
PIKAB='graphics/pokemon/pikachu/back.png'
PIKAF='graphics/object_events/pics/pokemon/pikachu.png'
BIRD='graphics/object_events/pics/pokemon/spearow.png'
HO='graphics/object_events/pics/pokemon/ho_oh.png'
HO_PAL='graphics/object_events/palettes/npc_blue.pal'
@lru_cache(maxsize=2)
def hooh_field(frame):
    return gfx.sprite(source(HO), frame, 32, 32, source(HO_PAL))

ELEC='graphics/battle_anims/sprites/electricity.png'
BOLT='graphics/battle_anims/sprites/lightning_2.png'

def electricity(im,x,y,t,scale=1):
    a=recolour(ELEC,int(t//3)%4,32,32,'electric')
    if scale!=1:a=a.resize((round(32*scale),round(32*scale)),NEAREST)
    put(im,a,x,y)

def rain(im,t,count=17,opacity=.68):
    # Each drop is the shipped weather tile, travelling diagonally at two depths.
    for i in range(count):
        x=(i*47-int(t*(1.5+(i%3)*.4)))%280-20
        y=(i*31+int(t*(4+(i%3))))%132-32
        a=spr('graphics/weather/rain.png',0 if i%3 else 1,16,32).copy()
        a.putalpha(a.getchannel('A').point(lambda v:round(v*opacity)))
        put(im,a,x,y)

def flock(im,t,count=7,near=False):
    for i in range(count):
        x=18+i*28 + math.sin(t*.045+i)*7
        y=9+(i%3)*9+math.sin(t*.11+i*1.5)*3
        # The two open-wing frames alternate around the folded-wing frame.
        frame=[0,1,2,1][int(t//5+i)%4]
        a=spr(BIRD,frame,16,16,flip=bool(i%2))
        a=tint_sprite(a,.23 if near else .38)
        put(im,a,x,y)

def shot_tunnel(t):
    # The native intro's three authored zoom states, with a brief matching palette fade.
    idx=min(2,t//8)
    base=bg('graphics/intro/scene_1/bg').crop((0,idx*128,240,idx*128+96))
    front=bg('graphics/intro/scene_1/grass').crop((0,idx*128,240,idx*128+96))
    im=Image.new('RGBA',(240,96),(43,62,86,255));put(im,base,0,0);put(im,front,0,0)
    return wash(im,(0,0,0),max(0,(7-t)/8))

def shot_meeting(t):
    im=forest(t*.18)
    red_frame=0 if t<23 else 1 if t<36 else 2 if t<43 else 3 if t<51 else 4 if t<66 else 0
    put(im,spr(RED,red_frame),20,39)
    hop=round(6*math.sin(math.pi*(t-49)/18)) if 49<=t<67 else 0
    # Size correction only. The existing front sprite remains a placeholder;
    # opening-specific facial expressions and action cels are NOT yet available.
    original=spr(PIKA)
    left,top,right,bottom=original.getbbox()
    meeting_scale=MEETING_VISIBLE_HEIGHT/(bottom-top)
    size=round(original.width*meeting_scale)
    pika=original.resize((size,size),NEAREST)
    left,top,right,bottom=pika.getbbox()
    px=MEETING_FOOT_ANCHOR[0]-(left+right)/2
    py=MEETING_FOOT_ANCHOR[1]-bottom-hop
    put(im,pika,px,py)
    # Ball leaves the hand, then is rejected. The character itself is unmodified.
    if 44<=t<63:
        u=(t-44)/19;x=79+u*91;y=53-27*math.sin(math.pi*u)
        put(im,spr('graphics/interface/ball/poke.png',int(t//3)%2,16,16),x,y)
    elif 63<=t<82:
        u=(t-63)/19
        put(im,spr('graphics/interface/ball/poke.png',int(t//3)%2,16,16),167-u*108,52-u*69)
    if 60<=t<79:
        # Keep the inherited effects beside the resized cheeks. Spark cels scale
        # with this shot alone and never use the global 1.5x chase/strike scale.
        factor=size/original.width
        for local_x,local_y,phase in [(2,5,0),(28,17,6)]:
            effect=recolour(ELEC,int((t+phase)//3)%4,32,32,'electric')
            effect=effect.resize((round(32*factor),round(32*factor)),NEAREST)
            put(im,effect,px+local_x*factor,py+local_y*factor)
    grass(im,t*.15,y=63)
    return im

def shot_chase(t):
    im=forest(t*2.05,.37)
    flock(im,t)
    # Native six-frame credits run, mirrored as a whole to maintain travel direction.
    ri=int(t//6)%6
    put(im,tint_sprite(spr(RUN,ri,flip=True),.13),108+round(math.sin(t*.04)*5),23)
    pf=[2,7,2,8][int(t//5)%4]
    put_pikachu(im,tint_sprite(spr(PIKAF,pf,16,16,flip=True),.10),92,76-(int(t//5)%2))
    # A close bird uses the same authored flap cycle at double pixel scale.
    for phase in (0,78):
        u=t-phase
        if 0<=u<54:
            x=-37+u*5.7;y=39+math.sin(u/54*math.pi)*17
            put(im,tint_sprite(spr(BIRD,[0,1,2,1][int(u//4)%4],16,16,scale=2),.20),x,y)
    rain(im,t)
    grass(im,t,.34,3.7,65)
    return im

def shot_protect(t):
    im=forest(90+t*.2,.46)
    # Reverse angle: Red's open arm divides the incoming flock and Pikachu.
    # This is an existing throw pose; a purpose-drawn shielding pose is still needed.
    put_pikachu(im,tint_sprite(spr(PIKAB,scale=.75),.13),155,52)
    put(im,tint_sprite(spr(RED,3 if t>10 else 2,flip=True,scale=1.25),.13),74,28)
    for i in range(5):
        x=-12+i*19+min(13,t*.26); y=15+(i%3)*15
        put(im,tint_sprite(spr(BIRD,[0,1,2,1][int(t//4+i)%4],16,16),.18),x,y)
    rain(im,t+156,14,.60)
    grass(im,t,.4,.6,66)
    return im

def shot_strike(t):
    im=forest(104+t*.6,.57)
    if t<27:
        # A compressed anticipation, then an upward leap into the clearing.
        y=50-39*math.sin(min(1,t/27)*math.pi/2)
    elif t<90:
        y=11+round(math.sin((t-27)*.15)*2)
    else:
        y=11+(t-90)*1.7
    if 47<=t<78:
        power=min(1,(t-46)/4)
        im=wash(im,(246,232,132),.20*power)
        for x,k in [(45,0),(181,11)]:
            bolt=recolour(BOLT,[0,2,1,2][int((t+k)//4)%4],32,32,'electric')
            put(im,bolt,x,-2);put(im,bolt,x,30)
        for i in range(6):
            ang=(i*math.pi/3)+(t-47)*.055
            rad=32+(t-47)*.35
            electricity(im,120+math.cos(ang)*rad-16,51+math.sin(ang)*rad*.62-16,t+i*3)
    for i,(bx,by) in enumerate([(39,30),(184,24),(12,6),(211,5)]):
        if t<47:
            dx=(t*.45)*(1 if bx<120 else -1);dy=0
        else:
            elapsed=t-46
            dx=46*.45*(1 if bx<120 else -1)+elapsed*(-2.4 if bx<120 else 2.4)
            dy=elapsed*1.2
        put(im,tint_sprite(spr(BIRD,[0,1,2,1][int(t//4+i)%4],16,16,scale=1 if i>1 else 2),.15),bx+dx,by+dy)
    grass(im,t,.36,.3,67)
    # Dedicated expression edits derived from the supplied anime crouch reference.
    # The inherited meeting/Red/background shots remain byte-identical.
    state='01-braced' if t<15 or t>=94 else '02-charge' if t<47 or t>=78 else '03-release'
    cel=Image.open(HERE.parents[1]/'outputs/pikachu-expression-edit-v1'/(state+'.png')).convert('RGBA')
    height=52 if t<10 else round(52+(min(t,28)-10)*1.6) if t<28 else 81
    cel=cel.resize((round(80*height/88),height),NEAREST)
    center_x=121
    foot=86 if t<10 else 86-min(17,(t-10)*.94) if t<28 else 87
    if t>=94:foot=87+(t-94)*1.7
    left=center_x-cel.width//2;top=round(foot-cel.height)
    put(im,cel,left,top)
    # Use the actual face position; effects stay outside the eye/mouth region.
    px,py=left,top

    if 15<=t<98:
        if 47<=t<78:
            electricity(im,left-16,top+round(cel.height*.76),t)
            electricity(im,left+cel.width-14,top+round(cel.height*.69),t+5)
        else:
            electricity(im,left-8,top+round(cel.height*.76)+8,t,scale=.5)
            electricity(im,left+cel.width-6,top+round(cel.height*.69)+8,t+5,scale=.5)
    if t<38:rain(im,t+220,8,.45)
    # One short impact accent. No repeated full-screen strobing.
    if 47<=t<50:im=wash(im,(255,255,239),.55)
    if t>110:im=wash(im,(250,249,217),(t-110)/16)
    return im

def shot_sky(t):
    im=Image.new('RGBA',(240,96),(116,188,226,255))
    # Discrete palette bands are a GBA-compatible colour effect, not painted scenery.
    px=im.load()
    for y in range(96):
        band=y//16
        colour=(116+band*7,188+band*5,226+band*3,255)
        for x in range(240):px[x,y]=colour
    cloud=spr('graphics/weather/cloud.png',0,64,64)
    for x,y,speed in [(-38,14,.15),(8,-22,.12),(166,-16,.16),(213,29,.24)]:
        put(im,cloud,x-t*speed,y)
    # Head-on native Ho-oh art approaches on the depth axis, never slides sideways.
    bird=hooh_field(int(t//9)%2)
    z=max(0.0,min(1.0,(t-45)/18))
    z=z*z*(3-2*z)
    size=32+round(8*z)
    bird=bird.resize((size,size),NEAREST)
    put(im,bird,122-bird.width//2,9-round(t*.055))
    put(im,spr(RED),39,59)
    put_pikachu(im,spr(PIKAB,scale=.75),134,66)
    # Keep the same foreground grass as the forest, recoloured by morning light.
    grass(im,0,.05,0,71)
    if t<12:im=wash(im,(250,249,217),(12-t)/12)
    if t>116:im=wash(im,(0,0,0),(t-116)/15)
    return im

SHOTS=[
    (0,24,'forest','숲으로 들어가는 도입',shot_tunnel),
    (24,120,'meeting','볼을 거부하는 피카츄',shot_meeting),
    (120,276,'chase','폭우 속 깨비참의 추격',shot_chase),
    (276,342,'protect','앞을 막아서는 레드',shot_protect),
    (342,468,'strike','피카츄의 도약과 방전',shot_strike),
    (468,600,'sky','비가 그친 하늘과 칠색조',shot_sky),
]

def render(n):
    for start,end,key,label,fn in SHOTS:
        if start<=n<end:
            viewport=fn(n-start)
            image=Image.new('RGB',(W,H),(0,0,0))
            image.paste(viewport.convert('RGB'),(0,32))
            return image
    raise ValueError(n)

KEYS=[(18,'01-forest'),(67,'02-meeting'),(93,'03-rejection'),(184,'04-chase'),
      (312,'05-protection'),(375,'06-leap'),(415,'07-thunderbolt'),(534,'08-clear-sky')]
keydir=OUT/'keyframes';keydir.mkdir(exist_ok=True)
for n,name in KEYS:
    im=render(n)
    im.save(keydir/(name+'-native.png'))
    im.resize((960,640),NEAREST).save(keydir/(name+'.png'))

def font(size):
    for p in ['C:/Windows/Fonts/malgun.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()

sheet=Image.new('RGB',(1024,1580),(17,24,35));d=ImageDraw.Draw(sheet)
d.text((24,18),'THUNDER YELLOW  /  HO-OH ORIGINAL COLOUR STUDY 05',font=font(27),fill='#f8dc69')
d.text((24,61),'방전 표정 3컷 수정 — 제공된 참고 작화 기반 / 전체 원화 완성 아님',font=font(18),fill='#c2cad9')
for i,(n,name) in enumerate(KEYS):
    x=24+(i%2)*500;y=110+(i//2)*360
    frame=render(n).resize((480,320),NEAREST);sheet.paste(frame,(x,y))
    label=next(s[3] for s in SHOTS if s[0]<=n<s[1])
    d.text((x,y+325),f'{i+1:02d}  {n/60:04.2f}s  {label}',font=font(18),fill='#e1e7ee')
sheet.save(OUT/'keyframes-contact-sheet.png')

# Existing repo captures are for a local comparative review; no user reference film is copied.
comparisons=[('0970-s3-standoff.png',67,'같은 원본 숲 / 다른 인물 배치'),
             ('1150-s3-recoil.png',184,'원본 숲의 픽셀 밀도 / 추격 구도'),
             ('1255-s3-attack-start.png',415,'원본 액션 / 방전 시안')]
comp=Image.new('RGB',(1024,1130),(17,24,35));cd=ImageDraw.Draw(comp)
cd.text((24,14),'FR/LG 원본 컷                                  새 오프닝 시안',font=font(24),fill='#f4d771')
for i,(name,n,label) in enumerate(comparisons):
    p=args.repo/'docs/anim/shots/intro-original'/name
    if p.exists():
        original=Image.open(p).convert('RGB')
        original.resize((480,320),NEAREST).save(HERE/f'comparison-source-{i}.png')
        comp.paste(original.resize((480,320),NEAREST),(24,60+i*354))
    comp.paste(render(n).resize((480,320),NEAREST),(524,60+i*354))
    cd.text((24,385+i*354),label,font=font(17),fill='#c2cad9')
comp.save(OUT/'original-comparison.png')

if not args.stills_only:
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg:
        import imageio_ffmpeg
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    raw=OUT/'opening-10s-native.mp4'
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24',
         '-video_size','240x160','-framerate','60','-i','pipe:0','-an','-c:v','libx264',
         '-preset','medium','-crf','10','-pix_fmt','yuv420p','-movflags','+faststart',str(raw)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    digests=[];previous=None;unchanged=[]
    with zipfile.ZipFile(OUT/'opening-native-600-frames.zip','w',zipfile.ZIP_DEFLATED) as z:
        import io
        for n in range(COUNT):
            im=render(n); data=im.tobytes();proc.stdin.write(data)
            digest=hashlib.sha256(data).hexdigest();digests.append(digest)
            if digest==previous:unchanged.append(n)
            previous=digest
            buf=io.BytesIO();im.save(buf,format='PNG');z.writestr(f'frames/{n:04d}.png',buf.getvalue())
            if n%120==0:print(f'Rendered {n}/{COUNT}',flush=True)
    proc.stdin.close();err=proc.stderr.read().decode();rc=proc.wait()
    if rc:raise RuntimeError(err)
    for name,start,duration in [('opening-10s-preview.mp4',0,10),('chase-motion-sample.mp4',2,2.6)]:
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-ss',str(start),'-i',str(raw),
                        '-t',str(duration),'-vf','scale=960:640:flags=neighbor','-an','-c:v','libx264',
                        '-preset','medium','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/name)],check=True)
    audit={'frames':COUNT,'fps':FPS,'duration_seconds':10,'size':[240,160],
           'pikachu_scale_other_scenes_relative_to_initial_preview':PIKACHU_SCALE,
           'preview_label':'방전 표정 3컷 수정 — 참고 원화의 수동 편집',
           'meeting_visible_height_px':MEETING_VISIBLE_HEIGHT,
           'meeting_foot_anchor_viewport_px':MEETING_FOOT_ANCHOR,
           'opening_specific_character_art_included':'three derivative expression edits in strike only',
           'new_original_poses':False,
           'viewport':[0,32,240,96],'distinct_frames':len(set(digests)),
           'identical_adjacent_frames':unchanged,'audio':'none / visual study',
           'rom_integrated':False,'gba_palette_vram_oam_budget_validated':False,
           'keyframes':[{'frame':n,'name':name} for n,name in KEYS]}
    (OUT/'validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')

manifest={'version':'opening-hooh-color-v5','source_repo':'jihansong/pokefirered',
          'preview_label':'방전 표정 3컷 수정 — 참고 원화의 수동 편집',
          'pikachu_scale_other_scenes_relative_to_initial_preview':PIKACHU_SCALE,
          'meeting_visible_height_px':MEETING_VISIBLE_HEIGHT,
          'meeting_foot_anchor_viewport_px':MEETING_FOOT_ANCHOR,
          'opening_specific_character_art_included':'three derivative expression edits in strike only',
          'new_original_poses':False,
          'expression_provenance':'outputs/pikachu-expression-edit-v1/provenance.json',
          'source_snapshot':'48e75f4d1f150c98eecfc82ba15487485c47e5e3',
          'latest_user_direction':'10-second anime episode 1; FR/LG native asset route',
          'shots':[{'start_frame':a,'end_frame_exclusive':b,'id':c,'label':d} for a,b,c,d,_ in SHOTS],
          'limitations':['Only strike uses three edited expressions from the supplied anime reference. Other shots retain existing gameplay sprites. New original run/leap poses are unfinished.',
                         'Silent compositing prototype, not ROM footage.',
                         'Existing throw pose substitutes for shielding pose.',
                         'Pikachu runs beside Red; no existing carrying pose was found.',
                         'Ho-oh uses head-on flight art on a depth-axis approach.',
                         'Title and ending credits have not been changed.'],
          'assets':[{'path':p,'sha256':hashlib.sha256((args.repo/p).read_bytes()).hexdigest()} for p in sorted(sources)]}
(OUT/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Created {OUT}',flush=True)
