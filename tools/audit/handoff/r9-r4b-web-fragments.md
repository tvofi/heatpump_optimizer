_Requested by **tvofi**_

Round-9 readiness follow-up to R4 (handed on from `handoff/r9-r4-instruments`, whose lease-seam enumeration left this file open). The shared `GATE` prompt fragment in `.claude/workflows/web-fragments.md`, and its four copies in `web-{decomp-stage,fix-wave,stamp,triage}.js`, told a seat that `run.sh` "holds flock for the gate run and renews the lease before every script". It also told the seat to take the lock by hand before any run that selects `stress.py`. Neither has been true since v6.7.0 (the FIFO gate lease).

**The claim, checked against the tree first.** `tests/run.sh` `leased()` asks `gate_lock.py needs-lease` about each script and leases only the scripts it names, one run at a time (`auto-lease`, or `flock-wrap` under a seat's own `HPO_GATE_LOCK_LABEL`). Every other script runs bare. At merge base `81f2c18c`, `python3 tests/gate_lock.py needs-lease <file>` printed `lease` for a file naming `tests/stress.py` and `none` for one naming `tests/entities.py`, rc=0 both.

**The change.** The fragment now says what `run.sh` does: it leases each `stress.py` run alone and releases it after. The queue, the wait bound and holding the lease by hand across commands are cited to `.claude/rules/gate-scoping.md`, not restated. "Never remove a lock you did not create" and the concurrent-process-count rule stay, because `gate-scoping.md` does not carry them. The `MODE: FULL` explanation is kept unchanged. The two `TAKE THE LOCK` arrows now point at the `run.sh` command.

**How the copies were produced.** `fragments_sync.mjs` is a checker only; it has no write mode. `web-fragments.md` says "change the text here, then copy it out". The `GATE` declaration was copied out mechanically, by a scratch script using `fragments_sync.mjs`'s own boundary rule (a `const` line up to the next `const`, `// ---` banner or fence). No copy was edited by hand. Each copy still parses as a workflow function body.

## Approval

`.claude/workflows/web-fragments.md`, `web-fix-wave.js` and the other `web-*.js` copies are policy under `CLAUDE.md`. `web-fragments.md` and `web-fix-wave.js` are code-owned by @tvofi in `.github/CODEOWNERS`. **tvofi's approving review is owed before the merge.** This is not a budget raise: no cap in any `*_budgets.json` moves. `policy_lint --budgets` shows `web-fragments.md` and the aggregate `corpus` both falling. The delivery row (`docs/delivery/<N>.md`) is written by the Mac seat once the pull request number exists.

## Head

`26b51272aca3fc62781bd5dfc2d640ebe853e1f3`, measured on merge base `81f2c18c96636ce85006a2ef61fa0731f0813ba0`, which was `origin/main`'s tip when this branch was cut. The handoff commit after this head only carries this body.

## Mutation proof

`fragments_sync.mjs` already pins this: governance's `fragments` step runs it, and it compares every copy byte for byte with the canonical declaration. Both directions, at this head:
- **Canonical changed, copies stale.** Right after editing `web-fragments.md`, before copying out, it printed `DRIFT` for all four `web-*.js` (`GATE` first differs at line 6 of the fragment), then `FRAGMENTS: 4 copy(ies) differ`, and exited rc=1.
- **One copy hand-edited.** I changed `web-triage.js` alone ("stress.py run alone and releases it after" became "stress.py run and holds flock for the gate run"). It printed `DRIFT .claude/workflows/web-triage.js: GATE first differs at line 28 of the fragment`, then `FRAGMENTS: 1 copy(ies) differ`, rc=1. Restoring the copy restored rc=0.

`fragments_sync.mjs --self-test`: 20 passed, 0 failed, rc=0.

## Null control

At merge base `81f2c18c`, `node .claude/workflows/fragments_sync.mjs` reported `FRAGMENTS ok` with 13 fragments across 4 scripts, rc=0. The five files agreed with each other and carried the false sentence, which is why a sync check cannot find this class: it pins agreement, not truth. The seam grep below returned the stale text in all five files at the merge base, and in none of them at this head.

## Figures

- the claim against the tree: `python3 tests/gate_lock.py needs-lease <file>` on a file naming `tests/stress.py` (prints `lease`) and on one naming `tests/entities.py` (prints `none`)
- the sync check, at this head and at the merge base: `node .claude/workflows/fragments_sync.mjs`, and `node .claude/workflows/fragments_sync.mjs --self-test`
- policy budgets (the per-file line cap and every aggregate hold, and `web-fragments.md` falls): `node .claude/workflows/policy_lint.mjs --budgets`
- the scoped gate's mode line (`MODE: SCOPED -- 1 script(s) run`, and `scope.run` names `tests/entities.py`): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL ... ENTITY CHECKS PASSED`, rc=0
- rc=0 for each of: `python3 tests/structure.py`, `node .claude/workflows/policy_lint.mjs`, `node .claude/workflows/rules_sync.mjs --check`, `node .claude/workflows/check-wave-script.mjs`
- stale-lease seams, enumerated by `git grep -n -E "holds flock|renews the lease|TAKE THE LOCK|NO LOCK" -- ':!tools/audit/round*'`, with each seam and its disposition:
  - `.claude/workflows/web-fragments.md` and `web-{decomp-stage,fix-wave,stamp,triage}.js`: **closed here**. They are absent from the enumeration at this head.
  - `tests/gate_lock.py` (the `flock_available` docstring, "holds flock"): says that a child which inherited the fd holds flock. That is true, and it is not the stale claim. Left as is.
  - `tools/audit/round6/D13/fixtures/web-fix-wave-no-merge.js`, excluded above: a round-6 measurement fixture that recounts the old text and does not instruct (fixer step 10). `fragments_sync.mjs` reads only `.claude/workflows/web-*.js`. Left as is.
  - the other lease seams, `tools/audit/README.md` and `.claude/skills/steward/SKILL.md`: `handoff/r9-r4-instruments` closes them. This branch does not touch them.

## Red checks

none

## Forward-carry

none. This corrects a stale instruction to match `gate-scoping.md`; no later stage has to work differently.

## Friction

- fragments-sync: unenforced: `fragments_sync.mjs` pins that the copies agree with `web-fragments.md`, not that the fragment agrees with `run.sh`. The stale sentence passed at the merge base in all five files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
