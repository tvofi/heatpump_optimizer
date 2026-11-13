# Proposal triage, session s14, batch 225

Source: the orchestrator's message to the triage seat (2026-11-12), ruled as P680. Line numbers
are at origin/main 47788534da. Roster read at handoff/audit-r10-roster 8ab8d08a00.

## P680: main's instrument-self-tests job is red on an under-scoped prepr closure

Verdict: ACCEPT as a new hotfix group, R10-HOTFIX-MAIN-IST-PREPR-SCOPE (size S, severity high,
class hotfix). Main is red, so the 20% bar does not apply.

Evidence: main's push CI at 6d16af36c2 (#3482 merge), job governance / instrument-self-tests,
prints `UNDER-SCOPED step prepr: files misses ['dev/audit/harnesses/mutant_guard.py',
'tools/audit/seat/mutant_run.py']` and `selftest_scope check: 111 gated step(s), 1 refusal(s)`.
The workflow requires "0 refusal(s)". Two notes also report over-scoped entries: steps
cloud-dispatcher and prepr each name 1 file no longer read.

Home: the table is `tools/ci/selftest_closures.json`, read and written by
`tools/ci/selftest_scope.py`, whose docstring states the re-record rule (`record` on Linux with
strace, or commit the `--write` measurement main uploads as the `selftest-closures` artifact).
No open roster group owns this red. Every group naming selftest_scope or the closure table is
done. R10-HOTFIX-PREPR-WC-PAD touches the same script, but its fixer was dispatched before this
red was known, so it does not get this as a carry.

Cause: the #3455 merge, 046736a49f, changed `tools/pr/prepr.sh` so that its self-test runs
`tools/audit/seat/mutant_run.py`. The closure entry for the prepr step was not re-recorded.

Cheaper detector: `prepr.sh` or ci_predict could run `selftest_scope.py check` before handoff
whenever a gated step's script changes. That is recorded as a carry for the root-cause record.
This ruling does not build it.
