Fix review: merge 202cb8874ef72b82d9db49a6ecd77f28ad22838a
bus-nonce: ffed08738f8420708ca332870a5678a2

Reviewed head: 202cb8874ef72b82d9db49a6ecd77f28ad22838a (unchanged across all three rounds — the body and the roster moved, never the tree). Diff: `dev/audit/rca/nightly-ha-pyspy-timeout.md` (new) and `dev/programme/delivery/2479.md` (row). Round 3.

## RESULT lines

RESULT merge clean: the RCA's claims are measurable and the ones re-derivable from the API hold; the doc-only diff scopes out; both forward-carries are now landed on `handoff/audit-r10-roster` with the body naming file, stage and branch SHA; `carry_audit` and `pr-contract` are green; every check at the head is green or skipped; the head has not moved; `merge-tree` against main is clean.

RESULT verified cause: `tests/nightly_ha.py` has one `py-spy dump --nonblocking --pid <self>` call at `timeout=30` (`LoopHeartbeat.dump`, :1938-1939), `HB_CONTROL_S = 0.6` (:282), `_hb_spin` (:1863) called at :2065-2066, `check_hb_positive_control` (:1978); `tests/entities.py` pins `_HB_BOTH`/`_hb_ctl` and `"--nonblocking"` (:17893-17950); requirement commit `ab45a5f7c` exists. CI-side class claims re-derived: failed jobs 117649075688 / 117731309720 / 117738343906 are `nightly-ha (stable)` failures, each two `py-spy did not run: TimeoutExpired` lines and `FAIL hb:positive_control` at digest `sha256:33afb0659d78`; green jobs 117746567958 / 117731855696 are `success`, `Python v3.14.6`, `py-spy rc=0`, same digest — same image, both outcomes.

RESULT verified root-cause record: `root-cause.md`'s four deliverables are present — a named cause (section 1), process state **(c)** with evidence (section 2), a cost test with internally consistent arithmetic (section 4: 8/120 = 6.7%, 45×3 min = 2.25 runner-hours, 45×70 s ≈ 53 min), and a countermeasure (A) plus a recorded refusal (B) and a proposal (C). Class search (section 3) and null controls (green pair, 59/60, host 105/0) are stated.

RESULT verified gate: `python3 tests/closure.py select --diff origin/main` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`; `dev/audit/` is on `tests/closure.py`'s inert set (line 320), so a doc-only diff runs no script. `scope` check green.

RESULT verified carry (step 10): countermeasure A is landed as `dev/programme/carries/carry-201.json` on `handoff/audit-r10-roster` (tip 606aaca86), appended as an entry with all of `from`/`effect`/`control`/`remeasure`/`brief`, its `stage` string extended to name the later seat that repairs `tests/nightly_ha.py`, and its `brief` stating the control as a precondition. The Friction finding is landed as `R10-RCA-FRICTION`'s own roster carry (2 entries; the cross-run count present, with Control, Re-measure and a Precondition clause). The body names the file, the stage and both branch SHAs (606aaca86, 3a9d79531). `tools/audit/carry_audit.py check --body` reads `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`; `#201` is valid because `carry-201.json` is in the head tree.

RESULT verified checks: `pr-contract` at this head is red-then-green — 118500521433 failed at 07:06 on the first body, 118502573687 and 118508185309 succeeded at 07:12 and 07:28 on the re-bodied one, the newest log reading `CARRY-AUDIT: 4 finding item(s): 4 routed`. Across the head's 44 distinct checks every latest conclusion is success or skipped; none is red or in progress. The body's `## Red checks` names and answers the superseded `pr-contract` failure.

RESULT verified hygiene: no claim file, `VERSION`, manifest version or notes heading is touched (pr-contract: "no version edit"); `merge-tree --write-tree origin/main 202cb8874` exits 0; the body's head SHA equals the head measured.

## Not re-derived (stated per fix-review step 8)

The local lane reproduction (1 of 60), the host-side sampler figures (28.7 s CPU / 29 s wall, utime 7.49 s, stime 21.24 s, 74% kernel) and the synthetic-dump counts are the seat's own; the container lane is CI-only and no Docker daemon exists in this seat. The record names each instrument and its reproduction, so they are measurable, but they are the author's figures. The RCA honestly states the 30-s mechanism inside py-spy is not established and belongs to py-spy's maintainers.

## Non-blocking observations

- The `## Head` section still lists `93647bfd9b4c2d940bc87b162bf4159ad2dd6b1e`, which is not an ancestor of the head (the head's merge parent is `f81d96c4`), and says `202cb8874` "merges origin/main" although that commit adds only the delivery row. Body accuracy only; the head SHA it names is correct. Carry: #2479
- The landed carry's `brief` for countermeasure A is stricter than the RCA's own countermeasure A: the RCA proposes retrying py-spy until an `rc=0` names the spin, while the carry says a repair "must not simply retry until it succeeds … it must either take the sample with a method whose failure is distinguishable from a real hang, or make the check's sample deterministic." The carry is the later stage's brief, so its wording governs; the fixing seat should reconcile the RCA section 5 text with this precondition rather than follow the looser retry. Carry: #201

## Friction

- None this round: the round-1 and round-2 blocks were both real (markers absent, then the carry not yet in the tree) and both were repaired at the same head without moving it. Carry: dismissed: block resolved; no process finding owed beyond the friction already routed to R10-RCA-FRICTION.
