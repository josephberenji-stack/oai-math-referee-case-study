# definitions whose value is produced by choosing from a local existence proof (Classical.choice / .choose / .some / Exists.choose / choose)
import re,sys,collections
rows=[l.rstrip("\n").split("\t") for l in open(sys.argv[2]) if l.strip()]
DECL=re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(def|abbrev|instance|theorem|lemma)\s+([^\s(:{\[]+)?")
CH=re.compile(r"Classical\.choice|Classical\.choose|Nonempty\.some|\.choose\b|Exists\.choose|Classical\.indefiniteDescription|Classical\.epsilon|\bchoose\b|Nonempty\.choose")
GL=re.compile(r"[Gg]lue|[Gg]luing|[Dd]escent|[Dd]escend")
c=collections.Counter()
for mod,path,_ in rows:
    t=open(path,errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
    L=t.split("\n"); i=0
    while i<len(L):
        m=DECL.match(L[i])
        if not m: i+=1; continue
        j=i+1
        while j<len(L) and (L[j]=="" or L[j][0] in " \t)|"): j+=1
        ch="\n".join(L[i:j]); i=j
        k="defs" if m.group(1) in ("def","abbrev","instance") else "theorems"
        c[k]+=1
        body=ch.split(":=",1)[1] if ":=" in ch else ""
        if CH.search(body): c[k+" with a choice in the body"]+=1
        if k=="defs" and GL.search(body): c["defs whose body glues or descends"]+=1
print(sys.argv[1],dict(c))
d=c["defs"]; print(sys.argv[1],"choice-valued defs %.2f%%"%(100*c["defs with a choice in the body"]/d),"glue/descent defs %.2f%%"%(100*c["defs whose body glues or descends"]/d),"theorems with choice %.2f%%"%(100*c["theorems with a choice in the body"]/c["theorems"]))
