import re,sys,collections
P=[l.split("\t")[1] for l in open(sys.argv[1]) if l.strip()]
DECL=re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma)\s+(\S+)")
TAC=re.compile(r"\b(simp|simp_all|aesop|omega|linarith|nlinarith|ring|ring_nf|norm_num|decide|positivity|field_simp|grind|tauto|continuity|measurability|fun_prop|gcongr|polyrith|abel|module|infer_instance|ext|induction|cases|rcases|obtain|calc|rw|rwa|erw|exact|apply|refine|constructor|intro|use|have|show|change|congr|funext|unfold|delta|subst|by_contra|contradiction|exfalso|norm_cast|push_cast|trivial|rfl)\b")
auto={"simp","simp_all","aesop","omega","linarith","nlinarith","ring","ring_nf","norm_num","decide","positivity","field_simp","grind","tauto","continuity","measurability","fun_prop","gcongr","polyrith","abel","module"}
lines=[];kind=collections.Counter();tacs=collections.Counter();n=0;useauto=0
for p in P:
    t=open(p,errors="replace").read(); t=re.sub(r"/-.*?-/","",t,flags=re.S); t=re.sub(r"--[^\n]*","",t)
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
