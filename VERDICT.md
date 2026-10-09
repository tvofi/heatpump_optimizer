Fix review: merge 316a364148cfdd47019314decae0037890c7211d

bus-nonce: 68a5ecf57751fa78e9cf3cc3b61bf62d
seat: review-deltas-1015
Evidence: /Users/timmalmstrom/hpo-seats/review-deltas-1015/2072/evidence

Round 4 of this PR, judging a **resolution delta** only: the live head moved from `8766b840f5582e96d13b7a322da0662433cce9a5` (my round-3 `merge` verdict, comment 6075940169) to `316a364148cfdd47019314decae0037890c7211d` under an orchestrator push. The round-3 verdict does not carry because the delta names a file inside the branch's own three-dot diff, so I re-measured at the new head. No `fixer.md` re-cut is owed: the fixer's lines are untouched.

## The delta, and how it differs from what the brief claimed

`git log --first-parent 8766b840..316a36414` is **one commit, not "main merges + one commit"**:

- `316a36414 record: the delivery row for #2072` — `dev/programme/delivery/2072.md`, `1 file changed, 1 insertion(+)`.
- `git rev-list --count 8766b840..316a36414` = 1, and the reverse = 0; `origin/main` (`b2b6acd64`) is **not** an ancestor of this head. The base is still `bd59a4af1b26`. So this PR received no main merge in the delta — my measurement, stated rather than assumed.
- Delta diff stat `8766b840..316a36414`: 1 file changed, 1 insertion(+).

- RESULT the row is one line, anchors #2072 once (`…/pull/2072`), and matches main's row shape; `delivery-status` is success at this head, which is the lane that reads rows.
- RESULT nothing else moved: the branch's own three-dot patch (merge base `bd59a4af`, unchanged) is **byte-identical once the row file is excluded** — the same 4 files, the same hunks; the only addition to the patch text is the row's own 7 lines.
- RESULT the policy paths this PR names, which the brief asked me to confirm untouched: `CLAUDE.md` `422732316…`, `dev/governance/roles/fixer.md` `db02b3db4…`, `dev/programme/carries/carry-1922.json` `54bc1ff31…`, and `tools/pr/prepr.sh` and `AGENTS.md` are all **blob-identical between `8766b840` and this head**. The round-3 review therefore still describes the code exactly, including the re-pointed retired-harness names in `CLAUDE.md` and `fixer.md`.
- RESULT claim files byte-identical to `origin/main` at this head (`62bf9eaba2…`, `c683379daf…`); `git merge-tree --write-tree origin/main 316a36414` → rc=0, tree `cbdf53fce1f7dc46c…`, clean, with no `MERGE-CLAIM` marker on stderr (driver installed), and GitHub reports `mergeable=true`, `mergeable_state=clean`, `draft=false`.

## Step 11 at this head (settled, from the commit's own check-runs API)

40 records, 38 distinct names, **all completed**; latest per name is success or skipped, and **zero runs anywhere at this head are red**. The two names that ran twice are green on both runs — `pr-contract` 113796819988 and 113796991843, `budget-raise-gate` 113796820024 and 113796824763 — so there is no red-then-green to misread.

- All **17 required status contexts** (ruleset 23698884, `main-protect-checks`) are present and success; none absent.
- The governance family reported at this App push: `policy-docs`, `env-matrix`, `wave-script`, `instrument-self-tests`, `delivery-status` success; `record`, `delivery-status-publish` skipped. `fast (3.14)` — the lane the layout guard lives in — is success, as are `closures`, `closure-scope`, `mutation`, `coverage`, `coverage-ratchet`, `typing`, `browser`, `briefs`.
- `nightly-status`, the only red at `8766b840` in round 3, is **success here**; nothing in `## Red checks` (which says none) needed re-answering.
- CI's heavy lanes are cited, not re-run. My round-3 local numbers — the 220-passed self-test, the `--guard`/`--stale` null control, the planted retired-path refusal — were taken at `8766b840`, and every file they measure is byte-identical at this head, so they survive un-re-taken; the row commit adds no line to any of them.
- The macOS SIGPIPE note I recorded in round 3 (`printf | grep -q` over `set -o pipefail`, rc 141 under load) still stands as a note against `prepr.sh`, unchanged by this delta and answered on #2069, whose diff is exactly that fix.

## Not mine to decide

`## Approval` still records the owner's approving review as owed at the head for the two policy re-points (`CLAUDE.md`, `dev/governance/roles/fixer.md`); `budget-raise-gate` and `policy-docs` are green, but the merge gate for a policy path is the review, not the tick.
