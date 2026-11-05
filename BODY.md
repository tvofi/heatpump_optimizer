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

## Head

`1acf58eb7c1fc4fe29e7e7098172db63f9bb9922`. The resolution merge, `6e652a3e`, merges origin/main `c0b082bc` into the reviewed head `91a75ed8` and resolves the one conflict in `tools/pr/prepr.sh` as described above. A full prepr ran clean at `6e652a3e`, from 00:40 to 01:01 UTC. Main then moved by one commit, `499162c8` (`ci: record nightly kills`). This head merges that commit, stamped 2026-11-05T01:02Z. The merge was clean and reaches none of `tools/pr` or `tools/audit/seat`: `git diff --stat HEAD~1 HEAD -- tools/pr tools/audit/seat` is empty. Prepr was run again at this head. It ran from 01:02 to 01:22 UTC and ended clean. Origin/main has not moved since, so no further run was needed.

## Mutation proof

Each mutant was applied to the production predicate at `6e652a3e`, run and then restored. `git status --short` was empty after the restore.
- **The tree comparison dropped.** In `reuse_verdict`, `[ "$(git rev-parse "$c^{tree}")" = "$t" ]` became `true`. `bash tools/pr/app_push.sh --self-test` then gives `219 checks, 1 failed`. The only failure is `FAIL real git (f): a tree differing from the trailer's runs the full prepr`: the verdict reused a receipt whose tree was not the code's.
- **`tests/structure.py` dropped from `merged_steps`.** Its run became `out=""; r=0`. `bash tools/pr/prepr.sh --self-test` then gives `503 passed, 1 failed`. The only failure is `FAIL (d) a clean merge whose tests/structure.py fails is refused, though HEAD alone passes (got 0, wanted 1)`.

## Null control

Every refusing arm has a passing twin on the same throwaway repository.
- **Verdict arms (in `app_push.sh --self-test`).**
  - (a) The receipted code merged cleanly with main reuses the receipt, for an open and for an update plus its own row.
  - (b) The null control: a body with no trailer, a trailer naming another sha, and no body ref at all each run the full prepr. So does the stub-driven push, which runs prepr once with no `PREPR_SKIP_CODE`.
  - (c) A resolved conflict runs the full prepr.
  - (f) A wrong tree runs the full prepr. Its twin, the same receipt with the right tree restored, reuses.
- **Merged-tree arms (in `prepr.sh --self-test`).**
  - (d) passes with a clean main and is refused only once main gains the file that fails `tests/structure.py`.
  - (e) passes once main is green again.
- **Unmodified tree.** At the base `2a9cd347`, `app_push.sh` has no `--reuse`, and `prepr.sh` writes no receipt: it prints `PRE-PR: <sha> <digest>` and records nothing. So every open and code update runs the full prepr, as the ruling measured.
- **The four named instances.** #3197, #3195, #3085 and the machinery part 2 open all predate this diff. Only this diff's `body_push.sh` writes a `Prepr:` trailer, so none of their body refs carries one, and the verdict reads all four as full prepr, the fail-closed arm. The ruling's reuse reading for #3197 and #3195 came from prose. It becomes a receipt only when those heads are handed off again through this `body_push.sh`, so no end-to-end check of the four was possible here.

## Figures

- The self-tests at `6e652a3e`, the merged head. `bash tools/pr/app_push.sh --self-test` gives `219 checks, 0 failed`. `bash tools/pr/prepr.sh --self-test` gives `504 passed, 0 failed`: the branch's 482 at `f88cc450` plus the rows main added since `af941ad4`. Each mutant above still fails exactly its own one check, so the resolution dropped neither arm.
- The gate scope from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` is `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- `python3 tests/structure.py` at `6e652a3e` gives `STRUCTURE RATCHET PASSED`.
- `git diff origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION` is empty: the claim files are byte-identical to origin/main.
- The full run at the resolution merge, `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at `6e652a3e`, ended `rc=0` with `receipt 6e652a3ea59b written`. The run this head's receipt records is the same command at `1acf58eb`: it ended `rc=0`, and its `receipt` step reads `1acf58eb7c1f written`.
- The kept-step wall time under `PREPR_SKIP_CODE` was measured at `91a75ed8` and not re-taken: 27 s, with no heavy slot, merged structure 20.9 s and ci predict 2.8 s. The merge adds no step to that set. Main's step 1a3 is a body check and runs in both modes.

## Red checks

none

## Forward-carry

none

## Friction

none
