A reviewer now posts `root-cause-unanswered` only once the head's workflows have concluded and a `pr-contract` run started after them has re-checked the body; while that run refuses the body, the reviewer waits, or hands back without a verdict and says so. Prepping at push is unchanged.

The edits:
- `dev/governance/roles/fix-review.md` step 11 carries the rule.
- `dev/governance/roles/orchestrator.md` section 11 points to step 11.
- `.claude/workflows/web-fix-wave.js` carries the same condition into the wave reviewer prompt, which teaches `root-cause-unanswered`.
- `dev/governance/config/policy_budgets.json` re-records `fix-review.md`'s token cap at the merged file's measure.

Evidence: R9-RCA-2028, section 6, "Not built" item 3, at `dev/audit/rca/R9-RCA-2028.md` on PR #2062's branch (not on main yet).
- 12 of its 19 `root-cause-unanswered` blocks are in two classes: A, where `pr-contract` had already refused the body before the verdict (7 blocks), and B, where the verdict came before the head's workflows concluded (5 blocks).
- Measured as body-only repair rounds, A and B account for 3 of 7 rounds and 341 of 574 minutes. A is 2 rounds and 249 min (#2007, #2049); B is 1 round and 92 min (#2018).
- The RCA states the cost: no compute, and a wait of up to one `Tests` run on a review that would otherwise block.

**Recarry repair.** At the recarry head `ae6fbdd5e` (the judged head `7c1d3b1b7` merged with `origin/main` `a3b83b8ea`) all five reds were one cause. `policy_lint` exited 1 on `dev/governance/roles/fix-review.md`: the branch re-recorded the file's per-file token cap to 2446 (`9784` bytes, its own head's exact measure, zero headroom), and `main` had independently edited the same file in `3adb02cd4`, adding `, or `--carry`s to it.` (21 bytes = 5 tokens). The merge combined both edits and left the file at `9805` bytes = 2451 tokens, 5 over the cap. The branch's own edit was in-budget at its head, so the break came from the merge, not the branch; but the honest cap is the merged file's measure, so the cap is re-recorded to 2451. The five extra tokens are `main`'s own policy text, so no payment inside the file is available. This is the `budget-raise-gate` change in the diff; it merges only on tvofi's approving review at the head.

**Local gate.** `tools/pr/prepr.sh` runs every step green through `claims hygiene`, then the closures step records `tests/entities.py`; that recording's `process_worker.py` child deadlocks on this macOS box (0 % CPU, no return), so the recording never finishes. It is the environment, not this branch: `python3 tests/entities.py` hangs at the same check at a clean `origin/main` worktree (`7cd5a588c`). The recording is left to CI's `closures` job, which runs it on Linux; with it left there (`PREPR_SKIP_CLOSURES=1`) every remaining step, the body contract included, reaches rc=0. No check is weakened.

## Head

The authored code head is `a2576fcb2f0928d0a0fc467bc0ba66d5d629f511` (`handoff/r9-review-timing-r2`), a merge of `7c1d3b1b7` with `origin/main` `7cd5a588cbbbef354c00148040da2d720b8a888c`, re-measured 2026-10-10.

## Approval

**Owner decision**, taken by tvofi in the orchestrator session's chat on 2026-10-08: tvofi chose option 2, settle-then-post, answering "2". The rule is anchored as RCA-2028 section 6 item 3 words it: the reviewer posts only once the head's workflows concluded and a `pr-contract` run started after them re-checked the body; a push-time run that started before they concluded does not count.

**Budget raise.** tvofi confirmed it in the same chat on 2026-10-08, "raise the cap", before this branch was first pushed; that confirmation covered up to 142 lines and 2461 tokens for `fix-review.md`. The raise in the diff is inside that envelope: `fix-review.md` goes from `main`'s 137 lines and 2389 tokens to 140 lines and 2451. Re-recording the cap pays for the branch's own step-11 text plus `main`'s 5-token addition; paying it down inside `fix-review.md` would mean rewording the step-11 rules the pull request exists to add, or deleting `main`'s own text.

`orchestrator.md` pays for its own edit and stays inside its cap (290 lines of 291, 4090 of 4096 tokens). The corpus total moves into its tolerance band: about 59960 tokens over its cap of 59591, within the 500-token band (60091); not a lint error, and the corpus cap is not raised.

Merging still needs tvofi's approving review at the head, required by `budget-raise-gate` (decision 0013) and the code-owner rule.

## Mutation proof

The fix's production line is the cap value in `dev/governance/config/policy_budgets.json`. Set it back to the branch's pre-merge 2446 and the checks below go red; restore to 2451 and they pass.

- **MUTANT (cap 2446):** `node tools/policy/policy_lint.mjs` prints `ERROR   [budgets] tools/audit/briefs/fix-review.md: about 2451 tokens across its lines exceeds its cap of 2446 tokens (files_tokens)` and `TOTAL: 1 error(s) across 40 policy file(s)`, rc=1.
- **MUTANT (cap 2446):** the `tests/entities.py` D11-05 template arm — which runs `policy_lint` and requires rc=0 against the real template — reports `the real template -> rc=1 (must be 0)`, the single `1 of 2243 ENTITY CHECKS FAILED` at that head.
- **HEAD (cap 2451):** `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s) across 40 policy file(s)` and `FIXTURE ok: 92 error(s) hold 243 pins across 12 check classes`, rc=0.
- **HEAD (cap 2451):** the same template arm run in isolation prints `rc_broken=1 (must be 1); rc_live=0 (must be 0)`.

## Null control

At `origin/main` `7cd5a588c` (the unmodified tree): `node tools/policy/policy_lint.mjs` reports `TOTAL: 0 error(s)`, so `main` is not the cause, and `fix-review.md` measures 9555 bytes = 2389 tokens under its cap of 2393. The mutation's own null control is the restored run above: `policy_lint` reads rc=0 at 2451 and rc=1 at 2446, so the red tracks the cap and nothing else.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: per-file lines and tokens — `fix-review.md` 140/2451, `orchestrator.md` 290/4090 — and the always-loaded (~3588) and corpus (~59960) totals, at the head.
- `node tools/policy/policy_lint.mjs`: total errors, at the head and at the mutant cap.
- `wc -c dev/governance/roles/fix-review.md`: 9805 bytes at the head, 9555 at `origin/main`.
- `git merge-base origin/main HEAD` and `git show origin/main:dev/governance/roles/fix-review.md`: the merge base and `main`'s copy.
- `python3 tests/structure.py`: the ratchet verdict.
- `python3 tests/entities.py`: the entity checks, including the D11-05 template arm.
- `git ls-remote origin refs/heads/handoff/r9-review-timing-r2`: the pushed code head.

## Red checks

The recarry head `ae6fbdd5e` carried four failed check runs; all four are one cause — `policy_lint` rc=1 on `main`'s own 5-token addition pushing the merged `fix-review.md` past its cap — and all four clear at the head now that the cap is re-recorded. Each is listed with its cheaper detector.

- `policy-docs`: red on `policy_lint rc=1` (`Lint the policy corpus`). Cheaper detector: `node tools/policy/policy_lint.mjs`, the same program the job runs, after merging `main`; standing cost about 55 s locally against the job's ~0.5 min plus the queue. Cleared by the cap re-record.
- `env-matrix`: red on `FAIL pr / policy_lint rc=0 and every pin earned -- rc=1 pins=243`. Cheaper detector: the same local `policy_lint` run; `env-matrix` adds the six environment shapes on top (~50 s each host). Cleared by the same re-record.
- `instrument-self-tests`: red on `Refuse a corpus or record-mode check that survives its own deletion`, which runs `policy_lint` and sees rc=1. Cheaper detector: the same local `policy_lint` run. Cleared by the same re-record.
- `fast (3.14)`: red on `python3 tests/entities.py` (`1 of 2243 ENTITY CHECKS FAILED`), the D11-05 template arm running `policy_lint` and requiring rc=0. Cheaper detector: the scoped gate, which runs `tests/entities.py` locally (`MODE: SCOPED -- 1 script(s) run`); the arm's own cost is one `policy_lint` run (~55 s). Cleared by the same re-record.
- `budget-raise-gate`: this diff raises a per-file cap in `dev/governance/config/policy_budgets.json` (`fix-review.md` 2393 -> 2451 tokens), so the gate is red until tvofi approves at the head. No cheaper detector exists: the raise is the change, and only the owner's review clears it.

## Forward-carry

`.claude/workflows/web-fix-wave.js`, the reviewer prompt: it now states the settle condition, so a wave-dispatched reviewer gets it as a precondition.

## Friction

`budgets`: `cost`: a per-file token cap has no working band, so a branch that re-records it at its own head's exact measure goes red the moment another lane edits the same file before the merge — this branch recorded `fix-review.md` at 2446 and the merge with `main` left it 5 tokens over.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
