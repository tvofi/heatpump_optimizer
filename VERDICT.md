Fix review: merge a27c7bd4412989300170b2648c417e9d6e93f0a9

bus-nonce: f604a672477d1589fd0f4755d7b90a5c

# Fix review — PR #2117, `fix/r9-recarry-readback`

- Head measured: `a27c7bd4412989300170b2648c417e9d6e93f0a9` (unchanged at posting:
  `git ls-remote origin refs/heads/fix/r9-recarry-readback` and
  `gh pr view 2117 --json headRefOid` both still that sha).
- Merge base with `origin/main`: `7cd5a588cbbbef354c00148040da2d720b8a888c`.
  `origin/main` has since moved `tools/audit/seat/merge_train.py` (not
  `app_push.sh`, not `governance.yml`).
- Diff: 4 files, +203/−32 — `tools/pr/app_push.sh` (the bounded read-back),
  `tools/audit/seat/merge_train.py` (the re-read), `.github/workflows/governance.yml`
  (wires the self-test), `dev/programme/delivery/2117.md` (the row).

## What the finding is, and that it is real

The defect is an **incident, not an argument**: `/Users/timmalmstrom/hpo-seats/merge-train-0118/logs36/batch-1.log`
(evidence `finder_log.txt`) ends

```
app_push: RECARRY: prepr SKIPPED: HEAD 61617145 is the clean merge of the live head 1f9d606d and origin/main's 23d35497, and the body is the live one
app_push: REFUSE: the pull request did not read back; its state is above -- re-read it by hand before touching anything
RESULT pr=2071 head=61617145f4a2cc254f90b53ba683ea74f13100d4
TRAIN STOPPED recarry: #2071 the main merge pushed nothing: …
```

Two independent facts in one log: the branch **was** at `61617145f` (the push
landed) and the read-back refused anyway — and the same run recarried #2072
with no refusal, which is the natural control that says "race", not
"systematic". The body's narrative, its five-PR blast radius and its shas all
re-derive from this file.

## The harnesses I used, and whose they are (fix-review.md step 2 and 9)

The finding has **no committed finder harness** — its evidence is the incident
log above. Every arm below is therefore driven by a harness **I built**, and I
name it as mine, not the fixer's:

- `evidence/prod_readback.sh` — the production `RB_TRIES`/`RB_SLEEP`/`read_once`/`confirm_readback`
  sliced **verbatim** out of the head's `tools/pr/app_push.sh` (sha256
  `2507fa6fca5de4b0abc01c60591dc74cdfbf4ce8708acdacb82f1f6e1fe40da2`), lines 193–255.
- `evidence/drive_readback.sh` — my own fake `curl` (a switch on a mode variable,
  emitting real JSON), driving those functions in a temp state dir I own. **No
  network, no key, no push.** The stash of a live instrument was not touched.
- `evidence/drive_train.py` — my own fake `Train.run`, driving the production
  `merge_train.Train.one` recarry block, independent of the fixer's `go()`
  self-test assertions.
- For `merge_train` I *also* ran the PR's own `--self-test` and my own targeted
  mutant; where the two disagree I would say so — they do not.

## Q1 — all three outcomes are reachable and correct

`app_push.sh`'s read-back, driven at the code's defaults (`6`/`2s`) by my harness
(`evidence/arms_readback.txt`):

| arm (stubbed API read) | rc | reads | settles | wording |
|---|---|---|---|---|
| `ok` — visible on the first read | 0 | 1 | 0 | `PUSHED` |
| `race` — read 1 stale, read 2 at the pushed sha | **0** | 2 | 1 | `PUSHED` |
| `stale` — never visible (every read answers the old sha) | 1 | 6 | 5 | `pushed and not visible within the budget` |
| `error` — the read cannot be performed (curl exit 22) | 1 | 6 | 5 | `the read was refused` |
| `bad` — open, right sha, body differs | 1 | 1 | 0 | `body is not byte-identical` |
| `closed` — `state != open` | 1 | 6 | 5 | `the read was refused (the read answered state=closed)` |

- **A genuinely-landed push whose read-back races reports success** (`race`:
  rc 0, `PUSHED`, at the intended second read).
- **A push that truly did not land still REFUSES.** A refused push dies at the
  push itself (`push-fails` arm), before the read-back is reached — I read that
  path at `tools/pr/app_push.sh:406`; the arm asserts the refusal wording and
  `0` pulls calls. And a read-back that never sees the pushed sha refuses
  (`stale`, rc 1).
- **A persistent failure refuses rather than hangs** (`stale`, `error`: rc 1
  after 6 reads).
- No false positive exists in the shape I could find: `ok` requires the live
  head to *equal* the pushed sha, so a push that did not land cannot read `ok`
  unless the branch was already there (a no-op push, which is a real success).

## Q2 — the poll budget is BOUNDED, and stated

`RB_TRIES=${APP_PUSH_READBACK_TRIES:-6}`, `RB_SLEEP=${APP_PUSH_READBACK_SLEEP:-2}`
(head `tools/pr/app_push.sh:193–194`). The loop breaks on the first `ok`
(`ok) return 0`), else `[ "$attempt" -lt "$RB_TRIES" ] || break` before each
sleep — so at the defaults it is **6 reads, 5 settles, 10s of sleeping** (my
harness: `stale`/`error`/`closed` elapsed 10.5–11.0s wall). The body's numbers
(6, 2s, "→ ~10s") match the code's defaults and my measurement, and the budget
is printed, not implied (`app_push: read-back 1/6: …; sleeping 2s`). Garbage in
`APP_PUSH_READBACK_TRIES` makes `[ -lt ]` error, which `|| break` catches — the
loop still terminates after one read. **Bounded, not silently defaulted.**

## Q3 — merge_train's re-read behaves as the body says

Read at `tools/audit/seat/merge_train.py:495–512` and driven by my own harness
(`evidence/arms_train.txt`), settling `RECARRY_RESETTLE = 2`:

```
recarry-refusal-head-moved   rc=0 merged_at=['22222222'] settle_calls=[2, 30]
  | #7 recarry: app_push refused but the head moved to 22222222; the push landed, not a stop
  | TRAIN DONE
recarry-refusal-head-still   rc=1 merged_at=[]           settle_calls=[2]
  | TRAIN STOPPED #7 recarry: the main merge pushed nothing: REFUSE: …
recarry-pushed-ok (null control, normal PUSHED)  rc=0 merged_at=['22222222'] settle_calls=[30]
```

A refusal with a **moved** head carries on and merges (rc 0); a refusal with an
**unmoved** head stops (rc 1) and pays exactly **one** 2s settle (`[2]`); the
common `PUSHED` path pays **no** 2s settle (`[30]` only) — the settle is only on
the refusal path, as claimed. `h` is the pre-recarry live head (`one()` sets it
before the recarry), so `moved != h` is a genuine "the branch advanced" test.

## Q4 — the self-test still passes, and the change adds arms

- Head: `bash tools/pr/app_push.sh --self-test` → **110 checks, 0 failed**
  (baseline at the merge base and at `origin/main`: **91 checks, 0 failed** —
  the +19 are the three read-back arms and the two re-keyed assertions).
- Head: `python3 tools/audit/seat/merge_train.py --self-test` → **96 checks, 0
  failed** (baseline 95; one check re-keyed, one added).

## fix-review.md's steps

1. **Mutation proof re-run** (`evidence/mutation_proof.txt`). The three mutants
   named in the body reproduce **exactly** their claimed counts, and each
   restores clean:
   - M1 `[ "$attempt" -lt "$RB_TRIES" ] || break` → `break`:
     **7 failed**, all read-back arms.
   - M2 the `notvisible` branch deleted: **2 failed** (the two wording arms).
   - M3 `moved != h` → `False`: **1 failed** (exactly
     `a recarry refusal whose head nonetheless moved is treated as landed, not a stop`).
2. **Finder's harness**: none exists; disclosed above.
3. **Null control / both ends**: the unmodified tree is 91/0 and 95/0, and the
   origin/main `app_push.sh` blob carries **0** read-back-race tokens — the arm
   is absent at the baseline and present at the head. The fix's own clean-path
   control holds: `ok` spends 1 read and 0 settles.
4. **Drift**: the diff touches no `tests/golden/**`, no `claimed_drift.txt`, no
   `card_claimed_drift.txt`, no `*_budgets.json`, no `closures.json`. Nothing
   moved, so nothing is owed a claim (I did not spend the ~20-minute
   `env_drift.py --all` capture on a diff that provably reaches no fixture;
   the head's `env-matrix` ran green).
5. **`VERSION` / manifest / `RELEASE_NOTES` heading**: untouched (not in the diff).
6. **The class, opened by me**: I drove *every* verdict `read_once` can return
   (`ok`, `stale`, `body`, `bad`, `error`) plus the `*` fall-through, and both
   recarry outcomes. One call site of `confirm_readback`; the other `PUSHED`
   readers (`tools/pr/push.sh`, `handoff_push.sh`) are different scripts.
   Nothing is left un-dispositioned.
7. **Head**: the body's `a27c7bd4412989300170b2648c417e9d6e93f0a9` is the head I
   measured.
8. **Numbers re-derived**: 110/91/95/96, 7/2/1, `SCOPED -- 0` (the two code
   files) and `SCOPED -- 2` (with the workflow wiring), `STRUCTURE RATCHET
   PASSED` with every metric exactly at budget, `dS +0.0000 NULL`. All confirmed
   except one derived figure in a message — see Observations.
9. Covered above.
10. **Forward-carry**: the body says "none". I agree — the finding is landed in
    this PR (both instruments), nothing narrows or removes an option for a stage
    that has not started, and no `.claude/workflows/*.json` brief or
    `dev/governance/` file needs to know.
11. **Red checks**: read from the check-runs API, not the body. The head has 40
    runs, **none red**; the two earlier heads have none red either (48d47ab19's
    `cancelled` runs are superseded, not red). "Red checks: none" is honest.
12. **Head re-read**: unchanged.
13. **Conflict**: `git merge-tree --write-tree origin/main a27c7bd4…` exits 0
    with no conflict markers — `merge_train.py` on main has moved but not where
    this branch writes.
14. **Metric-gamed**: no budget, ledger, closure, `INERT`, golden, claim or
    score moves. Nothing to plant.
15. **Architecture** (judged on added lines): one owner per concern — the
    read-back in the pusher, the re-read in the train; the small surface
    (`read_once`/`confirm_readback` are local, not exported); side effects stay
    at the App edge; the `body` mismatch still refuses at once, so no existing
    refusal is weakened. Ratchet and archscore unmoved. Sound.

## Observations — recorded, NOT blocks

- The refusal message computes `$((RB_TRIES * RB_SLEEP))` = "**6 attempts over
  ~12s**", but only `RB_TRIES - 1` settles are spent, so the real budget is
  10s — which is what the body says and what I measured. The message
  over-states by one sleep; it errs in the safe direction and never
  under-promises.
- A `bad` read (`state != open`, e.g. a PR closed mid-flight) polls the whole
  budget and is then reported as "the read was refused", though a read *was*
  performed. Main refused that case immediately. Still bounded, still refuses —
  wording, not behaviour.

## RESULT

```
RESULT app_push self-test head         110 checks, 0 failed
RESULT merge_train self-test head       96 checks, 0 failed
RESULT app_push self-test baseline      91 checks, 0 failed   (origin/main blob)
RESULT merge_train self-test baseline   95 checks, 0 failed
RESULT mutant M1 (single-shot poll)      7 failed  (body claims 7)
RESULT mutant M2 (third outcome gone)    2 failed  (body claims 2)
RESULT mutant M3 (moved head ignored)    1 failed  (body claims 1)
RESULT read-back arm ok        rc=0 reads=1 settles=0
RESULT read-back arm race      rc=0 reads=2 settles=1
RESULT read-back arm stale     rc=1 reads=6 settles=5
RESULT read-back arm error     rc=1 reads=6 settles=5
RESULT read-back arm body      rc=1 reads=1 settles=0
RESULT train arm head-moved    rc=0 merged_at=22222222 settle_calls=[2,30]
RESULT train arm head-still    rc=1 stop settle_calls=[2]
RESULT train arm pushed-ok     rc=0 merged_at=22222222 settle_calls=[30]
RESULT closure --diff MB       SCOPED -- 2 (entities.py, harness_headers.py)
RESULT closure two code files  SCOPED -- 0
RESULT structure.py            RATCHET PASSED (no metric moved)
RESULT archscore --diff HEAD   dS +0.0000 NULL
RESULT merge-tree origin/main  0 (no conflict)
RESULT check-runs at head      40 runs, 0 red
VERDICT merge a27c7bd4412989300170b2648c417e9d6e93f0a9
```
