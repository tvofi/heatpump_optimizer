## Summary

Pre-study (R9, seat `r9-covfast-scoping-prestudy`): measured decomposition of the `coverage` and `fast (3.14)` gates' cost, alternatives with verdicts, and a recommendation, per tvofi's request. Study only — no production change, no fix, no PR opened.

- On the watched push run (`38076804408`, main `6be88834e`): `coverage` finished at **61 m 01 s** (it was the run's critical path, not closures), `fast (3.14)` 52 m 17 s, `coverage-ratchet` 8 s. The measurement step is ~99% of `coverage`; grading and setup are noise.
- One script dominates everything: `tests/boost_drift_replay.py` is 81% of `coverage`'s critical lane (2925 s traced, 3.13), 86% of `fast`'s e2e lane (2323 s untraced, 3.14), and (per the closures pre-study) 55% of `closures`' re-record — ~2 h of lane time per push arm, and it runs in `fast` and `coverage` both.
- The variance is runner speed, not different work: the same script measured 1442 s and 2925 s traced in two push arms the same day — a uniform ~2x across every script. The "24-minute head" and the "35–46 min heads" are the same measurement.
- The premise corrected: PR heads are already scoped (both jobs — `GATE_SCOPE=auto`, and `coverage` reuses main's push per-script data via `coverage-split`). The full price is paid by the 8 push-to-main arms today and by PRs whose diff reaches `boost_drift_replay.py`'s 83-file closure — most production-code PRs.
- In-tree contradiction flagged: `run.sh` prices the replay at "three ~2-minute arms" (~6–8 min); it measures 38 m 43 s untraced — 4–6x the documented intent.

## Alternatives and verdicts

- (i) deduplicate coverage/fast into one run — REFUSED: the shared work besides the dominant script is ~700 s; a traced verdict lane fails the #525 heartbeat pair by design and drops one of the two interpreters the pair covers.
- (ii) scope by diff — already the design on PRs; the remaining full arm (push to main) is the detector AND the producer of the per-script base every PR reuses. Refused.
- (iii) nightly full, per-PR narrow — REFUSED: breaks the PR reuse chain (every PR a cache miss) and a drop survives ~5 merges; same argument as the closures pre-study's (d).
- (iv) shard — keep: a third coverage lane (boost alone) saves ~12 min per coverage run, zero safety change, contention bounded and measured on landing.
- (v) interpreter matrix — closed: the 3.13 suite leg was already retired with the tradeoff documented; removing either remaining leg reopens the #514-class hole.
- (vi) make the dominant script cheaper on the lanes that do not judge it — the real lever, found by this study: (vi-a) a cheap recorded invocation for `coverage` on the golden/env_drift precedent, proven by byte-identical per-script line sets (the R9-F10.14 shape); failure is loud — a line-skipping cheap run lowers the union and the per-module floor reddens. (vi-b) speed the replay itself (~288 real solves), as a fixer PR with mutation proof — the only lever that helps `fast` and the PR lane.

## Recommendation

(vi-a) first, then (iv), then commission (vi-b) as the prioritized fixer PR. Smallest first PR: a short-replay knob in `tests/boost_drift_replay.py` + its selection in `tools/coverage/coverage_tree.sh` + `tests/closure.py`'s recorded-argv rule; acceptance is byte-identical line sets on Linux CI and a measured green push run through `coverage-ratchet`. No `*_budgets.json` touched.

The full document — cost test with today's measured sums (coverage 6.6 h + fast 5.6 h + closures 5.7 h of push-arm lane time today), per-script tables, unmeasured-box and per-figure provenance — is `dev/audit/rounds/round9/prestudy/coverage-fast-scoping-prestudy.md`.

## Figures

Every measured figure, with its source (all read back from the API on 2026-10-10):

- 61 m 01 s coverage / 52 m 17 s fast / 8 s ratchet / 45 m 48 s closures on the watched run: `gh api repos/tvofi/heatpump_optimizer/actions/runs/38076804408/jobs`.
- Per-script walls (fast manifest, coverage `ran tests/… wall=Ns`): jobs `114285379973` and `114285380026` logs, `gh api .../actions/jobs/<id>/logs --allow-escape-sequences`.
- ~2x variance: job `114153557235` (06:38Z push) vs `114285380026` (18:41Z): boost 1442/2925 s, features 468/995 s, golden 130/259 s traced.
- PR-side durations 223–3639 s and reuse/miss behaviour: jobs of runs `38076465867` (`114284404870`), `38073939251`, `38073004857`, `38069955370` (`114265227002`).
- 8 push arms / 71 PR runs today, Σ durations (coverage 23 823 s, fast 20 005 s, closures 20 682 s): `gh api ".../actions/workflows/343082712/runs?per_page=100"` + `/runs/<id>/jobs` per arm.
- 83-file closure, 1489.6 s recorded: `tests/closures.json` at `6be88834e`.
- "~2-minute arms" comment: `tests/run.sh` at `6be88834e`; lanes and `min(nproc, 3)` same file.

## Mutation proof

n/a: study-only seat, no production file changes; the diff adds one document under `dev/audit/rounds/round9/prestudy/` (INERT, no `.py`/`.mjs`/`.sh` sibling, so no discovery glob reads it).

## Null control

n/a: no behavioural claim made by code; every figure is a read-back from a cited CI job log, the jobs API, or a committed data file, with each figure's command in the document (section 8).

## Red checks

n/a: no branch pushed for CI; the code head `handoff/r9-covfast-scoping-prestudy` (69e374393) is one commit over origin/main `6be88834e` adding only the document.

## Forward-carry

The 17:00Z cache miss (`38069955370`) whose base's push coverage job had succeeded — eviction or save-path failure, unmeasured in this study — belongs to whoever next leans on the coverage reuse chain, before (vi-a) widens it. The `run.sh` "~2-minute arms" comment goes to the (vi-b) fixer.

## Friction

none

## Head

- Code head: `69e374393` on `handoff/r9-covfast-scoping-prestudy` (one commit over origin/main `6be88834e`; adds only the pre-study document).
- Baseline: origin/main = `6be88834e` (2026-10-10).

_Requested by **tvofi**_
