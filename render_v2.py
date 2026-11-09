"""Narrated Boa Mesa film. Deterministic masks, kinetic type and real footage.
API credentials are deliberately absent. Narration and alignment are local assets.
"""
from pathlib import Path
from functools import lru_cache
import math,json,re,subprocess,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parent; A=ROOT/'assets'; O=ROOT/'renders'; O.mkdir(exist_ok=True)
W,H,FPS,DURATION=1080,1920,30,31
RED='#a11c25'; DEEP='#390d19'; GOLD='#ffbd28'; PAPER='#fffaf3'; WHITE='#ffffff'
SPEED=.92; DELAY=.55
if (ROOT/'assets_v2.zip').exists():
    with zipfile.ZipFile(ROOT/'assets_v2.zip') as z:
        for name in ['narracao_v2.mp3','Inter-Regular.ttf','Inter-Bold.ttf','whoosh.mp3','chime.mp3','impact.mp3']:
            if not (A/name).exists():(A/name).write_bytes(z.read(name))
alignment=json.loads((ROOT/'alignment_v2.json').read_text())
alignment=alignment.get('normalized_alignment') or alignment['alignment']
spoken=''.join(alignment['characters'])
WORDS=[]
for m in re.finditer(r'\S+',spoken):
    WORDS.append(dict(text=m.group(),start=DELAY+alignment['character_start_times_seconds'][m.start()]/SPEED,end=DELAY+alignment['character_end_times_seconds'][m.end()-1]/SPEED))
def cue(phrase,last=False):
    i=spoken.rfind(phrase) if last else spoken.find(phrase)
    if i<0: raise ValueError(phrase)
    return DELAY+alignment['character_start_times_seconds'][i]/SPEED
STARTS=[0,cue('Nossa equipe'),cue('Depois'),cue('É hora'),cue('Para sua casa'),cue('Boa Mesa',True)]
def clamp(x): return max(0,min(1,x))
def out(x): return 1-(1-clamp(x))**3
def smooth(x): x=clamp(x);return x*x*(3-2*x)
@lru_cache(100)
def font(sz,bold=True): return ImageFont.truetype(str(A/('Inter-Bold.ttf' if bold else 'Inter-Regular.ttf')),sz)
@lru_cache(300)
def label(txt,sz,color=WHITE,bold=True,width=920):
    f=font(sz,bold); lines=[];line=''
    for word in txt.split():
        test=(line+' '+word).strip()
        if f.getlength(test)>width and line:lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    img=Image.new('RGBA',(width,math.ceil(len(lines)*sz*1.16+sz*.25)))
    d=ImageDraw.Draw(img)
    for i,line in enumerate(lines): d.text((0,i*sz*1.16),line,font=f,fill=color)
    return img
def place(im,layer,xy,alpha=1):
    if alpha<=0:return
    if alpha<1:
        layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda v:int(v*alpha)))
    im.alpha_composite(layer,(round(xy[0]),round(xy[1])))
def reveal(im,txt,xy,sz,t,delay=0,color=WHITE,width=920,kind='up',duration=.65):
    layer=label(txt,sz,color,True,width);p=out((t-delay)/duration)
    if p==0:return
    if kind=='wipe':
        mask=Image.new('L',layer.size);ImageDraw.Draw(mask).rectangle((0,0,int(layer.width*p),layer.height),fill=255)
        layer=layer.copy();layer.putalpha(Image.fromarray(np.minimum(np.array(layer.getchannel('A')),np.array(mask))))
        place(im,layer,xy)
    else:
        # Fixed clipping window: the baseline rises into place instead of floating.
        box=Image.new('RGBA',layer.size);place(box,layer,(0,(1-p)*layer.height))
        place(im,box,xy)
def fitlogo(width):
    logo=Image.open(A/'logo.jpg').convert('RGBA')
    return logo.resize((width,round(width*logo.height/logo.width)),Image.Resampling.LANCZOS)
LOGOS={220:fitlogo(220),680:fitlogo(680)}
@lru_cache(1)
def background():
    yy,xx=np.mgrid[0:H,0:W];g=np.exp(-(((xx-1050)/1100)**2+((yy-650)/1100)**2))
    base=np.empty((H,W,3),np.uint8)
    for k,(lo,hi) in enumerate(zip((46,8,20),(138,26,39))):base[:,:,k]=lo+(hi-lo)*g
    return Image.fromarray(base).convert('RGBA')
@lru_cache(1)
def shade():
    a=np.zeros((H,W,4),np.uint8);a[:,:,:3]=[30,11,19]
    a[:,:,3]=np.clip((np.arange(H)[:,None]-930)/750,0,.97)*255
    return Image.fromarray(a)
def rule(im,xy,width,t,color=GOLD):
    p=out(t/.6)
    if p:ImageDraw.Draw(im).rounded_rectangle((xy[0],xy[1],xy[0]+int(width*p),xy[1]+6),radius=3,fill=color)
def brand(im,t,dark=False):
    c=RED if dark else WHITE
    reveal(im,'BOA MESA / CESTA BÁSICA',(72,171),26,t,.04,c,width=830,kind='wipe',duration=.7)
def progress(im,i,t,duration):
    d=ImageDraw.Draw(im)
    for n in range(4):
        x=74+n*235; d.rounded_rectangle((x,1750,x+210,1755),radius=3,fill=(255,255,255,75))
        p=1 if n<i else clamp(t/duration) if n==i else 0
        if p:d.rounded_rectangle((x,1750,x+210*p,1755),radius=3,fill=GOLD)

# Short caption groups use the returned character alignment, not estimated words.
CAPTIONS=[];group=[]
for word in WORDS:
    group.append(word)
    if len(group)>=5 or word['text'].endswith(('.',':','!')):
        CAPTIONS.append(group);group=[]
if group:CAPTIONS.append(group)
def captions(im,t):
    if t>=STARTS[4]:return
    groups=[g for g in CAPTIONS if g[0]['start']-.07<=t<=g[-1]['end']+.09]
    if not groups:return
    g=groups[-1];f=font(39,True);widths=[f.getlength(w['text']+' ') for w in g]
    lines=[[]];used=0
    for word,ww in zip(g,widths):
        if used+ww>865 and lines[-1]:lines.append([]);used=0
        lines[-1].append((word,ww));used+=ww
    hh=56*len(lines)+38
    panel=Image.new('RGBA',(944,hh));d=ImageDraw.Draw(panel)
    d.rounded_rectangle((0,0,944,hh),radius=22,fill=(28,8,17,210))
    for k,line in enumerate(lines):
        x=(944-sum(ww for _,ww in line))/2
        for word,ww in line:
            active=word['start']<=t<=word['end']+.04
            past=t>word['end']
            color=GOLD if active else WHITE if past else '#c9bfc4'
            d.text((x,14+k*56),word['text'],font=f,fill=color)
            x+=ww
    place(im,panel,(68,1585),out((t-g[0]['start']+.07)/.18))

def phone(t):
    p=Image.new('RGBA',(920,780));d=ImageDraw.Draw(p)
    d.rounded_rectangle((22,23,908,757),radius=50,fill=(0,0,0,65))
    d.rounded_rectangle((8,0,892,730),radius=47,fill='#f3efe7',outline=WHITE,width=8)
    d.rounded_rectangle((16,8,884,154),radius=38,fill='#075e54');d.rectangle((16,90,884,154),fill='#075e54')
    d.ellipse((54,44,124,114),fill='#dce9df');d.ellipse((78,55,100,77),fill='#57766b');d.ellipse((67,79,110,105),fill='#57766b')
    d.text((150,36),'Cliente',font=font(37),fill=WHITE);d.text((150,88),'WhatsApp',font=font(26,False),fill='#e3eee9')
    if t<1.18:
        d.rounded_rectangle((54,210,235,290),radius=20,fill=WHITE)
        for n in range(3):
            y=249-5*math.sin(t*9+n);d.ellipse((88+n*43,y-7,102+n*43,y+7),fill='#7f9b8e')
    else:
        d.rounded_rectangle((54,207,825,478),radius=24,fill=WHITE)
        msg='Olá! Vi seu anúncio de cestas básicas e gostaria de mais informações'
        n=max(1,min(len(msg),int((t-1.18)*49)))
        place(p,label(msg[:n],38,'#20392f',False,685),(90,238))
        d.text((712,430),'09:41',font=font(23,False),fill='#78877e')
    d.rounded_rectangle((52,580,840,664),radius=42,fill=WHITE)
    d.text((91,596),'Mensagem',font=font(30,False),fill='#88918b')
    return p

def intro(t,absolute):
    im=background().copy();d=ImageDraw.Draw(im)
    # A thin orbit moves continuously and motivates the later circular logo reveal.
    r=500+12*math.sin(t*.6); d.arc((750-r,-190-r,750+r,-190+r),30+t*4,300+t*4,fill='#a84143',width=3)
    d.rounded_rectangle((744,165,1000,391),radius=24,fill=WHITE)
    p=out((t-.08)/.7);place(im,LOGOS[220],(762,177+25*(1-p)),p)
    reveal(im,'PARA QUEM VOCÊ QUER CUIDAR.',(74,216),25,t,.16,GOLD,width=650,kind='wipe')
    reveal(im,'Cuidar',(70,399),148,t,.05)
    reveal(im,'começa com',(74,570),76,t,.20)
    reveal(im,'uma conversa.',(74,660),76,t,.35,GOLD)
    rule(im,(78,779),176,t-.5)
    card=phone(t)
    angle=4.2*(1-out((t-.15)/1.15))+.45*math.sin(t*.75)
    card=card.rotate(angle,Image.Resampling.BICUBIC,expand=False)
    pp=out((t-.28)/.9);place(im,card,(80,842+140*(1-pp)),pp)
    # A restrained notification ring marks the arrival of the client's message.
    if 1.18<t<1.85:
        a=clamp((t-1.18)/.67);ring=Image.new('RGBA',(W,H));rd=ImageDraw.Draw(ring)
        rr=50+110*a;rd.ellipse((178-rr,920-rr,178+rr,920+rr),outline=(255,189,40,int(170*(1-a))),width=3);im.alpha_composite(ring)
    reveal(im,'01 / COTAÇÃO E PEDIDO',(76,803),24,t,.75,GOLD,kind='wipe')
    captions(im,absolute);progress(im,0,t,STARTS[1]);return im

class Reader:
    def __init__(self,path,offset=0,slow=1):
        self.p=subprocess.Popen(['ffmpeg','-v','fatal','-threads','2','-ss',str(offset),'-i',str(path),'-an','-vf',f'setpts={slow}*PTS,fps=30,scale=1112:1978:flags=lanczos','-threads','2','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
        self.last=None
    def read(self,t):
        b=self.p.stdout.read(1112*1978*3)
        if len(b)==1112*1978*3:self.last=Image.frombytes('RGB',(1112,1978),b).convert('RGBA')
        if self.last is None:raise RuntimeError('Original source decode failed')
        x=16+int(9*math.sin(t*.19));y=29+int(12*math.sin(t*.16))
        return self.last.crop((x,y,x+W,y+H))
readers={}
def film(i,t):
    if i not in readers:readers[i]=Reader(A/['producao.mp4','estoque.mp4','carregamento.mp4'][i], [.4,.8,0][i])
    return readers[i].read(t)

HEADS=[('02 / PREPARAÇÃO','Cuidado em','cada cesta.'),('03 / ORGANIZAÇÃO','Tudo pronto.','Tudo organizado.'),('04 / CARREGAMENTO','É hora de','seguir viagem.')]
def operation(i,t,absolute):
    im=film(i,t);im.alpha_composite(shade())
    pill=Image.new('RGBA',(W,H));ImageDraw.Draw(pill).rounded_rectangle((54,152,705,220),radius=34,fill=(45,8,22,190));im.alpha_composite(pill);brand(im,t)
    stage,l1,l2=HEADS[i]
    reveal(im,stage,(76,1176),28,t,.05,GOLD,kind='wipe')
    reveal(im,l1,(71,1240),86,t,.18)
    reveal(im,l2,(71,1341),86 if i!=1 else 78,t,.32,GOLD)
    rule(im,(78,1484),180,t-.45)
    # A hand-drawn-style underline grows precisely at the narrated benefit.
    if i==0 and absolute>=cue('organização'):
        reveal(im,'ORGANIZAÇÃO + ATENÇÃO',(76,1524),25,t,0,WHITE,width=920,kind='wipe',duration=.4)
    captions(im,absolute);progress(im,i+1,t,STARTS[i+2]-STARTS[i+1] if i<2 else STARTS[4]-STARTS[3]);return im

def bridge(t,absolute):
    im=background().copy();d=ImageDraw.Draw(im);brand(im,t)
    reveal(im,'CUIDADO QUE FAZ PARTE',(76,389),27,t,.05,GOLD,kind='wipe')
    reveal(im,'da sua vida.',(74,442),88,t,.16)
    home=out((absolute-cue('Para sua casa')+.05)/.55)
    team=out((absolute-cue('Para sua equipe')+.05)/.55)
    for k,(small,big,pp) in enumerate([('Para sua','CASA.',home),('Para sua','EQUIPE.',team)]):
        y=740+k*385
        reveal(im,small,(82,y),53,pp,0,WHITE,kind='wipe',duration=.8)
        layer=label(big,131,GOLD,True,920);place(im,layer,(76+(1-pp)*160,y+63),pp)
        d.line((82,y+254,82+int(894*pp),y+254),fill='#ae4952',width=2)
    return im

def ending(t,absolute):
    im=Image.new('RGBA',(W,H),PAPER);d=ImageDraw.Draw(im)
    # Golden circular motif resolves into the original logo's paper card.
    p=out(t/.85);r=235+65*p
    d.ellipse((540-r,590-r,540+r,590+r),fill='#ffe9ad')
    brand(im,t,True)
    card=Image.new('RGBA',(820,732));cd=ImageDraw.Draw(card)
    cd.rounded_rectangle((0,0,820,732),radius=44,fill=WHITE)
    place(card,LOGOS[680],(70,62))
    # Controlled scale overshoot creates a precise hero landing.
    scale=.88+.12*out(t/.75)+.012*math.sin(clamp(t/.85)*math.pi)
    cw,ch=round(820*scale),round(732*scale)
    card=card.resize((cw,ch),Image.Resampling.LANCZOS)
    place(im,card,((W-cw)/2,364+(732-ch)/2),out(t/.45))
    reveal(im,'Solicite sua cotação.',(76,1190),69,t,.5,RED,width=940)
    reveal(im,'Faça seu pedido.',(76,1278),69,t,.65,RED,width=940)
    rule(im,(78,1401),190,t-.85,RED)
    reveal(im,'boamesacestabasica.com.br',(78,1476),37,t,.9,DEEP,width=930,kind='wipe',duration=.8)
    cta=Image.new('RGBA',(930,116));dd=ImageDraw.Draw(cta)
    dd.rounded_rectangle((0,0,930,116),radius=58,fill=RED)
    dd.text((118,33),'FALE COM A BOA MESA',font=font(31),fill=WHITE)
    dd.line((816,58,858,58),fill=GOLD,width=3);dd.line((846,45,859,58,846,71),fill=GOLD,width=3)
    place(im,cta,(75,1607+40*(1-out((t-1)/.7))),out((t-1)/.6))
    # One quiet moving highlight, then a stable hold for reading and action.
    if 1.7<t<2.6:
        p=(t-1.7)/.9;x=75+int(930*p);d.line((x,1741,min(1005,x+90),1741),fill=GOLD,width=4)
    return im

FUNCS=[intro,lambda t,a:operation(0,t,a),lambda t,a:operation(1,t,a),lambda t,a:operation(2,t,a),bridge,ending]
def transition(old,new,p,index):
    if index==0:
        pp=smooth(p);x0=80*(1-pp);y0=842*(1-pp);x1=1000+(W-1000)*pp;y1=1600+(H-1600)*pp
        mask=Image.new('L',(W,H));ImageDraw.Draw(mask).rounded_rectangle((x0,y0,x1,y1),radius=int(47*(1-pp)),fill=255)
        return Image.composite(new,old,mask)
    if index in (1,2):
        pp=smooth(p);edge=-H*.16+(W+H*.16+120)*pp
        mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
        md.polygon([(0,0),(edge,0),(edge-H*.16,H),(0,H)],fill=255)
        mask=mask.filter(ImageFilter.GaussianBlur(5))
        im=Image.composite(new,old,mask)
        if .03<p<.97:
            d=ImageDraw.Draw(im);d.line((edge,0,edge-H*.16,H),fill=GOLD,width=9)
        return im
    if index==3:
        pp=smooth(p);y=H-int(H*pp);outim=old.copy();outim.paste(new.crop((0,y,W,H)),(0,y))
        ImageDraw.Draw(outim).rectangle((0,y,W,min(H,y+8)),fill=GOLD);return outim
    # Final paper reveal uses the same circular geometry as the logo landing.
    pp=smooth(p);r=2350*pp
    mask=Image.new('L',(W,H));ImageDraw.Draw(mask).ellipse((540-r,630-r,540+r,630+r),fill=255)
    return Image.composite(new,old,mask)

def render():
    print('Voice-led edit points:',[round(x,2) for x in STARTS],flush=True)
    enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(O/'picture_v2.mp4')],stdin=subprocess.PIPE)
    for n in range(DURATION*FPS):
        t=n/FPS;i=max(k for k,s in enumerate(STARTS) if t>=s)
        im=FUNCS[i](t-STARTS[i]+(.5 if i else 0),t)
        if i<5 and t>=STARTS[i+1]-.5:
            nt=t-(STARTS[i+1]-.5);nextim=FUNCS[i+1](nt,t)
            im=transition(im,nextim,nt/.5,i)
        if n in [50,140,270,398,510,635,785,890]:im.convert('RGB').resize((360,640)).save(O/f'v2-{n:04d}.jpg')
        enc.stdin.write(im.convert('RGB').tobytes())
        if n%90==0:print(f'{t:.0f}s / {DURATION}s',flush=True)
    enc.stdin.close();rc=enc.wait()
    for rr in readers.values():rr.p.terminate()
    if rc:raise RuntimeError('Render failed')
    (ROOT/'timing_v2.json').write_text(json.dumps({'duration':DURATION,'voice_offset':DELAY,'voice_speed':SPEED,'scene_starts':STARTS,'words':WORDS},ensure_ascii=False,indent=2))

def mix():
    # Narration drives a sidechain compressor so music breathes around the voice.
    inp=['ffmpeg','-y','-v','error','-i',str(O/'picture_v2.mp4'),'-i',str(A/'narracao_v2.mp3'),'-i',str(A/'music.mp3'),'-i',str(A/'notification.mp3'),'-i',str(A/'whoosh.mp3'),'-i',str(A/'chime.mp3'),'-i',str(A/'impact.mp3')]
    filt=f'[1:a]atempo={SPEED},loudnorm=I=-16:TP=-1.5:LRA=8,adelay=550|550,apad,atrim=0:{DURATION},aformat=channel_layouts=stereo,asplit=2[v][side];[2:a]atrim=0:{DURATION},afade=t=in:d=0.4,afade=t=out:st=29:d=2,volume=.25[m];[m][side]sidechaincompress=threshold=.025:ratio=5:attack=10:release=280[duck];[3:a]volume=.16,adelay=1180|1180[ding];[4:a]asplit=5[w0][w1][w2][w3][w4];'
    for i,st in enumerate(STARTS[1:]):
        ms=round((st-.5)*1000);filt+=f'[w{i}]atrim=0:1.0,volume=.11,adelay={ms}|{ms}[sw{i}];'
    filt+='[5:a]volume=.065,adelay=24700|24700[ch];[6:a]atrim=0:1.5,volume=.055,adelay=200|200[hit];[v][duck][ding][sw0][sw1][sw2][sw3][sw4][ch][hit]amix=inputs=10:duration=first:normalize=0,alimiter=limit=.91:level=0[a]'
    subprocess.run(inp+['-filter_complex',filt,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(DURATION),'-movflags','+faststart',str(O/'video_pronto_bm_v2.mp4')],check=True)
if __name__=='__main__':render();mix()
