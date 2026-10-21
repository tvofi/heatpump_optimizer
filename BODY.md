Group: R10-FLOW-DISPATCH (PR #2577), round 3. No issue closed (`issues: []`). Blocked verdict `probe/rev-2577-e26587b4`: four mutants survived on the group path. This round adds three self-test checks in `_group_checks` that kill them, and the mutant drive gains the four. No production line changes. Base: PR head 69a429cfa merged with `origin/main` 5a755f53e (no conflict; main's tip stamped 2026-10-21 22:13 UTC).

Reviewer refusal arm, still deferred: R10-FLOW-MAIN-GATE's classifier is not on `origin/main`, and `dispatch_group("reviewer", ...)` still renders for any head. Carry: R10-FLOW-MAIN-GATE (item b87aa9e4)

## Head

11c9209a5b0429e18bc00a5f01b367762d4332ed (code head on `handoff/r10-flow-dispatch`).

## Mutation proof

`python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py` at the head above. Each mutant is one replacement in `cloud_dispatch.py`, applied alone, then the file is restored. Round 3's four:
- explicit-roster-ref-ignored (`reader_ref(repo_dir, roster_ref)` -> `reader_ref(repo_dir, None)`): failed=2, `an explicit roster ref is read, not the round's roster branch`, `the --group CLI passes --head and --roster-ref through`. Carry: dismissed: fixed in this diff (item 61800936)
- cli-head-dropped (`head=args.head or ""` -> `head=""`): failed=2, `the --group CLI passes --head and --roster-ref through`, `a re-dispatch from a second clone fast-forwards the existing ref`. Carry: dismissed: fixed in this diff (item 83f73eb7)
- cli-roster-ref-dropped (`roster_ref=args.roster_ref,` -> `roster_ref=None,`): failed=1, `the --group CLI passes --head and --roster-ref through`. Carry: dismissed: fixed in this diff (item 83f73eb7)
- fetch-skipped (`_publish`'s fetch of the existing ref -> `pass`): failed=1, `a re-dispatch from a second clone fast-forwards the existing ref`. The second clone is `--no-local --single-branch --branch main`. A plain local clone copies every object, so the tip would already be local and the mutant survived (measured: failed=0 at 70f1d19c3 and at 2f7137eed, the two intermediate commits). Carry: dismissed: fixed in this diff (item 695058e1)

The other 13 mutants keep their verdicts: 10 killed by named checks, and topic-to-id, parent-drop and roster-repo-ignored CRASHED. `RESULT mutants=17 survived=0`.

The near-equivalent mutant, `ref_privacy.refusal` run on a constant ref in `_publish`, is not pinned. The commit message carries the same home path, and git's ref-name check stands behind `_REF_CHARS`. Carry: dismissed: home-path case caught by the message check (item bd9a4d57)

## Null control

The drive's M0, the file unmutated: `RESULT mutant=M0 failed=0 verdict=null-ok`. `cloud_dispatch.py --self-test`: 51 checks, 0 failed at the head; 32 at `origin/main` 5a755f53e; 48 at 69a429cfa. The three added checks are this round's. Carry: dismissed: re-measured at this head (item 15632c35). Each check's own control: main's roster carries `Changed.` and the round branch carries `On the branch.`, so reading the default ref fails the explicit-ref and CLI checks. The CLI's `--head` is a dispatch commit distinct from main's tip, and the check asserts main's tip is absent. The second clone's dispatch changes the head, so it must write a commit whose parent is the prior tip.

## Figures

- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`: `RESULT mutants=17 survived=0`, M0 `failed=0` (venv-ci python 3.14.7). The same drive at 9dc32da66, before the closures line, printed the same.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test | tail -1`: `cloud_dispatch self-test: 51 checks, 0 failed` (python 3.11.17 and venv-ci 3.14.7).
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, runs `tests/entities.py`. `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py | tail -1`: `ALL 2382 ENTITY CHECKS PASSED`.
- `run.sh`'s `run_always` lines (venv-ci python 3.14.7, `PYTHONPATH=tests/hastub:custom_components:tests`): `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`; `tests/env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok`; `tests/closure.py selftest` prints `ALL 124 closure shrink pins PASSED`; `tests/layout.py` prints `layout self-test: ok`.
- `python3 tests/structure.py | tail -1`: `STRUCTURE RATCHET PASSED` (no budget touched)
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD | tail -1`: `Architecture score: dS +0.0000 NULL`
- `python3 -I tools/audit/seat/ref_privacy.py --check | tail -1`: `0 refused`; `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`; `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused` (the new clone goes through `throwaway_git_clone`).
- Class seam rule (fixer.md step 8): "every input the group path accepts reaches the payload". The rule that enumerates it is the parameter list of `dispatch_group` and the `--group` call in `main`. Each input and its pin: `role`, `group_id` and `model` by the round-trip; `roster_ref` default (roster-ref-main) and explicit (explicit-roster-ref-ignored); `head` default (head-from-roster-ref) and explicit (head-ignored); `pr` and `nonce` by the reviewer checks and nonce-altered; `overlay` and `environ` by `an unknown environment refuses` and the CLI check's overlay. CLI pass-through: `--head` and `--roster-ref` (this round), `--model` refused when missing (render's own check). `repo_dir` is the CLI's cwd, and the CLI check runs in the fixture's checkout.
- `git diff $(git merge-base origin/main HEAD)...HEAD --stat`: six files, the same set as at 69a429cfa. This round adds one `tests/closures.json` line: `tools/audit/seat/cloud_dispatch.py` as an inert read of `tests/entities.py`, written by `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`. Before it, the predictor printed `1 predicted red(s) on closures`; after it, `no closures or fast red predicted`. `VERSION`, the manifest, `RELEASE_NOTES.md`, goldens and claim files are untouched.

## Red checks

`nightly-status` grades `main`, not this branch; no change here reaches it. Carry: dismissed: grades main not this branch
`ci-ratchet` red on main is runner-speed variance; it was skipped on this PR. Carry: R10-CI-LAYOUT
No other check is red at 69a429cfa (check-runs API, 49 runs). CI has not yet run at this head.

## Forward-carry

- Seam with R10-ORCH-MACHINERY (K17): dispatch through `bus.sh dispatch` and the worker registry are that group's. Carry: R10-ORCH-MACHINERY (item 92bca45d)

## Friction

none
