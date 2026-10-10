# RCA — the orphaned-handoff class

Seat: root-cause, **beside** the fixes (`dev/governance/roles/root-cause.md`).
Trigger: the third-and-fourth instance in one evening; `dev/governance/rules/defect-root-cause.md`
and the working rule "a recurring error is not a third issue".
Bases: **main `7cd5a588c`** (remote tip, `git ls-remote origin refs/heads/main`), measured
**2026-10-10 00:50–01:20 CEST (+0200)**; earlier passes against `23d354970` are labelled where cited.
Evidence: `rca-orphaned-handoff/evidence/` (first pass, base `23d354970`) and
`rca-orphaned-handoff/evidence2/` (second pass, base `7cd5a588c`).
Scripts: `rca-orphaned-handoff/scripts/`.

**I did not die on a 429 and this is not unmeasured.** The coordinator's resume note says "nothing is
lost and nothing is measured yet"; the first is true, the second is not — this session had already
enumerated the refs, joined them against the pull-request API, classified them by
`git cherry` patch-equivalence, run the delivery ledger against main, and read `bus.sh`,
`open_pr.sh`, `handoff_push.sh`, `record_row.py`, `brief_lint.mjs`, `roster_edit.py` and
`delivery_status.py`. Main moved under me mid-session (`23d354970` → `7cd5a588c`), so every figure
below was re-taken against `7cd5a588c`; the first pass is kept as a second sample and the tip
movement between them is itself evidence (§1.4).

---

## 1. The class's true size

### 1.1 The number the owner asked for

| | count | how |
|---|---|---|
| `handoff/*` refs on the remote | **212** | `git ls-remote --heads origin 'refs/heads/handoff/*'` |
| `handoff-body/*` refs on the remote | **57** (58 by the last run) | `git ls-remote --heads origin 'refs/heads/handoff-body/*'` |
| pull requests enumerated | **1298** (5 open) | `/pulls?state=all&per_page=100`, 13 pages, 0 page failures |

The 212 partition two ways, and the two ways must not be confused — they answer different questions:

```
by whether a pull request carries the work          by whether a body ref made one owed
  delivered                                          with handoff-body/<t>   57
    via a body ref                    50               delivered          50
    without one                       85               ORPHAN              7
  ORPHAN                               7            without handoff-body/<t> 155
  no pull request and never owed      70               delivered          85
    (state, evidence, planning,                          not delivered      70
     prototype refs)                                  ----------          ---
                                      ---                                  212
                                      212
```

So the headline figures: **7 refs carry work no pull request carries** — **6** with no pull request at
all and **1** whose open pull request was left behind by its own later commits (§1.6) — plus 135 refs
the repository or a live pull request already carries, and 70 refs that never owed a pull request at
all. `135 + 7 + 70 = 212`. The 155 without a body ref are the countermeasure's null-control population
(§5.3): 85 of them are delivered and must not be reported either.

### 1.2 The seven, each measured

| topic | tip | age | commits no live PR and not main carries | first measured |
|---|---|---|---|---|
| `r9-eg-coordinator-seams` | `301abb21c2` | **89.9 h** | 1 | 2026-10-06 |
| `r9-ux-10` | `bcbc1af3ba` | **54.4 h** | 4 | 2026-10-08 |
| `r9-early-cutoff` | `5258d8559e` | **13.4 h** | 4 | 2026-10-09 |
| `r9-dbg-2` | `c901f8f34f` | **10.5 h** | 7 | 2026-10-09 |
| `r9-ux-6` | `66c1acf08a` | **9.2 h** | 9 | 2026-10-07 |
| `r9-ux-7` | `88c04a1722` | **9.1 h** | 8 | 2026-10-07 |
| `r9-ux-10-v2` | `27415fa539` | **9.0 h** | 8 | 2026-10-09 |

`commits no live PR carries` = `git rev-list --count <tip> --not <main> <every open PR head>`.
For all seven, `git cherry <main> <tip>` finds **zero patch-equivalents in main**, so none of this
work landed by a squash or a re-cut: it is on the ref and nowhere else.

**The seven are two repairs, not one**, and the split is load-bearing (§1.6):

- **6 lanes with no pull request at all** — `r9-eg-coordinator-seams`, `r9-ux-10`, `r9-ux-6`,
  `r9-ux-7`, `r9-ux-10-v2`, `r9-dbg-2`. Each needs an **opener**
  (`tools/audit/seat/open_pr.sh <topic> <code-sha> <title> <group>`).
- **1 lane whose open pull request was left behind by its own later work** — `r9-early-cutoff`,
  #2070, whose head is a strict *ancestor* of the ref. It needs an **update**
  (`tools/audit/seat/update_pr.sh <branch> <code-sha|-> <body-file>`, which merges the code head and
  `origin/main` into the existing PR branch and pushes as `hpo-author`), and dispatching an opener at
  it would open a second PR for work one PR is already carrying.

Against the brief's three instances: `r9-ux-10`, `r9-ux-6`, `r9-ux-7` are all confirmed. The
"mirror case" `r9-dbg-2` is **not only a mirror** — its seat, having found its group already merged,
wrote a new fix and pushed it to `handoff/r9-dbg-2` between 18:13 and 22:35, and that ref is a fourth
orphan with 7 unlanded commits. And two the brief does not name: `r9-eg-coordinator-seams` holds
`tools/audit/harnesses/eg_b7_seam_hubs.py` (81 lines, "R9-EG-B7: halt, no coordinator seam
detached"), **not in main**, 90 hours old; `r9-early-cutoff` is a different and sharper shape (§1.6).

### 1.6 The other shape: a ref that moved under an open pull request

`r9-early-cutoff` is **not** a lane with no pull request. It has one — **#2070 is open**, at head
`a9ba0b8874`. What the ref holds is the round of work that arrived *after* the PR opened:

```
$ git merge-base --is-ancestor 54391b3c7 a9ba0b8874   # the review-round-4 fix
  NO
$ git rev-list --count a9ba0b8874..5258d8559e         # ref side only
  122
$ git rev-list --count 5258d8559e..a9ba0b8874         # PR side only
  0            -> the PR head is a strict ANCESTOR of the ref; the ref is a superset
```

The four commits beyond it, pushed 14:41–19:40 on 2026-10-09, are #2070's own review round 4:

```
54391b3c7  fix(live-6): review round 4 of #2070 -- early_cutoff null control + defrost-off killing check
58e1c89df  ledger(live-6): #2070 r4 -- 4 structure-killed pins + 2 equivalent triage rows
2e411523b  ledger(live-6): #2070 r4 -- pin early_cutoff:190 (killed by tests/config_flow_steps.py)
5258d8559  Merge remote-tracking branch 'origin/main' into round4-early-cutoff
```

So **#2070 is open at a head that predates its own review round**, and nothing moved it. If it merges
as it stands the null control, the killing check and the four ledger pins are lost silently — the
revert-with-no-conflict shape this programme has already paid for. The same cause produces this: the
ref appeared and moved four times tonight, `bus.sh watch` reported each move once, and no arm of
anything asked whether the open pull request had been moved with it (`update_pr.sh` is the instrument;
nothing invokes it). This is why the class's size is not the same question as "how many lanes are
waiting" — and why the countermeasure reports the *shape*, not just a count.

`r9-cop-duty-floor` is the third shape, a **divergence** rather than a superset: 62 commits the PR
head (#2066) lacks and **1 commit the ref lacks** (`git rev-list --count` both ways). A blind "push
the ref to the PR" would drop that commit (§5.4).

### 1.3 Three false positives the name-based method produced, and why

The obvious join — `gh pr list --head fix/<topic>` — over-reports, because the orchestrator does not
always open at `fix/<topic>`:

| topic | the PR that exists | head |
|---|---|---|
| `r9-stale-ledger-pins` | #2073 (merged 2026-10-10) | `fix/rca-stale-ledger-pins` |
| `r9-cop-duty-floor` | #2066 (open) | `fix/cop-duty-floor` |
| `r9-live-power-clamp-foundation` | #2065 (merged) | `fix/live-power-clamp-foundation-pr` |

A name-only join reports 10; adding the commit-ancestry arm drops it to 7. The reverse arm is not
sufficient either: ancestry over-reports on a lane whose PR branch was squashed or re-cut, and
`git cherry` over-reports on a lane squashed into one commit — both measured on the September lanes
(§1.5). **So the class predicate needs both arms**; that is a design constraint on the
countermeasure, not a footnote.

### 1.4 The class is producing new instances while this runs

Two enumerations 25 minutes apart, same remote:

- **three new `handoff/*` refs appeared**: `r9-autofix-governance`, `r9-early-cutoff-r5`,
  `r9-row-stale`;
- **four orphan tips moved** — `r9-ux-6` `b5a3167989`→`66c1acf08a`, `r9-ux-7`
  `226e6fc241`→`88c04a1722`, `r9-ux-10-v2` `f9809c06ae`→`27415fa539`, `r9-cop-duty-floor`
  `386b7e2ff7`→`025b779c41`;
- three PRs merged and the open count fell 8 → 5.

So the recovery seats for these very lanes are **adding to the pile**: `handoff/r9-ux-10-v2` was
created by the recovery seat as its own handoff and is itself an orphan nine hours later. A class
that regenerates from its own repair is not on a path to closing by attention.

### 1.5 How far the class reaches

A wider search (`scripts/class_search.py`) drops the body-ref juncture and reports **24** refs
carrying unlanded production/test paths — 18 of them from **before** the body protocol existed
(2026-09-26 → 2026-09-30). I resolved two of the six `resume.stage: done` ones and both **delivered**:
`r9-f1-coordinator-5` → **#1751 merged**, `r9-f7-entities-2` → **#1764 merged**, each with a delivery
row in main reading `**merged`** and each at a PR branch named exactly `fix/<topic>` — their handoff
commits are unreachable only because the seat re-cut the branch ("PR branch squashed at 1c4d70fd").
Two of the remaining four carry commit subjects that say what they are: `r9-f9-test-pins-3`'s
uncovered commit is `transport: F9.2 PR body and resume note`; `r9-rca-p1`'s two are
`P1 barrier prototype: class sweep arm …` and `DEMO ONLY, not the fix`. **I checked 2 of 18 by
inspection and 6 of them by name against the PR API; I did not classify the rest**, so I do not claim
18 more instances of this class. What I can say: the same shape reaches refs that never owed a pull
request, which is exactly the noise the countermeasure must not emit.

---

## 2. The cause, established and not accepted

root-cause.md §1: reproduce it, and check which side moved. The cause has **three junctures**; the
first is the one the class is named for.

### 2.1 Nothing mints an obligation when a `handoff/*` ref appears

`tools/audit/seat/bus.sh` is the programme's ref bus and **does** see the family — `watch` prints one
line per changed ref in all four families, including `BUS handoff <name> <sha>`. But:

- `watch_once()` writes the new snapshot over `$S/refs` on every pass (`printf '%s\n' "$cur" > "$S/refs.new" && mv …`),
  so each change is reported **once** and never again. The bus is **edge-triggered with no
  level-triggered re-read**: a ref that appeared while the watch was not running, or whose one
  report the session did not act on, is never mentioned again. The header says so: "each change is
  reported once".
- The `case $kind in` block inside `watch_once` has arms for **`review`** and **`verdict`** only.
  A `handoff` ref prints its line and nothing else — the bus's own self-test pins exactly that and
  nothing more: it pushes a handoff ref and asserts
  `grep -qx "BUS handoff t1 $(git -C "$W/seat" rev-parse HEAD)"`, immediately beside
  `grep -qx "BUS review 7 $r1"` and the `BUS unconfirmed` assertion that follows it. The review family has a full obligation
  machinery — `dispatch` mints a nonce, `dispatched_to()` prints `BUS undispatched` when a review tip
  has no dispatch record for its PR and head. **The handoff family has neither a nonce nor a
  counterpart check.**

That asymmetry is the named cause: *the bus reports a handoff ref's appearance and mints no
obligation from it, and the one-shot report means nothing re-reads the level.*

### 2.2 The two records that would show it are claims, never re-derived

- **`roster_edit.py set-stage`** refuses only an empty value: `if not isinstance(stage, str) or not stage.strip(): raise Refuse("stage must be a non-empty string")`.
  `set-resume --field branch` likewise takes any text. There is no vocabulary and no verification
  against the remote.
- **`brief_lint.mjs` runs in CI** (`tests.yml:518`) and its only check on the field is
  `typeof g.resume.stage !== 'string' || !g.resume.stage.trim()` → *"missing or is not a non-empty
  string"*. Its own comment states the reasoning: *"only the exact string `done` skips a brief, so
  every misspelling already fails safe by linting MORE"*. That is sound for **whether a brief gets
  linted** and backwards for **whether a lane is finished** — the two purposes share one field and
  only one of them was designed for.

Measured, at the roster tip `955aaa724b` (`handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json`,
166 groups, stages: `done` 140, `in-flight` 7, `fixing` 7, `handoff` 3, `not-started` 7, `rca-done` 1,
`deferred` 1):

| group | roster `stage` | roster `branch` | does that ref exist? | what the real ref holds |
|---|---|---|---|---|
| R9-UX-6 | `fixing` | `handoff/r9-ux-money` | **ABSENT** | `handoff/r9-ux-6` holds 9 unlanded commits |
| R9-UX-7 | `fixing` | `handoff/r9-ux-model` | **ABSENT** | `handoff/r9-ux-7` holds 8 |
| R9-DBG-2 | `handoff` | `fix/r9-dbg-2` | **ABSENT** | `handoff/r9-dbg-2` holds 7 |
| R9-UX-10 | `handoff` | `null` | — | `handoff/r9-ux-10` holds 4, `-v2` 8 |
| R9-EG-B7 | `done` | `handoff/r9-eg-coordinator-seams` | exists | that ref holds 1 harness, not in main |

**Three of five `branch` values name refs the remote does not have**, and the refs that *do* exist
carry the work. A seat picking a lane up cold follows `branch` and finds nothing.

**The sharpest instance is not a missing field but a recorded one.** `R9-EG-B7`'s `resume` carries

```json
{"stage": "done", "branch": "handoff/r9-eg-coordinator-seams",
 "commit": "301abb21c2fce2e45419e6a67d4d59828c1d1e8d", ...}
```

and that SHA — `301abb21c2`, the tip of the orphan in §1.2 — **is not an ancestor of main** and is not
carried by any pull request. So the record holds a machine-readable pointer to unlanded work and
reads `done`, and no check compares a recorded `commit` against the tree. A reconciliation does not
need a new field here; it needs to *look at the one already there*.

### 2.3 The row's status word is never reconciled against the repository

`record_row.py` writes `dev/programme/delivery/<N>.md` as `— **open**, <title>` when the PR opens.
It can never upgrade that line, because **both** halves of its write path skip an existing row:

- `has_row()` (line 146) answers on the row file's **anchor** and prose mentions — never on its
  status; `plan_merges()` (line 179) is `if has_row(n, root): continue`;
- `write_rows()` likewise: `if target.exists(): continue` — *"a row file that already exists is left
  alone"*.

And the only checker grades presence: `tests/delivery_status.py`'s `classify()` sets
`state = "rowed" if has_row else (…)`, so a row that reads `**open**` for a merged PR is `rowed`.

Measured against main `23d354970` (`scripts/stale_rows.py`, joining main's row files to the API):

- rows in `dev/programme/delivery/`: **499**; reading `**open**` for a PR the API reports **MERGED**:
  **100** (PRs 1845–2078); correctly reading `**merged**`: 348;
- inside the ledger's **own** window (`v6.7.17..origin/main`, 15 merges): **15 of 15** are
  false-rowed, and `python3 tests/delivery_status.py --check` prints
  `DELIVERY STATUS OK — 15 rowed, 0 pending, 0 overdue` and `every merge in the window carries a row`,
  **exit 0**.

The brief's "24 rows" is the `>=2040` subset of the same measurement; tree-wide the count is **100**.
Nothing derives a rendered statement from the status word — `state_docs.py`, `plan_table.py` and
`resume_doc.py` do not read the rows — so the false rows mislead a **reader**, and the reader is the
seat that decides what to dispatch. That is the mechanism behind the brief's own report that "tonight
my status answers to the owner were drawn partly from generated documents built on those 24 false
rows": the record cannot be read without inheriting its staleness, and no check contradicts it.

### 2.4 The three candidate shapes, tested

**(a) "the handoff→PR step is owned by a human-shaped attention loop rather than an instrument"** —
**refuted as stated.** `open_pr.sh` is one atomic instrument: fetch `handoff/<t>` *and*
`handoff-body/<t>`, assert the code head is under the ref, add a worktree, merge main, push as
`hpo-author`, read the PR number out of the push log, retitle, un-draft, **write the delivery row**,
re-push, print `PR=N HEAD=H AUTHOR=…`. It fails closed at each step
(`|| { grep -E 'REFUSE' $D/p1.log; exit 1; }`, `|| { grep REFUSE; exit 1; }`). `handoff_push.sh` is the
same instrument with a `[ -n "$N" ] || exit 1` on the PR number. The step is instrumented; **deciding
to invoke it** is what is un-owned. What (a) predicts that the tree does not show: hand-made PRs with
inconsistent titles and no delivery row. Instead **4 of the 5 open PRs** carry an instrument-written
row in the PR head (#2063, #2066, #2070, #2072; #2075 has none, which is the ledger's ordinary
*pending* state), and 348 rows read `**merged`** — the instrument is being used, just not always.

**(b) "the roster `stage` is written by whoever remembers, and a seat that hand-offed without the
orchestrator seeing it leaves `not-started` behind"** — **supported in mechanism, mispredicted in
observation.** Yes it is free text (§2.2). But the observed rows are not `not-started`: they read
`fixing`, `handoff`, `done` on the orphan lanes, and they name branches that do not exist. The record
**was** updated and the update is wrong in a way no check can see. That is (c), not (b) — and the
(b)-shaped countermeasure has already been tried: tvofi's 2026-10-08 ruling *"never leave a PR/head
without a seat; run the dispatcher watcher all session"* is a firmer instruction, and within 24 hours
there were 7 orphan refs. Per root-cause.md §2, recording this as (b) would produce exactly the
countermeasure that has already failed.

**(c) "the bus mints a nonce for a review but nothing mints an obligation when a `handoff/*` ref
appears"** — **supported at code level** (§2.1), with the sharper form that the report is
edge-triggered and therefore consumed once.

**A correction to my own brief, in this direction.** The brief states that
`tools/audit/seat/undispatched.sh` "enumerates the inverse — PRs with no dispatch". That file does not
exist: not in the tree at any path, not under `/tmp/r9-orch`, `/Users/timmalmstrom/hpo-orch`, or
`~/.local/state/hpo`; `grep -rn undispatched` over `tools/ tests/ .github/ .claude/ dev/` matches
**only** `bus.sh`, where it is the **review** family's verdict. So the one level-triggered enumeration
the programme believes it has is (i) pointed at the review family, not at handoffs, and (ii) not in
the tree. Also corrected: the brief says R9-UX-7 has "no body ref at all" — `handoff-body/r9-ux-7`
does exist (`4364ced49e`), which is *worse* for the class, because it means `open_pr.sh` could have
opened it with no missing precondition.

---

## 3. The process state

### 3.1 **(c) The process was followed and did not produce the intended result.**

The process exists and is documented, in the bus's own header: *"Seats publish on refs; the
orchestrator watches them; the coordinator is left to start seats and handle blocks."* It ran. Every
check it passed is green:

- `bus.sh watch` reported each handoff ref's appearance exactly once, as designed;
- `brief_lint.mjs` lints the roster in CI and accepts `fixing`, `handoff`, `done` and any other
  non-empty string;
- `tests/delivery_status.py --check` prints `OK … every merge in the window carries a row`, exit 0,
  over a window in which 15/15 rows are false.

**A record-reading detector would have caught none of the seven.** Read the record for each: 2 of the
7 are named by a roster group and both read healthy work-in-progress (`R9-DBG-2` = `handoff`,
`R9-EG-B7` = `done`); 5 are named by **no** roster group at all (the roster's `R9-UX-6`/`R9-UX-7`
entries point at `handoff/r9-ux-money`/`handoff/r9-ux-model`, which do not exist, and nothing names
`handoff/r9-ux-10`, `-v2` or `r9-early-cutoff`); **zero** read `not-started`. A detector that reads the
record therefore sees a lane in progress and dispatches nothing — or, as the brief reports, reads a
stale record and states a confident wrong fact to the owner. That is the mechanism, and it is why the
countermeasure in §5 is an enumerator over the **repository**, not over the record.

**Which check could have caught it, and why it did not fire.** The cheapest detector that would have
caught all seven is the predicate in §5: three `git ls-remote` passes and local ancestry
tests, **10.6 s**, no GitHub token, no network beyond the ref listing. It did not fire because it does
not exist; and the three checks that *do* exist each grade a different question — the bus grades
*change*, `brief_lint` grades *shape*, `delivery_status` grades *presence*. A record read as answering
"is this lane done" is answering "does a row exist", and that is the confident-wrong-statement
mechanism the brief names.

**Why not (a).** A check on the roster exists and runs in CI (`tests.yml:518`), and a ledger over the
rows exists and runs on every push to main. "Nobody checked" is false. **Why not (b).** The firmer
instruction was issued on 2026-10-08 and the class recurred within a day; `roster_edit.py set-stage`
was used as designed. **Why not (d).** Tested and set aside as the state, though it is real and
aggravating — see below.

### 3.2 (d) checked: the precondition *did* change, and it is not the discriminator

The obligation's population is new. `handoff-body/*` refs did not exist before **2026-10-04**; the
body travelled as a commit inside the handoff ref until then (`handoff_push.sh` still carries that
read path). Owed refs by day, from the refs' own tip dates:

```
2026-10-02   0     2026-10-06   1     2026-10-08  18
2026-10-03   0     2026-10-07  21     2026-10-09  16
2026-10-04   1
2026-10-05   0
```

Nine-fold exposure growth in three days, against an edge-triggered watch that wakes a session once
per ref. But (d) predicts **zero** instances before the change, and the wider class search finds refs
carrying unlanded production paths from **2026-09-26**; and the pre-change lanes I could resolve
(#1751, #1764) **delivered**. So the change is why the class went from occasional to nightly, not why
it is possible. Naming (d) would licence a countermeasure that only notices its own precondition —
which is the right *shape* of fix (§5) attached to the wrong state, and the record would then read as
though the window were the bug.

### 3.3 A second detector hole, found by the search

`fold_ledger.py check` reports `28 classes, 549 instances, 101 rca entries, 0 violation(s)`. **This
class is not in the ledger at all** — no class id, no instances, no `_rca` entry — and the ledger
cannot report its absence because it only walks classes it already carries. A defect class can
therefore be invisible to the instrument that exists to demand a barrier for it. The class destination
in §6.2 addresses this.

---

## 4. The cost test, with numbers

```
cost(countermeasure, recurring) < cost(defect) x P(recurrence)
```

**cost(defect), per occurrence.** The brief supplies one measured value: a fresh opus seat spent
`duration_ms` **18482463** re-implementing R9-UX-10 before finding the orphan itself. That is **5.13
seat-hours** (18482463/3600000 = 5.134; the arithmetic is mine, the measurement is the launching
seat's session record, **not independently verified by me** — I have no access to it). I found no
second measured re-implementation to average against.

**P(recurrence), measured three ways on tonight's data** (`evidence2`, `scripts/reconcile.py`):

| basis | figure |
|---|---|
| orphans / refs that owed a PR | 7 / 57 = **12.3 %** |
| owed refs per day, 2026-10-07…09 | (21+18+16)/3 = **18.3 / day** |
| orphans/day implied | 18.3 × 0.123 = **2.25 / day** |
| orphans/day counted directly, tips 2026-10-06…10 | 7 / 4.0 days = **1.75 / day** |
| live orphans tonight over 2026-10-07 16:00 → 2026-10-10 01:00 | 7 / 2.7 days = **2.6 / day** |

**1.75–2.6 new orphans per day**, consistent with the coordinator's ~2.7. At 5.13 h each and the
unverified assumption that every orphan costs a re-implementation, the exposure is **9.0–13.3
seat-hours per day**. Tonight's *observed* cost is smaller and firmer: **5.13 h** (one
re-implementation) plus **four seats touched** (`r9-ux-6`, `r9-ux-7`, `r9-early-cutoff`'s round 5,
`r9-dbg-2`'s own seat) — I did not measure those four seats' durations, so I do not price them.

**cost(countermeasure, recurring).** Measured on the prototype (`scripts/orphan_enum.py`), arm 1 as
proposed: **10.6 s** per pass, over 212 refs and **1272 ancestry tests**, token-free. As a
`governance.yml` step on each push to main, plus the existing detached 15-minute loop for the window
between pushes, steady state is three `ls-remote` calls per beat. Ceiling: 60 pushes/day × 10.6 s +
96 beats × ~2 s ≈ **11 min/day of machine wall-clock, in parallel, needing no seat's attention** — its
output is a list, not a decision.

**Verdict: build it — the test passes with a margin of roughly three orders of magnitude**
(18 468 s of defect per occurrence against 10.6 s per run). The once-off cost of writing the check is
**not** part of the recurrence side; for completeness I estimate 2–3 seat-hours and label that an
estimate, not a measurement. It repays at the first prevented re-implementation.

**"No countermeasure" is not available here.** This is an audit class with **seven instances in one
round**, all of them aged past the window (9.0 h to 89.9 h), plus three refs and four moved tips in the
25 minutes between my two passes, so
`defect-root-cause.md`'s class trigger is met and a class-eliminating barrier is owed; the cost test
picks its form, not whether to have one.

---

## 5. The countermeasure, proposed and demonstrated

**Proposed owner: `bus.sh`.** It already enumerates the four ref families and already owns the
namespace's vocabulary; the asymmetry in §2.1 is one `case` arm and one predicate. A separate script
would be a second enumerator of the same refs, which is the shape `roster_lib`/`delivery_status`
deliberately avoid (`record_row.rowed_line` is `delivery_status.anchored`, "not a copy"). Proposed
surface: **`bus.sh orphans`**, with `watch_once`'s `case $kind in` gaining a `handoff` arm that asks
the counterpart question the `review` arm already asks.

### 5.1 The predicate — three junctures, and a fourth for the `done` case

For each `handoff/<t>` on the remote:

1. **OWED** — `refs/heads/handoff-body/<t>` exists. `open_pr.sh` fetches both and fails without the
   body, so the body ref is the protocol's own statement that this ref owed a pull request.
2. **DISCHARGED** — a pull request exists at `fix/<t>` or `fix/<t>-pr` (any state), **or** the tip is
   an ancestor of `main` or of any open pull-request head. Both halves are required (§1.3).
3. **AGED** — the tip's committer date is at least `--min-age-h` old (**default 2 h**).

**A fourth juncture, nearly free, for the `done` case** (§2.2): where the roster carries
`resume.commit`, `git merge-base --is-ancestor <commit> main` is **one git call, no ref listing, no
age window** — a lane recorded `done` at a commit main does not contain is a contradiction the record
itself supplies. It flags `R9-EG-B7` from the moment its `commit` was recorded and without reading a
single ref. It needs the roster, so it belongs to the orchestrator's beat rather than the CI step; the
CI step sees no roster.

Report the rest, one line each: `topic tip age_h uncovered_commits **which repair**`. The repair word
is not decoration: a lane with no pull request needs an **opener**, and a lane whose open pull request
is a strict ancestor of its ref needs an **update** (§1.6) — a watcher that prints only a count sends
the orchestrator to the wrong instrument for one in seven of tonight's lines, and at `r9-early-cutoff`
would open a second PR for work #2070 already carries. A **diverged** ref (neither an ancestor of the
other) is reported as a third word, `review`, because that one needs a human decision about the commit
only one side has (§5.4).

### 5.2 The demonstration, both runs

Prototype at `rca-orphaned-handoff/scripts/orphan_enum.py`, main `7cd5a588c`, run 2026-10-10 ~01:10 CEST:

```
RED ARM (as proposed)      REPORTED 7    exit 1
  skipped: {no-body: 155, named: 4, ancestor: 45, young: 1}
  runtime 10.6s (212 refs, 1272 ancestry tests)
  r9-dbg-2 c901f8f34f 10.5h uncovered=7 | r9-early-cutoff 5258d8559e 13.4h 4
  r9-eg-coordinator-seams 301abb21c2 89.9h 1 | r9-ux-10 bcbc1af3ba 54.4h 4
  r9-ux-10-v2 27415fa539 9.0h 8 | r9-ux-6 66c1acf08a 9.2h 9 | r9-ux-7 88c04a1722 9.1h 8

GREEN ARM (same code, same 212 refs, the seven excluded)   REPORTED 0   exit 0
  skipped: {no-body: 154, named: 4, ancestor: 45, young: 2, excluded: 7}
```

**What the green arm is and is not.** It is the same code path over the same population with no
orphan present, and its skip counters show it is **not green by skipping** — it still walked all 212
refs and filtered them one juncture at a time. It is **not** an independent control: the exclusion is
a fixture hook, not a repaired tree. `defect-root-cause.md` wants "failing on the defect and passing
once fixed"; the defect is live and I may not fix it, so **the fixture-driven both-arms arm is owed by
whoever lands the check**, driven from `tests/entities.py` the way `tests/delivery_status.py`'s
OVERDUE arm is ("A threshold that never fires is the always-green shape this repository keeps
catching, so `tests/entities.py` drives BOTH sides from fixtures").

### 5.3 The null control — each arm shown load-bearing on live data

| arm | junctures | REPORTED | of which not real | runtime |
|---|---|---|---|---|
| as proposed | body + name + ancestry + age | **7** | 0 | 10.6 s |
| `--no-ancestry` | body + name + age | 52 | **45** (all `uncovered=0`) | 6.4 s |
| `--no-body` | name + ancestry + age | 112 | ~100 (planning, prototype, state refs) | 89.3 s |

Removing either arm floods the output, which is the evidence that neither is decorative:

- **`--no-body`** reports `repo-reorg-plan` (78 uncovered), `silent-windows-plan` (75),
  `audit-r9-plan` (338), the eleven `r9-rca-*` prototype refs, `r9-row-stale` (3) and `r9-web-5` (1)
  — refs that by construction never owed a pull request. The 155 no-body refs tonight are the null
  control population, and the check must be silent on every one.
- **`--no-ancestry`** reports 45 refs whose content is in main, all `uncovered=0`: `r9-ro-8/9a/10/11/12/13`,
  `r9-sw-5`, `r9-sw6`, `r9-sw-actuation`, `r9-ux-actions`, `r9-ux9`, `r9-stale-ledger-pins`,
  `r9-record-automerge`, `r9-record-path`, `r9-rca-*` — the de-prefixed-name and deleted-branch cases
  of §1.3. A name-only watcher is 45 false positives on one pass.
- **the age window is live, not decorative:** `young: 1` on the first pass and `young: 2` on the last
  — refs pushed inside the 2 h window, i.e. the legitimate "minutes between a seat's push and mine"
  null control. The window sits **well clear of both populations**: the youngest measured normal
  handoff→PR latency is **8.8 minutes** (PR #2070, handoff tip `01:16:00`, row commit `01:24:48`),
  and the youngest orphan is 9.0 h — a 61× margin below the defect and a 13× margin above the normal.

### 5.4 What the countermeasure refuses

**It reports; it never repairs.** It does not push, open, or update a pull request, and it does not
write a roster stage. Two measured reasons, and the second is the sharper one:

- **Conflating the two shapes double-acts.** A lane with no pull request needs an opener; a lane whose
  pull request is behind its ref needs an update. A watcher that opened a PR for every uncovered ref
  would open a second one for `r9-early-cutoff`, which #2070 is already carrying.
- **A diverged ref needs a choice the watcher cannot make.** `r9-cop-duty-floor`'s ref and its PR head
  have **diverged** — 62 commits the PR head lacks and **1 commit the ref lacks** (`git rev-list
  --count` both ways). `update_pr.sh` happens to be safe here by construction, because it starts from
  `origin/$BR` and *merges* rather than force-pushes; but the general question "which of two divergent
  heads is the one to keep" is a judgement about a commit only one side has, and a detector that
  answers it by pattern would eventually drop one. The repair decision stays with the orchestrator,
  who sees the divergence in the same line.

### 5.5 Where it runs

Both, and why each:

- **CI, preferred** (tvofi 2026-10-07: heavy scripts run in CI and seats cite check-runs) — a
  `governance.yml` step beside the `delivery-status` lane. It needs **no GitHub token**: the PR head
  branches are remote `fix/*` refs and merged PRs are covered by `main`, which is why the prototype is
  three `ls-remote` passes (`handoff/*`, `handoff-body/*`, `fix/*`) and local ancestry. It fits
  `delivery_status.py`'s stated property, "no token and no network … the two agreeing is a
  cross-check, and a token-dependent collector here would have turned a rate limit into an EMPTY".
- **A beat beside the existing `wt_sync.sh`** detached loop — **verified live**, not assumed:
  pid **32225**, `bash -c 'while true; do wt_sync.sh --scratch …; sleep 900; done'`, uptime
  **5 d 23 h 33 m** when read, currently in its `sleep 900` child. A 15-minute period, so the beat
  has an owner and a place already; CI only sees a push, and the window that matters is *between*
  pushes. The beat's steady-state cost is three `ls-remote` calls plus ancestry tests only for refs
  whose tip moved.
- **Registered, not only written**: the check takes a structured input, so it registers that input in
  `tools/policy/field_coverage.mjs` or declares none, per `defect-root-cause.md` ("a governance check
  is in the derived set and registers its input or declares none").
- **Paced**: one pass per 15 minutes at most, per the owner's 2026-10-07 ruling on the shared API
  quota — noting that this check makes **no** REST call, so it does not compete for the quota the
  seats share.

---

## 6. Where the finding goes

### 6.1 Propagation (`dev/governance/rules/finding-propagation.md`)

The finding invalidates an assumption a later stage rests on: *the roster's `branch` resolves, and a
row reading `**open**` means the pull request is open.* It binds **every orchestrator turn**, so its
destination is the **role contract**, once — not each stage's brief, which "goes stale unevenly" and
is the rule's own words. Both destinations are **policy**: I am offering diffs, not editing them, and
they need the owner's approving review before merging (`CLAUDE.md`).

**Offered diff 1 — `dev/governance/roles/orchestrator.md`** (new subsection, numbered to sit beside
the seat's other obligations):

```diff
+## Before dispatching a seat to a lane, read the ref, not the record
+
+The roster's `resume.stage` and `resume.branch` are a seat's own claim, written
+at the moment it acted; `roster_edit.py set-stage` accepts any non-empty string
+and nothing verifies `branch` against the remote. Measured 2026-10-10: three of
+the five orphaned lanes' `branch` values named refs the remote does not have,
+while the refs that do exist held 7-9 commits no pull request carried. Where the
+record carries `resume.commit`, `git merge-base --is-ancestor <commit> main` is
+one call and catches a lane called `done` at a commit main does not have.
+
+So before dispatching, ask the repository, not the record:
+
+    git ls-remote --heads origin "refs/heads/handoff/<topic>" \
+        "refs/heads/handoff-body/<topic>" "refs/heads/fix/<topic>" \
+        "refs/heads/fix/<topic>-pr"
+
+A `handoff-body/<topic>` ref with a `handoff/<topic>` ref and no pull request at
+either `fix/` name is a lane that **handed off and was never opened**: dispatch
+an opener (`tools/audit/seat/open_pr.sh`), never a fresh implementer. A pull
+request that exists but whose head is an ancestor of the ref is a different
+repair — `tools/audit/seat/update_pr.sh` — and dispatching an opener at it opens
+a second pull request for work one already carries. `bus.sh orphans` answers all
+of it for every ref at once; this rule is what to do with the answer.
```

**Offered diff 2 — `dev/governance/rules/delivery-status-tracking.md`**, under "Status stays true,
not just present" (the rule already says the right thing; this adds the measurement that a row's
*word* is not checked, and names the instrument):

```diff
+- A row's status word is not reconciled by anything: `record_row.py`'s
+  `has_row`/`write_rows` skip a row that already exists, so the `**open**` line
+  written when a pull request opened is never upgraded, and
+  `tests/delivery_status.py` classifies on the row's *presence*. Measured
+  2026-10-10: 100 rows in `dev/programme/delivery/` read `**open**` for a
+  pull request GitHub reports MERGED, and 15 of 15 merges in the ledger's own
+  window were among them while `--check` printed OK and exited 0. `bus.sh
+  orphans` (§5) is the level-triggered reader; until a row's word is graded,
+  read the API, not the word.
```

I do **not** propose editing `.claude/workflows/wave-*-groups.json`'s `resume` fields with this
finding: those are per-group state, and `finding-propagation.md` sends a finding that binds every
seat to the role contract once. The wave-9 roster is also out of tree
(`handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json`), so a carry written there would
not survive the session.

### 6.2 The RCA record

Per `defect-root-cause.md` §"Where it is recorded", the analysis belongs at
**`dev/audit/rca/R9-ORPHAN-HANDOFF.md`**, cited by `rca` in `dev/audit/config/bugclasses.json` — and
that file needs a class id, because **this class is absent from it** (§3.3). The shapes below are read
off that file's own entries (`N-silent-zero`, `_rca['RCA-1041-silent-zero']`), not invented. Offered,
not applied:

```diff
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
+  "N-orphaned-handoff": {
+    "kind": "instrument",
+    "mechanism": "An obligation is recorded and never enumerated: the bus reports a handoff ref once and mints no counterpart obligation, so a lane's work sits on the ref, main has not got it, and the record still reads in-progress or done",
+    "rounds": [9],
+    "instances": ["R9 EG-B7 (handoff/r9-eg-coordinator-seams)", "R9 UX-10 (handoff/r9-ux-10)", "R9 UX-6 (handoff/r9-ux-6)", "R9 UX-7 (handoff/r9-ux-7)", "R9 UX-10-v2 (handoff/r9-ux-10-v2)", "R9 DBG-2 (handoff/r9-dbg-2)", "R9 early-cutoff (handoff/r9-early-cutoff, PR #2070 behind its own round 4)"],
+    "per_round": {"9": 7},
+    "total": 7,
+    "max_per_round": 7,
+    "status": "prototype-only",
+    "nearest_existing": "I3",
+    "mechanism_difference": "I3 is a required governance or CI check skipped, stale or bypassable; this is an obligation that no check enumerates at all, and the three checks that do read it are green",
+    "detector_idea": "the three-juncture predicate in the RCA: a handoff-body ref, no pull request at fix/<topic> or fix/<topic>-pr, no ancestry in main or a live head, older than a measured window",
+    "barrier": null,
+    "rca_planned": ["R9-ORPHAN-HANDOFF"],
+    "trigger": {"per_round": true, "cross_round": false, "barriered_any": false, "class_rca_on_record": false}
+  },
```

and, in the pull request that lands the document at `dev/audit/rca/R9-ORPHAN-HANDOFF.md`, the `_rca`
entry it must cite — `fold_ledger.py check` refuses `UNKNOWN-RCA` for a citation with no index entry,
and `DANGLING` for an `in_tree_home` that is not a file under `dev/audit/rca/`, which is why the
citation is `rca_planned` above until the file is in the tree:

```diff
   "_rca": {
+    "R9-ORPHAN-HANDOFF": {
+      "class": "N-orphaned-handoff",
+      "level": "class",
+      "subject": "orphaned-handoff class: a handoff ref that owed a pull request and never got one (7 refs, 5 of them 9-90h old, one re-implementation priced at 5.13 opus-hours)",
+      "trigger": "recurring class (2, 3 and 4 instances reported in one evening; 7 in round 9, all 9.0-89.9h old)",
+      "date": "2026-10-10",
+      "status": "prototype-only",
+      "parts_missing": [],
+      "process_state": "(c) class; (a) residual: no level-triggered enumerator exists",
+      "countermeasure": "bus.sh orphans, token-free, 10.6s over 212 refs and 1272 ancestry tests; prototype demonstrated red on the defect, green with none present",
+      "in_tree_home": "dev/audit/rca/R9-ORPHAN-HANDOFF.md"
+    },
```

Both are decisions about the ledger's vocabulary and its class-id set, so they are the orchestrator's
or the owner's, not mine. This document is the input: **path
`rca-orphaned-handoff/RCA-ORPHANED-HANDOFF.md`**.

---

## 7. What I did not measure

State plainly, because a limit reported is a limit priced:

- **The 5.13 h re-implementation** is the brief's figure, taken from a session record I cannot read.
  I verified the arithmetic (`18482463 ms → 5.134 h`) and nothing else.
- **The four recovery seats' costs** (`r9-ux-6`, `r9-ux-7`, `r9-early-cutoff` round 5, `r9-dbg-2`'s
  seat) are not measured, so the class's observed nightly cost is quoted as 5.13 h plus four seats
  touched, not as a total.
- **The countermeasure's once-off build cost** (2–3 seat-hours) is an estimate.
- **18 of the 24 wider-search refs** were not classified individually; I resolved 6 by name against
  the API and inspected 2, and I do not claim the rest are instances.
- **The green arm** is a fixture exclusion on live data, not a repaired tree (§5.2).
- **`git cherry` and ancestry both under-detect** a lane squashed into one commit; I measured that
  limitation on #1751 and #1764 and it is why the predicate needs the name arm as well.
- The **delivery-row count of 100** is against main `23d354970`; the ledger window figure (15/15) is
  the same base. I did not re-run the row measurement against `7cd5a588c` — three PRs merged between
  the bases, so the true figure at `7cd5a588c` is 100 or slightly different, and the *third* of it
  inside the current window is what the recommendation rests on.

---

## 8. Evidence index

All under `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/amazing-engelbart-fa0a4f/rca-orphaned-handoff/`.

| file | what it is |
|---|---|
| `RCA-ORPHANED-HANDOFF.md` | this document |
| `scripts/orphan_enum.py` | the proposed countermeasure, prototype; `--no-body`, `--no-ancestry`, `--min-age-h`, `--exclude-topic` for the arms |
| `scripts/reconcile.py` | the name × ancestry × body reconciliation that produces the class's size |
| `scripts/collect_pr_heads.sh` | the `/pulls?state=all` walk, paced, counting its own failures (0 of 13) |
| `scripts/class_search.py`, `class_search_detail.py` | the wider search over refs carrying unlanded production/test paths |
| `scripts/stale_rows.py` | the independent re-measurement of the false delivery rows (100) |
| `scripts/latency.py` | handoff→PR latency attempt; **its output is not used** — it reported negative latencies because a PR's original open time is earlier than work pushed into it later, so only the one clean row (#2070, 8.8 min) is cited |
| `evidence/`, `evidence2/` | the two enumerations (bases `23d354970`, `7cd5a588c`): ref lists, `pr_heads.tsv`, `handoff_topics.tsv`, `body_topics.tsv`, `roster.json`, `class_reconciled.txt`, `orphan_by_commit.txt`, `class_search*.txt`, `stale_rows.txt`, `ledger_main.json`, `handoff_to_pr_latency.txt` |

No pull request, branch, comment or issue was written. `/private/tmp/r9-main` and the recovery
seats' worktrees were read only; the reference checkout was left clean (its only untracked path,
`.wt-r13/`, predates this session) and the ledger run was emitted to this scratch directory.

---

## 9. Fixer's addendum (2026-10-10): the countermeasure landed, and the content arm

This document is the root-cause seat's analysis, transcribed in-tree by the
fixer seat that landed the countermeasure. Sections 1-8 are the analysis's own
text and figures, taken at the bases it names; this section is the fixer's.

**The countermeasure.** `bus.sh orphans` (its owner is this document's class)
fetches the three ref families over the git protocol -- no token, no REST -- and
reports each owed ref in one of three states: `STRANDED` (a line, rc 1, naming
the repair it needs -- `opener`, `update` or `review`), `SUPERSEDED` (a line,
rc 0: main already carries it), `IN FLIGHT` (inside the two-hour window,
counted, never a line). It repairs nothing. `bus.sh --self-test` drives the red,
the three repair words, the content arm, the two null controls and a green
remote, so the gate keeps it drivable.

**A correction to sections 1.2 and 5: one of the seven is superseded, not
stranded.** `r9-eg-coordinator-seams` (`301abb21c`) was recovered by PR #2017
(`b281a4c37e7cf91c79f205906418b2c6696d0e93`, 2026-10-07); issue #1744 closed
2026-10-07T12:17:26Z. Its one file is on main at
`dev/audit/harnesses/eg_b7_seam_hubs.py` (moved from `tools/audit/harnesses/`
by the `dev/audit/` restructure), differing from the ref's copy only by a
docstring path line and the `parents[3]` -> `repo_root` block. The ref is
therefore **non-ancestral to main** (the recovery rewrote the commit) yet
**fully carried**. The ancestry arm alone reports it as stranded; the
content-equivalence arm (`content_superseded`: a modification byte-identical on
main, an addition whose basename main holds) reads it out. Measured on the live
remote, the arm is load-bearing and narrow -- with it on, `r9-eg-coordinator-seams`
moves to `SUPERSEDED` and no other ref moves; with `--no-content` it returns to
`STRANDED`. The counts are a function of `origin/main`'s tip and the clock;
re-take them at the head. The stranded list is therefore partly refuted by the
arm this document proposes, and the class's per-round instance count is seven
flagged refs of which one is superseded.

**Two stale records the same recovery seat found, named not fixed here:**
`dev/programme/delivery/2017.md` reads `**open**` for the merged #2017, and
`dev/programme/plan-2026-09-open-issues.md` still lists `#1744` as scheduled.
Both are the row- and plan-staleness section 2.3 measures.
