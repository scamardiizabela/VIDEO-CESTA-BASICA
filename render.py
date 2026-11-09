"""Boa Mesa: deterministic 35s editorial composition. Pillow + FFmpeg.
Original footage remains unchanged; the compositor resizes proportionally.
"""
from pathlib import Path
import subprocess, math, json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parent
A=ROOT/'assets'; OUT=ROOT/'renders'; OUT.mkdir(exist_ok=True)
W,H,FPS,DURATION=1080,1920,30,35
RED='#991c25'; GOLD='#ffbd28'; PAPER='#fffaf2'; INK='#2b2020'
FONT={}
def font(size,bold=False):
    key=(size,bold)
    if key not in FONT: FONT[key]=ImageFont.truetype(str(A/('bold.ttf' if bold else 'regular.ttf')),size)
    return FONT[key]
def ease(x): return 1-(1-min(1,max(0,x)))**3
def wrap(text,f,width):
    lines=[]; line=''
    for word in text.split():
        test=(line+' '+word).strip()
        if f.getlength(test)>width and line: lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    return lines
def textblock(text,size,width,color,bold=False,spacing=1.18):
    f=font(size,bold); lines=wrap(text,f,width)
    im=Image.new('RGBA',(width,int(size*spacing*len(lines)+size*.3)))
    d=ImageDraw.Draw(im)
    for i,line in enumerate(lines): d.text((0,i*size*spacing),line,font=f,fill=color)
    return im
def paste(im,layer,xy,alpha=1):
    if alpha<=0: return
    if alpha<1:
        layer=layer.copy(); layer.putalpha(layer.getchannel('A').point(lambda v:int(v*alpha)))
    im.alpha_composite(layer,(int(xy[0]),int(xy[1])))
def reveal(im,layer,xy,t,delay=0,dur=.7,shift=55):
    p=ease((t-delay)/dur); paste(im,layer,(xy[0],xy[1]+shift*(1-p)),p)
logo=Image.open(A/'logo.jpg').convert('RGBA')
def fitlogo(width):
    return logo.resize((width,round(width*logo.height/logo.width)),Image.Resampling.LANCZOS)

# All graphic elements remain inside Reels safe margins (78px lateral, 180px bottom).
brand=textblock('BOA MESA  /  CESTA BÁSICA',27,900,PAPER,True)
introtitle=textblock('1. Você solicita sua cotação e confirma o pedido conosco',64,900,PAPER,True)
stages=[
    ('2. Nossa equipe inicia a preparação do seu pedido','Organização e cuidado em cada etapa','02  /  PREPARAÇÃO'),
    ('3. Tudo organizado para a próxima etapa','Seu pedido preparado com atenção','03  /  ORGANIZAÇÃO'),
    ('4. Pedido pronto! Hora de seguir viagem','Da nossa equipe até você, com compromisso e responsabilidade','04  /  CARREGAMENTO')
]
stages=[(textblock(a,67,900,PAPER,True),textblock(b,35,880,PAPER),textblock(c,28,900,GOLD,True)) for a,b,c in stages]
gradient=Image.new('RGBA',(W,H)); ga=np.zeros((H,W,4),np.uint8); ga[:,:,:3]=[29,17,19]
ga[:,:,3]=np.clip((np.arange(H)[:,None]-990)/660,0,.94)*255
gradient=Image.fromarray(ga)
footer=textblock('ATENDIMENTO • CUIDADO • COMPROMISSO',25,900,PAPER,True)

def intro(t):
    im=Image.new('RGBA',(W,H),RED); d=ImageDraw.Draw(im)
    # A restrained gold arc gives the opening depth without competing with copy.
    d.arc((640,-290,1440,510),0,360,fill='#ae3339',width=3)
    d.rounded_rectangle((78,174,304,368),radius=22,fill='white')
    reveal(im,fitlogo(204),(89,181),t,.08,.6,24)
    reveal(im,textblock('DO PRIMEIRO OLÁ AO SEU PEDIDO',25,900,GOLD,True),(78,410),t,.12)
    reveal(im,introtitle,(78,468),t,.18,.8)
    # Highlight semantic words with a gold rule, then the full readable headline stays.
    d.rounded_rectangle((78,806,78+int(160*ease((t-.6)/.6)),812),radius=3,fill=GOLD)
    phone=Image.new('RGBA',(W,760)); p=ImageDraw.Draw(phone)
    p.rounded_rectangle((106,18,974,705),radius=52,fill=(50,4,9,60))
    p.rounded_rectangle((92,0,960,687),radius=48,fill='#f4eee5',outline='#fefdf9',width=10)
    p.rounded_rectangle((102,10,950,152),radius=40,fill='#075e54')
    p.rectangle((102,90,950,152),fill='#075e54')
    p.ellipse((139,42,211,114),fill='#e2ede6')
    p.ellipse((165,54,185,74),fill='#57766b'); p.ellipse((155,78,195,106),fill='#57766b')
    p.text((240,39),'Cliente',font=font(37,True),fill='white')
    p.text((240,88),'WhatsApp',font=font(25),fill='#dcebe5')
    if t<1.45:
        p.rounded_rectangle((139,218,339,296),radius=18,fill='white')
        for j in range(3):
            yy=255-int(4*math.sin(t*8+j)); p.ellipse((176+j*42,yy-7,190+j*42,yy+7),fill='#9dafa8')
    else:
        message='Olá! Vi seu anúncio de cestas básicas e gostaria de mais informações'
        n=min(len(message),max(1,int((t-1.45)*49)))
        p.rounded_rectangle((139,208,904,480),radius=22,fill='white')
        p.polygon([(139,223),(120,211),(139,249)],fill='white')
        msg=textblock(message[:n],39,676,INK)
        phone.alpha_composite(msg,(174,235))
        p.text((788,430),'09:41',font=font(22),fill='#6d7471')
    p.rounded_rectangle((139,559,906,640),radius=40,fill='white')
    p.text((178,574),'Mensagem',font=font(30),fill='#78857e')
    reveal(im,phone,(0,884),t,.3,.8,100)
    reveal(im,textblock('01  /  ATENDIMENTO',27,900,GOLD,True),(78,1675),t,.7)
    return im

class Reader:
    def __init__(self,path,offset=0,slow=1):
        self.p=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-ss',str(offset),'-i',str(path),'-an','-vf',f'setpts={slow}*PTS,fps=30,scale=1080:1920:flags=lanczos','-threads','2','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
        self.last=None
    def next(self):
        b=self.p.stdout.read(W*H*3)
        if len(b)==W*H*3: self.last=Image.frombytes('RGB',(W,H),b).convert('RGBA')
        if self.last is None: raise RuntimeError('Cannot decode original source')
        return self.last.copy()
readers={}
def operation(i,t):
    if i not in readers:
        readers[i]=Reader(A/['producao.mp4','estoque.mp4','carregamento.mp4'][i], [.6,0,0][i],1.12 if i==2 else 1)
    im=readers[i].next(); im.alpha_composite(gradient)
    badge=Image.new('RGBA',(W,84)); bd=ImageDraw.Draw(badge)
    bd.rounded_rectangle((78,0,791,72),radius=36,fill=(112,18,27,232))
    badge.alpha_composite(brand,(108,17))
    reveal(im,badge,(0,184),t,.06,.55,25)
    head,sub,label=stages[i]
    reveal(im,label,(78,1232),t,.15,.6,25)
    reveal(im,head,(78,1300),t,.25,.7,55)
    reveal(im,sub,(78,1300+head.height+30),t,.48,.65,34)
    d=ImageDraw.Draw(im); d.rounded_rectangle((78,1734,970,1740),radius=3,fill=(255,255,255,50))
    count=3; dur=[9,8,7][i]; progress=min(1,max(0,t/dur))
    d.rounded_rectangle((78,1734,78+int(892*((i+progress)/count)),1740),radius=3,fill=GOLD)
    return im

endtitle=textblock('Solicite sua cotação e faça seu pedido',63,870,RED,True)
site=textblock('boamesacestabasica.com.br',38,930,INK,True)
def ending(t):
    im=Image.new('RGBA',(W,H),PAPER); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,28),fill=GOLD)
    reveal(im,textblock('DA NOSSA EQUIPE ATÉ VOCÊ',27,900,RED,True),(78,224),t,.12)
    d.rounded_rectangle((135,407,945,1113),radius=48,fill='white')
    reveal(im,fitlogo(724),(178,449),t,.18,.8,65)
    reveal(im,endtitle,(105,1215),t,.45,.8,48)
    reveal(im,site,(105,1463),t,.75,.65,30)
    d.rounded_rectangle((105,1594,975,1694),radius=50,fill=RED)
    reveal(im,textblock('FALE COM A BOA MESA',31,810,'white',True),(176,1620),t,.9,.6,16)
    if t>4.5:
        im=Image.blend(im,Image.new('RGBA',(W,H),PAPER),min(.18,(t-4.5)*.36))
    return im

def render():
    starts=[0,6,15,23,30]; funcs=[intro,lambda t:operation(0,t),lambda t:operation(1,t),lambda t:operation(2,t),ending]
    enc=subprocess.Popen(['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(OUT/'picture.mp4')],stdin=subprocess.PIPE)
    for n in range(DURATION*FPS):
        t=n/FPS; idx=max(i for i,s in enumerate(starts) if t>=s)
        im=funcs[idx](t-starts[idx]+(.4 if idx else 0))
        # Incoming scene begins just before each boundary; a warm cross dissolve preserves motion continuity.
        if idx<4 and t>=starts[idx+1]-.4:
            nt=t-(starts[idx+1]-.4)
            nxt=funcs[idx+1](nt)
            im=Image.blend(im,nxt,ease(nt/.4))
        if n in [90,255,540,780,975]: im.convert('RGB').resize((360,640)).save(OUT/f'frame-{n:04d}.jpg')
        enc.stdin.write(im.convert('RGB').tobytes())
        if n%90==0: print(f'{t:.0f}s / 35s',flush=True)
    enc.stdin.close()
    if enc.wait(): raise RuntimeError('Encode failed')
    for reader in readers.values(): reader.p.terminate()
    print('Picture completed',flush=True)
if __name__=='__main__': render()
