"""build_seq.py -- build one module's import closure one file at a time, each Lean process capped.

    python3 -I scripts/build_seq.py LEAN_DIR MODULE [--mem=5120]

Run from anywhere; LEAN_DIR is the upstream `lean/` folder (its packages must already be fetched). Modules outside
the upstream library (Mathlib and the other packages) are taken from their caches and must already be built. Each
module is compiled with `lake env lean -M<mem> -j2 -o <olean> -i <ilean>`, in dependency order, skipping any whose
.olean is newer than its source and its imports. Stops at the first error and prints it.
"""
import os, re, subprocess, sys, time

lean_dir, target = sys.argv[1], sys.argv[2]
mem = next((a.split("=", 1)[1] for a in sys.argv[3:] if a.startswith("--mem=")), "5120")
os.chdir(lean_dir)
OUT = ".lake/build/lib/lean"
imp = {}


def src(m):
    return m.replace(".", "/") + ".lean"


def imports(m):
    if m not in imp:
        imp[m] = [x for x in (re.match(r"\s*(?:public\s+)?import\s+(\S+)", ln) for ln in open(src(m), errors="replace"))
                  if x] if os.path.exists(src(m)) else []
        imp[m] = [x.group(1) for x in imp[m]]
    return imp[m]


order, seen = [], set()


def visit(m):
    stack = [(m, False)]
    while stack:
        x, done = stack.pop()
        if done:
            order.append(x)
            continue
        if x in seen or not os.path.exists(src(x)):
            continue
        seen.add(x)
        stack.append((x, True))
        stack += [(y, False) for y in imports(x)]


visit(target)
local = [m for m in order if os.path.exists(src(m))]
print(f"BUILD\t{target}\t{len(local)} local modules\tmem {mem} MB", flush=True)
t0 = time.time()
for i, m in enumerate(local, 1):
    olean, ilean = f"{OUT}/{m.replace('.', '/')}.olean", f"{OUT}/{m.replace('.', '/')}.ilean"
    deps = [src(m)] + [f"{OUT}/{y.replace('.', '/')}.olean" for y in imports(m) if os.path.exists(src(y))]
    if os.path.exists(olean) and all(os.path.getmtime(olean) >= os.path.getmtime(d) for d in deps if os.path.exists(d)):
        continue
    os.makedirs(os.path.dirname(olean), exist_ok=True)
    s = time.time()
    p = subprocess.run(["lake", "env", "lean", f"-M{mem}", "-j2", "-o", olean, "-i", ilean, src(m)],
                       capture_output=True, text=True)
    errs = [ln for ln in (p.stdout + p.stderr).split("\n") if ": error" in ln]
    print(f"{i}/{len(local)}\t{m}\t{time.time() - s:.0f}s\t{'ERROR' if p.returncode else 'ok'}", flush=True)
    if p.returncode:
        print("\n".join(errs[:10] or (p.stdout + p.stderr).split("\n")[-20:]))
        sys.exit(1)
print(f"BUILD\tdone\t{time.time() - t0:.0f}s", flush=True)
