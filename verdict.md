Fix review: merge a6c4c5207757d70e3e1c594391a534ddbd87aff3

bus-nonce: 620de170084e014b1bba15e963bb9cda

Head reviewed: `a6c4c5207757d70e3e1c594391a534ddbd87aff3` (re-read by `git ls-remote` before and after the gate wait; unmoved), from a detached worktree at that SHA. The head carries origin/main `10f459f18` through the merge `9b6558a7c`.

## Scope

Three-dot diff against the merge base: `dev/programme/triage/s6-batch34.md` (new, 182 lines) and `dev/programme/delivery/2862.md` (this PR's own row, one line). Nothing else, which is what the body names. Claim files, `VERSION`, manifest and release notes untouched.

## Against `proposal-triage.md`

- Each of P195-P198 is one `## P<n>:` entry with `Verdict:`, `Source:`, `Instances:`, a cost (`Cost:` for P195, P196, P198; `Cost of the filed arm:` for P197, the same form `s6-batch21.md`, `s6-batch32.md` and `s6-batch33.md` use) and `Binding:`.
- ACCEPTs name destinations: P195 a carry of R10-FLOW-BODY-ONLY, P196 a carry of R10-996-RUNNER-CLAIMS, P198 a new group R10-RECORD-HOLD-APPROVE with its brief. The DEFER (P197) names its owner (R10-ORCH-BEATD carry 13) and what would change the answer. Each rejected arm names its binding cost.
- Cost/benefit is argued before the verdict in every entry, and each "narrowed" ACCEPT is narrower than the filing in a direction the binding names (P195 rides a dispatch rather than standing alone; P196 keeps the both-sides refusal; P198 takes arm (b), refuses (a) on identity and hot-file surface).
- Instances carry their reference beside the figure (ledger lines, run ids, comment and review ids, commit SHAs, grep commands).
- Code citations re-checked at the head: `nightly.yml:913` is the step "Approve and merge a row-only record pull request"; `HOLD_REF=train-hold` at 973 precedes `if ! guard` at 1004; THE PITCH at 1021; `policy_lint.mjs:6835` is `resolvePathToken(tok)`; `body_patch.sh` 26/80/98 carry the quoted phrases and the contract call; `merge-main.yml:74` installs the driver; `merge_train.py` 4330-4396 holds K15 (c) with the claimnotes driver; `merge_train.py:1045` "the approver App's review is the beat's"; `tests/entities.py:28290` carries the pitch-order pin; `_train_hold_status` at 28174; `brief_lint.mjs` is 1,344 lines and `handover_prompt.py` 280, as stated. `merge_claim_file` at the head still returns None whenever both sides changed the claim map, so P196's arm and its 20-40-line estimate are not overtaken by #2843 (which left that function's decision unchanged).

## Instruments

- `node tools/policy/brief_lint.mjs`: rc 0.
- `tools/pr/prepr.sh --body-check` on the live body: rc 0 (`PR-BODY: 0 error(s)`; `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster 94d14569e`; `preflight ok`).
- Figures re-run: the body's `grep -oE '^Verdict: ...' | sort | uniq -c` prints 3 ACCEPT, 1 DEFER; `grep -c '^Instances:'` prints 4. Both match.
- Consumer and null control: `roster_edit.ruling_verdict` returns ACCEPT for P195, P196, P198, DEFER for P197, None for P199.

## The held roster ops

The dispositions support all three ops the body names, including the reopen. P196 is ACCEPT with R10-996-RUNNER-CLAIMS as its destination; on the roster branch at `94d14569e` that group is `resume.stage: done` (#2843, `bb8addd89`), and a done group is not a destination (`finding-propagation.md`), so the append must reopen it for the carry to land anywhere. The roster note there already holds the P196 carry for this batch.

## Checks at the head

Both `CI code` and `CI edit` runs for PR 2862 completed success. `gate` success (check runs 121633948027 and 121632178251), `pr-contract / pr-contract` success (121633564895, 121631856492), `governance / delivery-status` and `governance / instrument-self-tests` success. All check runs at the head: 38 success, 17 skipped, none failed, none pending. No red check, so no root-cause answer is owed.

## Non-blocking notes

- P196's text states R10-996-RUNNER-CLAIMS at "stage `queued`" and that the arm "can land as the group's first PR, ahead of the grammar", and the body's P196 bullet says "landing as that group's first PR". Both are false at this head: #2843 (`bb8addd89`, an ancestor of the head) was the group's first PR and landed the move-keyed claim grammar. The file declares its facts read at 510787b76, which predates #2843, and the body's Routing paragraph states the done stage correctly, so the verdict and destination are unaffected; the reopen op's text must say the P196 arm is the group's second PR, after the grammar. Carry: R10-996-RUNNER-CLAIMS
- P195's carry needs `tools/policy/brief_lint.mjs` and `tools/audit/seat/body_patch.sh`, neither of which is in R10-FLOW-BODY-ONLY's `files` on the roster branch (`update_pr.sh`, `cloud_relay.sh`, `pr_args.sh`, `INSTRUMENTS.md`); the ruling names the first as outside them. The append-carry op widens `files` to both, or the group's fixer edits outside its declared set. Carry: R10-FLOW-BODY-ONLY
