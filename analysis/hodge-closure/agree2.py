# Declaration-level agreement between the challenge's helper declarations and their OAI namesakes.
# For each helper declaration, take its chunk (from the declaration line to the next top-level line), split it into
# statement (before the top-level ':=' or 'where') and body, normalize namespaces and whitespace, and compare with every
# OAI declaration of the same last name; keep the best match.
import os,re,sys,collections
H="ComparatorChallenges/HodgeConjectureCMAbelianVarieties"
DECL=re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:public\s+|private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|abbrev|structure|class|instance|inductive)\s+([^\s(:{\[]+)")
NS=re.compile(r"\b(?:OAI\.AlgebraicGeometry\.|OAI\.|HodgeConjecture\.Definitions\.|HodgeConjecture\.Lemmas\.|HodgeConjecture\.Mathlib\.|HodgeConjecture\.|_root_\.|ComplexPoint\.Basic\.ComplexSchemePoint\.)")
def chunks(p):
    t=open(p,errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    L=t.split("\n"); i=0
    while i<len(L):
        m=DECL.match(L[i])
        if not m: i+=1; continue
        j=i+1
        while j<len(L) and (L[j]=="" or L[j][0] in " \t)|"): j+=1
        yield m.group(1),m.group(2).split(".")[-1],"\n".join(L[i:j]); i=j
def split(ch):
    d=0
    for k,c in enumerate(ch):
        if c in "([{⟨": d+=1
        elif c in ")]}⟩": d-=1
        elif d==0 and (ch.startswith(":=",k) or ch.startswith(" where",k)): return ch[:k],ch[k:]
    return ch,""
def norm0(x):
    x=NS.sub("",x); x=re.sub(r"\b(public|private|protected|noncomputable|@\[expose\])\s*","",x)
    x=re.sub(r"@\[[^\]]*\]","",x); return " ".join(x.split())
QUAL=re.compile(r"\b(?:[A-Za-z_][\w']*\.)+([A-Za-z_][\w'₀-₉!?]*)")
def norm(x):
    # second level: every qualified name reduced to its last component (Foo.Bar.baz -> baz), so a copy that writes
    # full names where the original relies on `open` compares equal; x.1 style projections are untouched
    return " ".join(QUAL.sub(lambda m: m.group(1), norm0(x)).split())
oai=collections.defaultdict(list)
for dp,_,fs in os.walk("OAI"):
    for f in fs:
        if f.endswith(".lean"):
            for kind,n,ch in chunks(os.path.join(dp,f)): oai[n].append((kind,ch,os.path.join(dp,f)))
helpers=[os.path.join(dp,f) for dp,_,fs in os.walk(H+"/HodgeConjecture") for f in fs if f.endswith(".lean")]+[H+"/CM.lean"]
res=collections.Counter(); bykind=collections.defaultdict(collections.Counter); rows=[]
for h in helpers:
    for kind,n,ch in chunks(h):
        st,bd=split(ch); ns,nb=norm(st),norm(bd)
        best="no namesake"; where=""
        for k2,c2,p2 in oai.get(n,[]):
            s2,b2=split(c2); s2,b2=norm(s2),norm(b2)
            if ns==s2 and nb==b2: best,where="statement and body identical",p2; break
            if ns==s2 and best!="statement identical, body differs": best,where="statement identical, body differs",p2
            elif best=="no namesake": best,where="statement differs",p2
        res[best]+=1; bykind[kind][best]+=1; rows.append((h,n,kind,best,where))
print("challenge helper declarations compared:",sum(res.values()))
for k,v in res.most_common(): print(f"  {k}: {v} ({100*v/sum(res.values()):.1f}%)")
print("by kind:")
for kd,c in sorted(bykind.items()): print(" ",kd,dict(c))
with open(sys.argv[1],"w") as f:
    f.write("helper_file\tname\tkind\tagreement\toai_file\n")
    for r in rows: f.write("\t".join(r)+"\n")
