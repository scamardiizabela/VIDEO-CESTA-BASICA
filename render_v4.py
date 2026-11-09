"""Boa Mesa V4. Voice-led product campaign, deterministic perspective compositor.
Original imagery only. Raster layers are composed at 1080x1920, 30 fps.
"""
from pathlib import Path
from functools import lru_cache
import json, math, subprocess, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R=Path(__file__).resolve().parent; A=R/'assets'; O=R/'renders'; O.mkdir(exist_ok=True)
W,H,FPS,D=1080,1920,30,44
if (R/'assets_v4.zip').exists():
    with zipfile.ZipFile(R/'assets_v4.zip') as z:
        for n in z.namelist():
            if '/' not in n and not (A/n).exists():(A/n).write_bytes(z.read(n))
alignment=json.loads((R/'alignment_v4.json').read_text())
al=alignment.get('normalized_alignment') or alignment['alignment']; speech=''.join(al['characters'])
def cue(s,last=False):
    i=speech.rfind(s) if last else speech.find(s)
    if i<0:raise ValueError(s)
    return .25+al['character_start_times_seconds'][i]
S=[0,cue('Na Boa Mesa'),cue('Escolha entre'),cue('Complete'),cue('E para empresas'),cue('No WhatsApp'),cue('Do pedido'),cue('Tudo organizado'),cue('Entrega rápida'),cue('Boa Mesa Cesta'),cue('Escolha sua')]
C={'red':'#8e1320','wine':'#450a12','gold':'#ffbb36','cream':'#fff6e5','dark':'#25090f','white':'#ffffff'}
def clamp(x):return max(0,min(1,x))
def out(x):return 1-(1-clamp(x))**4
def smooth(x):return .5-.5*math.cos(math.pi*clamp(x))
def spring(x):
    x=clamp(x)
    return 1-math.exp(-7*x)*math.cos(10*x) if x<1 else 1
@lru_cache(200)
def font(size,display=True):return ImageFont.truetype(str(A/('Display-Bold.otf' if display else 'Inter-Bold.ttf')),int(size))
def paste(im,layer,x,y,alpha=1):
    if alpha<=0:return
    if alpha<.999:
        layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda p:round(p*alpha)))
    im.alpha_composite(layer,(round(x),round(y)))
@lru_cache(400)
def txt(s,size,color,display=True,stroke=0):
    f=font(size,display);bb=f.getbbox(s,stroke_width=stroke)
    im=Image.new('RGBA',(math.ceil(f.getlength(s))+stroke*2+10,bb[3]-bb[1]+stroke*2+12))
    ImageDraw.Draw(im).text((stroke+3,stroke-bb[1]+4),s,font=f,fill=color,stroke_width=stroke,stroke_fill=color)
    return im
def text(im,s,x,y,size=70,color=None,display=True,maxw=940,alpha=1):
    color=color or C['cream'];layer=txt(s,size,color,display)
    if layer.width>maxw:layer=layer.resize((maxw,round(layer.height*maxw/layer.width)),Image.Resampling.LANCZOS)
    paste(im,layer,x,y,alpha);return layer.height
def reveal(im,s,x,y,size,t,start,color=None,style='rise',maxw=940):
    p=out((t-start)/.6);layer=txt(s,size,color or C['cream'])
    if layer.width>maxw:layer=layer.resize((maxw,round(layer.height*maxw/layer.width)),Image.Resampling.LANCZOS)
    if style=='scale':
        sc=.76+.24*spring((t-start)/.7);layer=layer.resize((max(1,round(layer.width*sc)),max(1,round(layer.height*sc))),Image.Resampling.BICUBIC)
        paste(im,layer,x,y+35*(1-p),p)
    else:
        target=Image.new('RGBA',(layer.width+4,layer.height+14));paste(target,layer,0,(1-p)*(layer.height+15))
        paste(im,target,x,y)
def lines(im,ss,t,start,x=76,y=1120,size=150,accent=-1):
    for i,s in enumerate(ss):reveal(im,s,x,y+i*size*.87,size,t,start+i*.075,C['gold'] if i==accent else C['cream'])
def brand(im,t):
    text(im,'BOA',76,122,53,display=False,maxw=170);text(im,'MESA',200,122,53,C['gold'],False,maxw=210)
    ImageDraw.Draw(im).line((78,199,204,199),fill=C['gold'],width=4)

@lru_cache(4)
def base(kind=0):
    yy,xx=np.mgrid[0:H,0:W];r=np.sqrt(((xx-620)/980)**2+((yy-950)/1700)**2)
    c1=np.array([165,29,43]) if kind==0 else np.array([89,13,25]); c2=np.array([51,7,17])
    v=np.clip(r,0,1)[...,None];ar=c1*(1-v)+c2*v
    rng=np.random.default_rng(41);ar+=rng.normal(0,.65,(H,W,1))
    return Image.fromarray(np.uint8(np.clip(ar,0,255))).convert('RGBA')
def stage(t,kind=0):
    im=base(kind).copy();layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    # Graphic planes echo the gold folded packaging in the logo.
    dx=75*math.sin(t*.35)
    d.polygon([(820+dx,-50),(1180,-50),(340+dx,1980),(-80,1980)],fill=(202,43,45,34))
    d.line([(1190+dx,410),(930+dx,1100),(690+dx,1750)],fill=(255,182,48,47),width=3)
    im.alpha_composite(layer);brand(im,t);return im

names=['proposta_01.png','proposta_02.png','proposta_03.png','proposta_04.png','kit_limpeza.png']
ART=[Image.open(A/n).convert('RGBA')for n in names]
PACK=[im.crop((140,487,731,1297))for im in ART]
for im in PACK:
    mask=Image.new('L',im.size);ImageDraw.Draw(mask).rounded_rectangle((4,3,im.width-5,im.height-4),radius=20,fill=255);im.putalpha(mask)
POST=[im.resize((648,1152),Image.Resampling.LANCZOS)for im in ART]
logo=Image.open(A/'logo_site.png').convert('RGBA');logo=logo.crop(logo.getchannel('A').getbbox())
def project(im,source,cx,cy,height,ry=0,rz=0,opacity=1):
    """Project an intact photo plane through a real perspective homography."""
    hh=height;ww=hh*source.width/source.height
    ry,rz=math.radians(ry),math.radians(rz)
    pts=[]
    for x,y in [(-ww/2,-hh/2),(ww/2,-hh/2),(ww/2,hh/2),(-ww/2,hh/2)]:
        xx=x*math.cos(ry);z=-x*math.sin(ry);yy=y
        xx,yy=xx*math.cos(rz)-yy*math.sin(rz),xx*math.sin(rz)+yy*math.cos(rz)
        fac=1700/(1700+z);pts.append((cx+xx*fac,cy+yy*fac))
    bx=max(-W,math.floor(min(p[0]for p in pts))-4);by=max(-H,math.floor(min(p[1]for p in pts))-4)
    ex=min(W*2,math.ceil(max(p[0]for p in pts))+4);ey=min(H*2,math.ceil(max(p[1]for p in pts))+4)
    if ex<=bx or ey<=by:return
    dest=[(x-bx,y-by)for x,y in pts];src=[(0,0),(source.width,0),(source.width,source.height),(0,source.height)]
    mat=[];rhs=[]
    for (x,y),(u,v) in zip(dest,src):
        mat.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);rhs.extend([u,v])
    co=np.linalg.solve(np.array(mat),np.array(rhs))
    layer=source.transform((ex-bx,ey-by),Image.Transform.PERSPECTIVE,co,Image.Resampling.BICUBIC)
    paste(im,layer,bx,by,opacity)
def shadow(im,cx,cy,w=640):
    layer=Image.new('RGBA',(W,H));ImageDraw.Draw(layer).ellipse((cx-w/2,cy-33,cx+w/2,cy+33),fill=(8,0,3,160));layer=layer.filter(ImageFilter.GaussianBlur(23));im.alpha_composite(layer)
def underline(im,x,y,width,t,st):
    p=out((t-st)/.45);d=ImageDraw.Draw(im);d.polygon([(x,y),(x+width*p,y-6),(x+width*p+12,y+10),(x+5,y+13)],fill=C['gold'])
def hook(t):
    im=stage(t);local=t
    if t<cue('Mais qualidade'):
        reveal(im,'SUA COMPRA',76,305,115,t,.15)
        reveal(im,'MERECE',70,428,228,t,.3)
        reveal(im,'MAIS.',61,623,355,t,.65,C['gold'],'scale')
    else:
        if t<cue('Mais escolha'):a='QUALIDADE';st=cue('Mais qualidade')
        elif t<cue('Mais cuidado'):a='ESCOLHA';st=cue('Mais escolha')
        else:a='CUIDADO';st=cue('Mais cuidado')
        reveal(im,'MAIS',77,337,180,t,st)
        reveal(im,a,73,520,210,t,st+.07,C['gold'],'scale')
        underline(im,80,759,840,t,st+.18)
    p=spring((t-.45)/1.0);shadow(im,555,1780,670)
    beats=[0,cue('Mais qualidade'),cue('Mais escolha'),cue('Mais cuidado')]
    bi=max(i for i,s in enumerate(beats)if t>=s);age=t-beats[bi]
    bump=math.exp(-age*7)*math.sin(age*13) if bi else 0
    project(im,PACK[bi],555+210*(1-out(t/.9))+48*bump,1370+490*(1-p),840*(.85+.15*p)+65*bump,-19*(1-out(t/1.2))+6*math.sin(t*.7)+19*bump,-7*(1-out(t/1.1))+1.5*math.sin(t)+5*bump)
    return im
def audiences(t):
    im=stage(t,1);p=out((t-S[1])/.75)
    home=t<cue('sua empresa')-.1;st=S[1] if home else cue('sua empresa')-.1
    lines(im,['PARA SUA' if home else 'PARA SUA','CASA.' if home else 'EMPRESA.'],t,st,y=310,size=197,accent=1)
    shadow(im,590,1620)
    for i in range(2):
        project(im,PACK[0 if i==0 else 3],350+i*350,1245+95*i+100*(1-p),710+70*i,(-20 if i==0 else 20)*(1-.25*p),(-9 if i==0 else 8),.92 if i==0 else 1)
    return im
def proposals(t):
    im=stage(t);q=(t-S[2])/(S[3]-S[2]);center=q*3.6
    reveal(im,'ESCOLHA A SUA.',76,290,154,t,S[2],C['gold'])
    # Continuous 3D camera pass: original cards glide through, no slide deck holds.
    for i in sorted(range(4),key=lambda i:-abs(i-center)):
        dist=i-center;cx=540+dist*680;hh=1180-190*min(abs(dist),2)
        project(im,POST[i],cx,1080+35*abs(dist),hh,-dist*19,-dist*4,clamp(1-abs(dist)*.24))
    text(im,'CESTAS BÁSICAS • DIFERENTES PROPOSTAS',77,1748,30,C['cream'],False,maxw=930)
    return im
def cleaning(t):
    im=stage(t,1);p=spring((t-S[3])/.8)
    lines(im,['COMPLETE','O CUIDADO.'],t,S[3],y=300,size=174,accent=1)
    shadow(im,550,1635)
    project(im,PACK[4],550+540*(1-out((t-S[3])/.6)),1190+95*(1-p),1000*(.82+.18*p),35*(1-out((t-S[3])/.8)),5*(1-out((t-S[3])/.8)))
    reveal(im,'KIT DE LIMPEZA',78,1715,81,t,S[3]+.45)
    return im
def pat(t):
    im=stage(t);p=out((t-S[4])/.7)
    text(im,'SOLUÇÕES PARA EMPRESAS',78,313,35,C['cream'],False)
    reveal(im,'SUA EQUIPE',72,410,162,t,S[4])
    reveal(im,'BEM CUIDADA.',72,558,162,t,S[4]+.15,C['gold'])
    project(im,PACK[2],830+130*(1-p),1280,590,15,-5)
    reveal(im,'PAT',72,900,290,t,cue('fornecedor'),C['gold'],'scale',maxw=600)
    text(im,'Fornecedor registrado',80,1227,45,C['cream'],False,maxw=500)
    text(im,'Programa de Alimentação',80,1308,30,C['cream'],False,maxw=490)
    text(im,'do Trabalhador',80,1352,30,C['cream'],False,maxw=490)
    underline(im,80,1435,450,t,cue('PAT'))
    text(im,'Registro FO002424',80,1495,28,C['cream'],False,maxw=500)
    return im
def wrapped(s,size,width):
    f=font(size,False);ls=[];line=''
    for w in s.split():
        if f.getlength((line+' '+w).strip())>width and line:ls.append(line);line=w
        else:line=(line+' '+w).strip()
    if line:ls.append(line)
    return ls
def phone(t):
    im=Image.new('RGBA',(840,1160));d=ImageDraw.Draw(im)
    d.rounded_rectangle((1,1,839,1159),radius=70,fill='#180e12',outline='#b7856a',width=4)
    d.rounded_rectangle((19,20,821,1140),radius=55,fill='#eee9df')
    d.rounded_rectangle((19,20,821,194),radius=55,fill='#075e54');d.rectangle((19,111,821,194),fill='#075e54')
    text(im,'Boa Mesa',117,72,47,'#ffffff',False,maxw=600);d.ellipse((52,78,84,110),fill='#25d366')
    text(im,'Atendimento pelo WhatsApp',116,133,25,'#d7eee7',False,maxw=650)
    st=S[5]+.35;msg='Olá! Vi seu anúncio de cestas básicas e gostaria de mais informações';p=clamp((t-st)/1.1)
    if p>0:
        d.rounded_rectangle((51,250,724,500),radius=23,fill='white')
        for i,l in enumerate(wrapped(msg[:int(len(msg)*p)],33,600)):text(im,l,82,285+i*45,33,'#20352d',False,maxw=600)
    if t>S[5]+1.9:
        p=out((t-S[5]-1.9)/.5);b=Image.new('RGBA',(680,225));bd=ImageDraw.Draw(b);bd.rounded_rectangle((0,0,679,224),radius=23,fill='#d7f8ce')
        for i,l in enumerate(wrapped('Olá! Vamos encontrar a proposta ideal para você.',34,610)):text(b,l,29,32+i*46,34,'#20352d',False,maxw=610)
        paste(im,b,110,599+70*(1-p),p)
    return im
def contact(t):
    im=stage(t,1);p=out((t-S[5])/.8)
    lines(im,['GENTE DE','VERDADE.'],t,S[5],y=300,size=184,accent=1)
    project(im,phone(t),590+350*(1-p),1180,1000,-16*(1-.6*p),-6*(1-p))
    if t>=cue('Atendimento'):
        reveal(im,'HUMANIZADO + RÁPIDO',78,1716,73,t,cue('Atendimento'),C['gold'])
    return im

class Frames:
    def __init__(self,n):
        self.n=n;self.p=None;self.index=-1;self.last=None
    def get(self,t):
        target=max(0,int(t*FPS))
        if self.p is None or target<self.index:
            if self.p:self.p.terminate()
            self.p=subprocess.Popen(['ffmpeg','-v','fatal','-threads','2','-i',str(A/self.n),'-an','-vf','fps=30,scale=1080:1920:flags=lanczos','-threads','2','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE);self.index=-1
        while self.index<target:
            b=self.p.stdout.read(W*H*3)
            if len(b)<W*H*3:break
            self.last=Image.frombytes('RGB',(W,H),b);self.index+=1
        if self.last is None:raise RuntimeError('No source frame')
        return self.last.convert('RGBA')
FILM={}
def frame(name,t):
    if name not in FILM:FILM[name]=Frames(name)
    return FILM[name].get(t)
@lru_cache(1)
def scrim():
    ar=np.zeros((H,W,4),np.uint8);ar[:,:,:3]=[20,2,8]
    ar[:,:,3]=np.maximum(np.clip((np.arange(H)[:,None]-830)/1000,0,.86),np.clip((240-np.arange(H)[:,None])/400,0,.4))*255
    return Image.fromarray(ar)
def real(name,tt,t):
    im=frame(name,tt);im.alpha_composite(scrim());brand(im,t);return im
def prep(t):
    local=t-S[6]
    # Cut to a second real framing on the spoken material-quality cue.
    off=.5+local if t<cue('qualidade nos') else 10+local-cue('qualidade nos')+S[6]
    im=real('producao.mp4',off,t)
    if t<cue('qualidade nos'):ss=['PEDIDO','CONFIRMADO.'];st=S[6]
    elif t<cue('cuidado em'):ss=['QUALIDADE','NOS MATERIAIS.'];st=cue('qualidade nos')
    else:ss=['CUIDADO EM','CADA DETALHE.'];st=cue('cuidado em')
    lines(im,ss,t,st,y=1280,size=151,accent=1);underline(im,80,1600,780,t,st+.2)
    return im
def stock(t):
    im=real('estoque.mp4',t-S[7]+1,t)
    lines(im,['TUDO','ORGANIZADO.'],t,S[7],y=1310,size=173,accent=1)
    return im
def loading(t):
    im=real('carregamento.mp4',t-S[8]+.5,t)
    lines(im,['ENTREGA','RÁPIDA.'],t,S[8],y=1230,size=199,accent=1)
    underline(im,80,1610,630,t,S[8]+.25)
    text(im,'Condições combinadas no atendimento.',80,1691,31,C['cream'],False,maxw=920)
    return im
def closing(t):
    im=stage(t,1);p=out((t-S[9])/.7)
    # Official logo retained as original raster on a warm brand plaque.
    plaque=Image.new('RGBA',(820,440),C['cream']);sc=min(650/logo.width,370/logo.height);lg=logo.resize((round(logo.width*sc),round(logo.height*sc)),Image.Resampling.LANCZOS);paste(plaque,lg,(820-lg.width)/2,(440-lg.height)/2)
    project(im,plaque,540,600+120*(1-p),440,15*(1-p),-3*(1-p))
    for i in [0,2,1]:
        project(im,PACK[[0,4,3][i]],270+i*270,1360+65*(i!=1),680 if i!=1 else 760,[-13,0,13][i],[-9,0,9][i])
    if t>=S[10]:
        # Final CTA replaces the pack fan with strong white typography.
        im=stage(t,1);paste(im,plaque,130,290)
        lines(im,['ESCOLHA A SUA.','PEÇA AGORA.'],t,S[10],y=850,size=153,accent=1)
        underline(im,80,1164,850,t,S[10]+.28)
        p=spring((t-S[10]-.3)/.8);box=Image.new('RGBA',(920,166));bd=ImageDraw.Draw(box);bd.rounded_rectangle((0,0,919,165),radius=28,fill='#22c36a')
        text(box,'CHAME NO WHATSAPP',54,43,67,'#092e1b',True,maxw=820);paste(im,box,80,1280+70*(1-p),out((t-S[10]-.3)/.5))
        text(im,'(17) 98159-2950',80,1515,53,C['cream'],False,maxw=920)
        text(im,'boamesacestabasica.com.br',80,1645,36,C['cream'],False,maxw=920)
    return im
FUN=[hook,audiences,proposals,cleaning,pat,contact,prep,stock,loading,closing,closing]
def raw(t):return FUN[max(i for i,s in enumerate(S)if t>=s)](t)
def renderframe(t):
    i=max(k for k,s in enumerate(S)if t>=s);im=FUN[i](t)
    if i<9 and t>S[i+1]-.35:
        q=clamp((t-S[i+1]+.35)/.35);nxt=FUN[i+1](S[i+1]+q*.035)
        if i in (1,2,7):
            # Camera whip: adjoining planes, acceleration and directional shutter blur.
            p=smooth(q);outgoing=im;im=base(1).copy()
            paste(im,outgoing,-W*p,0);paste(im,nxt,W*(1-p),0)
            if .05<q<.95:
                a=np.asarray(im).astype(np.float32);step=round(15*math.sin(math.pi*q))
                a=(a+np.roll(a,step,axis=1)+np.roll(a,-step,axis=1))/3
                im=Image.fromarray(a.astype(np.uint8))
        elif i in (4,8):
            # Lens opening into the phone/brand: increasing rounded aperture.
            p=smooth(q);mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
            rw=10+W*1.4*p;rh=20+H*1.4*p
            md.rounded_rectangle((540-rw/2,960-rh/2,540+rw/2,960+rh/2),radius=round(80*(1-p)),fill=255)
            im=Image.composite(nxt,im,mask)
        else:
            # Brand-angle wipe, alternating direction through the operational sequence.
            xx,yy=np.meshgrid(np.arange(W),np.arange(H));edge=(-W*.5)+(W*2.2)*smooth(q)
            coord=xx+.27*(yy-H/2) if i%2==0 else W-xx+.27*(yy-H/2)
            mask=np.uint8(np.clip((edge-coord)/10,0,1)*255)
            im=Image.composite(nxt,im,Image.fromarray(mask));d=ImageDraw.Draw(im)
            if .12<q<.86:
                x=edge+.27*H/2
                if i%2==0:d.line((x,0,x-.27*H,H),fill=C['gold'],width=12)
                else:d.line((W-x,0,W-x+.27*H,H),fill=C['gold'],width=12)
    return im
def render():
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','15','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(O/'picture_v4.mp4')]
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    print('Cues',S,flush=True)
    for n in range(D*FPS):
        t=n/FPS;im=renderframe(t)
        if n%15==0:im.convert('RGB').resize((270,480)).save(O/f'v4-{n:04d}.jpg')
        enc.stdin.write(im.convert('RGB').tobytes())
        if n%90==0:print(f'{t:.0f}/{D}s',flush=True)
    enc.stdin.close()
    if enc.wait():raise RuntimeError('Failed encode')
    (R/'timing_v4.json').write_text(json.dumps({'duration':D,'scene_starts':S,'voice_offset':.25},indent=2))
if __name__=='__main__':
    if '--frames' in sys.argv:
        for t in map(float,sys.argv[sys.argv.index('--frames')+1:]):renderframe(t).convert('RGB').resize((540,960)).save(O/f'v4-review-{t:g}.jpg')
    else:render()
