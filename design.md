# Design: R11-SEAM-comments-tests (round 11, size XL)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 50a932de3b2a9db4a5e9213bff6b5be06e26f13b: ADR-010 parts 2, 3 and 5,
`PLAN.md` "Hot-file order". Roster row read on `handoff/audit-r10-roster`
(83ef6bc3, `wave-r11-groups.json`; the base carries no r11 roster). Base, and
code read at, `origin/main` 1723f9fdc9d8a6e6987190d2887686297a621dd4; the group
has no `after` edge, so there is no predecessor head. No production code on this ref.

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

**B. Parts by release.** Run the release command of the comments-production
note section 3 B with `git ls-files tests/`, the roster at
`origin/handoff/audit-r10-roster`, and every `tests/` `.py`/`.mjs`/`.sh`
accepted. Run it at each dispatch and again at each handoff. At 1723f9fd it
prints these files as HELD:

| part | files | released when these groups merge | long (s9/s7) |
|---|---|---|---|
| p1 | ratchet script; `tests/*.sh`, `tests/hastub/**` | now | `run.sh` 15, hastub 4+ |
| p2 | `tests/*.mjs` (card family) | now | `card.mjs` 106 units (s8) |
| p3 | every other RELEASED `tests/*.py` | now | `env_drift` 34, `mutation_table` 31, `replay` 30, `closure` 79 units, ... |
| p4 | `stress.py`, `config_flow_steps.py` | `R11-SEAM-tests` | 112 |
| p5 | `harness.py` | `R11-SEAM-actuation-writes` | per harness |
| p6 | `guard_pins.py` | `R11-SEAM-dead-state` | per harness |
| p7 | `ci_ratchet.py` | `R11-CARRY-MACHINERY-CHECK` | per harness |
| p8 | `structure.py` | `R11-SEAM-ratchets`, `R11-SEAM-ratchet-raise`, `R11-ARCH-fabric-learner` | 17 |
| p9 | `entities.py` | `R11-PRODUCT-TEXT-PINS`, `R11-SEAM-inputs-freshness`, `R11-SEAM-ratchets` | 470 |
| p10 | `features.py` | `R11-PRE-SHARED-FILES`, `R11-OUTSIDE-HONEST-DHW-RUNS`, `R11-CARRY-DRAWMAP`, `R11-SEAM-inputs-freshness`, `R11-SEAM-learners`, `R11-ARCH-fabric-learner` | 460 |

A file is in a part only while the release command prints it as RELEASED at that
part's dispatch. A file that a later roster edit holds moves to a part of its
own. The roster's `files` globs (`tests/*.py`, `tests/run.sh`, `tests/card.mjs`)
miss the other `.mjs` and `.sh` files. Those files are released, and no other
group names them.

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
  drop the name. These are `resource_r5.py`, `ruleset.py`, `carry-201.json`,
  `carry-1922.json`, `docs/delivery`, `CONDENSED.md`, the two
  `dev/programme/designs/` notes, `card_shapes.mjs` and `DESIGN.md`.
- **D5-s7-01, part p10:** the "eight between-run" count at `features.py:6858`
  is restated without a number ("one per start after the first"). The
  unresolved names `_feedback_sent` become `pump_arbiter._feedback` /
  `FeedbackRun.sent_c`. `PlantRig` and the `w5-partition/partition.py` path
  become `tools/coverage/partition.py` or are removed. All five C2 names come
  from `m4_comments.py --detail`.

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
  `tests/`; parts p1 to p10 cover all of them.
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
- **p10, C1:** `s7/c1_sleep_count.py` still reads 3..34 between-run calls per
  solve, and its `--perturb` arm moves. Both runs are recorded. A comment with
  no count cannot go stale with them.
- **End of group:** the five harness figures in section 1 read 0 at p10's head.
- **Goldens:** none move; both claim files stay byte-identical.
- **Mutation targets (p1 only):** the `> 40` compare, the per-file `<=`, the
  total `<=`, the new-file branch, the base resolution, the `.sh` marker
  stripping, and each `--text-only` arm. Parts p2 to p10 add no code.

## 7. Hot files, serial position, carries

p1 is the first on `tests/run.sh` of the comment groups. It also adds a row to
`tests/README.md`, ahead of `R11-SEAM-governance-text`. `tests/closures.json`
follows `R11-PRE-SHARED-FILES`'s scheme if that has merged; otherwise the second
merge regenerates it (`gate-scoping.md`). p4 to p10 each come last on their file
by construction of the release command. In `PLAN.md`'s hot-file order, the
`entities.py`, `features.py` and `structure.py` rows end in this group. p1
changes no pinned grader, so no p1/p2 split applies unless `ci_predict.py`
prints `BOOTSTRAP` at p1's handoff. Received carries: the comments-production
note's `one-sentence-ratchet`, served by section 3 A.

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

Seat token count: not reported by this harness.
