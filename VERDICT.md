Fix review: blocked 4a4107fcde80e55b5b9a24748554f0d4491b6b59 harness: class-open runtime imports in the else or not-branch of TYPE_CHECKING, constant-name importlib.import_module and absolute self-imports are not edges; each plant reads IMPROVES +0.1466

bus-nonce: 0f8fe14b632dbe8b78dad7a6547c4273

PR #2320, R10-ARCHSCORE-COVERAGE part 3, **round 1**. Reviewer: rev-2320, working from a detached worktree at the head. Contract: fix-review.md from origin/main `ef08fb420`. The preamble diff over `dev/governance/roles/` is empty.
Measured head: `4a4107fcde80e55b5b9a24748554f0d4491b6b59`. It was re-read before posting and is unchanged.
Part 3's own diff was judged as the tree diff from merge-tree(origin/main merge base `7215e39df`, part-2 `134810973`) to the head. That covers 13 paths: `metrics/layering.py`, `vector.py`, `counters.py`, `controls.py`, attempts 21 to 23, `expected.json`, `corpus_vectors.json`, `ABOUT.md`, `ci_budgets.json`, `closures.json` and the delivery row.

## Blocking

**1. harness: class-open (step 6 / step 14).** The body states the rule as every `ast.Import` and `ast.ImportFrom` at any scope, plus `importlib.import_module`, with imports under `TYPE_CHECKING` excluded. Its only stated residual is `import_module` with a *computed* name. Four seams fall inside that rule, but the diff does not handle them and the body does not give them a disposition. Each plant below keeps the runtime import (behaviour unchanged) and moves both metrics. Nothing improves. The plants are in `silent_mode.py`; see `plants.txt` and `plant_scores.txt`, measured with the full vector at the head.
   - p1: `if TYPE_CHECKING: pass` / `else: from .optimizer import _utc_step_starts`. RESULT layer_violations 22->21, private_cross_module 17->16, dS +0.1466 IMPROVES. Cause: `common._in_type_checking` walks the whole `ast.If`, so `orelse` is included.
   - p2: `if not TYPE_CHECKING: from .optimizer import ...`. Same +0.1466. Cause: `ast.unparse(test).endswith("TYPE_CHECKING")` matches `not TYPE_CHECKING`.
   - p3: `importlib.import_module(".optimizer", __package__)._utc_step_starts`. Same +0.1466. The body puts `import_module` in the rule, but `layering.graph` has no `import_module` arm at all.
   - p4: `from custom_components.heatpump_optimizer.optimizer import _utc_step_starts`. Same +0.1466. An absolute self-import is filed as the external root `custom_components` and becomes no edge.
   - The control holds. The same import made lazy (p9) reads 22/17, unchanged, so C17 works. A TYPE_CHECKING-only import (p10) is the by-design exclusion.

   None of the four seams occurs in today's package; my grep found no hits. The repair is local to `layering.py`: count only `body` of a positive `if TYPE_CHECKING`, resolve absolute self-imports and constant-name `import_module`. The alternative is to give each seam a disposition in the body. A calibration case or attempt for the else/not branch would pin it.

**2. pr-contract is red at the head (step 7, a required check).** Run 116780967581 started 02:33:39Z after the body edit and refused it with: "`## Head` does not name 4a4107f ... 77991f1 is not authored and committed as github-actions[bot]". The edit dropped the `77991f1ad` and `aacdc1c4c` lines from `## Head`, which breaks the carry chain to the two bot commits. The earlier run, 116766013900, accepted the chain but refused the unnamed `closures` red. Restore the `## Head` lines. The new `## Red checks` entry for `closures` is acceptable, because it names UNDER-SCOPED at `77991f1ad`, gives the bot repair `551b660e7`, and names the cheaper detector (`--single` on every script whose closure holds `vector.py`) with its standing cost.

## Instrument findings, non-blocking here (finding-propagation.md: carry them to the stage that owns the D7 brief or the next archscore part)

- **C19 is defeated by a junk read.** p5 adds `import scipy` plus `assert scipy` to `silent_mode`. RESULT layer_violations 22->21, unused_boundary_imports 1 (unchanged), dS +0.0641 IMPROVES. The tripwire keys on "never read", and one bare read satisfies it.
- **Private crossings outside C18's spellings:** p6 `getattr(_o, "_utc" + "_step_starts")`, p7 `vars(_o)["_utc_step_starts"]`, p8 `_m = _o; _m._utc_step_starts`. Each reads private_cross_module 17->16 with the edge kept. The body's residual "reached through an object rather than a module binding" covers p8 at most.
- **The GOOD case `a3_private_cross_module_fix` is a pure rename** (`_parse_return_time` -> `parse_return_time`). Under this metric, declaring a private public is credited as improvement with no coupling change. This is defensible as making an API explicit, but it is the metric's cheapest move, and the D7 brief should say so.
- **The TYPE_CHECKING exclusion is pinned by no calibration case.** M6 (`type_checking_imports` ignored) moved none of the nine cases (`arm_M6_*`). On today's tree it reads layer_violations 36, so only the `ci_budgets.json` row (22, via `tests/entities.py`) would catch it. No script under `tests/` names `layering`.

## Verified

- Finder's harness (ARCH2-s4 export from `b202335e2`; score_delta.py sha1 35570991, layering.py sha1 314f35a4):
  - RESULT base(`7215e39df`) P1 delta_S=+0.0000 NULL
  - RESULT head P1 delta_S=+0.4460 IMPROVES (layer_violations 21->18 term +0.2115; private_cross_module 19->16 term +0.2345; unused_boundary_imports 1->1)
  - RESULT head P1 --revert delta_S=+0.0000 NULL, no metric moved

  Removing the mechanism (the base has no layering job) gives 0.0000, so the movement belongs to the metric. P1 is a real owner move: the clock leaves the solver.
- Corpus: `--measure-corpus --only-metric layering --jobs 4` re-measured 87/87 ok, rc=0. RESULT corpus_vectors_remeasure=byte-identical to the committed file. `calibrate.py --stored-only` gives 0 MOVED on any of the 45 corpus cases; the 137 "now None" lines are the live cases a stored-only run omits. `expected.json` adds exactly the nine new cases, with none changed or removed.
- Ablation on the nine cases: C17 reopens only rt_21 (IMPROVES +1.1699), C18 only rt_22 (+0.2224), C19 only rt_23 (+2.0000). The other two stay closed in each arm. M0 moves nothing.
- Mutants, re-run by me: M1 moves only rt_21; M2 only rt_22; M3 only rt_23; M5 moves a3_private_cross_module_control to NULL and rt_22 to WORSENS. These match the body.
- **M4** (`r > 2`): under the full nine-case run, calibrate dies. Attempt 23 asserts "no violating module" and raises CalledProcessError, so `tests/arch_score.py` fails and the mutant is killed. That crash is why the fixer's script printed no line. The fixer's hand run, which excluded rt_23, is the verdict-level measurement. I confirmed the kill but did not re-run the hand subset.
- Layer assignment: an independent grep census of `homeassistant` and `scipy` imports per module agrees with all 77 module ranks. glue = the 29 modules with a non-TYPE_CHECKING HA import. solver = `optimizer` and `dhw_planner`. `payload`'s only glue reach (`open_meteo`) is under TYPE_CHECKING and is correctly excluded. Measured today: 22 / 17 / 1, matching the new rows.
- `ci_budgets.json`: three new rows, no existing row moved. budget-raise-gate (116766012119) flags only part 2's `hub_solve_writes` 38->41, and the body answers it; per the brief, not blocking.
- Forward-carry: #2315 merged (`084052aae`, an ancestor of origin/main). The R10-CONFIGFLOW-PAGES `carry` and brief hold the C19 precondition (remove `dr`, lower the row 1->0). `config_flow.py:16` still binds `dr` and nothing reads it.
- VERSION, the manifest and the notes heading are untouched; neither claim file is touched. `git merge-tree --write-tree origin/main HEAD` exits 0.
- CI heavy runs at the head (cited, not re-run): arch-score 116766006389 success ("dS +0.0000 NULL, no gate metric rose"); mutation 116766005198 success ("MUTATION TABLE PASSED (empty scope)": no production code line, so no mutant is drawn); fast (3.14) 116766059378/116766156899, closures 116769787511/116772540708, coverage-ratchet and composed-proof all success. Of 74 check-runs, all completed: 2 failures (budget-raise-gate, pr-contract), the rest success or skipped.
