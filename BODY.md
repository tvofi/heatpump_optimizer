Group R10-FLY-NO-FOOTERS-EMITTERS (follow-up of R10-FLY-NO-FOOTERS, done at 7deeef1b6b). Part of #201.

#2636 made ref_privacy and policy_lint refuse a `co-author-trailer`, but two producers on main still write one into the commits they make: `commit_row` in tools/audit/seat/delivery_row.sh (every open_pr.sh and update_pr.sh row commit) and the stamp commit in tools/release/stamp.py. Both now emit the subject alone. stamp.py's message moved into `stamp_message()` so its self-test can drive it.

Opened with the tools from this fixed worktree, so the opener's row commit is made by the fixed delivery_row.sh. Not a bypass: every refusal in open_pr.sh and app_push still runs; only the producer it calls is the fixed one.

## Head

`01ee39a074a230b1fb4ef1b1d22c3057d5e2dc38` (code head; the opener appends the row commit).

## Mutation proof

- Trailer restored in `commit_row`: `bash tools/audit/seat/delivery_row.sh --self-test` gives `FAIL the row commit's message carries no attribution trailer`, 6 checks, 1 failed. Restored: 6 checks, 0 failed.
- Trailer restored in `stamp_message`: `python3 tools/release/stamp.py --self-test` gives `FAIL stamp message: ref_privacy's own reader finds no attribution in it` and `RESULT stamp_self_test=fail`. Restored: `RESULT stamp_self_test=pass`.

Both rows read the message through `ref_privacy.attribution` (imported, not a copy of its pattern).

## Null control

Each row also asserts `ref_privacy.attribution` does flag a message carrying the banned trailer (stamp row), and the delivery row reads a real commit made by `commit_row` in a throwaway repo. At origin/main (a243a79f4) the delivery row commit carries `Co-Authored-By: Claude Opus 5.5` and `stamp_message` does not exist, so the new rows cannot pass there.

## Figures

- `bash tools/audit/seat/delivery_row.sh --self-test`: 6 checks, 0 failed.
- `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 87 self-testing, 87 wired, 0 unwired.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, 2 scripts (tests/doc_claims.py, tests/entities.py); both pass.
- Class sweep, rule: `git grep -n -i 'co-authored-by\|noreply@anthropic\|Generated with \[Claude\|Claude-Session' -- tools .github .claude dev`. Dispositions:
  - tools/audit/seat/delivery_row.sh (commit message): producer, fixed here.
  - tools/release/stamp.py (stamp commit message): producer, fixed here.
  - tools/audit/seat/ref_privacy.py (pattern, self-test fixture, noreply email_leaks fixture), tools/policy/policy_lint.mjs (patterns, body contract), tools/policy/agreement_py.py (agreement fixture): refusal patterns and fixtures, quote the text, produce nothing.
  - tools/audit/seat/cloud_dispatch.py FOOTER_BAN: instructs a seat not to write the lines; not a producer.
  - tools/audit/carry_audit.py (TRAILER regex; self-test fixture at the attribution-trailer row): reader and fixture, produce nothing.
  - tools/policy/fixtures/policy-rot/prepr/*.md: policy-rot fixtures that quote the banned text.
  - dev/audit/rca/R10-RCA-BODY-LINT.md, dev/audit/rca/v6612-root-cause.md: records recounting history; no producer.
  - .github/, .claude/: no hit.

## Red checks

The red: app_push's ref_privacy refusals on #2651's opener run (roster seat, 06:1xZ): `ref_privacy: REFUSE: co-author-trailer in the message of <row commit>`.
- Cause: #2636 added a refusal on commit messages without enumerating the instruments that write commit messages; `commit_row` and the stamp commit hardcoded the trailer from before the rule.
- Process state: the cheaper detector existed (a producer sweep, the grep above, seconds) but the refusal's review did not run it; no self-test of a producer read its own output through the new reader.
- Countermeasure built: each producer now pins its own message through `ref_privacy.attribution` in its self-test, so a producer that regains a trailer fails its own file's self-test and the scoped gate that reaches it. Recorded refusal: a global "no producer emits a banned line" census. The sweep above returns only quoting hits and two instances do not meet the recurrence trigger; a census over free-text commit sites would cost more than the per-producer pins it adds.

## Forward-carry

none

## Friction

none
