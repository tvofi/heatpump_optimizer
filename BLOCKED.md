BLOCKED: r10-dispatch-at-handoff-p2 body repair (head 5f28e55aae26748ab33274d87c1ab8d79d7e50b2)

The body's `## Head` now names 5f28e55a and lists the commits after e27484ff. `## Red checks` stays `none`.
prepr.sh and body_push.sh both refuse it for a code reason:

pr-body ERROR [pr-body] BODY.md: check `governance / instrument-self-tests` is red and `## Red checks` does not name it. Name the failure and answer it: the cheaper detector and its standing cost, or the finding that none exists.
body_push: REFUSED BODY-LINT

Cause: the policy_lint at this head still requires an answer for every red. `merge_train.py owed-reds`
does not exist at this head. Run from origin/main's copy, it lists 23 owed checks and `governance / instrument-self-tests` is not among them (only `tests / arch-instrument` matches "instrument").
Under the owner ruling of 2026-11-09 that red is owed no answer, so I did not add one. Fix: merge origin/main into the handoff (brings the owed-reds-aware lint) or have the relay accept the answer.
Also: body_push ancestry reds read code-scanning alerts as NOT READ (HTTP 403).
No code was changed. The refused body is kept at refs/heads/handoff-wip/r10-dispatch-at-handoff-p2-body 38150311713697dc20001560bed014fb8c8ed967.
