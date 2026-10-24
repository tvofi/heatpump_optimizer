# Review — PR #2488, the round-9 handoff archive (round 1)

Role: **fix reviewer**. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**
Read `dev/governance/roles/fix-review.md` first: review the head adversarially from a detached worktree, with your
own harness, and check that the numbers are real.

## What you review

- PR **#2488**, head **`916431aefd47a8953cb5b84a990c993a77c371e3`** — *chore(archive): move handoff/round9 into the
  archive tree (R10-HANDOFF-ARCHIVE)*.
- Bus nonce: **`03ec7d662c9771a80a7c37590e1c0fbb`** (`bus.sh dispatch 2488 <head> rev-2488-r1`).
- Detached worktree: `git -C /Users/timmalmstrom/heatpump_optimizer fetch origin fix/r10-handoff-archive`, then
  `git worktree add --detach ~/hpo-seats/r10s3/rev-2488 916431aefd47a8953cb5b84a990c993a77c371e3`.
- Scratch: `~/hpo-seats/r10s3/rev-2488-ev` (create it).
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.

## What the PR claims, each of which you verify

1. **The move is content-preserving.** `handoff/round9/`'s two files moved to `dev/archive/handoff/round9/`;
   `git diff -M --summary <merge-base> HEAD` shows two 100% renames and `--numstat` shows `0 0`; the sha256 of each
   file at the head equals its blob at the merge base. Verify, do not take.
2. **The layout guard is clean at both ends**, and its perturbation fires:
   `python3 -I tests/layout.py --guard --base origin/main` at the head; then stage a live file citing the old path
   and confirm the guard refuses. The base run is your null arm.
3. **`moved_paths.py` names no `STALE?` line in a live file.** Run it over the added lines and over the touched files
   whole; say which hits are the map's own entry and which are the round-9 record's pre-existing other moves.
4. **The remaining `handoff/round9` mentions are archives and records only.** The body claims 26 files; re-derive the
   set with `git grep -l` and classify every one. A live tool, test or product file is a finding.
5. **The new mechanism, which is the part this PR adds beyond a move.** To keep the instruments from manufacturing an
   emptied `handoff/` parent and sweeping 322 branch-name citations in 53 files, the diff adds a `ref_namespaces`
   list to `tests/layout.json` and teaches `landed()` — shared by `layout.py` and `moved_paths.py` — to skip only
   manufactured parents that name refs. Attack it:
   - Does the skip fire on anything other than an emptied parent that names a ref namespace? Plant a case where a
     manufactured parent is also a real swept path and confirm the guard still refuses.
   - Is the exemption keyed on the same shape everywhere (both instruments), and does each have a self-test that
     reddens when the clause is deleted? Re-run both self-tests and delete the clause in a scratch copy as your
     perturbation.
   - Does `ref_namespaces` widen the guard for a future move of a real directory whose name collides with a ref
     namespace (`handoff/` itself, `verdict/`, `review/`)? State what would happen.
6. **The body's other claims**: `tests/entities.py` passed at the head; the scoped gate's mode line; the delivery row
   is the PR's own and names `R10-HANDOFF-ARCHIVE`; `VERSION`, the manifest and the notes heading are untouched.
7. **CI at the head.** Read `/repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`, never a checks summary. Do
   not run the full local gate — CI runs it; cheap targeted re-runs are yours. A `nightly-status` red grading `main`
   is not this PR's, and `delivery-status` owes an answer only if the diff touches what it reads.

## Known and acceptable unless you falsify it

- `since` in the map's entry is left null for the orchestrator to record the PR number after it opens, as the
  round-9 moves did. Check that the schema and every reader accept null there; if a reader would misbehave, say so.
- The fixer's report says the grep control could not be made literal because the tree's `historical` layout rule
  keeps paths that were true when written. That is a claim about the rule — verify it in `tests/layout.json` rather
  than accepting the sentence.

## Deliver

```
bash /Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/bus.sh push-verdict 2488 <VERDICT.md> <evidence dir>
```

Verdict line: `Fix review: merge 916431aefd47a8953cb5b84a990c993a77c371e3` or
`Fix review: blocked 916431aefd47a8953cb5b84a990c993a77c371e3 <class>: <reason>`.

**Every path in the verdict and its evidence must be home-relative (`~/…`)** — the poster refuses a host path and a
refused verdict costs a round trip (#2310).

Report back: the verdict line, the review ref SHA, the rename proof, what your guard perturbations did, and the
classification of the 26 (or whatever the real number is) remaining mentions.
