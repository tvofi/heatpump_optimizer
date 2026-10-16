Fix review: blocked c777f855b9d87f8218ed3650aead1e92537f51e1 harness: class-rule-missing the body names no rule for class N-registry-leak — the issue's own is `dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py`, and the four seams it returns beyond the ones the body lists (`const.INPUT_MAX_AGE_MINUTES`, `coordinator._FENCED_CAUSES`, `coordinator._WORKER_FALLBACK_CAUSES`, `store._NEWER_ON_DISK`) appear nowhere in the body

bus-nonce: d8023917c443c8a931bbfce4a8140e4a

Round 1 (round-1 of this PR; the previous reviewer seat was killed before posting, so this is a fresh review, not a repair of its numbers). Fresh `origin/main`; the `dev/governance/roles/` diff against the merge base is empty, so this contract is current. Measured head `c777f855b9d87f8218ed3650aead1e92537f51e1`, merge base `dec1a264553463414d170a2a14dc53008b31e5b6` (three-dot; `origin/fix/r10-registry-leak`). Head re-read at post time: **unchanged**.

**The fix itself is sound and I verified it end to end.** The block is a body obligation under `fixer.md` step 8 / `fix-review.md` step 6, and it is cleared by one paragraph of prose — no code change. Everything below in `## RESULT lines`, `## Mutation proof`, `## Null control`, `## Drift and versions`, `## Red checks`, `## Conflicts` passes.

## The block, and what clears it (body-only)

`#2231` is the class issue. Its Enumerator section names the rule that enumerates the class's seams, and states nine of them:

```
PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py [--rounds N] [--clean] [--plant]
```

I ran it at both ends (output in `ev/enum_base_default.txt`, `ev/enum_head_default.txt`, `ev/enum_head_clean.txt`, `ev/enum_head_plant.txt`). It returns nine seams in both halves, and the body names neither the rule nor four of them:

| seam | in the diff? | in the body? | disposition (my run, at the head) |
|---|---|---|---|
| `early_cutoff._STATES` | yes | yes | closed in this diff — `held_pins_key` 3 -> 0 |
| `boost._STATES` | no | yes | guarded — `pins_key` 0 at both ends |
| `boost._PLAN_BASES` | no | yes | guarded — `pins_key` 0 at both ends |
| `pump_arbiter._STATES` | no | yes | guarded — `pins_key` 0 at both ends |
| `debugger._COLLECTORS` | no | yes | guarded — `pins_key` 0 at both ends |
| `const.INPUT_MAX_AGE_MINUTES` | no | **no** | `pins_key` 0 at both ends |
| `coordinator._FENCED_CAUSES` | no | **no** | `pins_key` 0 at both ends |
| `coordinator._WORKER_FALLBACK_CAUSES` | no | **no** | `pins_key` 0 at both ends |
| `store._NEWER_ON_DISK` | no | **no** | `pins_key` 0 at both ends |

`grep -c` of the body for each of the four un-named symbols reads 0 (`INPUT_MAX_AGE_MINUTES` 0, `_FENCED_CAUSES` 0, `_WORKER_FALLBACK_CAUSES` 0, `_NEWER_ON_DISK` 0). The body's class-closure claim is the sentence "No sibling seam to file", and it rests on a hand-listed four registries — `fix-review.md` step 6's own lead, "a harness's configurations are its parameters, not its population". The issue states nine seams and the body names no rule, which is `harness: class-rule-missing` verbatim; running the issue's rule is what shows the four the body never mentions, i.e. `harness: class-open`'s evidence. One paragraph naming the rule and putting every seam it returns against its disposition clears both. The class is in fact closed — I could not open it (below) — so this is a record obligation, not a code defect.

**Two sentences, one line each, clear it.** Prose only: this is a body edit, and the head need not move. It is not a re-cut (`fixer.md`'s fourth-round rule does not apply at round 1).

Precedent within this wave is uniform, which is why I did not read the omission as a form: `2284` ("Seam rule (fixer.md step 8): `python3 $EXPORT/dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py` ... Dispositions:"), `2289` (`.../D14/sweep-N-move-stale-path/enumerate.py .` with the seam/broken diff), `2275` (`.../D14/sweep-N-gate-yield/enumerate.mjs window.json`), `2320` and `2311` (`Class seams (step 8)`, rule named). All merged; all name the rule. `#2231` is closed by this merge, so this body becomes the durable record of the class closing.

## RESULT lines (my runs; numbers are mine, not the body's)

Harness: **the finding's own `dev/audit/rounds/round10/D1/s1/m1_reload_leak.py` + `rig.py`, in tree at both ends** (not the fixer's one-file copy) — `fix-review.md` step 2. Worktrees at the two SHAs under my own scratch; `PYTHONPATH=tests/hastub`.

Base `dec1a264553463414d170a2a14dc53008b31e5b6`:
```
RESULT rounds=5 count
RESULT early_cutoff_arm_calls=5 count
RESULT torn_alive=5 count
RESULT registry_early_cutoff_torn_keys=5 count
RESULT registry_boost_states_torn_keys=5 count
RESULT registry_boost_plan_bases_torn_keys=5 count
RESULT registry_pump_arbiter_torn_keys=5 count
RESULT registry_debugger_torn_keys=0 count
```

Head `c777f855b9d87f8218ed3650aead1e92537f51e1`:
```
RESULT rounds=5 count
RESULT early_cutoff_arm_calls=5 count
RESULT torn_alive=0 count
RESULT registry_early_cutoff_torn_keys=0 count
RESULT registry_boost_states_torn_keys=0 count
RESULT registry_boost_plan_bases_torn_keys=0 count
RESULT registry_pump_arbiter_torn_keys=0 count
RESULT registry_debugger_torn_keys=0 count
```

`ev/finder_base_r5.txt`, `ev/finder_head_r5.txt`. This reproduces the issue's 5-of-5 and the body's `torn_alive=0`, at the head.

**The harness's own parameter, both ends** (`ev/finder_base_r1.txt`, `ev/finder_base_r8.txt`, `ev/finder_head_r1.txt`, `ev/finder_head_r8.txt`): base `rounds=1 torn_alive=1`, `rounds=8 torn_alive=8`; head `torn_alive=0` at both. The defect tracks N and the fix holds at every N I ran.

**The landed instrument** (`dev/audit/harnesses/r10_registry_leak.py`, new in this diff, for a later seat) reads `torn_alive=0`, every registry 0, at the head (`ev/landed_head_r5.txt`); it cannot be run at the base, where the file does not exist — checked with `git ls-tree`, not inferred.

**The class rule at both ends** (the enumeration `fixer.md` step 8 asks for):
```
base (--rounds 3)          head (--rounds 3)        head --clean   head --plant
torn_alive=3               torn_alive=0             torn_alive=0   torn_alive=3
early_cutoff pins_key=3    early_cutoff pins_key=0  all 0          boost._PLAN_BASES pins_key=3
```
`ev/enum_base_default.txt`, `ev/enum_head_default.txt`, `ev/enum_head_clean.txt`, `ev/enum_head_plant.txt`. This reproduces the issue's `torn_alive=3 pins_key=3` and disposes every returned seam as the table above. The base `--clean` arm is the issue's own null control (the one judged site repaired in memory reads 0 on every registry) and it re-derives; the `--plant` arm is the instrument's sensitivity control on the fixed tree: re-introducing one line (`boost._PLAN_BASES[c] = {"pin": c}`) still reads `pins_key=3 torn_alive=3` at the head, so the rule is not blind at the head — a zero from it is a measurement, not a dead code path.

## Mutation proof (my mutants; `ev/M_*_features.log`)

Closure: `python3 tests/closure.py select --diff dec1a2645534` prints `MODE: SCOPED -- 21 script(s) run, 12 scoped out`, which is the body's 21. The named script is `tests/features.py` (it carries the new checks). Clean at the head: `ALL 4138 FEATURE CHECKS PASSED`, 4138 = the body's figure (`ev/M0_head_features.log`, `ev/structure_head.txt` for the mode line). Every mutant below was applied to `early_cutoff.py` only, run through `tests/features.py`, then restored from `HEAD` (asserted byte-identical after each).

| mutant | what it removes | `tests/features.py` |
|---|---|---|
| M_A | `early_cutoff.py` reverted whole to the base blob — the PR's production change deleted | `1 of 4138 FEATURE CHECKS FAILED` — `FAIL unloading the entry frees the coordinator the cut-off record was keyed by  [False False]` |
| M_D | `held.wiring = None` dropped from `detach` | `1 of 4138 FAILED` — same check, `[False False]` |
| M_C | `if held.wiring is None:` -> `if True:` (the diff's added GUARD_OFF line, `:160`) | `1 of 4138 FAILED` — `FAIL arming twice registers one unload hook, not one per cycle  [2]` |
| M_B | `if held.wiring is None:` -> `if False:` (the ledger's own GUARD_OFF mutant) | `3 of 4138 FAILED` — the hook-count check `[0]`, "unloading the entry drops the listener", and the freed check `[False False]` |
| M_F | the hook registered in the listener branch only, still calling `detach` — the body's "old shape" | `1 of 4138 FAILED` — same check, `[True False]`, the no-switch arm alone, exactly as the body claims |
| M_E | the hook registered in the listener branch *and* calling `release` — the base's own shape | `1 of 4138 FAILED` — `[False False]`. **My misreading, not evidence about the body** (below) |

**Step 1 holds**: delete the production line(s) the PR names and the named check goes red, with the body's own `[False False]` (M_A) — the same two arms the body reports. The new guard is pinned: M_C reproduces the body's `[2]` exactly, which is what the body's `## Unpinned sites` disposition for `early_cutoff.py:160` rests on. And the mutant that separates the *site* from the *hook body* — M_F's `[True False]` against M_E's `[False False]` — re-derives the body's own mutant, so the fix's mechanism is pinned on both axes: the wiring has to be dropped, and the hook has to be registered whether or not a listener exists.

**One quoted figure I could not re-derive, said rather than confirmed** (`fix-review.md` step 8). The ledger entry the autofix bot landed, `tests/mutation_ledger/killed_by/early_cutoff.py/arm.GUARD_OFF.d460246f.json`, records "GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4". The pin holds — rc 0 -> 1, the mutant is killed by `tests/features.py` — but I measure **3** failures, not 4 (M_B above), on the same tree with the same substitution. I could not reproduce a fourth; I did not build a different mutant to reach one. The entry's substance (this mutant is killed by this script) is verified; its count is not.

The body's other mutant — "register `detach` only inside the listener branch (the old shape of the hook) … red on the no-switch arm alone: `[True False]`" — I had to run twice. My first build (M_E, `ev/M_E_hook_in_listener_branch_features.log`) read "the old shape" as the base's *hook body* and registered `release`, which is not a mutant at all but the base's registration site restored — it reads `[False False]`, the same as M_A and M_D, and says nothing about the body. The body's actual mutant keeps `detach` and moves only its registration (M_F, `ev/M_F_old_shape_detach_features.log`): `[True False]`, re-derived.

## Null control (step 3; the group's carry)

The carry is "popping the registry at unload reads 5 to 0; a live coordinator must keep its entry." Both halves re-run:

- **`--perturb` at both ends** (`ev/finder_base_perturb.txt`, `ev/finder_head_perturb.txt`). Base: `torn_alive=0`, every registry 0 — so the base's 5 *is* the registry pinning the coordinator, and the null moves the metric. Head: `torn_alive=0` unperturbed and 0 perturbed, so the pop moves nothing, as the body says.
- **A live coordinator keeps its entry.** In the same check group as the freed check, `not _ec_freed("switch.hp", False)` — an entry never unloaded is still pinned. I verified it is actually evaluated and not vacuous: with M_B applied it still passes while the freed check fails, so it is a check that *can* fail and does not (this is the "green arm may mean dead code" trap of `#546`, and here it is not dead).
- **Both arms of the config.** The finding's harness runs one config (no switch), the case the body says had *no unload hook at all*. The features check runs the two the body names — `switch.hp` and `None` — and both arms move together under M_A/M_D (`[False False]` -> the fix's `[True True]`, which is what makes M_F's predicted `[True False]` a discriminating mutant rather than a restatement).

## Drift, claims and versions (steps 4 and 5)

```
base  tests/golden/claimed_drift.txt       13f46c8c12f2fbcd6ea3fcaed02b088ee15896c4
head  tests/golden/claimed_drift.txt       13f46c8c12f2fbcd6ea3fcaed02b088ee15896c4
base  tests/golden/card_claimed_drift.txt  2935c1bfd35d2df66ddab250f5d97c7cb9942ef1
head  tests/golden/card_claimed_drift.txt  2935c1bfd35d2df66ddab250f5d97c7cb9942ef1
```
Byte-identical; the branch claims nothing and moves no fixture. `python3 tests/env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE` (`ev/env_drift_head.txt`) — so the pairing holds in both directions. `node tests/card_drift.mjs`: `identical in all 40 states` (`ev/card_drift_head3.txt`; it needs `tests/plan_view.py`'s payload first, which I ran — `ev/plan_view.log`, `rc=0`).

`VERSION` is `7.0.0` at both ends and neither `VERSION`, the manifest version nor the `RELEASE_NOTES.md` heading is in the three-dot diff; `claims-for:` is `7.0.0` in both claim files, so it equals `VERSION`.

## Red checks (step 11)

Read from the commit's own check-runs API, all 45 runs at the head, not a per-name listing. At `c777f855`: every run is `success` or `skipped`, no red. The earlier head `d19dd83907cda81ed5bd62fbdcdfeba1bad53fca` carries two reds — `mutation` and `pr-contract` — and the head's `pr-contract` run names the range itself:

```
record   red-history           6 commit(s) between origin/main and this head, every failure conclusion across them: mutation
PR-BODY: 0 error(s) in /tmp/pr-body.md
```

So the range's only failure conclusion is `mutation`, the body's `## Red checks` names it and answers it (the added guard site, `prepr.sh`'s prediction as the cheaper detector, and the `mutation-autofix` bot commit `c723bd9d` that pinned it). The `pr-contract` red at `d19dd839` is the same check *demanding* that answer (`ERROR [pr-body] …: check 'mutation' is red and '## Red checks' does not name it`) and is green at the head; `pr-contract`'s own red-history enumerator does not carry its earlier self. Trigger answered; not a block. `nightly-status` and `delivery-status` are green, and the diff reaches neither.

## Conflicts (step 13)

`git merge-tree --write-tree origin/main c777f855b9d87f8218ed3650aead1e92537f51e1` exits **0**, stderr `LEDGER-MERGE: resolved tests/closures.json` — the closures ledger driver, resolved, and not a claim file. The branch touches neither `claimed_drift.txt` nor `card_claimed_drift.txt`, so the `claimnotes` driver is not in play. `mergeStateStatus: BLOCKED` is a required-check field, not a conflict; nothing to block on here.

## Attacks, and the class opened (step 6)

- **The harness's other configuration**: the no-switch arm (the harness's own default) and the switch arm, N = 1, 5, 8, both ends — above. The fix is flat at the head on every one and the defect scales on every base one.
- **The `entry_released` arm**: `arm` releases the listener and returns early *without* touching `held.wiring`, and the unload hook is registered before that return (it is the first thing `arm` does). So the early-return path still detaches. Read on the added lines, not run as a separate harness — my reading is disclosed as mine.
- **The class, opened and closed.** Rule and its nine seams in the table above, run at both ends; `--plant` proves the rule still sees a pin at the head; `--clean` proves the same rule's zero is a repair and not an absence. **The class is closed in code** — every seam the rule returns reads `pins_key=0` and `torn_alive=0` at the head, and I found no tenth seam by hand beyond the rule's nine. The block is the record, not the code.
- Step 9: the finding **has** a committed harness (`dev/audit/rounds/round10/D1/s1/m1_reload_leak.py`), and I measured with it. The fixer's one-file copy under `dev/audit/harnesses/` is disclosed in the body as the finder's, which is what `fixer.md` 18 / `#1879` want; it is classified as an inert read of `tests/harness_headers.py`, and `tests/entities.py` reports `ALL 2329 ENTITY CHECKS PASSED` and `tests/harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED` at the head, so the new tracked file is deliberately classified.

## Metric movement (step 14)

`python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, `41 counting rules hold`, every budget row at or under (`ev/structure_head.txt`, `ev/structure_head_full.txt`). `tests/structure_budgets.json` is not in the diff. `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL` (`ev/archscore_head.txt`) — the package is one file's 15 lines and the metric reads NULL by construction. `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries` (`ev/tmp_paths_head.txt`). No golden, claim, ledger or budget figure moves, so there is no movement to attack with a planted one; the two figures the diff *adds* (the `closures.json` inert read, the `mutation_ledger` pin) are sinks, not counters, and both re-derive.

Step 15 (`fixer.md` 17) on the added lines: one owner (`early_cutoff` owns the record and now its own detach, where before the unload half lived in the listener branch), no `homeassistant` import added, no new module, and the guard it adds is the pre-existing `held.wiring is None` predicate the file already used at `allow_on` (`:195`) and `_changed` (`:178`) — dead there at the base, live now. `detach` is the second call site of `release` rather than a second releaser. Sound.

## Forward-carry (step 10)

The body says `## Forward-carry: none`, and I agree for the groups this merge gates. `R10-PUMP-MODEL`, `R10-I5-DOCS` and `R10-LIVESTATE` all sit after this group; I opened their briefs and files — `pump_arbiter.py`/`thermal_model.py`, docs plus `__init__.py`'s service counts, and `boost.py`/`coordinator.py` respectively — and none of the three states or edits the registry/unload protocol this fix changes. The incoming carry ("popping the registry at unload reads 5 to 0; a live coordinator must keep its entry") **is** carried: it is the body's `## Null control` section, and both halves re-derive above. The one thing I would leave the box holding, for whoever edits `boost` or `pump_arbiter` state next: those two registries are guarded by *accident* — their values happen not to reach their keys — and the rule (`registry_leak.py`) is the instrument that says so. That is an observation, not a carry owed by this PR.

## What is mine, and what I did not do

Both `--perturb`/`--clean`/`--plant` arms, the closure selection, the seven mutants and the `git merge-tree` are re-runs; the enumeration rule and the finding's harness are the issue's and the finder's, not built by me. I built the mutants (that is what step 1 asks a reviewer for) and the mutation runner, which lives at `mutants.py` in my scratch, not in the tree. I did not re-run the gate or the mutation table (tvofi 2026-09-30); I cite CI's runs. `tests/features.py` runs on this box at 222 s unloaded and 6-12 min under the load of this wave's other seats; every figure above is a count, none is a time.
