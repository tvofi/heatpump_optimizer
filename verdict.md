Fix review: merge 884c291aa428ada298f9aa1b63f804962bf9e2f5

bus-nonce: e188930c87defddd920db1ed4a94ef1c

## Summary

Round 1. This is the first verdict on #2922: the PR has no comments and no earlier probe ref. Measured at head `884c291aa428ada298f9aa1b63f804962bf9e2f5`, which is still the PR head after CI concluded. The diff against merge base `beb570c817c4efcae0d5f6f4bba52f3383baf8db`, which is origin/main, is two added markdown files: `dev/programme/triage/s6-batch51.md` (229 lines) and `dev/programme/delivery/2922.md` (1 line). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract I followed is current.

## Findings

- The figure "1 of 1002" in P253, and the "2904 commits before 10-26" built from it, were not taken at the ref the section names. The section says "read at origin/main `f844df1fe`". At `f844df1fe` the count since 2026-10-26T00:00Z is 1 of **994**. 1 of 1002 is the count at the next main commit, `eab04d0eb`. So `2904 = 3906 - 1002` mixes the two refs. Taken at one ref it is 2912 (`f844df1fe`: 3906 - 994), and the anthropic count in that window is 499 either way. The 17 % and 0.1 % rates and the ruling do not change, and neither does the carry. Carry: dismissed: a prose figure off by 8 commits between two adjacent main refs; no ruling, carry or gate reads it
- A task is owed after the merge: `roster_edit.py append-carry R10-FLY-NO-FOOTERS` citing `triage: dev/programme/triage/s6-batch51.md#P253`. It is queued and held until the file is on main, because the triage gate refuses a citation to a file that is not on main (null control below). The carry text in the file states its controls: the mutant that drops the `anthropic-identity` class fails the refusal arm, and the `--over` fence is the null control for old commits. Carry: R10-FLY-NO-FOOTERS
- P251 item 3 records as owed an owner decision on whether L/XL, critical-path and repeatedly blocked fixers move to cloud. Triage did not overturn the owner's 2026-10-24 ruling, which is in force. Carry: dismissed: an owner ruling stands and nothing in the tree is owed; whether to revisit it is the owner's call
- P250 is a DEFER whose trigger is a measurement the orchestrator takes outside the tree: per-step times for 10 or more open-time prepr runs. If that measurement clears the bar, the owner is R10-PREPR-CAP, whose stage is `done`, so it would be a reopen. Carry: dismissed: a DEFER with no tree change owed; the measurement is orchestrator practice and the reopen is conditional on it
- `governance / instrument-self-tests` (job 122999149895) concluded `cancelled` at 18:16:14Z after about 20 min. It stopped in the step "Show the CI predictor (tools/pr/ci_predict.py) predicting pr-contract's carry refusal", and the two steps after it were skipped. The diff writes no file that job reads: two markdown files under `dev/programme/`. Carry: dismissed: not this PR's, since a markdown-only diff cannot reach the ci_predict self-test; `gate` concluded success on this head, so the cancelled job does not block

## Evidence

- RESULT mutation-proof: on the committed file, `roster_edit.ruling_verdict` reads P249 REJECT, P250 DEFER, P251 ACCEPT, P252 REJECT and P253 ACCEPT. `triage_refusal` refuses carries citing P249, P250 and P252 (`is not an ACCEPT ruling (REJECT|DEFER)`) and passes P251 and P253.
  - Mutant P249 to ACCEPT: the P249 carry passes.
  - Mutant P253 to REJECT: `#P253 is not an ACCEPT ruling (REJECT)`.
  - Extra mutant, the P253 `Verdict:` label renamed: `(unreadable)`.
  - The script and its output are `ev/mut.py` and `ev/mutation.txt`.
- RESULT null-control: with the file absent, every citation returns `the triage ruling dev/programme/triage/s6-batch51.md is not on the roster branch or origin/main`, matching the body.
- RESULT figures re-derived at `f844df1fe750d5e420af0d1555f4b9472a740413` (`ev/figures*.txt`, `ev/identities.txt`). With `--since` anchored at 2026-10-21T16:40Z, about when the filing ran `--since=7.days`:
  - author email: 500 of 3906
  - committer email: 482
  - identities: 453 `Claude`/`Claude`, 20 `Claude`/tvofi, 27 seat names
  - all history: 919 of 12434 (author), 863 (committer)
  - daily spread: 47 on 10-18 and 159, 168, 57, 122, 64 on 10-21 to 10-25; the last of that run is `70b57a370` at 10-25T20:07:12Z
  - since 10-26: only `b9a66d28d`, authored and committed as `Claude <noreply@anthropic.com>` at 2026-10-28T01:41:39Z. It is an ancestor of main, and `71fe1f7fc` is the #2903 merge. All of these match the body.
- RESULT figures I could not re-derive: the host-side figures, which are read on the orchestrator's host and are not reproducible from this container:
  - `gate_lock.py slot-status` 4/4 at 16:03Z
  - load averages 64.09, 75.32, 67.71 on 8 cores
  - open durations of 13, 16, 23 and 30 min
  - 11 `tests/features.py` processes
  - seat-dir counts (5, 4, 2, 1) and 17 STATE/RESUME files
  - the wt_sync pass timings, 76,178 files and 113 passes
  - 524 `wip-sync/*` refs, a count that changes as refs are pushed. I did not re-count it.
- RESULT cited code at main. The cited files are byte-identical between `f844df1fe` and `beb570c81` (`ev/cited-files-moved.txt` is empty). All of these hold:
  - `tests/gate_lock.py:102` `HEAVY_SLOTS = 4`
  - `ref_privacy.py` `email_leaks` at :240; author and committer emails added at :347; null control `email_leaks("noreply@anthropic.com", fid) == []` at :706; `host-email` CLI arm at :781
  - guard invoked at `handoff_push.sh:141` and `app_push.sh:376`
  - `wt_sync.sh:27` is the worktree-list arm and `:39` is the per-file `git hash-object`
  - `prepr.sh` has 3927 lines, no `tests/run.sh`, and a self-test skip at 3650-3656
  - `cloud_dispatch.py` sets identity only through `_SEAT` (:225) and the verdict commit-tree (:150-151)
- RESULT merge: `git merge-tree --write-tree origin/main 884c291a` exits 0 (tree `07920609072ccc2608b44e6daf5db143a057b83f`, `ev/merge-tree.txt`). Neither claim file is touched.
- RESULT version: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (the three-dot diff over those paths is empty).
- RESULT metrics: no budget, closure, golden, claim, score or ledger file moves, so step 14 has nothing to remove. No production line is added, so step 15 has no added code to judge.
- RESULT head: the body's chain holds: `b64672f6a` against `f844df1fe` is the triage file alone, `dbeaed1ba` merges main `beb570c81`, and `884c291a` adds only `dev/programme/delivery/2922.md`.
- RESULT class (step 6): this is a triage ruling with no product seam. The body names no enumeration rule, and none is owed for one markdown ruling file.
- RESULT naming: the file is `s6-batch51.md` while its header says "session s7". That follows the tree's convention: `s6-batch35..46` on main also say session s7. Numbering continues after P236 on main, and P249-P253 do not collide with anything there.
- RESULT review packet: rendered at this head (`ev/review-packet.md`). Refusals: none. carry_audit: 1 routed, 0 unrouted. figure_lint: 2 resolved, 3 unverified (git flags), 0 refused.
- RESULT CI at this head (`ev/check-runs-final.tsv`, read from the check-runs API after every run had completed): `gate` success (twice), `pr-contract / pr-contract` success (twice, the last completing 19:36:09Z), `tests / closure-scope`, `closures`, `fast (3.14)`, `coverage`, `typing`, `mutation`, `briefs`, `policy-docs`, `delivery-status`, `nightly-status`, `env-matrix`, `wave-script`, `arch-score`, `budget-raise-gate`, CodeQL, hassfest and validate-hacs all success. No check concluded `failure`. The cancelled `governance / instrument-self-tests` is listed under Findings.
- RESULT red-checks (step 11): no gate check went red, so the body's `none` stands.
- Local runs: `tests/entities.py` cannot run in this container, because `homeassistant` is not installed. CI's `closure-scope` and `closures` concluded success at this head, and I cite them for classification of the new files.
