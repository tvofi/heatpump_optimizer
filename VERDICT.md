Fix review: merge 765414af4e6ad2bc24aa7f491267e205b8410d9b

bus-nonce: 53a40fe15d1a6efc5534fbca876c6f18

## Scope

- Delta review against the merge verdict at e368e32982 (verdict/3897). e368e329 is an ancestor of the head. 765414af merges 40600fd1 (origin/main 43ec8e3273 into e368e329) with an identical tree (5fecc40c64).
- The branch-own production patch, three-dot against main before (aee9548a47...e368e329) and after (43ec8e3273...765414af), differs only in the pump_arbiter.py `from .inputs import` line, ignoring hunk offsets (`ev/interdiff_production.txt`). No wider review: the resolution touches only that import line.

## Prior findings: resolved

- The pump_arbiter.py conflict against f99ae8a4ef is resolved as the body states: the head's `delivers_to` is kept (read at the write path's delivery refusal), and main's removal of `quantise_setpoint_c` is kept. The head's module no longer references `quantise_setpoint_c`, and the module compiles. Carry: dismissed: verified here
- D16-s1-05 departure: accepted under mandate 6893738184. Carry: dismissed: ruled by the orchestrator under the mandate

## Findings

- None in the delta.

## Evidence

- CI at the head: `merge_train.py classify` RED with nothing pending and only `gate` red (`ev/classify.txt`). The gate's only FAIL line is `tests / mutation` (`ev/gate_job_log.txt`). That job's refusal names only flow_lift.py FlowCurveBias.observe_temps BOOLOP 04143c3f (`ev/mutation_job_log.txt`). This PR does not touch flow_lift.py three-dot. The same check is red on main at 43ec8e3273 and at 7b0ddc205f (`ev/main_mutation.txt`), so the red comes from main, and open PR 3939 cures it. nightly-status is red but is not owed. Carry: dismissed: evidence, not a finding
- VERSION, manifest, RELEASE_NOTES.md and tests/golden are untouched three-dot. Carry: dismissed: evidence, not a finding
