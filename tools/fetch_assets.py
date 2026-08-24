import json,urllib.request,os,sys
a=json.load(open('assets.json'))
ok=fail=0
for uid,v in a.items():
    out=os.path.join('_masters',uid+'.'+v['ext'])
    if os.path.exists(out) and os.path.getsize(out)>1000: ok+=1; continue
    try:
        req=urllib.request.Request(v['url'],headers={'User-Agent':'Mozilla/5.0','Referer':'https://grizzlyanimation.com/'})
        d=urllib.request.urlopen(req,timeout=60).read()
        open(out,'wb').write(d); ok+=1
        print('ok',uid[:8],v['w'],len(d)//1024,'KB',flush=True)
    except Exception as e:
        fail+=1; print('FAIL',uid[:8],e,flush=True)
print('DONE ok=%d fail=%d'%(ok,fail))
