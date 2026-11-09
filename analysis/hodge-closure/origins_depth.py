# Where the statement's definitions sit in the closure: map each OAI definition in
# results-hodge/HodgeConjectureCMAbelianVarieties/origins.txt to its module (longest prefix that is a module with
# theorems in rfl.tsv, whose 4th column is the module's import depth) and summarise the depths.
# usage: python3 origins_depth.py <rfl.tsv> <origins.txt>
import sys,collections
dep={}
for l in open(sys.argv[1]):
    c=l.rstrip("\n").split("\t")
    if len(c)>=4: dep[c[0]]=int(c[3])
ds=[];miss=0
for l in open(sys.argv[2]):
    k=l.rstrip("\n").split("\t")[1].split(".")
    m=next((".".join(k[:i]) for i in range(len(k),0,-1) if ".".join(k[:i]) in dep),None)
    if m is None: miss+=1; continue
    ds.append(dep[m])
ds.sort(); n=len(ds)
print("statement definitions mapped to a module depth:",n,"unmapped:",miss)
print("depth median",ds[n//2],"p90",ds[int(n*.9)],"max",ds[-1],"(the proof's top file, MainSubmission, is at depth 189)")
print("by band of 20:",sorted(collections.Counter(min(d//20,9)*20 for d in ds).items()))
