Fix review: merge 47e6dab020c89ffed44e02d4ee05af003f448b22

bus-nonce: ca554e9ab5f4aff6364338e84f0b307f

Round 6. Measured `47e6dab020c89ffed44e02d4ee05af003f448b22`. Live pull-request head at posting is that SHA. The body ## Head names it. Merge-base and `origin/main` are `618d014f0b91ac39d77250bf887618002f628307`. `git merge-tree --write-tree origin/main 47e6dab020c89ffed44e02d4ee05af003f448b22` exited 0 with empty stderr. Three-dot diff of `VERSION`, the manifest and `RELEASE_NOTES.md` is empty.

`_flow_inlet_c` reads `inp.state.floor_return_temperature`. A state with `return_temperature` 99 and `floor_return_temperature` 30 returns 30.0. The same state with `floor_return_temperature` None returns 35.0. No `getattr` or `hasattr` in `pump_arbiter.py` names `return_temperature`. `ThermalState` stores `floor_return_temperature`.

`probe_install` reads `freq_control_mode` with `DEFAULT_FREQ_CONTROL_MODE`, which is `observe`, the same constant the entities-metering form passes. An absent key with a frequency entity adds no frequency write. The key set to `control` does.

`dev/programme/delivery/2006.md` is the open row for #2006. `docs/delivery/2006.md` is not in this tree. The body's flow command prints `48.0`. ## Figures states `48.0`.
