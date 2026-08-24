from PIL import Image
import os,glob,json
Image.MAX_IMAGE_PIXELS=None
SIZES={'lg':2400,'md':1400,'sm':640}
for d in SIZES: os.makedirs('assets/img/'+d,exist_ok=True)
os.makedirs('assets/img/poster_w',exist_ok=True)
src=sorted(glob.glob('_masters/*.png')+glob.glob('_masters/*.jpg'))
tot_in=tot_out=0
for p in src:
    uid=os.path.splitext(os.path.basename(p))[0]
    tot_in+=os.path.getsize(p)
    im=Image.open(p); im=im.convert('RGB')
    w,h=im.size
    for k,mx in SIZES.items():
        out='assets/img/%s/%s.webp'%(k,uid)
        if os.path.exists(out): tot_out+=os.path.getsize(out); continue
        nw=min(w,mx); nh=round(h*nw/w)
        im.resize((nw,nh),Image.LANCZOS).save(out,'WEBP',quality=82 if k!='sm' else 80,method=6)
        tot_out+=os.path.getsize(out)
# posters
for p in sorted(glob.glob('_masters/poster/*.jpg')):
    vid=os.path.splitext(os.path.basename(p))[0]
    im=Image.open(p).convert('RGB'); w,h=im.size
    nw=min(w,800); nh=round(h*nw/w)
    out='assets/img/poster_w/%s.webp'%vid
    if not os.path.exists(out): im.resize((nw,nh),Image.LANCZOS).save(out,'WEBP',quality=80,method=6)
print('originals %.1f MB -> webp variants %.1f MB'%(tot_in/1e6,tot_out/1e6))
