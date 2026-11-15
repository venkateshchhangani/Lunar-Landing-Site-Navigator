import glob,json
n1=len(glob.glob('../../exp4/clones/Site01_final_adj_5mpp_*_err.tif')); n4=len(glob.glob('../../exp4/clones04/Site04_final_adj_5mpp_*_err.tif'))
r=[]
r.append(["Site 01 clones (%d of NASA's 100, shrunk to 20 m)"%n1,"Check 2: how much the answer moves if the ground is slightly different","received" if n1>=50 else "partly","ok" if n1>=50 else "part"])
r.append(["Site 04 clones (%d of NASA's 100, shrunk to 20 m)"%n4,"Check 2 for Site 04","received" if n4>=50 else ("partly" if n4 else "assumed pattern"),"ok" if n4>=50 else "part"])
r.append(["LROC photo tile P892S2250, cropped for Site 01 and for Site 04, and image list","Check 3: our shadows vs the real photo (Site 04's photo covers its western two-thirds)","received","ok"])
json.dump(r,open('frows.json','w')); print(r)
