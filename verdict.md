Fix review: blocked 131b1358e408954ed0076904bb9a811e5e80fac8 architecture-unsound: the checkout guard re-implements its own command parser instead of reusing pre-bash.sh's, so bash -c, eval, subshell and $() moves of the orchestrator checkout pass

bus-nonce: 21df4a33ef0868b295a7d81b5955e62d

Round: first round of fix review for PR 3294 (R10-FLY-STANDING-CONTRACTS part 2). Measured head 131b1358e408954ed0076904bb9a811e5e80fac8, from a detached worktree at that head.

## Block

- architecture-unsound (fix-review.md step 15, departure from the approved design). The design at design/r10-fly-standing-contracts 21210036, decision [V4] (design.md:96), rejected a separate checkout guard because it "duplicates pre-bash.sh's command-position parser (pre-bash.sh:13-17, which reads `bash -c` and `eval` bodies); a second arm reuses it". The second arm, `HPO_PRE_BASH_GUARD_PY` in `.claude/hooks/pre-bash.sh`, does not reuse that parser. It splits the command with its own `re.split(r"\n|;|&&|\|\||\||&", cmd)` and `shlex`, so it never reads a `bash -c` or `eval` body, a `( ... )` subshell, or a `$( ... )` substitution. At this head, with `HPO_STATE_DIR/orch-checkout` naming a throwaway repository (ev/guard_probes.txt), these all exit 0 (allowed): `bash -c 'git pull'` and `eval git pull` from inside the checkout; `(cd <orch> && git pull)`, `echo x $(git -C <orch> checkout main)` and `sh -c 'cd <orch>; git reset --hard'` from another repository. The controls behave: plain `git pull` in the checkout exits 2, and `git status` exits 0. This is gap 4's own class ("P3's guard refuses the same class for a session"), and it sits in the design's named seam, so it is a design departure and not a later refinement. Cure: route the second arm through the first arm's command-position parser (the `parse` walk at pre-bash.sh:65-131, which already descends into `bash -c`, `eval` and `$(`), and pin each of the five probes above in `--self-test`, each with a mutant.
- mutation-vacuous (step 1), second block on the same head. `tools/audit/seat/hooks/seat_interpreter.py`'s only positive behaviour, printing `SEAT-INTERPRETER refused` when `seat_venv.sh --check` fails, is pinned by no case. Mutant S1 (`if r.returncode == 0:` becomes `if True:`, which makes the hook always silent) SURVIVES `hooks_setup.py --self-test` (ev/mutants.txt). The only seat-interpreter case is the inert case, which S2 kills. Cure: add a fixture case whose `seat_venv.sh --check` refuses (for example a stub seat directory or an override path) and assert on the line.

## Findings

- The guard arm in `.claude/hooks/pre-bash.sh` passes `bash -c`, `eval`, subshell and `$()` moves of the orchestrator checkout because it does not reuse the first arm's command-position parser, against design [V4]. This is the block above, owed by this group's fixer on this PR. Carry: R10-FLY-STANDING-CONTRACTS
- `seat_interpreter.py`'s refusal line is unpinned: mutant S1 survives `hooks_setup.py --self-test`. This is the second block above, owed on this PR. Carry: R10-FLY-STANDING-CONTRACTS
- Follow-up: the design's MOVERS list (`checkout switch reset pull merge rebase stash clean restore`, design.md:194), which the diff copies faithfully, omits other subcommands that rewrite the working tree a running script is read from: `cherry-pick`, `revert`, `am`, `apply`, `rm`, `mv`, `checkout-index`. This is not a departure from this design. The group's design owner should judge whether gap 4's class is wider than the list. Carry: R10-FLY-STANDING-CONTRACTS

## Evidence

- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. Merge base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76.
- Merge: `git merge-tree --write-tree origin/main 131b1358e` exits 0, tree 24327a97fbec531c1045b4b74dc38f176450668b. tests/closures.json resolved by the LEDGER-MERGE driver (ev/merge-tree.txt).
- CI: `merge_train.py classify 131b1358e408954ed0076904bb9a811e5e80fac8 --pr 3294` exited 0: `GREEN 131b1358e408954ed0076904bb9a811e5e80fac8 pending: none red: none` (ev/classify.txt).
- Red checks, read job by job across all 68 check runs of the head (ev/check-runs.txt): `tests / nightly-status` 128515447702 failed, outside the required set, named in the body. `pr-contract / pr-contract` 128515449967 failed at 17:40Z and was superseded by pr-contract 128515052906, which succeeded at 20:10Z, started after the last red concluded and checked the body. The body names both. Step 11 is satisfied.
- RESULT hooks_setup self-test: `python3 -I tools/audit/seat/hooks_setup.py --self-test` gives 19 checks, 0 failed, matching the body (ev/hooks_setup.selftest.txt).
- RESULT pre-bash self-test: `bash .claude/hooks/pre-bash.sh --self-test` gives 35 passed, 0 failed, matching the body (ev/prebash.selftest.txt).
- RESULT offline_spy: network=0 remote_git=0, matching the body. RESULT selftest_wiring: 119 self-testing, 119 wired, 0 index gaps, matching. RESULT tmp_paths --check: 0 refused. RESULT ref_privacy --check: 0 refused. RESULT structure.py: STRUCTURE RATCHET PASSED, and no `*_budgets.json` is in the diff (ev/figures.txt).
- Not re-derived locally: `tests/entities.py` (it needs homeassistant, absent from this seat's venv) and the `closure.py select` MODE line. Both are cited from CI instead: `tests / closures` 128515449043 and `tests / closure-scope` 128515472716 succeeded, so the new tracked files are classified. The open-PR overlap figure (16 open PRs) was not re-derived.
- RESULT my mutants, each through the owning self-test (ev/mutants.txt). Killed: guard G1 (drop pull), G2 (ignore -C), G3 (ignore cd), G4 (arm never dispatched), G5 (any repo), G6 (ignore -c skip); git_identity I1 and I2; seat_interpreter S2. Survived: seat_interpreter S1. The null control N0 (a comment-only change) survives, as it should. The body's five installer and liveness mutants run inside the 19 checks and all die.
- Finder's harness: the packet names none. This group is a feature, so its harness is the design's section 6 acceptance list. I measured the guard against it with my own probes (ev/guard_probes.txt), which are disclosed here as mine.
- VERSION, the manifest and the RELEASE_NOTES.md heading are untouched. `dev/programme/delivery/3294.md` is in the diff. The body's `## Head` names 131b1358e408954ed0076904bb9a811e5e80fac8, the measured head.
- Policy: the three-dot diff touches no file under dev/governance/, no CLAUDE.md and no `.claude/rules/`, so it loosens no rule in CLAUDE.md. The brief's "policy change" framing applies to design P2, which this part defers. Merging still needs tvofi's review, as requested.
- Self-audit: `carry_audit.py check` exits 0 with 6 routed, 0 unrouted, 0 bad destinations (ev/carry_audit.txt). It ran over the body's Head, Forward-carry and Carries sections, transcribed from the live PR body, and over this verdict.
- Carries: every carry the body leaves open routes to R10-FLY-STANDING-CONTRACTS. The roster at handoff/audit-r10-roster bfca97ae3465fd168205f30b13882239ffda8661 holds that group with 30 carry items, including carry 19, carry 25, carry 26 (this part's scope) and carry 27 (this PR's alive-file item). None is silently dropped. The packet's carry_audit reports 5 routed, 0 unrouted.

## Friction

none
