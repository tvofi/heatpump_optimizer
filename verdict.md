Fix review: blocked 3d1c405ddbe8d9adefbbb1d26a22ba63871fd995 mutation-vacuous: ci-watch.sh sleep "$POLL_S" -> sleep 300 survives

bus-nonce: 2849fd6aa13fe99059e04be26c5ca565

Round 1 of this review. Measured head: 3d1c405ddbe8d9adefbbb1d26a22ba63871fd995 (still the PR head when written; ev/HEAD.txt).

## Block

- `tools/audit/seat/ci-watch.sh` line 299, the one line that turns arm 1's cadence into behaviour for ci-watch: mutating `sleep "$POLL_S"` back to the old `sleep 300` leaves `bash tools/audit/seat/ci-watch.sh --self-test` at `14 checks, 0 failed` (ev/own_mutants.txt, `ciwatch-sleep-literal`). The new check, "the poll is inside [60 s, 240 s]", pins only the value of `POLL_S` (the body's `POLL_S=240`->`300` mutant is killed), not that the loop sleeps for it. So the ci-watch half of gap 1 can regress to a 300 s wait with every check green: fix-review.md step 1, `mutation-vacuous`. A cheap fix: an assertion that the loop sleeps `$POLL_S`, for example by driving one non-ONCE cycle with a stubbed `sleep` that records its argument, or failing that a grep for the loop's sleep line. Then re-run the mutant. Carry: R10-FLY-CACHE-PROMPTS

## Findings

- `proof_watch.Watcher.__init__`'s `poll: float = POLL_S` -> `300.0` survives (ev/own_mutants.txt, `proof-ctor-default-300`). It is equivalent in production: the only callers are `main`, which always passes `poll=a.poll` (that default is pinned and its mutant is killed), and the self-test, which passes `poll=1.0`. No action is needed unless a new caller relies on the default. Carry: dismissed: equivalent mutant, no production caller uses the constructor default
- `reviewer-head-off` survives `r10_flow_dispatch_mutants.py` at this head, as the body states. It is pre-existing and is carried by the body. Carry: R10-FRICTION-MUTATION-SURVIVOR

## Evidence

- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. The merge base is b0b2d7697f8c5baaef2c082d9bf3242b57249e68, which is the origin/main tip.
- Merge: `git merge-tree --write-tree origin/main HEAD` gives rc=0 and tree 2625e3ab (ev/merge-tree.txt).
- Self-tests at the head (ev/selftests.txt): cloud_dispatch 87 checks, 0 failed; stop-selfcheck 29 passed, 0 failed; ci-watch 14 checks, 0 failed; proof_watch 43 checks, 0 failed; `policy_lint --hooks` HOOKS ok: 3 wired hook(s). Each matches the body's figure.
- `r10_flow_dispatch_mutants.py` at the head (ev/dispatch_mutants.txt): `RESULT mutants=33 survived=1`, with the survivor `reviewer-head-off` and M0 `null-ok`, as the body states. The new arms match the body's figures: pointer-ref-dropped 4, pointer-off 4, publish-ignored 2, publish-ref-rev-dropped 2, wait-line-dropped 1, claude-md-reread 1, nonce-altered 4, prompt-wrong 12 and flag-unlisted 2 are killed, and topic-to-id is CRASHED after FAIL lines. parent-drop, head-ignored and roster-repo-ignored also print CRASHED after FAIL lines. The harness counts these as detected, and they are not this diff's arms.
- I did not re-run the harness at the base. The body's base figure (`mutants=4 survived=1` on a subset) is not re-derived here. The base nonce pattern count is re-derived: `git show b0b2d769:tools/audit/seat/cloud_dispatch.py | grep -cF 'pr=pr, topic=topic, nonce=nonce,'` prints 0 (ev/class_rules.txt).
- My own mutants (ev/own_mutants.txt). These are killed: the settings.json fallback dropped; `[ -f "$f" ] || exit 0` dropped (got 127, wanted 0); the proof_watch floor off; proof_watch POLL_S 300; ci-watch POLL_S 300. These survive: the ci-watch sleep line (see Block) and the Watcher constructor default (equivalent, see Findings).
- Class rules re-run at the head (ev/class_rules.txt). Every seam the rule returns is either in the diff or dispositioned in the body: tick_loop, state_docs, merge_train, orchestrator_tick, prepr stubs, codeql-triage-poll, ci_probe MIN_POLL_S (a floor, not a wait). The gap-6 rule returns handover_prompt and sweep_template, which the body dispositions, and the cloud_dispatch self-test string.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (the three-dot diff is empty). Neither claim file is touched and no fixture moved, so step 4 is vacuous.
- The PR body names head 3d1c405ddbe8d9adefbbb1d26a22ba63871fd995, which matches.
- CI on this head (ev/check-runs.txt, read from the check-runs API) has no red conclusion so far. codeql python, env-matrix, instrument-self-tests, policy-docs, browser, closures, coverage, fast (3.14) and one prelude were still in_progress when read. The body's "Red checks: none" holds so far, but this was not re-checked after they concluded.
- Forward-carry destinations R10-FRICTION-MUTATION-SURVIVOR and R10-FLY-SUITE-ENV-FLAKES exist in origin/main:dev/programme/rosters/wave-r10-groups.json.
- No finder's harness is named, and this is an owner-ordered tooling fix. The dispatch mutant harness is in the tree. I built no instrument; my mutants are one-off replacements, listed in ev/own_mutants.txt.
