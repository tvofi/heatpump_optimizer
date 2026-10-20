Fix review: blocked 202cb8874ef72b82d9db49a6ecd77f28ad22838a carry-missing: countermeasure A changes the fixer stage but is carried nowhere; the body's three ## Forward-carry items and one ## Friction item name no Carry: destination and the only destination named is a future orchestrator action, not a file in the tree (`carry_audit.py` refuses at this head: CARRY-AUDIT: 5 finding item(s): 0 routed, 5 unrouted; group R10-RCA-NIGHTLY-PYSPY `carry: []`).
bus-nonce: ffed08738f8420708ca332870a5678a2

Reviewed head: 202cb8874ef72b82d9db49a6ecd77f28ad22838a (live PR head matches at review time; merge base with origin/main 0c298f6b5). Diff: `dev/audit/rca/nightly-ha-pyspy-timeout.md` (new) and `dev/programme/delivery/2479.md` (the delivery row). Round 1.

## RESULT lines

RESULT blocked carry-missing: the fix countermeasure A (RCA section 5) changes how the fixer stage must work, and `finding-propagation.md` forbids merging the producing PR until the carry is in the tree. The group's own brief says "the fix it names is routed by its own Carry lines", yet none of the body's `## Forward-carry` items (countermeasure A, countermeasure C, the bugclasses non-addition) nor its `## Friction` item ends in a `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>` marker. The one destination that is named — "The orchestrator appends it as a roster carry" — is a future action, not a file at this head, and the group's roster entry is `carry: []`. This is exactly the head's red `pr-contract`: `CARRY-AUDIT: 5 finding item(s): 0 routed, 5 unrouted, 0 bad destination(s)`. Remedy: add the `Carry:` destination for countermeasure A (a roster group or a `dev/programme/carries/carry-<N>.json` naming its stage) and route the other items, at the same head; the RCA content itself is sound.

RESULT blocked red-check-unanswered: the body's `## Red checks` says "none", but `pr-contract` is red at this head with the CARRY-AUDIT refusal above. The red is the same defect as the block above, so fixing the Carry routing answers it; either way the body must not say "none" over a red gate check.

## Verified (re-derived by this seat)

- Gate mode: `python3 tests/closure.py select --diff origin/main` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` — matches the body's Gate figure; `dev/audit/` is on `tests/closure.py`'s inert set (line 320), so the doc-only diff scopes out every script. `scope` check green at head.
- Body file references all exist at this head: `tests/nightly_ha.py`, `tests/entities.py`, `tests/requirements-nightly-ha.txt`, `dev/audit/rca/nightly-ha-pyspy-timeout.md`.
- Code sites the RCA cites are present and match: `HB_CONTROL_S = 0.6` (nightly_ha.py:282), `def _hb_spin` (:1863), `def dump` (:1923) with exactly one `py-spy dump --nonblocking --pid <self>` call at `timeout=30` (:1938-1939), `check_hb_positive_control` (:1978), the caller `call_soon(_hb_spin, HB_CONTROL_S)` then `asyncio.sleep(HB_CONTROL_S + 0.2)` (:2065-2066). The `tests/entities.py` pins on `_HB_BOTH`/`_hb_ctl` and on `"--nonblocking"` in `dump`'s source exist (:17893-17950).
- Requirement commit `ab45a5f7c` exists and is "nightly-ha A15: dwell before settling; py-spy must name the spin; pin stop and wiring", as the RCA states.
- CI-side class claims re-derived from the GitHub API. Failed jobs 117649075688, 117731309720, 117738343906 are all `nightly-ha (stable)` with conclusion `failure`, each carrying `py-spy did not run: TimeoutExpired` twice and `FAIL hb:positive_control [...] py-spy rc=0 names it: False`, at digest `sha256:33afb0659d78`. Green null-control jobs 117746567958 and 117731855696 are `nightly-ha (stable)` `success`, `Python v3.14.6`, `py-spy rc=0` present, same digest `sha256:33afb0659d78`. Same image, both outcomes — the race claim holds on the API side.
- `merge-tree --write-tree origin/main 202cb8874` exits 0 (no conflict; `mergeStateStatus: BLOCKED` is the red check, not DIRTY).
- Root-cause obligations (`root-cause.md`): the record names a cause (section 1), a process state with evidence — **(c)**, "followed and did not produce the intended result" (section 2), a cost test with numbers (section 4, arithmetic internally consistent: 8/120 = 6.7%; 45 runs × 3 min = 2.25 runner-hours; 45 × 70 s ≈ 53 min), and a countermeasure plus a recorded refusal (A carried to a fixer, B refused, C proposed for tvofi). All four deliverables present.

## Not re-derived (stated per fix-review step 8)

- The local lane reproduction (1 of 60, the 60 s / 70 s timings), the host-side sampler figures (28.7 s CPU / 29 s wall, utime 7.49 s, stime 21.24 s, 74% kernel) and the synthetic-dump counts (710 dumps / 0 timeouts, 18 rc=1, 2/200 symbol fallback, host 105/0) are the seat's own measurements. I cannot re-run them: the container lane is CI-only here, and there is no Docker daemon in this seat. They name their instrument and their reproduction (RCA "Reproduce"), so they are measurable, but they are the author's figures, not mine.
- The clause "py-spy 0.4.2's walks are bounded at 4096 …" cites py-spy source lines not in this tree; it is cited as an upstream mechanism and the record honestly says the 30-s mechanism is not established.

## Non-blocking observations

- Body accuracy: the `## Head` section lists `93647bfd9b4c2d940bc87b162bf4159ad2dd6b1e` as a merge of origin/main into the authored code head, but that commit is not an ancestor of the reviewed head (the head's actual merge parent is `f81d96c4`). Re-take that line so the body names only the commits the head contains. Carry: #2479
- Forward-carry routing: not adding the class to `dev/audit/config/bugclasses.json` is disclosed and defensible for a CI-lane race rather than an audit class, but it needs a `Carry:` line stating that disposition (e.g. `dismissed: <reason>`) rather than an unrouted bullet. Carry: #2479

## Forward-carry

- The block itself: the remedy is a body edit at this head, so it returns to this PR, not a later stage. Carry: #2479

