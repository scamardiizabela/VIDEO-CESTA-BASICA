"""V5 refinement: products only in the quick proposal passage; seamless brand ending."""
import sys,math,json,subprocess
from functools import lru_cache
import render_v4 as v
from PIL import Image,ImageDraw,ImageFilter
W,H,FPS,D=v.W,v.H,v.FPS,v.D
S,C,R,A,O=v.S,v.C,v.R,v.A,v.O

def kinetic(im,s,x,y,size,t,start,color,maxw=930):
    """Tracked letter reveal with damped settle and precise final baseline."""
    f=v.font(size);width=f.getlength(s);scale=min(1,maxw/max(1,width));xx=x
    for i,c in enumerate(s):
        p=v.out((t-start-i*.025)/.48)
        if p:
            tile=v.txt(c,size,color)
            if scale<1:tile=tile.resize((max(1,round(tile.width*scale)),max(1,round(tile.height*scale))),Image.Resampling.LANCZOS)
            dy=55*(1-p);v.paste(im,tile,xx,y+dy,p)
        xx+=f.getlength(c)*scale

def hook(t):
    im=v.stage(t)
    if t<v.cue('Mais qualidade'):
        v.reveal(im,'SUA COMPRA',77,443,133,t,.14)
        kinetic(im,'MERECE',70,604,245,t,.3,C['cream'])
        v.reveal(im,'MAIS.',64,839,370,t,.65,C['gold'],'scale')
        v.underline(im,80,1202,830,t,.9)
    else:
        if t<v.cue('Mais escolha'):word='QUALIDADE';st=v.cue('Mais qualidade')
        elif t<v.cue('Mais cuidado'):word='ESCOLHA';st=v.cue('Mais escolha')
        else:word='CUIDADO';st=v.cue('Mais cuidado')
        v.reveal(im,'MAIS',76,503,225,t,st)
        kinetic(im,word,73,740,239,t,st+.035,C['gold'])
        v.underline(im,80,1002,870,t,st+.22)
        # A typographic echo grows behind the lead without competing with it.
        p=v.out((t-st)/.6)
        v.text(im,'BOA MESA',79,1150+30*(1-p),72,C['cream'],False,alpha=p)
    v.text(im,'CESTAS BÁSICAS  •  KITS DE LIMPEZA',80,1655,32,C['cream'],False,maxw=930)
    return im

def audiences(t):
    # Real operation replaces the floating cutout photographs in the introduction.
    im=v.real('producao.mp4',3+t-S[1],t)
    tint=Image.new('RGBA',(W,H),(48,3,13,100));im.alpha_composite(tint)
    home=t<v.cue('sua empresa')-.1;st=S[1] if home else v.cue('sua empresa')-.1
    v.lines(im,['PARA SUA','CASA.' if home else 'EMPRESA.'],t,st,y=1100,size=213,accent=1)
    v.underline(im,80,1510,790,t,st+.26)
    return im

def cleaning(t):
    # The fifth original joins the same camera language as the quick basket proposals.
    im=v.stage(t,1);p=v.out((t-S[3])/.65)
    v.reveal(im,'COMPLETE O CUIDADO.',76,306,132,t,S[3],C['gold'])
    v.project(im,v.POST[4],540+600*(1-p),1080+20*(1-p),1160+25*math.sin((t-S[3])*.7),-24*(1-p),-3*(1-p))
    v.reveal(im,'KIT DE LIMPEZA',78,1748,58,t,S[3]+.25)
    return im

def pat(t):
    im=v.stage(t)
    v.text(im,'SOLUÇÕES PARA EMPRESAS',78,313,35,C['cream'],False)
    v.reveal(im,'SUA EQUIPE',72,410,162,t,S[4])
    v.reveal(im,'BEM CUIDADA.',72,558,162,t,S[4]+.15,C['gold'])
    kinetic(im,'PAT',72,882,315,t,v.cue('fornecedor'),C['gold'])
    v.text(im,'Fornecedor registrado',80,1245,48,C['cream'],False,maxw=900)
    v.text(im,'Programa de Alimentação do Trabalhador',80,1334,34,C['cream'],False,maxw=910)
    v.underline(im,80,1450,870,t,v.cue('PAT'))
    v.text(im,'Registro FO002424',80,1516,29,C['cream'],False,maxw=900)
    return im

@lru_cache(1)
def endbase():
    im=Image.new('RGBA',(W,H),C['cream']);d=ImageDraw.Draw(im)
    d.polygon([(980,0),(1080,0),(1080,850),(965,1190)],fill='#f4e5cc')
    d.polygon([(0,1490),(83,1710),(151,1920),(0,1920)],fill='#f1dfbe')
    return im

def closing(t):
    im=endbase().copy();entrance=v.out((t-S[9])/.85)
    settle=v.smooth((t-(S[10]-.35))/.9)
    maxw=760-145*settle;maxh=675-185*settle
    sc=min(maxw/v.logo.width,maxh/v.logo.height)*(.95+.05*entrance)
    lg=v.logo.resize((round(v.logo.width*sc),round(v.logo.height*sc)),Image.Resampling.LANCZOS)
    cy=755-250*settle+45*(1-entrance)
    v.paste(im,lg,(W-lg.width)/2,cy-lg.height/2,entrance)
    if t<S[10]:
        alpha=entrance*(1-settle)
        v.text(im,'MAIS QUALIDADE. MAIS CUIDADO.',92,1260,44,C['wine'],False,maxw=900,alpha=alpha)
    if t>=S[10]-.05:
        # Wine text remains high contrast on the continuous ivory canvas.
        v.reveal(im,'ESCOLHA A SUA.',76,942,153,t,S[10],C['wine'])
        kinetic(im,'PEÇA AGORA.',76,1080,153,t,S[10]+.075,C['wine'])
        v.underline(im,80,1240,850,t,S[10]+.3)
        pp=v.out((t-S[10]-.35)/.6);box=Image.new('RGBA',(920,166));bd=ImageDraw.Draw(box)
        bd.rounded_rectangle((0,0,919,165),radius=38,fill='#159954')
        v.text(box,'CHAME NO WHATSAPP',54,43,67,'#ffffff',True,maxw=820)
        v.paste(im,box,80,1340+45*(1-pp),pp)
    v.text(im,'(17) 98159-2950',80,1564,51,C['wine'],False,maxw=920,alpha=entrance)
    v.text(im,'(17) 99622-0624',80,1621,51,C['wine'],False,maxw=920,alpha=entrance)
    v.text(im,'boamesacestabasica.com.br',80,1670,36,C['wine'],False,maxw=920,alpha=entrance)
    return im

# Keep the approved gallery, narration, operation footage and timeline intact.
v.FUN=[hook,audiences,v.proposals,cleaning,pat,v.contact,v.prep,v.stock,v.loading,closing,closing]
def render():
    # Fragment the intermediate so its stream metadata is written before media data.
    # The final deliverable is remuxed as a standard fast-start MP4 by mix_v4.
    cmd=['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','15','-pix_fmt','yuv420p','-threads','4','-movflags','+frag_keyframe+empty_moov+default_base_moof',str(O/'picture_v5.mp4')]
    enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(D*FPS):
        t=n/FPS;im=v.renderframe(t)
        if n%15==0:im.convert('RGB').resize((270,480)).save(O/f'v5-{n:04d}.jpg')
        enc.stdin.write(im.convert('RGB').tobytes())
        if n%120==0:print(f'{t:.0f}/{D}s',flush=True)
    enc.stdin.close()
    if enc.wait():raise RuntimeError('Encode failed')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(O/'picture_v5.mp4')]))
    if abs(float(info['format']['duration'])-D)>.05:raise RuntimeError('Incomplete picture stream')
    (R/'timing_v5.json').write_text(json.dumps({'duration':D,'scene_starts':S,'voice_offset':.25,'proposal_sequence':[S[2],S[4]]},indent=2))
    for reader in v.FILM.values():
        if reader.p:reader.p.terminate()
if __name__=='__main__':
    if '--frames' in sys.argv:
        for t in map(float,sys.argv[sys.argv.index('--frames')+1:]):v.renderframe(t).convert('RGB').resize((540,960)).save(O/f'v5-review-{t:g}.jpg')
    else:
        render()
        from mix_v4 import mix
        mix('picture_v5.mp4','video_pronto_bm_v5.mp4')
