Fix review: merge dd2f26e749d54d7295dc2873a601487ce59367a4

bus-nonce: 3fc4155dcd9448c785a92dae39c0bbb1
pending-ci: gate

## Scope
This is round 2 at this head, re-dispatched under a new nonce. The round-2 verdict at the same head (probe/rev-3832-28b90c3e, f1c6b2f9) was returned pending one CI context. The head has not moved: the API head equals the reviewed head. Every figure below was re-taken in this fire, not carried. The three-dot diff is data only: `tools/ci/selftest_closures.json` (+802/-3) and the delivery row (+1). No `custom_components/` line changes.

The `dev/governance/roles/` three-dot diff from the merge base to origin/main 35c3e31cc9 is not empty: `fix-review.md` and `fixer.md` changed on main. This review follows main's `fix-review.md` (the role pack rendered at this checkout), including the new step 6 axis rule.

## Evidence
- RESULT byte-identity. The head's `tools/ci/selftest_closures.json` is byte-identical (`cmp`, sha256 8db94f8a3843...) to the `selftest-absorbed` artifact 14730141227 of main run 44957362163 at 4ebd430fbf. Both zip sha256s match the API digests (ev/merge-and-artifacts.txt).
- RESULT failing and passing test, replayed with `selftest_scope.drift` against that run's `selftest-closures` artifact 14729559307 (ev/drift-replay.txt). The replay script ev/drift_rev.py was built by this reviewer, not the finder.
  - Main's table: 11 refusals (rc 1). They are identical in step and path to the 11 that main's own CI drift step printed in jobs 137032369357 and 137049045377.
  - The head's table: 0 refusals (rc 0).
- RESULT mutation. The diff is data only, so the mutants are table perturbations. Each one fails with exactly its own single refusal, and none survives:
  - verdict-bus without wave-r11-groups.json;
  - ci-predictor without wave-r11-groups.json;
  - regret-oracle without room_record.py;
  - the body's own perturbation, roster-library without `dev/governance/dimensions`.
- Class: the enumeration rule is `drift` over all 127 gated steps of the measured run. At the measured SHA it returns 0 at the head. The quantified set is "every read of every gated step in that run's measurement", and the rule's output is that set, so there is no open axis.
- Figures re-derived at this head (ev/figures.txt):
  - `selftest_scope.py static` prints 127 gated step(s), 0 problem(s).
  - numstat is 802/3.
  - 11 steps gain reads, 802 in all.
  - The 3 removals are roster-library's probes D12.md, D3.md and D99.md. Its new dirs entry `dev/governance/dimensions` subsumes them.
  - No duplicates, and the steps are 127 at both ends.
- VERSION, the manifest version, the RELEASE_NOTES heading and both claim files are untouched.
- Merge: `git merge-tree --write-tree origin/main(35c3e31cc9) <head>` exits 0 (tree 338732fae0). The main table is unchanged from the merge base to origin/main.
- The body's `## Head` names this head.

## CI
- Every check run at this head has completed (ev/ci-checkruns.txt).
- `governance / instrument-self-tests` job 137076225595 succeeded (03:17Z to 03:46Z). It was cancelled in the previous fire.
- The code run's gate, job 137088560925, succeeded at 04:12Z.
- The one red is the edit run's gate, job 137029528697 at 23:57Z. That is the edit-run deferral the body describes.
- No owed red is red at this head.
- `merge_train.py classify` exits 3 (WAIT, pending: gate red: none): it defers that red while the gate-sweep.yml runs queued at 04:07Z to 04:24Z can re-judge it. Classify was polled 60 s or more apart from 04:24Z to 04:54Z and printed WAIT on every poll; the polls are in ev/classify.log and ev/classify.rcs. Its last line is `WAIT dd2f26e749d54d7295dc2873a601487ce59367a4 pending: gate red: none`. In that time no gate-sweep run started.
- The verdict is pending `gate` at this head. The relay must not post it over a red, or after the head moves.

## Findings
- Follow-up: the table is stale against current main, measured rather than inferred. The head's table replayed against main's later `selftest-closures` artifacts gives 3 refusals: 14734763358 of run 44964363447 at e4c929bd1c, and 14737820685 of run 44970308211 at f269ecccb5. The refusing steps are prepr, dependency-graph-census and policy-lint-mutants. Each one misses #3814's 4 directories under `dev/audit/rounds/round11/D3/s1/state/` (ev/drift-replay.txt). The `selftest-absorbed` artifact 14737054783 of run 44970308211 is this head's table plus 12 reads, with none removed, and it replays to 0. Main's drift step therefore stays red after this merge until a re-absorb lands; that is the hotfix family's open root cause, a hand-committed absorb that lags each merge adding a read. Carry: dismissed: the automatic absorb job that settles it is unbuilt pending the owner's D1/D2 ruling (bugclasses.json countermeasure text, body item 132fe653), so no group can take it now
- Follow-up: a pull request that changes only `tools/ci/selftest_closures.json` still runs all 127 self-test steps under the 30-minute pull-request cap. That is the margin the reviewed head's job hit. Carry: dismissed: already recorded in the instrument round-end triage (body item d45f668f), with no roster group to take it

## Notes
- Note: stale-body: the Red checks section says the drift step "goes green on the first main push after merge". The replay against main's newer measurements gives 3 refusals (first Finding).
- Note: harness: the finder's harness is the committed CI drift step (`selftest_scope.drift`). The fixer's `drift_harness.py` and this reviewer's `ev/drift_rev.py` are each disclosed as their builder's.
