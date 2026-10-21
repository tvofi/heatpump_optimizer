Group: R10-FLOW-DISPATCH (PR #2577; registration pending: roster PR-B). Repo half of K16 only; the standing triggers are the owner's and are not built. No issue closed (`issues: []`).

`cloud_dispatch.py` gains a one-call path: `dispatch_group(role, group, model)` (CLI: `--role R --group G --model M`). It renders through the unchanged `render()`, publishes `PAYLOAD.json` and `PROMPT.md` on origin as `dispatch/<role>-<topic>` (fast-forward; an identical tree adds nothing; a render refusal pushes nothing) and prints that ref name, the one line a standing trigger is fired with. It is a plain function (returns the ref, raises `Refusal`), so the beat can host it unchanged. The flag path is untouched.

Round 2 (blocked verdict `probe/rev-2577-afe25a70`, orchestrator decisions under mandate 6175172275). Two sources, never one: the brief, the topic and the repository come from the roster at `--roster-ref`, whose default is now `roster_lib.reader_ref` (O17: the round's roster branch, else `origin/main` with the note printed); the head comes from `--head`, else `origin/main`'s tip (`HEAD_REF`), never from the roster ref's tip, which would fork a fixer from the roster branch. A reviewer must pass `--head` (its PR head) and is refused without it, since no ref's tip is a PR head. The two round-1 survivors are pinned: a reviewer check passes an explicit head distinct from every tip and finds it, and not main's tip, in the prompt; `_publish` is called directly with a ref naming a home directory and must refuse and push nothing, so the guard is pinned independently of `render`'s host-path search. The mutant drive lands as `dev/audit/harnesses/r10_flow_dispatch_mutants.py` (fixer.md step 18), so the figures below re-run with one command. Base: PR head 6684dee65 merged with `origin/main` 57f0c9c77 (merge commit 345cbbc36, no conflict).

Reviewer refusal arm, deferred (orchestrator decision 1). The group brief (revision 7) requires the dispatcher to refuse a reviewer dispatch for a head where a required context's latest run has concluded failure, reading R10-FLOW-MAIN-GATE's classifier. That classifier is not on `origin/main` 57f0c9c77 (R10-FLOW-MAIN-GATE has not landed; #2570, at the base, adds only the tick's superseded-cancel rule), and building the arm against the check-runs API here would duplicate the concept the classifier owns, a parallel mechanism fixer.md step 17 rules out. No code is added for it: `dispatch_group("reviewer", ...)` still renders for any head it is given. The arm lands with or after the classifier, reading it. Carry: R10-FLOW-MAIN-GATE (item b87aa9e4)

## Head

742ed664b56b540b1a420fbd8a7b460ae016147b (code head on `handoff/r10-flow-dispatch`).

## Mutation proof

`python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py` at the head above: each mutant is a one-occurrence replacement in `cloud_dispatch.py`, applied alone, the self-test run, the file restored byte for byte (the drive refuses a dirty file and aborts on a pattern not found exactly once).
- head-ignored (`head or _git(...)` -> `_git(...)`): failed=1, `a reviewer is dispatched at the PR head passed, not at a ref's tip`. Round 1's survivor.
- privacy-off (`if why:` -> `if False:` in `_publish`): failed=1, `_publish itself refuses a ref that would publish the host, and pushes nothing`. Round 1's survivor.
- roster-ref-main (`reader_ref(...)` -> `roster_ref or roster_lib.MAIN_REF`): failed=1, `by default the brief is the round's roster branch's and the head is main's tip, not that branch's`.
- head-from-roster-ref (`HEAD_REF` -> `roster_ref` in the head default): failed=1, the same check.
- reviewer-head-off (`if role == "reviewer" and not head:` -> `if False:`): failed=1, `a reviewer needs its PR head`.
- tree-skip (identical-tree return disabled): failed=2, `a re-dispatch of the same brief moves no ref`, `a changed brief fast-forwards the ref`.
- brief-drop (`brief=""`): failed=5, the round-trip, the roster brief inlined, the changed-brief fast-forward, the host path in a roster brief, and the two-sources check. (Round 1's body said 3; at round 1's head it was 4, as the reviewer measured; the new two-sources check adds the fifth.)
- nonce-altered (`nonce + "0"` before render): failed=1, the byte-identical round-trip.
- prompt-wrong (`PROMPT.md` written empty): failed=4, `the ref carries the prompt the payload carries` and the three checks that read the prompt back.
- render-host-off (`m = None` in `render`): failed=5, the four `render` home-path refusals and `a host path in a roster brief refuses and pushes nothing`.
- topic-to-id (ref named by group id): FAIL `a group dispatch prints one short line, the ref name`, FAIL `a reviewer dispatch with pr and nonce renders`, then the self-test dies (a later fetch of the topic ref finds nothing): failed=-1, CRASHED.
- parent-drop (no `-p` in `_publish`): the second dispatch's push is refused non-fast-forward and the self-test dies: failed=-1, CRASHED, no check named.
- roster-repo-ignored (`repo=known["repo"]`): the fixture environment carries no repo, so `render` refuses and the self-test dies: failed=-1, CRASHED, no check named.
`RESULT mutants=13 survived=0`. The two crash-only kills are the drive's own CRASHED class: killed, but by an uncaught refusal rather than a named check.

## Null control

The drive's M0, the file unmutated: `RESULT mutant=M0 failed=0 verdict=null-ok`. `python3 -I tools/audit/seat/cloud_dispatch.py --self-test | tail -1`: `cloud_dispatch self-test: 46 checks, 0 failed` (round 1's 42, less none, plus 4: the reviewer-head refusal, the reviewer at its PR head, `_publish`'s own refusal, the two-sources check). Controls inside the checks: the reviewer's head is a dispatch commit no ref's tip equals, and the check also asserts `origin/main`'s tip is absent from the prompt; the two-sources fixture puts the roster branch one commit ahead of main with its own brief, so reading main's roster or the branch's tip each fails it; the leaked ref is asserted absent from `ls-remote` after the refusal, and pushing that ref name without the guard succeeds (privacy-off above is that run).

## Figures

- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`: `RESULT mutants=13 survived=0`, M0 `failed=0` (per mutant above).
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test | tail -1`: `cloud_dispatch self-test: 46 checks, 0 failed`.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`: `MODE: SCOPED -- 1 script(s) run`, runs `tests/entities.py`; the new harness file is classified (not FULL). `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py | tail -1` (python 3.14.7): `ALL 2382 ENTITY CHECKS PASSED`.
- `run.sh`'s `run_always` lines (venv-ci python 3.14.7, `PYTHONPATH=tests/hastub:custom_components:tests`): `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED` (its inline scan first refused the new harness's `parents[3]` root, so the harness now carries the canonical `repo_root` walk); `tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`; `tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`; `tests/layout.py`: `layout self-test: ok`.
- `python3 tests/structure.py | tail -1`: `STRUCTURE RATCHET PASSED` (no budget touched).
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD | tail -1`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/ref_privacy.py --check | tail -1`: `0 refused` (`cloud_dispatch.py` stays `GUARDED` in `PUSHERS`; its guard is now pinned, above).
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`; `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
- Class seam rule (fixer.md step 8): "an instrument that pushes a ref carries the privacy guard"; instrument `ref_privacy.py --check`, which enumerates every push site against `PUSHERS`; it returns no new site in this round, and the one this PR adds (`cloud_dispatch.py`) is guarded and now pinned. The second seam, "a reader's default roster ref is `default_roster_ref`": `git grep -n "roster_ref.*MAIN_REF\|default=roster_lib.MAIN_REF" -- tools/` prints nothing at the head, where at 6684dee65 it printed `cloud_dispatch.py`'s two defaults.
- `git diff $(git merge-base origin/main HEAD)...HEAD --stat` names six files: `cloud_dispatch.py`, `INSTRUMENTS.md`, `ref_privacy.py`, the new harness, its `tests/closures.json` inert-read entry (written by `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`, after which the same command prints `no closures or fast red predicted`), and the delivery row the orchestrator wrote; `VERSION`, the manifest, `RELEASE_NOTES.md` and every golden and claim file untouched. None matches a `.github/CODEOWNERS` pattern (`grep -nE "closures.json|audit/seat|ref_privacy|cloud_dispatch|INSTRUMENTS|r10_flow" .github/CODEOWNERS` prints nothing; the only `harnesses` entries are the two `README.md` files).

Alternatives considered: the head defaulting to the roster ref's tip (round 1; forks a fixer from the roster branch); the roster defaulting to `origin/main` (round 1; 12 of 108 groups carry a stale brief there, by the reviewer's measurement); a reviewer head defaulting to main (dispatches the reviewer at a tree it is not reviewing; refused instead); building the failed-context refusal on the check-runs API now (duplicates R10-FLOW-MAIN-GATE's classifier; deferred above).

## Red checks

`nightly-status` grades `main`, not this branch: red on main's ancestry, no change here reaches it, and its answer is main's. Carry: dismissed: grades main not this branch
No check red on this branch at round 1's head; `entities.py` and the self-test pass at this head.

## Forward-carry

- Seam with R10-ORCH-MACHINERY (group pack K17 carry): dispatch through `tools/audit/seat/bus.sh` (`dispatch`) so the ledger's `reviewer-fire` close is written, and add the seat to the worker registry the seats job reads (a runtime file, not in the tree). Neither is in this group's `files`; both are that group's seam, so neither is built here: `dispatch_group` takes `pr` and `nonce` for a reviewer but mints neither. Carry: R10-ORCH-MACHINERY (item 92bca45d)

## Friction

none
