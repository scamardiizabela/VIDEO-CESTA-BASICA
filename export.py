"""Render picture, mix original instrumental and notification, export final MP4."""
import subprocess
from render import ROOT,A,OUT,render

render()
subprocess.run(['ffmpeg','-y','-v','error','-i',str(A/'music.mp3'),'-i',str(A/'notification.mp3'),'-filter_complex','[0:a]atrim=0:35,afade=t=in:d=0.5,afade=t=out:st=33.5:d=1.5,volume=0.75[m];[1:a]volume=0.25,adelay=1450|1450[n];[m][n]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[a]','-map','[a]','-ar','48000','-ac','2',str(A/'mix.wav')],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(OUT/'picture.mp4'),'-i',str(A/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-t','35','-movflags','+faststart',str(OUT/'video_pronto_bm.mp4')],check=True)
