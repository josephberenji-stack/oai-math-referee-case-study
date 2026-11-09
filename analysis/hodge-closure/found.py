import re,collections,sys,os
C=os.environ.get("CLOSURE_DIR", "/srv/oai/casestudy/results-hodge/closure")
R=sys.argv[1:]
mods=[l.strip() for l in open(C+"/MODULES.txt") if l.strip()]; S=set(mods)
paths=[l.strip() for l in open(os.environ.get("SRCS", "/tmp/srcs.txt")) if l.strip()]
def fix(p):
    for r in R:
        q=os.path.join(r,p)
        if os.path.exists(q): return q
    raise SystemExit("missing "+p)
P={m:fix(p) for m,p in zip(mods,paths)}; imp={}; ext={}
for m,p in P.items():
    d=[];e=[]
    for line in open(p,errors="replace"):
        mm=re.match(r"import\s+(\S+)",line)
        if mm: (d if mm.group(1) in S else e).append(mm.group(1))
    imp[m]=d; ext[m]=e
sys.setrecursionlimit(100000); depth={}
def dep(m):
    if m in depth: return depth[m]
    depth[m]=0; x=1+max((dep(y) for y in imp[m]),default=-1); depth[m]=x; return x
for m in mods: dep(m)
idx={m:i for i,m in enumerate(mods)}
users=collections.defaultdict(list)
for m,ds in imp.items():
    for d in ds: users[d].append(m)
# upward reach: files that transitively import m; process highest depth first
order=sorted(mods,key=lambda m:-depth[m]); up={}
for m in order:
    b=0
    for u in users[m]: b|=up[u]|(1<<idx[u])
    up[m]=b
reach={m:bin(up[m]).count("1") for m in mods}
top="OAI.AlgebraicGeometry.HodgeConjecture.MainSubmission"
under=set()  # files MainSubmission rests on
st=[top]
while st:
    x=st.pop()
    for y in imp[x]:
        if y not in under: under.add(y); st.append(y)
print("files MainSubmission rests on",len(under),"of",len(mods))
bases=[m for m in mods if not imp[m]]
ub=[m for m in bases if m in under]
print("bases",len(bases),"bases under MainSubmission",len(ub))
def stats(m):
    t=open(P[m],errors="replace").read()
    th=len(re.findall(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma)\s",t,re.M))
    df=len(re.findall(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(?:def|abbrev|structure|class|inductive|instance)\b",t,re.M))
    ax=len(re.findall(r"^\s*(?:axiom|opaque)\s",t,re.M)); so=len(re.findall(r"\bsorry\b",t))
    doc=re.search(r"/-!(.*?)-/",t,re.S); doc=" ".join(doc.group(1).split())[:160] if doc else ""
    return t.count("\n"),th,df,ax,so,doc
print("\nTOP 25 BY UPWARD REACH (files resting on it)")
for m in sorted(mods,key=lambda m:-reach[m])[:25]:
    n,th,df,ax,so,doc=stats(m)
    print(f"{reach[m]}\t{depth[m]}\tL{n}\tthm{th}\tdef{df}\tax{ax}\tsorry{so}\t{m}\tMathlib:{len(ext[m])}\t{doc}")
# reach distribution
h=collections.Counter()
for m in mods:
    r=reach[m]; k="0" if r==0 else "1" if r==1 else "2-9" if r<10 else "10-99" if r<100 else "100-999" if r<1000 else "1000-9999" if r<10000 else "10000+"
    h[k]+=1
print("\nreach histogram",[(k,h[k]) for k in ["0","1","2-9","10-99","100-999","1000-9999","10000+"]])
# base file content
tot=collections.Counter()
for m in ub:
    n,th,df,ax,so,_=stats(m); tot["lines"]+=n; tot["thm"]+=th; tot["def"]+=df; tot["ax"]+=ax; tot["sorry"]+=so
print("\nbases under MainSubmission totals",dict(tot))
ec=collections.Counter(".".join(x.split(".")[:2]) for m in ub for x in ext[m]); print("their Mathlib imports top",ec.most_common(10))
ar=collections.Counter(".".join(m.split(".")[1:3]) for m in ub); print("their areas top",ar.most_common(12))
# spread: chain fan-in per depth for files under MainSubmission
dc=collections.Counter(depth[m] for m in under); print("\nfiles under Main per depth band",[(b*20,sum(dc[d] for d in range(b*20,b*20+20))) for b in range(10)])
# out-degree of files under main
od=collections.Counter(min(len(imp[m]),6) for m in under); print("internal imports per file (6=6+)",sorted(od.items()))
ud=collections.Counter(min(len(users[m]),6) for m in under); print("importers per file (6=6+)",sorted(ud.items()))
