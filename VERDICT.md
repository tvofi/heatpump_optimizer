Fix review: blocked 53f24912dee67629b3bc383f91031627c995d520 body-stale: the code clears round 3's block (F13 now fails a behavioural row, sweep 128 mutants 0 survivors, carry on the roster and on main) but the body still describes 37cffb09 and never mentions the status-line change, its figures (43 rows, 119 mutants, 8 rules, 10 equivalents) are not the head's, and it names roster SHA 306a96d5f where the carry is absent

bus-nonce: 2b2b388e59fd87b772a395b119b55a77

Round: fourth review (round 4), of cloud fixer round fix2589z on round 3's block at `74a18df9`. By `fix-review.md`'s last line, the next block owes `fixer.md`'s re-cut, not a repair. The block below is about the body only. The code at this head passed every check I ran.

How I worked:
- I reviewed from detached worktrees at `53f24912dee67629b3bc383f91031627c995d520` (the head) and at `74a18df941939cd87c11280ec216531148015b46` (round 3's head, the other end).
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.
- The fixer's authored delta since `74a18df9` is `9b9770b34` alone. It changes `gh_transient` (lines 121-127) and the self-test table in `tools/pr/app_approve.sh`, and adds the `copy` rule to `dev/audit/harnesses/r10_gh_read_retry_mutants.py`. `53f24912` merges it, then merges origin/main `b787c7d45`.
- The finder's harness is round 2's runner and list (`origin/review/2589:evidence/finder-runner.py`), copied as `ev/finder-runner.py`.
  - At the head, two of its search strings no longer exist, because the fix renamed `code` to `status` and the sed now prints `\2 &`.
  - I adapted exactly those two: X6's `"$1"` became `"$status"`, and X13's `\2/p` became `\2 &/p`. The adapted copy is `ev/finder-runner-head-adapted.py`, and the change is the reviewer's own.
- The fresh mutants are my own instrument, `ev/fresh-head-runner.py`, built in that runner's shape.

## Block

1. **body-stale: the PR body describes `37cffb09`, not this head.**
   - The body says "Every figure below was taken at `37cffb09`". Since then, `9b9770b34` changed the classifier.
   - The body was last written at `handoff-body/r10-fly-gh-read-retry` `fd387f479` (04:41:02Z). The code commit is `9b9770b34` (06:03:51Z), later. Only the `## Head` paragraph was patched to name `53f24912`.
   - What is stale (`ev/body-vs-head.txt`):
     - **The change itself is not described.** The body says a 403 is retried "with the phrase `secondary rate limit` in any case". At the head, the phrase is read on the deciding status line only (`status=... \2 &/p | tail -1`; `403) printf '%s\n' "$status" | grep -qi ...`). No section names round 3's block or how it was cleared. The body still says "This round clears the review of `6e4d2b5c`".
     - **"Three rows encode design choices"**: the head's self-test comment says "Four design choices are rows", and the fourth is the status-line-only phrase.
     - **"a table of 43 inputs"**: the head has 48 rows. The per-alternative table is also off (403 is 2/3 at the head, not 1/1; `secondary rate limit` 2/4, not 1/4; `^Get` 3/4, not 2/4), and its sed key is `\2 &/p`, not `\2/p` (`ev/figs-rows.txt`).
     - **The sweep**: the body says 119 mutants (89 + 30), "eight rules", 109 killed and 10 equivalent. At the head it is `mutants=128 killed=116 equivalent=12 survivors=0`, with a ninth rule, `copy` (`ev/sweep-head-53f24912.txt`). The two new EQUIVALENT entries (`ONELINE`) are not in the body's list of equivalents.
     - **The forward-carry**: the body says "No roster write was made, so there is no roster SHA to name" and cites `306a96d5f`, where the carry is absent. The carry was written at `5620151813e03a5916c375554dd57c977f6d8097` (`ev/roster-carry.txt`). Step 10 opens the carry "at the body's roster SHA", and round 3 asked for that SHA to be named in the body.
     - **`## Red checks`** stops at `37cffb09` ("not yet run"). The head has 49 check runs: 33 success, 16 skipped, 0 red.
   - **Fix (body only; no code change needed):**
     - Describe `9b9770b34`'s status-line rule and the `copy` rule, and say how round 3's block is cleared.
     - Re-take the figures at the code head.
     - Name the roster carry SHA `5620151813e0`.
     - Bring `## Red checks` to the head.
   - Every figure needed is re-derived in `ev/`. A re-review of an unmoved head needs only to diff the body against `ev/body-vs-head.txt`.

## Findings

- G7 (`\2 &/p` -> `\2 \1/p` in the status sed) is killed only by the table-key precondition `(the table keys exactly the alternatives gh_transient's source holds)` (`ev/fresh-mutants-head.txt`). By the harness's own rule that reads SURVIVED, and no sweep rule rewrites a sed replacement.
  - It is behaviourally equivalent on what gh prints. `\1` is the message from after `gh: ` up to the `(` before `HTTP`, and the phrase can only sit there. When group 1 is absent (`gh: HTTP 403`), neither copy holds the phrase.
  - Carry: dismissed: \1 holds the whole message the phrase can occur in, so the 403 branch classifies identically on every gh status line

## Evidence

- **Round 3's block 1 (F13) is cleared at this head.**
  - F13 at `74a18df9` (`403) printf "$1" | tail -1 | grep`): `225 checks, 0 failed`, rc=0. It survives, re-derived (`ev/f13-prev-74a18df9.txt`).
  - At the head, the corresponding mutants are killed, each by `FAIL every alternative's inputs and near-misses classify as the table needs (production gh_transient)`. This is a behavioural check, not a source-text precondition (`ev/fresh-mutants-head.txt`):
    - G1, the F13 shape (`"$status"` -> `"$1" | tail -1`): KILLED (got '2').
    - G2 (`"$1" | head -1`): KILLED (got '1').
    - G3 (revert to `"$1"`): KILLED (got '2').
  - G4 and G5 (`"$status" | tail -1` and `| head -1`) survive. They are the harness's `ONELINE` EQUIVALENT entries (M53, M54), which is sound: `status` is assigned through `| tail -1`, so it is one line.
- **Null control on the three new two-line 403 rows** (`ev/nullctl-new-rows.txt`, script `ev/nullctl.sh`):
  - Deleting any one row leaves the unmutated self-test at `225 checks, 0 failed`.
  - With each row deleted, G3, G1 and G2 stay killed, with one exception: deleting `403 refuse gh: You have exceeded a secondary rate limit.\ngh: Forbidden (HTTP 403)` lets `"$1" | head -1` pass (`225 checks, 0 failed`).
  - So each row is load-bearing for at least one copy-of-stderr mutant, and that row is the sole killer of the `head -1` copy.
- **Fresh one-line mutants of every touched line and its readers** (`ev/fresh-mutants-head.txt`). G0 null: `225 checks, 0 failed`. Every other G is KILLED (failed checks in brackets):
  - Status sed: G6 `\2 &`->`\2` (5), G10 `tail -1`->`head -1` (1), G11 tail deleted (1), G20 `"$1" | tail -1 | sed` (3), G21 `| head -1 | sed` (1).
  - Case reader: G8 `${status%% *}`->`$status` (18), G9 `${status% *}` (18).
  - Phrase: G12 `-qiw` (1, the `limits` row), G13 `-q` (1), G14 `limit\.` (2), G15 `rate limit` (2), G16 every 403 transient (5).
  - Transport copy: G17 `"$1"`->`"$status"` (8), G18 `| tail -1` (1), G19 `| head -1` (1).
  - Retry and backoff arms: G22 budget unbounded (6), G23 READ_TRIES 3 (7), G24 READ_TRIES 5 (5), G25 READ_SLEEP 1 (3), G26 x2 (1), G27 no backoff (1), G28 sleep deleted (2), G29 drop `!` (33), G30 classify GH_ERR (2).
  - Labels: G31 `5??` only (6), G32 `40?` (2).
  - G7 is the only precondition-only kill (see Findings).
- **RESULT finder's harness at both ends:**
  - `53f24912`: X0 `225 checks, 0 failed`; 24 KILLED, 0 SURVIVED (`ev/finder-harness-head-53f24912.txt`, adapted runner).
  - `74a18df9`: X0 `225 checks, 0 failed`; 24 KILLED, 0 SURVIVED (`ev/finder-harness-prev-74a18df9.txt`, unadapted runner).
  - The harness is flat at both ends, as round 3 found. It never held F13, which is why the fresh mutants above are the discriminating instrument.
- **RESULT sweep (the fixer's harness, evidence only) at the head**: `python3 dev/audit/harnesses/r10_gh_read_retry_mutants.py --jobs 4` gives `RESULT mutants=128 killed=116 equivalent=12 survivors=0`, rc=0, M0 `NULL-OK` (`ev/sweep-head-53f24912.txt`).
  - The new `copy` rule generates M26-M28, M53-M55 and M72-M74.
  - All are killed except M53 and M54 (ONELINE equivalent). M55 is the revert to `"$1"`.
  - This settles the sweep gap round 3 named.
- **The "225 checks" figure, re-counted**:
  - `bash tools/pr/app_approve.sh --self-test` gives `225 checks, 0 failed`, rc=0, at both `53f24912` and `74a18df9` (`ev/selftest-both.txt`).
  - It is unchanged because the five added rows go through one aggregate table check.
  - The null control is every G/X/M0 null line above, each at 225/0.
- **Round 3's block 2 (carry-missing) is cleared in the tree.**
  - The fenced text was applied verbatim at `5620151813e03a5916c375554dd57c977f6d8097` (`roster_edit append-carry R10-FLY-GH-READ-RETRY`). It is on `origin/handoff/audit-r10-roster` at `e5d5c508465f` as the group's third carry item (`ev/roster-carry.txt`).
  - Item (d) names "which copy of stderr is classified", and the head's `copy` rule implements it.
  - main has it: roster PR #2598 merged at 2026-10-22T08:09:18Z, and origin/main `01cf1398a9cf` holds three carry items for the group. Main's tip at the head's merge base, `b787c7d45`, held two.
  - So pr-contract's in-tree carry_audit reads a roster that has the item. Both pr-contract runs at the head were green in any case (jobs 119690871830 and 119691102440), because the body's `Carry:` items are `dismissed`, with no group destination.
- **carry_audit**: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body ev/pr-body.md` gives `1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`. It gives the same with `--roster-ref origin/main`, at both `b787c7d4` and `01cf1398`, and with no `--roster-ref` (`ev/carry-audit.txt`).
- **CI at the head** (`ev/checkruns-head.tsv`, from the commit's check-runs API, re-read at 07:48Z after every run concluded): 49 runs, 33 success and 16 skipped, none red, so there is no external rate-limit or unreachable red to classify.
  - `closures`, `fast (3.14)`, `coverage`, `mutation`, `pr-contract` (x2), `delivery-status` and `nightly-status` are all success.
  - `ev/checkruns-range.tsv`: `74a18df9`, `9b9770b3`, `841b2fea` and `37cffb09` show no non-success run.
  - The `mutation` lane is success, but this diff writes no `custom_components` production line, so it drew no mutant from it.
- **Merge** (`ev/merge-tree.txt`): `git merge-tree --write-tree origin/main 53f24912...` is rc=0, clean:
  - against `b787c7d45` (an ancestor of the head), tree `3d62282d`;
  - against `01cf1398a9cf` (re-read after #2598 merged), tree `62ceb650`. `LEDGER-MERGE: resolved tests/closures.json` there is the ledger driver merging `inert_reads` as a set, not a conflict.
- **Figures re-derived at the head** (`ev/figures.txt`, `ev/figs-alts.txt`):
  - ALTS prints 8 lines (9 with `default`).
  - `closure.py select` gives `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`.
  - NONE-TOUCHED (VERSION, manifest, notes, claim files).
  - `STRUCTURE RATCHET PASSED`.
  - `policy_lint --budgets` rc=0.
  - `--pr-body`: `PR-BODY: 0 error(s)`.
  - `tmp_paths: 0 refused, 0 stale allow entries`.
  - `CI PREDICT: no closures or fast red predicted against b787c7d45951`.
  - The seams awk prints 10 lines.
- **Figures I did not re-take**: `score.py --diff` (`dS +0.0000 NULL`), the `run_always` lines and `entities.py`'s `1 of 2382`. CI's green `arch-score`, `closures` and `fast` runs at the head are cited instead, per step 11.
- **Head re-read before return**: `refs/heads/fix/r10-fly-gh-read-retry` is still `53f24912dee67629b3bc383f91031627c995d520`, and the PR body is unchanged since it was first read (`ev/pr-body.md`).
