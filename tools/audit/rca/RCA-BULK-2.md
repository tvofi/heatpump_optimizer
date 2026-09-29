# RCA-BULK-2: I2, N-structure-blind, R-register

Root-cause seat, 2026-09-28, per `root-cause.md` and `defect-root-cause.md`, at `origin/main` `3490cb16`. Not posted. Helpers and outputs are in `phaseC/bulk2/`. Spans run from issue created to fix merged (GitHub via MCP).

---

## 1. I2: a measured closure diverges from the real dependency graph

### 1.1 The instances, read at their seams

| row | seam | direction | fix |
|---|---|---|---|
| R2 D3-09 | the package import makes every solver closure 38–44 modules; validate.py executes 8 | over | refused (not executed) |
| R5 D3-01 #1309 | a warm-`.pyc` `exec_module` load is dropped by `_rel`: 0 recorded against 1 cold | **under** | #1343, 1.5 h |
| R5 D3-02 #1310 | a phantom entry: `merge` never drops, and `check` prints it as "safe: over-scoped" | **under** (#1358: `select` trusts it) | #1358 (PR 1.0 h) |
| R8 D3-s1-02 #1531 | env_drift's cache key hashes `HPO_*` variables that no capture reads | over (cache) | #1561, 13.7 h |
| R9 D14-s5-01 #1663 | a spawned child's reads go unrecorded: `closure.py:848-854` records only the child's **argv** paths | **under** | open 2.1 d, F10.3 |
| R3 D3-FLAKE #810 | a wall-clock floor in a null control | not I2 | move to `none` (timing) |
| R5 R5-INST-01, R7 R7-INSTR-01 | a hand-typed D0–D12 list in schema and DIMS, against the set of briefs | not I2 | → **I4**; guarded since ef4a1bf1/06851b14 (the scope regex test and `check_scopes.py`) |

Five true instances remain. Under-scope accounts for 3 of them: #1309, #1310 and #1663.

### 1.2 Cause

**The closure is self-attested.** `check` is closure.py's whole anti-rot guarantee (docstring: *"This one cannot rot silently either"*). It compares the committed closure with a **fresh recording by the same recorder** (`closure.py:1627-1648`). A file the recorder cannot observe, such as a warm `.pyc` load or a child's reads, is therefore missing from both sides, and the check passes.

Each blind spot is patched after the fact, per instance, by a hand-declared rule that "a trace cannot know" (`_widen`: `DRIVEN_BY_OTHERS`, `PRODUCERS`, env_drift's whole-integration rule; `_pyc_source`). The over-direction is labelled `safe: over-scoped` and never tested, and #1310 and #1309 both hid behind that label.

### 1.3 Process state

- **(c), for each landing.** `check` ran on every push to main and was obeyed, but it cannot see its own instrument's blind spots.
- **(c), for the class.** It met the per-round trigger at R5 (v2) unseen (§3).

### 1.4 Reach

The recorder is blind to child reads, to `.pyc`-only loads (patched) and to out-of-repo worktrees (patched by a rule). Its sibling, the env_drift cache key, is now guarded by names derived from `golden.py`'s closure.

### 1.5 Cost

- 5 instances, 09-02 to 09-26: **6.3/month**; under-scope alone 3, **3.75/month**.
- Per instance 1.0, 1.5 and 13.7 h (**n=3**, mean 5.4 h), plus an unmeasured red main one merge later. Over-scope: D3-09 measured 2424 CI s per change to a never-executed module.
- Releases escaped: **0** (an instrument class; main's forced FULL precedes a stamp). Expected: 3.75 × 5.4 h ≈ **20 h/month**.

### 1.6 Countermeasure: build a second oracle (F10.3)

The build is a **nightly `strace -f -y` differential**, for Linux only. It re-records every selectable Python script under `strace -f`, maps `.pyc` paths through the existing `_pyc_source`, and fails on any repo file strace saw that the committed closure lacks (`BLIND-SPOT: <script> <file>`). The node lane already records under strace, so the machinery exists.

- **Cost test:** nightly CI minutes only (finder: 9.4 s strace against 5.9 s hook for one script, not re-measured); **0 s** on the PR gate and 0 seat time unless it fires, against ~20 h/month. **Build.**
- **Demonstration owed (F10.3):** at `1936d5ca` it must list the 22 child-read seams of `deployment_shape.py`'s `-P/--driver` child (#1663's `closure_divergence.py`), and 0 once fixed. Null control: a script that spawns nothing gives identical sets. #1309's shape is caught only with `_pyc_source` on both sides (landed in #1343).
- **Refused:** a barrier for over-scope (D3-09). Over-scope is the safe direction of the gate's design, and its cost is CI seconds, already priced.

---

## 2. N-structure-blind: production reached by nothing, and `structure.py` reads 0

### 2.1 The instances, read at their seams

| instance | the metric's proxy, and the shape it misses |
|---|---|
| #364 (09-03, pre-round) | the name census kept only an alias, so 6 **live** symbols read dead; fixed by counting both names |
| R6 D7-02 #1395 | `dead_top_level_symbols` walks module level only, so 379-line `identify()` reads 0; fixed by adding `dead_methods`, **by name, `@property` skipped, "called but unreachable … pinned behaviourally, not here"** (`structure.py:1106-1109`) |
| R8 D7-s2-01 #1538 | a live-by-bare-name rule: 12 dead because another module reads the same name. #1538 itself calls #364's widening "the name-based fix that now yields false negatives" |
| R8 D7-s2-02 #1539 | seams bucketed by name regex, so a pure rename moves the zero-headroom `cross_seam_edges` |
| R9 D7-s3-02 #1650 | `dead_methods` skips properties and counts bare-name loads: **exactly #1395's documented exclusions** |
| R9 D7-s3-01 #1661 | 10 members with no production caller, 9 kept only by tests; `DefrostDerate.samples` is kept alive by name collision with `AccuracyTracker.samples` (#1538's shape, one level in) |
| R9 D7-s3-72 #1661 | write-only `_step_*` scratch: attributes are not measured at all |
| R9 D7-s1-01 #1686 | state reached via module-level `_helper(self, …)` goes unpriced; the docstring already says *"the `_helper(self, ...)` move W4-G4 already refused"* |

Reproduced at `3490cb16`: `RESULT dead_methods=0` (`structure_run.out`), while `InputHealth.healthy` and `OpenMeteoSolar.last_success` are `@property` getters with **0** production references.

### 2.2 Cause

Every structural metric decides a semantic property (liveness, seam membership, state reach) from a **syntactic name proxy**, with no positive control per known shape.

Each fix widens the proxy for the shape just reported and writes the shapes it leaves out as **docstring prose** ("pinned behaviourally, not here", "W4-G4 already refused"), not as counted cases. So 0 reads as clean over shapes the metric says it cannot see, and the next round re-finds them: #1395 → #1650, #1538 → D7-s3-01, W4-G4 → #1686. One fix's widening even produced the next false negative (#364 → #1538).

### 2.3 Process state

- **(c), for each instance.** The ratchet ran green, and each fixer ran fixer.md step 8 for the reported shape only; #1605 enumerated #1538's class at top level. The process was followed and left the holes it documented.
- **(c) plus (a), for the class.** R8's pair was never classified (state (a), §3). R9's judge split one mechanism into N-dead-member (2), N-structure-blind (1) and I4 (D7-s3-02), so each stayed under 3. Merged, R9 has 3 (4 with D7-s3-02).

### 2.4 Cost

- 8–10 instances, 09-02 to 09-26 (5 in the class, 4 flagged, #364): **~11/month**.
- Per instance (n=4): 5.5 h (#364), 6.5 h (#1395), 42.0 h for #1538+#1539 in one PR (#1605, +1341/−270, 45 commits; 21 h each). Mean **13.5 h**. #1650, #1661 and #1686 open 2.1 d.
- Escapes: dead code ships (`identify()` from #1330 until b462a7c9); hygiene, but a mis-priced ratchet can buy headroom with a rename (#1539).
- Expected ≈ 11 × 13.5 h ≈ **150 h/month** of issue span (an upper figure; spans include queueing).

### 2.5 Countermeasure: build the barrier in F10.4, which already holds all four R9 findings

1. **Liveness by reachability** from declared production roots (HA entry points, platform setups, `HA_CONVENTION_*`, the coordinator), never from tests. Attributes count (stores with no production load are dead), and `_helper(self, …)` resolves to its class. This is #1661's static `reach.py`. **Drop the dynamic sentinel** from the gate as too costly per run; the `.samples` name collision becomes a declared shape.
2. **A planted-shape corpus** in `self_check()`, one plant per historical shape: #364 alias, #1395 called-but-unreachable, #1538 same-name elsewhere, #1539 rename invariance, #1650 dead property plus bare load, #1661 collision plus write-only attribute, #1686 `_helper(self)`. Each must read ≥1, and must not move for the rename.
3. **Declared blind shapes are counted** as `RESULT unmeasured_shapes=<n>`, never left to prose.

- **Cost test:** an AST walk over trees `structure.py` already parses (3.2 s now), estimated ≤+2 s per run, not measured; 1000 runs a month is ~33 min, against ~150 h. **Build.**
- **Demonstration:** #1605's probe is the template (planted `describe` read 0 at `cdf82daa`, 1 at head). The dead-property plant reads 0 at `3490cb16`, like `InputHealth.healthy`, and must read 1 at F10.4's head. Null control: a uniquely named live plant reads 0 dead at both ends.

---

## 3. R-register: the bug-class register and the RCA records decay

RCA-1736 §2 already records **(a)**: no step folds a round into `bugclasses.json`. It also records **(c)**: the barrier trigger counts per round. Neither is repeated here. The five mechanisms below come on top of those.

### 3.1 Cause, mechanism by mechanism

1. **The round has no ledger writer and no record landing.** `audit-verify.js:216-223` writes the register doc, `rotation.json`, `ISSUES.json` and the roster, never `bugclasses.json`. `check-wave-script.mjs:730-737` syncs class **ids** only. The file therefore changes only when a barrier PR needs its row (c80f2554, 821a9f16, 63a75419, 7ca03761), while D14 step 2, lens 3 (`:58`) and the judge (`:98`) all read it.
   - The ledger was created at ef4a1bf1 (09-23T22:53Z), and R8's register landed 2.5 h later (9fd07379) unfolded.
   - Round 9's register, `JUDGE.json`, sweeps and RCAs are **not on main**: there is no `tools/audit/round9/`, and `docs/audit-2026-09.md` ends at Round 8. The writer is told *"Commit on the branch and stop"*, and landing that branch is nobody's step.
2. **Re-minting.** judge.md:20-21 and `:98` accept "a `bugclasses.json` id or a new one" with no comparison to the nearest class, and ledger mechanisms are single narrow sentences. P10, for example, reads "a solve on a GIL-holding thread starves the event loop". **20 of 31** R9 judge classes map onto an existing id (19) or merge (1), per A1's table (the brief's 21 also counts D7-s3-02's I4 flag).
3. **Splitting below the trigger.** The trigger counts per class **id**, and the judge sets an id's granularity. N-dead-member (2) and N-structure-blind (1) are one mechanism.
4. **No unit for "instance".** The sweep dispositions **every seam** as `instance`, but returns `instances` only for seams "NOT among the findings" (`:206-214`). The drafts print both: #1661 *"N = 2 (2 judge-verified findings + 7 sweep-confirmed instances)"*, and #1686 *"N = 1 (… + 6 sweep-confirmed)"*. The sweeps' count lines say 0 additional (A1), so N is 2 and 1 by the tools and 9 and 7 by the rule's words. The fix plan counts a third way (P9: 5 strict, 11 with RCA- and fixer-found).
5. **Records have no durable home.** "Where it is recorded" names *the defect's issue*, and a class RCA has none. Of 82 RCAs:
   - 27 live in PR bodies only.
   - 17 live in deletable comments only.
   - **9 are lost**: deleted #201 and issue comments, and 7 PRs by the retired `tvofi-seat-author` that now 404.
   - 14 R9 class RCAs exist only at `763b0ba4`.
   - Just 13 have any in-tree trace, mostly a `docs/delivery/` row pointing at the lost record.
6. **A new trigger was never applied to history.** The per-round rule (09-25) ran on R9 only. Over the whole ledger (`cross_round.out`) it had already fired for **P10 at R1, P4 at R2, P8 at R4 and I2 at R5** (P10 weakens with flags applied). None of the four has an RCA.

### 3.2 Process state

| mechanism | state | evidence |
|---|---|---|
| no fold, no landing | (a) | the writer prompt; no round9 on main |
| re-mint, split | (a) | no nearest-class or granularity rule |
| instance unit | (c) | followed, by tools that define the term two ways |
| no durable home | (a) | only "the defect's issue" is named |
| 404 PRs | (d) | decision 0011 retired the App whose PR bodies held the records |
| history never re-evaluated | (a) | no step applies a new rule to the ledger |

### 3.3 Cost

- **Late:** R8's P2 (7), I3 (6), I5 (6) and I1 (5) crossed the trigger unseen; their class RCAs came **64.5 h** later (09-24T01:16Z → 09-26T17:44Z). R9 then registered 75 rows in those four classes (P2 31, I5 23, I1 14, I3 7), most of them pre-existing seams.
- **Never:** P10, P4, P8 and I2 have no RCA. **28 instances** came after their trigger round (P4 11, P10 9, P8 5, I2 3), 6 of them after the rule existed. P7 was barriered without an RCA. N-shared-config, visible only to a window, carried **115 escaped releases** (RCA-1736 §4).
- **Records:**
  - 9 are lost, and 40 of 82 cannot be found from the register or an issue.
  - 9 of 14 R9 class countermeasures are unlanded (A2).
  - Re-deriving took **at least 4 seats** (A1's 486 rows, A2's 82 RCAs, RCA-1736 §2, this bundle); their wall-clock was not measured.
- **Rate:** a round every ~2.8 d (9 rounds, 09-01 to 09-26). Each unfolded round leaves 39 (R8) to 162 (R9) rows unclassified.

### 3.4 The proposed mechanism, part by part

- **(i) Build, sharpened.** Use a **deterministic script**, `tools/audit/fold_ledger.py`, not the writer agent; `audit-verify.js` runs it after the sweep.
  - It appends `R<n> <id>` and recomputes per-round N: judged survivors plus sweep seams marked `beyond_finding: true`, a new sweep-schema field that removes mechanism 4. It prints both terms.
  - It refuses a survivor whose class is absent, and a new id without `nearest` and `differs`.
  - The one-time backfill is A1's v2, with the owner reviewing the flags, and the `class_guess` enum moves in the same PR.
  - The workflow also opens the **round record PR** (`tools/audit/round<N>/` plus the register section).
  - Cost: seconds per round, 0 per PR.
- **(ii) Keep it, enforced by (i).** `nearest` and `differs` become required fields, refused rather than exhorted. Add one sentence: a class is a mechanism, never a site; two new ids sharing a nearest class are counted as one for the trigger. On R9 this catches 20 of 31. **Policy: owner.**
- **(iii) Policy: the owner decides.**
  - The **window** arm (≥3 in any 3 consecutive rounds) adds P7 (from R3) and N-shared-config (R9), and fires earlier for P1 (R2, not R5) and P5 (R2, not R3).
  - The **≥5 while open** arm adds nothing on the registered classification, but it is the only arm that catches §1's corrected I2 (5 over 4 rounds, max 2).
  - Recommend both; the cost is at most one RCA per class, and there are 27 classes.
  - The P4/P8/P10/I2 gap is not the window but never applying the rule over history, which (iv) does mechanically.
- **(iv) Build it slim**, as `fold_ledger.py --check` in an existing lane, under 1 s:
  1. each in-tree judge survivor sits in exactly one class (the source is JUDGE survivors, not "issue #", since R1–R7 rows often lack one);
  2. each class that met an adopted trigger has a `barrier` or an `rca`, else the check prints OWED and fails;
  3. `rca` resolves in-tree.

  **Drop** "every class cites an RCA".
- **(v) Build it.** Docs go to `tools/audit/rca/<id>.md`. That path is under the INERT prefix, so it costs 0 gate seconds, and it is outside `POLICY_GLOBS`, so it has no cap. The issue keeps a short Root cause section with the path. Land the 14 R9 docs from `763b0ba4`, RCA-1736 and this bundle. **Refuse** rebuilding the 9 lost records, whose countermeasures landed. Changing "Where it is recorded" is **policy: owner**.

### 3.5 Demonstration of (iv)

The prototype is `bulk2/register_check.py` (output in `register_check.out`).

| ledger | rc | rows in no class | unparseable instances | OWED |
|---|---|---|---|---|
| main `3490cb16` | **1** | **186** (R8 39, R9 147) | P11 16, N-restart 1 | 12 classes |
| A1 v2 | **1** | 0 | 0 | 14 classes |
| null control: v2 with `rca` on every class | **0** | 0 | 0 | 0 |

The check would have failed at 9fd07379 on R8's 39 unclassified survivors. Once the R9 class RCAs land in-tree, OWED reduces to {I2, P4, P8, P10, N-structure-blind}, exactly the set owed and never conducted.

---

## 4. Summary

| subject | cause (one line) | process state | cost | verdict | roster | register changes |
|---|---|---|---|---|---|---|
| **I2** | the closure is checked only against a re-recording by the same recorder, so its blind spots (child reads, `.pyc`) never show; over-scope is labelled safe | (c) each landing; (c) class, trigger met at R5 unseen | 5 instances, 6.3/mo (3.75/mo under-scope); 1.0/1.5/13.7 h (n=3); ~20 h/mo; 0 releases | **build** a nightly `strace -f` differential (0 PR-gate s); **refuse** an over-scope barrier | **F10.3** | D3-FLAKE → none; R5-INST-01 and R7-INSTR-01 → I4; `rca`; barrier at F10.3 |
| **N-structure-blind** | liveness, seams and reach are decided by name proxies; known blind shapes live in docstrings, so 0 reads as clean and fixes re-open the next shape | (c) each fix; (a) R8 unclassified, plus an R9 split | 8–10, ~11/mo; 5.5/6.5/21/21 h (n=4); ≤150 h/mo; 3 open | **build** reachability liveness, planted-shape `self_check` and `unmeasured_shapes`; no dynamic sentinel | **F10.4** | merge N-dead-member; D7-s3-02 from I4; add R2 D7-06, R6 D7-02, R7 D2-02 (low), #364 non-round |
| **R-register** | no ledger writer or record landing in the round; unconstrained mint and split; no instance unit; RCAs with no durable home; triggers never applied to history | (a) ×5; (c) instance unit; (d) 404 PRs | 4 classes 64.5 h late; P4/P8/P10/I2 never (28 instances since); 115 releases (N-shared-config); 9 lost, 40/82 unfindable; ≥4 re-derivation seats | **build** (i) `fold_ledger.py` plus the round record PR, (iv) slim `--check`, (v) `tools/audit/rca/`; **owner**: (ii), (iii) both arms (recommended), (v) wording; **refuse** rebuilding lost records | **new F11.7** (after F11.4); policy into **F11.5** | land v2 (486 rows, flags reviewed); add `rca`, `nearest`, `differs`, `per_round`; OWED: I2, P4, P8, P10, N-structure-blind |

## 5. Not measured

- Seat wall-clock for phase A and this bundle.
- Standing seconds for the F10.4 walk (estimated), and the strace ratio (the finder's figure).
- Main-red cost from an under-scope.
- The 150 h/month figure is issue span, not seat time.
