Fix review: merge f4e168719d12f071bbc7771944e9430147a223db

bus-nonce: a71ad76c02dff7e6ce6a5308fcc45606

Review round 4. Round 1 blocked at `aac8c5e80`. Round 2 returned merge at `98d33ce03`. Round 3 carried that merge to `6f6aa4e48`. This round judges only the resolution delta, `6f6aa4e48..f4e168719`, by `fix-review.md` step 12. The last verdict was a merge, so the round-4 re-cut rule does not bite.

I measured head `f4e168719d12f071bbc7771944e9430147a223db`. The merge base with origin/main is `55dc8d9c2`. origin/main is at `5a41a5669` both now and at the time of posting, and the PR head is unchanged at posting. My copy of the contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. Evidence is under `/tmp/seat/rev2379/ev`.

## Resolution delta

The delta has five commits, all merges.

- `fe4d15d76` and `60368fbac` are `ci: merge main` by github-actions. They are clean merges, and `merge-tree` reproduces each tree byte for byte. The ledger driver resolved `structure_budgets.json` and `closures.json`.
- `9e2cdca95` is tvofi's merge of `be2d3676e`. It **conflicted** in `tests/entities.py` in two hunks, both additions at the same spot. The hand resolution differs from the conflicted tree only by deleting the six marker lines and restoring one closing `)` (`resolution_9e2cdca95_entities.diff`). It keeps both sides: this branch's `zone_setpoint_names` P2 entry and plant, and main's `slot_floor_rule` entry and plant. That matches the body's `## Head` account.
- `b44e17cb0` and `f4e168719` are clean, and their trees reproduce.
- **The authored diff is unchanged.** Compare each end's three-dot diff against its own base: `6f6aa4e48` against `42e6dedb2`, and `f4e168719` against `55dc8d9c2`. The added and removed lines are identical across `custom_components/`, `tests/finite_boundary.py`, `tests/mutation_ledger/`, `tests/structure_budgets.json` (the `recorded_at` line aside), `tests/entities.py`, `tests/closures.json` and `dev/programme/delivery/`. The delta brings in main and nothing else.

## Checks re-run at this head

- **Mutation proof of the resolved hunk.** Mutant: climate's `extra_state_attributes` writes `attrs["upper_floor_setpoint"]` directly, a second spelling outside the owner. In `tests/entities.py`, `P2 owners: zone_setpoint_names` goes red (`SEAM ['climate.py:266 ...']`), and so does the P2 null-control row. That is 3 failures against the head's baseline. I restored the mutant, which was in a separate worktree. So the resolved entry is live beside `slot_floor_rule`.
- **`tests/entities.py` at the head reads `ALL 2349 ENTITY CHECKS PASSED`.** My first run read `1 of 2349` failed. The failing row was `graders-head-copy's delivery_status step ...`, which is the container's doing, not this PR's. This container's `BASH_ENV=/etc/profile.d/hpo-toolchain.sh` puts `/opt/hpo/venv-ci/bin` back in front of `PATH` inside the arm's `bash -e -c`, so the arm's stub `python` is shadowed. I reproduced this directly (`type python` gives the venv's python). Neither the arm nor `tests.yml` differs from main. With `env -u BASH_ENV`, every check passes. This is an instrument finding (below).
- **`tests/finite_boundary.py` at the head reads `ALL 106 FINITE BOUNDARY CHECKS PASSED`.**
- **Finder's harnesses at both ends.** I ran scratch copies of origin/main's files with `BASE` set to each end's SHA. The base end is `55dc8d9c2` and the head end is `f4e168719`.
  - `shape_payload_guard`: `guard_families` 4 to 2, `driven_sites` 26 to 1, `disagreeing_probes` 3 (`0,True,'21.5'`) to 0.
  - `scrub_escapes`: `escapes=0` over 91 entity classes at both ends.
  - `probe_scrub_mixin`: `nan_published` 1 to 0, with `nan_published_outside_pkg` and `nan_published_null` at 0 at both ends.
  - P6 `enumerate.py --tree`: `seams=56 instance=31 guarded=5 not_applicable=20` to `seams=26 instance=0 guarded=6 not_applicable=20`. Its null control: `--fixture clean` gives instance=0 and `--fixture reintro` gives instance=1.
  - Every figure matches round 1's. The same blindness still applies: the mixin's seams leave the enumerator rather than becoming guarded by it. Round 1 covered that behaviourally.
- **Budget decrease, step 14.** `duplication_copies` goes from 33 to 17, recorded in c15f92abf with its reason.
  - Measured: `structure.py` reads 33 at the base and 17 at the head, and every ratchet row passes.
  - Mechanism removed: I put back the base's `sensor.py`, `climate.py` and `entity.py` in the head tree, and the count returns to `33`. So the drop is the change's.
  - What dropped: the four clone classes that vanished are the 11-copy, 4-copy and 2-copy `native_value` bodies and the 3-copy zone `extra_state_attributes`. That is 10+3+1+2 = 16 copies, all of them bodies the mixin and owners replaced. **Earned.**
  - Plant: on the base, I rewrote one of the 11-copy `native_value` bodies cosmetically, with no deduplication (`IndoorTemp` as `(data or {}).get(...)`), and the count reads `32`. The instrument therefore credits a reworded clone. The diff's change is not that shape, because its bodies are deleted, not reworded. Per step 14 this is an instrument finding, not a block (below).
- **Merge-tree.** `git merge-tree --write-tree origin/main(5a41a5669) f4e168719` exits 0 with no conflicts.
- **Untouched paths.** `VERSION`, the manifest version, `RELEASE_NOTES.md` and `tests/golden/` are not in the three-dot diff.
- **Forward-carry.** D8-s1-01 is in the R10-ARCH-SHAPES carry on origin/main (`wave-r10-groups.json:1739`). It carries the 1 and 4 control and a re-measure instruction, and the body names R10-ARCH-SHAPES and #2380.
- **Head.** The body's `## Head` names `f4e168719...`.

## CI

- **At the head, from the commit's check-runs API:** 46 runs, 31 success and 15 skipped, none red.
  - `mutation` (117719203618), read from its log: `PIN RE-VERIFICATION: 8 reproduced`. It covers the three round-1 survivors (climate.py:140, entity.py:142, which is round 1's entity.py:140 after the shift, and sensor.py:2808), and reads `0 survivor(s) of 8 evaluated`, `MUTATION TABLE PASSED`. Not inconclusive.
  - `closures`, `composed-proof`, `fast (3.14)`, `coverage`, `pr-contract` (twice), `budget-raise-gate` and `delivery-status`: all success.
- **Reds in the range, step 11:**
  - `nightly-ha (stable)` was red at `fe4d15d76`. The body answers it: a py-spy attach timeout, no file the diff reaches, green at the next head, cheaper detector none with its standing cost.
  - `pr-contract` was red at `60368fbac`, in the `Check the body against the contract` step. I could not read its log, because the blob host is unreachable through this container's proxy. Both `pr-contract` runs at the head are green, so the body now satisfies the contract.
  - The runs at `b44e17cb0` were `cancelled` because a newer head superseded them.
  - `mutation`'s earlier reds are answered in the body's `## Red checks`.

## Not verified by me

- I did not re-derive archscore `dS +5.6289` at this base. It is round 1's figure, and the authored diff is unchanged since then.
- I did not re-run the mutation table. CI's run is cited, per step 11.

## Instrument findings (non-blocking; for `finding-propagation.md`, not filed)

1. **`tests/structure.py` `duplication_copies` credits rewording.** One cosmetic rewrite of one clone moves the count by 1 (`plant_cosmetic.txt`: 33 to 32). A drop recorded under a "pay by improving code" ratchet should be checked by removing its mechanism, as step 14 already does. The count alone does not show that.
2. **`tools/audit/seat/cloud-setup.sh`'s profile breaks a PATH-stubbing arm for cloud seats.** The profile goes into `BASH_ENV` (`PROFILE=${HPO_PROFILE:-/etc/profile.d/hpo-toolchain.sh}`), so every `bash -c` re-prepends the venv. A cloud reviewer running `tests/entities.py` therefore reads one false red, the graders-head-copy `delivery_status` row. CI is unaffected.
