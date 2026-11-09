"""Boa Mesa editorial film: original proposal artwork, real footage, voice-led type.
No clocks, playback indicators, step numbers or generated operational imagery.
"""
from pathlib import Path
from functools import lru_cache
import json,re,math,subprocess,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter

R=Path(__file__).resolve().parent;A=R/'assets';O=R/'renders';O.mkdir(exist_ok=True)
W,H,FPS,DURATION=1080,1920,30,47
IVORY='#f7f0e5';WINE='#641014';INK='#341312';GOLD='#f6b43c';WHITE='#ffffff';OFFSET=.35
if (R/'assets_v3.zip').exists():
    with zipfile.ZipFile(R/'assets_v3.zip') as z:
        for name in z.namelist():
            if '/' not in name and not (A/name).exists():(A/name).write_bytes(z.read(name))
al=json.loads((R/'alignment_v3.json').read_text());al=al.get('normalized_alignment') or al['alignment']
speech=''.join(al['characters'])
def cue(phrase,last=False):
    i=speech.rfind(phrase) if last else speech.find(phrase)
    if i<0:raise ValueError(phrase)
    return OFFSET+al['character_start_times_seconds'][i]
S=[0,cue('Para empresas'),cue('Aqui'),cue('Cada pedido'),cue('Da montagem'),cue('entrega rápida'),cue('Solicite')]
GALLERY=[0,2.54,5.08,7.62,cue('E kits')]
def clamp(x):return min(1,max(0,x))
def ease(x):x=clamp(x);return 1-(1-x)**4
def sine(x):return .5-.5*math.cos(math.pi*clamp(x))
@lru_cache(100)
def font(sz,serif=False,bold=True):return ImageFont.truetype(str(A/('Display-Serif.ttf' if serif else 'Inter-Bold.ttf' if bold else 'Inter-Regular.ttf')),sz)
def paste(im,layer,xy,alpha=1):
    if alpha<=0:return
    if alpha<1:
        layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda v:round(v*alpha)))
    im.alpha_composite(layer,(round(xy[0]),round(xy[1])))
@lru_cache(300)
def textimage(text,size,color=INK,serif=False,bold=True,width=940):
    f=font(size,serif,bold);lines=[];line=''
    for word in text.split():
        test=(line+' '+word).strip()
        if f.getlength(test)>width and line:lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    im=Image.new('RGBA',(width,math.ceil(len(lines)*size*1.18+size*.35)));d=ImageDraw.Draw(im)
    for i,line in enumerate(lines):d.text((0,i*size*1.18),line,font=f,fill=color)
    return im
def text(im,text,xy,size,color=INK,serif=False,bold=True,width=940):paste(im,textimage(text,size,color,serif,bold,width),xy)
def typeline(im,words,xy,size,t,start,color=WHITE,serif=True,highlight=None):
    """Words reveal upward through their own baseline masks, then settle precisely."""
    f=font(size,serif);x=xy[0]
    for i,word in enumerate(words.split()):
        p=ease((t-start-i*.055)/.52);ww=math.ceil(f.getlength(word+' '))+6;hh=math.ceil(size*1.5)
        layer=Image.new('RGBA',(ww,hh));d=ImageDraw.Draw(layer)
        d.text((0,(1-p)*(size+16)),word,font=f,fill=GOLD if highlight and word.strip('.,') in highlight else color)
        paste(im,layer,(x,xy[1]),p);x+=f.getlength(word+' ')
def headline(im,l1,l2,t,start,xy=(76,1190),size=111,color=WHITE,accent=True):
    typeline(im,l1,xy,size,t,start,color,True)
    typeline(im,l2,(xy[0],xy[1]+size*1.08),size,t,start+.12,GOLD if accent else color,True)
def underline(im,xy,width,t,start,color=GOLD):
    p=ease((t-start)/.55)
    if p:
        d=ImageDraw.Draw(im);end=xy[0]+width*p
        d.line((xy[0],xy[1],end,xy[1]-3),fill=color,width=7)
def wraplines(text_,size,maxwidth,serif=False):
    f=font(size,serif);lines=[];line=''
    for word in text_.split():
        if f.getlength((line+' '+word).strip())>maxwidth and line:lines.append(line);line=word
        else:line=(line+' '+word).strip()
    if line:lines.append(line)
    return lines

logo=Image.open(A/'logo_site.png').convert('RGBA');bbox=logo.getchannel('A').getbbox();logo=logo.crop(bbox)
def logofit(w):return logo.resize((w,round(w*logo.height/logo.width)),Image.Resampling.LANCZOS)
LOGO=logofit(600)
@lru_cache(1)
def shade():
    ar=np.zeros((H,W,4),np.uint8);ar[:,:,:3]=[20,8,8]
    ar[:,:,3]=np.clip((np.arange(H)[:,None]-900)/780,0,.91)*255
    return Image.fromarray(ar)
def wordmark(im,color=WHITE):
    text(im,'Boa Mesa',(76,128),40,color,True)
    text(im,'CESTA BÁSICA',(77,178),20,color,False,False)

POSTER_NAMES=['proposta_01.png','proposta_02.png','proposta_03.png','proposta_04.png','kit_limpeza.png']
POSTERS=[Image.open(A/n).convert('RGBA').resize((790,1405),Image.Resampling.LANCZOS) for n in POSTER_NAMES]
SHADOW=Image.new('RGBA',(850,1465));ImageDraw.Draw(SHADOW).rectangle((30,28,820,1435),fill=(65,28,13,50));SHADOW=SHADOW.filter(ImageFilter.GaussianBlur(15))
def poster(im,i,x,y=300):
    paste(im,SHADOW,(x-30,y-20));paste(im,POSTERS[i],(x,y))
def gallery(t):
    im=Image.new('RGBA',(W,H),IVORY)
    # The originals move as printed editorial pages: no image deformation or rewrites.
    i=max(k for k,st in enumerate(GALLERY) if t>=st)
    if i<4 and t>=GALLERY[i+1]-.65:
        p=sine((t-GALLERY[i+1]+.65)/.65);poster(im,i,145-1080*p);poster(im,i+1,145+1080*(1-p))
    else:poster(im,i,145,300+18*(1-ease(t/.55)) if i==0 else 300)
    if t<cue('Para quem'):
        title='Para sua casa.';start=0
    elif t<cue('Boa Mesa'):
        title='Para sua equipe.';start=cue('Para quem')
    elif t<cue('essencial'):
        title='Diferentes propostas.';start=cue('Boa Mesa')
    elif t<cue('E kits'):
        title='Do essencial ao mais completo.';start=cue('essencial')
    else:title='Limpeza para sua rotina.';start=cue('E kits')
    lines=wraplines(title,78,940,True)
    for k,line in enumerate(lines):typeline(im,line,(73,98+k*84),78,t,start+k*.07,WINE,True)
    text(im,'boamesacestabasica.com.br',(271,1777),26,WINE,False,False,width=850)
    return im

class Reader:
    def __init__(self,name,offset):
        self.p=subprocess.Popen(['ffmpeg','-v','fatal','-threads','2','-ss',str(offset),'-i',str(A/name),'-an','-vf','fps=30,scale=1080:1920:flags=lanczos','-threads','2','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
        self.last=None
    def read(self):
        b=self.p.stdout.read(W*H*3)
        if len(b)==W*H*3:self.last=Image.frombytes('RGB',(W,H),b).convert('RGBA')
        if self.last is None:raise RuntimeError('Original footage did not decode')
        return self.last.copy()
readers={}
def filmed(id_,name,offset):
    if id_ not in readers:readers[id_]=Reader(name,offset)
    im=readers[id_].read();im.alpha_composite(shade());wordmark(im);return im
def pat(t):
    im=filmed('pat','producao.mp4',8)
    if t<cue('fornecedor'):
        headline(im,'Sua empresa,','bem atendida.',t,S[1],xy=(76,1160),size=106)
        text(im,'Cestas para colaboradores',(80,1435),43,WHITE,False,False,width=900)
    else:
        typeline(im,'Fornecedor registrado',(76,1107),71,t,cue('fornecedor'),WHITE,True)
        typeline(im,'PAT',(69,1180),212,t,cue('registrado'),GOLD,True)
        text(im,'Programa de Alimentação do Trabalhador',(79,1465),40,WHITE,False,False,width=850)
        text(im,'Registro FO002424',(79,1603),28,WHITE,False,False)
    return im

def bubble(message,width,bg,fg):
    f=font(42,False,False);lines=wraplines(message,42,width-82)
    hh=round(len(lines)*55+62);im=Image.new('RGBA',(width,hh));d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,width,hh),radius=18,fill=bg)
    for i,line in enumerate(lines):d.text((39,25+i*55),line,font=f,fill=fg)
    return im
CLIENT=bubble('Olá! Vi seu anúncio de cestas básicas e gostaria de mais informações',910,IVORY,INK)
ANSWER=bubble('Olá! Vamos encontrar a melhor proposta para você.',780,'#dfeada',INK)
def contact(t):
    im=Image.new('RGBA',(W,H),WINE);wordmark(im)
    if t<cue('humanizado'):
        headline(im,'De pessoa','para pessoa.',t,S[2],xy=(76,352),size=119,color=IVORY,accent=False)
    else:
        headline(im,'Humanizado.','E rápido.',t,cue('humanizado'),xy=(76,352),size=119,color=IVORY)
        underline(im,(81,625),477,t,cue('rápido'))
    text(im,'ATENDIMENTO PELO WHATSAPP',(78,775),28,IVORY,False,False)
    pp=ease((t-(S[2]+.35))/.65);paste(im,CLIENT,(75+110*(1-pp),855+45*(1-pp)),pp)
    pp=ease((t-(S[2]+1.75))/.65);paste(im,ANSWER,(225-80*(1-pp),1225+40*(1-pp)),pp)
    return im
def preparation(t):
    im=filmed('quality','producao.mp4',.5)
    if t<cue('qualidade'):
        headline(im,'Preparado','com cuidado.',t,S[3],size=118)
        underline(im,(82,1460),570,t,cue('cuidado'))
    elif t<cue('atenção'):
        headline(im,'Qualidade','nos materiais.',t,cue('qualidade'),size=113)
    else:headline(im,'Atenção','aos detalhes.',t,cue('atenção'),size=118)
    return im
def stock(t):
    im=filmed('stock','estoque.mp4',.15)
    headline(im,'Tudo','organizado.',t,S[4],size=125)
    return im
def loading(t):
    im=filmed('load','carregamento.mp4',0)
    if t<cue('Boa Mesa Cesta Básica',True):
        headline(im,'Entrega','rápida.',t,S[5],size=136)
        underline(im,(82,1505),385,t,S[5]+.55)
        if t>cue('condições'):
            text(im,'Condições combinadas no atendimento.',(82,1567),34,WHITE,False,False,width=880)
    else:headline(im,'Boa Mesa','Cesta Básica.',t,cue('Boa Mesa Cesta Básica',True),size=117,accent=False)
    return im
def ending(t):
    im=Image.new('RGBA',(W,H),IVORY)
    pp=ease((t-S[6])/.75)
    paste(im,LOGO,((W-LOGO.width)/2,222+38*(1-pp)),pp)
    headline(im,'Solicite','sua cotação.',t,S[6],xy=(77,947),size=139,color=WINE,accent=False)
    underline(im,(83,1271),750,t,S[6]+.65,WINE)
    typeline(im,'Escolha sua proposta.',(79,1347),62,t,cue('escolha'),WINE,True)
    text(im,'boamesacestabasica.com.br',(80,1534),37,WINE,False,False,width=930)
    text(im,'WhatsApp  (17) 98159-2950',(81,1610),35,WINE,False,False,width=920)
    return im

FUNCS=[gallery,pat,contact,preparation,stock,loading,ending]
def push(old,new,p,direction):
    """Adjacent moving planes; text from different scenes never crossfades together."""
    pp=sine(p);im=Image.new('RGBA',(W,H),IVORY)
    if direction=='x':
        x=round(pp*W);paste(im,old,(-x,0));paste(im,new,(W-x,0))
    else:
        y=round(pp*H);paste(im,old,(0,-y));paste(im,new,(0,H-y))
    return im
def render():
    enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','15','-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(O/'picture_v3.mp4')],stdin=subprocess.PIPE)
    print('Scene cues',S,flush=True)
    for n in range(DURATION*FPS):
        t=n/FPS;i=max(k for k,s in enumerate(S) if t>=s);im=FUNCS[i](t)
        if i<6 and t>=S[i+1]-.44:
            im=push(im,FUNCS[i+1](t),(t-S[i+1]+.44)/.44,'x' if i in(0,2,5) else 'y')
        if n in[30,110,195,264,352,465,558,657,724,806,871,981,1090,1179,1326]:
            im.convert('RGB').resize((360,640)).save(O/f'v3-{n:04d}.jpg')
        enc.stdin.write(im.convert('RGB').tobytes())
        if n%120==0:print(f'{t:.0f}s / {DURATION}s',flush=True)
    enc.stdin.close();rc=enc.wait()
    for reader in readers.values():reader.p.terminate()
    if rc:raise RuntimeError('Encoder failed')
    words=[]
    for m in re.finditer(r'\S+',speech):words.append({'text':m.group(),'start':OFFSET+al['character_start_times_seconds'][m.start()],'end':OFFSET+al['character_end_times_seconds'][m.end()-1]})
    (R/'timing_v3.json').write_text(json.dumps({'duration':DURATION,'offset':OFFSET,'scene_starts':S,'gallery_starts':GALLERY,'words':words},ensure_ascii=False,indent=2))
def mix():
    if not (A/'music_v3.wav').exists():
        f='[0:a]asplit=3[a][b][c];[a]atrim=0:21.4286,asetpts=PTS-STARTPTS[a1];[b]atrim=8.5714:25.7143,asetpts=PTS-STARTPTS[b1];[c]atrim=25.5:35,asetpts=PTS-STARTPTS[c1];[a1][b1]acrossfade=d=0.5357:c1=qsin:c2=qsin[ab];[ab][c1]acrossfade=d=0.5357:c1=qsin:c2=qsin[out]'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(A/'music.mp3'),'-filter_complex',f,'-map','[out]','-ac','2','-ar','48000',str(A/'music_v3.wav')],check=True)
    inputs=['ffmpeg','-y','-v','error','-i',str(O/'picture_v3.mp4')]
    for n in ['narracao_v3.mp3','music_v3.wav','notification.mp3','whoosh.mp3','chime.mp3','click_soft.mp3','producao.mp4','estoque.mp4','carregamento.mp4']:inputs+=['-i',str(A/n)]
    f=f'[1:a]loudnorm=I=-16:TP=-1.5:LRA=8,adelay=350|350,apad,atrim=0:{DURATION},aformat=channel_layouts=stereo,asplit=2[v][side];[2:a]atrim=0:{DURATION},afade=t=in:d=0.4,afade=t=out:st=44:d=3,volume=0.28[m];[m][side]sidechaincompress=threshold=0.027:ratio=5:attack=8:release=330[duck];[3:a]volume=0.11,adelay=20900|20900[notification];'
    changes=GALLERY[1:]+S[1:];count=len(changes)
    f+='[4:a]asplit='+str(count)+''.join(f'[w{i}]'for i in range(count))+';'
    for i,st in enumerate(changes):
        ms=round(max(0,st-.5)*1000);speed=1.1 if i%2 else .92
        f+=f'[w{i}]atrim=0:0.75,atempo={speed},volume=0.052,adelay={ms}|{ms}[sw{i}];'
    f+='[5:a]atrim=0:1.6,volume=0.055,adelay=41100|41100[chime];[6:a]asplit=4[c0][c1][c2][c3];'
    for i,st in enumerate(GALLERY[1:]):
        ms=round(st*1000);f+=f'[c{i}]volume=0.12,adelay={ms}|{ms}[click{i}];'
    amb=[(7,.5,S[3],5.5,.025),(8,.15,S[4],3.2,.025),(9,0,S[5],6.05,.055)]
    for i,(idx,trim,st,dur,gain) in enumerate(amb):
        ms=round(st*1000);f+=f'[{idx}:a]atrim=start={trim}:duration={dur},asetpts=PTS-STARTPTS,highpass=f=150,lowpass=f=2500,afade=t=in:d=0.2,afade=t=out:st={dur-.3}:d=0.3,volume={gain},adelay={ms}|{ms}[amb{i}];'
    tracks=['v','duck','notification','chime']+[f'sw{i}'for i in range(count)]+[f'click{i}'for i in range(4)]+[f'amb{i}'for i in range(3)]
    f+=''.join('['+n+']'for n in tracks)+f'amix=inputs={len(tracks)}:duration=first:normalize=0,alimiter=limit=0.91:level=0[a]'
    subprocess.run(inputs+['-filter_complex',f,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-t',str(DURATION),'-movflags','+faststart',str(O/'video_pronto_bm_v3.mp4')],check=True)
if __name__=='__main__':render();mix()
