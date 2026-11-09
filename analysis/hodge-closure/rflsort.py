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
def clos(m):
    u={m}; st=[m]
    while st:
        x=st.pop()
        for y in imp[x]:
            if y not in u: u.add(y); st.append(y)
    return u
under=clos(top)-{top}
sw=clos("OAI.AlgebraicGeometry.HodgeConjecture.SurfaceConstructionCycle")
DECL=re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|abbrev|instance|structure|class|inductive)\s+(\S+)?")
PURE=re.compile(r":=\s*(?:by\s+)?(?:exact\s+)?(?:rfl|Iff\.rfl|Eq\.refl\s+\S+|HEq\.rfl|\(rfl\))\s*$",re.S)
def chunks(p):
    t=open(p,errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    L=t.split("\n"); i=0
    while i<len(L):
        m=DECL.match(L[i])
        if not m: i+=1; continue
        j=i+1
        while j<len(L) and (L[j]=="" or L[j][0] in " \t)"): j+=1
        yield m.group(1),(m.group(2) or ""),"\n".join(L[i:j]).rstrip(); i=j
IDT=re.compile(r"[A-Za-z_][\w'.₀-₉]*")
defs=collections.defaultdict(list); thms=[]
for m in under:
    for kind,nm,ch in chunks(P[m]):
        if kind in ("theorem","lemma"):
            if PURE.search(ch): thms.append((m,nm,ch))
        else:
            body=ch.split(":=",1)[1] if ":=" in ch else ch
            lit=bool(re.search(r"\bwhere\b",ch)) or body.strip().startswith(("⟨","{"))
            defs[nm.split(".")[-1]].append((m,frozenset(x.split(".")[-1] for x in IDT.findall(body)),lit))
def statement(ch):
    t=re.sub(r"^\S+\s+\S+","",ch.split("\n",1)[0])+"\n"+(ch.split("\n",1)[1] if "\n" in ch else "")
    d=0;last=None
    for j,c in enumerate(t):
        if c in "([{⟨": d+=1
        elif c in ")]}⟩": d-=1
        elif d==0 and t.startswith(":=",j): return " ".join(t[last+1:j].split()) if last is not None else ""
        elif d==0 and c==":": last=j
    return ""
def split_top(st):
    d=0
    for j,c in enumerate(st):
        if c in "([{⟨": d+=1
        elif c in ")]}⟩": d-=1
        elif d==0:
            if st.startswith(" = ",j): return st[:j],st[j+3:],"eq"
            if st.startswith(" ↔ ",j): return st[:j],st[j+3:],"iff"
            if st.startswith(" ≍ ",j) or st.startswith("HEq",j): return st,"","heq"
    return st,"","?"
IDT=re.compile(r"[A-Za-z_][\w'.₀-₉]*")
def head(x):
    x=x.strip()
    while x and x[0] in "(↑⇑@": x=x[1:].strip()
    m=IDT.match(x); return m.group(0).split(".")[-1] if m else ""
def projected(x):
    return bool(re.search(r"\)\s*\.\s*[a-z]\w*(\s|$)",x.strip()+" ")) or bool(re.match(r"^[\w.']+\.[a-z]\w*$",x.strip()))
cls=collections.Counter(); rows=[]
for m,nm,ch in thms:
    st=statement(ch); L,R,rel=split_top(st)
    hL,hR=head(L),head(R)
    dL=defs.get(hL,[]); dR=defs.get(hR,[])
    if rel=="iff": c="iff-rfl"
    elif rel!="eq": c="other-rel"
    elif projected(L) or any(lit for _,_,lit in dL): c="projection"
    elif dL and hR and any(hR in b for _,b,_ in dL): c="unfold"
    elif dR and hL and any(hL in b for _,b,_ in dR): c="unfold"
    elif dL and dR and hL!=hR: c="identification"
    elif dL and hL==hR: c="same-head"
    else: c="other"
    cls[c]+=1; rows.append((c,m,nm,depth[m],reach[m],m in sw,hL,hR,st[:300]))
print("pure-rfl theorems parsed",len(thms))
for k,v in cls.most_common(): print(k,v)
idn=[r for r in rows if r[0]=="identification"]
print("\nidentifications on the switch subtree",sum(1 for r in idn if r[5]),"of",len(idn))
print("\nTOP 40 IDENTIFICATIONS BY FILES RESTING ON THEM")
for r in sorted(idn,key=lambda r:-r[4])[:40]:
    print(f"{r[4]}\t{r[3]}\t{'SW' if r[5] else '--'}\t{r[1].split('.',1)[1]}::{r[2]}\t{r[6]} = {r[7]}\t{r[8][:200]}")
print("\niff-rfl (proved by Iff.rfl or rfl on an iff) top 10 by reach")
for r in sorted([r for r in rows if r[0]=="iff-rfl"],key=lambda r:-r[4])[:10]:
    print(f"{r[4]}\t{r[3]}\t{r[1].split('.',1)[1]}::{r[2]}\t{r[8][:160]}")
with open(os.environ.get("OUT_TSV", "/tmp/rflsort.tsv"),"w") as f:
    f.write("class\tmodule\ttheorem\tdepth\treach\ton_switch\thead_L\thead_R\tstatement\n")
    for r in rows: f.write("\t".join(map(str,r))+"\n")
