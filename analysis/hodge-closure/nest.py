# definition nesting depth: layers of in-corpus definitions a definition's body passes through
# usage: nest.py <label> <file-list> ; file-list lines "module<TAB>path<TAB>import1,import2,..."
import re,sys,collections
sys.setrecursionlimit(1000000)
label=sys.argv[1]
rows=[l.rstrip("\n").split("\t") for l in open(sys.argv[2]) if l.strip()]
DECL=re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+|partial\s+|unsafe\s+)*(def|abbrev|structure|class|inductive|instance|theorem|lemma)\s+([^\s(:{\[]+)?")
IDT=re.compile(r"[A-Za-z_][\w'.₀-₉!?]*")
defs={}; bymod=collections.defaultdict(dict); byname=collections.defaultdict(list); mimp={}
thm_proofs={}
for mod,path,ims in rows:
    mimp[mod]=[x for x in ims.split(",") if x]
    t=open(path,errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    L=t.split("\n"); i=0
    while i<len(L):
        m=DECL.match(L[i])
        if not m or not m.group(2): i+=1; continue
        j=i+1
        while j<len(L) and (L[j]=="" or L[j][0] in " \t)|"): j+=1
        ch="\n".join(L[i:j]); i=j
        kind,nm=m.group(1),m.group(2); last=nm.split(".")[-1]
        if kind in ("theorem","lemma"): continue
        body=ch.split(":=",1)[1] if ":=" in ch else (ch.split(" where",1)[1] if " where" in ch else "")
        key=(mod,nm); defs[key]=set(x.split(".")[-1] for x in IDT.findall(body))-{last}
        bymod[mod][last]=key; byname[last].append(key)
res=collections.Counter()
def resolve(mod,name):
    if name in bymod[mod]: res["same file"]+=1; return bymod[mod][name]
    for im in mimp.get(mod,[]):
        if name in bymod.get(im,{}): res["direct import"]+=1; return bymod[im][name]
    c=byname.get(name)
    if c and len(c)==1: res["unique name"]+=1; return c[0]
    if c: res["ambiguous (skipped)"]+=1
    return None
edges={k:[r for r in (resolve(k[0],n) for n in b) if r and r!=k] for k,b in defs.items()}
depth={}; onstack=set()
def dep(k):
    if k in depth: return depth[k]
    if k in onstack: return 0
    onstack.add(k); d=1+max((dep(x) for x in edges[k]),default=0); onstack.discard(k); depth[k]=d; return d
for k in defs: dep(k)
D=sorted(depth.values()); N=len(D)
print(label,"definitions",N,"resolution",dict(res))
print(label,"nesting depth median",D[N//2],"p90",D[int(N*.9)],"p99",D[int(N*.99)],"max",D[-1],"mean %.2f"%(sum(D)/N))
h=collections.Counter(min(x,30) for x in D); print(label,"histogram (30=30+)",sorted(h.items()))
deep=max(depth,key=depth.get); ch=[deep]
while edges[ch[-1]]:
    nx=max(edges[ch[-1]],key=lambda x:depth[x])
    if depth[nx]>=depth[ch[-1]]: break
    ch.append(nx)
print(label,"deepest chain:"); [print("  ",depth[k],k[1],"(",k[0],")") for k in ch[:40]]
with open(sys.argv[3],"w") as f:
    for k,d in depth.items(): f.write(f"{k[0]}\t{k[1]}\t{d}\t{len(edges[k])}\n")
