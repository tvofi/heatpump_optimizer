Fix review: merge 8e4957cf0ffb4c892f7aed9d092687cb6b232346

bus-nonce: dd59ec6e3eeff524761b21714d242a83

## Evidence

- Round: later round (delta) over the reviewed head 991ff6e21ab2b68fd71f5143e99319f937751ba2, whose verdict was merge with no findings. Measured head 8e4957cf0ffb4c892f7aed9d092687cb6b232346 (ev/HEAD.txt); the branch still pointed there when I posted (git ls-remote).
- RESULT delta: the PR's patch against its merge base differs from the reviewed head's only in tools/audit/seat/cloud_dispatch.py (+4/-3, from 5c1c05d0ee). The cloud_relay.sh patch is the same as at the reviewed head. The rest of the delta is main merged in. Nothing in custom_components/ changed, so the scope is not widened.
- RESULT self-test at head: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` printed `cloud_dispatch self-test: 169 checks, 0 failed` with rc=0 (ev/selftest-head.txt). The previously red check `a handoff-wip push is invisible to cloud_relay.sh's handoff arm and bus.sh orphans; handoff/ is not (null)` prints `ok`.
- RESULT mutants (ev/mutants.txt). Null tree: rc=0, 0 failed. m-nodedup (dict.fromkeys removed, which brings back the 5-glob count) KILLED. m-nofilter (WIP_NS filter disabled) KILLED. m-relay-wide (the cloud_relay.sh handoff glob widened to `refs/heads/handoff*`, which matches handoff-wip) KILLED. Each was killed by that same check, at 1 failed. The new `len(globs) == 2` pin checks the number of distinct globs, not the named set its comment describes, but every mutant that widens or duplicates a glob still fails.
- RESULT the introduced red is answered in the body. `## Round 4` and `## Red checks` name the instrument-self-tests step `Show the cloud dispatcher refusing its own fixtures`, its cause (this diff's second listing of `refs/heads/handoff/*`), and its detector, the self-test itself, which prepr.sh does not run. `merge_train.py owed-reds` does not list governance / instrument-self-tests (ev/owed-reds.txt). This is an INTRODUCED red under fix-review.md step 11, and it is fixed at this head.
- Figures re-derived at head: cloud_relay self-test `452 checks, 0 failed` (ev/relay-selftest.txt); cloud_dispatch `169 checks, 0 failed`; `python3 -I tools/ci/selftest_scope.py --self-test` printed `117 checks, 0 failed`; `STRUCTURE RATCHET PASSED` (ev/structure.txt). I did not re-run the earlier rounds' figures (416/443/444 and the round-3 mutant table). They were verified at 991ff6e2, and that code is unchanged.
- Merge: `git merge-tree --write-tree origin/main 8e4957cf0f` returned rc=0 with no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify 8e4957cf0ffb4c892f7aed9d092687cb6b232346 --pr 3448` printed `GREEN 8e4957cf0ffb4c892f7aed9d092687cb6b232346 pending: none red: none` with rc=0 at 15:31:14 UTC, after WAIT polls from 15:04 (ev/classify.txt). review_packet refused `introduced-red: unreadable` while instrument-self-tests was still running. classify decides, and it now reads GREEN.
- The body's `## Head` paragraph still gives merge base f24d107bd7 and says "main was not merged". At this head the merge base is 19baca7618, and the head merges main through 9b27db2cc6. The red head is also named as 6d4be3faca, where the brief says 9b27db2c; both are ancestors of the head. This is stale body prose only. No figure or check depends on it. Carry: dismissed: stale body prose about a superseded merge base; it changes no stage and no measurement.
- Self-audit: `carry_audit.py check` on this verdict returned rc=0, with 1 item routed and 0 unrouted. I ran it with a stub body because this seat cannot fetch the PR body as a file. The packet's `carry_audit at the head` reads the real body as 0 finding items.

## Findings

none
