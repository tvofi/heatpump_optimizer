Fix review: merge cf0d110352351cb8fb76cc4000e669bf91f3bdd6

R9-F1.9 (#1805), round 1. Reviewer seat (opus), measured at code head cf0d1103, merge base 6793659c.
Branch tip c6781512 adds only transport files above the code head (PR body, resume note). No resume file sits in the code head's ancestry.
#1805's head e54fb07a is cf0d1103 with main cc00ed85 merged in. `git merge-tree --write-tree origin/main cf0d1103` exits 0 with no conflict.

RESULT features_head: `tests/features.py` at cf0d1103 reports ALL 3631 FEATURE CHECKS PASSED (Python 3.13, CI pins, OPENBLAS_CORETYPE=Haswell).
RESULT fi_block_base: the head's FI block run against the base code. FI-sw3 is FAIL and FI-sw1/sw2/sw4/rca1 are ok, as expected because F3.1 closed those four.
RESULT fi_block_control: the same block at the head gives five ok.

Targeted mutants (a copy of the package, the FI block only; run.py and mutants.txt are in this directory):
- M1 `"last_tick" in ...bounded` -> False: FI-sw3 FAIL
- M2 `if ahead or gap<0` -> `if gap<0`: FI-sw3 FAIL
- M3 `if ahead or gap<0` -> `if ahead`: FI-sw3 FAIL
- M4 `hits.append(...)` -> pass: FI-sw3 FAIL
- M5 `self.bounded = hits` removed: FI-sw3 FAIL
- M6 the bound switched off (`_bound_instants` call skipped): FI-sw1/sw2/sw4/rca1 FAIL with the baseline defect values (cooldown held, damping on, margin 2.0, due 168.0 h)
- M8 the dict path key dropped: FI-sw3 FAIL
- M7 the tz coercion dropped: survives the FI block. The ledger pins its kill to features.py's T3 naive-tick check (features.py:39213-39226), which my full features run covers.

Finder's harness (the RCA's repro_loaders.py, sha1 f10ee0ee…). I ran it unmodified and also as my own row-safe copy, which only wraps each row in try/except:
- outage_flagged_after_6h_cut: base null=True skewed=False, head null=True skewed=True. The defect moves and the null control holds.
- The naive-clock rows (boost, echo, immersion) raise TypeError identically at both ends. That is the harness's naive T0 against the aware boundary, as the fixer disclosed. Their re-expression with aware clocks in features.py is what I mutated above.

Class sweep: I ran the S7 enumerator (sha1 80afe72f…, from `git archive 1152a74346`) at base and head. It lists 19 sites at both, identical apart from line numbers, and every coordinator.py site maps to a seam the body dispositions.
Production code review:
- `last_tick` has been written aware (`dt_util.now().isoformat()`) since it was introduced, so the energy store's UTC naive_zone cannot falsely bound it.
- The energy store's lead is 0, so a reported bound always means the stamp really is ahead.
- `bounded` is assigned and read with no await in between.
- A None or "" stamp still opens no window.

Checks:
- VERSION, the manifest and RELEASE_NOTES are untouched, and no golden or claim file changes.
- The structure budgets are re-recorded downward only (coordinator_loc and max_class_loc 9022 -> 9014). No raise.
- Forward-carry: none owed. bugclasses.json is updated in the diff.

CI on #1805 (e54fb07a) when this was written: typing success (answers the fixer's unrun --mypy line). Also green: closure-scope, budget-raise-gate, pr-contract, policy-docs, env-matrix, browser, briefs, delivery-status, nightly-status, hassfest and validate-hacs. Still running: fast (3.14), mutation, closures, coverage and CodeQL python. Nothing is red. Per the merge rule, the Mac merges only once these are green.
Real-HA ha_contract, run by the Mac at e54fb07a on HA 2026.9.3 / Python 3.14.7 (relayed by the coordinator): ALL 61 contracts PASSED, and the 22 stub-vs-real probe comparisons PASSED. The 2025.2.0 floor arm was not run.

Body correction (non-blocking): "Mutation proof" says that with `_bound_instants` replaced by the identity "all five rows go red ... outage masked". At the head that is wrong for FI-sw3. With the bound off, the raw `gap_minutes < 0.0` arm still reads the outage, so FI-sw3 stays ok (M6). That is the right behaviour. Only the four F3.1 rows go red, and those are the ones the brief requires.
