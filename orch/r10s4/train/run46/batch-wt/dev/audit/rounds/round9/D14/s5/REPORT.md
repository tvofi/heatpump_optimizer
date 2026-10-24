# Round 9, D14 seat s5: recurring bug classes, instrument axis (I1, I2, I3, I5)

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1). Box B9 is a cloud container with 4 cores, shared with two other seats. Interpreter: CPython 3.14.0rc2 at /home/claude/venv314/bin/python, with strace 6.8. Every command runs from the worktree root with PYTHONPATH=tests/hastub. Counts are exact. Wall and CPU numbers are provisional.

## Method
- M1: ledger read. On my axis, I1 has 7 rounds and 49 instances, I5 has 7 and 60, I3 has 6 and 18, and I2 has 4 and 6. All four are open with detector null.
- M2: picked I1 and I2. I5 got its backticked-reference arm, which produced a non-finding. I3 was not picked because its detector needs the live ruleset from the GitHub API.
- M3: closure_divergence.py and stub_scope_probe.py (I2), guard_inventory.py (I1), doc_refs.py (I5).
- M4: D14-s5-01 (I2) and D14-s5-02 (I1).
- M5: barriers and costs are given per finding.

## D14-s5-01 (I2): child-process reads never reach the Python closure recorder
closure._exec_record records Python scripts in-process with sys.addaudithook plus sys.modules. A child process's reads are invisible to it, and only the child's argv is kept. The node lane already records under strace -f. closure.py check re-records with the same blind instrument, so it can never flag these seams.

The detector re-records each script under strace -f -y, normalises every read with the production closure._rel and _is_real_file, and asks the production closure.select([F]) about each read file F that is missing from the closure.

Default set: 31 seams. tests/doc_claims.py has 9, all hastub files read by its child tests/plan_view.py, whose payload the demand-windows figure draws. tests/deployment_shape.py has 22, all hastub files read by its own '-P --driver' child; its closure holds no hastub file at all. typing_ruler, structure and guard_pins have 0.

Perturbations: --perturb union gives 0. --perturb drop gives 32.

Failing probe (stub_scope_probe.py): append 'import gate_lock as _d14s5_probe' to tests/hastub/homeassistant/helpers/update_coordinator.py in a scratch copy. deployment_shape.py goes rc 0 -> 1, and select() is scoped with 13 scripts and skips it: red_and_skipped=1. With --perturb union it is 0. On the same edit, 7 of the 13 selected scripts re-run by hand stay green.

Heavy set (entities, features, harness_headers, config_flow_steps, finite_boundary): 883 seams.
- python-child: 133, of which 128 are on measured files. These are harness_headers.py's live-header children, round4/D10/qs_rules.py and round4/D6/claims.py, reading workflows and docs.
- node-child: 334, of which 332 are INERT. This is the policy corpus that entities.py's policy_lint.mjs reads.
- git: 416, of which 312 are on measured files. These are entities.py's git grep full-tree scans and git status/ls-files.
- config_flow_steps and finite_boundary: 0 each.

Barrier: on Linux, record Python lanes the way _record_node_strace records node. Wrap --exec-record in strace -f -y, use the absolute path of the returned fd, and union the result with the audit-hook set. Decide explicitly whether git-internal reads are dependencies. The cost falls only on main's closures job: 9.4 s strace wall vs 5.9 s audit-hook seconds on the default set, provisional. A partial alternative is a _widen rule giving deployment_shape.py all of tests/hastub, plus a closure union doc_claims.py <- plan_view.py.

## D14-s5-02 (I1): 528 of 2313 guard seams are invisible to the mutation ratchet
The detector enumerates guards by AST and asks the production candidates() for a site on each guard's line.
- EXIT: 1346 seams, 52 invisible. Causes: multi-line test 46, elif 3, trailing comment after the colon 2, has else 1.
- CLAMP: 668 seams, 246 invisible. Causes: numpy/math clamp 179, multi-line call 63, 3+ args 4.
- TERN: 299 seams, 230 invisible. No operator touches a conditional expression.

Production ratchet probe on a scratch price_model.py: a new single-line guard moves unpinned_sites by +1 and ratchet_refusal refuses. The same guard with its test split over two lines moves it by 0, and there is no refusal.

History, at pre-fix commits:
- invisible: #1312 (ternary >= 2) and #1316 (np.clip).
- inventoried: #1313, #1314, #1315 and #1317.

Fixture: clean 0, re-introduction 1. --perturb widen takes invisible EXIT seams from 52 to 0 and the total from 528 to 476.

Context, not a finding: 3677 of 3951 inventoried sites are unpinned at baseline, because the ratchet is growth-only.

Barrier: widen candidates() three ways. GUARD_OFF on any If, rewriting the test segment. CLAMP_DROP on numpy/math clamps and multi-line calls. A TERN operator. The cost is AST-only: inventory() takes 3.77 s CPU, provisional.

## Non-findings
- doc_refs.py: 303 references in the user docs, 4 unresolved, all deliberate. 1282 in production comments, 16 unresolved, all external names. 0 stale after classification.
- The I2 null controls show 0 seams.

## Could not finish
- Scripts not traced under strace: stress, optimality, backtest, edge and validate.
- The I2 ledger instances were not run at their pre-fix commits.
- I3 was not picked.
- The node lane's argument-path strace parse, which can resolve relative paths against the wrong cwd, is unmeasured.
- Barrier costs need a quiet-window re-take.

## Exposure
See the JSON exposure field.
