Group: R10-FLOW-DISPATCH (registration pending: roster PR-B). Repo half of K16 only; the standing triggers are the owner's and are not built. No issue closed (`issues: []`).

`cloud_dispatch.py` gains a one-call path: `dispatch_group(role, group, model)` (CLI: `--role R --group G --model M`). The roster at `--roster-ref` (default `origin/main`) gives the brief, the topic (the group's branch) and the repository; the head is that ref's tip; the environment id comes from the known seat environment (overlay / `HPO_CLOUD_ENV_ID`). It renders through the unchanged `render()`, publishes `PAYLOAD.json` and `PROMPT.md` on origin as `dispatch/<role>-<topic>` (fast-forward, identical tree adds nothing, a render refusal pushes nothing) and prints that ref name, the one line a standing trigger is fired with. It is a plain function (returns the ref; raises `Refusal`), so the beat can host it unchanged. The old flags are untouched. Base: fetched 929275e8a, cut from `origin/main` b6a38f858 (a descendant).

## Head

d45f4b49bb5efb5580bdbb72af268f3709bc842b (code head on `handoff/r10-flow-dispatch`).

## Mutation proof

Failing test first: with only the new checks in `_group_checks` and no `dispatch_group`, `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` died at the first group check (`NameError: name 'roster_lib' is not defined`). Then, one predicate at a time, restored after each (self-test = the closure's check, `governance.yml` "cloud_dispatch self-test"):
- tree-equality skip in `_publish` removed: FAIL `a re-dispatch of the same brief moves no ref`, `a changed brief fast-forwards the ref` (2 failed).
- roster brief dropped from the render (`brief=""`): FAIL `the printed line round-trips to a payload byte-identical to today's flag path`, `the roster brief is inlined and the roster tip is the head`, `a changed brief fast-forwards the ref` (3 failed).
- parent commit dropped in `_publish`: traceback (push refused non-fast-forward), self-test dies.
- nonce altered before render: FAIL `the printed line round-trips ...` (1 failed).
- ref named by group id instead of topic: FAIL `a group dispatch prints one short line, the ref name`, `a reviewer dispatch with pr and nonce renders` (2 failed).
- host-path search in `render` disabled (`m = None`): FAIL `a macOS home in the brief is refused`, `a linux home ...`, `a public account's home ...`, `a home path in the nonce is refused`, `a host path in a roster brief refuses and pushes nothing` (5 failed). A first draft of that last check was vacuous (the fixture roster dropped the bad group, so it refused for "no such group"); the second `land` now keeps it, and the mutant above is what shows it live.

## Null control

Unmodified tree, same self-test: 42 checks, 0 failed (`python3 -I tools/audit/seat/cloud_dispatch.py --self-test | tail -1`). Controls in the test: a clean-brief group dispatch passes where the host-path one refuses (same roster, same call); the flag path run through `main()` with the roster brief as `--brief` is the byte-for-byte oracle for the fetched `PAYLOAD.json`; `ls-remote refs/heads/dispatch/*` lists exactly one ref after the refused group was tried.

## Figures

- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test | tail -1`: `cloud_dispatch self-test: 42 checks, 0 failed` (the 27 pre-existing checks unchanged, 15 new).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED`, runs `tests/entities.py`; `PYTHONPATH=tests/hastub python3 tests/entities.py` (venv-ci python 3.14.7): `ALL 2375 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py | tail -1`: `STRUCTURE RATCHET PASSED` (no budget touched).
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`; `cloud_dispatch.py` moves from `prompt` to `GUARDED` in `PUSHERS` because it now has a push site, and calls `ref_privacy.refusal` on the ref and message.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`; `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +0.0000 NULL`.
- Class seam rule (fixer.md step 8): the seam is "an instrument that pushes a ref carries the privacy guard". Instrument: `ref_privacy.py --check` (enumerates every push site against `PUSHERS`); it returned the one new site (`cloud_dispatch.py`), dispositioned above as guarded. `GOLDEN_MODE=drift`: no golden or claim file touched, `VERSION`, manifest and `RELEASE_NOTES.md` untouched (`git diff $(git merge-base origin/main HEAD)...HEAD --stat` names three files).
- Code-owned: none of the three touched files (`tools/audit/seat/cloud_dispatch.py`, `INSTRUMENTS.md`, `ref_privacy.py`) matches a `.github/CODEOWNERS` pattern (`grep -nE "audit/seat|ref_privacy|cloud_dispatch|INSTRUMENTS" .github/CODEOWNERS` prints nothing).

Alternatives considered: a `--payload-file` flag set (what the flags path already does; leaves the three-step cost and the two trigger bodies); writing only the brief to the ref (the seat would re-render; the byte-identical control would not hold). Design choices stated: the ref carries both the exact payload and the prompt text; the repository comes from the roster's `repo` key, falling back to `HPO_CLOUD_REPO`; the environment id is never read from the tree.

## Red checks

none (no check red on this branch; `entities.py` 2375 pass, structure passes). `nightly-status` grades main, not this branch.

## Forward-carry

Seam note for the groups that consume this: the owner half (three standing trigger prompts: Opus fixer, Opus reviewer, Sonnet fixer, each fetching `dispatch/<role>-<topic>`) is the owner's, per R15; the seam with R10-ORCH-MACHINERY (dispatch through `bus.sh dispatch` so the `reviewer-fire` close is written) is not built here: `dispatch_group` takes `pr` and `nonce` for a reviewer but mints neither. Carry: R10-ORCH-MACHINERY (already carries this seam in the roster group `carry`; no pending group is pointed to).

## Friction

none
