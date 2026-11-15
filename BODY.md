p1 of the BOOTSTRAP split of R11-PRE-OWNER-CRITERIA (decision 0013, Consequences; fixer.md step 5). It registers `dev/governance/dimensions/criteria/` in `POLICY_GLOBS` in `tools/policy/policy_lint.mjs`: one regex line with its comment, byte-identical to the hunk the group's code head `da868a90ffa56ba62502dde5b1268bbb093c8cd2` (p2) carries, plus a `checkCoverage` acceptance pair beside the existing coverage arms. p2 adds the owner's per-dimension criteria files under that directory; the base's copy of the grader refuses them as `sits in a policy directory and matches no POLICY_GLOBS pattern`, and no change in p2's own pull request can reach the base's copy, so the glob lands first. p2 (`da868a90ffa5`) follows once this merges, as the orchestrator's dispatch.

This is a grader change (a policy path, code-owned): approval under mandate 6893738184. It is the file-level hunk only: no criteria file lands here, so the corpus, the caps and every budget figure are unchanged.

The red it prevents: `governance / policy-docs` on p2, which is in `merge_train.py` owed-reds. The cheaper detector already answered it: `tools/pr/prepr.sh`'s `ci_predict` printed `PREDICT governance / policy-docs GRADER policy_lint.mjs REFUSED by the base's copy ... -- BOOTSTRAP` before any pull request existed (BLOCKED.md at `handoff-wip/r11-pre-owner-criteria`, 8321dd2e27d5).

## Head

ee230f08557adf1bc84e0cabf5165b705fd6f23c on origin/main 646352ff13 (Sun Nov 15 2026).

## Mutation proof

Predicate mutated: the one regex line `/^dev\/governance\/dimensions\/criteria\/[A-Za-z0-9_.-]+\.md$/` removed from `POLICY_GLOBS`, then `node tools/policy/policy_lint.mjs`: `FIXTURE OVER-FIRES: checkCoverage reported dev/governance/dimensions/criteria/D10-criteria.md ... The criteria directory is a policy directory with its own glob.`, exit 1 (the new `covCriteria` arm). Restored: exit 0, `FIXTURE ok: 93 error(s) hold 278 pins`. The deep-path arm (`criteria/sub/D10-criteria.md` must stay reported) would go red if the glob were widened to a subtree.

## Null control

At origin/main (no hunk), a throwaway tracked file `dev/governance/dimensions/criteria/X-criteria.md`: `node tools/policy/policy_lint.mjs` printed `ERROR [coverage] dev/governance/dimensions/criteria/X-criteria.md: sits in a policy directory and matches no POLICY_GLOBS pattern` and `TOTAL: 1 error(s)`. With the hunk, the same file draws no `[coverage]` error (it draws only `[index]` and `[budgets]` ones, the deliberate classification a real criteria file owes, which p2 supplies) and `TOTAL` is 2 from those alone. The throwaway file is not in the commit.

## Figures

- `node tools/policy/policy_lint.mjs` at the head, directory empty: `TOTAL: 0 error(s) across 52 policy file(s)` and `FIXTURE ok: 93 error(s) hold 278 pins` (276 at origin/main; the two new pins are the new arms).
- `node tools/policy/policy_lint.mjs --budgets` at origin/main and at the head, diffed: the only difference is a trailing shell `exit=` line I appended, so the budget figures are unchanged (`diff` over both outputs).
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Gate scope: this is a policy-path diff, run by prepr in hotfix scope (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`), CI is the authority.

## Red checks

none. The cheaper detector for the red this prevents is `prepr.sh`'s `ci_predict` BOOTSTRAP line, already in place; it fired at p2's prepr and found this split.

## Forward-carry

none

## Friction

none
