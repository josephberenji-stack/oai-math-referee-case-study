"""run_all.py -- run the referee, the census and the statement-origin pass on every Comparator challenge.

    python3 -I scripts/run_all.py LEAN_DIR DA2_LEAN_DIR OUT_DIR [--only=Name1,Name2] [--mem=8192] [--skip-done]
                                  [--side=solution|challenge] [--config=PATH.json] [--helpers=Root1,Root2]

--config=PATH.json runs one configuration given by its path under LEAN_DIR (e.g.
ComparatorChallenges/HodgeConjectureCMAbelianVarieties/main.json, which is not at the top of the folder);  its output
folder is named after the configuration's folder;  give it its own OUT_DIR.  --helpers names module roots kept inside
the challenge folder under their own names (Hodge:  HodgeConjecture);  definitions declared there are reported as a
third origin, challenge-folder helpers (column challenge_folder_helper_defs), never as solution-side.

--side=challenge refers each challenge's own file (`ComparatorChallenges.<Name>`, built first with `lake build`)
instead of the solution:  it needs only Mathlib (and OAI for the 2 challenges that import it).  The statements are the
same;  the proofs are `sorry`, so L0 FAILs there by construction and is not read.

LEAN_DIR is openai/math's `lean/` folder, already built (`lake build` of every solution module, or of `OAI`).
DA2_LEAN_DIR is Discipline-Architecture-2's `discipline/lean/`.  For each `ComparatorChallenges/*.json` it writes, under
OUT_DIR/<challenge>/:
    referee.out     the referee on the solution module (every theorem in it), with L1u
    census.out      the census on the solution module, against referee.out (and census/ with its tables)
    origins.txt     every definition the headline statements reach, by declaring module (see StmtOrigins.lean.tmpl)
    meta.json       the challenge's solution module, theorem names, whether its file imports OAI, its local
                    definition count, and the exit codes
and OUT_DIR/summary.tsv, one row per challenge theorem:  L0, L1, L1u, L2 statuses, the class, the census's unread
count, the number of solution-side definitions in the statement, and the number declared in the challenge file.
Runs one challenge at a time.  A failure on one challenge is recorded and the run moves on.  Several copies may run at
once on disjoint `--only=` lists:  each copy writes its own temporary file, and each challenge's rows are appended to
summary.tsv (under a file lock) as soon as that challenge is done, before its meta.json, so `--skip-done` after an
interruption never skips a challenge whose rows are missing (a challenge interrupted between the two is redone and its
rows appear twice;  read the last).
"""
import fcntl, json, os, re, subprocess, sys, time

lean_dir, da2, out = (os.path.abspath(a) for a in sys.argv[1:4])
opts = dict(a[2:].split("=", 1) for a in sys.argv[4:] if a.startswith("--") and "=" in a)
flags = {a for a in sys.argv[4:] if a.startswith("--") and "=" not in a}
mem = opts.get("mem", "8192")
side = opts.get("side", "solution")      # "solution":  the solution module (needs OAI built);  "challenge":  the
                                         # challenge file only (needs Mathlib only, except the 2 that import OAI)
only = set(opts["only"].split(",")) if "only" in opts else None
here = os.path.dirname(os.path.abspath(__file__))
registry = os.path.join(here, "..", "referee", "registry.tsv")
tmpl = open(os.path.join(here, "StmtOrigins.lean.tmpl")).read()
sys.path.insert(0, os.path.join(da2, "census"))
from census import stated_names   # noqa: E402

cdir = os.path.join(lean_dir, "ComparatorChallenges")
env = dict(os.environ, DISCIPLINE_LEAN_REGISTRY=os.path.abspath(registry), REFEREE_MEM=mem)
os.makedirs(out, exist_ok=True)
HEADER = ("challenge\ttheorem\tL0\tL1\tL1u\tL2\tclass\tcensus_unread\tsolution_side_defs\tchallenge_local_defs"
          "\tchallenge_file_decls\timports_oai\tdefinition_holes\tchallenge_folder_helper_defs\n")


def append_rows(rows):
    """append one challenge's rows to OUT_DIR/summary.tsv, the header first if the file is empty, under a lock."""
    with open(os.path.join(out, "summary.tsv"), "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0, os.SEEK_END)
        if f.tell() == 0:
            f.write(HEADER)
        for r in rows:
            f.write("\t".join(r) + "\n")
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)


def is_local(x, local):
    """a definition the challenge file declares, or one Lean generates from such a declaration (an instance named
    `inst...<Name>...` for a `deriving` or anonymous `instance` on a challenge-local type, and its `._aux_<n>` parts)."""
    parts = x.split(".")
    while parts and (parts[-1].startswith("_aux") or parts[-1].startswith("_proof") or parts[-1].startswith("match_")):
        parts.pop()
    base = ".".join(parts)
    if any(base == s or base.endswith("." + s) for s in local):
        return True
    last = parts[-1] if parts else ""
    shorts = {s.split(".")[-1] for s in local}
    return last.startswith("inst") and any(len(n) > 2 and n in last for n in shorts)


def run(cmd, log):
    with open(log, "w") as f:
        p = subprocess.run(cmd, cwd=lean_dir, stdout=f, stderr=subprocess.STDOUT, env=env)
    return p.returncode


helpers = [h for h in opts.get("helpers", "").split(",") if h]
if "config" in opts:
    cfgs = [(os.path.basename(os.path.dirname(opts["config"])) if os.path.basename(opts["config"]) == "main.json"
             else os.path.basename(opts["config"])[:-5], os.path.join(lean_dir, opts["config"]))]
else:
    cfgs = [(x[:-5], os.path.join(cdir, x)) for x in sorted(os.listdir(cdir)) if x.endswith(".json")]
for name, cfgpath in cfgs:
    if only and name not in only:
        continue
    d = os.path.join(out, name)
    if "--skip-done" in flags and os.path.exists(os.path.join(d, "meta.json")):
        continue
    os.makedirs(d, exist_ok=True)
    cfg = json.load(open(cfgpath))
    mod, thms = cfg["solution_module"], cfg["theorem_names"]
    holes = cfg.get("definition_names") or []      # definitions whose value the solution chooses (miss mode B)
    if side == "challenge":
        mod = cfg["challenge_module"]
        run(["lake", "build", mod], os.path.join(d, "build.out"))
    # the challenge file, from its module name (the top-level files and subfolders such as Hodge's alike)
    chal_src = open(os.path.join(lean_dir, *cfg["challenge_module"].split(".")) + ".lean", errors="replace").read()
    imports_oai = bool(re.search(r"^import OAI", chal_src, re.M))
    local = stated_names(chal_src)
    t0 = time.time()
    rc_ref = run(["python3", "-I", os.path.join(da2, "referee_lean.py"), f"--project={lean_dir}", f"--modules={mod}"],
                 os.path.join(d, "referee.out"))
    rc_cen = run(["python3", "-I", os.path.join(da2, "census", "census.py"), f"--project={lean_dir}", f"--modules={mod}",
                  f"--out={os.path.join(d, 'census')}", f"--referee-log={os.path.join(d, 'referee.out')}"],
                 os.path.join(d, "census.out"))
    src = tmpl.replace("@@HELPERS@@", "[" + ", ".join("`" + h for h in helpers) + "]").replace("@@IMPORTS@@", f"import {mod}") + "".join(f"\n#stmt_origins {t}" for t in thms)
    tmp = os.path.join(lean_dir, f"_run_all_origins_{os.getpid()}.lean")
    open(tmp, "w").write(src)
    rc_org = run(["lake", "env", "lean", f"-M{mem}", "-j2", os.path.basename(tmp)], os.path.join(d, "origins.raw"))
    os.unlink(tmp)
    odefs, cdefs, hdefs = {}, {}, {}
    for ln in open(os.path.join(d, "origins.raw"), errors="replace"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 3 and p[0].endswith("ODEF"):
            odefs.setdefault(p[1], []).append(p[2])
        elif len(p) >= 3 and p[0].endswith("CDEF"):
            cdefs.setdefault(p[1], []).append(p[2])
        elif len(p) >= 3 and p[0].endswith("HDEF"):
            hdefs.setdefault(p[1], []).append(p[2])
    with open(os.path.join(d, "origins.txt"), "w") as f:
        for t, ds in odefs.items():
            for x in ds:
                f.write(f"{t}\t{x}\n")
        for t, ds in cdefs.items():
            for x in ds:
                f.write(f"{t}\t{x}\tchallenge-file\n")
        for t, ds in hdefs.items():
            for x in ds:
                f.write(f"{t}\t{x}\tchallenge-folder-helper\n")
    ref = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(d, "referee.out"), errors="replace")
           if ln.startswith("REFEREE\t")]
    unread = 0
    m = re.search(r"no CLASS row:\s+(\d+)", open(os.path.join(d, "census.out"), errors="replace").read())
    if m:
        unread = int(m.group(1))
    rows = []
    for t in thms:
        st = {r[1]: r[3] for r in ref if len(r) >= 5 and r[2] == t}
        cls = next((r[4] for r in ref if len(r) >= 5 and r[1] == "CLASS" and r[2] == t), "")
        ds = odefs.get(t, [])
        in_ch = [x for x in ds if is_local(x, local)] + cdefs.get(t, [])
        rows.append([name, t, st.get("L0", ""), st.get("L1", ""), st.get("L1u", ""), st.get("L2", ""), cls,
                     str(unread), str(len(ds) - len(in_ch) + len(cdefs.get(t, []))), str(len(in_ch)), str(len(local)), str(imports_oai), str(len(holes)), str(len(hdefs.get(t, [])))])
    append_rows(rows)
    json.dump(dict(challenge=name, solution_module=mod, theorems=thms, imports_oai=imports_oai, definition_holes=holes,
                   local_definitions=len(local), exit=dict(referee=rc_ref, census=rc_cen, origins=rc_org),
                   seconds=round(time.time() - t0)), open(os.path.join(d, "meta.json"), "w"), indent=1)
    print(f"{name}\treferee {rc_ref}\tcensus {rc_cen}\torigins {rc_org}\t{round(time.time() - t0)}s", flush=True)
