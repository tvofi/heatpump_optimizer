Fix review: merge cfa9fb9aa6846b8707df45808a9c266f042d8e4d

bus-nonce: d9749e58083eb114c3f17102ad56afdf

Round: 2, third publication on review/2118 (first: `blocked beb97ea69 ...
head-moved`, 1386da31; second: `blocked cfa9fb9aa ... root-cause-unanswered`,
d213eea0). Both blocks are now discharged at this head, and this verdict
carries them.

## What was measured (all at this head or its identical-production parent beb97ea69)

- RESULT typing-ruler (mine, pinned toolchain mypy 2.3.1 / stubs 2026.9.3,
  venv built fresh from --print-requirements): `ALL 9 typing-ruler checks PASSED`
  under `--mypy`; source-only lane `ALL 11 ... PASSED`; independent strict mypy
  over custom_components/heatpump_optimizer: 0 error lines. Census 0. The CI
  `typing` job at beb97ea69: success.
- RESULT arch-score gate (base's copy, base 969c3a5c8): `PASS: dS -0.0028
  WORSENS; every rise explained in the body: coord_footprint 2586->2591`. The
  body's `## Architecture score` carries the gate's own figures (2586 -> 2591)
  with the counting explanation; body and gate agree.
- RESULT mutation: bot pin commit 72cfb1d07 is an ancestor; `--list RETURN_DEL`
  reads coordinator.py:830 and :872 both `pinned ... pass`; the head's CI
  mutation lane at the same production tree (beb97ea69, job 114273437986):
  `MUTATION TABLE PASSED`, 4 mutants over 2 files, 0 survivors, PIN
  RE-VERIFICATION 4 reproduced / 0 not reproduced, no `ADDED UNPINNED` anywhere
  in the log. ci_predict at the head: no closures or fast red predicted.
- RESULT production delta bc0488018..cfa9fb9aa: exactly ONE file,
  custom_components/heatpump_optimizer/coordinator.py, one line
  (`heat_kw: float | None = coord._flow_bias.heat_output_kw`), the field's own
  type; `return heat_kw` no longer returns Any, and the mutated line is
  byte-identical so the bot's RETURN_DEL pin still matches. No second production
  change. VERSION, manifest version and the notes heading untouched.
- RESULT cfa9fb9aa itself: github-actions[bot] 2026-10-10T18:36:27Z, "ci:
  re-record closures", touches ONLY tests/closures.json (+1 line, the
  inert_reads entry). It changes nothing any ruler, gate or pin reads.

## The two blocks, discharged

1. head-moved (beb97ea69 -> cfa9fb9aa): the move was exactly the record-only
   closures re-record; re-measured as the delta above — no production change, no
   new review surface.
2. root-cause-unanswered (`closures` red, `## Red checks` did not name it):
   the red was main's pre-#2125 state (identical INERT READS UNDER-APPROXIMATED
   failure at main tip 969c3a5c8; closures-autofix "changed -- nothing owed to a
   human"), repaired on this branch by the accepted autofix commit cfa9fb9aa and
   on main by #2125 (main tip 6be88834e). The body now names and answers it as
   item 9 under the real `## Red checks` heading, and the head's own checker
   certifies: the latest pr-contract run at cfa9fb9aa (2026-10-10T19:07:28Z)
   completed success. The two earlier pr-contract failures at this head
   (18:36:46Z, 19:05:36Z) are the pre-edit and misplaced-edit runs of the same
   check, superseded by the green one — not unanswered reds.

No check at this head is red. The heavy lanes (closures, mutation, coverage,
fast) were still in flight at publication; they gate the merge train, and their
subjects are unchanged from the green runs cited above (the only diff at this
head over beb97ea69 is the one closures.json line).

## Evidence

/Users/timmalmstrom/hpo-seats/r9rev-2118b/evidence/ — head.txt (names
cfa9fb9aa), typing-ruler-mypy.txt, archscore-gate.txt, mutation-list-returndel.txt,
mutation-lane-log-full.txt, ci-predict.txt, closures-lane-log.txt,
pr-contract-1843-log.txt, pr-contract-1905-log.txt, check-runs-head-final.txt,
check-runs-red-history.txt, pr-body.md. Worktree:
/Users/timmalmstrom/hpo-seats/r9rev-2118b/wt (detached at
beb97ea691f95f20de19f512460ee7ad361c35ba; cfa9fb9aa verified by git show and
ls-remote).
