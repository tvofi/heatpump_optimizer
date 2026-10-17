Fix review: merge 8920402b8d9be3ced09f7026c5f3f088f1973ced

Reviewer: adversarial review seat for PR #1889, dispatched per fix-review.md from a
detached worktree at the head SHA. Evidence dir: /Users/timmalmstrom/hpo-seats/review-1889/
(worktree `wt/`, throwaway clone `throwaway/` + `fakeorigin.git/` for the wt_sync.sh live
test). Measured head: 8920402b8d9be3ced09f7026c5f3f088f1973ced; live head re-checked at
posting — unchanged. Merge base 4efc5b63e = origin/main tip.

## 1. Diff scope

`git diff 4efc5b63e...8920402b8` touches exactly the four named surfaces:
docs/HANDOVER.md (round-9 section rewrite only), tools/audit/seat/wt_sync.sh (new, 37 lines),
docs/delivery/1888.md, docs/delivery/1889.md. No VERSION, no *_budgets.json, no claim files,
no production code.

## 2. HANDOVER

- `updated-for: 4bcfcf203...` verified an ancestor of HEAD (`git merge-base --is-ancestor`: OK).
- entities.py UNVERIFIED-RAN-CI: no homeassistant module in ~/.local/state/hpo/venv-ci on this
  Mac. CI's entities lane at this head is `wave-script` (governance.yml runs tests/entities.py
  there, restored from the base commit): **success**. record/delivery-status (the other entities
  runners) skipped at head; no red lane at any branch head except nightly-status (below).
- Null control reproduced: `git show origin/handoff/audit-r9-plan:handoff/round9/RESUME-CURRENT.md`
  fails; the path the section now names, `handoff/round9/state/RESUME-CURRENT.md`, resolves
  (ls-tree checked) — matches #201 comment 5977838979's resume instruction.
- All four named seat scripts (merge_train.py, remerge_main.sh, handoff_push.sh, seat_venv.sh)
  exist in tools/audit/seat/ at head (#1879, merged 0ea7c92b per #201).
- The section's other figure — `merge_fastpath.py` printed `FASTPATH ELIGIBLE` for #1888 —
  reproduced locally: `python3 tools/audit/merge_fastpath.py --head 7fd56c493 --main f4e8d911b`
  prints `FASTPATH ELIGIBLE`.
- The dispatch's suggested spot-checks (v6.7.15 tag/site, hpo-ledger bypass removal,
  R9-UX-8/R9-SW-5 folds) appear nowhere in the changed section or the diff, so no claim to
  mismatch; the pre-existing hpo-ledger owed-work text is untouched.

## 3. wt_sync.sh — live test on a throwaway clone against a fake origin

- Dirty worktree (untracked scratch.txt): snapshot pushed, `synced hpo-seats-review-1889-wta
  43c8a832`; `git show origin/wip-sync/<slug>:scratch.txt` returns its content; snapshot
  commit's parent is the worktree's HEAD.
- Negative control: clean worktree with HEAD on a remote branch — **skipped**, no snapshot.
- Worktree untouched: index md5 identical before/after; scratch.txt still present, still
  untracked (snapshot uses a temp GIT_INDEX_FILE).
- `--scratch <dir>` snapshots to `wip-sync/orchestrator-scratch` with `orch/` prefix, content
  verified.
- Note, not a block: `set -uo pipefail` without `-e` means a failed push exits 0 with no
  "synced" line — the loop's caller detects a missed snapshot only by that line's absence.

## 4. Delivery rows

- #1888: gh truth = MERGED at 4efc5b63e, title "record: Delivery-status rows for #1882-#1884" —
  row matches SHA and title. #1889: OPEN — row says "open". Title of the PR names only the
  #1888 row; cosmetic staleness, pr-contract green.
- `python3 tests/delivery_status.py --check`: `DELIVERY STATUS OK — 8 rowed, 0 pending,
  0 overdue`.

## 5. CI at head (check-runs API)

Only completed red: nightly-status (main's scheduled 2026-10-03 run, mutation-ledger;
#1878 merged fixes it) — named and answered in ## Red checks; this diff reaches nothing it
grades. coverage in_progress (not red). Everything else green or skipped.

## 6. Body contract

First line `_Requested by **tvofi**_`; headings match the template plus `## Approval`
(policy surface, POLICY_GLOBS includes docs/HANDOVER.md); figures re-derived
(policy_lint TOTAL: 0 errors / 40 files; structure STRUCTURE RATCHET PASSED; is_inert(wt_sync.sh)
True); Friction `none`; preflight.sh on body+title: rc=0, no closing-keyword refusal;
merge-tree vs origin/main: clean.
