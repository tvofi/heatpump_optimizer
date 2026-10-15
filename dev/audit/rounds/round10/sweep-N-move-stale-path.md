# Sweep: N-move-stale-path (round 10, D14 steps 3-4)

**Class.** A file move leaves an executable consumer importing or resolving the
old path, so the instrument fails or splits keys after the move. Finding:
D13-s3-01 (`dora_keys.py` cannot import `d11lib` after it moved to
`tools/audit/round4/D11/`). `dev/audit/config/bugclasses.json` has **no entry**
for this class at this head (status: absent; the judge's new class awaits its
ledger row).

## Enumerator

`python3 -I dev/audit/rounds/round10/D14/sweep-N-move-stale-path/enumerate.py [ROOT]`

Seam = an executable reference from a tracked `.py`/`.sh`/`.mjs` to a repo
path: (a) a sibling import enabled by `sys.path.insert(0, dirname(__file__))`,
(b) a code string literal spelling a repo-relative file (docstrings and comments
excluded: prose drift is I5). A seam is listed when its target is absent **and
its basename exists elsewhere in the tree** (the move signature).
At `9355f107d`: `seams=2859 broken=367` (51 import, 316 path).

Probe for import seams: `probe_import.py FILE LINE MOD` executes the
consumer's own prelude above the import, then the import; exit 1 = stale.

## Controls

| control | command | result |
|---|---|---|
| positive | enumerate at head, grep `dora_keys.py 89 import d11lib` | 1 (re-found) |
| null | fixture `tools/a/use.py` importing sibling `lib` and naming `tools/a/data.json`, both present | `seams=2 broken=0` |
| perturbation | same fixture, one `git mv tools/a/lib.py tools/b/` | `broken=1`; then moving `data.json` too, `broken=2` |

## Disposition (all 367 listed seams)

| group | n | disposition |
|---|---|---|
| `import d11lib`, round4/D11 x7 | 7 | **instance** (probe exit 1, ModuleNotFoundError); dora_keys.py:89 is the finding |
| `import budget_raise_gate`, round9/D11/s2/owner_review.py:24 (`sys.path` `.claude/workflows`) | 1 | **instance** |
| other sibling imports (`harness`, `stress`, `golden`, `profiles`, `closure`, `gen_device_fixtures`) | 43 | **guarded**: each file adds `tests/` (or the module's dir) to `sys.path` beside its own dir; probe exit 0 under `PYTHONPATH=tests/hastub`. solve_poison.py resolves through `parsers.py`'s path setup |
| old-round harness path literals read/run relative to ROOT (`.claude/workflows/policy_lint.mjs` x18, `policy_budgets.json` x2, `gh_comment.py`, `tools/audit/prepr.sh`, `tools/audit/push.sh`, `docs/plan-2026-09-open-issues.md`, `tools/audit/{bugclasses,finding.schema,scopes}.json`, `tools/audit/round9/D4/s2/step_grid.mjs`) | 28 | **instance** (`test -e` fails at repo root) |
| `dual_path.py:373` (is_file fallback), `standards.py:137` (any-of candidates), `codeowners_gap.py:674` (`locate()`) | 3 | **guarded** |
| `round9/fixplan/gen.py` 420/501 | 2 | **not applicable**: path inside its own output tree `OUT` |
| other old-round harness literals (labels, git-show-at-baseline args, data) | 139 | **not applicable** by a line-shape heuristic (no open/read/exec on the line); not individually probed |
| `tools/` (81) and `.claude/` (3) literals | 84 | **guarded** by the move-aware resolvers `locate()`/`at()` (tools/policy/counts.mjs:52), `canon()`, `tests/layout.json` remap in policy_lint.mjs:600-608, and old-then-new tuples (merge_train TOOLS/GATE_PATHS, roster_lib LEGACY_ROSTER_PATHS, roster_edit BRIEF_LINT_OLD/NEW, record-predicate PLAN_PATHS); or **not applicable** as classifier test inputs (stamp.py 1068-1081, stop-selfcheck.sh 55-58, budget_raise_gate.py 766/1264, record_row.py 1317). `check-wave-script.mjs` passes its schema blocks through `at()` |
| `tests/` literals | 60 | **not applicable**: fixture/expectation data (entities.py, closure.py, layout.py lists of retired paths) |

**Count: 36 instance seams, 35 beyond the finding.** All 36 are in
`dev/audit/rounds/round{3..9}` harnesses; no production or live-tool seam is
unguarded. The live tools carry a guard (`locate`/`at`), the old harnesses
predate it.

## Proposed barrier

Run `enumerate.py` in the `tests/entities.py` family, refusing any listed seam
outside an allow-list. Or make the move tool (`tests/layout.json` application)
rewrite or `locate()`-wrap consumers in the same pull request. It is a static
scan over about 2.9k seams, under 2 s. 36 instances meet the
`defect-root-cause.md` recurrence trigger: cite a `root-cause.md` record before
choosing.
