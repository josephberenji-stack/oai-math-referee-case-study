# Which challenge helper files have a copy in OAI?  For each file under ComparatorChallenges/HodgeConjectureCMAbelianVarieties/HodgeConjecture
# (plus CM.lean), find the OAI file sharing the most declaration names, then compare normalized bodies.
import os,re,sys,difflib,collections
H="ComparatorChallenges/HodgeConjectureCMAbelianVarieties"
DECL=re.compile(r"(?m)^\s*(?:@\[[^\]]*\]\s*)?(?:public\s+|private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma|def|abbrev|structure|class|instance|inductive)\s+([^\s(:{\[]+)")
def norm(t):
    t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    t=re.sub(r"(?m)^\s*(public\s+)?import .*$","",t); t=re.sub(r"(?m)^\s*module\s*$","",t)
    t=re.sub(r"@\[expose\]\s*","",t); t=re.sub(r"(?m)^public\s+","",t)
    t=re.sub(r"\bOAI\.AlgebraicGeometry\.|\bOAI\.|\bHodgeConjecture\.Definitions\.|\bHodgeConjecture\.Lemmas\.|\bHodgeConjecture\.Mathlib\.|\bHodgeConjecture\.","",t)
    t=re.sub(r"(?m)^\s*(namespace|end|open|noncomputable section|section|variable|set_option)\b.*$","",t)
    return [l.strip() for l in t.split("\n") if l.strip()]
helpers=[os.path.join(dp,f) for dp,_,fs in os.walk(H+"/HodgeConjecture") for f in fs if f.endswith(".lean")]+[H+"/CM.lean"]
oai=[os.path.join(dp,f) for dp,_,fs in os.walk("OAI") for f in fs if f.endswith(".lean")]
idx=collections.defaultdict(set)
names={}
for p in oai:
    t=open(p,errors="replace").read(); ns=set(n.split(".")[-1] for n in DECL.findall(t)); names[p]=ns
    for n in ns: idx[n].add(p)
rows=[]
for h in helpers:
    t=open(h,errors="replace").read(); hn=set(n.split(".")[-1] for n in DECL.findall(t))
    cand=collections.Counter(p for n in hn for p in idx.get(n,()))
    if not hn: rows.append((h,"no decls","",0,0.0)); continue
    if not cand: rows.append((h,"no OAI match","",len(hn),0.0)); continue
    best,k=cand.most_common(1)[0]
    r=difflib.SequenceMatcher(None,norm(t),norm(open(best,errors="replace").read()),autojunk=False).ratio()
    rows.append((h,"match",best,k/len(hn),r))
c=collections.Counter()
for h,s,b,share,r in rows:
    if s!="match": c[s]+=1
    elif share==1 and r>=0.98: c["copy, text identical after renaming (>=98%)"]+=1
    elif share>=0.8 and r>=0.8: c["copy, modified (80-98%)"]+=1
    else: c["partial or different"]+=1
print("challenge helper files (+ CM.lean):",len(helpers))
for k,v in c.most_common(): print(f"  {k}: {v}")
with open(sys.argv[1],"w") as f:
    f.write("helper_file\tstatus\toai_file\tdecl_name_share\tbody_similarity\n")
    for h,s,b,share,r in sorted(rows): f.write(f"{h}\t{s}\t{b}\t{share:.2f}\t{r:.3f}\n")
# coverage: helper declaration names that exist anywhere in OAI, and how many OAI files hold them
tot=0; found=0; spread=collections.Counter(); low=[]
for h in helpers:
    t=open(h,errors="replace").read(); hn=set(n.split(".")[-1] for n in DECL.findall(t))
    if not hn: continue
    files=set(p for n in hn for p in idx.get(n,()))
    f=sum(1 for n in hn if n in idx); tot+=len(hn); found+=f
    spread[min(len(set(next(iter(sorted(idx[n]))) for n in hn if n in idx)),6)]+=1
    if f/len(hn)<0.8: low.append((h,f,len(hn)))
print(f"helper declarations: {tot}; with an OAI declaration of the same name: {found} ({100*found/tot:.1f}%)")
print("helper files by how many OAI files hold their names (6=6+):",sorted(spread.items()))
print("helper files with under 80% of names found in OAI:",len(low)); [print("  ",h.split("HodgeConjecture/",1)[-1],f,n) for h,f,n in low[:10]]
