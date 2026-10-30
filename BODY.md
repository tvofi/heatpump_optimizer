Triage batch 66 rules the orchestrator's P297 message of 2026-10-30. It concerns a recarried head whose `tests/golden/claimed_drift.txt` is refused as "something other than the union". The class has 4 instances: #2917, #2975, #2955 and #2976. This is the next rolling batch under V182, after batch 65 (#2981). It holds one ruling, and it changes no roster: there is no held op.
- **P297: ACCEPT as already ruled (P290, `s6-batch62.md`).** The fix is R10-FLY-CARRY-CLAIM-DRIVER's #2977. It is approved and in the live train, at head `967abc3e`, a clean main merge of its verdicted head `9f0e4478`.
  - Measured: `app_approve.sh --carry <verdict> <merge> origin/main` was run on the refused merges of #2975 (`2c162670`), #2955 (`502b0df3`) and #2976 (`ebbdcaa6`).
  - Each gives rc 1 from origin/main `1148ee635` and rc 0 from #2977's head `967abc3e`. So P290's driver-versus-union mechanism is the cause of all four instances, and not inherited claims or the stamp's emptied list.
  - (b), re-running claims-autofix before the carry, is rejected: it rewrites a verdicted head.
  - (c), an RCA seat, is not owed: the cause is measured.
  - The barrier this audit class owes is #2977, and its merge is the lever. After it merges, the three PRs re-carry on the train's next add.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`8a908a975121c202c21a3cc223c09ec85ddc0387`; the file is the whole diff against `1148ee635`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P297 as `ACCEPT`. `triage_refusal` passes a citation `triage: dev/programme/triage/s6-batch66.md#P297`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same citation is refused: `dev/programme/triage/s6-batch66.md#P297 is not an ACCEPT ruling (REJECT)`.

## Null control

- In the carry re-run, the same three merges under origin/main's `app_approve.sh` refuse (rc 1). So the pass at `967abc3e` is the change's, not the merges'.

## Figures

- `grep -nE '^(SKIP|ADD REFUSED) #[0-9]+ carry:.*claimed_drift'` over the live `merge_train/train.log` gives 9 lines: #2917 six times, and #2975 (line 2582), #2955 (2799) and #2976 (2885) once each. Line 1984 is an `ADD REFUSED #2917` of the same refusal, with its text cut short before the file name.
- The carry re-run gives rc 1 from `1148ee635` and rc 0 from `967abc3e` for each of the three.
- `gh pr view 2977` gives `reviewDecision: APPROVED`, `mergeStateStatus: BLOCKED` and head `967abc3e`. The train log's last lines read `beat: waiting CI at 967abc3e`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
