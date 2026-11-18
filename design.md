# Design: R11-SEAM-comments-tests (round 11, size XL)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 50a932de3b2a9db4a5e9213bff6b5be06e26f13b: ADR-010 parts 2, 3 and 5,
`PLAN.md` "Hot-file order". Roster row read on `handoff/audit-r10-roster`
(83ef6bc3, `wave-r11-groups.json`; the base carries no r11 roster). Base, and
code read at, `origin/main` 1723f9fdc9d8a6e6987190d2887686297a621dd4; the group
has no `after` edge, so there is no predecessor head. No production code on this ref.

**Revise round 1** answers `design-verdict/R11-SEAM-comments-tests` (a9081a0c2d,
revise of b71b07bf16, `sibling-design-conflict`). Sibling note read:
`design/R11-PRE-SHARED-FILES` at 20cafac7df, approved at 9d71412cc0 ("Features
script" in its section 3, part 4 in its section 7). Changed: section 3 B (the
release command and the parts), 3 C (D5-s7-01 anchors, `docs/delivery`), 6 (end
of group), 7 (the routed decision). Sections 1, 2, 4 and 5 stand.

## 1. What each finding reads at the base (finder's harness, run here)

Harnesses under `dev/audit/rounds/round11/D5/` on `plan/r11`, run with
`PYTHONPATH=tests/hastub` against the fork 92d38ecb and the base 1723f9fd.

| finding (merged in) | harness, figure | 92d38ecb | 1723f9fd |
|---|---|---|---|
| D5-s9-04 | `s9/comments.py` C5-long sentences (its 69 cells) | 820 | 824 |
| D5-s7-01, -02, -03 | `s7/m4_comments.py` c5_fail: features / finite_boundary / frontend | 460 / 14 / 3 | 460 / 14 / 3 |
| D5-s7-01 | `s7/m4_comments.py` c1_fail, c2_fail (features.py) | 1, 5 | 1, 5 |
| D5-s9-01, -02, -03 | `s9/stale_paths.py` stale_refs (entities / run.sh / structure) | 19 | 18 (14 / 3 / 1), contradicted=3 |
| D5-s8-03, -04, -05 | `s8/m4_ledger.py` unresolved units: closure / doc_claims / card.mjs | 5 / 3 / 4 | 5 / 3 / 4 |

The controls move: the `comments.py --perturb` C5 unit goes 1 to 0 and its C2
restore goes 18 to 0; the `stale_paths.py --perturb` restore goes 18 to 0. The fork's
nineteenth stale ref (`tests/edge.py:143`) was repaired on main in between.
C5 grew by four sentences since the fork, all from behaviour merges.

## 2. Owning seam

Test comments (`COMPONENTS.md`): the comment and docstring text of `tests/`'s
scripts (`*.py` including `tests/hastub/`, `*.mjs`, `*.sh`). There are no
callers: no assertion, interface or string changes. The 40-word detector is
ADR-010's ratchet. ADR-001 allows one copy of the rule, so the comment groups
share **one** script.

**What moved since the comments-production design.** b3fdb779e7 on
`handoff/audit-r10-roster` gives `R11-SEAM-comments-production` ten `after`
edges, one to each behaviour group ADR-010 part 1 names. This group still has
none, so it now dispatches first. **The shared ratchet script therefore lands in
this group's part 1, with the tests scope**, and comments-production's part 1
adds the package scope to the same file and does not write a second script
(the carry in section 7). That reverses which group writes the file, not who
owns the rule: it stays one script under `tests/`, owned by ADR-010's comment
groups. No stop.

## 3. Shape

**A. The ratchet (part 1).** This is the script specified in
`design/R11-SEAM-comments-production` (15dd4f5b3a) section 3 A, approved at
`design-verdict/R11-SEAM-comments-production` (1a27d04c17), changed only in its
scope list:

- `tools/audit/text_ledger.py` `units_of(..., "D5")` and `sentences`, with
  comment markers stripped.
- A unit is long when one sentence is longer than 40 whitespace words.
- The script derives its base from `tests/mutation_table.py` `ratchet_base`.
  It refuses when a file present at both ends gains long units, or when the
  scope total rises, and the refusal quotes the unit's first words.
- `--text-only <base>` prints `RESULT code_changed_files=<n> line_shifted_hunks=<n>`.

The scope list starts as the tracked `tests/` files with extensions `.py`,
`.mjs` and `.sh`. The `.sh` files need `#` stripping, the same as Python
comments. The ratchet itself is not a key in `tests/structure_budgets.json`.

```
tests/run.sh -> ratchet -> git show <ratchet_base>:<f> --\
                        -> worktree <f> -----------------> text_ledger.units_of/sentences
                        <- per-file counts, total, refusal <-/
```

**B. Parts by release.** p10 is **the features scripts**: `tests/features.py`
while it exists; after `R11-PRE-SHARED-FILES` part 4, every `tests/` file the
commit that deleted it added (the per-module scripts and the shared helper
module the splitter writes). The release command holds each of them on the
`tests/features.py` row of every open group that names that path, so a split
script stays HELD until the last such group merges. While `R11-PRE-SHARED-FILES`
is open, it also holds the files its note edits outside the roster's `files`:
every `tests/` file naming `features.py` (its section 5 rewrites live names),
plus `tests/env_drift.py` and `tests/harness_headers.py` (its section 6). No
`tests/` glob is prefixed, and `.py`/`.mjs`/`.sh` count at any depth. Run it
from the repository root at each dispatch and again at each handoff:

```
python3 - <<'E'
import fnmatch, json, subprocess, sys
sys.path.insert(0, "tools/audit/seat"); import roster_lib as R
sh = lambda *a: subprocess.check_output(a).decode().split()
G = R.groups_of(json.loads(subprocess.check_output(["git", "show",
    "origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r11-groups.json"])))
F, S = "tests/features.py", "R11-PRE-SHARED-FILES"
d = sh("git", "log", "--diff-filter=D", "--format=%H", "-1", "--", F)
fam = {F} if not d else set(sh("git", "diff-tree", "--no-commit-id", "--name-only",
    "-r", "--diff-filter=A", d[0], "--", "tests/"))
edits = set()
if S in G and R.gates(G[S]):
    edits = {"tests/env_drift.py", "tests/harness_headers.py"} | set(sh("git", "grep",
        "-l", r"features\.py", "--", "tests/", ":!tests/mutation_ledger"))
for f in sh("git", "ls-files", "tests/"):
    if not f.endswith((".py", ".mjs", ".sh")): continue
    keys = {f} | ({F} if f in fam else set())
    held = sorted(n for n, g in G.items() if "comments-" not in n and R.gates(g) and any(
        fnmatch.fnmatch(k, p) for k in keys
        for p in (g.get("files") or []) + (g.get("hot_files") or [])))
    held += [S] if f in edits and S not in held else []
    print("HELD" if held else "RELEASED", f, *held)
E
```

At 1723f9fd it prints 71 RELEASED and 24 HELD:

| part | files | released when these groups merge |
|---|---|---|
| p1 | ratchet script; RELEASED `tests/*.sh`, `tests/hastub/**` | now |
| p2 | `tests/*.mjs` (card family) | now |
| p3 | every other RELEASED `tests/*.py` | now |
| p4 | `stress.py`, `config_flow_steps.py` | `R11-SEAM-tests`, `R11-PRE-SHARED-FILES` |
| p5 | `harness.py` | `R11-SEAM-actuation-writes` |
| p6 | `guard_pins.py` | `R11-SEAM-dead-state`, `R11-PRE-SHARED-FILES` |
| p7 | `ci_ratchet.py` | `R11-CARRY-MACHINERY-CHECK` |
| p8 | `structure.py` | `R11-SEAM-ratchets`, `R11-SEAM-ratchet-raise`, `R11-ARCH-fabric-learner`, `R11-PRE-SHARED-FILES` |
| p9 | `entities.py` | `R11-PRODUCT-TEXT-PINS`, `R11-SEAM-inputs-freshness`, `R11-SEAM-ratchets`, `R11-PRE-SHARED-FILES` |
| p10 | the features scripts | `R11-PRE-SHARED-FILES`, `R11-OUTSIDE-HONEST-DHW-RUNS`, `R11-CARRY-DRAWMAP`, `R11-SEAM-inputs-freshness`, `R11-SEAM-learners`, `R11-ARCH-fabric-learner` |
| p11 | the files held by `R11-PRE-SHARED-FILES` alone: `run.sh`, `derive_closures.sh`, `closure.py`, `mutation_table.py`, `env_drift.py`, `harness_headers.py`, `dst_checks.py`, `finite_boundary.py`, and eight more `tests/*.py` | `R11-PRE-SHARED-FILES` |

A file is in a part only while the command prints it RELEASED at that part's
dispatch; a file a later roster edit holds moves to a part of its own. p1 adds
one `run` line to `tests/run.sh` for the ratchet and no text edit there:
`run.sh`'s comment text waits for p11. `run.sh` has no row in `PLAN.md`'s
hot-file order, so this keeps ADR-010's acceptance line. The roster's `files`
globs (`tests/*.py`, `tests/run.sh`, `tests/card.mjs`) miss the other `.mjs`
and `.sh` files. Those files are released, and no other group names them.

**C. Each part's text work.** Every file in a part receives all three of these
edits:

- **C5:** split every long sentence. A split keeps every reason, constraint and
  unit the sentence stated.
- **C2 stale paths:** run `python3 tools/audit/seat/moved_paths.py <part's files>`
  (one `tests/layout.json` sweep) together with `s9/stale_paths.py`. Each moved
  path is respelled to its successor: `tools/coverage/coverage_tree.sh`,
  `dev/programme/HANDOVER.md`, `dev/governance/roles/{fixer,judge}.md`,
  `tools/pr/preflight.sh`, `tools/devices/gen_device_fixtures.py`,
  `dev/governance/config/cfr_exclusions.json`,
  `tools/policy/check-wave-script.mjs`, `dev/archive/backlog.md`,
  `dev/programme/register/audit-2026-09.md`, `dev/audit/README.md`
  (`structure.py`) and `tools/audit/round4/D11/governance_cost.py`
  (`closure.py`). The three CONTRADICTED units name the path the code beneath
  them reads.
- **C2 cites with no successor:** pin them to the SHA or tag that holds the file,
  verified by `git cat-file -e <sha>:<path>`; otherwise state the rule inline and
  drop the name. `docs/delivery` is not one: it is respelled to its successor
  `dev/programme/delivery/`, which D5-s8-03's claim names. The rest are
  `resource_r5.py`, `ruleset.py`, `carry-201.json`,
  `carry-1922.json`, `CONDENSED.md`, the two
  `dev/programme/designs/` notes, `card_shapes.mjs` and `DESIGN.md`.
- **D5-s7-01, part p10:** each edit lands in whichever features script carries
  the block, found by its anchor and never by a line number. The "eight
  between-run" count in `_d901_gil_yield_inside_run`'s docstring
  (`features.py:6858` at the base) is restated without a number ("one per start
  after the first"). The unresolved name `_feedback_sent` (`features.py:87592`
  at the base) becomes `pump_arbiter._feedback` / `FeedbackRun.sent_c`.
  `PlantRig` (`features.py:54916`) and the `w5-partition/partition.py` path
  (`features.py:57373`) become `tools/coverage/partition.py` or are removed. All
  five C2 names come from `m4_comments.py --detail`, run over the features
  scripts (section 6).

**Invariants kept:** no code token changes (`code_changed_files=0`), and every
unit keeps its line count (`line_shifted_hunks=0`). So `span_loc`, coverage
lines, closures and `tests/mutation_ledger/` pins do not move. Deleting words is
allowed only for history words (C4), and only to stay line-neutral. When a
respelled path changes a line's length, the hunk's line count still holds.

## 4. Alternatives (lost on the code)

- **A second ratchet script for `tests/`:** two copies of the 40-word rule and
  of `--text-only`, which ADR-001 refuses. The approved verdict also carried
  the single script to this group.
- **Waiting for comments-production's part 1 to land the script:** that part
  now waits on ten behaviour groups. Meanwhile, tests parts released now would
  have no gate, and the C5 count grew by four sentences since the fork with no
  detector.
- **A stale-path arm in the ratchet:** no finding names a detector for C2, and
  `N-move-stale-path` is not barriered. Adding one changes behaviour that no
  finding of this group names, so the path rule stays a sweep run per part.
- **One PR per file, or one PR for all the released files:** about 49 PRs; or
  one review that spans the card rig and the governance scripts, roughly 500
  long units. p1 to p3 split the released set by language and family.

## 5. Sibling sites (commands)

- **C5:** the ratchet's per-file table, `s9/comments.py --show | grep -P
  '\tC5-long\t'`, `s7/m4_comments.py` (column c5_fail) and `s8/m4_ledger.py
  --show` (long_sentence_units). Their cells are disjoint and together cover
  `tests/`; parts p1 to p11 cover all of them.
- **Stale paths:** `s9/stale_paths.py | grep ^STALE`, `s8/m4_ledger.py --show`
  (unresolved rows), `s7/m4_comments.py --detail` (C2 rows), and
  `tools/audit/seat/moved_paths.py tests/`. All of them are covered.
- **Out of scope:** `tools/` comments (round-12 deferral, cited in the
  comments-production verdict), and package and card text (comments-production).

## 6. Evidence plan

- **Failing test first, p1:** the script's `--self-test`, as in the
  comments-production note section 6. It plants a 41-word sentence in a copy of
  `tests/edge.py` (refused) and in a `.sh` comment (refused). A 40-word sentence
  is the null control and passes. A move to a new file passes. `--text-only`
  reads 1 for a changed token and 1 for a shifted hunk. At 1723f9fd no test
  refuses the plant.
- **Reconcile at p1's head:** the script's per-file totals equal the three
  harnesses on the same files, to the unit. Fix each difference in the script;
  never record one.
- **Each part:**
  - The part's files read 0 in the ratchet, in C5-long (`comments.py`),
    c5/c2/c1_fail (`m4_comments.py`), unresolved (`m4_ledger.py`) and STALE
    (`stale_paths.py`).
  - Null control: every file outside the part reads what it read at the part's
    base.
  - `--text-only` reads 0 and 0, `score.py --diff` reads NULL, and
    `tests/structure.py` is unchanged.
- **Reading the features scripts.** `s9/comments.py`, `s9/stale_paths.py` and
  `s8/m4_ledger.py` enumerate the tree at the ref (`m4_ledger.py` takes one
  `--file` per script), so they read the split scripts as they stand.
  `s7/m4_comments.py` hard-codes `SEAT_FILES`, so p10 runs it through an import
  that sets `SEAT_FILES` to the features scripts plus its other two files, and
  leaves the harness unedited. Its null control is the same import with
  `["tests/features.py"]` at the base: it must reproduce c5/c1/c2 = 460/1/5.
  After the split, the 460 figure is the sum of c5_fail over the features
  scripts.
- **p10, C1:** `s7/c1_sleep_count.py` still reads 3..34 between-run calls per
  solve, and its `--perturb` arm moves. Both runs are recorded. A comment with
  no count cannot go stale with them.
- **End of group:** the five harness figures in section 1 read 0 at the head of
  the last part, with every `features.py` row read as the sum over the features
  scripts. p10 and p11 are the last parts; either may land last.
- **Goldens:** none move; both claim files stay byte-identical.
- **Mutation targets (p1 only):** the `> 40` compare, the per-file `<=`, the
  total `<=`, the new-file branch, the base resolution, the `.sh` marker
  stripping, and each `--text-only` arm. Parts p2 to p11 add no code.

## 7. Hot files, serial position, carries

p1 is the first on `tests/run.sh` of the comment groups, with a single added
line (section 3 B). It also adds a row to `tests/README.md`, ahead of
`R11-SEAM-governance-text`. `tests/closures.json` follows
`R11-PRE-SHARED-FILES`'s scheme if that has merged; otherwise the second merge
regenerates it (`gate-scoping.md`). p4 to p11 each come last on their files by
construction of the release command, and p10 comes after the split. In
`PLAN.md`'s hot-file order, the `entities.py`, `features.py` and `structure.py`
rows end in this group. p1 changes no pinned grader, so no p1/p2 split applies
unless `ci_predict.py` prints `BOOTSTRAP` at p1's handoff. Received carries: the
comments-production note's `one-sentence-ratchet`, served by section 3 A, and
the verdict's `release-command-tests-globs` and `docs-delivery-successor`, served
by sections 3 B and 3 C.

**Routed, decision: orchestrator.** Which group writes the shared ratchet
script. This note puts it in this group's p1 (section 2); the approved
comments-production note still tells its fixer to write it. Neither p1
dispatches until the orchestrator confirms one writer and lands the carry below
in that group's roster brief. If the ruling keeps the script in
comments-production, this group's p1 shrinks to the tests scope addition, and it
is dispatched after that part merges.

### Notes for the fixer

- The shared ratchet script lands in this group's p1. Comments-production's p1
  then extends its scope list to the package's top-level `*.py` and the card's
  script, and writes no second script. Carry: R11-SEAM-comments-production (item ratchet-lands-in-tests-p1)
- The comments-production verdict's four fixer notes bind this p1 in the same
  terms:
  - `text_ledger.py` goes in `INERT_EXCEPT`, recorded with `--single`.
  - Nothing is imported from `dev/audit/rounds/round11/`.
  - Read `script_runs_per_push` and `script_runs_full_case_pr` against
    `tests/ci_budgets.json`. If either is over budget, make the ratchet an arm
    of an existing gate script.
  - A shallow checkout fails closed at the ratchet base.

  Carry: R11-SEAM-comments-tests (item production-verdict-notes)
- The release set shifts whenever the roster changes. Re-run the release command
  at each dispatch and handoff, never this note's table. Carry: R11-SEAM-comments-tests (item rerun-release)
- After `R11-PRE-SHARED-FILES` part 4 lands, a test comment naming `features.py`
  may already have been respelled by its sweep. Re-run `moved_paths.py` on the
  part's files, and do not respell a name back. Carry: R11-SEAM-comments-tests (item split-respell)

Seat token count: not reported by this harness.
