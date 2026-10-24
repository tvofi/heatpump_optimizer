Fix review: merge dcec0b010961256b49112d66af73805f3c592ebf

bus-nonce: 94b2340a6b53541ecb8892e5210410c4

## Scope

PR #2759, triage batch 16 (P85), round 1 at this head; the earlier dispatched head 5c824098 is ignored as briefed. Measured head dcec0b010961256b49112d66af73805f3c592ebf on merge base 2636ce9e9. Three-dot delta: `dev/programme/triage/s6-batch16.md` (new, 36 lines) and `dev/programme/delivery/2759.md` (new, 1 line). No production code, check, budget, closure, golden or claim file is touched, so steps 1, 4 and 14 have nothing to mutate or re-derive beyond the ruling's own consumer.

## Findings

- The carry text for R10-FLY-LEDGER-SAMPLE does not say what happens to the one push when a single shard fails. At 2636ce9e9, `mutation-ledger-push` in `.github/workflows/nightly.yml` runs only on `needs.mutation-ledger.result == 'success'`. A matrix's default `fail-fast: true` cancels the sibling shards when one fails, and a matrix with any failed arm reports `failure` to `needs`. So one crashed shard would throw away every other shard's kills that night. The ruling's line "every failure mode is a partial shard or a listed survivor, never a red job" holds for clipped shards but not for a crashed one. The group should set `fail-fast: false` and decide whether the push applies the shards that succeeded, for example by gating on `!cancelled()` plus each shard's own `status` file, which `merge_pin_shards` already ranks. Carry: R10-FLY-LEDGER-SAMPLE
- Shard sizes are not bounded by `--max 80`. `pin_shard` deals whole anchors round-robin by anchor count, not by site count, and `drain_pool` caps the whole slice at N times `--max`. So one shard can draw more than 80 sites while another draws fewer. `--budget-minutes 240` still clips the large shard as partial, so no job goes red. But the "about 220 min per shard" estimate holds only on average, and the first-night control should report each shard's drawn count against 80. Carry: R10-FLY-LEDGER-SAMPLE
- The ruling's convergence figures disagree with each other. "Roughly 3400 killable sites" is the orchestrator's figure and was not re-counted. Against 4012 unpinned sites it implies a kill share of about 85 percent, which is the 15-percent-survival assumption the ruling itself rejects. At the ruling's own measured 50 to 70 percent share, about 2000 to 2800 of 4012 sites are killable. Also, `drain_pool` redraws survivors from the unpinned stock, so the yield per night falls as the stock drains. "About 3 weeks" is therefore an estimate, not a derived figure. The group's first-night controls (kills, survivors, drawn counts) measure it directly, so nothing needs to change in this PR. Carry: R10-FLY-LEDGER-SAMPLE

## Evidence

- RESULT `roster_edit.ruling_verdict(batch16, "P85")` = ACCEPT; `"P99"` = None, which reproduces the body's null control. A mutant with the `Verdict:` line deleted returns `unreadable`, so the consumer does read that line. `triage_refusal` passes a text citing `triage: dev/programme/triage/s6-batch16.md#P85` (returns None). Output is in `ev/results.txt`.
- RESULT Figures: there is 1 `Verdict:` line, and it is ACCEPT. This matches the body.
- Head: the body's `## Head` names dcec0b010961256b49112d66af73805f3c592ebf and merge base 2636ce9e9, which is the head I reviewed. It lists the three commits (94182758, 5c824098, dcec0b01) as the history shows them.
- Merge: `git merge-tree --write-tree origin/main <head>` against origin/main 593c4fb28 exits 0 with tree 576a0c42, so there is no conflict (`ev/git.txt`). No other branch uses the P85 number: P84 is on `triage/s6-batch15` (#2758) and P80 to P82 are on main.
- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched. The roles diff from the merge base to origin/main is empty, so this contract is current.
- Delivery row: `dev/programme/delivery/2759.md` follows the format of the existing rows (for example 2748.md). `dev/programme/` is on `tests/closure.py`'s INERT list (line 273), so both new files are classified.
- Every tree claim in the ruling was checked against 2636ce9e9:
  - `pin_shard` deals anchors round-robin in sorted order and its shards are disjoint.
  - `merge_pin_shards` folds `status`, `pins.json` and `head` with a precedence, and does not union `survivors.txt`.
  - `write_drain` writes the same layout plus `survivors.txt`.
  - `--shard` is honoured only under `--pin-killed`; its help says so, and the `--drain` branch in main() never slices.
  - Both nightly jobs save their pool-seconds cache under `pool-seconds-${{ github.run_id }}`.
  - The schedule is the single cron `17 2 * * *`. The other crons are in separate workflows: `codeql.yml` `41 2 * * 1` and `governance.yml` `0 7 * * 1`.
  - The `tests/entities.py` cron check needs only a daily `\d{1,2} \d{1,2} \* \* \*`, which `37 0 * * *` satisfies.
  - `nightly.yml`'s comment says `mutation-nightly` "records nothing".
  - `tests/nightly_status.py` `missing_lanes` already strips a matrix suffix (` (`), so `mutation-ledger (1)` and its siblings still count as the required lane.
  - The ledger lane today runs `--max 40 --jobs 3 --budget-minutes 270` with `timeout-minutes: 330`.
- The durations were re-derived from the job list of run 40054585693 through the API. `mutation-ledger` ran from 02:32:24Z to 04:58:29Z, which is 146 min, and the run was created at 02:32:22Z. 146 / 40 = 3.65 wall-min per mutant, and ×3 workers is about 11 core-min. 80 × 11 / 4 is about 220 min. 4 × 80 = 320, and 60 percent of 320 is about 190.
- Figures I could not re-derive:
  - The unpinned counts (4062 to 4012) and total sites (6283 to 6297) are the orchestrator's; the body says so.
  - The daily kills of 20 to 28 are also the orchestrator's.
  - The merges-by-hour counts are also the orchestrator's.
  - The 02:35:26Z start of the other scheduled run.
  - The repository's `private: false` setting.
  - The S6-V20 proposal text, which lives in the out-of-tree s6 `proposals.md`. So I could check the ruling against the tree's mechanics and against tvofi's three relayed questions as the ruling quotes them, but not against the proposal's own wording.
- The ruling answers all three relayed questions: (1) higher within about 4 hours: 320 at 240 min per shard; (2) the cost to programme CI: one push, placed in the lowest-merge hours; (3) as many mutants per push as possible: shard, still one push. It moves the reduced budget (270 to 240) together with the push window, and it keeps `mutation-nightly` unchanged, in line with that job's "deliberately one job" comment.
- Mutation proof: n/a. No production line exists. The consumer mutant above (deleting the `Verdict:` line) shows the gate reads the file.
- Forward-carry: per the body, the orchestrator routes the carry through `roster_edit.py` after the merge, citing this file. The three findings above belong in that group's brief when it is created.
- CI at this head (check-runs API): no check concluded red. The following have passed: fast (3.14), closures, closure-scope, browser, typing, coverage, coverage-ratchet, mutation, lane-proofs, briefs, policy-docs, delivery-status, env-matrix, wave-script, budget-raise-gate, arch-score, nightly-status, hassfest, validate-hacs, and the three codeql runs. When this verdict was written, `governance / instrument-self-tests` and the `prelude` of run 40129784732 were still in progress. The body's `## Red checks: none` matches every concluded run. If either in-progress run ends red, the body owes an answer under step 11.
- I did not run `tests/entities.py` locally: there is no Home Assistant package in this container (`ev/entities-local.txt`). For that I rely on CI's `fast` and `closure-scope` passes.
