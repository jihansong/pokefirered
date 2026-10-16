#!/usr/bin/env python3
"""Review-only title text from existing SVG paths; Pillow PNG I/O only."""
from pathlib import Path
import argparse,hashlib,json,math,re,sys,xml.etree.ElementTree as ET
from PIL import Image
SVG_SHA="3847e12d357a45d6167455821021c67c4dcf3179552420f5c609c44db3dc4238"
PNG_SHA="81fd0c6c1cbece648405a5ce26c6b770c3d3474f93ab5ceb1e9da321c9d8bfa0"
BOX=(34,58,134,93)
GLYPHS={"T":"M0 0H10V3H7V16H3V3H0Z","H":"M0 0H3V6H7V0H10V16H7V10H3V16H0Z","U":"M0 0H3V11Q3 13 5 13Q7 13 7 11V0H10V12Q10 16 5 16Q0 16 0 12Z","N":"M0 0H3L7 9V0H10V16H7L3 7V16H0Z","D":"M0 0H5Q11 0 11 8Q11 16 5 16H0ZM3 3V13H5Q8 13 8 8Q8 3 5 3Z","E":"M0 0H10V3H3V6H9V9H3V13H10V16H0Z","R":"M0 0H5Q10 0 10 5Q10 8 7 9L11 16H7L3 9V16H0ZM3 3V7H5Q7 7 7 5Q7 3 5 3Z","Y":"M0 0H3L5 6L7 0H10L7 10V16H3V10Z","L":"M0 0H3V13H10V16H0Z","O":"M5 0Q10 0 10 8Q10 16 5 16Q0 16 0 8Q0 0 5 0ZM5 3Q3 3 3 8Q3 13 5 13Q7 13 7 8Q7 3 5 3Z","W":"M0 0H3L4 10L6 5L8 10L9 0H12L10 16H7L6 11L5 16H2Z"}
def sha(b):return hashlib.sha256(b).hexdigest()
def word(text,x,y,sx,sy):
    acc=0;parts=[]
    for i,c in enumerate(text):
        angle=(-5,3,-3,2,0,-3,4)[i%7];dy=abs(i-(len(text)-1)/2)*.7
        parts.append(f'<g transform="translate({acc} {dy:g}) rotate({angle} 5 8)"><path d="{GLYPHS[c]}"/></g>')
        acc+=14 if c=="W" else 13 if c in "DR" else 12
    return f'<g transform="translate({x} {y}) scale({sx} {sy})">'+"".join(parts)+"</g>"
def overlay():
    letters=word("THUNDER",40,59,.94,.82)+word("YELLOW",36,75,1.2,.87)
    body='<rect x="34" y="58" width="100" height="35" fill="#3152b5"/>'
    body+='<g fill="#081840" stroke="#081840" stroke-width="3.1" stroke-linejoin="round" fill-rule="evenodd" transform="translate(1 1.7)">'+letters+"</g>"
    body+='<g fill="#F8E838" stroke="#2848C8" stroke-width="2.3" stroke-linejoin="round" paint-order="stroke" fill-rule="evenodd">'+letters+"</g>"
    return '<g id="native-wordmark-python-v3" shape-rendering="crispEdges">'+body+"</g>"
I=(1,0,0,1,0,0)
def mul(a,b):
    A,B,C,D,E,F=a;G,H,J,K,L,M=b
    return(A*G+C*H,B*G+D*H,A*J+C*K,B*J+D*K,A*L+C*M+E,B*L+D*M+F)
def transform(text):
    out=I
    for name,body in re.findall(r"([A-Za-z]+)\(([^)]*)\)",text):
        v=[float(n) for n in re.findall(r"[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?",body)]
        if name=="translate":m=(1,0,0,1,v[0],v[1] if len(v)>1 else 0)
        elif name=="scale":m=(v[0],0,0,v[1] if len(v)>1 else v[0],0,0)
        elif name=="rotate":
            a=math.radians(v[0]);m=(math.cos(a),math.sin(a),-math.sin(a),math.cos(a),0,0)
            if len(v)==3:m=mul(mul((1,0,0,1,v[1],v[2]),m),(1,0,0,1,-v[1],-v[2]))
        else:raise ValueError("Unsupported transform: "+name)
        out=mul(out,m)
    return out
def inverse(m):
    a,b,c,d,e,f=m;det=a*d-b*c
    assert abs(det)>1e-12
    return(d/det,-b/det,-c/det,a/det,(c*f-d*e)/det,(b*e-a*f)/det)
def point(m,x,y):a,b,c,d,e,f=m;return a*x+c*y+e,b*x+d*y+f
def contours(d):
    tokens=re.findall(r"[A-Za-z]|[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?",d)
    i=0;x=y=0.;current=[];paths=[];cmd=None
    def num():
        nonlocal i
        v=float(tokens[i]);i+=1;return v
    while i<len(tokens):
        if tokens[i].isalpha():cmd=tokens[i];i+=1
        if cmd=="M":
            if current:raise ValueError("Unclosed contour")
            x,y=num(),num();current=[(x,y)];cmd="L"
        elif cmd=="L":x,y=num(),num();current.append((x,y))
        elif cmd=="H":x=num();current.append((x,y))
        elif cmd=="V":y=num();current.append((x,y))
        elif cmd=="Q":
            qx,qy,nx,ny=num(),num(),num(),num();ox,oy=x,y
            for step in range(1,33):
                t=step/32;s=1-t
                current.append((s*s*ox+2*s*t*qx+t*t*nx,s*s*oy+2*s*t*qy+t*t*ny))
            x,y=nx,ny
        elif cmd=="Z":
            if current[0]!=current[-1]:current.append(current[0])
            paths.append(current);current=[];cmd=None
        else:raise ValueError("Unsupported glyph command: "+str(cmd))
    if current:raise ValueError("Open glyph contour")
    return paths
def inside(paths,x,y):
    odd=False
    for path in paths:
        for (a,b),(c,d) in zip(path,path[1:]):
            if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:odd=not odd
    return odd
def near(paths,x,y,half):
    h2=half*half
    for path in paths:
        for (a,b),(c,d) in zip(path,path[1:]):
            dx,dy=c-a,d-b;n=dx*dx+dy*dy
            t=0 if not n else min(1,max(0,((x-a)*dx+(y-b)*dy)/n))
            if (x-a-t*dx)**2+(y-b-t*dy)**2<=h2:return True
    return False
def colour(value):
    if value in (None,"none"):return None
    assert re.fullmatch(r"#[0-9A-Fa-f]{6}",value),value
    return bytes.fromhex(value[1:])+b"\xff"
def render_wordmark(original,markup):
    raw=bytearray(original);elements=[]
    def walk(node,m=I,style=None):
        st=dict(style or {})
        for k in ("fill","stroke","stroke-width","paint-order"):
            if k in node.attrib:st[k]=node.attrib[k]
        m=mul(m,transform(node.get("transform","")))
        if node.tag=="path":elements.append((contours(node.attrib["d"]),m,st))
        elif node.tag=="rect":
            x,y,w,h=(float(node.get(k,"0")) for k in ("x","y","width","height"))
            elements.append(([[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]],m,st))
        elif node.tag!="g":raise ValueError("Unsupported SVG node: "+node.tag)
        for child in node:walk(child,m,st)
    walk(ET.fromstring(markup))
    for paths,m,st in elements:
        inv=inverse(m);fill=colour(st.get("fill"));stroke=colour(st.get("stroke"));half=float(st.get("stroke-width","1"))/2
        points=[point(m,x,y) for p in paths for x,y in p]
        margin=half*max(math.hypot(m[0],m[1]),math.hypot(m[2],m[3]))+1 if stroke else 1
        x0=max(BOX[0],math.floor(min(p[0] for p in points)-margin));x1=min(BOX[2],math.ceil(max(p[0] for p in points)+margin))
        y0=max(BOX[1],math.floor(min(p[1] for p in points)-margin));y1=min(BOX[3],math.ceil(max(p[1] for p in points)+margin))
        for y in range(y0,y1):
            for x in range(x0,x1):
                u,v=point(inv,x+.5,y+.5);f=fill if fill and inside(paths,u,v) else None
                s=stroke if stroke and near(paths,u,v,half) else None
                c=(f or s) if st.get("paint-order")=="stroke" else (s or f)
                if c:raw[(y*240+x)*4:(y*240+x+1)*4]=c
    return bytes(raw)
def build(source):
    source=Path(source);sb=(source/"title-front-candidate.svg").read_bytes();pb=(source/"title-front-candidate-240x160.png").read_bytes()
    assert sha(sb)==SVG_SHA,"Unreviewed SVG source; stop"
    assert sha(pb)==PNG_SHA,"Unreviewed PNG source; stop"
    old=Image.open(source/"title-front-candidate-240x160.png").convert("RGBA");assert old.size==(240,160)
    markup=overlay();old_raw=old.tobytes();raw=render_wordmark(old_raw,markup);changed=outside=0
    for y in range(160):
        for x in range(240):
            i=(y*240+x)*4
            if raw[i:i+4]!=old_raw[i:i+4]:
                changed+=1
                if not(BOX[0]<=x<BOX[2] and BOX[1]<=y<BOX[3]):outside+=1
    assert changed and outside==0
    cel=Image.open(source/"front-mono-fitted.png").convert("RGBA");values=list(cel.getdata());cols={p[:3] for p in values if p[3]};alpha=sorted({p[3] for p in values})
    assert len(cols)==15 and alpha==[0,255] and all(v%8==0 for c in cols for v in c)
    svg=sb.decode("utf-8");assert svg.count("</svg>")==1
    append='<defs><clipPath id="python-wordmark-clip"><rect x="34" y="58" width="100" height="35"/></clipPath></defs><g clip-path="url(#python-wordmark-clip)">'+markup+"</g>"
    svg=svg.replace("</svg>",append+"</svg>")
    report={"status":"FONT_ONLY_REVIEW_PNG","native_size":[240,160],"changed_pixels":changed,"outside_font_rectangle_changed_pixels":outside,"source_svg_sha256":sha(sb),"source_png_sha256":sha(pb),"output_rgba_sha256":sha(raw),"pikachu_source_unchanged":True,"pikachu_colours":len(cols),"pikachu_alpha":alpha,"new_pikachu_art":False,"gif_created":False,"rom_integrated":False,"user_approved":False,"renderer":"Existing SVG paths; quadratic curves subdivided into 32 segments, binary pixel-centre fill and round stroke; Pillow PNG I/O only","libvips_pixel_equivalence_claimed":False}
    return Image.frombytes("RGBA",(240,160),raw),svg,report
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source-dir",type=Path,default=Path("outputs/title-front-edit-v1"));ap.add_argument("--out",type=Path,required=True);ap.add_argument("--check-only",action="store_true");args=ap.parse_args()
    if args.out.exists():raise FileExistsError("Choose a new review directory")
    im,svg,report=build(args.source_dir)
    if args.check_only:print(json.dumps(report));return 0
    args.out.mkdir(parents=True);(args.out/"title-font-candidate.svg").write_text(svg,encoding="utf-8");im.save(args.out/"title-font-candidate-240x160.png");im.resize((960,640),Image.Resampling.NEAREST).save(args.out/"title-font-candidate-4x.png")
    report["output_png_sha256"]=sha((args.out/"title-font-candidate-240x160.png").read_bytes());(args.out/"validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8");print(json.dumps(report));return 0
if __name__=="__main__":sys.exit(main())