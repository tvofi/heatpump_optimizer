Round-10 closure record (R10-CLOSEOUT-CLEANUP, closure runbook step 9): lands the final round-10 roster on main, retargets every bare citation of a ref the closeout prunes to its `archive/` tag, mirrors the four round-10 state documents into main, and rewrites `dev/programme/HANDOVER.md` to the closure state. `closeout.py`'s `step_in_main` blocks until main holds all four parts. It closes nothing by keyword and leaves #3394 open.

## Summary

- **Roster.** The head merges `handoff/audit-r10-roster` at `00e3c2f8c04066e64182cfa89c0e137ec5eed962` into `origin/main` and takes the branch's blob for `dev/programme/rosters/wave-r10-groups.json` (the merge conflicts in that file). `main_only_roster_delta.py` lists what the blob copy drops from main; its `DROPPED` lines, quoted verbatim (`orchestrator.md` section 6):

``
R10-CATALOG-PR.owner_price_cite: main changed it; result DROPPED  main='owner-stated price, tvofi 2026-11-12: "Price it at 4h"'  result='tvofi 2026-11-12: Price it at 4h'
R10-CATALOG-PR.resume: main changed it; result DROPPED  main="{'stage': 'not-started', 'branch': None, 'commit': None, 'last_step': None, 'next_step': 'after the v10.0.0 closeout stamp: open the hacs/default catalog PR as "  result="{'stage': 'not-started', 'branch': None, 'commit': None, 'last_step': None, 'next_step': 'after the v10.0.0 closeout stamp: open the hacs/default catalog PR as "
``

  Both are wording only on R10-CATALOG-PR (`owner_price_cite` and the `resume.note` set-price suffix); the roster branch carries its own price record.
- **Bare citations.** `closeout.py` step 1 refuses each in-tree citation of a ref in its delete plan that is not prefixed `archive/`. The rewrite is `retarget.py` from the closure runbook directory (session scratch, named in the handover's prototype inventory; a `retarget` arm in `closeout.py` is a round-end proposal), applied to `wave-r10-groups.json` and `wave-r9-groups.json` until a dry pass printed no `cited bare` line. It is a file rewrite in this pull request because `roster_edit.write_roster` refuses it at the triage gate. Review the roster diff with `git diff --word-diff-regex='[^ ]+'`: it should be the `archive/` prefixes plus the branch's own edits.
- **State docs.** `python3 tools/audit/seat/state_docs.py --roster-ref origin/handoff/audit-r10-roster --mirror dev/programme/round10/state` writes `PLAN-TABLE.md`, `FLOW-BOARD.md`, `RESUME-CURRENT.md` and `NEXT-SESSION-PROMPT.md` (`state_docs.DOC_NAMES`).
- **Handover.** `updated-for:` names `6abf88e617ee32844e809b3a3daad82d3d7e7f80`, the merge of #3596, the last gating merge before this pull request; #3599 (R10-HOTFIX-REFERENCE-BASIS), the last gating item, was still in review and CI, and the handover says so. It records the gating set and its merges, the REFERENCE_BASIS defect and its hotfix, the routed non-gating groups with their evidence, the pre-round-11 gate, the soak read, the friction counts by family and the closeout's `--orch-root` trap. Volatile state (the stamp sha, the closeout counts, the catalog pull request) goes on #3394, not here.
- **#201 is unwired from R10-CATALOG-PR in this roster** (orchestrator ruling, logged as OVERNIGHT-DECISION): with the wire, `node tools/policy/brief_lint.mjs` refused `dev/programme/carries/carry-201.json` (`issue 201 already has a live roster group`), and that file stays on main until #3553 deletes it. The orchestrator re-wires #201 on the roster branch after #3553 merges and before closeout pass A. The delta check confirms the wire is absent on both sides: it prints no `issues` line for R10-CATALOG-PR.
- **`tests/layout.json` (code-owned) gains `dev/programme/round10/` in `historical`**, as round 9's closure record did for `dev/programme/round9/` (`git show 205a45208e -- tests/layout.json`, #2086). The generated `PLAN-TABLE.md` quotes roster briefs that cite retired paths (`handoff/round9/`, `tools/audit/briefs/fixer.md`), which `tests/layout.py --guard` refused as `new-reference`; a frozen round's state docs are a historical record, and the placement glob `dev/programme/round10/**` was already there. The handover's one host path was rewritten to `~/hpo-orch/...` for `ref_privacy.py`.

## Head

`5c72ace0402a27780082cc373bced15beff977b9`. Commits on `origin/main` `6abf88e617`: a first build (the roster landed at `5eaef97ee4`, the state docs, the retarget), then, after the #201 unwire, the roster re-landed at `00e3c2f8c0`, the state docs refreshed, the retarget re-applied, the handover, and the layout and privacy repair below. Read the diff three-dot.

## Mutation proof

n/a: record files only (roster, state docs, handover); no production, test or instrument code.

## Null control

Keyed on the `group` field (measured at this head), main's roster holds 508 groups and this head's 544: 36 added by the roster branch since its last landing, 0 removed, so the landing drops no group. 263 of main's groups differ at the head (branch edits plus the `archive/` prefixes); a vacuous keying would print 0 changed. The retarget itself only rewrites citation text: `python3 retarget.py` printed `json parses; dump round-trip identical` for both rosters.

## Figures

- `cited bare` lines before the retarget: `287` (286 in the round-10 roster, 1 in the round-9 roster, measured at roster `1b5c5d1cc4` before step 8's two marks); after the last pass: `0` (`grep -c "cited bare"` over the output of `python3 tools/audit/seat/closeout.py --checkout <head worktree> --main <head> --roster-file <final roster> --repo tvofi/heatpump_optimizer --report-dir <dir> --seats-root /nonexistent --orch-root /nonexistent --verdicts-drained --successor 3394`, dry).
- The same dry run at the head prints `step in-main: ok` and no `brief_lint refuses` line.
- `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)` prints `0 refusal(s)`; `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused`.
- `python3 -I main_only_roster_delta.py` (closure runbook directory) printed the `DROPPED` lines quoted above.
<!-- figure-block: scope-line mb=6abf88e617ee32844e809b3a3daad82d3d7e7f80 head=5c72ace0402a27780082cc373bced15beff977b9 -->
~~~text
MODE: SCOPED -- 3 script(s) run, 30 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
