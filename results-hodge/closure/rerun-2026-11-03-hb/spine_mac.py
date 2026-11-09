"""spine_mac.py: closure-spine-2026-11-03/spine.py run on the Mac copies (6 Nov 2026).

Same per-module statistics as spine.py lines 22-56 (theorem -> module from census accepted-constants.tsv;
L0/R1/R7/R1k rows; BUILD FAIL groups; structural = R1 FAIL, packaged = R7 REVIEW).  Two differences, both forced:
  * the spine itself (module list and depth) is read from closure-spine-2026-11-03/spine.tsv, which spine.py computed
    on the VM from the Lean sources' imports; the sources are not on the Mac.  The import graph has not changed since
    (same closure-root, GROUPS.tsv md5 checked below).  The depth-band section of spine.py needs every module's depth,
    so it is not reproduced.
  * results = the original closure run (oai-hodge-pull-2026-11-06/.../closure/{referee,census}) with the 10 groups
    whose build failed there (675 1128 1129 1134 1154 1192 1199 1200 1201 1736) taken from the heartbeat-fixed rerun
    copies in closure-reruns-2026-11-05/{referee,census}.
Also writes every CLASS row of every spine module (spine-class.tsv).
"""
import collections, glob, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ORIG = os.path.join(ROOT, "oai-hodge-pull-2026-11-06/casestudy/results-hodge/closure")
RERUN = HERE
SPINE_TSV = os.environ.get("SPINE_TSV", os.path.join(ROOT, "analysis/hodge-closure/spine.tsv"))
RERUN_GROUPS = {"675", "1128", "1129", "1134", "1154", "1192", "1199", "1200", "1201", "1736"}

def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()

spine, depth = [], {}
for l in list(open(SPINE_TSV))[1:]:
    c = l.rstrip("\n").split("\t"); spine.append(c[1]); depth[c[1]] = int(c[0])
grp = {}
for l in open(os.path.join(ORIG, "GROUPS.tsv")):
    k, m = l.rstrip("\n").split("\t"); grp[m] = k

def gid(path): return os.path.basename(path).split("group-")[1].split(".")[0].split("/")[0]

ref_files = {gid(f): f for f in glob.glob(os.path.join(ORIG, "referee/group-*.out"))}
cen_files = {os.path.basename(os.path.dirname(f))[6:]: f for f in glob.glob(os.path.join(ORIG, "census/group-*/accepted-constants.tsv"))}
for k in RERUN_GROUPS:
    ref_files[k] = os.path.join(RERUN, f"referee/group-{k}.out")
    cen_files[k] = os.path.join(RERUN, f"census/group-{k}/accepted-constants.tsv")

t2m = {}
for k, f in sorted(cen_files.items()):
    if not os.path.exists(f): continue
    for l in open(f):
        c = l.rstrip("\n").split("\t")
        if len(c) >= 4 and c[0] != "module": t2m.setdefault(c[3], c[0])
rows = collections.defaultdict(lambda: collections.defaultdict(dict))
cls = collections.defaultdict(list)
failed = set()
for k, f in ref_files.items():
    for l in open(f, errors="replace"):
        c = l.rstrip("\n").split("\t")
        if len(c) < 4 or c[0] != "REFEREE": continue
        if c[1] == "BUILD" and c[3] == "FAIL": failed.add(k)
        if c[1] in ("L0", "R1", "R7", "R1k"): rows[k][c[2]][c[1]] = c[3]
        if c[1] == "CLASS": cls[c[2]].append((k, c[3], c[4] if len(c) > 4 else ""))
mstat = {}
for k, th in rows.items():
    for n, r in th.items():
        m = t2m.get(n)
        if not m: continue
        s = mstat.setdefault(m, collections.Counter()); s["thm"] += 1
        if r.get("R1") == "FAIL": s["structural"] += 1
        if r.get("R7") == "REVIEW": s["packaged"] += 1

out = open(os.path.join(HERE, "spine-2026-11-06.tsv"), "w")
out.write("level\tmodule\tgroup\tstatus\ttheorems\tR1_FAIL_structural\tR7_REVIEW_packaged\tsource\n")
tot = collections.Counter(); nodata = 0
for m in spine:
    k = grp.get(m, "?"); s = mstat.get(m, collections.Counter())
    st = "BUILD FAIL" if k in failed else ("no theorems" if s["thm"] == 0 else "ok")
    if k in failed: nodata += 1
    src = "rerun-hb" if k in RERUN_GROUPS else "original"
    out.write(f"{depth[m]}\t{m}\t{k}\t{st}\t{s['thm']}\t{s['structural']}\t{s['packaged']}\t{src}\n"); tot += s
out.close()
cout = open(os.path.join(HERE, "spine-class-2026-11-06.tsv"), "w")
cout.write("level\tmodule\tgroup\ttheorem\tstatus\tclass\n")
ncls = collections.Counter(); spine_set = set(spine)
for n, lst in cls.items():
    m = t2m.get(n)
    if m in spine_set:
        for k, stt, cc in lst:
            cout.write(f"{depth[m]}\t{m}\t{k}\t{n}\t{stt}\t{cc}\n"); ncls[(stt, cc)] += 1
cout.close()
print("GROUPS.tsv md5", md5(os.path.join(ORIG, "GROUPS.tsv")), "| spine.tsv md5", md5(SPINE_TSV))
print("spine length", len(spine), "modules; top depth", depth[spine[0]])
print("spine modules in failed groups (no rows yet)", nodata, "| failed groups:", sorted(failed) or "none")
print("spine theorems with rows", tot["thm"], "structural", tot["structural"], "packaged", tot["packaged"])
print("spine modules with 0 theorems", sum(1 for m in spine if mstat.get(m, {}).get("thm", 0) == 0 and grp.get(m) not in failed))
print("spine CLASS rows", sum(ncls.values()), dict(sorted(ncls.items(), key=lambda x: -x[1])))
print("theorems mapped to modules", sum(s["thm"] for s in mstat.values()))
