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

e414ab711d7302f290f0f7865fd4af419ae9649c, on merge base b8f67a775137a8032d5c71b34ea64165c1d4613a (origin/main when the branch was cut). The commits:
- 9350dc7c: the fix and the failing tests;
- 8e795cda: the mutant harness;
- b4f272a6: the guides and the inert classification;
- e414ab71: a direct pin on `policy_approval_due`, added after the harness found P3 survived.

## Mutation proof

Failing first: the new `queue_pre_flight.py` self-test checks were run against the unfixed `merge_train.py`/`PreFlight.entry` (working tree, before the fix was written). `python3 tools/audit/seat/queue_pre_flight.py --self-test` printed `52 checks, 2 failed`:
- `a policy head with no review yet passes under the train's --mandate in force for policy merging (the approval policy_approve posts, judged by policy_gate)`;
- `null control: under a --mandate tvofi revoked it still PARKs, named as revoked` (the unfixed park did not name the revocation).

Mutant P1 below restores that unfixed call at the head, and it fails the same two checks.

`python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` at e414ab71 makes one in-place mutant per arm under `mutant_guard`. It runs `queue_pre_flight.py --self-test` for each mutant, and the tree is clean afterwards (`git status --porcelain` printed nothing). It printed `8 mutant(s), 0 not as required`:
- P0, unmutated: PASS.
- P1, `PreFlight.entry` calls `policy_gate` alone (the defect): KILLED. Both checks above fail.
- P2, `policy_admits` builds no posting: KILLED, by the pass check.
- P3, `policy_approval_due` returns the id even when the mandate is not live: KILLED by `policy_approval_due names the mandate in force for policy merging; revoked, expired or scope code-owned it names none`. At 8e795cda this mutant SURVIVED, because `policy_gate` re-judges the simulated review and still parks. e414ab71 pins the function directly, since `policy_approve` posts on the same answer.
- P4, no-mandate arm (`cid = self.mandate_id() or MID`): KILLED by `null control: the same head with no --mandate still PARKs on the review`, and by the existing `a policy head with no owner review at its head PARKs`.
- P5, the mandate's reason dropped from the park: KILLED by the revoked null control.
- P6, the posting judged instead of the reviews read: KILLED by `an owner CHANGES_REQUESTED at the head still PARKs under the --mandate`.
- P7, the pre-flight posts (`policy_approve` called in `policy_admits`): KILLED by the pass check and the CHANGES_REQUESTED check.

Re-anchored: `dev/audit/harnesses/r10_train_upgrade_mutants.py` M3 and M5 named spans in `policy_approve` that moved into `policy_approval_due`. Their mutations are the same, re-pointed at the new spans (M3 `return cid, pol, why`; M5 `pass` over the at-head return).

`python3 dev/audit/harnesses/r10_train_upgrade_mutants.py M3 M5`, run at b4f272a6, printed `M3 KILLED` and `M5 KILLED` (rc 0). Its `merge_train.py` is e414ab71's.

## Null control

- No `--mandate`: the same policy head with no review still PARKs `policy`, with `no decisive review`.
- A mandate tvofi revoked: it still PARKs, naming `revoked`.
- A mandate with scope `code-owned`: it still PARKs.
- An expired mandate: it still PARKs.
- An owner `CHANGES_REQUESTED` at the head under a live mandate: it still PARKs.
- Each check above was run at e414ab71. It passes there, and its own mutant (P3 to P6) turns it red.
- The pre-existing policy and raise arms of the pre-flight self-test stay green at the head: cited approval passes, uncited parks, no review parks, revoked parks, and the raise arms.

## Figures

- `python3 tools/audit/seat/queue_pre_flight.py --self-test` at e414ab71: `queue_pre_flight self-test: 53 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test` at b4f272a6 (whose `merge_train.py` is e414ab71's): `merge_train self-test: 608 checks, 0 failed`, rc 0.
- `python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` at e414ab71: `8 mutant(s), 0 not as required`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff b8f67a775137a8032d5c71b34ea64165c1d4613a --workdir <tmp>` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, running `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`, run at e414ab71, printed `1 of 2706 ENTITY CHECKS FAILED`, rc 1. The one failure was `a measured script's late-writing descendant is waited for, not recorded as nodata`. That is the coverage stage's wait-bound check, run in a temporary directory, and its waiting arm recorded every script, `entities` included, as `nodata`. The run was taken on a host at load average about 350 (`uptime`), and the check reads none of this diff's files: its inputs are the coverage stage and planted scripts, not `tools/audit/seat/` or the harnesses. It is left to CI's `entities` run at this head, which judges it. Every other check, the planted-failure controls included, read as designed.
- `python3 tools/pr/ci_predict.py --apply-inert` printed `APPLIED inert_reads tests/harness_headers.py: dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` and `CI PREDICT: no closures, fast, governance or instrument red predicted`.
- The class rule: `git grep -n "policy_gate(\|\.policy_admits(" -- tools .github` enumerates every tracked policy judge call (4 lines at e414ab71). Each one, and its disposition:
  - `merge_train.py` `land`: after `policy_approve`, unchanged.
  - `merge_train.py` batch admission: after `policy_approve`, unchanged.
  - `merge_train.py` `policy_admits`: new.
  - `queue_pre_flight.py`: replaced by `policy_admits`, this diff.
  - No other caller judges policy before the post.

## Red checks

none

## Forward-carry

none

## Friction

none
