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

DECL=re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma)\s+(\S+)")
PURE=re.compile(r":=\s*(?:by\s+)?(?:exact\s+)?(?:rfl|Iff\.rfl|Eq\.refl\s+\S+|HEq\.rfl|\(rfl\))\s*$",re.S)
def scan(p):
    lines=open(p,errors="replace").read().split("\n"); out=[]; i=0
    while i<len(lines):
        m=DECL.match(lines[i])
        if not m: i+=1; continue
        j=i+1
        while j<len(lines) and (lines[j]=="" or lines[j][0] in " \t)"): j+=1
        ch="\n".join(lines[i:j]); ch=re.sub(r"--[^\n]*","",ch).rstrip()
        last=ch.split("\n")[-1].strip()
        k="pure" if PURE.search(ch) else "tailrfl" if re.search(r"(^|\s|<;>\s*)(rfl|Iff\.rfl)$",last) else "other"
        out.append((m.group(2),k)); i=j
    return out
res={m:scan(P[m]) for m in mods}
top="OAI.AlgebraicGeometry.HodgeConjecture.MainSubmission"
under=set(); st=[top]
while st:
    x=st.pop()
    for y in imp[x]:
        if y not in under: under.add(y); st.append(y)
tot=collections.Counter(k for m in under for _,k in res[m]); n=sum(tot.values())
print("theorems in files under MainSubmission",n,dict(tot),"pure %.1f%% tail %.1f%%"%(100*tot["pure"]/n,100*tot["tailrfl"]/n))
allr=[m for m in under if res[m] and all(k=="pure" for _,k in res[m])]
print("files whose every theorem is pure rfl",len(allr),"files with no theorems",sum(1 for m in under if not res[m]))
print("\nby depth band: theorems, pure%, tail%")
for b in range(10):
    c=collections.Counter(k for m in under if b*20<=depth[m]<b*20+20 for _,k in res[m]); t=sum(c.values()) or 1
    print(b*20, sum(c.values()), "%.1f"%(100*c["pure"]/t), "%.1f"%(100*c["tailrfl"]/t))
print("\nTOP 30 FILES BY RESTING WEIGHT x PURE-RFL COUNT")
sc=sorted(under,key=lambda m:-(reach[m]*sum(1 for _,k in res[m] if k=="pure")))[:30]
for m in sc:
    c=collections.Counter(k for _,k in res[m])
    print(reach[m],depth[m],"pure",c["pure"],"tail",c["tailrfl"],"other",c["other"],m)
thin=set(allr)|{m for m in under if not res[m]}
print("\nthin files (no theorem, or every theorem pure rfl)",len(thin),"of",len(under))
memo={}
def tl(m):
    if m in memo: return memo[m]
    memo[m]=0; v=(1+max((tl(y) for y in imp[m] if y in thin),default=0)) if m in thin else 0; memo[m]=v; return v
best=max(thin,key=tl); print("longest run of consecutive thin files",tl(best),"ending at",best)
spine=[top]
while imp[spine[-1]]: spine.append(max(imp[spine[-1]],key=lambda x:depth[x]))
sp=collections.Counter(k for m in spine for _,k in res[m]); print("\nspine (190 files, by source scan):",dict(sp))
with open(os.environ.get("OUT_TSV", "/tmp/rfl.tsv"),"w") as f:
    for m in under:
        for nm,k in res[m]: f.write(f"{m}\t{nm}\t{k}\t{depth[m]}\t{reach[m]}\n")
