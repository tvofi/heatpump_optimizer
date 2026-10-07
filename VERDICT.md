Fix review: blocked 21a62c10a03f5bd684d529aa70d8ff7ef6938471 root-cause-unanswered: pr-contract went red, unanswered

bus-nonce: 5acd2baddab0bc2b5ba2800d0a936943

Measured `21a62c10a03f5bd684d529aa70d8ff7ef6938471`. `git merge-tree --write-tree origin/main 21a62c10a03f5bd684d529aa70d8ff7ef6938471` exited 0, stderr empty. `dev/programme/delivery/2006.md` is the open row. `docs/delivery/2006.md` is absent.

The body's flow command prints `48.0`. `FLOW_HEAT_C` is `55.0`. A state with no `floor_return_temperature` attribute: `_flow_inlet_c` returns `35.0`, and the same no-duty call returns `48.0`. A present `30.0` returns `30.0`.

Coverage job 112597999833 on `47e6dab`: `tests/features.py exit=1 wall=358s`. The log has no `AttributeError` line. coverage-ratchet job 112604091360: `notifier.py: 78.63 %`, `pump_arbiter.py: 79.86 %`, `sysid.py: 92.98 %`. Three-dot names `pump_arbiter.py` and not `notifier.py` or `sysid.py`.

Range failures include `pr-contract` on `47e6dab`, job 112613349309: `coverage-ratchet` and `mutation-autofix` were red and unnamed. The live body names those two and does not name `pr-contract`.
