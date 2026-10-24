## v7.0.2

**Plans on set-point-driven heat pumps heat at a sensible flow temperature instead of a 25 °C floor (#2465).** Installs whose power is commanded through the heating-flow set-point were planned at a 25 °C flow set-point in cheap hours even with comfort headroom, and low-power slots filled the day. Three changes: the heating floor now sits above the flow gate, the draw window is censored so an implausible reading cannot widen it, and every set-point write is quantised to whole degrees at the single write owner.

**Monthly savings keep their scale when the store upgrades mid-month (#2463).** The coverage factor is computed on the store the month actually ran on, so the monthly savings entity no longer drops to extreme negative values after a mid-month store upgrade.

Other changes users can see:

Engineering and audit programme (round 10):

- Tooling: `tools/audit/seat/update_pr.sh` takes a per-branch lock and the relay retries a BUSY update (#2469); the stale-contract follower runs once per pull-request head instead of once per watched workflow completion (#2480).
- CI: layout PR 0, the dispatch-only umbrella stub and the reuse-free runs budget (#2464).
- Budgets: the inherited `coverage_floor_override` is withdrawn, so the solver-work floors return to the literal 40 and 15 instead of the 18 and 6 a merged branch left behind (#2485).
- Policy: the canonical-instruments rule, look them up before hand-rolling a loop, watcher or relay (#2462).
- Records: the nightly-ha py-spy timeout root-cause record and its carries (#2479); the round-10 roster and the delivery rows (#2460, #2461, #2466, #2467, #2468, #2470, #2471, #2472, #2473, #2474, #2475, #2476, #2477, #2478, #2481, #2482, #2483).

Known and recorded, not fixed in this release: `ci-ratchet` is red on `main`'s push runs. The `fast (3.14)` critical path reads about 59 minutes against a 54.8-minute budget, and the job's metrics-gathering step crashes on an empty API answer (`json.decoder.JSONDecodeError`, because a failed `gh api` leaves an empty `window.json` that the Python then parses). Both are folded into R10-CI-LAYOUT and are fixed in the CI restructuring that follows this release; this stamp therefore runs with `--allow-red` on that recorded cause (tvofi, 2026-10-20).
