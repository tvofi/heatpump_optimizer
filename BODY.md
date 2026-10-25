R10-DIAG-REDACT: Download diagnostics now redacts each value its keyed passes remove wherever else that value reaches. Part of #2271; whether #2271 can close is the orchestrator's call (see Forward-carry).

The download's redaction (`diagnostics.async_get_config_entry_diagnostics`) is keyed. `async_redact_data(..., TO_REDACT)` blanks `tibber_token` and `name`, and `_coarsen` cuts `latitude`/`longitude`, but only under those keys. A copy of the token, the entry name or the exact coordinate under any other key, inside a message, as a key, or as a number under `lat`/`lon` went out unredacted. D15's production triage (the group's first carry) found redacted credential values surviving elsewhere in the same payload.

The fix is one value pass, owned by `diagnostics.py`:
- `_private_values` collects the text of every value the keyed passes remove from the entry's own `data` and `options`: each value under a `TO_REDACT` key, and each coordinate the coarsening cuts.
- After the existing three passes, `_without_values` redacts each of those values anywhere in the payload: inside a string, as a dict key, and as a number whose text matches. Tuples are handled too.
- A value shorter than `replay_doc.LEAK_MIN_CHARS` is not searched for. That is the replay seal's existing bound of 6. It is now named in `replay_doc` and read by both leak checks, so there is one bound, not two literals.

Alternatives considered:
- (a) Widen `TO_REDACT` to `replay_doc.SECRET_KEY`. Rejected: this is still keyed, so it closes no path where a value sits under an innocent key or in text. It would also blank the `tibber_reauth_started` flag that support reads.
- (b) Redact the values at each producer: store writers, self-test texts, payload. Rejected: one rule would be spread over every writer, and the next writer would be unguarded.
- (c) Refuse the whole download, as `replay_doc.seal` refuses a document. Rejected: a diagnostics file must still download, and over-redaction there fails safe (module docstring).

The value pass runs on every download, whatever path a value took, so it closes the class.

## Head

The head is `c11ecdff359b` (`handoff/r10-diag-redact`). It differs from `4f5bc8ab1d88`, where the gate and mutants ran, only by renaming a test-local set in `tests/debug_collect.py` (`_kept` → `_untouched`, for `closure.py no-copies`). At `c11ecdff359b`: `tests/debug_collect.py` passes all 128 checks, and `python3 tests/closure.py no-copies` reports no copies. The merge base is `da12aa37dee1`, which was `origin/main` at 2026-10-25T17:00Z.

## Mutation proof

Each mutant was applied to the head, then `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` was run. Every mutant is killed:
- Value pass deleted (`redacted: dict[str, Any] = _without_values(async_redact_data(` → identity; re-run at `4f5bc8ab1d88`; the others ran at `7c0f3c649ef1`, whose production lines are the same except that binding). FAIL: `Download diagnostics carries none of the values its redaction removes -- ...`
- `len(text) >= replay_doc.LEAK_MIN_CHARS` → `>`. FAIL: `the value pass searches for a removed value at the leak check's shortest length ...`
- Coordinate cut predicate removed (`and _coordinate(node) != node`). FAIL: same check.
- `isinstance(value, (list, tuple))` → `list`. FAIL: `the value pass redacts a private value inside text, as a key, and as a number, in a tuple too ...`
- Keys not passed (`{key: _without_values(...)}`). FAIL: both checks above.
- Number arm returns `value`. FAIL: both checks above.
- Options not read (`[dict(entry.data)]`). FAIL: `Download diagnostics carries none ...`. The fixture plants a token that only `options` holds.
- `replay_doc.LEAK_MIN_CHARS = 7`, and `len(s) >= LEAK_MIN_CHARS` → `>` in `seal`. FAIL: `replay_doc.seal refuses a document where a dropped credential survives elsewhere ...`

## Null control

- Unmodified tree: `diagnostics.py` and `replay_doc.py` at the merge base, with this branch's test. The new check fails with 14 carrying paths: `.config.ecl110_state_topic; .config_setup.ecl110_state_topic; .coordinator.mode; .debug.cycle_rows[0].lon; .debug.cycle_rows[0].note; .debug.cycle_rows[0].<token as key>; .debug.diagnostics.mode; .debug.manifest.self_tests.feeds.error; .debug.payload_snapshots[0].data.msg; .debug.stores.heatpump_optimizer_rp_accuracy.lat; .debug.stores.heatpump_optimizer_rp_accuracy.note; .inputs.problem_messages[0]; .last_diagnosis; .plan.current_action`. At the head the count is 0. (The `.learning` plant was added after this baseline run.)
- Non-sensitive fields are byte-identical, checked two ways in `tests/debug_collect.py`:
  - A clean install's download is compared, with `sort_keys=True`, with the value pass on and switched off: `json.dumps` is identical.
  - In the planted download, every field whose path and value hold no private text is compared between pass on and pass off: no field differs.
- The controls' own perturbation: adding `'Europe/Stockholm'` to the private set fails both null controls, along with 23 other checks. So the controls do detect over-redaction.
- The section census is derived from the download's own keys and its bundle's keys, minus five named exempt sections. Removing the `.learning` plant makes it fail with `unplanted=['.learning']`.

## Figures

- Paths carrying a private value in the planted download: 14 at the merge base, 0 at the head. Command: `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`; the detail of check `Download diagnostics carries none ...` lists the paths. Rule: a path counts when its key or value contains the token, the options token, the entry name or the exact coordinate text.
- Mutants killed: 9 of 9. Same command, with each mutant above applied.
- Architecture score: `python3 tools/audit/archscore/score.py --diff da12aa37dee1 HEAD` printed `Architecture score: dS +0.0000 NULL`.
- Scoped gate at `4f5bc8ab1d88`, from `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=da12aa37dee1 bash tests/run.sh`. It printed `MODE: SCOPED -- 14 script(s) run, 19 scoped out.`
  - Every script ran ok except `tests/entities.py`, which reported 2 of 2445 failed: `gate-sweep.yml: on CI's completion, ...` and `graders-head-copy's delivery_status step is red only when ...`.
  - The same two fail at the merge base `da12aa37dee1` with this diff absent (`PYTHONPATH=tests/hastub python3 tests/entities.py` there: 2 of 2445 failed, the same two names). Neither check reads `diagnostics.py` or `replay_doc.py`, so neither failure is this branch's.
  - `tests/typing_ruler.py`, with the pinned census under `HPO_TYPING_PYTHON`, passes at the head. An earlier head `7c0f3c649ef1` failed it with `by_code[no-any-return]` +1, from `return _without_values(...)`; `4f5bc8ab1d88` binds that result to `dict[str, Any]`.

## Unpinned sites

- `custom_components/heatpump_optimizer/diagnostics.py:113 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:115 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:117 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:119 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:121 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:121 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:121 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:126 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:129 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:130 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:133 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:135 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:138 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/diagnostics.py:319 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/replay_doc.py:101 CONST`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/replay_doc.py:507 BOOLOP`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/replay_doc.py:507 CMP_BOUND`: pinned by mutation-autofix

## Red checks

- `mutation`: predicted red. Its cause is the 17 sites under `## Unpinned sites`, which no ledger pin covers until `mutation-autofix` pins them after the push (`ci-autofix.md`). This is not a defect: each site is in `custom_components/`, which is that lane's scope, and the mutants listed under `## Mutation proof` show the checks in `tests/debug_collect.py` kill them. The cheaper detector already exists and ran here: `prepr.sh` step 6d, through `tools/pr/ci_predict.py`. Its standing cost is the predictor's seconds per handoff. No further detector is owed.

## Forward-carry

- Neither the owner bundle nor the triage record is in the tree, so I could not reproduce the two values the triage named. If they were values the replay sanitiser dropped from recorded attributes, that path is untouched: `replay_doc.seal` still refuses a document in which a dropped value survives (the existing check `replay_doc.seal refuses a document where a dropped credential survives elsewhere ...` passes at the head). This PR's pass guarantees only the keyed diagnostics values. R10-REPLAY-REAL-DAY's precondition ("R10-DIAG-REDACT's redaction holds on the exported document") is therefore met only by running `export.check_file` and `seal` on the owner's own exported day, not by this merge. The destination is that group's brief in `dev/programme/rosters/wave-r10-groups.json`. This seat may write only its return refs, so the orchestrator owes the roster edit. Carry: R10-REPLAY-REAL-DAY

## Friction

none
