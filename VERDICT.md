Fix review: merge dfd5227d8cfdf534794ab3acd3271363287ba728

bus-nonce: 4ccf9af80fb1919096d1111d68979fd6
seat: review-deltas-1015
Evidence: /Users/timmalmstrom/hpo-seats/review-deltas-1015/2069/evidence

Round 4 of this PR. This is a **resolution delta**, judged on its own: the live head moved from `d8988a473a4d1c282278ecee1c1b37ddd22754f5` (my round-3 `merge` verdict, comment 6071499556) to `dfd5227d8cfdf534794ab3acd3271363287ba728` under an orchestrator push, so the round-3 verdict does not carry (the delta names a file inside the branch's own three-dot diff) and I re-measured at the new head. Nothing here is a re-cut owed by `fixer.md` — the fixer's lines are untouched; the orchestrator wrote the record row.

## The delta, and what it claims

`git log --first-parent d8988a47..dfd5227d8` is three commits, and they are what the brief says they are:

- `99d958b8e` merge of main `c518447eb`, `ee43721f1` merge of main `b2b6acd64` — both automatic, no resolution;
- `dfd5227d8 record: the delivery row for #2069` — **one commit, one file, one line**: `dev/programme/delivery/2069.md`, `1 file changed, 1 insertion(+)`.

Delta diff stat `d8988a47..dfd5227d8`: 33 files changed, 2784 insertions(+), 1254 deletions(-).

- RESULT delta-path attribution: of the 33 paths, 32 are paths `origin/main` itself changed between `d8988a47` and `b2b6acd64`; the set difference names exactly one path outside main's set — `dev/programme/delivery/2069.md`. No third thing rode along. (The reverse difference — paths main's tree differs on that the head did *not* change, `tools/pr/app_push.sh` and `tools/audit/seat/remerge_main.sh` — is not a dropped main edit: `git log bd59a4af..b2b6acd64` touches neither, they differ only because of this branch's own edits, and the merge left both blobs byte-identical to `d8988a47`. See the line test below.)
- RESULT the row is one line, anchors #2069 (`…/pull/2069`, one match), and is in main's row shape (compared with `origin/main:dev/programme/delivery/2062.md`). `delivery-status` is success at this head, which is the lane that reads rows.
- RESULT reviewed content unchanged: the branch's own three-dot patch (merge base `bd59a4af` at the verdict head, `b2b6acd64` at the new head) carries **271 changed `+`/`-` lines at both heads, identical in order** once the row file is excluded. Only hunk-header line numbers and blob-index lines shift, because main added lines above them.
- RESULT step 13: `git merge-tree --write-tree origin/main dfd5227d8` → rc=0, tree `6bf35903a9127f4cb4125f99dc022e65fc59abab`, clean; no `MERGE-CLAIM` marker on stderr (driver installed in this clone).
- RESULT claim files byte-identical to `origin/main` at this head: `claimed_drift.txt 62bf9eaba2…`, `card_claimed_drift.txt c683379daf…`.

## Step 11 at this head (settled, from the commit's own check-runs API)

40 records, 38 distinct names, **all completed**: success or skipped only, and **zero red runs anywhere in the head's records** — including the two names that ran twice (`pr-contract` 113787346774 + 113787493444, `budget-raise-gate` 113787345802 + 113787347925), green on both, so there is no red-then-green to misread.

- All **17 required status contexts** (ruleset 23698884, `main-protect-checks`) are present and success — none absent. The governance family reported at this App push: `policy-docs`, `env-matrix`, `wave-script`, `instrument-self-tests`, `delivery-status` success, `record`/`delivery-status-publish` skipped.
- `nightly-status`, the one red at my round-3 head, is **success here** — nothing I answered in round 3 needs the body to answer it again.
- The reds the body answers (`instrument-self-tests`, `pr-contract` at `6b1d0c46`, named with the cheaper detector and its routing) are unchanged in `## Red checks`; the trigger is answered, and my round-3 verdict already judged that answer.
- The full suite, the mutation table and the closures re-record remain CI's — cited, not re-run. `mutation` and `closures` are both success at this head.
- RESULT the four files this PR owns (`tools/pr/app_push.sh`, `tools/audit/seat/remerge_main.sh`, `tools/audit/seat/merge_train.py`, `tools/audit/seat/INSTRUMENTS.md`): `app_push.sh` and `remerge_main.sh` are blob-identical `d8988a47`→`dfd5227d8`; the other two blobs moved because main itself edited them in `bd59a4af..b2b6acd64` (R9-RO-9a, `42bf40f99`/`de5f65497`) and the merge inherited that. Line test, both sides: all 14 + 5 branch-added lines and all 21 + 6 main-added lines are present at the head — **nothing from either side dropped**, which is what a clean automatic main merge owes.
- RESULT nothing round 3 measured is invalidated: the branch's own lines in all four files are intact at this head, so the SIGPIPE control, the (a)/(b)/(c) attack set and the 91-check mutation proof all still describe the code.
- GitHub: `mergeable=true`, `mergeable_state=blocked` (approvals outstanding, not a merge blocker I own), `draft=false`, base `b2b6acd64`.

## Not mine to decide (unchanged from round 3)

The body's `## Approval` still owes the code-owner/approver path: this PR changes `tools/pr/app_push.sh` and the train's recarry. `mergeable_state=blocked` is the approval, not a red.
