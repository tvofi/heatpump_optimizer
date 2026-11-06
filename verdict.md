Fix review: blocked 4512d770d6fab83a43b953bbcfe95db5a61c891a root-cause-detectable: governance / instrument-self-tests is red on this PR's own new file tests/replay_cost_draws.tsv (in no audit universe, not excluded), ## Red checks does not name it; tools/audit/check_scopes.py --repo . shows it in 1.2 s

bus-nonce: d519881ffaebad047af1a10f82dea3e0

## Block

`governance / instrument-self-tests` (job 127916728606, run 42214980826, concluded failure 12:31:39Z) is red because of this diff. The failing step runs `python3 -I tools/audit/check_scopes.py --self-test --repo .`; its arms `the default verdict passes the live scopes` and `the default invocation exits 0 on the live scopes` are False. The live invocation at this head names the cause:

    FAIL coverage tracked=9100 in_universe=1416 excluded=7683 unclassified=1
       in no universe and not excluded: tests/replay_cost_draws.tsv

The same self-test passes at the merge base 7e8939d3 and at origin/main b36679ce (rc 0, `SELF-TEST passed`) and fails at 4512d770 (rc 1); the only difference in its output is the D11 universe gaining one file and the live verdict turning False (ev/cs-base.txt, ev/cs-main.txt, ev/cs-head.txt). It is not inherited from main: main's 7e8939d3 ran this check green (job 127863739526).

The body's `## Red checks` says this check was "still in progress when read"; it concluded red, and `pr-contract / pr-contract` (job 127916741200, started 12:35:58Z, after the red concluded) refuses the body for it: `check governance / instrument-self-tests is red and ## Red checks does not name it` (ev/prc.log). That is also the packet's refusal (`red-unanswered`) and the pr-contract red itself.

A cheaper detector exists: `python3 -I tools/audit/check_scopes.py --repo .` runs in 1.2 s locally and names the file; `tools/pr/prepr.sh` does not call it (it runs only in governance.yml:595). So: root-cause-detectable.

What the fixer owes: classify `tests/replay_cost_draws.tsv` in `dev/audit/config/scopes.json` (a universe or a reasoned exclusion), re-run check_scopes at both ends, and answer the red in `## Red checks` (the cheaper detector and its standing cost, or a recorded refusal). The code fix itself is not what blocks.

## Round

This is round 4 of the fix review. The body carries a `## Re-cut` scoped to the round-3 blocked finding, and I accept the re-cut as the reason a fourth round is allowed. The re-cut's scope (the ref46/ref53 border) is settled at this head; see Evidence.

## Findings

- Follow-up: `tools/pr/prepr.sh` does not run `tools/audit/check_scopes.py --repo .` (1.2 s), so a new tracked file in no audit universe reaches CI and turns `governance / instrument-self-tests` red after the handoff; this PR is an instance. The fixer answers it in `## Red checks` with this detector or a recorded refusal. Carry: R10-REPLAY-COST-2
- Residual: the grading unit is still one number per job. A job whose pooled ruler reaches >= 51.12 but whose runner is a ref47 runner is graded on ref53's 2.076 and goes red (the body's own `--ruler 51.5` null shows `cpu_ratio 2.256 over its budget 2.076`). The nearest ref47 job sits at 50.07, 1.05 ms under the border; ref53's lowest is 52.17. The body states this residual and does not claim it fixed. Carry: R10-REPLAY-COST-2

## Evidence

- Head reviewed: 4512d770d6fab83a43b953bbcfe95db5a61c891a (ev/HEAD.txt). The roles dir is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge with origin/main b36679ce: `git merge-tree --write-tree` rc 0, `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).
- Blocked finding of round 3 settled. `replay_draws.py grade --job 127046649273` at this head: synthetic job ruler 50.07, class ref47, clean passes (cpu_ratio 2.2558 against ref47's 3.3424, the figure that now stands beside 2.256 / 2.081); cpu arm `cpu_ratio 4.444 over its budget 3.342`, loop arm `loop_cpu_ratio 0.2063 over its budget 0.1527`, memory arm `peak_kib 3861 over its budget 2686`. `--ruler 51.5`: `cpu_ratio 2.256 over its budget 2.076` (the regression above the border still reds). `--clean-from cpu`: refused on cpu and loop. Each figure matches the body (ev/figures.txt).
- Finder's harness: the round-3 probe's own draw set (probe/rev-3234-c9b474ca ev/draws.tsv, 110 jobs, 535 runs, every job also in the committed set) graded with this head's code: 0 offenders. Every ref53 job (11, rulers 52.17-54.61, cpu 1.4437-1.4926) grades green on ref53's 2.076, so the true ref53 draws pass (ev/finder-draws-graded-at-head.txt).
- Body figure `draw_offenders` over the committed draws: 0, re-derived (ev/figures.txt). Controls at this head: 36, none failing (ev/controls-head.txt). 116 jobs and 565 runs as the body states; the per-class counts match (ref23 18, ref28 2, ref31 33, ref38 2, ref40 2, ref47 48, ref53 11).
- Mutation proof, re-run: `draw_rulers` returning the synthetic clean run's own rulers turns `class_rule`, `draws` and `lane_prints_notice` red (3 of 36), as the body says (ev/mutant-draw_rulers-synclean-both.txt). A narrower mutant (only ref_ms un-pooled) reds `class_rule` alone (ev/mutant-draw_rulers-clean.txt). `job_cost` graded on the clean run's own ruler reds `runner_class_fallback` (ev/mutant-job_cost-clean-ruler.txt). No mutant survived.
- `tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure-head.txt). `tests/entities.py` could not run in this container (`No module named 'homeassistant'`, ev/entities-head.txt); CI's `tests / closures` and `tests / fast (3.14)` concluded success at this head.
- No claim file, `VERSION`, manifest, release-notes heading or `*_budgets.json` is touched (three-dot diff stat empty for them). The delivery row `dev/programme/delivery/3234.md` is present.
- CI at this head (read live, both pages, 105 check runs, ev/check-runs-head.tsv): red `governance / instrument-self-tests`, red `pr-contract / pr-contract`, `gate` jobs failing/in progress on the red; `tests / replay` success. `merge_train.py classify` exited 2 (`the check runs at 4512d770d6fa could not be read`): its paginated read follows a `repositories/{id}` link the proxy refuses (HTTP 403); I read both pages by hand instead.
- Carry audit at the head: 7 finding items, 7 routed to R10-REPLAY-COST-2, 0 unrouted (review packet).
