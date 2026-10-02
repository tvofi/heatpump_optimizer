# Root cause: `closures-autofix` green on `skip-not-under-scoped` beside a `closures` UNDER-SCOPED

Root-cause seat, round 9, 2026-10-02. Contract: `tools/audit/briefs/root-cause.md`;
policy: `.claude/rules/defect-root-cause.md`, `.claude/rules/ci-autofix.md`. Source
read at `origin/main` 2e7422e59. Nothing in #1846 or in any workflow was changed.

## Defect

PR #1846 (`fix/r9-web-page`), head `e42b1cdd`, Tests run 37019499517:
`closures` printed `UNDER-SCOPED: tests/harness_headers.py really reads 1 file(s) ...
DISCLAIMER.md` and went red. `closures-autofix` printed `allowed=True`,
`AUTOFIX: skip-not-under-scoped`, `nothing owed to a human`, and went green. No bot
commit followed. By `ci-autofix.md` a green `skip-not-under-scoped` reads as "no repair
was owed to the bot", which the `closures` log contradicts.

## 1. Cause (reproduced; the reviewer's hypothesis confirmed, with one refinement)

`closures` and `closures-autofix` classify the same recordings with **different
programs**:

- `closures` runs the pull request's own `tests/closure.py check` (tests.yml step
  "Fail if tests/closures.json under-approximates").
- `closures-autofix` restores `tests/closure.py` from
  `github.event.pull_request.base.sha` (tests.yml step "Restore the programs this job
  runs from the base commit", D11-s1-03, decision 0013's pinned-grader rule) and the
  classifying step `import closure` loads that copy — `git checkout $PINNED -- path`
  writes the working tree, `git reset` only unstages it.

#1846 moves `DISCLAIMER.md` and `docs/index.html` from INERT to `INERT_EXCEPT` in
`tests/closure.py` and commits closures that list them. The base copy (aab94eea) still
holds them INERT, so its `check()` fails at the **first** gate,
`inert_closure_violations(committed)` ("files on the INERT list are inside a recorded
closure"), and returns 1 **before** the under-approximation comparison. No
`UNDER-SCOPED` text is produced, so `apply_under_scoped_recordings` returns
`skip-not-under-scoped`, a quiet status in `AUTOFIX_QUIET`.

Refinement: it is not that the base classifier sees DISCLAIMER.md as "not
under-scoped" — the base classifier never reaches the comparison at all; an earlier,
unrelated refusal (the #357 INERT-pair check) masks it.

Reproduction (Darwin, Python 3.14, recordings artifact of run 37019499517 downloaded,
tree at `e42b1cdd`, only `tests/closure.py` swapped):

| `tests/closure.py` from | `check()` first failure | `apply_under_scoped_recordings` |
|---|---|---|
| head `e42b1cdd` | `UNDER-SCOPED: tests/harness_headers.py ... DISCLAIMER.md` | `skip-failed-recording` (red) |
| base `aab94eea` (what CI ran) | `files on the INERT list are inside a recorded closure: DISCLAIMER.md, docs/index.html` | `skip-not-under-scoped` (green) |

The head classifier would have reddened (the `tests/stress.py` recording has `rc=1`,
"2 of 98 STRESS CHECKS FAILED" under recording). So the base pin turned a red
"repair did not happen" into a green "nothing owed".

Even with no failed recording a bot repair is **structurally impossible** on this
path: the base `merge()` refuses the same INERT-and-recorded pair (`skip-merge-failed`).
Any PR that moves a file out of INERT and must re-record a closure reading it can only
be repaired by a human `--single`. The defect is the signal, not the missing repair.

### The earlier #1846 reds (a46a91c, ddaf6bf7) are a different, by-design path

There `closures` printed `INERT READS UNDER-APPROXIMATED ... tests/doc_claims.py:
DISCLAIMER.md` and no UNDER-SCOPED at all. The autofix does not repair `inert_reads`
(not in `ci-autofix.md`'s table), and `skip-not-under-scoped` is the accurate answer;
the `closures` log itself names the remedy (`--single`). Not this defect. It is the
null control below.

## 2. Process state: **(d)** — the process was sound and its precondition changed

The autofix (523402460, 2026-09-06, #498) was correct while it ran the same
`tests/closure.py` as `closures`: its quiet `skip-not-under-scoped` assumed "the
grader that failed and the classifier that re-reads its recordings agree".
42460ce2f (2026-09-26, F11.2, D11-s1-03) pinned the classifier to the base for a
sound security reason (a `contents: write` job must not execute PR code), and nothing
re-examined the quiet statuses' meaning against a classifier that can now disagree
with the grader. #1569 (8658ef6ac) already fixed one instance of the same symptom
from the other divergence — recordings made on the merge tree, classified on the
branch head — so this is the second tree/program mismatch behind one symptom.

Not (b): nobody skipped a step; the seat on #1846 read the summary line as
`ci-autofix.md` instructs, and the line was wrong. Not (c): the pin did what it was
written to do. Per the policy, the (d) countermeasure is making the process notice
its own precondition change, not a firmer instruction.

## 3. Class reach

- Same job: any PR that edits a classification table in `tests/closure.py` (INERT,
  INERT_EXCEPT, the header corpus, SLOW_GATED, DRIVEN_BY_OTHERS) or adds a check that
  fails before the comparison, while a closure is also stale. Measured: 3 runs, 2 PRs
  (below).
- Same shape elsewhere, not measured: `claims-autofix` (pins `env_drift.py`, quiet
  `skip-not-inherited`) and `mutation-autofix` (pins `mutation_table.py`, quiet
  `skip-not-unpinned`) also re-classify the grader's failure with the base program and
  have a quiet "not my case" status. A PR changing those classifiers can produce the
  same green-beside-red. The countermeasure below generalises to them; no instance was
  searched for there.

## 4. Cost test

**Measured frequency.** All `tests.yml` `pull_request` runs created 2026-09-26
(pin date) to 2026-10-02: **423** runs listed (0 list failures), jobs read for every
run (0 failures), logs read for every run where `closures` failed and
`closures-autofix` ran: **22** (0 log-fetch failures). Of these, **15** had `closures`
print `UNDER-SCOPED`:

| autofix status | runs | meaning |
|---|---|---|
| `changed` | 5 | repaired |
| `skip-failed-recording` | 5 | red, correct |
| `skip-not-allowed` | 1 | loop guard, documented (d92ffb87, `fix/r9-f9-test-pins-3`) |
| `skip-clean` | 1 | autofix checked out a newer head (89572df0, after an earlier bot re-record) — legitimate |
| **`skip-not-under-scoped`** | **3** | **this defect** |

The three: #1846 at `9bc802e6` and `e42b1cdd` (base aab94eea), and #1851
(`fix/r9-eg-archscore`) at `3a28a3ea` (base aab94eea; it moved `tools/audit/archscore/`
out of INERT; base check fails on the INERT pair). **All three reproduced locally**
with the downloaded recordings: head classifier → `skip-failed-recording`, base
classifier → `skip-not-under-scoped`. So **3 of 15 UNDER-SCOPED runs (20%) in 7 days,
2 of the PRs that hit UNDER-SCOPED**, both on 2026-10-02.

**cost(defect), per occurrence**: a red PR whose autofix says nothing is owed. The
#1846 instance cost a review round to diagnose plus this RCA seat; the delay is
unbounded by design (a seat waiting on the bot waits forever, #523's shape).
Estimate **≥ 30 min of seat time per PR** (basis: one reviewer diagnosis cycle; not
measured).

**cost(countermeasure, recurring)**: one `tee` in `closures` (no measurable time) and
one regex over a ~80 KB text file in `closures-autofix`, which runs only on a failed
`closures` (22 of 423 runs): well under 1 s per run. Once-off: ~10 production lines in
`tests/closure.py` (ratchet: the fixer pays for them), ~3 YAML lines, one `entities.py`
case.

Verdict: < 1 s × 22 runs/week ≪ 30 min × 2 PRs/week. **Build it.**

## 5. Countermeasure (for a fixer; not built here)

Addresses state (d): the autofix notices when its pinned classifier disagrees with
the grader instead of trusting itself.

1. `closures` job, step "Fail if tests/closures.json under-approximates": run the
   check with `set -o pipefail` and `| tee "$RUNNER_TEMP/closures/check.txt"` (both
   arms). `.txt` is outside every `*.json` glob; the upload step already uploads the
   directory with `always()`.
2. `tests/closure.py`: add a red status, e.g. `skip-classifier-disagrees`, **not** in
   `AUTOFIX_QUIET["closures-autofix"]`, and an entry in `_AUTOFIX_STATUS_REMEDY`:
   "the closures job (this PR's tests/closure.py) printed UNDER-SCOPED; the base's
   copy this job is pinned to stops earlier (usually: this PR moves a file out of
   INERT). No bot repair can come — the base merge would refuse the pair. Re-derive
   the script the closures log names with `--single` and commit tests/closures.json."
   In `apply_under_scoped_recordings` (or a small wrapper the step calls), when the
   pinned result is `skip-not-under-scoped` **and** `in_dir/check.txt` has a line
   matching `^UNDER-SCOPED: `, return the new status. Read the file as data only; the
   PR-produced text can only make the job redder, never push.
3. `.claude/rules/ci-autofix.md` (policy; owner approval before merging): name the
   status in the red list and in "What green means", and note that the classifier is
   base-pinned. Regenerate `.cursor/rules/ci-autofix.mdc` with `rules_sync.mjs`.
4. Optional, same PR or later: the same "grader printed X, pinned classifier says not
   X" guard for `claims-autofix` (`INHERITED CLAIMS`) and `mutation-autofix`.

### Demonstration of the predicate (prototype, scratch only)

`demo.py` beside this file runs `origin/main`'s unchanged `closure.autofix_report` /
`autofix_repair_failed` with the proposed predicate over the real CI logs:

```
e42b1cd defect: today status=skip-not-under-scoped job_rc=0 | proposed status=skip-classifier-disagrees job_rc=1
a46a91c null (INERT READS only): today status=skip-not-under-scoped job_rc=0 | proposed status=skip-not-under-scoped job_rc=0
```

Fails (red) on the defect, stays green on the by-design INERT READS failure. Other
null controls from the scan: the predicate is keyed on `skip-not-under-scoped` only,
so the legitimate `skip-clean` on a moved head (89572df0) and the documented
`skip-not-allowed` are untouched; a healthy run never starts the job. The fixer owes
the real demonstration: an `entities.py` case that writes a `check.txt` with
`UNDER-SCOPED:` beside recordings whose base check fails on an INERT pair (red),
the same without the line (green), and a mutation that drops the guard (case fails).

## 6. Recording

`defect-root-cause.md` asks for a **Root cause** section on the defect's own issue;
there is no issue for this defect and this seat may not write to GitHub. The
orchestrator carries this document to the fixer's brief / the PR body.
