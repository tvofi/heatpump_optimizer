The merge train parked a policy head that its own `--mandate` should have carried. On #3366, at head 97839ed60f8b59cd59adc99d106b4e94ac4dccab with a merge verdict at that head (comment 6754586447), the live train (state dir `mandate` file 6715477401) logged `PARK #3366 policy: policy paths changed (...): no decisive review by tvofi (id 70032254) on this pull request`. A re-add under `--mandate 6715477401` then answered `ADD REFUSED #3366 policy: ... (the pre-flight park at this verdict still holds)`.

Root cause: an ordering defect between the train's two policy steps. The batch admission (`Train.at_head`) and `Train.land` both call `policy_approve` (post the citing approval under the mandate) and then `policy_gate` (judge it). The `--pre-flight` read, `queue_pre_flight.PreFlight.entry`, called `policy_gate` alone, so it ran before anything was posted. A policy head with no review yet therefore parked on "no decisive review" before admission could post the approval that cures it. `train_add`'s re-admission of a `PRE-FLIGHT` park at the same verdict re-runs that same read (`Train.preflight_entry`), so it refused #3366 again for the same reason. Both symptoms come from one seam. The park memo itself is correct: it re-asks the pre-flight, and the pre-flight gave the wrong answer.

The mandate covers this act. Comment 6715477401 on #201, by tvofi, created 2026-11-08T01:12:45Z and never edited, reads `MANDATE: agents may approve as tvofi, scope all, from 2026-11-08T01:12Z until 2026-11-16T18:00Z`. budget_raise_gate's own reader, `mandate_state(..., "merge", MANDATE_COVERS_POLICY, "policy merging")`, run on the live comment and the #201 thread since its creation, returned `(True, 'mandate 6715477401 (scope all, from 2026-11-08T01:12Z until 2026-11-16T18:00Z)')`. With one tvofi revocation comment appended, it returned `(False, "mandate 6715477401 was revoked by tvofi's comment 1")`.

The fix, in `tools/audit/seat/merge_train.py` and `tools/audit/seat/queue_pre_flight.py`:
- `Train.policy_approval_due(pr, h, files)` decides whether `policy_approve` will post. It is a read, holding policy_approve's own decision unchanged: no policy path, no `--mandate`, a budget file beside the policy, the owner's approval already at the head, or a mandate that `mandate_state` does not read as in force for policy merging each mean no post. `policy_approve` now posts on its answer.
- `Train._agent_approval_body` is the body `_post_agent_approval` posts, factored out so the pre-flight can judge the same body without posting it.
- `Train.policy_gate(..., posting=None)` judges the reviews it reads plus, optionally, the review about to be posted, appended last as GitHub would list it. Every caller but one passes none.
- `Train.policy_admits(pr, h, item, files)` is the pre-flight's policy read: `policy_gate` as admission reaches it, with the due approval judged unposted. It posts nothing. When a `--mandate` is set but nothing is due, the park names the mandate's own reason (revoked, expired, scope) beside the gate's.
- `PreFlight.entry` calls `policy_admits` in place of `policy_gate`.
- `land` still re-reads the real reviews at the merge, so the merge decision is unchanged and `policy_gate` stays the only judge.

Alternatives rejected:
- (a) Post the approval inside the pre-flight. That makes a read-only instrument write, and it would post an owner-account approval for an entry a later pre-flight step (row, findings, raise) then parks.
- (b) Skip the policy read in the pre-flight under a mandate. That passes heads the merge would refuse, such as an owner `CHANGES_REQUESTED` (pinned below), because it bypasses the judge where (c) consults it.
- (c), taken, keeps one decision (`policy_approval_due`) and one judge (`policy_gate`), shared by the post, the pre-flight and the merge.

## Head

593a28c96e54a64c3ce25d99dfd4850be6094e4b. This is the repair of the CI block at f0b7564596d2725f87090f921e0d3ceb51ceec8b (hpo-approver comment 6758409766): one commit over that head, 593a28c9, adding the line `    from pathlib import Path` to the harness's inlined `repo_root`. Its `def repo_root` through the `raise RuntimeError` line is now byte-identical to `tools/audit/repo_root.py`'s, compared by regex extraction of both texts. The earlier commits are unchanged:
- 9350dc7c: the fix and the failing tests;
- 8e795cda: the mutant harness;
- b4f272a6: the guides and the inert classification;
- e414ab71: a direct pin on `policy_approval_due`;
- 20f3028f: origin/main b0762725 merged in;
- f0b75645: the delivery row.

The merge with main changed `tools/audit/seat/merge_train.py` (+16/-12, other pull requests' lines), so every figure below that names 593a28c9 was re-taken at this head. The ones naming an earlier SHA say so.

## Mutation proof

Failing first: the new `queue_pre_flight.py` self-test checks were run against the unfixed `merge_train.py` and `PreFlight.entry`, in the working tree before the fix was written. `python3 tools/audit/seat/queue_pre_flight.py --self-test` printed `52 checks, 2 failed`:
- `a policy head with no review yet passes under the train's --mandate in force for policy merging (the approval policy_approve posts, judged by policy_gate)`;
- `null control: under a --mandate tvofi revoked it still PARKs, named as revoked` (the unfixed park did not name the revocation).

Mutant P1 below restores that unfixed call at the head, and it fails the same two checks.

`python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` at 593a28c9 makes one in-place mutant per arm under `mutant_guard`. It runs `queue_pre_flight.py --self-test` for each mutant. The tree was clean afterwards: `git status --porcelain` printed nothing. It printed `8 mutant(s), 0 not as required`, rc 0:
- P0, unmutated: PASS.
- P1, `PreFlight.entry` calls `policy_gate` alone (the defect): KILLED. Both checks above fail.
- P2, `policy_admits` builds no posting: KILLED by the pass check.
- P3, `policy_approval_due` returns the id even when the mandate is not live: KILLED by `policy_approval_due names the mandate in force for policy merging; revoked, expired or scope code-owned it names none`. At 8e795cda this mutant SURVIVED, because `policy_gate` re-judges the simulated review and still parks. e414ab71 pins the function directly, since `policy_approve` posts on the same answer.
- P4, the no-mandate arm (`cid = self.mandate_id() or MID`): KILLED by `null control: the same head with no --mandate still PARKs on the review`, and by the existing `a policy head with no owner review at its head PARKs`.
- P5, the mandate's reason dropped from the park: KILLED by the revoked null control.
- P6, the posting judged instead of the reviews read: KILLED by `an owner CHANGES_REQUESTED at the head still PARKs under the --mandate`.
- P7, the pre-flight posts (`policy_approve` called inside `policy_admits`): KILLED by the pass check and the CHANGES_REQUESTED check.

Re-anchored: `dev/audit/harnesses/r10_train_upgrade_mutants.py` M3 and M5 named spans in `policy_approve` that moved into `policy_approval_due`. Their mutations are unchanged, re-pointed at the new spans (M3 `return cid, pol, why`; M5 `pass` over the at-head return). `python3 dev/audit/harnesses/r10_train_upgrade_mutants.py M3 M5`, run at b4f272a6, printed `M3 KILLED` and `M5 KILLED`, rc 0. It was not re-run at 593a28c9. The main merge did not touch the spans either mutant names; CI's mutation lane judges the head.

The repair's own control: `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at f0b75645 (the blocked head) printed `1 of 112 HARNESS HEADER CHECKS FAILED`, rc 1: `every inlined walk matches the canonical helper and no depth root remains [FAIL python copies=174 differ=['dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py']`. At 593a28c9 it printed `ALL 112 HARNESS HEADER CHECKS PASSED`, rc 0.

## Null control

- No `--mandate`: the same policy head with no review still PARKs `policy`, with `no decisive review`.
- A mandate tvofi revoked: it still PARKs, naming `revoked`.
- A mandate with scope `code-owned`: it still PARKs.
- An expired mandate: it still PARKs.
- An owner `CHANGES_REQUESTED` at the head under a live mandate: it still PARKs.
- Each check above passes at 593a28c9 (`queue_pre_flight` self-test below), and its own mutant (P3 to P6) turns it red.
- The pre-existing policy and raise arms of the pre-flight self-test stay green at the head. These are: a cited approval passes, an uncited one parks, no review parks, a revoked mandate parks, and the raise arms.

## Figures

- `python3 tools/audit/seat/queue_pre_flight.py --self-test` at 593a28c9: `queue_pre_flight self-test: 53 checks, 0 failed`, rc 0.
- `python3 tools/audit/seat/merge_train.py --self-test` at 593a28c9: `merge_train self-test: 608 checks, 0 failed`, rc 0.
- `python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` at 593a28c9: `8 mutant(s), 0 not as required`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at 593a28c9: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`, at e414ab71: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`, at e414ab71: `1 of 2706 ENTITY CHECKS FAILED`, rc 1.
  - The one failure was `a measured script's late-writing descendant is waited for, not recorded as nodata`, the coverage stage's wait-bound check.
  - Its waiting arm recorded every script as `nodata`, `entities` included. The host was at load average about 350 (`uptime`).
  - Its inputs are the coverage stage and planted scripts, none of this diff's files.
  - It is left to CI's run at this head.
- The class rule: `git grep -n "policy_gate(\|\.policy_admits(" -- tools .github` printed 5 lines at 593a28c9. Each line, with its disposition:
  - `merge_train.py` `def policy_gate`: the judge itself, taking the new optional `posting`.
  - `merge_train.py` `policy_admits`: new; it calls the judge with the unposted approval.
  - `merge_train.py` `land`: after `policy_approve`, unchanged.
  - `merge_train.py` batch admission: after `policy_approve`, unchanged.
  - `queue_pre_flight.py`: now calls `policy_admits`, this diff.
  - No caller judges policy before the post.

## Red checks

- `tests / fast (3.14)`, red at f0b75645 in `tests/harness_headers.py`. The new harness's inlined `repo_root` lacked the canonical line `    from pathlib import Path` from `tools/audit/repo_root.py`, so the header check refused the copy. 593a28c9 copies the function verbatim (see `## Mutation proof` for the before and after).
  - Root-cause trigger answer: a cheaper detector existed. It is `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`, run locally in about 188 s, against about 13 min of the fast lane.
  - It was not run before the handoff because `tools/pr/ci_predict.py` predicted no `fast` red: `CI PREDICT: no closures, fast, governance or instrument red predicted`. ci_predict does not run the `run_always` script `harness_headers.py` over a new harness.
  - That predictor gap is the countermeasure's place, carried below to R10-PREPR-RESIDUE. It is not fixed here: it is a different seam (`tools/pr/ci_predict.py`), and not one line.

## Forward-carry

- ci_predict does not run the `run_always` `tests/harness_headers.py` over a new or changed `dev/audit/harnesses/*.py`. So a harness whose inlined `repo_root` drifts from `tools/audit/repo_root.py` passes prepr step 6d and `body_push.sh`'s predictor, and turns `tests / fast` red in CI (this PR, at f0b75645). Carry: R10-PREPR-RESIDUE
- The ambient `gh` account is never checked against the owner before the train acts as the owner. `policy_approve` posts an approval as whatever account `gh` holds, and `policy_admits` judges an unposted review it labels with the owner's pinned identity. A train run under a non-owner token would post a non-owner approval, which `policy_gate` then refuses at the merge, and the pre-flight would have passed it. Not fixed here: it predates this PR (`policy_approve`'s post) and wants one owner check shared by the post and the simulation, not a line. A barrier exists to reuse: `tools/audit/seat/ci_probe.py` `owner_check` (`GET /user`, refuse unless the login is the owner). Carry: R10-TRAIN-RESIDUE
- `policy_approval_due` ignores the owner's own `CHANGES_REQUESTED`. Where tvofi's latest decisive review requests changes, `policy_approve` still posts a mandated approval. `budget_raise_gate.approval` then refuses it ("a mandated approval does not override it"), so nothing merges, but a needless owner-account approval is posted. The pre-flight already parks this head (P6's check), so this PR's read is correct. The post's decision is the owner's-latest-decisive rule, which lives in `approval()`, and sharing it is more than one line. Carry: R10-TRAIN-RESIDUE

## Friction

none
