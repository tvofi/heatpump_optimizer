Fix review: blocked 93184bb07cd6606e017ebf1bb93795db19ff0f52 carry-missing: not carried to R9-CI-2b (#2057/#2059 do not touch .github/workflows/tests.yml; no brief in the tree holds the tests.yml comment correction or #2024's lost pin)

bus-nonce: b359e196dfb7774a53b86049915e2f18

Round 1. Reviewer seat review-2060. I measured code head cef15d6352e970806dc9a3e32b4c23c92e212e95 (merge base dcc77dd0).

## Head moves (re-dispatched at 93184bb0)

- **cef15d63 to e5439edc:** exactly one file, `dev/programme/delivery/2060.md` (+1, this PR's own row).
- **e5439edc to 93184bb0:**
  - 3433e9d2 merges authored commit 2ac9d6f0, which adds `dev/audit/rca/R9-CI-2.md` section 7 (+26 lines) and one body paragraph.
  - 93184bb0 merges origin/main 4647321d8 (#2056: tests/nightly_ha.py, tests/debug_collect.py, the ledger, delivery/2056).
  - That merge is clean: `git merge-tree --write-tree 3433e9d26 4647321d8` exits 0, and its tree aa1e3496 equals 93184bb0's tree. `merge-tree` against the current origin/main (4647321d8) also exits 0.
- **Every code figure survives.** tests/mutation_table.py and tests/entities.py are byte-identical to the measured cef15d63, and main changed neither since dcc77dd0.
- **2ac9d6f0 reviewed.**
  - Section 7's "16 of 1087" re-derives at dcc77dd0's ledger (`load_budgets()`: 1087 `killed_by` entries, 16 naming tests/structure.py).
  - The `drive_pool`/`driver_order` reasoning matches the code's own docstring.
  - Its disposition (no change here, candidate group to the orchestrator, not filed) is in the tree, in the RCA, which is a durable destination.
  - **It does not answer this block.** The body's Forward-carry section still names R9-CI-2b as the tests.yml destination. The tests.yml comment and #2024's lost pin still have no destination outside this PR.

## Why this is blocked

Step 10 of fix-review.md is the only failure. The code fix, the test, the mutation proof, the cause and the RCA all hold (see the RESULT lines below).

The body's Forward-carry says the false comment in `.github/workflows/tests.yml` ("One artifact per shard ..., each in its own subdirectory", lines 2580-2582) is left for the next PR that touches tests.yml, and that "R9-CI-2b (`fix/r9-ci-2b`) touches it". It does not:
- #2057 (`fix/r9-ci-2b`, af9936d8) changes 6 files, and tests.yml is not among them.
- #2059 (`fix/r9-ci-2b-carry`) changes 16 files, and tests.yml is not among them.
- No `.claude/workflows/*groups.json` brief and nothing under `dev/programme/` carries the correction (evidence/carry-check.txt).

So the finding exists only in this PR's body. The comment states the exact assumption that caused this defect, so leaving it is a trap for whoever next reads the autofix step.

The second carry, #2024's lost pin (`inputs.py:InputReader.read_flow_kg_s RETURN_DEL 69557675#2`, run 37769767377, artifact 11549410702), is also only in the body. I confirmed it is still absent at #2024's head c13216ce, where `git grep 69557675` over tests/ finds nothing. It needs a destination too: #2024's resume field or brief, or the delivery record.

Either of two remedies clears this block:
- (a) Write both carries into real destinations: the R9-CI-2b group brief, or the brief of whichever stage next owns tests.yml, plus #2024's resume. Then correct the body's claim that R9-CI-2b touches tests.yml.
- (b) Restore the comment edit that cef15d63 reverted, accept the FULL gate, and carry only the #2024 pin.

## RESULT lines

- **(1) Cause: confirmed from primary sources.**
  - `actions/download-artifact@37930b1c`, file `src/download-artifact.ts` lines 176-181: the action extracts to `resolvedPath` when `isSingleArtifactDownload || inputs.mergeMultiple || artifacts.length === 1`, and otherwise to `path.join(resolvedPath, artifact.name)` (evidence/download-artifact.ts).
  - Autofix job 113280999308 printed `Found 4 artifact(s)`, then `Filtering artifacts by pattern 'mutation-pins*'`, then 1 artifact `mutation-pins-1 (ID: 11547045879)`, extracted to `.../_temp/mutation-pins-shards`, then `shards merged: skip-no-measurement`.
  - Shard job 113265218115 printed `PIN KILLED: 4 pinned` and `measure: measured, 4 anchor(s)`, and uploaded artifact 11547045879.
  - I downloaded artifact 11547045879 to evidence/art/flat. It contains `status`=measured, `head`=de81043a31a3, and `pins.json` with 4 entries, all at the root, which is the layout `merge_pin_shards` on main cannot read.
- **(2) Configurations: my own harness**, evidence/harness/review_harness.py. The finding has no committed harness, so this one is mine, not the finder's. Its head-gate column copies apply_pins' `measured_at != head` test rather than calling apply_pins, because apply_pins writes the ledger.

  | case | main dcc77dd0 | head cef15d63 |
  |---|---|---|
  | real lone artifact, flat | skip-no-measurement | measured 4, would-apply |
  | real artifact in a subdirectory | measured 4 | measured 4 |
  | lone shard at a stale head | skip-no-measurement | measured 4, gate skip-head-moved (no pin) |
  | lone `skip-nothing-killed` / `skip-measure-failed` | skip-no-measurement | own status, 0 pins |
  | lone `measured` with corrupt pins.json | skip-no-measurement | skip-measure-failed |
  | lone shard with no status (crash) | skip-no-measurement | skip-no-measurement |
  | empty or missing root | skip-no-measurement | skip-no-measurement |
  | 3 shards | measured 2 | measured 2, unchanged |
  | 2 shards at mixed heads | skip-head-moved | skip-head-moved, unchanged |
  | 3 shards with one missing | measured 1 | measured 1, unchanged |

  - A stale head never pins.
  - A failed or crashed shard never pins.
  - A missing shard pins only what the shards that did report measured. This is main's existing multi-shard semantics: each pin is a real kill at the checked head, so it is partial but not false.
  - The fix newly reaches one case: N>1 shards where only one artifact uploaded. That lone artifact is now flattened and read, and the head gate still applies.
- **(3) Failing test first, the mutant and the null control**, all re-run by me with venv-ci Python 3.14.7 and `PYTHONPATH=tests/hastub tests/entities.py`:
  - head: `ALL 2212 ENTITY CHECKS PASSED`
  - mutant `shards = [r] if False else ...`: `1 of 2212 ENTITY CHECKS FAILED`, the pin-shards check, `one-artifact=skip-no-measurement,[]`
  - main's mutation_table.py with the branch's test: `1 of 2212`, same check, same value
  - After restoring, the tree is clean.
  - Null control: the multi-shard cases are unchanged at both ends, and run 37756428662 (skip-nothing-killed) stays skip-nothing-killed (evidence/harness/results.txt).
- **(4) #2024's job 113260740304** (run 37756428662, 8fb1b717): the mechanism was the same bug (`Found 3 artifact(s)`, `Total of 1`, `skip-no-measurement`). But artifact 11542577440 holds `skip-nothing-killed` with empty pins, so those were real survivors and no pin was lost. The body says this. #2024's other run, 37769767377 at c13216ce (artifact 11549410702), did lose 1 measured pin. The body says that too.
- **(5) RCA**, dev/audit/rca/R9-CI-2.md:
  - It names the cause and process state (c): the 8 proof runs had 3, 4 or 10 shards and none had 1.
  - It gives a cost test (2 lost repairs, 5 pins, in 5.3 h) and records a no-new-rule decision for the process.
  - Class reach holds: `pattern:` appears in only one download-artifact across the workflows, and every other download uses `name:`.
  - I re-derived the census independently with evidence/census/census.py, paced at 1 call per second. It found 10 rows, 1 of which is a cancelled autofix with no steps (run 37762874942, #2010, log 404). That leaves 9 that reached the merge: 6 single-shard, all `skip-no-measurement`, and 3 multi-shard (7, 2, 10), all measured. This matches the body's 9, 6 and 3. API failures: 1, the cancelled job's log.
- **(6) CI at the head** (check-runs API):
  - 19 success, 14 skipped, 1 neutral.
  - Red: `delivery-status` (UNCHECKED, 0 overdue) and `nightly-status` (main's nightly 37753990323). Neither is this PR's: the diff reaches neither, per defect-root-cause.md. So the body's "Red checks: none" stands.
  - `mutation` is green. The diff writes no `custom_components/` line, so no mutant was drawn.
  - **Settled at 93184bb0** (check-runs API, evidence/checks-93184bb0.txt): 21 success and 14 skipped.
    - `closures`, `fast (3.14)`, `mutation`, both `pr-contract`, and all three `Analyze` jobs are green.
    - `coverage` was still in progress. It is not a required context, and the orchestrator said not to wait on it.
    - Red: `delivery-status` and `nightly-status`. `delivery-status` (job 113344301733) printed `DELIVERY STATUS UNCHECKED — 77 rowed, 0 pending, 0 overdue`, so this PR's own row counts and nothing is overdue. `nightly-status` reports main's nightly.
    - The body now answers both reds by name, so step 11 is satisfied.
  - The earlier range commits e7e6f0ef and 9e181f5e have no check-runs; they were never pushed as heads.
- **Version and claims:** the diff touches neither VERSION, the manifest, RELEASE_NOTES nor either claim file.
- **Step 14:** the diff moves no metric. No budget, closures.json or ledger change.
- **Code ownership:** the head's diff does not touch the workflow (cef15d63 reverted it). tests/ and dev/audit/ are the only paths changed.
