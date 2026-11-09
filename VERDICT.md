Fix review: blocked 40c79702c72359f00a0a932eabf727a942b1f9eb ci-red: required context gate is red at this head in the push-time suite 115222010076 (run 128906901790), never re-run; classify exits 1

bus-nonce: 4d1f7e0e4846bb280d0368717412fa35

Round 1. Measured head 40c79702c72359f00a0a932eabf727a942b1f9eb (the PR head at the time of writing). The fix itself is sound; the only block is the red gate suite, which needs a re-run of that suite's gate (or a fresh head), after which this verdict should be re-taken at once.

## Block

- `python3 tools/audit/seat/merge_train.py classify 40c79702c72359f00a0a932eabf727a942b1f9eb --pr 3359` exits 1: `RED 40c79702c72359f00a0a932eabf727a942b1f9eb pending: none red: gate` (ev/classify-final.txt). The head has three gate runs in three check suites: 128906901790 (suite 115222010076, workflow run 42537694877) concluded failure at 00:04:53Z; 128920004891 and 128920774162 later concluded success. `latest_runs` keeps the worst gate across suites (A5), so the older failure stands.
- The failed run's log (job 128906901790) ends `FAIL run(s) [42537695400] at this head are still being judged; their gate decides`: it judged while sibling runs were still pending, and no later run of that suite exists. The review packet at render read `red-unanswered` / `required-red` for it; re-rendered later (ev/review-packet-final.md) it read `Gate digest: green` and no refusals, because the digest keeps the latest gate only. The instrument that decides the train's admission is classify, so I follow it.
- Root-cause trigger (fix-review step 11): the body's `## Red checks` says `none`, written before this head's CI began. The later pr-contract run 128917889353 (success, started 00:50:25Z, after the red gate concluded) is the evidence the contract accepts, so I do not block on root-cause-unanswered; I block on the live red alone.

## Findings

- A push-time gate that fails with `still being judged; their gate decides` leaves its own check suite red for good, and classify's A5 rule (worst gate across suites) then reads the head RED although every later gate is green. This PR's rejoin keys on exactly a red holding gate, and its candidate predicate `GATE in s.red` cannot tell this stale-suite red from a real one; a rejoin of such a head would read RED and stay skipped. Carry: #201

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 40c79702c72359f00a0a932eabf727a942b1f9eb` rc 0, tree 1dfec79bee195c76ab41ec68b83a105f46263548, no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- Head 40c79702 is the authored code head 1dae7f1c plus a main merge 2b9984cb and the PR's own delivery row; VERSION is 7.1.8 and unchanged, and the diff touches no manifest, RELEASE_NOTES or claimed_drift file, so steps 4 and 5 hold (no golden fixture moves).
- dev/governance/roles/fix-review.md is unchanged between the merge base and origin/main.
- Mutation proof, step 1: the PR's own harness `python3 dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py` at the head printed `MUTANTS: 20 run, 0 not as required` (M0 PASS, M1 to M19 KILLED; ev/mutants.txt). This is the fixer's harness: the finding names none of its own (packet: `Finder's harness: none named`), which I disclose, and I did not build another. CI's mutation job concluded success.
- `python3 tools/audit/seat/merge_train.py --self-test` at the head: `merge_train self-test: 580 checks, 0 failed`, matching the body (ev/selftest-head.txt). The base's 564 I did not re-take.
- `bash tools/audit/seat/pr_args.sh --self-test` at the head printed `pr_args self-test: 195 checks, 0 failed`; the body quotes 185. I could not re-derive 185: the head contains a main merge, which probably added checks. Nothing failed, so this does not block (ev/pr_args-head.txt).
- Class enumeration, step 6, the body's rules re-run at the head (ev/enumeration.txt): `self.recarry(` returns four sites (2426, 2451, 2465, 3849), all handing on nr_base; `self.skip(` returns five, as the body lists; `MERGE CONFLICT` outside tests and docs returns remerge_main.sh and handoff_push.sh:201 (a merge-only chain, as the body says); remerge_main.sh has the single consumer merge_train.py. No seat is left undispositioned.
- Structure, architecture score, scoped gate and ci_predict figures in the body: I did not re-run these (CI's arch-score, closure-scope and fast runs are success); the packet's figure_lint resolved 15 of 18 commands and left 3 git-grep rules unverified, which I re-ran above.
- Forward-carry: carry-201.json carries the BOT_HEAD count to #201, a live destination (carry_audit at the head: 3 routed, 0 unrouted).
- CI at the end: classify RED (above); every other required and non-required run concluded success or skipped, none pending.
