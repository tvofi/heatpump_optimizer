# Proposal triage, session s14, batch 164 (P578)

This batch rules `s7/triage-queue-s7.txt` line 260. The bar and the denominators are batch 141's.

Sources:
- origin/main `dbd1ab5b07`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster` (33adcf993e).
- `git ls-remote origin 'refs/heads/design/*' 'refs/heads/design-verdict/*'
  'refs/heads/dispatch/design-reviewer-*'` at 05:20Z: 29 design refs, 27 verdict refs and 19
  dispatch refs. All of them were fetched, and every time below is a committer time from `git log`.
- No GitHub API calls.

## P578: DESIGN-REVIEW-OWED-NO-BOARD-LINE

Verdict: ACCEPT. A new tick line in the owed family, `DESIGN-REVIEW OWED:`. It goes to
R10-TICK-RESIDUE as a PART 2 carry. The line is git only, keyed on the group and the design tip.
It reuses the refs `design_builds` already lists, so it adds one fetch per pass and no API call.

Source: queue line 260, 2026-11-11T05:06:21Z, orchestrator s14.

Instances:
- **The gap in the tick.** The tick prints two design lines:
  - `DESIGN OWED:` (`orchestrator_tick.py:1608`), only when no `design/<g>` ref exists;
  - `DESIGN-BUILD:` (`:1660`, `ledger.py:621`), only on `Design review: approve <sha>` at the
    tip (`ledger.py:123`).

  A design tip newer than a `revise` verdict fits neither. The tick has no line for it, so a
  revised design that nobody dispatches is invisible to the board.
- **`owed_unactioned.py`** keys only the `FAMILY` prefixes at line 56. `DESIGN OWED` is not among
  them, so even the existing designer line is never tracked as unactioned.
- **The three cases named in the queue line, replayed at 05:06Z.** For each group: the design
  tip's commit time, the last `dispatch/design-reviewer-<g>` commit before 05:06Z, and the
  verdict first line before 05:06Z.

  | group | tip | tip time | last dispatch before 05:06Z | verdict before 05:06Z |
  |---|---|---|---|---|
  | R10-STANDING-CONTRACTS-P2 | a249d768 | 00:43:43Z | 00:11Z | `revise 5bcd069c` |
  | R10-ADVISOR-STEADY-START | d2d663c3 | 00:43:45Z | 00:12Z | `revise e29f9b4a` |
  | R10-DUTY-SWITCH-RESTART-LEARNING | abc57517 | 00:50:34Z | 00:17Z | `revise edf2ceb3` |

  In all three, the verdict names a sha that is not the tip, and the last dispatch predates the
  tip. The rule therefore fires 3 lines at 05:06Z.
- **After the orchestrator acted.** Reviewers were dispatched at 05:07-05:08Z, and verdicts
  `approve <tip>` landed at 05:15-05:17Z. Each verdict now names its tip, so the rule fires 0
  lines for these three.
- **Null control, at 05:20Z.** 4 of 29 designs have a verdict that does not name their tip:
  r10-arch-docs-first, r10-hotfix-codeql-headroom, r10-orch-machinery and r10-user-docs-final.
  All four groups are `done` at 33adcf993e, so a stage gate excludes them. The other 25 have a
  verdict at the tip. The rule prints 0 lines at 05:20Z.
- **Frequency and cost of the state, measured.** For each verdict commit in every
  `design-verdict/<g>` history, I measured from the commit time of the tip that verdict names to
  the first `dispatch/design-reviewer-<g>` commit at or after that tip
  (`s14-7/design-lat.txt`, 51 verdicts).
  - 33 of the 51 have a reviewer dispatch ref. The other 18 predate the dispatch refs.
  - Median dispatch latency 0.8 h; p75 15.05 h.
  - **15 of the 33 waited more than 2 h, 420.9 h in total.**
  - The longest: r10-ceiling-probe 104.3 h; R10-ADVISOR-WHATIF 96.2 h; r10-fly-standing-contracts
    60.1 h; R10-ADVISOR-STEADY-START 25.0 h; R10-STANDING-CONTRACTS-P2 24.2 h; R10-ARCH-DOCS
    22.9 h.
  - Caveat: a commit time is no later than its push, so these are upper bounds. Some waits may
    have been deliberate holds. Even at a tenth, the state costs tens of hours of L/XL
    critical-path wall time across the round.

Cost:
- **Code.** About 25 lines in `orchestrator_tick.py`, beside `design_builds` (`:1660`), plus one
  `FAMILY` prefix and one key branch in `owed_unactioned.py` (lines 56, 118). Both files are
  R10-TICK-RESIDUE's.
- **Reads.**
  - The line widens the existing `ls-remote` at `:1667` with `refs/heads/dispatch/design-reviewer-*`.
  - It adds one `git fetch` of the design and dispatch tips, needed for commit times. That is
    git only and incremental: about 48 refs, almost always already present.
  - No API call.
- **Checks.** 2 self-test arms, next to the DESIGN-BUILD arm (`:5071`). No new file, check or
  workflow.
- **Hot file.** `orchestrator_tick.py`. It goes to the group's next part, not PR 3425.
- No capped file is touched by the ruling itself.

Binding:
- Benefit: 15 waits over 2 h, 420.9 h in total, against a cost of about 25 lines and one
  incremental fetch per pass. Even discounted tenfold for deliberate holds and the upper-bound
  times, this clears the bar.
- This is a new line for an observed silent state, not repair of a low- or normal-severity
  instrument, so the 20% machinery rule does not apply. The measured gain is far above it anyway.
- Rule, run per instance (results above):
  - 3 lines at 05:06Z;
  - 0 lines at 05:20Z, where 25 designs have a verdict at the tip and 4 are stale on `done`
    groups.
