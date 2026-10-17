The pr-contract preflight's closing-keyword arm bound nowhere, and its
multi-issue arm refused one spelling of a class it never stated. Round 1
derived the intended list from the roster and removed the `|| true`; this round
replaces the multi-issue arm's three-separator list with the property that list
stood in for. The round-1 verdict on this pull request was `blocked ...
harness: class-rule-missing`, and the block was one class run plus its
dispositions.

GITHUB CLOSES `KEYWORD #N` AND NOTHING ELSE. `Closes #A #B` closes #A and
silently not #B -- #B has no keyword of its own. Check 1's grep keeps the first
number after each keyword, so the dropped second is arm 1b's business.

THE ARM IS OWNERSHIP, NOT A SEPARATOR LIST. A closing keyword OWNS AT MOST ONE
REFERENCE, decided inside a CLAUSE -- a paragraph, and a sentence within it. The
round-1 arm spelled three separators (whitespace, a comma, an "and"); the
round-1 review ran the class's own rule over 200 merged bodies and returned six
more seams that list let through -- `/`, `&`, `+`, `(`, `;`, any plain word, and
a keyword and its reference split across a newline -- none of them
dispositioned. A separator list always has a next separator; this arm enumerates
none, and no separator is named in it.
`dev/audit/harnesses/closing_keyword_ownership.py` is the rule, the enumerator
and the instrument every number below comes from; the shapes it runs are
GENERATED -- every printable ASCII separator, connector words, wrapping layouts,
the four reference forms, the keyword's spellings and casings -- so it checks
the property the class states rather than the six instances the review happened
to name. `--script` runs the same matrix against another copy: `git show
5c35cd9ba:tools/pr/preflight.sh > /tmp/round1.sh` is the other end.

## Head

`2f7aafdc856db407ac2407c4231d547899546b88`: the round-1 head
`5c35cd9ba6c6915a28ec982648389bd53d742b32`, one commit adding the arm, the rule
harness and the pins, a merge of `origin/main` `e3f3b312fff572904f24d78a44a2c4492b1a8ddb`
with no hand resolution, and one commit recording the new harness in
`tests/closures.json`. The merge base is therefore `e3f3b312f` itself. Every
figure below that reads the pull-request corpus is a function of `origin/main`'s
tip, which was `e3f3b312f` on 2026-10-17; re-take those against a newer tip.

## Mutation proof

Each mutation is ONE named edit of arm 1b's production lines, applied alone in
its own worktree at this head. The check names are what
`PYTHONPATH=tests/hastub python3 tests/entities.py` printed there, and the
second column is the committed rule harness run against the mutated tree.

- `M1-needs-three-references` -- the predicate narrowed from
  `hits(clause[i], ref) > s` to `> s + 1`, i.e. refuse only a THIRD reference.
  `1 of 2343 ENTITY CHECKS FAILED`: `one closing keyword naming several issues
  refuses, since GitHub closes only the first`, detail `rc per separator:
  {'space': 0, 'comma': 0, 'and': 0, 'slash': 0, 'spaced-slash': 0, 'ampersand':
  0, 'plus': 0, 'paren': 0, 'semicolon': 0, 'word': 0, 'colon': 0, 'newline':
  0}`. The scope check stays green, and the harness reads `seams_open=86` of the
  102 shapes.
- `M2-clause-becomes-paragraph` -- the clause reset
  (`gsub(/[.!?][[:space:]]+/, "&\n", t)`) deleted, so the scope is the paragraph.
  `1 of 2343 ENTITY CHECKS FAILED`: `and a second reference in a LATER clause is
  not refused (the scope's own null control)`, detail `rc per shape: {'part-of':
  0, 'leaves-open': 1, 'bare-reference': 0, 'heading': 0}`. The multi-reference
  check stays green -- which is what makes the scope a pinned decision rather
  than a leftover -- and the harness reads `seams_open=0` with
  `refused_but_not_seam=8`, naming exactly the later-clause shapes the rule
  excludes.
- `M3-no-boundary-sentinel` -- the leading space removed from the clause the
  site count reads (`c = " " clause[i]` -> `c = clause[i]`), so the keyword's
  boundary class has no preceding character to bound on. `1 of 2343 ENTITY
  CHECKS FAILED`: the multi-issue check, all twelve rcs 0. The harness reads
  `seams_open=86` and `refused_but_not_seam=1` -- `not-owned:two-keywords-one-clause`,
  the one shape whose SECOND keyword still has a space in front of it.
- `M4-arm-deleted` -- the whole arm-1b block removed. `1 of 2343 ENTITY CHECKS
  FAILED`: the multi-issue check; the harness reads `seams_open=86`. The SCOPE
  check is green here, which is the contrast with `M2`: removing the arm cannot
  red a check about scope, and narrowing the scope cannot red the multi-issue
  check. Each pin moves for its own line. (Run beside its three siblings this
  mutant once also red `the lease has one winner ...`, the gate-lease race
  measuring five concurrent gate scripts; it is green with the mutant alone,
  which is the run this figure is taken from.)

## Null control

- Arm 1b is not always-red. Sixteen of the 102 shapes are ones the rule does NOT
  call seams -- the eleven `NOT_OWNED` rows, plus five generated ones (a `!`, a
  `?` and a `..` used as separators, `i.e.`, and the blank-line layout) -- and
  every one of them exits 0, printed with its own rc
  (`refused_but_not_seam=0` at this head: no shape is refused that the rule does
  not call a seam).
- The corpus does not discriminate arm 1b: it refuses 0 of the 200 merged
  bodies at BOTH ends. So the seam matrix is the discriminating instrument and
  the corpus is a false-positive floor, not evidence of a fix. Stated because a
  figure that reads the same at both ends reads like a pass, and here it is one.

## Figures

- `python3 dev/audit/harnesses/closing_keyword_ownership.py` (this head):
  `RESULT shapes=102  seams_open=0  refused_but_not_seam=0  refusal_not_gating=0`,
  rc 0.
- `python3 dev/audit/harnesses/closing_keyword_ownership.py --script /tmp/round1.sh`
  -- the other end, on the round-1 head's own `tools/pr/preflight.sh` (`md5
  bf6c362d0216b763d6ce025f729588ed`, the same file `review/2342`'s
  `evidence/class-probe.txt` measured): rc 1, `seams_open=73`. The review's own
  twelve instances are rows of that matrix; 3 of them are refused there and 9
  pass with a second, unclosed reference, and all 12 are refused here.
- `python3 dev/audit/harnesses/closing_keyword_ownership.py --corpus /tmp/bodies.json`
  over the 200 most recently merged PRs (`gh pr list --state merged --limit 200
  --json number,body`): `corpus_clause_scope=0`, `corpus_whole_body=25`. The
  scope is measured, not asserted: the same ownership test over the whole body
  refuses 25 real bodies, each carrying its second reference in a later clause.
- The script itself -- not the rule -- over the same 200 bodies, read off arm
  1b's own REFUSE line: 0 at this head and 0 at the round-1 head.
- The intended-list wiring over the same 200: `bash tools/pr/preflight.sh` with
  NO list exits 1 on 27 of them; with the workflow's own derivation, 6 still
  exit 1 -- `#2007 #2008 #2009 #2010 #2015 #2041`, every one at `intended=0`,
  the round-9 roster `issues` number no group names in `fixes`. That derivation
  is the `INTENDED=$(jq -rs --rawfile body ...)` line of
  `.github/workflows/pr-contract.yml`'s pre-flight step, verbatim, over the
  corpus above and `dev/programme/rosters/wave-r*-groups.json` -- the two inputs
  are the whole reproduction. The 9 the round-1 body named is a lower bound; the
  corpus answers 27.
- `MODE: SCOPED -- 2 script(s) run` over 6 changed files (`tests/entities.py`,
  `tests/harness_headers.py`), derived per `fixer.md` step 5 against the merge
  base `e3f3b312f`. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  `tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`.
  `tests/env_drift.py --claims-only e3f3b312f`: `claims hygiene ... ok`.
  `tests/layout.py`: `layout self-test: ok`. `tests/harness_headers.py`: green,
  after the new harness's inline `repo_root` matched the canonical copy (a
  `ROOT = Path(__file__).resolve().parents[3]` reds its depth-seam arm, which is
  how that arm was found).

### The class's seams, each with its disposition

Named individually, because the block asks for a rule over the class and a range
reads as complete while covering a fraction. `seams_open=0` above is the same
claim under the generated matrix; this table is the review's own six instances.

| seam | the rule's shape | disposition |
|---|---|---|
| whitespace | `Closes #A #B` | closed in this diff -- rc 1 |
| comma | `Closes #A, #B` | closed in this diff -- rc 1 |
| `and` | `Closes #A and #B` | closed in this diff -- rc 1 |
| `/` | `Closes #A/#B` | closed in this diff -- rc 1 |
| `&` | `Closes #A & #B` | closed in this diff -- rc 1 |
| `+` | `Closes #A +#B` | closed in this diff -- rc 1 |
| `(` | `Closes #A (#B)` | closed in this diff -- rc 1 |
| `;` | `Closes #A; #B` | closed in this diff -- rc 1 |
| a plain word | `Closes #A then #B` | closed in this diff -- rc 1 |
| newline split | `Closes #A<newline>#B` | closed in this diff -- rc 1 |
| the keyword's casing | `CLOSES #A; #B` | closed in this diff -- rc 1. The arm's keyword class is case-permissive because check 1's grep is `-i`; a case-sensitive class would leave the second reference out of a body check 1 had already acted on. Found by the generated matrix, not by the review |
| the four reference forms | `Closes #A / GH-N` and `/ gh-N`, `/ owner/repo#N`, `/ <issue URL>` | closed in this diff -- rc 1 |
| a second reference in a LATER clause | `Closes #A. #B.` | NOT the class, and deliberately not refused: the reference is in another clause, so the keyword does not claim it. Dispositioned here rather than filed, because `fixer.md` step 8's third arm is for a DISTINCT finding and this is the same class's boundary -- measured, not argued: clause scope refuses 0 of the 200 merged bodies, whole-body scope refuses 25 |

### The closure entry the `closures` job would have reddened

`tests/harness_headers.py`'s depth-seam scan reads every `.py` under
`dev/audit/harnesses/`, and it does so in a CHILD process -- `inline_scan` runs
as a child of `check_repo_roots`, as its own docstring says. CI's Linux
`strace -f` union sees that read and prints `INERT READS tests/harness_headers.py:
dev/audit/harnesses/closing_keyword_ownership.py (a new file beside 37 it
lists)`, which `python3 tools/pr/ci_predict.py --base origin/main` predicted at
the first handoff. A Darwin `--single` recording CANNOT add the entry: the audit
hook does not follow children, so `bash tests/derive_closures.sh --single
tests/harness_headers.py` exited 0 here having changed only the recorded
`seconds` (and reporting `would drop 152 file(s) the committed closure listed;
keeping them`, the partial merge that stops a Darwin recording replacing a Linux
one). The entry is therefore made the way that recording would make it -- through
`closure.write_closures`, sorted into `inert_reads["tests/harness_headers.py"]`,
validated by `closure.layout_errors` -- and `ci_predict` afterwards reads
`CI PREDICT: no closures or fast red predicted against e3f3b312fff5`. The
re-recorded `seconds` for that script sits beside it; `closure.py lane-plan` is
identical with and without them.

### Where a proxy rule and the class statement diverge, and why the measurement decides

The review's rule is stated as "one closing keyword followed by more than one
issue reference". That is a PROXY for the class -- "one closing keyword NAMING
several issues" -- and the two part company at exactly one place: a second
reference in a later clause. Read literally, the proxy also refuses
`Closes #A.` followed by `Part of #B.`, which is not a keyword naming several
issues, it is this repository's convention for "closes one, touches another"
(`Part of` is what a round-9 roster `issues` number gets for the same reason, and
six such bodies are named above). The literal reading refuses 25 of the 200 most
recently merged bodies; the clause-scoped reading refuses 0. So the proxy is not
widened past what the class states, and the shapes it would add are listed in
the harness's `NOT_OWNED` table with the exit code each gets -- they are
dispositioned, not passed over.

### Where this lands, because `pr-contract` runs it from the BASE

The job restores `tools/pr/*.sh` from the pull request's base commit before it
runs them -- an anti-tamper restore, so a pull request cannot weaken the gate
that grades it -- so THIS pull request's own `pr-contract` run exercises the
base's arm. `tests/entities.py` runs the TREE's copy and is not in that
restore's pathspec, so it is what pins this head's arm; and from the next base
that carries this commit, every pull request runs the ownership arm. The
workflow half of round 1 (the derived intended list, the removed `|| true`) is
live for this run, because the job's own YAML is not restored.

The class's grammar lives in the diff, not only in this body: check 1 and arm 1b
now read ONE `CLOSING_REF` spelling. The round-1 head spelled the reference
pattern in two places inside this script (and a third in the workflow's `jq`,
which cannot share it) -- the round-1 review called that coupling out as an
observation, and this closes the two that can share.

## Red checks

- `coverage-ratchet` (its one run at the round-1 head concluded failure,
  20:18:23Z, `early_cutoff.py` below the 95 % per-module floor). NOT this pull
  request's and not touched here: the module is absent from the diff, sibling PR
  #2343 was red on the same lane with a DIFFERENT figure (`75.16 %` against this
  branch's `81.53 %`) on a diff of two record files, and the same branch one
  commit earlier (`55b0fba11`, the same tree but for a delivery row) carries the
  lane SUCCESS -- all three measured by the round-1 review at `review/2342`.
  The `coverage` job reuses the base's per-script data when no
  `custom_components/` file changed, so the lane keys its base wrongly on a
  runner class; it is not one of the ruleset's 17 required contexts, so it does
  not gate the merge. The cheaper detector is `coverage` on `main`.
- `pr-contract` at the round-1 head: red once at 20:29:55Z and GREEN at
  20:34:14Z on the same commit (read off the commits' check-runs API, not the
  pull request's tick, which hides red-then-green). The failure is not standing
  and this revision does not carry it.

The original defect -- the arm bound nowhere -- could not itself go red: the
step's `|| true` swallowed the refusal. The cheaper detector already existed on
the human path (`prepr.sh` forwards the intended list and its own comment names
the CI gap); the CI arm was never wired, so no check could have caught it
earlier. For THIS round's defect the cheaper detector is the harness in this
diff, and it is the detector: it reds on the round-1 arm and passes on this one,
which is the demonstration `defect-root-cause.md` asks of a check.

## Forward-carry

`none`. No finding here changes how a stage that has not started must work. The
same-stage sibling seam the round-1 review named is CLOSED IN THIS DIFF rather
than routed to a new issue, which is `fixer.md` step 8's first disposition; the
rule's remaining seams are the generated matrix above, and each one is named
with its own verdict.

## Friction

`none`
