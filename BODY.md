Group: R10-FLOW-DISPATCH (PR #2577). No issue closed (`issues: []`). Round 4, so this body is a re-cut (fixer.md, "Past three rounds"). The PR adds the group path to `tools/audit/seat/cloud_dispatch.py`: `dispatch_group()` and `--group` render one seat from the roster, publish it to `dispatch/<role>-<topic>` on origin and print that ref name. The round-3 verdict (`origin/review/2577`) blocked on three `--group` CLI inputs that no check pinned: `--role`, `--pr` and `--nonce`. This round adds one self-test check in `_group_checks` that drives `main()` as a reviewer with a second roster group, its own model, pr and nonce, and asserts every one of those values on the published ref. The `--group` and `--model` constants (cli-group-fixed, cli-model-fixed) survived the same way and are pinned by the same check. No production line changes this round. Base: the code head 11c9209a5 merged with `origin/main` 46e368127 (no conflict; main's tip committed 2026-10-22T00:13:54Z, measured at 2026-10-22T00:38Z).

Reviewer refusal arm, still deferred: R10-FLOW-MAIN-GATE's classifier is not on `origin/main`, so `dispatch_group("reviewer", ...)` still renders for any head. Carry: R10-FLOW-MAIN-GATE (item b87aa9e4)

## Head

d2154512250c0b78d59356c168892767a1de37cb (code head on `handoff/r10-flow-dispatch`).

## Mutation proof

Instrument: `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`. Each mutant is one replacement in `cloud_dispatch.py`, applied alone; then `cloud_dispatch.py --self-test` runs and the file is restored byte for byte. This round's mutants, red first. With the new check stashed (the tree at ecff263a6 less the `cloud_dispatch.py` hunk):
- cli-role-fixed (`dispatch_group(args.role,` -> `dispatch_group("fixer",`): failed=0, SURVIVED.
- cli-pr-dropped (`pr=args.pr,` -> `pr="",` in the `--group` call): failed=0, SURVIVED.
- cli-nonce-dropped (`nonce=args.nonce,` -> `nonce="",` in the `--group` call): failed=0, SURVIVED.
- cli-group-fixed (`args.group` -> `"R10-X"`, the fixture's group) and cli-model-fixed (`args.model` -> `"m-1"`, every other call's model): failed=0 each, SURVIVED, on the tree at ae9be31f8 less its `cloud_dispatch.py` hunk.

At the head, each is killed by the one new check, `the --group CLI passes --role, --group, --model, --pr and --nonce through`, failed=1 each. cli-overlay-dropped (`overlay=args.overlay` -> `overlay=None`) joins the drive, already killed: failed=3. Carry: dismissed: fixed in this diff

The full drive at the head: 23 mutants, `RESULT mutants=23 survived=0`. 20 are killed by named checks. parent-drop, topic-to-id and roster-repo-ignored are CRASHED (a self-test that died before its summary line; killed, but no check names the break).

The near-equivalent `ref_privacy.refusal` on a constant ref in `_publish` (privacy-checks-message-only) is not pinned: the commit message carries the same home path, and git's ref-name check stands behind `_REF_CHARS`. Carry: dismissed: home-path case caught by the message check (item bd9a4d57)
cli-model-check-off and flagpath-head-required-off are equivalent: render refuses a missing model and a non-hex head (rc=2), so neither yields a silent wrong result. Carry: dismissed: equivalent, the refusal is render's own

## Null control

The drive's M0, the file unmutated: `RESULT mutant=M0 failed=0 verdict=null-ok`, at the head and in each red run above. `cloud_dispatch.py --self-test`: 52 checks, 0 failed at the head; 51 at 973a07983 (the merged base before this round); 32 at `origin/main` 46e368127. The one added check is this round's. Each value it asserts is distinct from every earlier call in the fixture (group `R10-Y` with topic `r10-y`, model `m-9`, pr `8`, nonce `def456`), so no earlier dispatch could have published it; a role, group or pr/nonce mutant publishes no `dispatch/reviewer-r10-y` ref, which the check reads as a failure by name, not a crash.

## Figures

- Finder's harness, both ends: the round-3 reviewer's drive, `git show origin/review/2577:evidence/mydrive_r3.py` (sha1 b30194ef708c52f9f166c427ef863f279db6c231), run as `python3 -I mydrive_r3.py <worktree>`. At 973a07983: `RESULT mutants=6 survived=3` (cli-pr-dropped, cli-nonce-dropped, cli-role-fixed at failed=0). At the head: `RESULT mutants=6 survived=0`; the three are killed (failed=1 each), cli-overlay-dropped killed (failed=3), pr-dropped-api and nonce-dropped-api CRASHED as at 973a07983. Its null control is the change of verdict between the two ends on the same script.
- The round-2 reviewer's drive, `git show origin/review/2577:evidence/prev_mydrive.py` (sha1 c58fb9b816679c7d4ca50527da7348b01304e265), at the head: `RESULT mutants=10 survived=3`, the three equivalents dispositioned under Mutation proof.
- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`: `RESULT mutants=23 survived=0`, M0 `failed=0` (python 3.11.17).
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test | tail -1`: `cloud_dispatch self-test: 52 checks, 0 failed`.
- Class seam rule (fixer.md step 8): every input main()'s `--group` branch accepts reaches the published ref. The rule that enumerates the seams is the argument list of the one `dispatch_group(...)` call inside `main`, read by AST: `python3 -c 'import ast,sys; f=next(n for n in ast.parse(open(sys.argv[1]).read()).body if getattr(n,"name","")=="main"); c=[n for n in ast.walk(f) if isinstance(n,ast.Call) and getattr(n.func,"id","")=="dispatch_group"]; assert len(c)==1; [print(ast.unparse(a)) for a in c[0].args]; [print(k.arg) for k in c[0].keywords]' tools/audit/seat/cloud_dispatch.py`. It prints 8 seams. Null control: the same command on a copy with `environ=None` added to the call prints 9. Each flag and its pin:
  - `--role` (`args.role`): the new reviewer CLI check; cli-role-fixed killed.
  - `--group` (`args.group`): the new reviewer CLI check (group `R10-Y`); cli-group-fixed killed; dropped, it refuses (no roster group).
  - `--model` (`args.model`): the new reviewer CLI check (`session_context.model == "m-9"`); cli-model-fixed killed; dropped, render refuses.
  - `--roster-ref` (`roster_ref=args.roster_ref`): `the --group CLI passes --head and --roster-ref through`; cli-roster-ref-dropped killed.
  - `--head` (`head=args.head or ""`): the same check and the new one; cli-head-dropped killed (failed=3).
  - `--pr` (`pr=args.pr`): the new reviewer CLI check (`PR #8 `); cli-pr-dropped killed.
  - `--nonce` (`nonce=args.nonce`): the new reviewer CLI check (`Bus nonce: def456.`); cli-nonce-dropped killed.
  - `--overlay` (`overlay=args.overlay`): both CLI checks (the fixture's only environment id is in the overlay); cli-overlay-dropped killed (failed=3).
  The API half, `dispatch_group`'s own parameters, is pinned by the earlier checks: roster_ref default (roster-ref-main) and explicit (explicit-roster-ref-ignored), head default (head-from-roster-ref) and explicit (head-ignored), pr and nonce (the reviewer refusals and nonce-altered), environ (`an unknown environment refuses`), repo_dir (every fixture call).
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, runs `tests/entities.py`. `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py | tail -1`: `ALL 2382 ENTITY CHECKS PASSED`.
- `run.sh`'s `run_always` lines (venv-ci python 3.14.7, `PYTHONPATH=tests/hastub:custom_components:tests`): `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`; `tests/env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok`; `tests/closure.py selftest` prints `ALL 124 closure shrink pins PASSED`; `tests/layout.py` prints `layout self-test: ok`.
- `python3 tests/structure.py | tail -1`: `STRUCTURE RATCHET PASSED` (no budget touched)
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD | tail -1`: `Architecture score: dS +0.0000 NULL`
- `python3 -I tools/audit/seat/ref_privacy.py --check | tail -1`: `0 refused`; `python3 -I tools/audit/seat/tmp_paths.py --check | tail -1`: `0 refused`; `python3 -I tests/throwaway_git.py --check | tail -1`: `0 raw git init or clone site(s) refused`
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main | tail -1`: `CI PREDICT: no closures or fast red predicted`
- `git diff $(git merge-base origin/main HEAD)...HEAD --stat | tail -1`: `6 files changed, 428 insertions(+), 15 deletions(-)`. `git diff $(git merge-base origin/main HEAD)...HEAD --stat -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden tests/golden/claimed_drift.txt | wc -l` prints 0: `VERSION`, the manifest, `RELEASE_NOTES.md`, goldens and claim files are untouched.

## Red checks

From the check-runs API, per commit. 997dadc90 (the PR head before this round; the same tree as 11c9209a5): 49 runs, one `failure`, `nightly-status`; every other run `success` or `skipped`. The commits this round adds (ecff263a6, ae9be31f8, d21545122) and the merge 973a07983 are not yet on the PR branch, so they carry no check runs.
`nightly-status` grades `main`, not this branch; no change here reaches it. Carry: dismissed: grades main not this branch
`ci-ratchet`, red on main, is runner-speed variance; it is skipped on this PR. Carry: R10-CI-LAYOUT

## Forward-carry

- Seam with R10-ORCH-MACHINERY (K17): dispatch through `bus.sh dispatch` and the worker registry are that group's. Carry: R10-ORCH-MACHINERY (item 92bca45d)

## Friction

none
