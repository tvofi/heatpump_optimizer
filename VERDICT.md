Fix review: merge a22a15f1d946db9c5afb52e4f14dd81146165a00

bus-nonce: 3e86c9c1580c586d5edb146ce993066e

## Findings

- Contradictory batching floors on R10-FLOW-RECORD-PITCH. Op `e8b692b0f` appends the 2026-10-25 owner directive (carry [7]: record PRs batch "at least 8-10 delivery rows", the safe maximum to be measured). Carry [6], the P88 text from `dev/programme/triage/s6-batch19.md` ("open or update the record PR only when the plan holds at least 4 rowless merges", with a margin derived from that floor), stays on the group unchanged. Neither carry says which one binds. A fixer given both has two floors, and the margin arithmetic in [6] (8 commits under `STALE_AFTER_COMMITS = 12`) is tied to the floor of 4. Carry [7] also names R10-FLOW-MQ-PROBE as owner of tests.yml's merge_group handling, and that group is now done with nothing merged. Precondition for the fixer: treat [7] as superseding [6]'s floor of 4, re-derive [6]'s staleness margin for the floor that [7]'s measurement picks, and do not count R10-FLOW-MQ-PROBE as a live seam owner. Carry: R10-FLOW-RECORD-PITCH
- Dangling evidence path in a live carry. Op `c5b71ebe8` (R10-ROUND-PLAYBOOK, the round-11 org-move decision item) cites `dev/audit/rounds/round10/D13/mq-probe.md` as the record of the HTTP 422 probe "with controls". The file is not at origin/main or at this head: it existed only on #2826, which the owner closed unmerged on 2026-10-25. The fix review of #2826 found that its positive control is missing, and the owner's closing comment accepts that finding as unresolved. So "with controls" overstates what was recorded. Precondition for round 11's plan: cite #2826's head `754ab29f7aab253c26981159034d292cc45d4256` and the owner's closing comment (6402178136) instead of the tree path, and state that the positive control is missing. Carry: R10-ROUND-PLAYBOOK
- Op `6073f1668` (R10-FLY-ROW-HEAD-CARRY, the tests.yml comment wording) cites only #2839, which is still open and unmerged. Its stated reason, that the line was "left out of the ci-ratchet hotfix #2839 on purpose", rests on a PR that may never merge. Precondition for the group's fixer: confirm #2839 merged, and that `run_minutes` in tests/ci_ratchet.py still excludes runner queue, before rewording the comment to cite it. If #2839 closes unmerged, the hotfix this comment describes is not on main. Carry: R10-FLY-ROW-HEAD-CARRY

## Evidence

- Round 1 of review for #2842 (the PR has no comments). The measured head is `a22a15f1d946db9c5afb52e4f14dd81146165a00` (`ev/HEAD.txt`), the PR head when the review started; see the head re-read at the end. Role contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- RESULT ops: `709ee1929..d49603ff8` holds 52 commits and no merge commits. By op: 43 append-carry, 3 append-group, 3 drop-carry, 1 set-after, 2 set-stage. Each subject and group matches the body's Figures list in order. Per op, each append-carry adds exactly one string and changes no existing string (`ev/op-citations.tsv`).
- RESULT citations. Ops that cite a merged triage ruling: every op whose text carries `triage: dev/programme/triage/s6-batchNN.md#Pnnn`. The rulings are P110, P123-P126, P128-P141, P143, P144, P158, P163 and P164, and each is present at origin/main (`ev/pr-merge-state.txt`). Ops that cite a merged PR or merged decision:
  - `362a47062` cites #2829 (P158) and mandate 6329234399.
  - `af7a2ee20` and `12993ed8c` cite mandate 6329234399, which is recorded in merged decision 0015; they also cite open #2819.
  - `86da909ee` cites P141 (merged, s6-batch27) beside open #2834.
  - `2b7fe35c6` cites merged triage PRs #2827-#2831.
  - `d49603ff8` cites #2817, merged at `5261ba84`.
  - `283b24abd` cites #2807 and #2712, both merged.
- RESULT ops that cite neither a merged ruling nor a merged PR. They are named here as the brief asks:
  - `e8b692b0f`, `63d8938eb` and `c5b71ebe8` cite a tvofi directive or ruling of 2026-10-25 given in an orchestrator session. I found no record of these in the tree or on the PRs I read.
  - `12dddd429` cites tvofi's 2026-10-25 acceptance of pipeline-benchmark decision cards. No record of it is in the tree.
  - `6073f1668` cites open #2839 only (Findings).
  - `23b0a4cbc` (set-after removing R10-FLOW-MQ-PROBE), `b4535b9ab`, `1f647d21e` and `60b405dbc` (drop-carry) and `5caa24d5b` (set-stage done) carry no citation in their commit message or their own text. Their authority is the owner's closing comment on #2826 (tvofi, OWNER, 2026-10-25: closed unmerged, result stands, the org move goes to R10-ROUND-PLAYBOOK). The reroute carries `05a6870ac`, `d3f9a3ade` and `0d89a0e5d` cite that ruling, as do the seven "Resolved" carries. #2826 itself is not merged.
  - Each of these is an owner ruling given outside the tree, or rests on one. Only the second and third findings above need a change in the work.
- RESULT carries dropped: net main to merged tree, exactly 3 carries leave any group, all from R10-FLOW-MQ-PROBE. Each dropped string appears verbatim inside a carry on R10-ROUND-PLAYBOOK (stage `not-started`), prefixed "Rerouted from R10-FLOW-MQ-PROBE (dropped: #2826 closed unmerged, tvofi 2026-10-25 ruling ...)". No carry is dropped without being rerouted (`ev/carry-drop-and-stage-check.txt`).
- RESULT carry_audit: `tools/audit/carry_audit.py pr 2842`, run from the merged tree, prints `CARRY-AUDIT #2842: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit.txt`). The body's Forward-carry is `none`.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs`, run on the merged tree (origin/main merged with the head, tree identical to `git merge-tree --write-tree` output), prints `TOTAL: 0 error(s) across 48 file(s)` and exits 0. The fixture ERROR lines it prints are its own self-test arms (`CARRY ok: 10 error(s) pin the carry acceptance ...`) (`ev/brief_lint.txt`). The dangling `mq-probe.md` path in `c5b71ebe8` is not flagged by brief_lint.
- RESULT delivery row: `dev/programme/delivery/2842.md` is added in the three-dot diff `$(git merge-base origin/main HEAD)...HEAD`. The diff's only other file is `dev/programme/rosters/wave-r10-groups.json` (`ev/merge-and-figures.txt`).
- RESULT body figures, all re-derived:
  - groups go 192 to 195, none removed, 3 new;
  - 20 groups changed, with the per-group carry counts as listed;
  - stages main `done 121, in-progress 8, not-started 46, queued 8, absorbed 4, carries-open 5`, merged `done 123, in-progress 7, not-started 45, queued 11` with the other stages unchanged;
  - roster blob `bdc22109539294e43f26872fb0d8579c4f473219` on main and `6c8e6f46ebc63c8cf352392c77944628ae9e8b0e` merged;
  - `git merge-tree --write-tree origin/main d49603ff8` prints `9ebb6bae9e45bbe322326bf48e1c0425651e8d8e`.
- Merge: `git merge-tree --write-tree origin/main a22a15f1d946db9c5afb52e4f14dd81146165a00` exits 0 with no conflict. origin/main `5261ba84139d9459465ccd842b61b04c2b1329d8` equals the merge base.
- Not applicable: the mutation proof, the finder's harness, the null control re-run and the class enumeration (steps 1-3 and 6). The diff writes no production, test or check line. `VERSION`, the manifest and the notes heading are untouched. No claim file, budget or closure moved (step 14 has nothing to remove).
- CI on this head, read from the commit's check-runs API once every run had concluded: 55 runs, 35 success, 19 skipped, 1 failure (`ev/ci-check-runs.tsv`).
  - The one failure is `governance / delivery-status`. Its log lists OVERDUE rows for #2773, #2812, #2813, #2712, #2807, #2804, #2798, #2799, #2780, #2749, #2775, #2797, #2762 and #2795; none of them is #2842. The log also prints "This check is NOT a required context and a red here blocks no merge." This PR's diff adds only its own row, so the red is not this PR's (`defect-root-cause.md`). Its trigger owes no answer, and the body's "Not read by this seat" leaves nothing unanswered.
  - Two `pr-contract / pr-contract` runs (started 00:36:01Z and 00:38:32Z) both concluded success, after the failing check concluded at 00:22:15Z.
- Head re-read before posting: `git ls-remote origin refs/heads/fix/audit-r10-roster-pr12` prints `a22a15f1d946db9c5afb52e4f14dd81146165a00`, the head measured. Every number above was taken at this head.
