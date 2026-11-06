CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-planted-defect-audit, at head b88684a218923f85de66f1e8fb1833e31a76a154. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch b88684a218923f85de66f1e8fb1833e31a76a154 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-planted-defect-audit before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-planted-defect-audit, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-planted-defect-audit, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-planted-defect-audit <body.md>`, which pushes refs/heads/handoff-body/r10-planted-defect-audit; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-planted-defect-audit`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-planted-defect-audit and refs/heads/handoff-wip/r10-planted-defect-audit-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
tvofi 2026-11-01: dispatch one planted-defect audit per tripped arm, adopt P0=0.28/ALPHA=0.05, never block. A review-strength guardrail trip (`review_strength.py --guardrail` printing would-trip) dispatches the planted-defect audit it names, keyed by arm and cut, never twice for the same line, nothing for ok or insufficient; the guardrail still sets no exit code and blocks nothing. The ruling on the R10-FLY-YIELD-GUARD entry in dev/programme/carries/carry-201.json is made; the owner gate is cleared and this group is dispatchable. Stranded on R10-ORCH-DISPATCH-REG and R10-ORCH-BEATD, both done. Every carry was moved verbatim by the s9 carry-routing pass (2026-11-01) from a carries-open source group; each names its own controls. Re-measure every figure a carry states at this group's own merge base; carry no count. A carry that says it waits on this ruling no longer waits: the ruling is made.

After: none

Carry 0: STRANDED CARRY 13 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-DISPATCH-REG, index 9; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: owner-gated: #2865 item [9]; carry-201.json R10-FLY-YIELD-GUARD entry has no ruling; mirrors BEATD [29]/[33].

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From #2765 (R10-FLY-YIELD-GUARD, round-1 fix review review/2765): a review-strength guardrail trip names a planted-defect audit that nothing dispatches. `review_strength.py --guardrail` prints `would-trip: audit the last reviews with a planted defect` and stays report-only under owner ruling R13; low incidence is also what a scarce supply of defects produces, and only a defect of a known class planted in a reviewed head, scored caught or missed, separates weak review from scarce defects. Dispatching that audit is this group's work (the dispatch half of standing-dispatch.md becomes a beat job owned by this group's registry). Precondition, not opportunity: the dispatch is built behind the owner's ruling on whether a trip dispatches at all (dev/programme/carries/carry-201.json, the R10-FLY-YIELD-GUARD entry); until the owner rules, a trip dispatches nothing and changes no exit code. Control, once built: a `would-trip` arm line dispatches one audit seat per tripped arm, keyed arm and cut, and a repeat of the same line dispatches none; the null control is an `ok` or `insufficient` arm line, which dispatches nothing. Re-measure at your merge base: `python3 -I tools/audit/seat/review_strength.py --self-test` (every check ok), then `--fetch --window X=2026-10-01T00:00Z..<now> --guardrail` and read which arms trip on the live bus; the trip state is a snapshot of the bus at its fetch.

Carry: R10-ORCH-LEDGER

Carry 1: STRANDED CARRY 48 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 29; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: owner-gated: #2865 item [9] "Not built: behind the owner's ruling in dev/programme/carries/carry-201.json (the R10-FLY-YIELD-GUARD entry), which has not been made"; no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From R10-ORCH-DISPATCH-REG (handoff de66f00b): **A guardrail trip dispatches a planted-defect audit.** Not built: behind the owner's ruling in `dev/programme/carries/carry-201.json` (the R10-FLY-YIELD-GUARD entry), which has not been made. The precondition holds at this head: the live `--guardrail` run under Figures prints `would-trip` on the `local` arm and exits 0 at both base and head, and this PR adds no dispatch on it. The dispatching job is the beat's dispatch half ([5]). Control to carry: a `would-trip` arm line dispatches one audit seat per tripped arm, keyed arm and cut, and a repeat of the same line dispatches none; an `ok` or `insufficient` line dispatches nothing.

Carry: R10-ORCH-LEDGER

Carry 2: STRANDED CARRY 50 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 33; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: owner-gated: #2865 item [9] "Not built: behind the owner's ruling in dev/programme/carries/carry-201.json (the R10-FLY-YIELD-GUARD entry), which has not been made"; no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
**R10-ORCH-BEATD: carry [9], the planted-defect audit dispatch,** behind the owner's ruling in `dev/programme/carries/carry-201.json`; the control is as written in carry [9] above. Carry: R10-ORCH-BEATD

Carry: R10-ORCH-LEDGER
