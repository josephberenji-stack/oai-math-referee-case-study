import Bench.Challenge
import Bench.Solution
open Lean Elab Command
/-- Comparator's two documented checks, reimplemented:  the solution theorem's type equals the challenge theorem's
type, and its axioms are among propext, Quot.sound, Classical.choice. -/
elab "#comparator " c:ident s:ident : command => do
  let env ← getEnv
  let some cc := env.find? c.getId | logInfo m!"CMP\t{s.getId}\tMISSING challenge"
  let some sc := env.find? s.getId | logInfo m!"CMP\t{s.getId}\tMISSING solution"
  let same := cc.type == sc.type
  let axs ← liftCoreM (collectAxioms s.getId)
  let ok := axs.all ([`propext, `Quot.sound, `Classical.choice].contains ·)
  logInfo m!"CMP\t{s.getId}\tstatement {if same then "match" else "DIFFERS"}\taxioms {if ok then "ok" else s!"EXTRA {axs.toList}"}\t{if same && ok then "PASS" else "FAIL"}"
#comparator Bench.fa BenchS.fa
#comparator Bench.fb BenchS.fb
#comparator Bench.fc BenchS.fc
#comparator Bench.fd BenchS.fd
#comparator Bench.fe BenchS.fe
