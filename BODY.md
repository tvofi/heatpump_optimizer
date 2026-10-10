# R9-RC-POSTREVIEW-MERGE — class RCA (root-cause seat, issue #2096)

Group **R9-RC-POSTREVIEW-MERGE**. This handoff carries the analysis document and
the class entry only: no production, workflow or policy file is changed, no
pull request is opened, no countermeasure is landed. `dev/governance/roles/root-cause.md`
and `dev/governance/rules/defect-root-cause.md` are the contract; every part is
in `dev/audit/rca/R9-RC-POSTREVIEW-MERGE.md`.

## Head

`0cb14166117fc00acdd60f10f11a6edf24b9bf2a` — one commit on `origin/main`, two
files: `dev/audit/rca/R9-RC-POSTREVIEW-MERGE.md` (new) and
`dev/audit/config/bugclasses.json` (class `N-postreview-merge-red` + its `_rca`
entry, one commit with the document: `fold_ledger.py check` refuses either half
alone, and it passes at this head — 29 classes, 0 violations).

## Findings

**Named cause.** The independence premise of the recarry skip: a head's green or
clean status is established against a main that has moved by publish time, and
the merge with the live main is graded first by CI, minutes later, after the
review, inside the batch pass. `app_push.sh --recarry` (#2069) judges text and
identity — two parents, tree equals `merge-tree`, live body — never the
interaction of the head's delta with main's.

**Process state. (c)** — followed, and did not produce the intended result. The
verdict ran exactly as written; the head it published was red on a check whose
local arm costs 0.055 s. Not (a): the detector existed, locally, in the very
script the flag skips (`prepr.sh` step 3h runs `--self-test` whenever
`selftest_owed` holds — and #2072's carry names `tools/pr/prepr.sh`, so it was
owed). Not (b), not (d): argued in the document, section 3.

**Instance (1) reproduced.** At the merge base `bd59a4af1` two `printf | grep -q`
arms existed; #2072's branch added a third (`moved_line`) while main (#2067,
`09d2061b2`) converted the two inherited arms to `case` and shipped
`pipe_grep_q_sites` scanning `tools/pr/prepr.sh`. The clean text merge leaves
exactly one site — the branch's own new arm — and main's new detector finds it:
`pipe_grep_q_sites` rc 1 at `04d10721b` (0.055 s), rc 0 at main `23d354970`
(null control), at the fixed head `00e31e8a3`, and at live main; `prepr.sh
--self-test` at `04d10721b` in a scratch worktree: rc 2, 122 s, `243 passed, 1
failed`, the same FAIL row CI's `instrument-self-tests` printed (job
11404006359). #2066 reproduced likewise: `merge-tree` 0 conflicts against
`d0f085ffb`, 27–30 conflicting files against the main of publish time.

**Cost test (measured).** Census via the check-runs API: **76 recarry heads in
2026-10-08..10-10, 15 reddened by the merge** (green at the reviewed parent) —
19.7 %, ~5/day; #2072 cost 9 h 42 m red-to-fix-head, 14 h 24 m red-to-merge,
plus the batch pass. Against ~2.5 h/day of rework: the recommended
countermeasure stands at ~34 min/day.

**Countermeasure — proposed, not landed.** The skip's unit changes: a carry
skips the local grade only when it owes none, and "owes" is `prepr.sh`'s own
`selftest_owed` over the carry's three-dot diff (no second list). When owed,
`prepr.sh --self-test` runs on the merged tree before the push; its refusal
stops the train at step 1, as a conflict already does. Priced: 122 s × 50/76
recarries (66 %) ≈ 34 min/day. Demonstrated failing on the defect and passing
once fixed (both runs above). The files-shared-with-main probe is recorded
**insufficient** (0.088 s, 47 % sensitivity). Whole-prepr rejected (pays what
#2069 removed); unconditional self-test dominated by the owed-gated one (the 5
reds on carries owing no self-test name no check it grades). **Budget-raise
sub-shape (4 of 15) propagates to the carry lane's brief** — the raise is
main's; no local predicate measured sees it.

## Figures

All enumerators are section `## Figures` (F1–F7) of the document at this head.
headline numbers: 76 recarry heads; 15 merge-reddened; 122 s self-test; 0.055 s
class arm; 50/76 owe the self-test; 43/76 share a file with main's delta (7/15
of the reds); #2072 timeline 21:47:51Z red → 07:29:47Z fix head → 12:11:35Z
merged.

## Red checks

none — this branch changes two inert files (`closure.py select`: MODE SCOPED, 0
scripts run); `tests/structure.py` passed; `fold_ledger.py check` passed.

## Forward-carry

`dev/audit/rca/R9-RC-POSTREVIEW-MERGE.md` section 7 carries the two exact
propagation sentences (the countermeasure PR's fixer brief; the carry lane's
budget-raise sentence) and names what issue #2096's Root cause section owes.

## Mutation proof

none owed — no production or check code is changed; the document's claims are
API figures and command runs, each with its enumerator.

## Null control

`pipe_grep_q_sites` rc 0 on main `23d354970` (0.057 s), on the fixed head
`00e31e8a3` (0.040 s) and on live `origin/main` (0.037 s): the detector the
countermeasure would run is green on healthy trees, and its planted-site arm is
pinned in CI already.

## Friction

none.
