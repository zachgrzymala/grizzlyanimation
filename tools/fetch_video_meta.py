import json,urllib.request,urllib.parse,re,os
man=json.load(open('manifest.json'))
vids={}
for page,blocks in man.items():
    for b in blocks:
        if b['t']=='vimeo': vids[b['id']]={'kind':'vimeo','h':b.get('h','')}
        elif b['t']=='yt': vids[b['id']]={'kind':'yt'}
print(len(vids),'videos')
meta={}
for vid,info in vids.items():
    try:
        if info['kind']=='vimeo':
            u='https://vimeo.com/'+vid+(('/'+info['h']) if info['h'] else '')
            api='https://vimeo.com/api/oembed.json?url='+urllib.parse.quote(u,safe='')+'&width=1280'
            j=json.load(urllib.request.urlopen(urllib.request.Request(api,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
            th=j.get('thumbnail_url','')
            th=re.sub(r'-d_\d+x?\d*','-d_1280',th)
            meta[vid]={'kind':'vimeo','title':j.get('title',''),'dur':j.get('duration'),'h':info['h'],'thumb':th}
        else:
            th='https://i.ytimg.com/vi/%s/maxresdefault.jpg'%vid
            meta[vid]={'kind':'yt','title':'ALDI Christmas 2022 | Feast of Football','dur':None,'h':'','thumb':th}
    except Exception as e:
        print('meta FAIL',vid,e); meta[vid]={'kind':info['kind'],'title':'','dur':None,'h':info.get('h',''),'thumb':''}
ok=0
for vid,m in meta.items():
    if not m['thumb']: continue
    out='_masters/poster/%s.jpg'%vid
    if os.path.exists(out) and os.path.getsize(out)>2000: ok+=1; continue
    try:
        d=urllib.request.urlopen(urllib.request.Request(m['thumb'],headers={'User-Agent':'Mozilla/5.0'}),timeout=45).read()
        open(out,'wb').write(d); ok+=1
    except Exception as e: print('thumb FAIL',vid,e)
json.dump(meta,open('videos.json','w'),indent=1)
print('posters downloaded:',ok,'/',len(meta))
