import re,collections,glob,os,sys
C=os.environ.get("CLOSURE_DIR", "/srv/oai/casestudy/results-hodge/closure")
mods=[l.strip() for l in open(C+"/MODULES.txt") if l.strip()]; S=set(mods)
paths=[l.strip() for l in open(os.environ.get("SRCS", "/tmp/srcs.txt")) if l.strip()]
imp={}
for m,p in zip(mods,paths):
    deps=[]
    for line in open(p,errors="replace"):
        mm=re.match(r"import\s+(\S+)",line)
        if mm:
            if mm.group(1) in S: deps.append(mm.group(1))
    imp[m]=deps
sys.setrecursionlimit(100000); depth={}
def dep(m):
    if m in depth: return depth[m]
    depth[m]=0; d=1+max((dep(x) for x in imp[m]),default=-1); depth[m]=d; return d
for m in mods: dep(m)
top="OAI.AlgebraicGeometry.HodgeConjecture.MainSubmission"
spine=[top]
while imp[spine[-1]]:
    spine.append(max(imp[spine[-1]],key=lambda x:depth[x]))
grp={}
for l in open(C+"/GROUPS.tsv"):
    k,m=l.rstrip("\n").split("\t"); grp[m]=k
# theorem -> module from census
t2m={}
for f in glob.glob(C+"/census/group-*/accepted-constants.tsv"):
    for l in open(f):
        c=l.rstrip("\n").split("\t")
        if len(c)>=4 and c[0]!="module": t2m.setdefault(c[3],c[0])
rows=collections.defaultdict(lambda: collections.defaultdict(dict))
failed=set()
for f in glob.glob(C+"/referee/group-*.out"):
    k=os.path.basename(f)[6:-4]
    for l in open(f,errors="replace"):
        c=l.rstrip("\n").split("\t")
        if len(c)<4 or c[0]!="REFEREE": continue
        if c[1]=="BUILD" and c[3]=="FAIL": failed.add(k)
        if c[1] in ("L0","R1","R7","R1k"): rows[k][c[2]][c[1]]=c[3]
mstat={}
for k,th in rows.items():
    for n,r in th.items():
        m=t2m.get(n)
        if not m: continue
        s=mstat.setdefault(m,collections.Counter()); s["thm"]+=1
        if r.get("R1")=="FAIL": s["structural"]+=1
        if r.get("R7")=="REVIEW": s["packaged"]+=1
out=open(os.environ.get("OUT_TSV", "/tmp/spine.tsv"),"w"); out.write("level\tmodule\tgroup\tstatus\ttheorems\tR1_FAIL_structural\tR7_REVIEW_packaged\n")
tot=collections.Counter(); nodata=0
for i,m in enumerate(spine):
    k=grp.get(m,"?"); s=mstat.get(m,collections.Counter())
    st="BUILD FAIL (rerun pending)" if k in failed else ("no theorems" if s["thm"]==0 else "ok")
    if k in failed: nodata+=1
    out.write(f"{depth[m]}\t{m}\t{k}\t{st}\t{s['thm']}\t{s['structural']}\t{s['packaged']}\n"); tot+=s
print("spine length",len(spine),"modules; top depth",depth[top])
print("spine modules in failed groups (no rows yet)",nodata)
print("spine theorems with rows",tot["thm"],"structural",tot["structural"],"packaged",tot["packaged"])
print("spine modules with 0 theorems",sum(1 for m in spine if mstat.get(m,{}).get("thm",0)==0 and grp.get(m) not in failed))
# whole closure by depth band
band=collections.defaultdict(collections.Counter)
for m,s in mstat.items(): band[min(depth[m]//20,9)]+=s
for b in sorted(band): s=band[b]; print("depth %3d-%3d: theorems %6d structural %5.1f%% packaged %5.1f%%"%(b*20,b*20+19,s["thm"],100*s["structural"]/max(1,s["thm"]),100*s["packaged"]/max(1,s["thm"])))
print("theorems mapped to modules",sum(s["thm"] for s in mstat.values()))
