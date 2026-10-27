Fix review: merge 9513b571420de2740607e12847adcf047ec94b1b
bus-nonce: dff024021523043219dc7c9688714fb9

# Fix review -- PR #2876, R10-HOUSE-GRADE, round 4

Reviewed head: 9513b571420de2740607e12847adcf047ec94b1b (GitHub's `headRefOid`
matched it when the review began; re-checked before publishing). Worktree: a
detached worktree at the head under `~/hpo-seats/r10s6/review-2876-r4/wt-head`;
the reviewed head at `wt-prev`; the merge base at `wt-base`; the harness's own
baseline `3b4180dcc` at `wt-hgbase`. I did not run the fixer's worktree, push
the branch, or edit the main checkout.

This is the fourth round. All three verdicts on `verdict/2876` reviewed the same
head, `253dc4867cf39f2aa9875f5f2540c5b67b7c1018`, and the same fix (the house
grade rewritten against the configured type and era, its drivers published, the
card explaining them). `app_approve.sh --carry` refuses
`253dc4867 -> 9513b5714` because `b71541154` merges `e0237e6d0`, a branch
commit not on `origin/main`; the delta below is why a fresh review was owed.

## The delta between the reviewed head and this one

`git log --first-parent --oneline 253dc4867..9513b5714` names three commits and
no non-merge commit:

| commit | what it is | branch's own or main's |
|---|---|---|
| `9513b5714` | merge of `d08647f05` and `origin/main` `e40806a7d`; a clean automatic merge, its tree equal to this head's | branch's own merge-forward |
| `d08647f05` | merge of `b71541154` and `origin/main` `2b45d098c` (PR #2881); clean automatic merge | branch's own merge-forward |
| `b71541154` | `--no-ff` re-merge of `e0237e6d0`, a descendant of its first parent; its tree is byte-identical to `e0237e6d0`'s, so it adds no content | branch's own merge commit |

`e0237e6d0` is not a third-party branch: its parents are the reviewed head
`253dc4867` and `origin/main` `67178dc6a` (PR #2880), so it is the branch's own
`git merge origin/main`, cut in a detached worktree at `253dc4867` (the
`fix-2876-claim` worktree still sits at it). `67178dc6a`, `2b45d098c` and
`e40806a7d` are all ancestors of `origin/main`; none of the three delta commits
is. Merging it was legitimate in content; the `--no-ff` shape is what the carry
predicate refuses, which is a process cost, not a content change.

The end-to-end proof that the delta is only main's movement: the head's tree is
`d234588b0ebf2b4ebead50ea4fa97773a3e50cbf`, exactly what
`git merge-tree --write-tree 253dc4867 e40806a7d` writes. Byte-for-byte, the
branch-owned files are unchanged from the reviewed head: `presets.py`,
`coordinator.py`, `config_flow.py`, the card JS, both harnesses, `tests/entities.py`
and `tests/golden/card_claimed_drift.txt` all have the same blob ids at both
heads. The one production file that differs in the delta, `payload.py`, gains
only main's `SavingsMonth.meter_calibration` (PR #2492 via #2745); the branch's
`Scores.envelope_drivers` is still there. Nothing in the delta weakens or
reverts the reviewed fix, and the head's `#2816` checks (14 occurrences in
`tests/features.py`) and the card's `envelopeDrivers` block are present.

## Results

The reviewed fix's own evidence still holds at this head, re-measured with the
finder's harness rather than the fixer's. At `3b4180dcc` and at the merge base
`e40806a7d` the copied head harness reads `era_spread=67.7`, `owner_min=20.3`,
`owner_max=44.3`, `monotone=False`, `curve_min=0.0`, `drivers_max_gap=None`; at
this head it reads `era_spread=0.0`, `owner_min=35.2`, `owner_max=35.2`,
`monotone=True`, `curve_min=4.23`, `drivers_max_gap=0.0`, and under its own
`--era-blind` perturbation `era_spread=50.5`, `owner_min=16.8`, `curve_min=1.61`.
Both the head and the perturbation therefore move, and the base is the null's
failure, exactly as the body states.

`r10_scores_envelope` reads `split_max_abs_gap=0.0` at the head and `0.0` under
`--ratio-override 1.0`; all 40 `band` rows read `tree_grade=50.0` at the head,
against a 21.8..99.9 span at the base. `python3 tests/plan_view.py` then
`node tests/card_drift.mjs` reads `1 state(s) moved and claimed, 44 identical`.
`python3 tests/structure.py` reads `STRUCTURE RATCHET PASSED`, with no budget in
the three-dot diff. `python3 tests/env_drift.py --all origin/main` exits 0 with
`NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and
`NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.

The claim-file resolution is correct and measured: the head's
`tests/golden/claimed_drift.txt` is 772 lines; the merge stages are 750 (base
`524c1896b`), 770 (ours) and 752 (theirs); both sides' edits against the base are
additions only (`20/0` and `2/0` in `--numstat`); the head's claim multiset
equals base + both additions; `env_drift.merge_claim_defect` returns `None`
(`DEFECT: none`); `--claims-only origin/main` prints `claims hygiene: origin/main
ok`; and `excusing_claims` at this head names exactly the five `coord_*` claims
as branch-authored and filters `config_flow`, `negative_prices` and
`summer_dhw_only`. Both claim files stamp `claims-for: 7.0.4`, equal to
`VERSION` 7.0.4; `VERSION`, the manifest version and the release-notes heading
are untouched in the delta.

The gate at this head: `gh pr view 2876 --json statusCheckRollup` returns three
`gate` rows, each `"status": "COMPLETED", "conclusion": "SUCCESS"` (19:16:22Z,
19:17:19Z, 19:19:46Z). The commit check-runs API for the head returns 68 runs,
all at `head_sha=9513b571420de2740607e12847adcf047ec94b1b`: 43 success, 25
skipped, 0 failure, 0 cancelled; `gate` ids 122412872175, 122413376158 and
122414671515 are all success at that SHA.

The forward-carry is in the tree: `a4a348a6dc67e30ef6644ab73b5da60d4f45f4da`
adds the driver-interface carry to R10-COP-GATE's `carry` list in
`dev/programme/rosters/wave-r10-groups.json`, states its controls as a
precondition (240 null-control cells grade mid-scale, `tree_grade=50.0` for every
preset house, and `era_spread 0.0 -> 50.5` under `--era-blind`) and a
re-measurement command, and is an ancestor of this head.

The body's `## Head` names this head; the template's seven headings are all
present (`## Head`, `## Mutation proof`, `## Null control`, `## Figures`,
`## Red checks`, `## Forward-carry`, `## Friction`), in order, plus
`## Unpinned sites`; `pr-contract` is green at the head.

## Findings

### F1 -- the base end is labelled "the merge base `3b4180dcc`", which is not this head's merge base (non-blocking; correct the body)

Claim: `## Figures` says "At the merge base `3b4180dcc`". Evidence: at this head
`git merge-base origin/main 9513b5714` is `e40806a7d8b024e7090182ea6d1906f45ddf89e2`;
`3b4180dcc` is the branch's earlier fork point, two main merges back. Harness:
the same head harness run in a `3b4180dcc` worktree and in an `e40806a7d`
worktree. Metric: the six `RESULT` lines; both ends print identical values
(67.7/20.3/44.3/False/0.0/None), so no figure changes, only its label. The
qualitative claim stands at both bases.
Carry: R10-HOUSE-GRADE (item for the next body re-take)

### F2 -- the roster's `files` still under-specifies the seam (non-blocking; the round-3 F2, still open)

Claim: two production files move outside the group's roster `files`. Evidence:
`git diff --name-status 253dc4867..9513b5714` has no `config_flow.py` or
`payload.py` change at this head because those moves are in the reviewed code
head, but the roster entry for R10-HOUSE-GRADE at this head still lists only
`coordinator.py`, `presets.py` and the card JS, while the three-dot diff carries
`config_flow.py` and `payload.py`. The body discloses both. Harness: the roster
entry in `dev/programme/rosters/wave-r10-groups.json` against the three-dot
diff. Metric: two production files touched and not listed. Record them at the
next roster edit, as the round-3 verdict asked.
Carry: R10-HOUSE-GRADE (item 966df279)

### F3 -- a real `gate` failure at the intermediate merged head `d08647f05` is not named in the body (non-blocking observation)

Claim: the body's `## Red checks` names the earlier gate reds but not this one.
Evidence: gate check-run `122390400672` at `d08647f05` concluded `failure` at
18:37:55Z, its log reading `FAIL tests / fast (3.14): cancelled (run
40557884581)`, three more `cancelled`, and `pr-contract: no run at this head
judged base 'main'` -- the 19:16 push superseded the 18:35 runs, so the gate
could not judge rather than finding a defect. Harness: the commit's check-runs
API and the job log. Metric: the head's three `gate` runs are all success, and
`pr-contract / pr-contract` ran at 19:15:25Z and 19:18:52Z (both after the last
red concluded) and went green; no cheaper detector exists, because the red is a
cancellation, not a code failure. Record it in the body at the next re-take; it
does not block a head whose gate and body check are green.
Carry: R10-HOUSE-GRADE (item for the next body re-take)

### F4 -- `origin/main` has advanced past the merged base (observation for the orchestrator)

Claim: the head merges `e40806a7d`; `origin/main` is now
`a0e7664ea6485b9ad8f68d164cd255ec4fd51fb9`. Evidence:
`git merge-tree --write-tree origin/main 9513b5714` exits 0 with tree
`783c0a858...`, so the next merge-forward is automatic and conflicts nowhere.
Harness: `git merge-tree` and `git diff --stat e40806a7d..origin/main`, which
touches no scenario, fixture or solver path (governance, tooling, delivery rows,
triage only). Metric: the head's merged base vs current main. The delta that
merge produces is the orchestrator's to judge under the carry predicate.
Carry: R10-HOUSE-GRADE (orchestrator)

### F5 -- the round-4 body carries no `## Re-cut` note (non-blocking; process record)

Claim: `fixer.md`'s "Past three rounds, re-cut rather than repair" asks for a
`## Re-cut` note at the fourth round, and this body has none. Evidence: the
body's headings are the template's seven plus `## Unpinned sites`. The body is
otherwise a full re-take at this head -- every figure under `## Figures` was
re-measured in this pass -- and the authored content is byte-identical to the
round-3 head; the only movement is main's two merge-forwards. Recorded so the
next round's dispatch can require the heading; it is not a code defect.
Carry: R10-HOUSE-GRADE (item for the next body re-take)

## What I could not establish

I did not re-run the 60-minute `tests / mutation` job or the mutants: the
branch's production lines are byte-identical to the reviewed head where round 3
re-ran M1/M4 and the four `killed_by` rows were recorded, and the head's
`tests / mutation` job is green with `3814 unpinned site(s) ... 3814 at the
ratchet base e40806a7d` and `MUTATION TABLE PASSED`, so the table reads the
base's count with 0 added.

I did not locally re-run `tests/features.py` (655 s) or
`tests/config_flow_steps.py`; the head's `tests / fast (3.14)` is green and its
own log prints `ALL 4476 FEATURE CHECKS PASSED` and `ALL 502 checks PASSED`. The
body quotes neither count; the 502 appears only as the earlier red's "2 of 502".

The captured `env_drift --all` output retained only its summary tail, so I quote
`NO UNCLAIMED DRIFT: 56` and `NO STALE FIXTURE: 56` and the separately measured
claim map and `excusing_claims`, not the per-fixture `CLAIMED` strings.

Verdict: merge 9513b571420de2740607e12847adcf047ec94b1b. The reviewed fix is
present and unweakened; the delta is main's movement plus one no-op re-merge, the
head's gate and `pr-contract` are green, and F1-F3 and F5 are body records for
the next re-take, not reasons to hold the code.
