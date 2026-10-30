Triage batch 67 rules the orchestrator's P298 message of 2026-10-30: the merge train's add-dedupe prints ADDED and then drops the re-added pull request as ALREADY. It is the next rolling batch under V182, after batch 66 (#2982). It holds one ruling, and it changes no roster: there is no held op.
- **P298: ACCEPT as already ruled (P129, P189, P291 on R10-TRAIN-OVERLAP-GRADE).** The fix is #2978, which is merge-verdicted at `882da1e0`, APPROVED and CLEAN.
  - In the live train log, #2976 is ADDED at line 2922 and ALREADY at 2956, #2980 is ADDED at 2903 and ALREADY at 2957, and #2917 is ADDED at 2542 and ALREADY at 2644. In each, `train_add` and the drain disagree.
  - At `882da1e0`, `already_held(pr, verdict, seen, spooled)` is the one rule both call. A skipped entry is re-admitted at a new verdict, or at the same verdict for an environmental skip class (`HOLDER`, `BRANCH_POLICY`). `add` now prints the ALREADY reason, not ADDED.
  - The proposal's key, (PR, head, verdict tip), is narrowed to #2978's (PR, verdict head, skip class). A head key would re-admit a recarried head after every skip and loop.
  - Recorded and not carried: an instrument-defect carry skip (the claim-file class, cured by #2977) stays ALREADY for the rest of the run, and a fresh train re-admits it.
  - Also recorded: #2980's never-ran shape is re-checked after #2978 merges.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`bd13371c8b94263e04ee29a02f37c5c4f4df6b8b`; the file is the whole diff against `aced25893`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P298 as `ACCEPT`. `triage_refusal` passes the citation `triage: dev/programme/triage/s6-batch67.md#P298`: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same citation is refused: `dev/programme/triage/s6-batch67.md#P298 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `grep -nE '^(SKIP|ALREADY|ADDED|ADD REFUSED) #(2980|2976|2917|2872|2961)'` over the live `merge_train/train.log` gives these pairs:
  - #2976: ADDED at 2922, ALREADY at 2956.
  - #2980: ADD REFUSED at 2873, ADDED at 2903, ALREADY at 2957.
  - #2917: ADDED at 2542, ALREADY at 2644.
  - #2917, #2872 and #2961: ALREADY at 2339-2341.
- `git show 882da1e01:tools/audit/seat/merge_train.py` gives `def already_held` at line 885 and `READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)` at line 685.
- `gh pr view 2978` gives `reviewDecision: APPROVED`, `mergeStateStatus: CLEAN` and head `882da1e0`. `verdict/2978` reads `Fix review: merge 882da1e01b3d`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
