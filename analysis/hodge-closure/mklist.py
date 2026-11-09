import re,sys,os
# closure: modules from MODULES.txt + srcs.txt, two roots
if sys.argv[1]=="closure":
    R=sys.argv[2:]; mods=[l.strip() for l in open(os.environ.get("CLOSURE_DIR", "/srv/oai/casestudy/results-hodge/closure") + "/MODULES.txt") if l.strip()]
    paths=[l.strip() for l in open(os.environ.get("SRCS", "/tmp/srcs.txt")) if l.strip()]
    def fix(p):
        for r in R:
            q=os.path.join(r,p)
            if os.path.exists(q): return q
    items=[(m,fix(p)) for m,p in zip(mods,paths)]
else:
    root=sys.argv[2]; items=[]
    for dp,_,fs in os.walk(os.path.join(root,"Mathlib")):
        for f in fs:
            if f.endswith(".lean"):
                p=os.path.join(dp,f); items.append((os.path.relpath(p,root)[:-5].replace("/","."),p))
S=set(m for m,_ in items)
for m,p in items:
    ims=[x for x in re.findall(r"(?m)^(?:public\s+)?import\s+(\S+)",open(p,errors="replace").read()) if x in S]
    print(f"{m}\t{p}\t{','.join(ims)}")
