Part of #201

Wires the cloud-seat dispatch shape into the operator guide: a new `tools/audit/seat/cloud_dispatch.py` renders the full cloud-runner trigger payload (`job_config.ccr`) for a reviewer, fixer or probe seat, and `tools/audit/seat/INSTRUMENTS.md` records the measured shape of a cloud seat. Until now the payload came from an orchestrator-local `mkrev.sh` that hard-coded the environment id and the model. The `cloud-setup.sh` entry was stale on one point (it implied a seat sources the profile it writes) and is corrected; the script itself is unchanged. Not wired into `governance.yml`'s `instrument-self-tests` (a workflow edit is policy; the self-test runs by hand): the orchestrator decides.

## Head

Code head `0266d022ba0c337700130b20c72e645f4eb18275` on merge base `c8cc75ea90a3bb38dbc6b8dbb7d27d9cce74cdd0` (`origin/main` at 2026-10-18T17:00Z). Everything below was measured at it.

## Mutation proof

Each predicate was replaced in turn (not a line appended past a return) and `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` re-run; every mutant exits 1 and names the checks that went red, then the file was restored (baseline `26 checks, 0 failed`):

- head length test `len(head) == 40` widened to `>= 40`: `a 41-hex head is refused`; made `True`: `a 39-hex head is refused`, `a 41-hex head is refused`
- `if not nonce.strip():` made `if False:`: `an empty reviewer nonce is refused`, `a blank reviewer nonce is refused`
- the home-directory search `m = HOME.search(json.dumps(payload))` made `m = None`: `a macOS home in the brief is refused`, `a linux home in the brief is refused` (and the public-account and nonce arms)
- `if not pr.isdigit():` made `if False:`: `a reviewer without --pr is refused`
- the topic predicate disabled: `a fixer without --topic is refused`, `a topic with a slash is refused`
- the empty environment id / model / repo test disabled: `a missing environment id is refused`, `a missing model is refused`
- hex-set test `set(head) <= LOWER_HEX` made `True`: `an upper-case head is refused`, `a non-hex head is refused`; the set widened to upper case: `an upper-case head is refused`

## Null control

The refusals are graded against a rendering that passes: the first self-test check renders a reviewer from the same inputs every refusal arm perturbs by one field, and a repo-relative brief passes where a brief naming a home directory is refused. A 40-hex lowercase head, a non-empty nonce, a `--pr`, an environment id, a model and an `OWNER/NAME` repo render; remove any one and it refuses. The tree before this change had no renderer at all; `git ls-tree origin/main tools/audit/seat/cloud_dispatch.py` prints nothing.

## Figures

- Self-test: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` prints `cloud_dispatch self-test: 26 checks, 0 failed`.
- Host paths: `python3 -I tools/audit/seat/tmp_paths.py --check` prints `0 refused` and `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused`. Both refused the first draft of this file (a literal home path inside the self-test, and the word sequence `git ... push` in a prompt string); the fix builds the test paths from parts and rewords the prompt. The self-test's home-path arms still fire (mutant above), so the guard was not blinded.
- Agreement lane: the first draft spelled the 40-hex grammar as a regex, which `agreement_py.py` reported `UNREGISTERED` beside `policy_lint.mjs`'s; the head test is now a length and character-set check (the route changed, no registry entry added), and `node .claude/workflows/agreement.mjs --py-json <out of agreement_py.py>` prints `AGREEMENT ok`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, key on the mode line: `MODE: SCOPED -- 0 script(s) run`, changed files `tools/audit/seat/INSTRUMENTS.md` and `tools/audit/seat/cloud_dispatch.py`. Both sit under the `tools/audit/` INERT prefix, so no classification entry is added and none is owed; the file is not one the gate reads.
- Shape source: the orchestrator's `mkrev.sh` template (the live shape); the rendered reviewer prompt differs from it only in naming the evidence directory generically (the template wrote a fixed temp path, which `tmp_paths.py` would refuse in a tracked file) and in taking the repository from a flag.

## Red checks

`none`

## Forward-carry

`none`: the dispatch shape lands in `tools/audit/seat/INSTRUMENTS.md` (the operator guide the orchestrator and seats read). Open question for the orchestrator: wiring `--self-test` into `governance.yml` `instrument-self-tests` (policy surface, not done here).

## Friction

`none`
