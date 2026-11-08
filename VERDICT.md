Fix review: merge 41a196a242f20636f9e354ad98c5a401445831d9

bus-nonce: e2a00e377ef4ee1c8f5d041d06cfa03e

Round 2 (repair of the round-1 block at 81741e448). Measured head 41a196a242f20636f9e354ad98c5a401445831d9; still the PR head at verdict time (ev/head_live.txt). Its tree is identical to the authored head 32fbd8338c86 where the body took its figures (`git diff --stat 32fbd8338 41a196a24` is empty). `review_carry.py 81741e448 41a196a24` prints FRESH-REVIEW, so this was reviewed in full, not carried.

## Evidence

- CI: `merge_train.py classify 41a196a2... --pr 3341` printed `GREEN 41a196a242f20636f9e354ad98c5a401445831d9 pending: none red: none`, rc 0 (ev/classify.txt). No red check, so step 11 has nothing to answer.
- Merge: `git merge-tree --write-tree origin/main 41a196a2...` rc 0 at origin/main 425b85849 (ev/merge_tree.txt). Merge base daf8b349f. `dev/governance/roles/` has no change between the merge base and origin/main.
- Step 1, re-run at the head: the six spec mutants named in the body are pinned by `survivor_list.py --self-test`, which prints `survivor_list self-test: 20 checks, 0 failed`, rc 0 (ev/survivor_list_selftest.txt). The repair arm `a key is a whole token: tools/setup.py:3 does not list setup.py:3` is present and passes.
- My own spec mutants, run in place with `bus.sh --self-test` as the oracle: `SURVIVED NULL`, then KILLED `main_check_off`, `main_argv_swap`, `main_entry_off` and `bus_call_off` (deleting push-verdict's survivor_list call) (ev/mutant_run_spec_bus.txt, ev/spec_main.json). These cover the CLI dispatch that survivor_list's own self-test cannot reach. A first `--copy-tree` attempt killed its NULL mutant, because bus.sh's self-test needs the git checkout. It is kept as ev/mutant_run_spec_bus_copytree_nullkilled.txt and counts for nothing.
- My diff-mode driver run (`mutant_run.py --diff <base>...HEAD --cmd 'survivor_list.py --self-test' --report-only`, ev/mutant_run_diff.txt) reported 17 surviving sites. I judged each one, below. None is a non-equivalent survivor in a production predicate. Carry: dismissed: evidence, not a finding
- I ran survivor_list.py itself on that real driver output, with a verdict naming none of the sites: it printed `UNLISTED` for every site and `names 0 of the 17 survivor(s)`. So the parser reads `mutant_run.py --diff`'s real output format, not only its fixtures.
- Null controls re-run: survivor_list's three null-control arms pass, and `bus.sh --self-test` prints `bus self-test: 162 checks, 0 failed`, with `ok null control: another blocked class over the same evidence proposes` (ev/bus_selftest.txt).
- Figures re-derived at the head and matching the body: scope `--diff` gives `MODE: SCOPED -- 3 script(s) run, 30 scoped out.` and `--files` gives `MODE: FULL`, over 8 changed files (ev/scope_*.txt). `fix-review.md` measures 133/140 lines and 2449/2451 tokens (ev/policy_lint.txt). `STRUCTURE RATCHET PASSED`. `selftest_wiring: 125 self-testing, 125 wired, 0 unwired` and `0 index gap(s)`.
- Not re-derived: the body's doc_claims, entities and harness_headers counts (their CI lanes are green and I cite them), the sibling-handoff merge-tree results, and the `review_strength.py` motivating counts, which the body does not quote.
- Steps 4 and 5: no VERSION, manifest, RELEASE_NOTES or golden/claim-file change in the three-dot diff (ev/version_untouched.txt). No metric moved except one `tests/closures.json` INERT entry for the new file, which the new file earns. No budget raised.
- Step 6 class: this PR mechanises one seam, the survivor-line grammars. A tree search for survivor prints outside survivor_list finds only mutant_run.py:199, :203 and :332. Those are the `--spec` and `--diff` formats the tool reads and pins through PRODUCERS. mutation_table's formats are pinned the same way. The body dispositions `class-open` as having no mechanical check.
- Steps 9 and 10: no finder's harness applies (governance tooling, owner ruling). Forward-carry: none.
- Policy: the diff edits `dev/governance/roles/fix-review.md`, so it merges only on tvofi's approving review, as the body states.

## Findings

- The diff-mode survivors at survivor_list.py:38 (`sys.path.insert(1,...)`) and :67 (`split(" ", 2)[0]`) are equivalent: index 0 is unchanged by the mutation, and the inserted path holds the only `mutation_table`. So are :175 and :176, the usage text and the usage return `3` instead of `2`, which every caller only tests for non-zero. Carry: dismissed: equivalent mutants, no observable behaviour changes for any caller
- The diff-mode survivors at :104-167 and :179-180 are inside `_self_test` (the oracle mutated against itself) or the `__main__` guard. The guard is killed under bus.sh (`main_entry_off` above). Mutating the oracle is not a production mutant. Carry: dismissed: test-harness lines, not production
- `survivor_list.py check` counts every driver line anywhere under the evidence directory. That includes a reviewer's baseline control run (step 2 asks for both ends), so a `mutation-vacuous` block must also name the base-only survivors it put in evidence. This is over-inclusive only: naming an extra key keeps the verdict correct and costs one token. Carry: dismissed: over-inclusive, never under-inclusive; no wrong verdict is admitted

## Friction

none
