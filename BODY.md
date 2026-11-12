Part 4 of 5 of R10-STANDING-CONTRACTS-P2 (carries 15-19). Carry 15 is built: sweep_template.md steps (2), (3), (4) and (6) queued work to the standing seats instead of having the orchestrator run it. Carry 15 touches sweep_template.md steps 2, 3, 4, 6 and sweep_render.py self_test only (no orchestrator.md or standing.md heading, no merge_train.py function; the unused `orch_scratch` placeholder row is removed). Carries 16-19 are already on main and are dismissed with evidence below.

## Head

e199f727b44059611092c141d1d04edb8dee219a

## Mutation proof

tools/audit/seat/sweep_render.py --self-test: the mutant that restores a `merge_train.py sweep` launch to step (3) is caught by "null control: step (3) restored to a train launch is caught"; the check "the rendered sweep names no train launch for the orchestrator" fails on that text.

## Null control

The unmodified tracked template renders with no `merge_train.py sweep` or `train.sh` (37 checks, 0 failed).

## Figures

none

## Red checks

- `tests / nightly-status`: red because the scheduled nightly run 43130126209 (head 4778853, 2026-11-12) concluded cancelled on its mutation-ledger lanes. The cause is a cancelled scheduled run on main outside this diff, which touches only policy text and no workflow; main's nightly owner answers it, and this check is not a required context on `main-protect`.
- `tests / fast (3.14)`, `governance / instrument-self-tests` and `replay`: in progress or not yet reported when this body was written; no failure line was read for any of them at the PR head. This body does not claim them green.

## Forward-carry

- Carry 16 part (1) (judge every loop): not answered by this part; it stays open on the roster, unmarked, for the group's other part. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
- Carry 16 part (2) (hooks): dismissed. tools/audit/seat/hooks/liveness.py, seat_interpreter.py, git_identity.py, tools/audit/seat/hooks_setup.py (--check, --install, --self-test; main() near L393) and tools/audit/seat/instruments/hooks_setup.py.md exist on main since f0c6bbfd7; the project-level pre-bash guard is check-only in hooks_setup.py. No tracked .claude/ file is changed here (diff of .claude/hooks/session-start.sh and .claude/settings.json: empty). Carry: dismissed: implemented at f0c6bbfd7
- Carry 17: dismissed. `tick-digest` row: tools/audit/seat/beatd.jobs.json and beat_jobs.py:41; standing-tick.md is retired (b16084794); orchestrator.md L106-109 reads the digest; sweep step (5) reads it; tick_brief is absent (sweep_render.py self-test). Carry: dismissed: implemented at 0a98a0173
- Carry 18: dismissed. roster-drain, plan-beat, pulse, cancel-sweep, disk and opener rows are in beatd.jobs.json (0a98a0173); standing-roster.md is retired (b16084794). Carry: dismissed: implemented at 0a98a0173
- Carry 19: dismissed. dev/governance/roles/standing.md L47-50 names $HPO_STATE_DIR/alive/. Carry: dismissed: implemented at 1b174e9b3
- Carry 0: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 1: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 2: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 3: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 4: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 5: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 6: marked [implemented: d696193607835332443206f97bcba1304f5d1494] on the roster, not answered here. Carry: dismissed: implemented at d69619360
- Carry 7: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 8: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 9: marked [dismissed] on the roster by an orchestrator ruling, not answered here. Carry: dismissed: dismissed on the roster by orchestrator ruling
- Carry 10: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 11: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 12: marked [dismissed] on the roster by an orchestrator ruling, not answered here. Carry: dismissed: dismissed on the roster by orchestrator ruling
- Carry 13: marked [dismissed] on the roster by an orchestrator ruling, not answered here. Carry: dismissed: dismissed on the roster by orchestrator ruling
- Carry 14: marked [dismissed] on the roster by an orchestrator ruling, not answered here. Carry: dismissed: dismissed on the roster by orchestrator ruling
- Carry 20: marked [implemented: 1b174e9b319607e9594bfdd7cb21067ca004d340] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 21: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
- Carry 22: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
- Carry 23: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
- Carry 24: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
- Carry 25: marked [dismissed] on the roster by an orchestrator ruling, not answered here. Carry: dismissed: dismissed on the roster by orchestrator ruling
- Carry 26: marked [dismissed] on the roster by an orchestrator ruling, not answered here. Carry: dismissed: dismissed on the roster by orchestrator ruling
- Carry 27: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it

## Friction

none
