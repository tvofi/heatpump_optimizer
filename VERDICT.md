Fix review: blocked ced4bf66e91d3c61254066c310f1f9af7ea064ef carry-missing: not carried to R10-FLOW-POSTMERGE or R10-FLOW-AUTOTRAIN

bus-nonce: 88919d7150283ca7b820a8d4186cd07d

Round 1. Reviewed from a detached worktree at ced4bf66e91d3c61254066c310f1f9af7ea064ef, against merge base de69745ffcab66b566b3e75aee0b572023f80857 (= origin/main when reviewed). The head was re-read from the PR before writing this verdict, and it had not moved. Roles were current: `git diff <merge-base>...origin/main -- dev/governance/roles/` was empty.

## Block

- fix-review.md step 10 and finding-propagation.md "Enforcement" say a producing PR does not merge until its carry is in the tree, and that the body names the roster branch SHA. The body's `## Forward-carry` names two destinations. Neither is on `handoff/audit-r10-roster` at ddd2e8de9c50e5a56164ba8a29459c6b4e41a65b, and the body names no roster SHA.
  - R10-FLOW-POSTMERGE. Its brief describes the four after-merge steps. It does not say that nudge.md step 12 then shrinks to its exceptions, which is the residue of this group's own brief.
  - R10-FLOW-AUTOTRAIN. Its brief and carries do not mention `tools/audit/seat/sweep_template.md` item (3). After this PR, that item still describes one batch of verdicted PRs with no hourly pitch and no `--bot-prs`, which disagrees with nudge.md step 3.
- The body says the seat cannot write the roster (decision 0011/0013 identity). The remedy is therefore the orchestrator's:
  1. Land both carries with `roster_edit.py` on the roster branch and read them back with `brief_lint.mjs`.
  2. Add that roster SHA to the body.
  3. Re-review. The head does not need to move.
- Nothing else in this review blocks.

## Findings

- nudge.md step 16, as written at this head, holds a ready critical-path group behind two caps:
  - its flow-lane cap ("A critical path 4");
  - `pr_cap.py dispatch-gate`, which refuses at HPO_WIP_CAP (default 6) unless given `--over-cap <reason>`.

  Only expedite items (red main, quota exhaustion, outage, security) bypass the caps. That contradicts the owner rulings of 2026-10-22: "ready critical-path groups are exempt from the open-PR soft cap" and "remember critical path groups starts regardless off the caps when ready".

  R10-FLOW-ARCH-PLANNER already carries the first ruling, but only for orchestrator.md section 5's soft-cap bullet. Precondition for that group: nudge.md step 16 must also state that a ready critical-path group (a member of the plan's `critical_path`, every `after` group done) is dispatched regardless of its lane cap and the WIP total, via `pr_cap.py dispatch-gate --over-cap "critical path: <group>"`. The same `--over-cap` route should be named for expedite items. Control: no sentence in nudge.md or orchestrator.md conditions a ready critical-path dispatch on any cap. Carry: R10-FLOW-ARCH-PLANNER
- The lane caps (A4, B4, C3, F2) and the `R10-FLY-` fly-in naming are prose only. `pr_cap.py` has no notion of lane or fly-in and enforces only the roster-group WIP total (6). Because the lane caps sum to 13, above that total, they bind only within a lane. This matches the PR's own wording ("which enforces the total"), so it is not a defect here. Mechanising lane accounting is a design choice for the group that mechanises dispatch. Carry: dismissed: the wording states accurately what pr_cap.py enforces; lane caps as prose are the owner-adopted Lean study's choice, not a contradiction

## Evidence

- Head and merge:
  - Head checked at start and before writing: ced4bf66e91d3c61254066c310f1f9af7ea064ef (`ev/HEAD.txt`).
  - It is the authored head de20d0c7 plus one delivery-row commit (`dev/programme/delivery/2628.md`), as the body says.
  - `git merge-tree --write-tree origin/main <head>` exited 0 with tree 9f71d275513a115e36f34fd0f450c7b4e0e6473c, so there are no conflicts (`ev/merge_tree.txt`).
- Budgets, with `node tools/policy/policy_lint.mjs --budgets` (`ev/budgets_head.txt`, `ev/budgets_base.txt`):
  - nudge.md is 115/115 lines and ~3812/3814 tokens at both base and head (15249 bytes at base, 15246 at head). It is flat at its cap.
  - orchestrator.md goes from 316 lines, ~4481 tokens at base to 317, ~4512 at head (caps 319 and 4513).
  - The corpus goes from ~62857 to ~62888 tokens (cap 62892, under it without the band).
  - The body's figures match these.
- Mutation proof, re-run: I appended one sentence to nudge.md. `policy_lint.mjs` then exited 1 with two `[budgets]` errors: 116 lines against the 115 cap, and about 3822 tokens against 3814. After restoring, it exits 0 (`ev/mutant_append.txt`). The body's "about 3820" is approximate and consistent. The text has no content detector: a mutant to a sentence's meaning (for example dropping `--bot-prs`) is caught by nothing, and the body says so.
- Null control, re-run: `policy_lint.mjs` prints `TOTAL: 0 error(s) across 43 policy file(s)` at both base and head (`ev/lint_head.txt`, `ev/lint_base.txt`). `rules_sync.mjs --check` exits 0. `brief_lint.mjs` exits 0. I did not re-run the agreement and entities lines.
- Wording against the tools:
  - `pr_cap.py dispatch-gate` exists and enforces a total WIP cap.
  - `roster_edit.py append-group` exists.
  - `merge_train.py --bot-prs` exists, and merges record/autofix PRs inside the train.
  - `app_approve.sh --carry` exists.
  - The nightly record beat's `say skip-train-hold` exists (nightly.yml line 978), as do `skip-no-approver` and the other `skip-` outcomes the body cites.
- Cuts the body says are restated elsewhere, each checked:
  - Step 8's four-prepr train condition is in step 3.
  - Step 17's "not the handover" is in step 12.
  - Section 6 keeps "a `DIRTY` pull request never queues Tests".
  - The eligibility list excludes deferred groups.
- Version: neither `VERSION`, the manifest nor `RELEASE_NOTES.md` is touched. No claim file or golden fixture is touched, so step 4 is not applicable.
- CI on this head, from the check-runs API (`ev/check_runs.tsv`):
  - Every concluded check is success or skipped, except `nightly-status`, and `coverage` and `fast (3.14)` were still in progress when this was written.
  - `nightly-status` is red. It reads the last scheduled run of nightly.yml and grades main. This diff (two role files and a delivery row) does not reach what it reads, so it is not this PR's red. It is not a required check and does not block.
- Owner gate: policy paths need tvofi's approving review, or the mandate 6175172275 (until 2026-10-28T18:14Z). It is outside this verdict.
