_Requested by **tvofi**_

R9-RO-2, lane RO (the repository reorganisation, `handoff/round9/fix/RO.md` on `handoff/repo-reorg-plan`): the graders learn both paths. **No file moves here, and no restore step changes.**

Six workflow jobs restore their graders from the base, so every later RO pull request is graded by the base's copy of each grader. This change teaches the graders, and the readers of the restore text, both locations before anything moves:

- **One lookup per language.** Node: `moves`/`locate`/`canon`/`listDir`/`lsFiles`/`excludeMoved` in `.claude/workflows/counts.mjs`. Python: `moves`/`locate`/`canon` in `tests/layout.py`. Both read `tests/layout.json`'s `retired` map, plus a new `lifted` entry for tvofi's D1 rule-source lift.
- **How `locate` resolves.** A file is read at its old path while it is there, otherwise at its new path. A directory moves whole, so it resolves new-first. A listing is spelt old (`canon`) before it meets the graders' literals, so every literal and every output stays as it is today.
- **The listed restore form gets its readers.** `codeowners_gap.py`'s `RESTORE` and its allowlist, `prepr.sh`'s pin reader, and `entities.py`'s `_pt_*` and `_restores_workflow_py` all read it. `codeowners_gap` credits a listed restore only when the checkout of the list follows the listing directly. Its `EXEC` admits `dev/`.
- **CODEOWNERS** owns `tests/layout.py`, which pinned graders load, and the new homes of the owned policy paths. `dev/governance/roles/COMMON.md` stays unowned, as its old path is.
- **Harness.** `tools/audit/harnesses/dual_path.py` has four default arms:
  - `graders`: this head's graders on a planted tree with every move applied;
  - `neither`: the refusal is unchanged when the data is at neither path;
  - `ci`: this pull request's own CI, meaning the base's graders over this tree, per job;
  - `shadow`: an unowned copy at a new path cannot stand in for a grown file in use.

**Split (round 2).** Round 1 also changed the restore steps to the listed form. The base's graders grade this pull request, and they could not parse that form, so `policy-docs` and `wave-script` went red. The restore-form change moves to a follow-up, R9-RO-2b, which the parsers landed here will grade. The workflows are now byte-identical to main.

Alternatives rejected:

- **New-first `locate` (round 1).** An unowned copy at a new path shadowed the file in use. The reviewer grew COMMON.md past its cap beside a pristine copy, and policy_lint passed.
- **Refusing a tree that holds both paths.** It would also refuse CI's own composition during a code move, where the restore re-adds the base's files beside the pull request's.
- **Guarding the `layout` import instead of owning `tests/layout.py`.** A guard silently drops the lookup when the base lacks it. Ownership keeps the loaded file under review.
- **Keeping the restore change here behind a no-op line the base parser reads.** That is crediting an unexecuted checkout, the hole item 4 closes.
- **Re-pointing all 320 literal sites.** Each site would need its own planted case, and every output would change.

## Head

1ef3784ca71ab75966862e4af77b04ad31fc8666

## Mutation proof

`tests/mutation_table.py --scope changed` draws nothing, because no production line changed. Each fix was deleted by hand instead, the check run, and the fix restored:

- `counts.mjs` `locate` without the old-file test (that is, new-first): brief_lint `LOCATE VACUOUS`, and dual_path `shadow` at a607db2a reads `shadow_unrefused=2 of 3`.
- `counts.mjs` `canon` replaced by `(p) => p`: on the planted tree, `policy_lint.mjs` rc 1; the old-tree null control stays rc 0.
- `tests/layout.py` `locate` or `canon` replaced by `return p`: `budget_raise_gate.py --self-test` FAILs the moved-budget e2e checks.
- `codeowners_gap.py` without the adjacency rule: `--self-test` reads 3 wrong (the emptied, rewritten and truncated list probes). Without `dev` in `EXEC`: FAIL on the `dev/` EXEC row. Without the listed reader: FAIL on `NULL the listed restore`.

## Null control

`python3 tools/audit/harnesses/dual_path.py`.

- At round-1 head a607db2a, red before: `ci_differ=4 of 16`, which is the reviewer's two reds as four grader rows, and `shadow_unrefused=2 of 3`.
- At the final head less the two closures commits (d2881302; they change only `tests/closures.json`, which the harness does not read), all four default arms re-run after the first closures commit: `graders_differ=0 of 16`, `neither_differ=0 of 14`, `ci_differ=0 of 16`, `shadow_unrefused=0 of 3`.

## Figures

- `python3 tools/audit/harnesses/dual_path.py`, as quoted in Null control.
- `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --self-test`: 50 probes, 9 nulls, 0 wrong. `--check`: `uncovered_files=0`.
- `python3 .claude/workflows/budget_raise_gate.py --self-test`: 202 checks, 0 failed.
- Closures repair, two commits. d2881302: `PYTHON=~/.local/state/hpo/venv-ci/bin/python ./tests/derive_closures.sh --single tests/entities.py` on the macOS host (`sys.addaudithook`; the full derive stays Linux-only) — `closure: updated 1 closure(s)`; the closure gained `tests/layout.json` and `tests/layout.py`. That merge dropped `inert_reads["tests/entities.py"]` (`LICENSE` is opened by processes only Linux `strace` catches, `closure.py` `_union_strace`, R9-F10.9d), so CI's `closures` refused INERT READS UNDER-APPROXIMATED and `closures-autofix` returned `skip-manual-repair-owed`. 1ef3784: `python tests/closure.py merge --in-dir <dir> --partial` over `entities.py.json` from the `closure-recordings` artifact of CI run 37189159395 (Linux, `audithook+sys.modules+strace`, `inert_reads ["LICENSE"]`) — merging CI's own Linux recordings, never recording off Linux; the inert entry is restored and the closure list is unchanged.
- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python tests/entities.py` at 1ef3784: `ALL 2131 ENTITY CHECKS PASSED`. Had the closure repair been wrong, the closures check this feeds would refuse as UNDER-SCOPED or INERT READS, as it did between the two commits.
- `bash tools/audit/prepr.sh --self-test` at d2881302: `148 passed, 0 failed`. 1ef3784 touches only `tests/closures.json`, which the self-test's derived input set does not name.

## Red checks

`closures`: UNDER-SCOPED at round 1 — repaired at d2881302 (Figures), then INERT READS UNDER-APPROXIMATED at d2881302 because the Darwin audithook cannot see strace-only INERT reads — repaired at 1ef3784 by merging CI's own Linux recording (Figures). `closures-autofix`: red at d2881302 with `skip-manual-repair-owed` — the same repair answers it; no bot commit was coming. `nightly-status`: main's scheduled-run state, not this diff's.

## Forward-carry

The round-9 roster lives on the audit-r9-fixplan handoff branch, so the carry text goes to the orchestrator with this hand-off (`RESUME.md`):

- a new group, R9-RO-2b;
- the RO-3..RO-8 move pull requests delete the old file in the same commit, because a leftover old copy is what gets graded;
- `.gitignore`'s `config/` and RO-5;
- the round-1 carries to RO-4, RO-5, RO-6, RO-8 and RO-9.
- NEW, from round 2's closures repair: a Darwin `--single` on a script whose Linux recording carries `inert_reads` drops them (the audithook cannot see strace-only INERT opens) and reddens CI's `closures` the same way — `ci-autofix.md`'s "Darwin is sound for Python lanes" does not hold for the inert dimension; the repair route is merging the CI artifact's recording for that script.

## Friction

none
