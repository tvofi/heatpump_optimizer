## Summary

Pre-study (R9, seat `r9-closures-scoping-prestudy`): measured decomposition of the `closures` check's cost and an alternatives analysis with a recommendation, per tvofi's request. Study only — no production change, no fix.

- The re-record step is 98.9% of the job: 53 m 35 s of a 54 m 10 s push-to-main run (job `114258919874`); the batch proof measured 54 m 45 s (job `114247906174`). The checking steps after it are 0.2 s and 0.1 s.
- Lane 3 of `tests/derive_closures.sh` is the critical path at 53 m 35 s while lanes 1-2 idle after 15 and 21 minutes; `tests/boost_drift_replay.py` alone is 29 m 26 s — 55% of the wall.
- The CI job is already scoped on PRs; the full arm runs on main pushes (rule 1's detector), workflow_dispatch batch proofs, the nightly, and full-case PRs — 7 main-push runs on 2026-10-10 alone, ~8 full arms/day.
- Today's failure is the check working: PR #2109 took the 16-second skip fast lane, and only main's full arm caught `INERT READS UNDER-APPROXIMATED` (harness_headers.py rglobs `dev/audit/rounds/round*`) 54 minutes after merge.

## Alternatives and verdicts

- (a1) scope the batch/dispatch lane by its three-dot diff, fail-closed to full — preserves rule 1; saves up to 54 min per batch dispatch.
- (a2) make `inert_reads` visible to `affected`'s skip rule — turns today's incident class into a red on the PR in ~4 min; strengthens rule 1.
- (b) content-addressed recording cache — REFUSED: the key must contain the answer before the measurement that produces it; a stale restore is a wrong closure that stays green.
- (c) split the job — this is the current design; its residual costs are exactly a1, a2 and (e).
- (d) nightly full, per-PR static — REFUSED: a wrong closure survives ~5 merges; violates "red within one merge".
- (e) rebalance the derivation lanes — found by this study; same recordings, same checks, only scheduling; ~30-33 min wall instead of 53, ~40-45% off every full arm, zero change to the guarantee.

## Recommendation

(e) first — smallest PR (`tests/derive_closures.sh` lane layout only; acceptance: next push-to-main closures job green with all 33 recordings and re-record wall <= 35 min measured on two runs), then (a2), then (a1). (b) and (d) refused.

The full document, with the cost test, per-script table, provenance for every figure and an explicit unmeasured-box, is `dev/audit/rounds/round9/prestudy/closures-scoping-prestudy.md`.

## Figures

Every measured figure in this body, with the command that produced it (all run 2026-10-10 against job/run ids cited in the document):

- 98.9% re-record share of the 54 m 10 s job (53 m 35 s re-record; setup 33 s; check 0.2 s; no-copies 0.1 s): `gh api repos/tvofi/heatpump_optimizer/actions/jobs/114258919874/logs --allow-escape-sequences` (run 38067806307, push to main, 16:28:36Z-17:22:46Z).
- 54 m 45 s batch-proof closures job: `gh api repos/tvofi/heatpump_optimizer/actions/runs/38064024146/jobs` (job 114247906174, 15:32:29Z-16:27:14Z).
- 29 m 26 s boost_drift_replay.py recording, 53 m 35 s lane-3 critical path, lanes 1-2 done at 14 m 53 s / 21 m 22 s: the `[HH:MM:SS] record/done` lines of job 114258919874's logs (same fetch as above).
- 30 m 22 s on the 14:25Z push (full-arm range 30-55 min): `gh api repos/tvofi/heatpump_optimizer/actions/runs/38059574126/jobs`.
- 16 s PR #2109 fast arm (skip case): `gh api repos/tvofi/heatpump_optimizer/actions/runs/38058204083/jobs` (closures job 14:05:48Z-14:06:04Z).
- 7 push-to-main Tests runs on 2026-10-10; 12 merge commits; 686 commits since 2026-10-07: `gh api "repos/tvofi/heatpump_optimizer/actions/runs?branch=main&event=push&per_page=100"` filtered `name=="Tests"`; `git log --merges --since=2026-10-10T00:00:00Z origin/main | wc -l`; `git log --since=2026-10-07T00:00:00Z origin/main --oneline | wc -l`.
- 33 selectable scripts, 34 recorded entries, 4480 s = 74.7 min recorded work, 220.7 s harness_headers.py, 540 inert_reads files: `python3 -c` over `tests/closures.json` keys `recorded`/`inert_reads` at 969c3a5c84 (commands in the document, section 8).
- ~30-33 min projected lane-rebalance wall, ~40-45% saving: derived from the per-script measurements above; the derivation is in the document (section 4e); acceptance re-measures it on CI.

## Mutation proof

n/a: study-only seat, no production file changes; the diff adds one document under dev/audit/rounds/round9/prestudy/ (INERT, no .py/.mjs/.js/.sh sibling, so no discovery glob reads it).

## Null control

n/a: no behavioural claim made by code; every figure is a read-back from a cited CI job log or a committed data file, and the document's section 8 gives each figure's command.

## Red checks

n/a: no branch pushed for CI; the code head handoff/r9-closures-scoping-prestudy (177bb01c30) is one commit over origin/main 969c3a5c84 adding only the document.

## Forward-carry

The finding that the workflow's own comment prices the full table at "12-22 minutes" while it now measures 30-55 min belongs to whoever lands the follow-up PRs, as does the stale "~40 s an entry" line in .github/workflows/tests.yml's closure-scope comment (both named in the document, section 1.3).

## Friction

none

## Head

- Code head: `177bb01c30` on `handoff/r9-closures-scoping-prestudy` (one commit over origin/main `969c3a5c84`; adds only the pre-study document).
- Baseline: origin/main = `969c3a5c84` (2026-10-10).

_Requested by **tvofi**_
