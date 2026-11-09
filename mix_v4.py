"""V4 mix: voiced commercial, beat-aware score edit and bespoke transition accents."""
import wave,subprocess,math
import numpy as np
from render_v4 import A,O,R,D,S,cue

def sounddesign():
    sr=48000;mix=np.zeros((D*sr,2),np.float32);rng=np.random.default_rng(512)
    def add(sig,at,gain=1,pan=0):
        p=max(0,round(at*sr));n=min(len(sig),len(mix)-p)
        if n>0:mix[p:p+n]+=sig[:n,None]*np.array([math.sqrt((1-pan)/2),math.sqrt((1+pan)/2)])[None,:]*gain
    # Low-end punctuation gives the kinetic words weight without drowning the voice.
    for at in [.7,cue('Mais qualidade'),cue('Mais escolha'),cue('Mais cuidado'),S[3],S[4],S[6],S[8],S[10]]:
        t=np.arange(round(.42*sr))/sr
        phase=2*np.pi*(48*t+44*(1-np.exp(-24*t))/24)
        hit=np.sin(phase)*np.exp(-12*t)+rng.normal(0,1,len(t))*.12*np.exp(-80*t)
        add(hit,at,.21)
    # Short stereo air sweeps lead the transition instead of ringing over the next line.
    for i,at in enumerate(S[1:10]):
        t=np.arange(round(.36*sr))/sr;n=rng.normal(0,1,len(t))
        n=n-np.concatenate([[0],n[:-1]])*.72
        env=np.sin(np.pi*np.linspace(0,1,len(t)))**2
        add(n*env,at-.31,.035,-.4 if i%2 else .4)
    # Four tactile product pass-bys, not four identical loud explosions.
    for i in range(4):
        at=S[2]+i*(S[3]-S[2])/4;t=np.arange(round(.08*sr))/sr
        add(rng.normal(0,1,len(t))*np.exp(-t*65),at,.033,(i-1.5)*.3)
    # Brand resolution uses a soft three-note consonant chord.
    t=np.arange(round(1.6*sr))/sr
    for i,f in enumerate([440,554.365,659.255]):
        add(np.sin(2*np.pi*f*t)*np.exp(-t*3.6)*(1-np.exp(-t*80)),42.0+i*.055,.045)
    pcm=np.int16(np.clip(mix,-1,1)*32767)
    with wave.open(str(A/'sound_design_v4.wav'),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())

def mix(picture_name='picture_v4.mp4',output_name='video_pronto_bm_v4.mp4'):
    sounddesign()
    f='[0:a]asplit=3[a][b][c];[a]atrim=0:21.4286,asetpts=PTS-STARTPTS[a1];[b]atrim=8.5714:22.7143,asetpts=PTS-STARTPTS[b1];[c]atrim=25.5:35,asetpts=PTS-STARTPTS[c1];[a1][b1]acrossfade=d=0.5357:c1=qsin:c2=qsin[ab];[ab][c1]acrossfade=d=0.5357:c1=qsin:c2=qsin[out]'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(A/'music.mp3'),'-filter_complex',f,'-map','[out]','-ac','2','-ar','48000',str(A/'score_v4.wav')],check=True)
    ins=['ffmpeg','-y','-v','error','-i',str(O/picture_name)]
    for n in ['narracao_v4.mp3','score_v4.wav','sound_design_v4.wav','whoosh.mp3','notification.mp3','producao.mp4','estoque.mp4','carregamento.mp4']:ins+=['-i',str(A/n)]
    f=f'[1:a]highpass=f=75,equalizer=f=2800:t=q:w=1.2:g=1.2,loudnorm=I=-15.5:TP=-1.5:LRA=8,adelay=250|250,apad,atrim=0:{D},aformat=channel_layouts=stereo,asplit=2[v][side];'
    f+=f'[2:a]atrim=0:{D},afade=t=in:d=0.18,afade=t=out:st=42.2:d=1.8,volume=0.35[m];[m][side]sidechaincompress=threshold=0.025:ratio=5:attack=6:release=220[duck];[3:a]volume=0.9[sfx];'
    f+='[4:a]asplit=3[w0][w1][w2];'
    for i,at in enumerate([S[2],S[3],S[8]]):
        ms=round((at-.3)*1000);f+=f'[w{i}]atrim=0:0.55,atempo=1.25,volume=0.07,adelay={ms}|{ms}[whoosh{i}];'
    ms=round((S[5]+.4)*1000);f+=f'[5:a]volume=0.13,adelay={ms}|{ms}[notification];'
    for i,(idx,st,trim,dur,gain)in enumerate([(6,S[6],.5,S[7]-S[6],.04),(7,S[7],1,S[8]-S[7],.035),(8,S[8],.5,S[9]-S[8],.07)]):
        ms=round(st*1000);f+=f'[{idx}:a]atrim=start={trim}:duration={dur},asetpts=PTS-STARTPTS,highpass=f=150,lowpass=f=2600,afade=t=in:d=0.15,afade=t=out:st={dur-.25}:d=0.25,volume={gain},adelay={ms}|{ms}[amb{i}];'
    ts=['v','duck','sfx','notification']+[f'whoosh{i}'for i in range(3)]+[f'amb{i}'for i in range(3)]
    f+=''.join('['+x+']'for x in ts)+f'amix=inputs={len(ts)}:duration=first:normalize=0,alimiter=limit=0.89:level=0[a]'
    subprocess.run(ins+['-filter_complex',f,'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-t',str(D),'-movflags','+faststart',str(O/output_name)],check=True)
if __name__=='__main__':mix()
