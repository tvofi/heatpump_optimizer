Fix review: merge 83d9662d8c75ef75af2febcabf6e2e0a3c8a23fd

Round 2 of R10-FLOW-ANDON (#2582). I measured head 83d9662d8c75ef75af2febcabf6e2e0a3c8a23fd from a detached worktree. Merge base 57f0c9c77cfd, which is also current origin/main. dev/governance/roles/ is unchanged between the merge base and origin/main, so my contract is current.

RESULT ref_privacy_check head=0-refused 5005f02ef=1-refused (REFUSE tools/audit/seat/heartbeat.sh:35, the round-1 CI red reproduced)
RESULT ref_privacy_selftest 66 checks, 0 failed
RESULT heartbeat_selftest 7 checks, 0 failed
RESULT tick_loop_selftest 12 checks, 0 failed
RESULT mutants M0=0-seat-steps-red (ref_privacy step included) tick_loop-1 tick_loop-2 heartbeat-1 heartbeat-2 heartbeat-3 heartbeat-4 all KILLED, survivors=0
RESULT manual_tick_loop-1 (heartbeat call line deleted by hand) tick_loop self-test 12 checks, 4 failed
RESULT plant guard-deleted, committed on a detached scratch commit: ref_privacy --check 1 refused ("registered guarded but calls no ref_privacy guard"); the PUSHERS entry is earned, not decorative
RESULT selftest_wiring 39 wired, 0 unwired; throwaway_git 0 refused; structure RATCHET PASSED; closure MODE: SCOPED, 2 scripts (entities.py, harness_headers.py)
RESULT merge-tree --write-tree origin/main(57f0c9c77cfd) head: exit 0, tree d0952cf7, no conflict
RESULT version untouched: VERSION, manifest, RELEASE_NOTES, budgets, goldens, closures.json all unchanged in the three-dot diff; pr-contract prints "no version edit"
RESULT ci check-runs at head (41): all concluded; only nightly-status failure (main's nightly, answered); instrument-self-tests, pr-contract (18:42:00, after the last red), fast (3.14) (covers entities/harness_headers), coverage, mutation, closure-scope, policy-docs, Analyze (python) success
RESULT head re-read before return: fix/r10-flow-andon = 83d9662d8c75ef75af2febcabf6e2e0a3c8a23fd, origin/main 57f0c9c77cfd unchanged

## Non-blocking notes (every check I ran)

- Mutation proof (step 1). Each mutant named in the body is killed by its own self-test step. M0 runs every instrument-self-tests step unmutated and all of them pass. I repeated tick_loop-1 by hand: 4 checks fail, not only one.
- Finder's harness (step 2). The finder's harness is the CI ref_privacy step. I ran `ref_privacy.py --check` at 5005f02ef and at the head, and I ran the committed mutant harness myself. Both ends match the body.
- Force-push guard. hb_push pushes only refs/heads/heartbeat/orchestrator, with `-f --no-verify`. The message goes through `ref_privacy.py guard` before commit-tree. The commit message carried from tick_loop is `TICK-PASS <utc> relay=<rc> tick=<rc>`, with no --out path. Self-test check 3 shows that a $HOME-bearing message is refused and that the reachable ref stays put. heartbeat-4 kills it.
- Spec compliance. The spec pack at ff1beba2 sets a seam: a standalone job script with --once, and self-tests built through throwaway_git. Both hold. The heartbeat test reaches git only through tests/throwaway_git.sh, and throwaway_git --check reports 0 refused.
- Class (step 6). The group has one seam (one liveness ref) and the body names no enumeration rule. The class is that one seam.
- Red checks (step 11). pr-contract's range read is `record red-history 6 commits: instrument-self-tests, nightly-status`. instrument-self-tests is green at this head and the body answers it with a cheaper detector: `ref_privacy.py --check`, which costs seconds. nightly-status is answered truthfully. The body names its own governance.yml touch, which is why it owes the answer. nightly-status grades main's scheduled run 39563978649 (c77f89d, 07:43Z), and I confirmed from that run's logs: slow fails at `loop_cpu_ratio 0.1138 over its budget 0.111`, and mutation-nightly at `10 survivor(s) of 23 evaluated = 39.1% ... cap 30.0%`, all in custom_components/. #2548 merged at 17:03Z. The pr-contract run 119413000833 started 18:42:00, after nightly-status concluded red at 18:41:43, and passed: PR-BODY 0 errors, FIGURES 11 resolved, CARRY-AUDIT 2 routed, 0 unrouted.
- Head SHA (step 7). The body names 83d9662d8c75 and its code head a50dee030. Both match what I measured.
- Forward-carry (step 10). R10-ORCH-MACHINERY's job is to register `heartbeat.sh --once` as the beat's heartbeat job. That instruction is already written: the spec pin's shadow roster carries it in R10-ORCH-MACHINERY's own carry (K17: "heartbeat (R10-FLOW-ANDON's job script; interval 300 s, timeout 60 s ...)"), and so do FUTURE-STATE.md's folded carries. It is not yet on origin/handoff/audit-r10-roster (23ef06dc), because the pack's groups are "registration pending: roster PR-B", as the title says. The roster registration carries it there, so I do not block.
- Figures I did not re-derive locally. tests/entities.py and tests/harness_headers.py need the seat venv. This container has only Python 3.11, which cannot import voluptuous or parse the tree, so for those two I cite CI's fast lane at this head instead.

## Routing

Carry: dismissed: verified, no defect found (item d9752b9c)

Carry: dismissed: verified, no defect found (item 0c930d67)

Carry: dismissed: verified, guard holds as claimed (item 7230652b)

Carry: dismissed: verified, spec seam honoured (item 4fd55fb8)

Carry: dismissed: single-seam class, nothing open (item d0842686)

Carry: dismissed: every red answered, nightly-status is main's (item d0c46cb4)

Carry: dismissed: head matches body, no move (item 159e28cd)

Carry: R10-ORCH-MACHINERY (item e06d6cac)

Carry: dismissed: container lacks seat venv, CI fast lane cited (item ea4d55b2)

bus-nonce: 5f55e15cff83ca14fd0727e303b83a81
