Fix review: merge 4d4b3a5b3aa235311b596938e2041acefc0c4380
the prior carry-missing finding is cleared at this head and the new work measures sound
bus-nonce: b5cc5472ed41febf0153093f969e9a22

# Fix review — #2871 `roster: round-10 batch 23`

Round: 2 (the verdict at `4180a7d01`, `verdict/2871` `9cabb1d70`, was blocked round 1; no re-cut is owed under `fixer.md` until round 4).

Head measured: `4d4b3a5b3aa235311b596938e2041acefc0c4380`, checked before and after every measurement below and still `gh pr view 2871 --json headRefOid` at publication.
Merge base with origin/main: `4f3c7302046eccd1f869724a6de2cbf6f8183418` (= current origin/main).
Three-dot diff: `dev/programme/delivery/2871.md` (1/0) and `dev/programme/rosters/wave-r10-groups.json` (37/25). Nothing under `dev/governance/`, `.claude/rules/`, `.cursor/rules/`; `VERSION`, the manifest version, the `RELEASE_NOTES.md` heading and both claim files untouched. (`evidence/diff-numstat.txt`.)

## The prior finding is cleared

The blocked verdict required the three batch-35 carries to be in the tree, not only the body, because their ruling `dev/programme/triage/s6-batch35.md` (`c73d8984a`, an ancestor of origin/main) was already live. Re-measured at this head:

- **P199 → R10-FLOW-WIP.** Present: the group carries 8 entries at the head vs 7 on origin/main; the new entry begins `Triage P199 (s6 batch 35; triage: dev/programme/triage/s6-batch35.md#P199)`. (`evidence/roster-carry-stage.txt`.)
- **P200 → R10-ORCH-REVIEW-PACKET.** Present: 10 vs 9, cites `#P200`.
- **P203 → R10-ORCH-ROSTER-SCHEMA.** Present: 23 vs 22, cites `#P203`.

Each destination is the one the triage file's Verdict line names, and each group is live (`not-started` / `in-progress`). The three carry commits the body names — `82db76ffe`, `d052b8d78`, `2f63ddb60` — are ancestors of this head, so the carries are in the PR's own diff as well as on `handoff/audit-r10-roster`. Each carry text states its controls and its binding precondition on the same line: P199 `Controls: (1) the s60 shape ... (5) one mutant drops the end-line test and must fail (1)`, P200 `Binding: fix-review.md is at its policy cap ..., so the carry must pay by deleting prose in the same file`, P203 `Controls: a fixture of the gate strings ... one mutant ... null -- a group with no gate is not in the line at all`. (`evidence/forward-carry.txt`.)

`tools/audit/carry_audit.py pr 2871` reads the PR body as 5 finding items, all routed, 0 bad destinations. (`evidence/carry-audit.txt`.)

## Claims verified

- **Stage value.** `R10-HOUSE-GRADE.resume.stage` is `in-progress` at this head. `629674e0c` is the write that changed it, and its roster diff is exactly `- "stage": "in-review"` / `+ "stage": "in-progress"`. The null control reproduces: at `6bece0588` the stage is `in-review` and the unclassified scan returns `[('R10-HOUSE-GRADE', 'in-review')]`; at the head it returns `[]`. (`evidence/null-control-stage.txt`, `evidence/stage-classification.txt`.)
- **The four matched rows.** R10-HEAT-METER, R10-SAV-COMFORT, R10-COP-PARTLOAD and R10-FLOW-JIDOKA each carry `in-progress` and a `next_step` saying a review is owed, exactly as the body states. Roster-wide there are zero unclassified stages at this head.
- **Red check matches CI exactly.** Job `122016117273`, run `40451793722`, step 59 (`Show the roster-sync reconciler refusing its own fixtures`) concluded `failure` at head `6bece0588`; the run is the `CI code pr=2871` run at that sha and its only failed job is `governance / instrument-self-tests` (27 success, 12 skipped beside it). At this head the same context is `success` (job `122059761224`). (`evidence/job-122016117273.json`, `evidence/job-122016117273-summary.txt`, `evidence/red-run-jobs.txt`.)
- **The red check's answer is present.** The body names the check, the failing line, the cause (`in-review` in neither `DERIVABLE_STAGES` nor `PROTECTED_STAGES`), a cheaper detector (the same `roster_sync.py --self-test`, seconds locally) and demonstrates it failing at `6bece0588` and passing at `629674e0c`; I reproduced both (`55 checks, 1 failed` with the exact `FAIL every stage ... (got: {'in-review': 'wave-r10-groups.json'})` line, then `55 checks, 0 failed`). (`evidence/self-tests.txt`.)

## The disclosed drift is not a revert

On origin/main `R10-COP-PARTLOAD` reads `fixing` / `50ef300f7`; at the head it reads `in-progress` / `775ae0340`. This is a newer write, not a revert of another seat's row: main's write `de0354ada` is dated `2026-10-26T23:28:05+01:00`, the branch's write `deee1e8ca` is `2026-10-27T03:58:17+01:00`, and `de0354ada` is an ancestor of `deee1e8ca` (`git merge-base` of the two is `de0354ada`; `de0354ada..deee1e8ca` counts 41 commits). The branch therefore saw main's `fixing` write and superseded it with the pushed-handoff state; the handoff's `last_step` carries the structure re-record the main row described. No other origin/main commit after `de0354ada` touches the row. (`evidence/cop-partload-timeline.txt`.)

## Instrument behaviours judged

- **`closure.py select` workdir poisoning: real, and not the gate's.** Reproduced both ways. A `--workdir` inside the repo makes a second `select` in the same directory print `MODE: FULL` with `reason: no recorded closure mentions .scope-test/scope.json, .scope-test/scope.run, .scope-test/scope.skip, .scope-test/scope.txt`; a workdir outside the repo prints `MODE: SCOPED` on both runs. The gate is unaffected: `tests/run.sh:132` puts `WORKDIR` under `mktemp -d` in `TMPDIR` (outside the repo, which I confirmed), calls `select` once, and `tools/pr/prepr.sh:3167` passes no `--workdir` at all. Sound. (`evidence/closure-poison.txt`.)
- **The `in-review` contradiction class is not worsened.** This PR removes the only `in-review` occurrence and adds none; it deliberately does not add `in-review` to `roster_sync.py`'s tuples, so it neither entrenches the contradiction nor creates a second reader. The class is being root-caused and carried separately. Carry: R10-ORCH-ROSTER-SCHEMA

## Measurements at the frozen head

- **CI.** 81 check-runs across all pages, 47 distinct contexts: 50 `success`, 31 `skipped`, **zero non-green**. (`evidence/check-runs-all.tsv`, `evidence/check-runs-summary.txt`.)
- **Scoped gate, re-derived in a clean workdir.** `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, `RUN tests/doc_claims.py`; the named script prints `ALL 203 checks PASSED`. A re-run in the same directory outside the repo stays `SCOPED`, so the figure is not a reuse artefact. (`evidence/scoped-gate.txt`.)
- **The closures arm agrees and is green.** `closure.py affected --files <the two files>` re-derives 2 closures: `tests/doc_claims.py` (the roster) and `tests/harness_headers.py` (via its recorded inert read of `dev/programme`, `dir: dev/programme`). `tests / closures` is `success` at this head, so harness_headers was re-derived and ran; the gate's `select` arms the fast subset only, which is the two-arm design of `1ec5ce967`. No under-scope. (`evidence/closure-affected.txt`.)
- **Merge-tree.** `git merge-tree --write-tree origin/main HEAD` exits 0, tree `0f26573d0d9a31781c65e53fdb80c9787988f65d`, which is `HEAD^{tree}` and the tree the body names. (`evidence/merge-tree.txt`.)
- **Roster is valid and tool-shaped.** JSON loads, 208 groups, blob `91933dbd2`, and byte-identical to `json.dumps(d, indent=1)`. `roster_sync --self-test` 55/0, `roster_edit --self-test` 117/0, `record_row --self-test` all passed. (`evidence/self-tests.txt`.)
- **Lint and ratchet.** `brief_lint.mjs` `TOTAL: 0 error(s) across 1 file(s)`; `tests/structure.py` `STRUCTURE RATCHET PASSED`. (`evidence/brief-lint.txt`, `evidence/structure.txt`.)
- **Body figures re-derived at the merged tree, not an ancestor.** roster blob `91933dbd2` (main `852ec7bdd`), origin/main..head numstat `1/0` + `37/25`, 9 changed groups, carry counts main `7/9/22` head `8/10/23`, unclassified `[]` at head and `[('R10-HOUSE-GRADE','in-review')]` at `6bece0588`, ruling `c73d8984a` is an ancestor of origin/main. All match the body.
- **The `R10-FLY-WIP` friction is real.** The triage file's P199 Verdict names `R10-FLOW-WIP` (line 15) but its orchestrator dispatch list names `R10-FLY-WIP` (line 406); `R10-FLY-WIP` is a group in neither roster, and `R10-FLOW-WIP` is the group whose files and `after` edge match, where the carry landed. The fixer routed to the group that exists, per `finding-propagation.md`. (`evidence/triage-fly-wip.txt`.)

## Findings

None blocking. The one item the prior verdict blocked on is in the tree, routed to the destinations the triage file's Verdict names; the red check is answered and reproduced; the disclosed drift is a forward write, not a revert; and every figure the body quotes re-derives at this head.
