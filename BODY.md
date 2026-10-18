Part of #201

Round 3 addendum: `--confirm` (watch and single relay) runs `bus.sh confirm <pr> <review-sha>` only after a `push-verdict` that passed, the sha being the last field of the `review/<pr> <sha>` line it printed, and appends `POSTED` or `OWED` lines to `--log FILE` for the orchestrator (a missing sha or a failed confirm is OWED, never silent). Both arms are self-tested; a refused relay and a failed push-verdict are shown to run no confirm and write no line.

Round 3 (orchestrator): the poll loop was a scratch script, a session-local instrument. `cloud_relay.sh --watch [--interval N] [--once]` now lists `probe/rev-*` with `git ls-remote origin`, relays each ref+sha once (head and full nonce from the dispatch record) and notes a refused ref+sha in `<ledger>.refused` so it is not retried every interval. Chosen as a flag of `cloud_relay.sh`, not a second script: it shares the ledger, `relay()` and the self-test fixtures, and a second script would re-implement the ledger key. The relay also now normalises a bracketed blocked tail `[class: reason]` to `class: reason` and logs `normalised first line: A -> B`. Normalise rather than refuse, because the reviewer is a cloud seat that has already exited, so a refusal costs a full re-dispatch to fix punctuation, and the rewrite is lossless (one outer bracket pair, nothing else changes); anything not exactly that shape (a bracketed merge suffix, nested brackets, a class outside `[a-z-]+`) is refused unchanged, since stripping a merge suffix would lose text. The reviewer brief that taught the brackets (`[class: reason]`, from `mkrev.sh`) was my own template's, so `cloud_dispatch.py`'s prompt now gives the unbracketed grammar (generator fixed, per fixer.md step 10); the grammar check also now matches `bus.sh`'s `verdict_sha` (merge has no tail).

Round 2 (orchestrator, measured): a cloud reviewer's `bus.sh push-verdict` refuses "unknown nonce" because the dispatch record lives only on the orchestrator's machine, and a seat may not write a record it did not mint. So the reviewer role now commits verdict.md (first line, blank line, `bus-nonce: <nonce>`) plus `ev/` to a fresh repo and pushes `probe/rev-<pr>-<nonce8>`; new `tools/audit/seat/cloud_relay.sh <pr> <nonce> <head40>` fetches it, refuses a nonce mismatch, another PR or head and an already-relayed ref, then runs `push-verdict` locally. INSTRUMENTS.md documents both and two traps (update then run sequentially; `env -u BASH_ENV` for `tests/entities.py`). `tools/audit/seat/ref_privacy.py` gains a `prompt` PUSHERS entry for `cloud_dispatch.py`: the reviewer prompt names a push, with the ref built from a PR number and 8 hex digits under a constant identity. The entry is keyed on the file, so it also silences any push the script later gains; the script itself pushes nothing and review owns that.

Wires the cloud-seat dispatch shape into the operator guide: a new `tools/audit/seat/cloud_dispatch.py` renders the full cloud-runner trigger payload (`job_config.ccr`) for a reviewer, fixer or probe seat, and `tools/audit/seat/INSTRUMENTS.md` records the measured shape of a cloud seat. Until now the payload came from an orchestrator-local `mkrev.sh` that hard-coded the environment id and the model. The `cloud-setup.sh` entry was stale on one point (it implied a seat sources the profile it writes) and is corrected; the script itself is unchanged. Not wired into `governance.yml`'s `instrument-self-tests` (a workflow edit is policy; the self-test runs by hand): the orchestrator decides.

## Head

Code head `1acdb3cdc447966e7caa15aacf0d3a9f6509b4a1` on merge base `176851e950a8bea29b0c06f1891b8ce4b83b8836` (`origin/main` at 2026-10-18T17:00Z). Everything below was measured at it.

## Mutation proof

Each predicate was replaced in turn (not a line appended past a return) and `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` re-run; every mutant exits 1 and names the checks that went red, then the file was restored (baseline `28 checks, 0 failed`):

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

- Relay self-test: `bash tools/audit/seat/cloud_relay.sh --self-test` prints `cloud_relay self-test: 40 checks, 0 failed`; mutants (normalisation regex off or loosened to accept nested brackets, merge test loosened to a prefix, class test loosened, the `.refused` check and write removed, the no-record skip removed, the log line removed, confirm forced on or off, the failed-push return dropped, OWED turned into POSTED on a failed confirm and on a missing sha, plus the original ledger test, subject test, nonce test, head test each replaced by `true`/`false`, ledger write removed) each fail named checks. Removing the PUSHERS entry makes `python3 -I tools/audit/seat/ref_privacy.py --check` refuse the push site.
- Entities: `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` prints `ALL 2347 ENTITY CHECKS PASSED` (the scoped gate names it because ref_privacy.py is read by it).
- Self-test: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` prints `cloud_dispatch self-test: 28 checks, 0 failed`.
- Host paths: `python3 -I tools/audit/seat/tmp_paths.py --check` prints `0 refused` and `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused`. Both refused the first draft of this file (a literal home path inside the self-test, and the word sequence `git ... push` in a prompt string); the fix builds the test paths from parts and rewords the prompt. The self-test's home-path arms still fire (mutant above), so the guard was not blinded.
- Agreement lane: the first draft spelled the 40-hex grammar as a regex, which `agreement_py.py` reported `UNREGISTERED` beside `policy_lint.mjs`'s; the head test is now a length and character-set check (the route changed, no registry entry added), and `node .claude/workflows/agreement.mjs --py-json <out of agreement_py.py>` prints `AGREEMENT ok`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, key on the mode line: `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`, via `ref_privacy.py`, already in `INERT_EXCEPT`). `cloud_dispatch.py`, `cloud_relay.sh` and `INSTRUMENTS.md` sit under the `tools/audit/` INERT prefix, so no classification entry is added.
- Shape source: the orchestrator's `mkrev.sh` template (the live shape); the rendered reviewer prompt differs from it only in naming the evidence directory generically (the template wrote a fixed temp path, which `tmp_paths.py` would refuse in a tracked file) and in taking the repository from a flag.

## Red checks

`none`

## Forward-carry

`none`: the dispatch shape lands in `tools/audit/seat/INSTRUMENTS.md` (the operator guide the orchestrator and seats read). Open question for the orchestrator: wiring `--self-test` into `governance.yml` `instrument-self-tests` (policy surface, not done here).

## Friction

`none`
