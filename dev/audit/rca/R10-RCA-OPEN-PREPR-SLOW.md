# R10-RCA-OPEN-PREPR-SLOW: `open_pr.sh` runs the full prepr where a receipt should have skipped it, and the full prepr has outgrown its slot cap

Root-cause seat, `root-cause.md`, 2026-11-10, three opens at merge base
`b0762725099f`. Every figure this document rests on is printed by a command in
the tree:

- `dev/audit/rca/open_prepr_receipts.py`, read from git alone, with
  `--self-test` as its null control. Its output for the measured window is
  frozen beside it in `open_prepr_receipts-tips.tsv` and
  `open_prepr_receipts-opens.tsv`; each file's first line is the command and
  the `origin/main` it ran against. Tips move and refs are deleted after merge,
  so a re-run reads a later corpus: re-derive against your own window.
- `git` reads at named commits (section 3, C-B).
- `dev/audit/rca/open_prepr_6d.sh`, step 6d's predictor timed at one head
  (section 6, C4).

**Cut in round 2.** Round 1's host readings (process tables, slot `taken_at`,
load, swap, `vm_stat`, `iostat`, a CPU-loop multiplier, spawn costs, `p1.log`
step lines and durations, and record-issue-continuation's self-test result)
were taken on the orchestrator's host into out-of-tree scratch. No enumerator
for them is in the tree, so no figure from them stands here. What they argued,
that the opens were neither queued on `gate_lock.py` nor hung, is **not
established** by this document; C3 is the countermeasure that makes it
re-derivable from `p1.log` alone.

## 1. The answer to the brief's question

Each open ran the full prepr because its `handoff-body/<topic>` tip carried no
`Prepr:` trailer, and `app_push.sh`'s `reuse_verdict` refuses on exactly that
("carries no one `Prepr: <sha> <tree>` trailer, so no receipt"). Two of the
three tips are `never` rows of the frozen snapshot; the third's tip moved after
the window. By the latency proxy of section 5, a full-prepr open takes several
times as long as a reused one, and the full prepr has grown under a slot cap
that does not see it (C-B).

## 2. The instances

| open | code head | tip in `open_prepr_receipts-tips.tsv` |
|---|---|---|
| r10-process-slim-p2 | `6671786843` | `never` |
| r10-hotfix-record-issue-continuation | `0d5c1124` | not in the window: the tip moved after it |
| r10-arbiter-off-restore | `c19017d6` (pushed) | `never` |

## 3. The cause

Two causes multiply.

**C-A: a receipt that `reuse_verdict` would accept does not reach the open.**
P386 (owner directive 2026-11-04, "a fixer's prepr is not repeated at open or
update") is built: prepr writes `hpo-prepr-receipt` in its checkout's git dir
after a passing full run; `body_push.sh`'s `prepr_trailer` copies it onto the
handoff body as `Prepr: <sha> <tree>` **only when the receipt's sha equals the
code head and the receipt is in the checkout running `body_push.sh`**;
`app_push.sh --reuse`'s `reuse_verdict` accepts any receipted code that is an
ancestor of the head when the head is the clean merge of it with main.

The class, as `open_prepr_receipts.py tips` splits it (its `RESULT` lines; the
window is 2026-11-06T00Z to 2026-11-10T03:30Z):

| field | rule |
|---|---|
| `code`, `trailer`, `no_trailer` | code bodies; with a `Prepr:` trailer on the tip; without |
| `same` | an earlier body on the same ref carried a trailer for the **same** code; the re-push dropped it |
| `merge-only` | the earlier trailer's code is an ancestor, and only merges lie on the ancestry path between |
| `non-merge` | an ancestor, with a non-merge commit on that path |
| `never` | no trailer anywhere on the ref's first-parent history |
| `tree_equal` (of `merge-only` + `non-merge`) | `git merge-tree --write-tree <receipt> <base>` equals the code's tree but for delivery rows: `reuse_verdict`'s own test |

C1's reach is the `same` rows plus the `tree_equal` rows. The self-test's null
control is the case that keeps the reach honest: a non-merge commit past the
receipt reads `no`.

**Disclosed self-correction.** Round 1 took `<base>` as `git merge-base <code>
origin/main`. Once the code has landed on main that merge base **is** the code,
and merging any ancestor receipt into the code returns the code's tree, so the
test passed whatever lay between. On `r10-carry-residue-2`,
`r10-sav-meter-floor` and `r10-hotfix-stress-mem-peak` the round-1 rule reads
equal, while the first two carry fixer commits past the receipt. The harness
takes `<base>` as the newest commit on main's first-parent chain that the code
contains, which stays put after the code lands. C1's reach is about a quarter
of round 1's, and the cost test is re-taken on it.

**C-B: the full prepr has outgrown the heavy-slot cap's premise.** The cap is a
count, `HEAVY_SLOTS = 4` (`tests/gate_lock.py`), set on 2026-10-16 in
`c09cf12010` ("make the four-prepr cap a lease"), when `tools/pr/prepr.sh` had
less than half the lines and `st` assertion sites it has at `b0762725099f`
(`git show <rev>:tools/pr/prepr.sh | wc -l` and `| grep -c '^ *st '` at both).
Nothing the cap reads would notice that growth, and prepr's step lines carry no
time, so a run's per-step cost is recoverable only by sampling `ps`.

## 4. Process state

- **C-A: (c), followed and did not produce the intended result.**
  `open_pr.sh` passed `--reuse`; `app_push.sh` read the tip and fell through
  exactly as written. The design keys the receipt to one checkout's git dir and
  to sha equality, so `body_push.sh` dropped receipts `reuse_verdict` would
  accept: a body re-pushed from another checkout (`same`), or a code head moved
  only by a clean merge of main (`tree_equal` `yes`). For the `never` rows the
  state is **not established**: whether each fixer ran a passing full prepr in
  the checkout that pushed its body is recorded nowhere, because
  `body_push.sh` prints one undifferentiated "no receipt" line and writes
  nothing to the body commit (C2). The three triggering instances are `never`
  or outside the window, so C-A's (c) rests on the `same` and `tree_equal`
  rows, not on them; the instances are explained by C-B alone until C2 splits
  `never`.
- **C-B: (d), the preconditions changed underneath a sound process.** The
  4-slot cap was set for a prepr less than half its present size, and measures
  nothing that grows with it.

## 5. Cost test

Units: open-minutes, per occurrence, over the window.

- **cost(defect)**, a proxy, `open_prepr_receipts.py opens`: each delivery-row
  commit's time less the newest handoff-body commit, made before it, for the
  code it opened, graded `receipt` when that body carried a trailer, else
  `full`. It holds the relay's wait before the open as well as the open, for
  both grades alike, so the difference of the medians is what a receipt saves.
- **P(recurrence)**: C1's reach, `same` + `tree_equal`.
- **C1**: benefit reach x (full median - receipt median) open-minutes, and as
  many heavy-slot-minutes. Standing cost: one `git log -1` of the parent tip
  `body_push.sh` already fetches, and one `git merge-base --is-ancestor`, per
  body push. Build.
- **C2**: no run-time cost (it changes which line prints and which trailer is
  written). Benefit: the `never` rows become splittable from git. Build.
- **C3**: bash's `$SECONDS`, read per step, spawns nothing. Its benefit is not a
  number: it makes C-B, and round 1's "not queued, not hung" reading,
  re-derivable without sampling `ps`. Build, on that argument.
- **Lowering `HEAVY_SLOTS`, or moving open-time full prepr runs to the cloud:
  recorded refusal for now.** Fewer slots make each run faster and the queue
  longer; the net is unknown without per-step wall times from an idle and a
  loaded host, which C3 produces. A cap change is the owner's (`gate_lock.py`'s
  `HPO_HEAVY_SLOTS_OWNER`).

## 6. Countermeasures, routed

Each is check-shaped and owes a failing-then-passing self-test arm in its
fixer's pull request. The cases and null controls below are preconditions.

- **C1 (state c), R10-PREPR-RESIDUE.** `tools/audit/seat/body_push.sh`
  `prepr_trailer`: take the candidate receipt from the local
  `hpo-prepr-receipt`, else from the one `Prepr:` trailer on the parent tip
  `body_push.sh` already fetches; write it when the receipt's sha is an
  **ancestor of** the code head (not only equal) and its tree is that sha's
  tree. `reuse_verdict` re-proves the rest from git objects and fails closed.
  Failing cases: a re-push from a second clone keeps the trailer; a clean merge
  of main past the receipt keeps it, and `reuse_verdict` returns rc 0. **Null
  controls**: a non-merge commit past the receipt keeps the trailer and
  `reuse_verdict` returns rc 1, so a carried receipt never skips prepr on
  unproved code; a receipt on a non-ancestor writes no trailer. Re-measure the
  reach with `open_prepr_receipts.py tips` over your own window.
- **C2 (state c, for the `never` rows), R10-PREPR-RESIDUE.** The no-trailer
  line, and a `Prepr-absent: <reason>` trailer on the body commit, name which
  of: no receipt file in this checkout; a receipt at `<sha>` not an ancestor of
  the code head; a receipt whose tree is not its sha's; no trailer on the
  parent tip. Failing case: each of the four, planted, prints and writes its
  own reason (before the fix all four print one line). **Null control**: a
  valid receipt writes `Prepr:` and no `Prepr-absent:`. Then extend
  `open_prepr_receipts.py` to split `never` by that trailer.
- **C3 (state d), R10-PREPR-RESIDUE.** `tools/pr/prepr.sh`'s step line carries
  the step's elapsed seconds, and the final `PRE-PR:` line the run's. Failing
  case: a step stubbed to sleep 2 s prints an elapsed of at least 2 (before the
  fix there is no field). **Null control**: a no-op step prints 0 or 1, so the
  field times the step and not the run.
- **C4 (state d), R10-PREPR-RESIDUE.** The comment over `predict_line` says
  step 6d "costs seconds"; `ci_predict.py`'s header prices its GRADER arm in
  "minutes where keyed". `dev/audit/rca/open_prepr_6d.sh` times step 6d's
  predictor at `6671786843` (slim-p2, a diff the gate cannot scope) and at
  `c19017d6` (arbiter-off-restore, scoped) as its null control, and prints a
  sha1 of the sorted `PREDICT` lines. The fixer corrects the comment's premise,
  and bounds or leaves to CI the GRADER replays CI's `instrument-self-tests`
  already runs, keeping the SELF-TEST READS recording the step exists for
  (`R10-RCA-CLOSURE-ARGV.md`). Proof: `open_prepr_6d.sh 6671786843` before and
  after on one host, wall time down and `predict_sha1` unchanged; at
  `c19017d6`, `predict_sha1` unchanged.

## 7. Outside this RCA, found while measuring

- **No tool sets the caller's 3000 s bound** (`grep -rnE 'timeout
  (3000|7200)' tools/ dev/governance/ .claude/` prints nothing); the
  orchestrator chose it.

All four carries go to R10-PREPR-RESIDUE: on the round roster
(`handoff/audit-r10-roster`) it is the open group whose files hold
`body_push.sh`, `prepr.sh`, `ci_predict.py` and `gate_lock.py`. R10-HANDOFF-PATH
built P386 and R10-PREPR-CAP built the slot pool, but both are `done`, and
`carry_audit.py` refuses a carry to a done group.
