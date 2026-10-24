Fix review: merge 7dc281cd3f08fe05866ac5bdad10e5cfe5ec85dc

bus-nonce: 36bbdf280ca73024fe047e0bef5885e5

Round: first review of #2742 (R10-ROSTER-SYNC-CARRIES-OPEN). Measured head: `7dc281cd3f08fe05866ac5bdad10e5cfe5ec85dc` (still the branch head when this verdict was written). Merge base with origin/main: `73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec`. The roles directory on main has not changed since the merge base, so this contract is current.

## Findings

- The PR title and its own delivery row (`dev/programme/delivery/2742.md`) both say "carries-open classified as **derivable**". The diff does the opposite: it adds `carries-open` to `PROTECTED_STAGES`, and the body says protected. The record row will read wrong after the merge unless the title and row are corrected at merge time. Carry: R10-ROSTER-SYNC-CARRIES-OPEN
- The body's per-site census rule (`git grep -n "DERIVABLE_STAGES\|PROTECTED_STAGES\|DONE_STAGES\|WIP_STAGE" -- tools`) returns readers the body does not name: `flow_metrics.py`, `handover_prompt.py`, `plan_page.py`, `prune_refs.py` and `roster_lib.is_open` (the after-edge rule). They all read the one `roster_lib.DONE_STAGES` tuple, which the body disposes of as a whole ("unchanged"), so the class is closed and this is not class-open. The body does not state one consequence, though: a `carries-open` group counts as open in `roster_lib.is_open`. Its after-edges therefore keep blocking dependent groups, and `prune_refs` keeps its branch. This was already the runtime behaviour at the base, and this PR does not change it. A later seat dispatching on `after:` needs it stated. Carry: dismissed: pre-existing runtime behaviour that this PR leaves unchanged and that the body's DONE_STAGES disposition covers; noted so the orchestrator knows a carries-open predecessor blocks its dependents.

## Evidence

- RESULT selftest_head: `roster_sync self-test: 55 checks, 0 failed` (ev/selftest_head.txt).
- RESULT mutation: removing the `"carries-open"` entry from `PROTECTED_STAGES` gives `FAIL carries-open is classified protected and not derivable ...` and `55 checks, 1 failed`; restored afterwards (ev/mutant_m1.txt). The mutation is not vacuous.
- RESULT existing mutants: `r10_roster_sync_mutants.py` kills every plant and ends `restored` (ev/mutants_script.txt, tail shown).
- RESULT null control, re-run independently: origin/main exported with roster `wave-r9-groups.json` group R9-F1.1 set to `carries-open`. Base `roster_sync.py` gives `53 checks, 1 failed` (`every stage the tree's rosters carry is classified`). The head's `roster_sync.py` on the same tree gives `55 checks, 0 failed` (ev/null_base.txt, ev/null_head.txt). This matches the body.
- The body says the new fixture row (R9-CO, merged PR, stage unchanged) also passes at the base. That is consistent with the skip rule `stage not in DERIVABLE_STAGES`; the classification check is the one that kills the mutant.
- `pr_cap.py --self-test`: `21 checks, 0 failed` (ev/pr_cap.txt).
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`. `closure.py select` against the merge base: `MODE: SCOPED -- 1 script(s) run`, `scope.run` = `tests/entities.py`. `archscore --diff origin/main`: `Architecture score: dS +0.0000 NULL` (ev/figures.txt). Every body figure re-derived.
- I could not re-run `tests/entities.py` locally (killed after 300 s). CI's run on this head is cited instead.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched; the diff is two files (ev/version_untouched.txt). No claim files are touched and no fixture is value-bearing, so step 4 is vacuous.
- `git merge-tree --write-tree origin/main 7dc281cd3f08fe05866ac5bdad10e5cfe5ec85dc` exits 0, so there is no conflict (ev/merge_tree.txt).
- Head chain from the body checked: `05d056931` is the code commit, `6636dc5fd` merges origin/main `73b69fe0a`, and `7dc281cd3` adds only the delivery row.
- No metric moves (no budget, closures, INERT, ledger or score changes), so step 14 has nothing to earn. The added lines are a tuple entry, a comment and two self-test checks, consistent with the module's pattern (step 15).
- Forward-carry: the body says none. The second finding above concerns pre-existing behaviour, and is dispositioned there with its own Carry line.
- Red checks: `governance / instrument-self-tests` on #2710 is answered in the body (detector exists but is wired only at the PR; process state gap; countermeasure recorded as not built for a single instance, with its form named). The trigger is answered.
- Harness: the finder's harness is the existing self-test's tree-roster check, which is committed. I built no instrument of my own; the null-control roster edit is a one-line fixture change in a temp export.
- CI at this head: 53 check runs, all completed (ev/ci_checkruns.txt). Every gate check is success, skipped or neutral, with one exception. That exception is `gate` job 120917926764 (workflow run 40106062055, `KIND: edit`), concluded failure at 16:03:13Z with the single line `FAIL run(s) [40106062246] at this head are still being judged; their gate decides`. That run's own `gate` (job 120919122483, `KIND: code`) later printed `PASS` (16:06:40Z). The red is the edit-run gate deferring to the code run's verdict while that run was still in flight. It is not a test or contract failure, so it owes no root-cause answer. `governance / instrument-self-tests`, `tests / fast (3.14)`, `tests / mutation`, `tests / closure-scope` and `pr-contract / pr-contract` are success on this head. I did not read the mutation lane's log: the diff changes production lines only in an instrument tuple, and the targeted mutant above was run by hand.
