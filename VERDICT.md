Fix review: merge 4a07b1eca5cfd6c507ad7bdcd29e38af6e46f3de

bus-nonce: 2d64a4b1339cc077151b3445b5840a7e

Round 1 (first review; no reviewed head). Head measured = body head = 4a07b1eca5cfd6c507ad7bdcd29e38af6e46f3de.

## Evidence

- RESULT: classify `GREEN 4a07b1eca5cfd6c507ad7bdcd29e38af6e46f3de pending: none red: none` (ev/classify.txt).
- RESULT: `git merge-tree --write-tree origin/main <head>` exits 0, no conflict (ev/merge-tree.txt).
- RESULT: roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.
- RESULT: VERSION, manifest and RELEASE_NOTES.md untouched in the three-dot diff (ev/version.txt); no golden or claim file in the diff, so env_drift has nothing to compare (diff: ci.yml, tests/entities.py, dev/programme/delivery/3923.md; ev/diffstat.txt).
- RESULT: mutation proof re-run on the real script (`PYTHONPATH=tests/hastub tests/entities.py`, partial run to the rows): at the head every diff row is ok (ev/entities-head-rows.txt); with ci.yml set back to the base the three rows the body names FAIL (body-edit caller set, `#3885 L5 ...`, token-hygiene null control) and the supersession row stays ok (ev/entities-m1-base-ciyml.log), as the body states.
- RESULT: reviewer-built driver (ev/drv.py, ev/mut.py; the reviewer's instrument, not the finder's) evaluating the five supersession/refresh/token rows verbatim from tests/entities.py: baseline 5/5 PASS; ten mutants each caught (ev/mutants.txt): cancel step `if:` deleted -> supersession row; refresh `if:` losing the restore guard or `!cancelled()`, restore dropping `tools/ci/*.py`, refresh step deleted or moved before restore, job `if:` narrowed to pull_request or to same-repo heads, GH_TOKEN dropped, a second `refresh` job re-added -> the L5 row (plus the write-grant row, or its null control, where the restore or the extra job is the mutant).
- RESULT: design trace: design.md at 43ff5ae6 §L5 ("two steps of one job, keeping their order and conditions; refresh keeps running on review events"; test: the entities caller-set pin plus a run showing both steps) is met: step order restore -> cancel -> refresh, cancel step keeps the old job condition, job admits pull_request and pull_request_review including fork heads, caller-set pin updated, and the body cites run 45912926553 with both steps `success` in one job.
- RESULT: figure `Housekeeping jobs per pull_request event: base 2, head 1` re-derived with the body's rule at base 7194ff84 and head (ev/figure-jobs.txt): base lists `cancel-superseded` and `refresh`, head `cancel-superseded` only.
- Not re-derived: the per-run job timings (runs 45907700288, 45891233921) and the census arm figure; GitHub API history not read from this seat. The body states the census after-figure is owed on the first busy day past the merge.
- RESULT: red checks: classify reports none at the head; the body answers the earlier `gate` deferral red and names `tests / nightly-status` as outside the owed set.
- RESULT: finder's harness: none named (CI-cost lever from an approved design; no audit finding harness). Mutation lane draws no diff mutant (no production Python); the hand mutants above are the proof.
- RESULT: self-audit: `carry_audit.py check` over this verdict rc=0 (1 routed, 0 unrouted); over the body, the packet's `CARRY-AUDIT: 0 finding item(s)`.
- RESULT: refusal-on-actuator-write (step 16): not applicable, no `custom_components/` change.

## Findings

- Note: body-stale: the `## Head` section carries two paragraphs for two repairs and a garbled base line (`4f0c7af... on origin/main 8890fc2...`); paperwork only. Carry: dismissed: body paperwork, no code effect
- Follow-up: the design's `census` arm after-figure (ci3885_queue.py) is owed on the first busy day past the merge, as the body states. Carry: dismissed: owed and stated by the body's Figures section for the group's own lever measurement, not a finding of this review
