Fix review: merge 50b73644b8eab70a44cdfb7b67c446f6f1fd86b6

Round 1. PR #2555, group R10-MERGE-PR-MANDATE (roster entry read from origin/handoff/audit-r10-roster). I measured head 50b73644b8eab70a44cdfb7b67c446f6f1fd86b6 from a detached worktree. It is still the PR head (refs/pull/2555/head). My copy of fix-review.md is current: `git diff merge-base...origin/main -- dev/governance/roles/` came back empty.

## Harness
The issue (#2497) is one seam with no committed finder harness. The kind is instrument and the roster `findings` list is empty. I reviewed against the roster brief and the PR body, and I used the PR's own self-tests as the instrument (step 9). The body names no enumeration rule. The class is one seam: merge_pr.sh's owner-mode scope. Every other `mandate_state` caller reads a gate constant: merge_train.py:817 and orchestrator_tick.py:1334 read MANDATE_COVERS_POLICY, and merge_train.py:944/1024 use the raise default. After this diff no literal `("code-owned", ...)` scope is left in tools/.

## RESULT lines
RESULT M0 null: budget_raise_gate 242 checks 0 failed; merge_pr 14/0; proof_watch 36/0 (matches the body)
RESULT M1 COVERS_CODE_OWNED += budget-raise: gate 1 failed, merge_pr 1 failed (killed, as the body says)
RESULT M2 merge_pr reads COVERS_RAISE: merge_pr 2 failed (killed, as the body says)
RESULT M3 do_merge drops --mandate: proof_watch 1 failed (killed, as the body says)
RESULT M4 launch refusal predicate never true (gh stub exits 1): proof_watch 1 failed, got 1 want 2 (killed, as the body says)
RESULT M5 (mine) COVERS_CODE_OWNED drops "all": gate 1 failed, merge_pr 2 failed (killed)
RESULT M6 (mine) merge_pr literal scope widened to include budget-raise: merge_pr 1 failed (killed)
RESULT test-first: at a9012429d the gate self-test raises NameError on MANDATE_COVERS_CODE_OWNED (confirmed)
RESULT structure.py rc=0; closure select MODE: SCOPED -- 0 script(s) run, 33 scoped out (matches the body; all files are under tools/ and INERT, plus one delivery row)

## Other checks
- Claims, VERSION, manifest and notes: the diff touches none of them. No fixture moves, so env_drift has nothing to claim.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 against f58b14c19 (and against 03b49e152 earlier). No path overlaps with main's changes since the merge base.
- Merge commits: the remerge-diff is empty for both dc394e424 and 2eb1f3780, so neither has a hand resolution.
- Main ancestry: 0ed4aceb2, dcd012deb, 265d3bf1a and 6961f0663 are all ancestors of main, which supports the body's account of what main already landed. merge_train.py does read `g.MANDATE_COVERS_POLICY` (line 817), as the body says.
- CI at the head: every check-run has concluded (ev/check-runs.tsv). The one red is `nightly-status`. Its log grades main's scheduled run 39563978649 at c77f89d, where mutation-nightly and slow failed. This diff reaches nothing those lanes read. The body answers it under Red checks, naming the slow lane. A `pr-contract` run started at 11:44:50Z, after nightly-status concluded at 11:44:33Z, and it is green. instrument-self-tests, mutation, closures, budget-raise-gate and policy-docs are all green.
- Step 14: the diff moves no budget, score, ledger, closure or INERT entry.
- Step 15: the new constant sits beside MANDATE_COVERS_RAISE and MANDATE_COVERS_POLICY, which removes a duplicated literal. The architecture is sound.
- Forward-carry: the body says none, and nothing in the diff changes a later stage.
- Code-owned: tools/policy/budget_raise_gate.py is code-owned. The owner's approval, or a mandate in force, is still needed to merge.

bus-nonce: c4e633e0f4796305913a4862e408cf14
