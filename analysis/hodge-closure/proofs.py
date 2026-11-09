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
u={top}; st=[top]
while st:
    x=st.pop()
    for y in imp[x]:
        if y not in u: u.add(y); st.append(y)
DECL=re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma)\s+(\S+)")
TAC=re.compile(r"\b(simp|simp_all|aesop|omega|linarith|nlinarith|ring|ring_nf|norm_num|decide|positivity|field_simp|grind|tauto|continuity|measurability|fun_prop|gcongr|polyrith|abel|module|infer_instance|ext|induction|cases|rcases|obtain|calc|rw|rwa|erw|exact|apply|refine|constructor|intro|use|have|show|change|congr|funext|unfold|delta|subst|by_contra|contradiction|exfalso|norm_cast|push_cast|trivial|rfl)\b")
auto={"simp","simp_all","aesop","omega","linarith","nlinarith","ring","ring_nf","norm_num","decide","positivity","field_simp","grind","tauto","continuity","measurability","fun_prop","gcongr","polyrith","abel","module"}
lines=[];kind=collections.Counter();tacs=collections.Counter();n=0;useauto=0
for m in u:
    t=open(P[m],errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    L=t.split("\n"); i=0
    while i<len(L):
        if not DECL.match(L[i]): i+=1; continue
        j=i+1
        while j<len(L) and (L[j]=="" or L[j][0] in " \t)"): j+=1
        ch="\n".join(L[i:j]).rstrip(); i=j
        # proof = text after the first top-level ":=" (approx: first ":=" followed by by/term at statement end)
        d=0;k=None
        for q,c in enumerate(ch):
            if c in "([{⟨": d+=1
            elif c in ")]}⟩": d-=1
            elif d==0 and ch.startswith(":=",q): k=q; break
        if k is None: continue
        pf=ch[k+2:].strip(); n+=1
        pl=[x for x in pf.split("\n") if x.strip()]; lines.append(len(pl))
        ts=TAC.findall(pf); tacs.update(set(ts))
        if set(ts)&auto: useauto+=1
        if re.fullmatch(r"(?:by\s+)?(?:exact\s+)?(?:rfl|Iff\.rfl)",pf): kind["rfl"]+=1
        elif not pf.startswith("by") or re.fullmatch(r"by\s+exact\s+[^\n]*",pf,re.S) and "\n" not in pf.strip():
            kind["single term (application of other lemmas)" if "\n" not in pf.strip() or not pf.startswith("by") else "x"]+=1
        else: kind["tactic block"]+=1
lines.sort(); N=len(lines)
print("theorems",n,"proof lines median",lines[N//2],"p75",lines[int(N*.75)],"p90",lines[int(N*.9)],"p99",lines[int(N*.99)],"max",lines[-1])
h=collections.Counter(1 if x==1 else 2 if x<=2 else 5 if x<=5 else 10 if x<=10 else 30 if x<=30 else 100 if x<=100 else 101 for x in lines)
print("proof-line buckets (1,2,3-5,6-10,11-30,31-100,>100):",[h[k] for k in (1,2,5,10,30,100,101)])
print("proof shape:",dict(kind))
print("theorems using at least one automation tactic (simp/omega/linarith/ring/norm_num/decide/aesop/...)",useauto,"%.1f%%"%(100*useauto/n))
print("share of theorems mentioning each tactic:",[(k,"%.1f%%"%(100*v/n)) for k,v in tacs.most_common(25)])
