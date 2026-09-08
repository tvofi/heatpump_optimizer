Worktree removed and pruned; the repository is untouched. Report follows.

---

# Root cause: an assertion whose **reachability** was never measured

## Verdict on the framing: the class is distinct from 0002, and the evidence is stronger than the hypothesis you handed me

0002's cause is *"a property that is false on a healthy tree has no natural witness, so the author writes down a model of the check and pins the model."* Its subject is the assertion's **content** — the pin says something other than what the check does.

In all instances below the assertion's content is **correct**. Emptying `checkProvenance` at `e3449a5` *is* refused by `FIXTURE VACUOUS` — I ran it. What varies is whether the line executes, and that is decided by a fact about the clone, not about the code. Two consequences separate the classes:

- 0002's instances are all inside one function's acceptance and all fixed by writing a better witness. These are spread over three files and two languages and are fixed by making a *skip* visible.
- 0002's mutation lane is the fix for 0002 and is instance 3 here. **Your observation holds, and there is a second one you did not name: instance 5 was introduced by `99dd454`, the commit that landed decision 0003 rule 5 and its "keeps rule 5 honest" section.** The commit that wrote *"do not report a refusal you have not established"* created, in the same diff, an assertion that demands a refusal in exactly the environment its own new arm was written for.

Both countermeasure lanes — 0002's and 0003's — produced an instance of this class in the act of closing their own. That is not 0002 recurring; a defect class does not normally reproduce inside its own remedy twice, at two different levels, with the remedy's author reasoning correctly about the level below.

---

## 1. The named cause, established by reproduction

**Cause.** *A check's environment-dependence is reasoned about where the check reads the environment, and not where the assertion that drives it does. The result is an assertion that is correct, that did not run, and whose run is byte-identical to one where it did.*

The three instances you named, plus two more the sweep found live at the PR head.

### Instance 1 — the guard, at `e3449a5`

`assertAcceptance` drove `checkProvenance` with `HEAD` and skipped the assertion when `HEAD === origin/main`.

```
$ git clone -q --no-checkout /home/user/heatpump_optimizer c1
$ cd c1 && git checkout -q --detach e3449a5 && git update-ref refs/remotes/origin/main e3449a5
$ node .claude/workflows/policy_lint.mjs           # clean
rc=0    FIXTURE ok: 37 error(s) hold 54 pins across 7 check classes
# checkProvenance emptied (anchor asserted == 1 before writing):
$ node .claude/workflows/policy_lint.mjs
rc=0    FIXTURE ok: 37 error(s) hold 54 pins across 7 check classes
```

Byte-identical. The control that shows the assertion is sound and only unreachable:

```
$ git update-ref refs/remotes/origin/main e4a388a   # the pull-request shape
$ node .claude/workflows/policy_lint.mjs            # same mutant
rc=1  FIXTURE VACUOUS: checkProvenance did not refuse e3449a5, a commit origin/main does not carry.
```

Fixed. At `f20b757`, `origin/main == HEAD`, the same mutant gives `rc=1 FIXTURE VACUOUS … 5d2b909, a parentless commit`.

### Instance 2 — the count, `e3449a5` vs `310606f`

```
# clone with no origin/main, at e3449a5
skip     provenance-pin   origin/main is not in this clone, so neither direction can be driven
FIXTURE ok: 37 error(s) hold 54 pins        <-- the same 54 a full clone earns
# same clone, at 310606f
FIXTURE ok: 37 error(s) hold 51 pins
# same clone, at 310606f, origin/main restored
FIXTURE ok: 37 error(s) hold 54 pins
```

### Instance 3 — 0002's own countermeasure, at `99dd454`

```
$ git remote remove origin && git update-ref -d refs/remotes/origin/main
$ node .claude/workflows/policy_lint_mutants.mjs
  PIN      checkIndex … (6 rows)
  ACCEPTED checkProvenance      the acceptance returned 0 with this check reporting nothing at all
MUTANTS: `checkProvenance` is DELETABLE IN SILENCE …
rc=1
```

The acceptance had printed `skip provenance-pin` four lines earlier in the same run. The lane had the answer in its own null control's output and read only its exit code. Fixed at `e6230a3`; at `b34af6b` the same clone gives `SKIP checkProvenance … rc=0`, and the teeth control (full clone, drive cut) still gives `ACCEPTED … rc=1`.

### Instance 4 — **live at the PR head**: `check-wave-script.mjs` scans a directory

`.claude/workflows/check-wave-script.mjs:114` discovers its population with `fs.readdirSync(here).filter(/^wave-.*-groups\.json$/)`. The assertion guards vacuity on one operand (`known.length > 0`) and not on the one the environment controls.

```
$ mv .claude/workflows/wave-*-groups.json /tmp/rosters.bak/
$ node .claude/workflows/check-wave-script.mjs
  ok   every resume.stage in every committed roster is one the wave script branches on
26 passed, 0 failed        rc=0
```

Not hypothetical. Commit `198979d` **on this branch** deleted three of the seven rosters:

```
6b71e85 (main):  7 roster file(s), 84 group(s), 84 carrying resume.stage
f20b757 (branch): 4 roster file(s), 59 group(s), 59 carrying resume.stage
```

The printed verdict is identical at 84, at 59 and at 0. It landed at `6438406`, merged as **#611**, 2026-09-08 00:34, and has been on `main` since. The `wave-script` job in `governance.yml` runs it, so CI has been reporting `ok` over a population that fell 30% under it.

### Instance 5 — **live at the PR head**: introduced by the commit that landed 0003

`99dd454` added two things at once: a `--is-shallow-repository` arm in `checkProvenance` that declines rather than refusing, and an acceptance arm demanding that `checkProvenance` **refuse** `deadbeef…`. In a shallow clone those two cannot both hold.

Real shallow clone, `git clone --depth 1 --no-single-branch file://…`, `origin/main` present, at `f20b757`:

```
$ git rev-parse --is-shallow-repository
true
$ node .claude/workflows/policy_lint.mjs
  skip     provenance   this clone is shallow, so git cannot say whether deadbee is an ancestor of origin/main
FIXTURE VACUOUS: checkProvenance did not refuse a SHA no object in this clone carries. … and this clone is not shallow.
rc=1
$ node .claude/workflows/policy_lint_mutants.mjs
MUTANTS: null control FAILED -- the unmutated acceptance returned 1, so no mutant below proves anything.
rc=1
```

The failure message asserts *"this clone is not shallow"* four lines below a line of its own output saying it is. It takes both lanes down on any seat whose clone is shallow — the same local `prepr.sh` path where instance 3 was found. Attribution:

```
$ git log -S'deadbeefdeadbeef' -- .claude/workflows/policy_lint.mjs
99dd454 09-08 11:22 policy: "no" and "I cannot look" are different answers, and 0003 names the family
$ git diff 99dd454 f20b757 -- .claude/workflows/policy_lint.mjs | grep -E '^[-+].*(deadbeef|is-shallow|not shallow)'
(empty)
```

CI is not exposed (`governance.yml` uses `fetch-depth: 0`); the exposure is local, which is precisely where instance 3 was found.

Both instances are present at the **real** PR head, not only my local one: `#618`'s head is `b34af6b`, which differs from `f20b757` by a comment in one file (`git diff --stat f20b757 b34af6b` → 5 insertions, 3 deletions, comment text only), and the matrix run at `b34af6b` reports both.

### How far the cause reaches — the sweep

24 sites across the six files you named where an assertion's reachability turns on an environment fact.

| file | site | on absence | state |
|---|---|---|---|
| `policy_lint.mjs` | `checkProvenance` no `origin/main` | prints `skip provenance`, returns `[]` | handled |
| | `checkProvenance` shallow arm | prints `skip provenance`, returns `[]` | handled |
| | acceptance provenance drive, no ref / no `commit-tree` | prints `skip checkProvenance-pin`, pins not counted | handled (`310606f`; was 1+2) |
| | acceptance `deadbeef` arm, shallow clone | **`FIXTURE VACUOUS`, rc=1, message contradicts the run** | **UNHANDLED — instance 5** |
| | `fixtures/policy-rot/` missing | `FIXTURE VACUOUS`, rc=1 | handled, fail-closed |
| | `fixtures/policy-rot/prepr/` missing | `FIXTURE VACUOUS`, rc=1 | handled, fail-closed |
| | `index.md` fixture missing | `FIXTURE VACUOUS`, rc=1 | handled, fail-closed |
| | `.github/PULL_REQUEST_TEMPLATE.md` missing | drift assertion silently skipped | handled **by adjacency only** — measured: deleting it gives `TOTAL: 1 error` from `checkIndex`, not from this guard |
| | `--record-known-bad` with no merge base | refuses out loud | handled |
| `policy_lint_mutants.mjs` | null control red | refuses to report any mutant | handled |
| | anchor unmatched | `CRASH` | handled |
| | acceptance skipped a drive | `SKIP`, non-failing, named | handled (`e6230a3`; was 3) |
| `brief_lint.mjs` | cited tag ref unresolvable | `checkAgainstTags` → `warn`, printed | handled, residual below |
| | roster directory scan | `TOTAL: 0 error(s) across 0 file(s)` — **population disclosed**; acceptance runs on committed fixtures | handled |
| | `fileLines` unreadable | `null`; the path class errors independently | handled |
| `check-wave-script.mjs` | roster directory scan | **`ok` over zero rosters** | **UNHANDLED — instance 4** |
| | `web-fix-wave.js` read | throws | handled |
| `tests/entities.py` | `docs/HANDOVER.md` absent | `_uf is None` → check FAILS | handled, fail-closed |
| | `--is-ancestor` on a shallow clone | rc=128 → check FAILS, message names shallow as the cause | handled, residual below |
| | `_ic_exists`, `_preflight.is_file()` (6 sites, counted as one) | conjunction → check FAILS | handled, fail-closed |
| | `git ls-files tools/` equality | check FAILS | handled, fail-closed |
| `tests/closure.py` | `merge-base` fails | falls back to `diff_ref` | handled |
| | `git diff` fails | `raise SystemExit` | handled |
| | closures missing / uncovered / no changed files | `mode: full` + the `MODE:` line | handled — **fail-open-to-full, the strongest form in the tree** |

**Two residuals worth naming.** `brief_lint`'s tag path downgrades an error to a warning when the tag is not in the clone, so a genuinely rotted citation is a warning there and an error in CI — disclosed on the line, and that is the trade `SKIP` makes too. And `tests/entities.py` gets instance 5's situation *right*: I measured `git merge-base --is-ancestor 6438406 HEAD` → **rc=128** on the shallow clone, rc=0 on a full one, and the check's own message says *"a shallow clone cannot answer this; the gate jobs check out with fetch-depth: 0"*. That message landed at `b6a21f1` (#519), **2026-09-06 20:45 — two days before `99dd454` wrote "this clone is not shallow" into a shallow clone.** The correct handling was already in the tree, in another file, and nothing carried it.

---

## 2. Process state: **(c)** — followed, and did not produce the intended result

Not (a). Three instructions cover this ground and all three predate every instance:

- `defect-root-cause.md`: *"demonstrated failing on the defect it was written for, and passing once fixed."*
- `root-cause.md` §5: *"Null-control it: show it does not fire on a healthy tree, and does not go green by skipping."*
- `fixer.md` step 3: *"an 'every' or a 'none' is a measurement, owed the command that produced it and the result that would have appeared had it been false."*

Not (b) — each was **obeyed**, and I can show it in the authors' own words and artifacts:

- Instance 1: `310606f`'s body quotes the shipped comment — *"on main the two are equal and the probe would be a null control twice over"*. The author ran the demonstration and reasoned explicitly about which environments needed it. The reasoning was performed and reached the wrong set.
- Instance 3: 0002's Decision section specifies *"A null control runs first: the unmutated acceptance must return 0."* It was implemented, it works, and it still could not distinguish a check the clone had not driven.
- Instance 5: `99dd454` implemented 0003 rule 5 **and** its "keeps rule 5 honest" clause, and produced the defect in the same commit.

`root-cause.md` warns *"if your proposed countermeasure is 'tell the worker harder', suspect your state."* Every one of those three instructions is scoped to **the run the author performs**; none is scoped to the runs the check will later perform elsewhere. A firmer version of an instruction that was obeyed is the wrong medicine, which is what makes this (c) and not (b).

**The (d) reading, named and rejected as the class's state.** 0002's lane was sound for six checks that read only the tree, and its precondition — *every name in `CORPUS_CHECK_NAMES` is drivable in any clone* — changed when `checkProvenance` joined the enumeration. That is a genuine (d) for **instance 3 alone**. It cannot be the class's state: instances 1, 2 and 4 sit outside that lane and 4 predates it, and instance 5 postdates its fix.

---

## 3. The cost test, with numbers

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, wall-clock per occurrence.

**Measured on this box, at `f20b757`, full clone, healthy tree:**

| lane | runs | ms |
|---|---|---|
| `policy_lint.mjs` | 5 | 1253, 1308, 1343, 1410, 1502 |
| `policy_lint_mutants.mjs` | 5 | 833, 850, 864, 875, 882 |
| `brief_lint.mjs` | 3 | 814, 835, 838 |
| `check-wave-script.mjs` | 3 | 45, 46, 48 |
| `tests/entities.py` | 1 | 21577 |
| prototype matrix (below) | 6 | 8204, 8241, 8405, 8425, 8611, 8895 |
| hardlink clone + checkout | 3 | 111, 117, 123 |
| real `--depth 1` clone | 2 | 945, 1232 |

**A correction you should have.** The 1.3 s you gave me for the mutation lane does not reproduce: I measure **0.83–0.88 s** over five runs, against 1.25–1.50 s for `policy_lint` beside it. 0002 already says *"Re-measure it rather than carrying it"* about this exact figure; I am not claiming the lane got faster, only that 1.3 s is again a carried literal and mine is the number from this box today.

**Left side.** `cost(countermeasure, recurring) = 8.2–8.9 s` per run, ≈ **8.4 s**. That is 4× the existing governance pair (2.15 s) and 0.39× `tests/entities.py`, which the suite already pays.

**Right side.**

- `cost(defect)`, measured from author dates in the branch: instances 1+2 found and repaired `e3449a5` 10:46 → `310606f` 11:06 = **1200 s for the pair**; instance 3, `99dd454` 11:22 → `e6230a3` 11:30 = **480 s**. I take the cheapest measured figure, **480 s**, as the per-occurrence cost of a review round that catches one.
- The two instances review did **not** catch cost more: instance 5 has been live 52 min and counting since `99dd454`; instance 4 has been live on `main` for 11 h 40 min since #611 and is what the `wave-script` job has been certifying.
- `P(recurrence)`, **measured, not estimated**: 5 instances between 2026-09-08 00:34 and 12:14 — 11.7 h, **0.43 per hour**. Three of the branch commits touching these lanes introduced one, so ≈ **0.5 per lane-touching commit**. The surface is growing, as 0002 recorded for its own class.
- Governance runs in the cycle, measured from the API: `actions/workflows/governance.yml/runs?created=>2026-09-07` → **`total_count 48`** on 2026-09-08 (44 `pull_request`, 4 `push`).

**The test.** Break-even is `480 / 8.4 = 57` runs per catch. Observed rate is 5 instances across 48 governance runs = **one per 9.6 runs**. Margin ≈ **6×**, at the most conservative reading of both sides; at the 1200 s reading it is ≈ 15×. Per cycle: 48 × 8.4 s = **403 s** of machine time against 5 × 480 s = **2400 s** of review time.

**The dishonest part of that arithmetic, stated rather than hidden.** Both sides are wall-clock, as the policy requires, but the left is machine seconds and the right is agent seconds. If you weight them equally the margin is 6×; if agent time is worth more, it widens. It never narrows. I did not measure local `prepr.sh` invocations, so the left side counts only the 48 CI runs and is a floor.

**The countermeasure obeys the ratchet, measured.** With the prototype added as a tracked `.claude/workflows/*.mjs` and both site fixes applied: `policy_lint` → `TOTAL: 0 error(s) across 35 policy file(s)`, `FIXTURE ok … 57 pins`; `tests/entities.py` → `ALL 1112 ENTITY CHECKS PASSED`. `.mjs` is classified as code by 0003's inverted blocklist so no `policy_budgets` cap applies, and `structure_budgets.json`'s 24 metrics are all over `custom_components/`. **No budget raise is needed.**

---

## 4. The countermeasure, shown failing and shown passing

**What it addresses.** State (c): the existing instructions are scoped to the author's own run. This one runs the lanes in the environment shapes the repository declares it supports and requires each shape's declared outcome — which is the thing no author's single run can establish.

I built it as a prototype **in the scratchpad, not in the repository**: `envmatrix.mjs`, 5 hardlink clones, 13 declared outcomes. Full text available on request; the shapes are `pr`, `push-main` (`governance.yml`'s `push: branches: [main]`), `no-remote`, `shallow` (a `.git/shallow` graft — validated against a real `--depth 1` clone, which gives the identical outcome, at 120 ms instead of 1.0 s), and `no-rosters`.

**Failing on the defects it was written for.** At `e3449a5`, where instances 1–3 lived:

```
  ok    pr / policy_lint rc=0 and every pin earned
  ok    pr / nothing skipped in a full clone
  ok    pr / every corpus check measured and pinned
  ok    push-main / policy_lint rc=0
  ok    push-main / the same pins are earned as on a pull request
  FAIL  push-main / every corpus check still measured and pinned  --  rc=1 ACCEPTED checkProvenance …
  ok    no-remote / policy_lint rc=0
  FAIL  no-remote / the skipped drive is said out loud  --  no `skip checkProvenance-pin` line
  FAIL  no-remote / a skipped drive does not claim its pins  --  pins=54 vs pr=54
  FAIL  no-remote / the lane reports NOT MEASURED rather than failing  --  rc=1
  FAIL  no-rosters / a roster scan over zero rosters does not report ok  --  rc=0; 26 passed, 0 failed
RC=1
```

At the real PR head `b34af6b`, it isolates exactly the two live ones and passes all ten rows the three landed fixes cover:

```
  ok  × 10   (pr, push-main, no-remote)
  FAIL  shallow / policy_lint rc=0  --  rc=1 FIXTURE VACUOUS: … did not refuse a SHA no object in this clone carries
  FAIL  shallow / an undrivable arm is said out loud and not claimed  --  pins=null vs pr=57
  FAIL  no-rosters / a roster scan over zero rosters does not report ok  --  rc=0; 26 passed, 0 failed
RC=1
```

**Passing once fixed.** Two minimal site fixes in a scratch clone (both via anchor-asserted heredoc): `check-wave-script.mjs` counts its rosters, groups and stages, puts them in the label, and adds `rosters > 0 && used.size > 0` to the assertion; `policy_lint.mjs` guards the `deadbeef` arm on `--is-shallow-repository`, prints `skip checkProvenance-noobject` and does not count that pin — deliberately **not** spelled `checkProvenance-pin`, because the other three drives still run and the mutation lane must still measure the check.

```
  ok    pr / …  (3)
  ok    push-main / … (3)
  ok    no-remote / … (4)
  ok    shallow / policy_lint rc=0
  ok    shallow / an undrivable arm is said out loud and not claimed
  ok    no-rosters / a roster scan over zero rosters does not report ok
13 declared outcome(s) held, 0 did not, across 5 environment shape(s)
RC=0   elapsed 8611ms
```

The healthy run now discloses its population:

```
  ok   every resume.stage in all 4 committed roster(s) (59 group(s), 4 distinct stage(s)) is one the wave script branches on
```

**Null controls.** It does not fire on a healthy tree — the green run above, plus all five lanes on the fixed clone: `policy_lint` rc=0 / 57 pins (unchanged, so no pin is lost where the arm *can* be driven), `policy_lint_mutants` rc=0, `brief_lint` rc=0, `check-wave-script` rc=0, `rules_sync --check` rc=0. And it does not go green by skipping — pointed at a source with no `refs/heads/main`, the shape that cannot be built fails rather than vanishing:

```
  FAIL  pr / built  --  update-ref failed
  … 7 held, 4 did not …
RC=1
```

### What I would and would not recommend

Two things are owed **regardless of the lane decision**: instances 4 and 5 are live at `b34af6b` and need fixing. Instance 5 makes `prepr.sh` red-and-wrong for any seat on a shallow clone; instance 4 is a CI job certifying a population that has already shrunk 30% under it.

On the lane itself I recommend building it, and I want you to weigh the strongest objection, which is real: **the shape list is a hand-kept enumeration, which is decision 0003's own defect generator.** 0003 rule 1 says invert a list whose complement is measurable; there is no `git ls-files` of environments, so it cannot be inverted. Rule 4 says import the enumeration from production rather than copying it — and that *is* available for the two rows that matter most: `pr` and `push-main` are `governance.yml`'s `on:` triggers, and `shallow` is the complement of its `fetch-depth: 0`. A landed version should derive those three from `governance.yml` rather than list them, and declare `no-remote` and `no-rosters` as hand-kept local shapes with that stated on the line. My prototype does none of that; it hand-keeps all five, and that is its principal weakness.

If you would rather build nothing, the honest form of that decision is: fix the two sites, and record that the class's detector is an adversarial reader, at 480–1200 s per catch, against 8.4 s per run for a mechanical one. The numbers do not support it, but it is a coherent reading of the bound in `defect-root-cause.md` about complexity, and it is your call rather than mine.

**What I do *not* recommend is a rule.** State (c) means the instructions were obeyed; a firmer one is what `root-cause.md` tells me to suspect.

---

## What I could NOT check

- **Instance 5 at `99dd454` on a genuinely truncated clone.** My `--depth 1` clone does not carry `99dd454`. I reproduced it on a real shallow clone at `f20b757`/`b34af6b` and attributed it to `99dd454` by `git log -S` plus a byte-identical diff of both arms across that range.
- **The shallow simulation exercises the decision path, not object truncation.** `.git/shallow` flips `--is-shallow-repository`, which is the discriminator the code reads; I validated it against a real `--depth 1` clone, which gives the identical outcome. It would not catch a defect that depends on objects genuinely being absent.
- **`governance.yml` itself.** I ran its steps locally; I did not dispatch a workflow run.
- **Local `prepr.sh` invocation counts.** Unmeasurable from here, so the cost test's left side counts only the 48 measured CI runs and is a floor.
- **Files outside the six you named.** I did not sweep `tools/`, the other `tests/*.py`, or the rest of `.github/workflows/`. There may be more sites; the two I found were both in the named set.
- **Whether the two site fixes survive `fix-review`.** They are prototypes in a scratch clone, never committed to the repository, and the second changes a pin total in one environment shape — a reviewer should re-derive that.
- **My own prototype's vacuity guard is imperfect**, and its null control is what showed me: `EXPECTED_SHAPES` counts directories that exist rather than setups that succeeded. The row-level `built` failure caught the bad-source case, not that guard. A landed version must fix it, or it is this class one level up for the third time.
- **Release status.** `git tag --contains 6438406` matches no `v*` tag, and `VERSION` is 6.3.18 with this session's stamp pending — so `defect-root-cause.md`'s first trigger (reached a released version) does **not** apply. Like 0002, this analysis stands on the recurrence rule, not on a red check.

---

## ADR text, if you want it landed

I have written no file. If you judge the class distinct, this is the text for `docs/decisions/0004-an-assertion-that-did-not-run.md`:

```markdown
---
status: accepted
supersedes: []
superseded-by: []
---

# 0004 — An assertion that did not run reads exactly like one that held

## Why this is separate from 0002 and 0003

`0002` is about an assertion's CONTENT: the pin says something other than what
the check does. `0003` is about a LIST that cannot be completed. This one is
about an assertion whose content is correct and whose REACHABILITY was never
measured — it did not run, and the run where it did not run is byte-identical
to the run where it did.

The evidence that it is its own class is that both earlier countermeasures
produced an instance of it while closing their own. `policy_lint_mutants.mjs`,
which `0002` exists to build, could not tell a check it had not measured from
one that survived its deletion. `99dd454`, which landed `0003` rule 5 and the
section that keeps it honest, added a shallow-clone arm to `checkProvenance`
and, in the same diff, an acceptance arm demanding a refusal that arm cannot
give.

## The five

    e3449a5   the provenance witness was guarded by `unreachable !== mainSha`.
              On a pull request the guard holds; on `push: branches: [main]`,
              which governance.yml also runs, the pushed commit IS origin/main,
              the guard goes false and an emptied checkProvenance passes with a
              byte-identical 54-pin summary.
    e3449a5   `pins += 3` sat outside the branch that runs the drive, so a
              clone with no origin/main printed the full 54. 51 after 310606f.
    99dd454   policy_lint_mutants.mjs reported ACCEPTED ... DELETABLE IN
              SILENCE, rc=1, for a check the clone could not ask about. The
              acceptance had said `skip provenance-pin` in the same run; the
              lane read its null control's exit code and not its output.
    6438406   check-wave-script.mjs discovers its population by scanning a
              DIRECTORY. Zero rosters print `ok` and `26 passed, 0 failed`.
              Merged as #611; the archive pass took the population from 84
              stages to 59 with no line of output changing.
    99dd454   the acceptance demands checkProvenance REFUSE a SHA no object
              carries. In a shallow clone the check declines instead, and
              policy_lint exits 1 under a message asserting "this clone is not
              shallow" four lines below one saying it is.

The last two were live at #618's head when this was written.

## The cause

**A check's environment-dependence is reasoned about where the check reads the
environment, and not where the assertion that drives it does.** Every instance
has an author who thought about the environment correctly one level down.

## Process state: (c), followed and did not produce the intended result

Three instructions cover this and all three predate every instance:
`defect-root-cause.md`'s "demonstrated failing on the defect", `root-cause.md`
§5's "does not go green by skipping", and `fixer.md` step 3's "an 'every' or a
'none' is a measurement". Each was obeyed. Every one is scoped to THE RUN THE
AUTHOR PERFORMS, and none to the runs the check will later perform elsewhere.
A firmer instruction is what `root-cause.md` says to suspect, so the answer is
mechanical.

Not (a): `tests/closure.py` fails open to `MODE: FULL` on every environment
failure and prints the mode line, and `tests/entities.py` (b6a21f1, #519, two
days before 99dd454) says "a shallow clone cannot answer this" in the message
of the check that cannot answer. The knowledge was in the tree; nothing carried
it to the next assertion of the same shape.

## The decision

**Declare the environment shapes, and require each one's outcome.** A lane runs
the governance checks in the shapes the repository says it supports — a pull
request, the push to main, a clone with no origin/main, a shallow clone, and a
scan whose population is empty — and fails a shape whose declared outcome does
not hold. A shape that could not be built fails; a matrix that ran a subset
certifies nothing.

Three constraints on it, each from an earlier decision:

1. **Derive the shapes that can be derived.** `pr` and `push-main` are
   `governance.yml`'s `on:` triggers; `shallow` is the complement of its
   `fetch-depth: 0`. Read them from that file. Rows that cannot be derived are
   declared hand-kept on the line, because `0003` rule 4 is about exactly the
   two lists that must agree.
2. **Declare the property, not one spelling of it.** "An undrivable arm is said
   out loud and not claimed" is checkable as `pins < full && a skip line
   printed`; asserting the skip line's exact text tests the fix rather than the
   property. This was found by the row that failed on a correctly fixed tree.
3. **The lane's own vacuity guard counts setups that SUCCEEDED**, not
   directories that exist. The first draft got that wrong, and its null control
   is what said so.

## The cost test

    standing        8.2-8.9s per run, six runs, five hardlink clones (0.11-0.12s
                    each) plus three policy_lint, three mutants and one
                    wave-script run. Against 1.25-1.50s for policy_lint,
                    0.83-0.88s for the mutation lane beside it and 21.6s for
                    tests/entities.py, all measured on the same box the same
                    day. The 1.3s recorded in 0002 for the mutation lane does
                    not reproduce; that figure is again a carried literal.
    cost(defect)    480s measured (99dd454 11:22 -> e6230a3 11:30, one review
                    round, one instance) and 1200s for the round that found two.
                    The two review did NOT catch cost more: 52 minutes and
                    11h40 of undetected life.
    P(recurrence)   measured: 5 instances in 11.7 hours, 0.43/h, roughly 0.5 per
                    commit touching these lanes.
    the test        break-even is 480/8.4 = 57 runs per catch. Observed: one
                    instance per 9.6 governance runs, from the 48 governance
                    runs the API records for 2026-09-08. Margin ~6x at the most
                    conservative reading of both sides.
    both sides are wall-clock, as the policy requires, but the left is machine
    time and the right is agent time. Weighting agent time higher only widens
    the margin.

## The bound

`.mjs` is code under `0003`'s inverted blocklist, so no `policy_budgets` cap
applies, and `structure_budgets.json`'s metrics are all over
`custom_components/`. Measured with the lane added and both sites fixed:
`TOTAL: 0 error(s) across 35 policy file(s)`, `FIXTURE ok ... 57 pins`,
`ALL 1112 ENTITY CHECKS PASSED`. No budget raise.

## What it does not cover, measured rather than inferred

Its granularity is the shape, so it covers a lane whose outcome differs by
environment. It does not cover an assertion unreachable for a reason that is
not an environment fact — a code anchor that stopped matching is `0002`'s
`CRASH` verdict, not this. It does not cover a shape nobody thought to declare,
and that is the residual `0003` rule 1 cannot remove here: there is no
`git ls-files` of environments. Deriving three of five from `governance.yml` is
how much of that can be bought.

Two residuals stay named rather than closed. `brief_lint.mjs` downgrades a
rotted tag citation to a warning in a clone missing the tag — disclosed on the
line, the same trade `SKIP` makes. `tests/entities.py`'s handover check exits
128 on a shallow clone and reports a failure — measured, `--is-ancestor
6438406 HEAD` gives rc=128 shallow and rc=0 full — which is a false red whose
own message names the cause. Both are wrong in the direction that reports.
```