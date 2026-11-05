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

**Repair round 3.** The second fix review blocked `20d5aab0` on two defects:
- **`governance / instrument-self-tests` was red: pr_args.sh's fixtures had not been updated for the `--reuse` code push.** `bash tools/audit/seat/pr_args.sh --self-test` gave `172 checks, 19 failed` at `20d5aab0`, and `0 failed` at base `8364e624`. There were three causes:
  - The stubs shifted only `--row-only`. Under `--reuse` their `$2` was the repository, not the worktree, so the stub pushes failed. That accounts for the race, row-close, kept-worktree and lock rows.
  - The open row and the two update null controls still expected no flag on the code push.
  - The pusher census found two new files naming `app_push.sh` with no disposition: comments in `body_push.sh` and `prepr.sh`.

  The repair:
  - Every stub drops either mode flag.
  - The open row now asserts `--reuse` on the code push and `--row-only` on the row push. Both update null controls assert `--reuse`, never `--row-only`. They stay meaningful: each still separates a new-code head from a row-only head, which `mut:rowonly` crosses.
  - Each runner now carries `--reuse` on a line of its own, so a mutant can delete it without deleting the push. In `open_pr.sh` that is `RU=--reuse  # mut:opreuse`, and the push takes `${RU-}`. Before, the marker sat on the whole p1 push line. In `update_pr.sh` it is `[ -n "$RO" ] || RO=--reuse  # mut:updreuse`, placed after the restored `RO=""; … || RO=--row-only  # mut:rowonly`. Each mutant has a row that kills it.
  - The census gives both files `mention` entries.
- **The mutation-vacuous condition (e).** One real-git row in app_push.sh's reuse block has the shape of the reviewer's F9: the clean merge of C and main plus two commits that net to no tree change. It asserts (e)'s refusal, `HEAD carries 2 commit(s) beyond code …`. The same head reset under those two commits reuses again, which is its null control.

Alternatives for (1):
- Reverting the code push to no flag would have restored the old fixtures and dropped P386's reuse at open and update. That is the feature this PR exists for.
- Keeping the marker on the whole push line would leave a mutant that deletes the push itself. The run would then stop at `pr_wait` for a reason other than the missing flag, which is a vacuous pin.

## Head

`533b00b37c7f02896c7d5a14926aa97b947d1b2a`. It is the reviewed head `20d5aab0` with these commits added:
- four merges of origin/main, all clean: `9514f979` (main `6777ec33`), `34a42f91` (main `3ec5178c`, merged 2026-11-05T07:27Z), `6a85d1d2` (main `dad3178d`, merged 2026-11-05T07:58Z) and `533b00b3` (main `79f765e6`, merged 2026-11-05T08:24Z);
- the two repair commits: `687eb9a6` (app_push.sh) and `5b3de631` (pr_args.sh, open_pr.sh and update_pr.sh);
- `fff00030`, a merge-follow-up commit.

Neither `dad3178d` nor `79f765e6` reaches a path under `tools/`, `.claude/` or `.github/`: `git diff --quiet fff00030 533b00b3 -- tools .claude .github` exits 0. So the self-tests of `app_push.sh` and `pr_args.sh`, taken at `fff00030`, were not re-run. Main's only commit to this diff's files is `3ec5178c`'s step 3e2 in `tools/pr/prepr.sh`, the machinery ratchet. `git diff --stat 6777ec33 3ec5178c -- tools/pr/prepr.sh tools/pr/app_push.sh tools/audit/seat/body_push.sh tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh tools/audit/seat/pr_args.sh` prints only `tools/pr/prepr.sh | 9 +`, and `git diff --stat 8364e624 6777ec33` over the same files prints nothing.

**Merge follow-up.** Git placed the new step automatically, after `codeowners_gap`, inside the first code-keyed group, which `PREPR_SKIP_CODE` skips. That placement is kept. The ratchet reads the code's own history against main, as `codeowners_gap` beside it reads the code's corpus. CI's `policy-docs` runs it on every pull request whatever prepr did. `fff00030` adds `machinery ratchet` to that group's `say skip "code-keyed steps"` line, so a reuse run names every step it skips. A full run executes the step unchanged.

Every figure below was taken at this head unless it says otherwise. The full prepr at this head is the receipt this body's trailer carries: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`. Its passing run's receipt is this body commit's `Prepr:` trailer, and body_push.sh writes a trailer only from a receipt at this code head with its tree.

## Mutation proof

Round 3. Each mutant ran in a throwaway worktree, apart from the seat's own.
- **A5, reuse_verdict (e)'s `[ "$n" = 0 ] ||` replaced by `true ||`** (the reviewer's expression; app_push.sh line 313). `app_push.sh --self-test` gives `227 checks, 1 failed`, `FAIL real git (e): two tree-neutral commits past the clean merge run the full prepr (got '0', want '1')`. The unmutated head gives `227 checks, 0 failed`. The row came first and ran against the mutant before it was run on the unmutated head.
- **`mut:opreuse`, open_pr.sh's `RU=--reuse` line deleted.** The pr_args row `mutant mut:opreuse (its line deleted): the code push asks no reuse verdict, so it runs the full prepr` reads `ok`: the stub's first argv line starts `tvofi/heatpump_optimizer`. The same row without the mutant, `open_pr: its row push passes --row-only, and its code push --reuse, never --row-only`, also reads `ok`.
- **`mut:updreuse`, update_pr.sh's `RO=--reuse` line deleted.** The row `mutant mut:updreuse (its line deleted): a code sha the head lacks asks no reuse verdict, so its push runs the full prepr` reads `ok`.
- **`mut:rowonly`** now crosses into `--reuse`: `code sha '-' asks for --reuse, not --row-only` reads `ok`.
- **The repair against the red it answers.** At `20d5aab0` the pr_args self-test gave `172 checks, 19 failed` (the reviewer's `ev/pr_args_selftest.head.log`). At this head it gives `174 checks, 0 failed`. The two added rows are the opreuse and updreuse mutants.

Round 2's mutants were taken at `acd20e42`, and they are not re-taken here. None of their files moved since then except app_push.sh's seven-line row above. They are:
- P1, PH, P3 and P6 in `prepr.sh --self-test`, each `508 passed, 1 failed`;
- M2b and M5 in app_push.sh's self-test, each one row failed;
- M6, with three rows failed.

The review found P1 killed. A6 (app_push.sh line 564) was dismissed as equivalent.

## Null control

- **(e).** The row that follows the F9 row is `real git: the clean merge without them reuses (the (e) arm's null control)`. It is the same receipt and the same head without the two tree-neutral commits, and it reads `ok` both at the head and under A5. So the F9 row fails under A5 because of (e), not because of the fixture.
- **The flags.** Two pairs separate the assertions:
  - The open's row push asserts `--row-only` and its code push asserts `--reuse`.
  - `update_pr: code sha '-' asks app_push.sh for --row-only` (`ok`) and `a code sha the head lacks … asks for --reuse` (`ok`) are the same fixture with one argument changed.

  Each of the two flag mutants turns exactly its own row.
- Round 2's harnesses (`ev/midrun.sh`, `midrun3.sh`, `ev/plant.sh`) read files this round leaves unchanged except app_push.sh's self-test block, so they were not re-run.

## Figures

All figures were taken at `533b00b3` unless a figure names a commit. The two seat self-tests were taken at `fff00030`, whose `tools/` tree is identical.
- `bash tools/audit/seat/pr_args.sh --self-test`: `pr_args self-test: 174 checks, 0 failed`. That is 172 plus 2 rows: the `mut:opreuse` and `mut:updreuse` mutants.
- `bash tools/audit/seat/open_pr.sh --self-test` and `bash tools/audit/seat/update_pr.sh --self-test` each print `pr_args self-test: 174 checks, 0 failed`, rc=0. They are the same suite, which `instrument-self-tests` runs three times.
- `bash tools/audit/seat/pr_args.sh --pushers`: no `OPEN` line.
- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 227 checks, 0 failed`. That is 225 plus 2 rows: F9 and its null control.
- `bash tools/pr/prepr.sh --self-test`: `509 passed, 0 failed`.
- `body_push.sh` has no `--self-test`. Its trailer is pinned inside prepr.sh's self-test, which passes.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- The claim files, VERSION, RELEASE_NOTES.md and the manifest are untouched: `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/*/manifest.json` exits 0.
- Toolchain: `cloud-setup.sh --check` gives `OK`. numpy is 2.5.4 and scipy is 1.18.1, matching `tests/requirements-ci.txt`. No golden was run, because this diff touches no solver.
- The kept-step wall time under `PREPR_SKIP_CODE` (27 s at `91a75ed8`) was not re-taken.

## Red checks

The head `533b00b3` has no check run yet: handoff refs trigger no CI. The PR head `20d5aab0` had these concluded reds, from the review's `ev/nongreen_checks.txt`, which covers all check-run pages:
- **`governance / instrument-self-tests`** (127067016573) was this diff's red: pr_args.sh's self-test gave `172 checks, 19 failed`. It is repaired above, and the step now gives `174 checks, 0 failed`.
  - Cheaper detector: that same self-test, run locally on the seat scripts the diff edits, about 5 minutes. It existed and was not run before the round-2 handoff: root-cause-detectable. This round runs it for every seat script the diff edits.
  - The countermeasure is in `fixer.md` step 5 already: run what CI runs for every edited instrument.
- **`pr-contract / pr-contract`** (127077198867, 127077966989, 127078917945) refused the body because `## Red checks` did not name the red above. This body names it.
- **`gate`** (127077456468, 127078249806, 127079147825) failed on the same red-checks answer as pr-contract.
- **`governance / delivery-status`** (127067016566): the OVERDUE rows are #3174, #3091, #3089 and #3192, not this PR's row. It is not this diff's red.
- **`tests / nightly-status`** (127067016664): this diff does not reach it. It is not this diff's red.

## Forward-carry

none

## Friction

none
