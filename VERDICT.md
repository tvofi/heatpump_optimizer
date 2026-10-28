Fix review: blocked a7411d7ad644c1546b4dd4cf1ad34613cd61ca2a class-open: an over-limit part-load derate is still silently read as 0 when the Modbus pre-fill save narrows the power band, because _prefill_errors never runs _partload_errors

bus-nonce: dadb85f46fa24fe0cab2b4caa4b0d09c

Cloud reviewer seat. Head measured: `a7411d7ad644c1546b4dd4cf1ad34613cd61ca2a`, the head the PR body's `## Head` names. The round-1 review blocked `ea4630ace`. I could find no posted later review, so this is at least round 2 of review for this group. The brief's added check came from a previous reviewer's flag. This review answers it, and the check fails.

## Block

The brief asks for proof that no over-limit derate is silently treated as 0 at this head. One reachable path still does that.

- `_partload_derate` (`thermal_model.py`, `ThermalParameters.clamp`) refuses a derate at or past `band / (band + p_max)` and returns 0. It logs nothing and raises nothing. Its docstring says "the options page names the refusal on the field".
- That holds only for the `thermal_model` options page (`config_flow.py:3270`, `_power_errors(...) or _partload_errors(...)`).
- The Modbus pre-fill save is a second writer of `heat_pump_max_power`. `modbus_prefill._plant` suggests `capacity / cop`, and the user can edit it. That save is judged by `_prefill_errors` (`config_flow.py:2095`, called at `:3958` in the options flow and `:2535` in the setup flow). `_prefill_errors` re-runs the `thermal_model` page's `_power_errors` but not the new `_partload_errors`.
- Its own docstring says it holds "the refusals of the pages the suggested keys live on". The new refusal lives on that same page and is missing.
- Scenario: an install stores a 1-5 kW band and derate 0.40, which is legal because the limit is 0.444. A pre-fill save then writes max power 2 kW, which moves the limit to 0.333. The save returns no error, and from then on the model prices derate 0.0. The configured value stays in the options and the page shows nothing.

Failing-test-first control (`ev/probe_silent.py`, the tree's own functions, run at the head):

- `RESULT pre-fill save, max 5->2: errors {}; model reads derate 0.0`
- `RESULT silent over-limit read-as-0 via pre-fill: YES`, rc 1 (`ev/probe_silent-head.txt`).
- Same values on the thermal_model page: `errors {'heat_pump_cop_partload_derate': 'partload_derate_above_limit'}`. The refusal exists, but on one writer only.
- Null: derate 0.3 under the narrowed limit is kept by both paths (`read 0.3`, no errors).
- Planted repair, one line: `errors.update(_partload_errors(saved, current))` in `_prefill_errors` (`ev/planted-fix.diff`). The probe then reads `silent ... no`, rc 0 (`ev/probe_silent-planted-fix.txt`). The probe is therefore not vacuous: it fails at the head and passes once the path is guarded.
- The tree was restored afterwards: `git status` was clean.

The suite shows the same refusal from another side. At this head the full \`tests/features.py\` fails 1 check:

- Run on this host, it reads \`1 of 4552 FEATURE CHECKS FAILED\`, rc 1, 6m22s (\`ev/features-head.txt\`).
- The failing check is \`FAIL every configurable parameter is reachable from a config key [cop_partload_derate]\`.
- Its probe sets each \`CONF_\` key to the sentinel 0.5 on the default 1-5 kW band. 0.5 is past that band's limit of 0.444, so the round-2 reader refuses it to 0, and the probe finds no key that reaches the field.
- \`ev/reachability-sentinel.txt\`: \`from_config({derate: 0.5}) -> 0.0\`, \`0.25 -> 0.25\`.
- This is a deterministic logic result, not a host float. CI's \`tests / fast\` will go red on it.
- The body says it did not re-run the full \`features.py\` this round and quotes \`ALL 4550 FEATURE CHECKS PASSED\` from \`ad2bf7fd6\`. That figure does not hold at this head.
- The repair: either the check's sentinel accounts for the band limit, or the reader stops silently zeroing. The first is cheaper. The second is the brief's point.

Repair, for the fixer to own:

- Judge the derate on every save that can move the band. At this head that means `_prefill_errors` whenever the save carries `heat_pump_max_power` or `heat_pump_min_power`. The pre-fill form shows no derate field, so the error goes on `base` or on the power field.
- Add a `tests/features.py` cell for this path, failing first.
- Say in the body which rule enumerates "writers of the band" so the class is closed. The fix-review.md step 6 class here is every writer of min or max power, not every reader of the derate.

## Findings

- \`tests/features.py\` \`every configurable parameter is reachable from a config key\` fails at this head on \`cop_partload_derate\`, because its 0.5 sentinel is past the default band's limit. It must be fixed in this PR. Carry: R10-COP-PARTLOAD
- The fix leaves this open: the over-limit derate is silently read as 0 on the Modbus pre-fill path (the block above). It must be fixed in this PR before merge. Carry: R10-COP-PARTLOAD
- `review_packet.py render` refused this head with `host-path` and wrote no packet. This is a false positive on this host:
  - `HOME=/root`, and the case-folded home-directory match in `ref_privacy._leaks` finds the substring `/root` in `dev/governance/roles/root-cause.md` on line 3 of `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` (`ev/review-packet-refusal.txt`).
  - Any cloud seat whose home is `/root` will refuse every diff that adds a line naming `roles/root-cause.md`.
  - This is an instrument defect, not this PR's. The fixer should not rewrite the path to satisfy it.
  - Carry: dismissed: instrument false positive outside this PR's diff; the orchestrator, who owns tools/audit/seat/, can take the substring match (a home must match as a whole path component) to that seat's brief.

## Evidence

- The full \`tests/features.py\` at the head: 4551 of 4552 ok. The one failure is the reachability check under \`## Block\`.

- Reviewed head: `ev/HEAD.txt` holds `a7411d7ad644c1546b4dd4cf1ad34613cd61ca2a`.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. The merge base is origin/main `beb570c81`.
- Merge: `git merge-tree --write-tree origin/main a7411d7ad644c1546b4dd4cf1ad34613cd61ca2a` exits 0, tree `7e717bc14`, no conflict (`ev/merge-tree.txt`).
- CI on this head, from the check-runs API at review time (`ev/check-runs-a7411d7ad644c1546b4dd4cf1ad34613cd61ca2a.tsv`): 27 runs, 13 still queued or in progress, including `tests / mutation`, `tests / closure-scope`, codeql and hassfest. None had concluded red. The step-11 root-cause trigger could not be judged for this head's runs, so this review gives no answer on it.
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched three-dot (`ev/version-untouched.txt`).
- Toolchain: this seat had none of the advertised toolchain on PATH, and the system python is 3.11.17, not CI's. I built a venv with the pinned voluptuous, numpy, scipy, aiohttp, pyyaml and threadpoolctl versions from `tests/requirements-ci.txt`. The full hash-pinned install refuses on 3.11 (typing_extensions unpinned). Float figures from this host are not canonical.
- Not re-derived at this head: the body's harness figures (grid 27, spread and flat deltas, 32 of 32 null hashes), its stress counts and the round-2 mutant table. The block makes them moot for this round, and the fixer re-takes them after the repair.
