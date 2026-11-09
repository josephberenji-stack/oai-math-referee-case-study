"""Referee each unclassed theorem in the module that declares it (declmod.tsv), one referee run per module, and
collect the theorem's own rows. Writes referee/<module>.out and declmod-rows.tsv (challenge, theorem, module, check,
outcome, detail). Same referee, registry and memory cap as run_all.py; only --modules differs."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
lean_dir, da2, registry, inp, outdir = sys.argv[1:6]
mem = sys.argv[6] if len(sys.argv) > 6 else "16384"
env = dict(os.environ, DISCIPLINE_LEAN_REGISTRY=os.path.abspath(registry), REFEREE_MEM=mem)
os.makedirs(os.path.join(outdir, "referee"), exist_ok=True)
rows = []
for l in open(inp):
    c, m, t, d = l.rstrip("\n").split("\t")
    d = d.removeprefix("(some ").removesuffix(")")
    if d != m:
        rows.append((c, t, d))
mods = sorted({d for _, _, d in rows})

def one(mod):
    out = os.path.join(outdir, "referee", mod + ".out")
    with open(out, "w") as f:
        rc = subprocess.run(["python3", "-I", os.path.join(da2, "referee_lean.py"), f"--project={lean_dir}",
                             f"--modules={mod}"], cwd=lean_dir, stdout=f, stderr=subprocess.STDOUT, env=env).returncode
    print(mod, "rc", rc, flush=True)
    return mod, rc

with ThreadPoolExecutor(6) as ex:
    rcs = dict(ex.map(one, mods))
with open(os.path.join(outdir, "declmod-rows.tsv"), "w") as f:
    f.write("challenge\ttheorem\tdeclaring_module\treferee_exit\tcheck\toutcome\tdetail\n")
    for c, t, d in rows:
        ref = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(outdir, "referee", d + ".out"), errors="replace")
               if ln.startswith("REFEREE\t")]
        mine = [r for r in ref if len(r) >= 5 and r[2] == t]
        if not mine:
            f.write(f"{c}\t{t}\t{d}\t{rcs[d]}\t-\tNO ROWS\t\n")
        for r in mine:
            f.write(f"{c}\t{t}\t{d}\t{rcs[d]}\t{r[1]}\t{r[3]}\t{r[4]}\n")
