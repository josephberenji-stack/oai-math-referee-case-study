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

import glob
top="OAI.AlgebraicGeometry.HodgeConjecture.MainSubmission"
def clos(m):
    u={m}; st=[m]
    while st:
        x=st.pop()
        for y in imp[x]:
            if y not in u: u.add(y); st.append(y)
    return u
under=clos(top)-{top}
# ---- referee rows: hb rerun > rerun > original
C=os.environ.get("CLOSURE_DIR", "/srv/oai/casestudy/results-hodge/closure")
t2m={}
for f in glob.glob(C+"/census/group-*/accepted-constants.tsv")+glob.glob(C+"/rerun-2026-11-03*/census/group-*/accepted-constants.tsv"):
    for l in open(f):
        c=l.rstrip("\n").split("\t")
        if len(c)>=4 and c[0]!="module": t2m.setdefault(c[3],c[0])
src={}
for pri,pat in [(0,C+"/referee/group-*.out"),(1,C+"/rerun-2026-11-03/referee/group-*.out"),(2,C+"/rerun-2026-11-03-hb/referee/group-*.out")]:
    for f in glob.glob(pat):
        k=os.path.basename(f)[6:-4]; txt=open(f,errors="replace").read()
        ok=("\tBUILD\t" not in txt or not re.search(r"REFEREE\tBUILD\t[^\t]*\tFAIL",txt)) and "\tL0\t" in txt
        if ok and (k not in src or src[k][0]<pri): src[k]=(pri,f)
rows=collections.defaultdict(dict)
for k,(pri,f) in src.items():
    for l in open(f,errors="replace"):
        c=l.rstrip("\n").split("\t")
        if len(c)>=4 and c[0]=="REFEREE" and c[1] in ("L0","R1","R7","R1k","CLASS","IFF"): rows[c[2]][c[1]]=c[3]
mrow=collections.defaultdict(collections.Counter)
for n,r in rows.items():
    m=t2m.get(n)
    if not m: continue
    s=mrow[m]; s["rows"]+=1
    if r.get("R1")=="FAIL": s["R1fail"]+=1
    if r.get("R7")=="REVIEW": s["R7rev"]+=1
    if r.get("L0")=="FAIL": s["L0fail"]+=1
    s["CLASS_"+r.get("CLASS","?")]+=1
grp={}
for l in open(C+"/GROUPS.tsv"):
    k,m=l.rstrip("\n").split("\t"); grp[m]=k
print("referee files used",len(src),"of groups",len(set(grp.values())),"; reruns used",sum(1 for v in src.values() if v[0]>0))
# ---- A: conclusion types
def concl(p):
    t=open(p,errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    out=[]
    for mm in re.finditer(r"(?m)^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma)\s+(\S+)",t):
        i=mm.end(); d=0; last=None; j=i
        while j<len(t):
            ch=t[j]
            if ch in "([{⟨": d+=1
            elif ch in ")]}⟩": d-=1
            elif d==0 and t.startswith(":=",j): break
            elif d==0 and ch==":" : last=j
            j+=1
        if last is not None: out.append((mm.group(1)," ".join(t[last+1:j].split())))
    return out
INPUTS="ScalarDescentInput PairSwitchesInput FunctorialityInput LineBundleCyclesInput ExteriorInput PolarizedPairingInput RiemannProjectivityInput RiemannH1Realization RationalH1MapsAreAlgebraic LefschetzOneOne AbelianExteriorCohomology ResolutionInput ResolutionClassInput HodgeDecompositionInput CycleClassesAreHodge FourFactorSwitchAlgebraicity SurfaceConstructionInput cmHodgeClaim".split()
hits=collections.defaultdict(list)
for m in under|{top}:
    for nm,c in concl(P[m]):
        head=re.match(r"([\w.'ℚℂ]+)",c); h=head.group(1).split(".")[-1] if head else ""
        if h in INPUTS: hits[h].append((m,nm))
print("\nA. INPUT TYPE -> theorems whose CONCLUSION head is that type (source parse, files under MainSubmission)")
for I in INPUTS:
    L=hits[I]; print(f"{I}\t{len(L)}\t"+" | ".join(f"{m.split('.',1)[1]}::{n}" for m,n in L[:6]))
# ---- B: exclusive subtrees of Established's imports
est="OAI.AlgebraicGeometry.HodgeConjecture.CMReduction.Established"
ims=imp[est]; cl={i:clos(i) for i in ims}
print("\nB. EXCLUSIVE SUBTREES under each import of CMReduction.Established (files no other import reaches)")
print("import\tclosure\texclusive\texcl_thm\texcl_pure_rfl\texcl_tail_rfl\texcl_rows\tR1fail\tR7rev\tL0fail\tno-row-files")
for i in ims:
    others=set().union(*(cl[j] for j in ims if j!=i)); ex=cl[i]-others
    th=sum(len(res[m]) for m in ex); pu=sum(1 for m in ex for _,k in res[m] if k=="pure"); ta=sum(1 for m in ex for _,k in res[m] if k=="tailrfl")
    r=sum((mrow[m] for m in ex),collections.Counter()); nor=sum(1 for m in ex if res[m] and mrow[m]["rows"]==0)
    print(f"{i.split('.',1)[1]}\t{len(cl[i])}\t{len(ex)}\t{th}\t{pu}\t{ta}\t{r['rows']}\t{r['R1fail']}\t{r['R7rev']}\t{r['L0fail']}\t{nor}")
shared=set.intersection(*cl.values()); print("files reached by every import",len(shared))
# ---- C: the two theorems' own subtrees
for name in ["OAI.AlgebraicGeometry.HodgeConjecture.SurfaceConstructionCycle","OAI.AlgebraicGeometry.HodgeConjecture.CMReduction.FourFactorSwitches"]:
    u=clos(name); ex=u-set().union(*(cl[j] for j in ims if j not in u and name not in cl[j]))
    print("\nC.",name,"closure",len(u),"depth",depth[name])
    print(" its imports:",[x.split('.',1)[1] for x in imp[name]])
    sp=[name]
    while imp[sp[-1]]: sp.append(max(imp[sp[-1]],key=lambda x:depth[x]))
    print(" its own spine (depth, file, thm, pure, rows, R1fail, R7rev, group):")
    for x in sp[:25]:
        c=collections.Counter(k for _,k in res[x]); r=mrow[x]
        print(f"  {depth[x]}\t{x.split('.',1)[1]}\t{len(res[x])}\t{c['pure']}\t{r['rows']}\t{r['R1fail']}\t{r['R7rev']}\t{grp.get(x)}")
