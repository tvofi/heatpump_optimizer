Fix review: merge 3e5b8b7c5b3746230db1920968452931ff5fba1b

bus-nonce: 39187de42e2b050e0c1d335fcfccd742

## Verdict

Round 1 review of PR #2969 (R10-STAMP-ROUND-MAJOR) at head 3e5b8b7c5b3746230db1920968452931ff5fba1b, from detached worktrees at that SHA, merge base e5ddba1fad5e6eccfeceaeaaa249bc459963405b. The head was re-read before posting (`git fetch origin fix/r10-stamp-round-major` gave 3e5b8b7c5b3746230db1920968452931ff5fba1b). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- Surviving reviewer mutant M3: main() can pass the roster round under the wrong condition (`roster_round_at(ROOT) if args.round_close is None else None`) and `stamp.py --self-test` stays green. Its main-wiring arm only checks that a source substring is present. The mutant fails closed: every `--round-close` refuses with "no readable roster", and the closeout's own `--dry-run` on main shows that before anything is written. Carry: dismissed: fails closed and the closeout dry-run exposes it before any write; a behavioural main() test costs more than it prevents.
- Surviving reviewer mutant M1: main() can drop the `if nxt is None: raise Refuse(3, ...)` line and the self-test stays green. By reading (stamp.py lines 2509-2517 at the head), a None version then reaches `version_tuple(None)` in rule 3 and crashes with AttributeError before rule 4 or any write. So it fails closed, as a traceback rather than a refusal. Carry: dismissed: fails closed before any write; no path from it to a wrong version.
- `.claude/workflows/web-stamp.js` and its siblings in web-fragments only pass `--bump ${bump}`, so the round-10 closeout cannot be stamped through web-stamp. `bump: 'major'` now refuses with a message naming `--round-close`, and the PR body says the closeout must run `stamp.py --round-close 10`. Carry: dismissed: fails closed with a refusal that names the right flag, and decision 0016 and the body both state the closeout command.

## Evidence

- RESULT mutation proof (ev/mutants.txt): `r10_stamp_round_mutants.py` gave R1 rc=1 fails=2, R2 rc=1 fails=1, R3 rc=1 fails=2, R4 rc=1 fails=1, R5 rc=1 fails=1, R6 rc=1 fails=1, and `plants: 6, without a FAIL line: none`. All of these match the body.
- RESULT null control (ev/null.txt): `--null e5ddba1f...` gave `RESULT mutant=null rc=0 fails=0` and `RESULT null grid=720 differ=0`, which matches the body. The driver's self-test (ev/driver-selftest.txt) gave 8 checks, 0 failed. `stamp.py --self-test` gave `RESULT stamp_self_test=pass`.
- Reviewer's own mutants (ev/reviewer-mutants.txt): M2 (`roster_round_at` ignores its root) was killed by a FAIL line. M4 (no neither-flag refusal) was killed by a ValueError traceback, and argparse also guards that path. M1 and M3 survived; see Findings.
- CLI refusals at the head (VERSION 7.0.5, roster round 10), re-run with `--dry-run`. `--bump major`, `--round-close 7`, `--round-close 9` and `--round-close 10 --bump minor` each print `stamp refused (rule 3)` before any fetch. `--round-close 10` and `--bump minor` pass next_version and stop at rule 1, because HEAD is not origin/main. All of this matches the body.
- Finder's harness: the brief and body name none. This is a feature from an owner directive, not an audit finding, so there is no judge ruling and no design trace. The harness is the fixer's in-tree driver, and I disclose that I used it, plus my own mutants.
- Class: the body has a single seam, the version assignment in `stamp.py`. Every caller of `bump()` in the tree is `next_version`. The callers of `stamp.py --bump` are the web-*.js stampPrompt and web-fragments.md, and they are dispositioned above.
- Rule 4 / step 5: the three-dot diff touches none of VERSION, RELEASE_NOTES.md, the manifest or tests/golden (ev/rule4-untouched.txt).
- Step 4: `tests/env_drift.py --all` gave NO UNCLAIMED DRIFT and NO STALE FIXTURE, with 56 scenarios checked (ev/env_drift.txt). Neither claim file is in the diff.
- Ratchets and figures at the head: `tests/structure.py` gave STRUCTURE RATCHET PASSED. `tests/doc_claims.py` gave ALL 203 checks PASSED. `policy_lint.mjs --budgets` shows tools/audit/briefs/orchestrator.md at 4251 of 4251, which matches the body's figure. Locally, `tests/entities.py` could not import `homeassistant` in this seat (ev/entities-local-no-ha.txt), so for entities I cite CI's `tests / closures` success. I could not read the gate's MODE line (the logs are too long to tail), so the scoped-gate figure in the body is not re-derived; CI's closures check concluded success.
- Step 14: the only moved numbers are a new `tests/closures.json` INERT-read entry for the new driver, which is earned because the file is new, and a new `governance.yml` self-test step. No budget, golden or score moved. There is no raise.
- Step 13: `git merge-tree --write-tree origin/main 3e5b8b7c...` exits 0 with no conflict (ev/merge-tree.txt).
- Step 7: the body names the head 3e5b8b7c5b3746230db1920968452931ff5fba1b and explains the code head e1913fbf.
- Step 10: the body's Forward-carry is none, which is consistent: the closeout command lives in decision 0016 and in stamp.py's own refusal.
- Step 15: no architecture breach. One pure `next_version` owns every refusal, `bump()` loses its major arm, and the alternatives are recorded.
- CI on the head (ev/check-runs.txt, read from the check-runs API). Every gate check concluded success, skipped or neutral, including tests / closures, mutation, governance / instrument-self-tests, policy-docs, env-matrix and budget-raise-gate. `tests / nightly-status` is red, but it is not this PR's, because the diff does not reach what it reads (fix-review step 11). A `prelude` job in run 40961019797 (a PR-edit run on synthetic sha 200786555d) is still in_progress, and a `pr-contract` run was queued after a body edit. Neither is a gate result on this head. The body's Red checks section is "none", which is consistent with this.
