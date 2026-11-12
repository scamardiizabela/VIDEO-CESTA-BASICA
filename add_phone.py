"""Add only the second contact to the approved V5 export. Keep original audio packets."""
from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parent
SRC=R/'renders/video_pronto_bm_v5.mp4'
OUT=R/'renders/video_pronto_bm_v5_contatos.mp4'
EXPECTED='070b7937039304afda230ee7017543e1ab8ccb6ea8c9e6c13a271cf4c48610a7'
def run(args):subprocess.run(['ffmpeg','-y','-v','error']+args,check=True)
def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==EXPECTED,'Use the approved V5 master'
    temp=R/'renders/contact_patch';temp.mkdir(exist_ok=True)
    # Last original keyframe before the closing: frame 980 at 32 2/3 seconds.
    run(['-i',str(SRC),'-map','0:v:0','-an','-frames:v','980','-c:v','copy',str(temp/'prefix.mp4')])
    start=36.81-980/30
    alpha=f'if(lt(t,{start}),0,1-pow(1-min(1,(t-{start})/0.85),4))'
    filt=f"drawtext=fontfile={R/'assets/Inter-Bold.ttf'}:text='(17) 99622-0624':fontcolor=0x450a12:fontsize=51:x=83:y=1625:alpha='{alpha}'"
    run(['-ss',str(980/30),'-i',str(SRC),'-map','0:v:0','-an','-vf',filt,'-frames:v','340','-c:v','libx264','-crf','15','-preset','fast','-pix_fmt','yuv420p','-threads','4',str(temp/'ending.mp4')])
    (temp/'join.txt').write_text("file 'prefix.mp4'\nfile 'ending.mp4'\n")
    run(['-f','concat','-safe','0','-i',str(temp/'join.txt'),'-i',str(SRC),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(OUT)])
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(OUT)]))
    assert abs(float(info['format']['duration'])-44)<.04,info['format']
    print('Contact added:',OUT,flush=True)
if __name__=='__main__':main()
