Fix review: blocked beb97ea691f95f20de19f512460ee7ad361c35ba head-moved: measured beb97ea691f95f20de19f512460ee7ad361c35ba, head is cfa9fb9aa6846b8707df45808a9c266f042d8e4d (one commit, "ci: re-record closures", tests/closures.json +1 line)

bus-nonce: 688b00962bc87f658848cf3d6f50cb7d

Round: 2 (delta review of the repair round; round 1 measured the substance at
bc0488018, which this review does not re-open).

## What was verified at beb97ea691f95f20de19f512460ee7ad361c35ba (all survive as numbers; none carry a merge verdict to a moved head)

- RESULT typing-ruler (mine, pinned toolchain): `ALL 9 typing-ruler checks PASSED`
  under `--mypy` with mypy 2.3.1 / homeassistant-stubs 2026.9.3 (venv built fresh
  from `--print-requirements`); source-only lane `ALL 11 ... PASSED`. Independent
  `mypy --strict` over custom_components/heatpump_optimizer: 0 error lines, so the
  census is 0, not merely "did not grow".
- RESULT arch-score gate (base's copy, base 969c3a5c8): `PASS: dS -0.0028 WORSENS;
  every rise explained in the body: coord_footprint 2586->2591`. The body's
  `## Architecture score` says 2586 -> 2591 and explains it — body and gate agree.
  (The dispatch prompt's "2590 -> 2591" was the prompt's summary, not the body's
  figure; the body carries the gate's real numbers.)
- RESULT mutation: bot pin commit 72cfb1d07 IS an ancestor of the measured head;
  `mutation_table.py --list RETURN_DEL` at the head reads both
  `coordinator.py:830` and `:872` as `pinned ... pass`. The head's own CI mutation
  lane (job 114273437986, green): `MUTATION TABLE PASSED`, 4 mutants over 2 files,
  0 survivors, PIN RE-VERIFICATION 4 reproduced / 0 not reproduced (830 RETURN_DEL
  killed by tests/features.py), and no `ADDED UNPINNED` line anywhere in the log.
  `ci_predict.py --base 969c3a5c8`: "no closures or fast red predicted" (before the
  closures red below materialised — the predictor does not read inert_reads).
- RESULT production delta bc0488018..beb97ea69: exactly ONE file,
  custom_components/heatpump_optimizer/coordinator.py, one line:
  `heat_kw: float | None = coord._flow_bias.heat_output_kw`. No second production
  change. VERSION / manifest / RELEASE_NOTES heading untouched in the delta.
- RESULT typing CI job at the head: success.

## Why blocked, in order of what happened

1. At the measured head, `closures` went red (18:36Z): `INERT READS
   UNDER-APPROXIMATED: tests/harness_headers.py:
   dev/audit/rounds/round9/prestudy/boost_drift_refit.py`. Main tip 969c3a5c8
   carries the IDENTICAL failure (its own push, 17:22Z), and closures-autofix at
   the head printed `closures-autofix: changed -- nothing owed to a human` — so
   the red is main's (#2109's prestudy file), not this branch's diff. It is,
   however, a red at this head that `## Red checks` does not name, and pr-contract
   said so: the 18:43Z run FAILED with `check 'closures' is red and '## Red
   checks' does not name it` (red-history: closures, mutation, typing — the body
   names mutation and typing, not closures).
2. While this review ran, the branch moved: `fix/r9-ux-10-v2` is now
   cfa9fb9aa6846b8707df45808a9c266f042d8e4d, exactly one commit, `ci: re-record
   closures`, +1 line in tests/closures.json — the re-record that answers (1).
   The handoff made beb97ea69 mine; a head that moves under the review is a
   broken rule, not an accident, and a merge verdict cannot attach to a head that
   no longer exists.

The move is the closure re-record, a data file, no production code: the delta
from beb97ea69 to cfa9fb9aa is one line in tests/closures.json. Re-measuring that
delta is offered to the orchestrator, never owed by this verdict.

## Evidence

/Users/timmalmstrom/hpo-seats/r9rev-2118b/evidence/ — typing-ruler-mypy.txt,
archscore-gate.txt, mutation-list-returndel.txt, ci-predict.txt,
mutation-lane-log-full.txt, closures-lane-log.txt, pr-contract-1843-log.txt,
check-runs-head-final.txt, check-runs-red-history.txt, pr-body.md, head.txt.
Worktree: /Users/timmalmstrom/hpo-seats/r9rev-2118b/wt (detached at
beb97ea691f95f20de19f512460ee7ad361c35ba).
