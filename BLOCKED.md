Question: body_push.sh exited 4 (CARRY-LANDED); the relay must fold the carries and re-run it. Code head 59bb0506a003221fe2af38f30ab20fac46d1b73d is pushed to handoff/r10-config-flow-text-verify; body kept at handoff-wip/r10-config-flow-text-verify-body.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-CONFIG-FLOW-TEXT-VERIFY at 59bb0506a003, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 2de47db2: not in its brief or carries: '- docs/configuration.md:530, docs/how-it-works.md:924 and the away.py module docstring say the anti-'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 9ae2be30: not in its brief or carries: '- docs/configuration.md:1063 and docs/how-it-works.md:648 say the VVC loop pump runs only during the'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 55051373: not in its brief or carries: '- docs/configuration.md:1049 and docs/how-it-works.md:620 describe free disinfection as an opt-in cr'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 4ab03548: not in its brief or carries: '- docs/configuration.md:1102 says the open-window option lowers the target. It lowers the coldest ac'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item af528396: not in its brief or carries: '- docs/configuration.md:1115 says main fuse 0 keeps the headroom sensor dormant. The sensor follows '
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 31878861: not in its brief or carries: '- docs/configuration.md:1079 says the PV forecast corrects itself. Only the current step is replaced'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 734b6d33: not in its brief or carries: '- docs/setup.md:91 says the entry name is shown in front of every entity. Entities use the fixed dev'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 452440fb: not in its brief or carries: '- docs/configuration.md:155 says valve settings work only in two-zone. Only a Flow temperature write'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 86aa4096: not in its brief or carries: '- docs/how-it-works.md:822 says the planned start count is published. No sensor carries it. Carry: R'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item a64a0285: not in its brief or carries: '- docs/configuration.md:1083 does not say the price estimate is on by default. Carry: R11-INTAKE-R10'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item b30f48ba: not in its brief or carries: '- custom_components/heatpump_optimizer/setpoint_check.py:6 has the docstring "Space set-point is nev'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 6f36db0c: not in its brief or carries: '- custom_components/heatpump_optimizer/presets.py:11 has a docstring saying "three answerable" quest'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item bb5336e8: not in its brief or carries: '- custom_components/heatpump_optimizer/config_flow.py, setup step `device_prefill`: the second form '
CARRY-LANDED: 13 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-config-flow-text-verify-body 0e4ac9f298cc078a229402ee9b6b652af72106ac
```
