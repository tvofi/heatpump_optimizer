# Catch-up verification, group arch-s2 (D7-arch2-01 .. D7-arch2-11)

Baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef (production identical to d749c986d). Machine: shared
macOS 8-core box, load1 5-25 during the session; every metric here is a count or a returned value, so
contention cannot move it. Run each from a tree root with `PYTHONPATH=tests/hastub` and the seat venv
(`export PATH=$HOME/.local/state/hpo/bin:$PATH`). Patches are applied only to tempfile.mkdtemp
extractions of the baseline (archscore.score.tree_of), never to the working tree.

| harness | metric | command | expected |
|---|---|---|---|
| probe_scrub_mixin.py | mixin_supplied (baseline entity props owned by a runtime-object mixin); nan_published (synthetic NaN mixin read through the property HA reads); null: same property on the class | `python3 .../probe_scrub_mixin.py [--patch P]` | base 0 / 1 / null 0; patch 00: nan_published 0 |
| clone_v2.py | dup_funcs: whole-function normalised-body clones (independent of archscore C3) | `python3 .../clone_v2.py --min-stmts 1 --min-nodes 15 [--patch P] [--roundtrip]` | base 68; 00+01 51; 00+02 63; 99 46; roundtrip 68 |
| null_rename_only.patch | null arm for harness.py: a rename-only patch | `python3 dev/audit/rounds/round10/D7/arch-s2/harness.py --base 554e2ecfa... .../null_rename_only.patch` | delta_S +0.0000 |
| probe_coercion_reach.py | silent_cap_kw / compose caps for power states incl. '1e400'; pump_arbiter NaN -> flow set-point | `python3 .../probe_coercion_reach.py` | inf_reaches_cap 0, inf_changes_decision 1, perturbed 1e400==unknown 1, nan_reaches_flow 0 |
| probe_rerender.py | cleared _STORED slots re-rendered with the stored entity as suggested_value on a rejected `entities` form | `python3 .../probe_rerender.py` | baseline 9, patched 0, null 0 |

votes.json holds one record per finding.
