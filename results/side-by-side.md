# Same theorems, two checks:  Comparator and the referee (28 Oct 2026)

Comparator's column is what its configuration requires (`ComparatorChallenges/*.json`):  the solution's theorem matches
the challenge statement, and the proof uses only `propext`, `Quot.sound`, `Classical.choice`.  OpenAI reports these
as passing;  Comparator itself was not run here (it needs Linux's `landrun`).  The referee's column is our run on the
compiled solution modules (`results/*/referee-L1u.out`, `census.out`;  referee Discipline-Architecture-2 at 474014d).

| | PeriodicGroup | OddKaplansky | CharacterVarieties |
|---|---|---|---|
| headline theorem | `SourceBurnside.thm_main` | `OddKaplansky.main_theorem` | `…Diagram.producedMarkedValues_allSeams` |
| **Comparator:** statement matches | reported pass | reported pass | reported pass |
| **Comparator:** three axioms only | reported pass | reported pass | reported pass |
| **Referee L0:** three axioms only | PASS | PASS | PASS |
| **Referee L1:** stand-ins | REVIEW (2 opaque with a value) | REVIEW (2 opaque with a value) | REVIEW (1 opaque with a value) |
| **Referee L1u:** where the hidden values are reached | proof only (PASS) | proof only (PASS) | **the statement** (REVIEW) |
| **Referee L2:** hypotheses | none | none | a `Diagram` structure carrying propositions (REVIEW) |
| challenge file:  local definitions | 9 | 4 | 0, but it imports OpenAI's own library |
| **Referee class** | A? | A? | A? |
| **Census:** accepted theorems left unread | 0 | 0 | 0 (5 generated `congr_simp`) |

**Where the two agree.**  All three proofs use only the three axioms, by both checks.  Nothing fails outright.

**Where only the referee sees something.**
- CharacterVarieties:  the challenge file imports OpenAI's library, so the statement it fixes is itself an OpenAI
  definition, and that definition's meaning runs through the hidden value `cutGeneratorWitness`.  Comparator's match
  succeeds because both sides use the same definition;  it cannot say what that definition means.  The referee marks
  the statement REVIEW (L1u) and its `Diagram` hypothesis REVIEW (L2).
- In all three:  the referee says which hidden values exist and whether a statement or only a proof reaches them,
  and the census confirms every accepted theorem was read.  Comparator reports neither.

**What neither decides.**  Whether the challenge-local definitions (9 and 4 here) say what the papers' headlines say.
That is a person's reading;  the referee lists them so it is a short one.
