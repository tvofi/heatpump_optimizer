Own-seam findings were carried into the same group: R10-BODY-CONTRACT reached 47 carries over 4 parts (triage-ruling-body-contract-hygiene.md, instances table, in the orchestrator's triage directory; it is not tracked in the tree, so `git ls-files` finds nothing). tvofi ruled on 2026-11-08, "Do it, narrow exceptions": the rule is written once, in `dev/governance/roles/fixer.md`, and is policy, so it merges only on tvofi's approval. No automated refusal is added; triage rejected SELF-CARRY-BARRIER on cost.

- fixer.md: a finding in the fixer's own group seam is built in the PR. `Carry: <own group>` is allowed only for a pending owner or orchestrator ruling, or a planned split part.
- finding-propagation.md: one line pointing to fixer.md, no copy.
- fix-review.md: an own-group carry naming neither exception is `blocked <sha> carry-missing: own-group`. This reuses an existing verdict class because a new token must also enter `VERDICT_CLASSES` in `.claude/workflows/web-fix-wave.js`, which would add code to a policy-only PR (found when check-wave-script refused the first token, `carry-own-group`).
- Mirrors `.claude/rules` and `.cursor/rules` regenerated. Budgets were paid by cutting spent prose, no raise: `tools/audit/briefs/fix-review.md` sits exactly at its cap (2451).
- Read for what each sentence newly permits: the new fix-review sentence permits no new carry; the spent prose cut included a `#NNNN` list and two duplicate-ish clauses. The cloud fixer also dropped fix-review.md's closing line "A ruling naming a destination stage states it as a `Carry:` marker." The same sentence stays in judge.md. Restoring it puts the brief over its cap, so it is not restored. tvofi should decide whether that deletion is wanted.

## Approval

The owner directed this edit on 2026-11-08 ("Do it, narrow exceptions") but has not yet approved the merge. The merge waits on tvofi's approving review (`CLAUDE.md`, policy section; code-owner rule).

## Head

00a8f0d7943e7fec0053b9b64dd9bd2fbd56f833 (tree identical to the one prepr ran on at 9d0ce324fb; only author names were reset to hpo-fixer). origin/main unmoved from the base 4fe7d5934b for the diff (owner ruling 2026-11-07: no re-run for a moved main; `git merge-tree --write-tree origin/main HEAD` reports no conflict).

## Mutation proof

No code. Policy-text checks: `node tools/policy/rules_sync.mjs --check` (mirror drift), `node tools/policy/policy_lint.mjs --budgets`, `node tools/policy/brief_lint.mjs`, `node tools/policy/check-wave-script.mjs`. The wave-script check went red (1 of 226) on the first verdict token `carry-own-group`, which is the check refusing an ungrammatical verdict. It is green (226 passed, 0 failed) on `carry-missing: own-group`.

## Null control

Unmodified origin/main: `tests/entities.py` fails the same way (`ModuleNotFoundError: No module named 'homeassistant'` under venv-ci python). This environment gap is not the diff's doing.

## Figures

none

## Red checks

`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` returned rc=0 at 9d0ce324fb. The closures step was skipped under the orchestrator ruling (mandate 6715477401, 2026-11-08): the only refusal was closures failing on `tests/entities.py` for an environment reason, and the diff touches no Python. I ran `tests/entities.py` here with venv-ci python at this head and at origin/main. Both die identically on `homeassistant` not importable, so it is the null control. CI is the authority. The one real red, check-wave-script on the first verdict token, was fixed in this branch.

## Forward-carry

none

## Friction

none
