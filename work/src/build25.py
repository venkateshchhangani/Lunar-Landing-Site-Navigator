import json,base64,sys
D='../../exp2/'
t=open('app31.html',encoding='utf-8').read()
astro=open('node/node_modules/astronomy-engine/astronomy.browser.min.js',encoding='utf-8').read(); phys=open('physics.js',encoding='utf-8').read()
assert '</script' not in astro
t=t.replace('/*ASTRO*/',astro,1).replace('/*PHYS*/',phys,1)
sites={}
EV1E_ADD=" One simplification works the other way: the Earth is taken as seen from the Moon's centre, which shows it about 0.23 degrees too high at these spots, so Earth is in view slightly less often than this page says."
fj=json.load(open('far120.json',encoding='utf-8'))
FROWS=json.load(open('frows.json',encoding='utf-8'))
for k in ('01','04'):
    pk=json.loads(open(D+'pack_site%s.js'%k,encoding='utf-8').read().split('var PACK=')[1].rsplit(';',1)[0]); m=json.load(open(D+'meta_site%s.json'%k,encoding='utf-8'))
    assert pk['ev1e'].endswith('more often than we say.'); pk['ev1e']+=EV1E_ADD   # index25: audit finding, see patch30.py
    sites[k]=dict(key=k,name=m['name'],cx0=m['cx0'],cy0=m['cy0'],wx0=m['wx0'],wy0=m['wy0'],zmin=m['zmin'],zmax=m['zmax'],wzmin=m['wzmin'],wzmax=m['wzmax'],
        dem=open(D+'dem16_site%s.b64'%k,encoding='utf-8').read(),demw=open(D+'demw_site%s.b64'%k,encoding='utf-8').read(),spots=m['spots'],
        layers={q:pk['L'][q] for q in ['sun','spread','nasa','earth','both','nasaE','res']},ban=pk['ban'],pill2=pk['pill2'],meas=pk['meas'],pill3=pk['pill3'],cls3=pk['cls3'],conf3=pk['conf3'],frows=FROWS,horg=open(D+'horg_site%s.b64'%k,encoding='utf-8').read(),evid=pk['ev1']+'<br><br>'+pk['ev1e']+'<br><br>'+pk['ev2']+'<br><br>'+pk['ev3']+'<br><br>'+pk['ev4']+'<br><br>'+pk['trustleg'],trustleg=pk['trustleg'],spotinfo=pk['spots'])
# Label rule (decided 6 Nov): a spot's label is the stricter of the 100 m circle label (stored) and the single 25 m cell label (trustOf). strict_labels.json holds both, measured from the 6 Nov page.
STRICT=json.load(open('strict_labels.json',encoding='utf-8'))
for k in ('01','04'):
    for sp in sites[k]['spotinfo']:
        r=[x for x in STRICT[k] if x['n']==sp['n']][0]; assert sp['trust']==r['circle']
        sp['trust_circle']=r['circle']; sp['trust_cell']=r['cell']; sp['trust']=r['strict']
# Wording override (6 Nov): the pack scripts still say "you can rely on" for spot B; the page must not imply trust on a Medium spot.
OLDWHY='Most sunlight you can rely on (Earth in view too)'; NEWWHY='Most sunlight, with Earth in view too'
for k in ('01','04'):
    n=0
    for lst in ('spotinfo','spots'):
        for sp in sites[k][lst]:
            if sp.get('why')==OLDWHY: sp['why']=NEWWHY; n+=1
    assert n>=1,(k,n)
t=t.replace('/*FAR*/',open('far120.b64',encoding='utf-8').read(),1).replace('/*FZMIN*/0',repr(fj['zmin']),1).replace('/*FZMAX*/0',repr(fj['zmax']),1).replace('/*FN*/0',str(fj['n']),1).replace('/*FCELL*/0',repr(fj['cell']),1)
t=t.replace('/*SITES*/','var SITES='+json.dumps(sites)+';',1)
t=t.replace('/*EARTH*/','data:image/jpeg;base64,'+base64.b64encode(open('earth_bm4096.jpg','rb').read()).decode(),1)
t=t.replace('/*FRAG*/""',json.dumps(open('frag.glsl',encoding='utf-8').read()),1)
t=t.replace('/*MOON*/','data:image/jpeg;base64,'+base64.b64encode(open('moon_4096.jpg','rb').read()).decode(),1)
open('index25.html','w',encoding='utf-8',newline='\n').write(t);print(len(t)/1e6,'MB')
