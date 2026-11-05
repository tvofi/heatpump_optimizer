R10-HANDOFF-PATH part 1 (triage `dev/programme/triage/s6-batch121.md#P386`, the owner's directive of 2026-11-04): a fixer's prepr is not repeated at open or update. Part 1 is P386's carry with roster carries 3 and 4 and no other; one checkout per pull request, exit 75, the retry and the `open_driver` repairs are part 2. Carry 9 is answered by #3089's merge.

- **The receipt.** `tools/pr/prepr.sh`'s `receipt_write`: a run with a body that ends rc=0 writes `<HEAD sha> <tree sha>` to `hpo-prepr-receipt` in the checkout's git dir. The main flow removes an earlier receipt first, so a failing run leaves none. `--body-check` and `--fill-red` exit before the main flow and write none. A run that sets any `PREPR_SKIP_*` except `PREPR_SKIP_CLOSURES` writes none, and neither does a run over a dirty tree.
- **The trailer.** In `tools/audit/seat/body_push.sh`, `prepr_trailer` adds `Prepr: <sha> <tree>` to the `handoff-body/<topic>` commit, under `Code:`. It does so only when the receipt's sha is the handoff's code head and its tree is that head's tree. Otherwise one line says that no trailer was written.
- **The verdict.** `tools/pr/app_push.sh --reuse`'s `reuse_verdict` sits beside `recarry_verdict` and `row_only_verdict` and fails closed. Every one of these must hold:
  - (a) the tip of `handoff-body/<topic>` carries exactly one `Prepr: C T` trailer;
  - (b) C's tree is T;
  - (c) C is in HEAD, and C merges cleanly with the live head and then with the origin/main commit HEAD holds, which is on main's first-parent chain;
  - (d) HEAD's tree is that merge's tree, or that tree plus this pull request's own row;
  - (e) HEAD carries no commit beyond C, the live head and main except that one row commit.

  When the verdict holds, prepr runs under `PREPR_SKIP_CODE=C`, and then `row_only_checks` runs. Otherwise the full prepr runs, exactly as today. One `app_push: REUSE:` line names which path ran and why. `open_pr.sh` p1 asks for `--reuse`. `update_pr.sh` asks for `--reuse` on every head that is not a row-only push.
- **What still runs, with no heavy slot.** Under `PREPR_SKIP_CODE`, prepr takes no slot. It still runs transport, ancestry reds, ref privacy, temp paths, no version edit, claim files, claims hygiene, layout guard, preflight, pr-body, figures, carry, unpinned sites and push order. `merged_steps` adds two checks on HEAD merged with origin/main: `tests/structure.py` (carry 4, in every run) and ci predict (in this mode only). The merged tree is HEAD itself when HEAD already holds main; otherwise it is the `merge-tree` result. The skip is not keyed to main standing still under a closure (`s6-batch95.md#P346`).

**Each step's input, checked before dropping it** (read from `tools/pr/prepr.sh`'s main flow). The triage's split was a reading, and the input check differs from it in four places:
- **transport: kept.** Not listed by the triage, but it reads the commits since the merge base, which the merge and the row add, and it costs 0.0 s.
- **push order: kept.** Not listed either; it reads the remote head ref.
- **claims register: dropped.** Not listed either. It reads `BASE...HEAD` paths against `CLAIMS_READS`, and that is the code's diff alone.
- **gate mode and diff mutants: dropped.** The first prints the scope of the code's diff. The second is report-only, and `MUTANT_CMD` is code-keyed.

The other drops read the code alone:
- `policy_lint`, `rules_sync`, `fragments`, `hooks`, `codeowners_gap`, `brief_lint`, `field coverage`, `register check`, `pinned graders`, `self-test`, `wave-script`, `no-copies` and `throwaway git` read the tree's corpus and its own scripts. Main's half of that corpus passed on main.
- `agreement lane` reads the first-parent subjects since the tag. The only new ones are the open's or update's automatic merge and the row, both shapes the full prepr already passes at every open today.
- `closures` is already `PREPR_SKIP_CLOSURES` at every open.

**Merge resolution.** The open refused this head (`91a75ed8`): `merging origin/main into 91a75ed8 conflicts` in `tools/pr/prepr.sh`, because main had moved by 23 commits. Main's three commits to `prepr.sh` since `af941ad4` are `8f6f0ea2f`, `18481fd52` and `1584530f3`. They add the lazy `take_slot`, `closures_owes_slot` and the early `## Head` arm, step 1a3 (P208). The change over the reviewed content is a merge of origin/main, `c0b082bc`, with one conflict, in `tools/pr/prepr.sh`. It is resolved with both sides kept. Main's step 1a3 runs first, right after the ancestry-reds arm 1a2: it is keyed to the body, so it also runs under `PREPR_SKIP_CODE`. Next come this branch's recorder cache and its `PREPR_SKIP_CODE` gate. Main's five lazy `take_slot` calls are in these steps: mutants, field coverage, self-test, closures and diff mutants. Mutants and field coverage are in the first code-keyed group, self-test in the second and diff mutants in the third. Closures is behind `elif [ -n "${REUSE:-}" ]`. So a reuse run still defines and takes no slot. No other file of this diff changed on main since `af941ad4`: `git diff af941ad4a origin/main -- tools/pr/app_push.sh tools/audit/seat/body_push.sh tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh` is empty.

Alternatives:
- A separate check list in `app_push.sh` would have duplicated prepr's steps beside their owner. It lost to one mode of prepr's own flow.
- Reading the receipt from the body's prose is what the ruling had to do, and prose cannot be verified. A trailer on the body commit carries a sha and a tree that can be checked.

**Repair round 2** (the first fix review blocked `794fe6a7` on two defects, each letting a receipt skip a check the body says still runs):
- **The main flow's `merged_steps` call is pinned.** The `(a)` arm's real `PREPR_SKIP_CODE` prepr now runs with a body and asserts that one `merged structure` line and one `ci predict` line appear. Under `PREPR_SKIP_CODE` that call is the only ci predict and the only `tests/structure.py` on HEAD merged with main, and the function-level arms (d) and (e) could not see it deleted.
- **The receipt names the HEAD the run started on.** `receipt_line` reads `<HEAD sha> <tree sha>` once, where the main flow starts (`RUN_START`, right after the early receipt removal). `receipt_write` gets it as a third argument and writes that line, never a fresh read. When HEAD or its tree differ at the end, it refuses through `step "receipt" 1`, so the run ends rc=1 and writes no receipt. When no start was read, it writes none. A commit landing mid-run is therefore code the receipt never claims.
- **The five follow-ups, one row each, in the self-tests already touched:** reuse_verdict's first-parent arm of (c) (real git: HEAD holding a side commit main merged); two `Prepr:` trailers; `row_only_checks` after the reduced prepr under `--reuse` (a copy whose `reuse_verdict` is a stub that reuses, so the wiring past a reusing verdict runs: prepr under `PREPR_SKIP_CODE`, then the body contract and the carry check, and a contract refusal stops the push); the early receipt removal (the `(a)` run plants a stale receipt and asserts it is gone); and body_push.sh's sha comparison (a receipt whose tree is the head's but whose sha is not).
- The unsigned-receipt finding stays as it is: P386 dismissed it.

Alternatives for the starting HEAD:
- Re-reading HEAD at the end and comparing it to `## Head` alone was rejected. A seat that moves both the code and the body mid-run, which is the reviewer's real run 2, passes that check.
- Taking a lock on HEAD for the length of the run was rejected. It is heavier, and it would still need the same comparison at the end.
- Writing the start line, after checking that it is unchanged, makes the receipt the measured HEAD by construction.

## Head

`acd20e42a51fc981e37fe2e45eb72e523dc965f2`. It merges origin/main `8364e624` (stamped 2026-11-05T04:33Z) into the repair commits on the reviewed head `794fe6a7`, through three clean merges: `8ddab317`, `662b2966`, then `8364e624`. Main kept moving during the take, and a container restart stopped one prepr run. `git diff --stat 794fe6a7...origin/main -- tools/pr tools/audit/seat` is empty, so main's commits reach none of this diff's files. Every figure below was re-taken at this head after the last merge. The full prepr at this head is the receipt this body's trailer carries: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, whose passing run's receipt is this body commit's `Prepr:` trailer (body_push.sh writes one only from a receipt at this code head with its tree).

## Mutation proof

Each mutant was applied to a throwaway worktree of the repair head, the file's own self-test was run, and the worktree was removed. `git status --short` in the seat's worktree was empty after each mutant. Every row named below exists only in this repair.
- **P1, the main flow's `merged_steps "${1:-}" "$UNPINNED_SITES"` call replaced by `:`** (the reviewer's expression). `prepr.sh --self-test`: `508 passed, 1 failed`, `FAIL (a) and runs tests/structure.py and ci predict on HEAD merged with main, once each (got 00, wanted 11)`.
- **PH, the fix's start check `[ "$3" = "$(receipt_line)" ]` replaced by `true`**: `508 passed, 1 failed`, `FAIL receipt: HEAD moved past the run's start (a commit landing mid-run) is refused and writes none (got 0|61a7ddbb… 7b648a91…, wanted 1|)`.
- **P3, the early `rm -f "$(receipt_file)"` replaced by `:`**: `508 passed, 1 failed`, `FAIL (a) a run with a body removes an earlier receipt first, so one that writes none leaves none (got left, wanted )`.
- **P6, body_push.sh `[ "$s" = "$2" ]` weakened to `[ -n "$s" ]`**: `508 passed, 1 failed`, `FAIL body_push: a receipt whose tree is the head's but whose sha is not gives none`.
- **M2b, reuse_verdict's `grep -x "$mb"` on the first-parent list replaced by `{ cat >/dev/null; true; }`**. `app_push.sh --self-test`: `225 checks, 1 failed`, `FAIL real git (c): HEAD holding a main commit off main's first-parent chain runs the full prepr (got '0', want '1')`.
- **M5, the trailer count `= 1` relaxed to `-ge 1`**: `225 checks, 1 failed`, `FAIL real git (a): two Prepr: trailers, though each is the receipt, run the full prepr`.
- **M6, `[ "$reused" = 0 ] || row_only_checks` replaced by `true || row_only_checks`**: `225 checks, 3 failed`. The failures are the wiring rows `and prepr ran under PREPR_SKIP_CODE, then the body contract and the carry check (got '100', want '111')`, `a body the contract refuses refuses after the reduced prepr`, and `and nothing was minted or pushed (got '15', want '00')`. Re-run after the stub's spelling commit, with the same result.

The failing test came first. The two start-HEAD rows were added before the fix and ran red against the unfixed `receipt_write`: `507 passed, 2 failed`, `FAIL receipt: HEAD moved past the run's start … (got 0|7f9d0afa… b365d581…, wanted 1|)` and `FAIL receipt: a run whose start HEAD was not read writes none`. Once the fix was in, the result was `509 passed, 0 failed`.

## Null control

- **Start HEAD.** The first receipt row, a run whose start line is the unmoved HEAD, writes `<sha> <tree>`. The moved-HEAD row differs from it by one commit and is refused.
- **The reviewer's harness at both ends** (`ev/midrun.sh` from probe/rev-3221-33fa557d, sha1 `76abd37d…`). At `794fe6a7` it prints `RESULT: receipt names a HEAD the run did not start on`. At the head it prints `skip receipt: the run's starting HEAD was not read, so none written`. That is the fail-closed arm: the harness calls with the old two arguments, and its RESULT line, keyed to a written receipt, cannot read the refusal.
- **The ported companion** (`midrun3.sh`, sha1 `40f6b8fc…`, scratch). It passes the start line as the main flow now does and has a null arm:
  - At `794fe6a7`, moved: `receipt=b34397ef…`, `RESULT: receipt names a HEAD the run did not measure`.
  - At `794fe6a7`, null: `RESULT: receipt names the measured HEAD`.
  - At the head, moved: `REFUSE receipt: HEAD is b34397efd791, not b648dc7d9abe where this run started …`, `RESULT: no receipt`.
  - At the head, null: `RESULT: receipt names the measured HEAD`.
- **Planted receipts** (`ev/plant.sh`, sha1 `7e3063ae…`, against the production `reuse_verdict`). At both `794fe6a7` and the head, all nine rows PASS: the null and R8 reuse; R1 to R7 run the full prepr.
- **Each new pin's passing twin.**
  - The `(a)` rows' twin is the unmutated run.
  - The R7 row's twin is the single-trailer receipt restored just before it, which reuses.
  - The R6 row's twin is every earlier reusing real-git row.
  - The M6 refusal's twin is `ureused`, the same stub without `node-fails`, which pushes.

## Figures

All figures were taken at the head unless stated otherwise.
- `bash tools/pr/prepr.sh --self-test`: `509 passed, 0 failed`. That is 504 at `794fe6a7`, plus 5 rows: 2 start-HEAD rows, 1 sha-only trailer row, and 2 `(a)` rows.
- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 225 checks, 0 failed`. That is 219, plus 6 rows: 1 two-trailer row, 1 off-first-parent row, and 4 wiring rows.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- The claim files, VERSION, RELEASE_NOTES.md and the manifest are untouched: `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/*/manifest.json` exits 0.
- Toolchain: `cloud-setup.sh --check` gives `OK`. numpy is 2.5.4 and scipy is 1.18.1, matching `tests/requirements-ci.txt`. No golden was run, because this diff touches no solver.
- The kept-step wall time under `PREPR_SKIP_CODE` (27 s at `91a75ed8`) was not re-taken. The repair adds no step to that set: it adds one `git rev-parse` pair at the start and one at the end.

## Red checks

none. The head `acd20e42a51fc981e37fe2e45eb72e523dc965f2` has no check run: handoff refs trigger no CI. The reviewed head `794fe6a7`'s red `gate` was a cancelled job, not a failure, per the review. The base is `8364e624`. This diff reaches no workflow file and no `tools/ci` path.

## Forward-carry

none

## Friction

none
