Fix review: blocked 45339147f9fbeffb50df4cbcf047ac248b94efb4 class-open: tools/audit/seat/plan_audit.py:569 asserts the old fixture identity "t <t@t>" that this PR changed

bus-nonce: 86deb3c71a5cee2324a0c2403bdf05bb

## Block
- The PR moves the `tests/throwaway_git.{py,sh}` fixture identity from `t@t` to `1+t@users.noreply.github.com`. `tools/audit/seat/plan_audit.py:569` still asserts `git var GIT_AUTHOR_IDENT` starts with `t <t@t>`. Its self-test therefore fails: "plan_audit self-test: 27 checks, 1 failed" (CI job 128917294764, `governance / instrument-self-tests`, red at this head). I reproduced it locally with `python3 tools/audit/seat/plan_audit.py --self-test`. Changing that one assertion to the new identity gives 0 failed (ev/plan_audit-head.txt).
- The PR's enumeration (`git grep t@t`) covered the stubs that reach the guard. It missed this consumer of the harness identity, so the class is open: a consumer that hard-codes the fixture identity string.
- The red `governance / instrument-self-tests` at this head is a second failure. It differs from the app_push one the body answers. The body names no cheaper detector for it, so `root-cause-unanswered` also applies. A `git grep -n "<t@t>"` census at the time the fixture identity changes would have found it.
- `tools/audit/seat/delivery_row.sh:55` has a comment naming `t <t@t>`. It is stale but harmless.

## Findings
- Residual: `tools/audit/seat/delivery_row.sh:55` comment still names the old fixture identity `t <t@t>`. Carry: dismissed: comment only, fixed with the plan_audit.py repair on this PR.

## Evidence
- Reviewed head: 45339147f9fbeffb50df4cbcf047ac248b94efb4 (ev/HEAD.txt). `git merge-tree --write-tree origin/main` exits 0 (ev/merge-tree.txt).
- `ref_privacy.py --self-test`: 124 checks, 0 failed at the head, matching the body (ev/selftest-head.txt).
- My mutants (ev/mutants.txt) match the body: `email_shape` returning [] gives 7 failed; digits requirement dropped gives 5; committer-only restriction dropped gives 1; `PIN_HINT` print removed gives 2. I added a fifth mutant (adopted address admitted as committer), which gives 2 failed. All restored; the tree is clean.
- `app_push.sh --self-test`: 227 checks, 0 failed. `bus.sh` 159/0, `cloud_relay.sh` 381/0, `body_push.sh` 32/0, `handoff_push.sh` 6/0, `tick_loop.sh` 27/0 (ev/other-selftests.txt). `wt_sync.sh --self-test` printed no summary line in my run; I did not chase it.
- `VERSION` and release notes: untouched by the diff. The three-dot role-contract diff on main touches only `proposal-triage.md`.
- CI at this head (ev/checks-final.txt): every check green except `governance / instrument-self-tests` (failure) and two aggregate `gate` runs (failure). One of those `gate` runs was the transient "still being judged" state, and `gate` also has a success. `classify` printed WAIT throughout; it never reached a verdict.
- Round: first review of this head.
