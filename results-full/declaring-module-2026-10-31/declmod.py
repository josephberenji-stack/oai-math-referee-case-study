"""For each unclassed theorem (unclassed.tsv: challenge, solution_module, theorem), ask Lean which module declares it,
importing the challenge's solution module. Writes declmod.tsv: challenge, solution_module, theorem, declaring_module."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
lean_dir, inp, out = sys.argv[1:4]
import json
rows = [l.rstrip("\n").split("\t") for l in open(inp) if l.strip()]
cdir = os.path.join(lean_dir, "ComparatorChallenges")
rows = [(c, m or json.load(open(os.path.join(cdir, c + ".json")))["solution_module"], t) for c, m, t in rows]
by = {}
for c, m, t in rows:
    by.setdefault((c, m), []).append(t)

def one(key):
    c, m = key
    names = ", ".join(f"`{t}" for t in by[key])
    src = (f"import {m}\nopen Lean in\n#eval show CoreM Unit from do\n  let env ← getEnv\n"
           f"  for n in [{names}] do\n"
           f"    let d := (env.getModuleIdxFor? n).map (fun i => env.header.moduleNames[i.toNat]!)\n"
           f"    IO.println s!\"DECL\\t{{n}}\\t{{d}}\"\n")
    f = f"/tmp/declmod_{c}.lean"
    open(f, "w").write(src)
    p = subprocess.run(["lake", "env", "lean", "-M16384", f], cwd=lean_dir, capture_output=True, text=True)
    got = {}
    for ln in p.stdout.splitlines():
        q = ln.split("\t")
        if len(q) == 3 and q[0] == "DECL":
            got[q[1]] = q[2]
    return [(c, m, t, got.get(t, f"ERROR rc={p.returncode} {p.stderr.strip()[:120]!r}")) for t in by[key]]

with ThreadPoolExecutor(8) as ex:
    res = [r for rs in ex.map(one, sorted(by)) for r in rs]
with open(out, "w") as f:
    for r in res:
        f.write("\t".join(r) + "\n")
print(len(res), "rows")
