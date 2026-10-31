Fix review: blocked 73b1b404879bde41f2a741ccf3a7f9feb2b34fde carry-missing: carry-2733.json is a second destination for #2733 -- R10-ORCH-ROSTER-SCHEMA is live (carries-open, 728e1d80c) and lists 2733, so brief_lint refuses the file under the roster index and accepts it only through the blind no-argument arm (A1) this record carries

bus-nonce: 11723a5f71ff3958cd243df9847104a8

## Scope

This is fix review of #2896 (R10-RCA-FRICTION-RESIDUE), dispatched as round 2, at head `73b1b404879bde41f2a741ccf3a7f9feb2b34fde`. The merge base is `f844df1fe750d5e420af0d1555f4b9472a740413`, which is also origin/main. The roster is `handoff/audit-r10-roster` at `c3f563fdc6e5`. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. The named worktree did not exist, so I re-created it detached at the head. I re-read the head with `git ls-remote` before writing, and it is unchanged.

The three-dot diff touches seven files. Two are new since the round-1 head: `dev/programme/carries/carry-2733.json` and its `tests/closures.json` entry. There is no production line, so step 1 has no mutant. `VERSION`, the manifest version, the notes heading and the claim files are untouched. `git merge-tree --write-tree origin/main HEAD` gives rc=0. I cited CI's heavy runs and did not re-run them.

## Findings

- **Blocking: carry-missing (two destinations for #2733).** `finding-propagation.md` sends a carry to `carry-<N>.json` only when "the stage has no live roster group". It also says brief_lint "refuses a carry at an issue a live group covers, so no stage has two destinations". `brief_lint.mjs` states the reopen case directly: "a stage reopened as a group closes the carry file again". On the roster tip, `728e1d80c` moved R10-ORCH-ROSTER-SCHEMA from `done` to `carries-open`. That stage is live, because brief_lint skips only `done`, and the group lists 2733. R10-ROUTING-INVARIANTS (`absorbed`) also lists 2733 and is also indexed as live. I called `checkCarryShape()` on the head's `carry-2733.json` (`ev/carry_index.txt`):
  - With the no-argument index (size 1) it is accepted with 0 errors. This is the blind arm that record section 3 measures and A1 repairs.
  - With the roster tip's `dev/programme/rosters` it is refused: `issue 2733 already has a live roster group (wave-r10-groups.json R10-ORCH-ROSTER-SCHEMA)`. At origin/main and before the reopen it is refused against R10-ROUTING-INVARIANTS.
  - Null control: the same file with `issue: 999999` gets 0 errors under every index, so the refusal is specific to 2733.

  So the head passes `tests / briefs` only because of the defect it documents. R10-FLOW-TOOLKIT-MODEL carry 14 (A1) has as its acceptance "the no-argument call indexes the roster's issues". When that lands, this file turns brief_lint red on main. The file's own `_comment` ("#2733's only roster groups ... are done or absorbed, so no live group's brief can hold them") is false at the roster tip. The body's A1 line ("#2733 has no live group") is false too.

  The roster carry `2a0a854e6` (R10-ORCH-ROSTER-SCHEMA carry 24) does not duplicate the #2875 text. It only points at "carry-2733.json's two items" as first instances. So no item's text is routed twice, but the stage has two destinations, and its live brief holds a pointer instead of the items' controls.

  Repair:
  1. The orchestrator appends both items to R10-ORCH-ROSTER-SCHEMA, using the carry file's `control`, `remeasure` and `brief` text. These are: #2875 is listed by no group, with null #2860; and #2855 is listed only by this group, with null #2733.
  2. The fixer deletes `carry-2733.json` and its `tests/closures.json` entry.
  3. The body's two `Carry: #2733` items name `Carry: R10-ORCH-ROSTER-SCHEMA`, or stay `#2733`, which then resolves through the live group. The A1 line drops "#2733 has no live group".

  Carry: R10-RCA-FRICTION-RESIDUE
- Non-blocking: the second carry item's mechanism also strands four sibling issues. That item is #2855: when this group goes `done`, an open issue is listed only by a done group. On the roster tip, #2429, #2436, #2437 and #2438 are also listed only by R10-RCA-FRICTION-RESIDUE, and all four are open. The body routes `Carry: #2429`, `#2436`, `#2437` and `#2438` to them, and that resolves only while this group is live. At the merge's set-stage done, all four strand exactly as #2855 does. Name all five in the same item. Carry: R10-ORCH-ROSTER-SCHEMA
- Non-blocking: the `rounds.py` friction row routes `Carry: R10-ROUND-PLAYBOOK`, but that group's seven carries hold no text about it. This is case 3 of record section 3. A2's fold, or an append-carry, should land it. Carry: R10-ROUND-PLAYBOOK

## Verified

- **`Closes`:** I reproduced `pr-contract`'s jq derivation byte for byte, on origin/main's rosters and on the roster tip. Both give `INTENDED=2410 2593 2597 2660 2784`. `preflight.sh` prints `ok closes #N -- intended` for all five (`ev/pr-contract-closes-derivation.txt`). The five match the record's section 6 and section 10 dispositions:
  - #2410: held.
  - #2593: folded into section 4.
  - #2597: refusal recorded.
  - #2660: held, 7/8 → 1/1.
  - #2784: refusal stands.

  #2410 and #2593 are already CLOSED, which is harmless.
- **`carry_audit check --body`:** `CARRY-AUDIT: 17 finding item(s): 17 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (`ev/carry_audit.txt`). It accepts `#2733` through either the carry file or the live group, so it does not see the double destination.
- **brief_lint no-argument:** rc=0 (`ev/brief_lint-noarg.txt`).
- **Re-derived:** `rosterIssues()` is 1 at the head. With rosters it is 72 at origin/main and 69 at the roster tip. The record's 76 is its own base's figure, and the record labels it as such.
- **Red checks (step 11):** this is not judged. At read time no check-run on the head was red. `prelude`, `instrument-self-tests`, `closures`, `coverage` and `fast (3.14)` were still in progress, and no `gate` or `pr-contract` run existed yet (`ev/check-runs.txt`). The body's `prelude` answer refers to an earlier head.

RESULT carry-2733 brief_lint(no-arg)=accepted brief_lint(rosters@c3f563fdc)=refused:R10-ORCH-ROSTER-SCHEMA brief_lint(rosters@f844df1fe)=refused:R10-ROUTING-INVARIANTS control-999999=accepted(all)
RESULT closes intended=2410,2593,2597,2660,2784 refused=0
RESULT carry_audit routed=17/17
RESULT head 73b1b404879bde41f2a741ccf3a7f9feb2b34fde unchanged at write
