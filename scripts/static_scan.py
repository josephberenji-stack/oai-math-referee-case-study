"""static_scan.py -- token scan of the openai/math Lean library, without building or running anything.

    python3 -I scripts/static_scan.py sources/openai-math scans/

Writes, under scans/:  opaque.tsv (every `opaque` declaration with file:line and the text after `:=`),
challenges.tsv (each Comparator challenge with its theorem names and the number of local definitions in the challenge
file), and a summary.  Only token greps over the source:  a count here is a count of text, not of compiled constants.
"""
import json, os, re, sys

src, out = sys.argv[1], sys.argv[2]
lean = os.path.join(src, "lean")
OPAQUE = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*opaque\s+(\S+)")
DEFS = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(def|structure|abbrev|inductive|class|instance)\b")
TOKENS = {"sorry": re.compile(r"\bsorry\b"), "admit": re.compile(r"\badmit\b"), "axiom": re.compile(r"^\s*axiom\s"),
          "native_decide": re.compile(r"\bnative_decide\b"), "implemented_by": re.compile(r"implemented_by"),
          "extern": re.compile(r"@\[extern"), "unsafe": re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?unsafe\s"),
          "decide +kernel": re.compile(r"decide \+kernel")}


def strip_comments(s):
    s = re.sub(r"/-.*?-/", lambda m: "\n" * m.group(0).count("\n"), s, flags=re.S)
    return "\n".join(ln.split("--")[0] for ln in s.split("\n"))


os.makedirs(out, exist_ok=True)
nfiles, tok, opq = 0, {k: 0 for k in TOKENS}, []
for root, _, files in os.walk(os.path.join(lean, "OAI")):
    for f in files:
        if not f.endswith(".lean"):
            continue
        nfiles += 1
        p = os.path.join(root, f)
        text = strip_comments(open(p, encoding="utf-8", errors="replace").read())
        lines = text.split("\n")
        for k, pat in TOKENS.items():
            if any(pat.search(ln) for ln in lines):
                tok[k] += 1
        for i, ln in enumerate(lines):
            m = OPAQUE.match(ln)
            if m:
                # the value follows the first `:=` of the declaration, before the next top-level declaration
                j, chunk = i, []
                while j < len(lines) and j < i + 60:
                    if j > i and re.match(r"^(?:@\[|theorem|lemma|def|abbrev|structure|class|instance|inductive|"
                                          r"noncomputable|private|protected|opaque|namespace|end|section)\b", lines[j]):
                        break
                    chunk.append(lines[j]); j += 1
                body = " ".join(chunk).split(":=", 1)
                val = " ".join(body[1].split())[:120] if len(body) > 1 else "(no value)"
                opq.append((os.path.relpath(p, src), i + 1, m.group(1), val))
with open(os.path.join(out, "opaque.tsv"), "w") as o:
    o.write("file\tline\tname\tvalue (first 120 chars)\n")
    for r in opq:
        o.write("\t".join(map(str, r)) + "\n")
ch = []
cdir = os.path.join(lean, "ComparatorChallenges")
for f in sorted(os.listdir(cdir)):
    if f.endswith(".json"):
        cfg = json.load(open(os.path.join(cdir, f)))
        lf = os.path.join(cdir, f[:-5] + ".lean")
        nd = sum(1 for ln in strip_comments(open(lf, errors="replace").read()).split("\n") if DEFS.match(ln)) if os.path.exists(lf) else -1
        ch.append((f[:-5], len(cfg.get("theorem_names", [])), nd, ",".join(cfg.get("permitted_axioms", []))))
with open(os.path.join(out, "challenges.tsv"), "w") as o:
    o.write("challenge\ttheorems\tlocal_definitions\tpermitted_axioms\n")
    for r in ch:
        o.write("\t".join(map(str, r)) + "\n")
summary = [f"files under lean/OAI: {nfiles}", f"opaque declarations: {len(opq)}",
           f"opaque with no value: {sum(1 for r in opq if r[3] == '(no value)')}",
           f"challenge configs: {len(ch)}", f"challenge theorems: {sum(r[1] for r in ch)}",
           f"challenges with 0 local definitions: {sum(1 for r in ch if r[2] == 0)}",
           f"challenges whose axioms are not exactly propext,Quot.sound,Classical.choice: "
           f"{sum(1 for r in ch if set(r[3].split(',')) != {'propext', 'Quot.sound', 'Classical.choice'})}"]
summary += [f"files with {k}: {v}" for k, v in tok.items()]
open(os.path.join(out, "summary.txt"), "w").write("\n".join(summary) + "\n")
print("\n".join(summary))
