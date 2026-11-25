Round-11 roster record: puts the round-11 roster branch tip on main, so that the carry file `dev/programme/carries/carry-3881.json` is on `origin/main`. It closes nothing by keyword and leaves #3881, #3879 and #3394 open.

## Summary

The change is roster state plus one line in `tests/closures.json`. That line lists `carry-3881.json` in `tests/entities.py`'s closure beside `carry-1645.json` and `carry-3885.json`, because the predictor refuses an unclassified file. It was added by hand, as #3889 did, so `closures-autofix` may re-record it.

Roster files:
- `dev/programme/carries/carry-3881.json` (new). It is byte-identical to the copy at `34cefdc5`.
- `dev/programme/rosters/wave-r11-groups.json` (the roster branch's group state since #3889).

No production, test or instrument code is touched.

The roster branch tip that lands is `f520ce0365639f88b6074721a36683c6d6a798ea` (`handoff/audit-r11-roster`). It is merged with `--no-ff` into `origin/main` `b4a8bbd567`. Before that commit, the roster tip `079ac8dd` was merged with `origin/main` `b4a8bbd5`. The merge was clean, and `carry-3885.json` there is main's copy.

Why now: #3879 (R11-SEAM-two-zone-slab) routes one carry to `carry-3881.json`. `bus.sh dispatch`, `review_packet.py`, the train pre-flight and `app_push.sh`'s prepr all run `carry_audit.py` against `origin/main`. Until the file is on main, #3879's update is refused with `BAD-DEST` (orchestrator.md section 10: a carry a PR names needs it).

## Head

`329fa4ebb5a129448831b670487dc7603e8a516b` is `handoff/r11-roster-land-3881`. It is the merge (`830eb8a10dd6`) of `f520ce0365639f88b6074721a36683c6d6a798ea` into `origin/main` `b4a8bbd567`, plus the closures line. `node tools/policy/brief_lint.mjs` at the roster tip with `carry-3881.json` prints `TOTAL: 0 error(s) across 42 file(s)` and exits 0. `python3 tools/pr/ci_predict.py --only under-scoped` prints `no closures, fast, governance or instrument red predicted against b4a8bbd567b1`.

## Mutation proof

n/a: records only; no production, test or instrument code behaviour changes.

## Null control

`python3 -I tools/audit/carry_audit.py check --body <#3879 body>` was run at both trees:
- At `origin/main` `b4a8bbd567` it prints `BAD-DEST body item 8b887fdc: #3881: #3881 has no owner: no live roster group lists it and there is no dev/programme/carries/carry-3881.json`, ending `4 finding item(s): 3 routed, 0 unrouted, 1 bad destination(s)`.
- At this head it prints `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`.

## Figures

none

## Red checks

none at the time of opening. `tests / nightly-status` grades `main`, not this diff. It is outside the required set that `merge_train.py owed-reds` prints, and the diff does not touch its reporter inputs.

## Forward-carry

none

## Friction

carry-audit: unenforced: the instruments read carry files at `origin/main` or the roster ref, so a carry file a PR adds is unreceivable until a roster landing (P-R11-CARRY-LINE-OWN-FILE), the same friction #3889 recorded. Carry: dismissed: proposal P-R11-CARRY-LINE-OWN-FILE in the orchestrator's round-end triage
