# The instruments kept live, and where rounds 1, 2 and 3 went

## Rounds 1-3 are at a tag

`tools/audit/round1/`, `round2/` and `round3/` held 212 files and 5.5 MB of
write-once evidence for three closed rounds: reports, panel and judge verdicts,
mutant patches, quiet-window logs, `.out` files. Nothing in the gate reads them
(`tools/audit/` is `INERT` in `tests/closure.py`), and every number they carry
that anything still acts on is in `docs/audit-2026-09.md`, which stays.

They are reachable in full at **`d5d8c4a72fa7be7aebecc9e58d55002be17cac08`**
— `origin/main` at v6.3.18, the commit this archival was cut from, and
permanently on `main`'s first-parent history:

    git show d5d8c4a:tools/audit/round2/JUDGE.md
    git checkout d5d8c4a -- tools/audit/round2/D5/REPORT.md

Every citation in the tree names that SHA rather than a tag, because a SHA
cannot move and needs nobody's permission to exist; the owner may add named
tags at `d5d8c4a` for memorability, and nothing here depends on their doing so.
`audit-round2-evidence` is the counter-example: a real tag on the remote that
has already been moved once, which is why `tools/audit/README.md` tells you to
cite the SHA you actually ran.

Round 2's *executable* harnesses were archived earlier and separately, at
`audit-round2-evidence` (`757e164`); `tools/audit/README.md` carries the rule
for running one, and the root-resolution trap that has caught three reviewers.

The done wave rosters — `wave-1b-groups.json`, `wave-2-groups.json`,
`wave-3-groups.json` — were archived at that same commit, along with
`web-phase0.js` and `triage-quiet-judges.json`. Their briefs record what a
judge established and refuted, so read them before re-deriving anything a group
in them already settled.

## The three that stayed

Each was added by a fix pull request *after* its round closed, and each is an
instrument someone re-runs rather than a report someone reads. That is the whole
of the rule: evidence is archived, instruments are kept.

| file | metric | added by | who re-runs it |
|---|---|---|---|
| `j5_gil.py` | starvation share = sum(heartbeat gaps > 5 ms) / solve wall, on a real asyncio loop with a 1 ms heartbeat and `HeatPumpOptimizer.optimize` submitted the way production submits it | `8542e51` (W3-G3, #290 #199) | the #290 judge built it; `briefs/fix-review.md` §9 sends a fix reviewer to it |
| `h8_single_scenario.py` | whether the stress gate detects a 2x regression confined to one scenario, and stays quiet on a multi-start basin flip (#346) | `291ae76` (#378) | anyone changing `tests/stress.py`'s per-scenario or solver-work rules |
| `h9_basin_coverage.py` | how many of the 51 sweep scenarios the solver-work rule judges rather than exempts, against the tree's own floor (#387) | `32f309f` (#388) | the same |

All three drive production symbols and print `RESULT` lines under the harness
contract in `tools/audit/README.md`. `j5_gil.py` must never be run on
`FakeHass`, whose executor runs inline and would measure nothing. Their run
commands were updated to this directory when they moved; nothing else changed.

## The five that did not

`round1/B3/harness.py`, `round1/B4/entity_hygiene.py` and
`round1/B5/harness.py` are fix-group harnesses for groups B3, B4 and B5, merged
as #206, #205 and #207, every issue closed. `round3/closures-gate/mutations.py`
and `replay.py` are #356's mutation proof and its five-incident replay, both
spent once that change merged. All five are at `d5d8c4a`; copy
one out if a later round needs it, rather than assuming it still runs — the rot
classes in `round2/HARNESSES.md` apply to them too.
