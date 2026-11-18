# Design: R11-SEAM-comments-production (round 11, size XL)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75: ADR-010 parts 2 to 5,
`PLAN.md` "Hot-file order". Roster row read at `handoff/audit-r10-roster`.
Code read at `origin/main` bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; the group
has no `after` edge, so no predecessor head. No production code on this ref.

## 1. What each finding reads at the base (finder's harness, run here)

| finding | harness (under `dev/audit/rounds/round11/` on `plan/r11`) | fork 92d38ecb | bc658f9ded |
|---|---|---|---|
| D5-s3-03 (merged in) | `D5/s3/c5_long.py` `long_units` | 363 | 372 |
| D5-s4-01 | `D5/s4/comments.py` `long_units` | 558 | 559 |
| D5-s3-02 | `D5/s3/slider_ceiling.py` `stale_rows` | 1 | 1 |

`--perturb` controls reproduce: `c5_long.py` 352 (dhw_planner 29 to 9),
`slider_ceiling.py` `overshoot_c=1.0`, `stale_rows=0`. The count grew by ten
units since the fork: behaviour merges add long sentences while nothing
measures them. That is why the ratchet lands first.

## 2. Owning seam

Production comments (`COMPONENTS.md`): the comment and docstring text of the
package's modules and of the card's script. No caller: no interface, payload key,
entity attribute or string changes. The detector lives under `tests/`; ADR-010
assigns it to this group. ADR-001 forbids a second copy of the 40-word rule, so
`R11-SEAM-comments-tests` extends the same script's scope (carry, section 7).
One owner, no stop.

## 3. Shape

**A. The ratchet (part 1).** One new test script under `tests/`, registered in
`tests/run.sh`, with its closure measured. It applies the finders' rule:
`tools/audit/text_ledger.py` `units_of(..., "D5")` and `sentences`, comment
markers stripped as `c5_long.py` (`#`, `#:`) and `comments.py`
(`strip_js_comments`) do. A unit is long when one sentence has more than 40
whitespace words. The scope is the package's top-level `*.py` and the card's
script, as a list the tests group extends. It is **derived, not stored**: the
script measures HEAD and the ratchet base and refuses when:

- a file present at both ends has more long units at HEAD; or
- the scope's total long units is higher at HEAD. A file new at HEAD is counted
  by the total, so a module split that moves a docstring passes and a new long
  unit does not.

The ratchet base comes from `tests/mutation_table.py`'s `ratchet_base`
(merge base on a branch, `HEAD^1` on main). A refusal names the file, both
counts, and each new long unit's first words; text_ledger's JS line numbers are
unreliable (D5-s4-03), so a word quote stands in for a line.
`--text-only <base>` mode, for every part: for each `.py` file, `ast.dump`
with docstrings removed is equal at both ends; for the card, the text after
`strip_js_comments` is equal once whitespace is normalised; every
`git diff -U0` hunk has equal old and new line counts. It prints
`RESULT code_changed_files=<n> line_shifted_hunks=<n>`.

```
tests/run.sh -> ratchet script -> git show <ratchet base>:<file> --\
                               -> worktree file -------------------> text_ledger.units_of/sentences
                               <- per-file counts, total, refusal  <-/
```

**B. Parts by seam (ADR-010 part 2).** Part 1 holds the ratchet and the files
the release command prints `RELEASED` at its dispatch (21 files, 53 long units
at bc658f9ded). Every other part is one seam of `COMPONENTS.md`'s component
view, dispatched once its last file is released. The parts have no edges
between them. The `k` label is fixed; the dispatch order is the release order.

| part | seam | held files | long units | held by (groups, at the roster ref) |
|---|---|---|---|---|
| p2 | money | 6 | 39 | 5 |
| p3 | persisted store | 2 | 11 | 3 |
| p4 | input boundary | 6 | 34 | 5 |
| p5 | shared kernel | 5 | 52 | 10 |
| p6 | config surface | 4 | 49 | 8 |
| p7 | actuation | 10 | 52 | 12 |
| p8 | entity and service surface | 11 | 64 | 11 |
| p9 | learners | 9 | 88 | 10 |
| p10 | solver | 7 | 113 | 7 |
| p11 | plant model | 9 | 118 | 10 |
| p12 | card (`www/heatpump-optimizer-card.js`) | 1 | 158 | `card`, `product-text` |
| p13 | cycle (`coordinator.py`'s whole row) | 6 | 105 | 20 |

(Long units by the section 3 A rule; section 6 reconciles them with the
harnesses.) The release command, run from the repository root at each dispatch
and again at each handoff:

```
python3 - <<'E'
import fnmatch, json, subprocess, sys
sys.path.insert(0, "tools/audit/seat"); import roster_lib as R
P = "custom_components/heatpump_optimizer/"
G = R.groups_of(json.loads(subprocess.check_output(["git", "show",
    "origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r11-groups.json"])))
for f in subprocess.check_output(["git", "ls-files", P]).decode().split():
    if not ((f.endswith(".py") and f.count("/") == 2) or f.endswith("card.js")): continue
    held = [n for n, g in G.items() if "comments-" not in n and R.gates(g) and any(
        fnmatch.fnmatch(f, p if p.startswith("custom") else P + p)
        for p in (g.get("files") or []) + (g.get("hot_files") or []))]
    print("HELD" if held else "RELEASED", f[len(P):], *held)
E
```

`roster_lib.gates` already decides when a group holds back another group, so
the release command adds no second rule for that. A `carries-open` or `deferred`
group keeps its files held.

**C. D5-s3-02.** One bullet of `comfort_band.py`'s module docstring is
rewritten to say the slider's maximum equals the ceiling (`climate.py` sets
`_attr_max_temp` to `max_temperature`). ADR-010 part 4 puts it in the first
part, but `R11-SEAM-inputs-guards` names `comfort_band.py` and has not merged.
It therefore rides the first part dispatched after that group merges, with that
file's own long units, whatever that part's seam.

**Invariants kept:** no code token changes (`code_changed_files=0`); every unit
keeps its first line and its line count (`line_shifted_hunks=0`). As a result,
`tests/structure.py`'s line-span metrics (`span_loc` counts docstring and
comment lines), coverage line numbers and closures do not move. A split keeps every reason, constraint
and unit the sentence stated. A deletion is allowed only for history words (C4),
and only to stay line-neutral.

## 4. Alternatives (lost on the code)

- **A key in `tests/structure_budgets.json`:** that ratchet is two-sided. Any
  behaviour PR that deletes a long comment (`R11-SEAM-dead-state`) would be
  refused as "improved, not recorded". Every part would also edit a row that
  three groups own in the hot-file order. ADR-010 wants `tests/structure.py`
  unchanged by a comment PR.
- **A stored per-file budget file:** `tools/policy/budget_raise_gate.py`
  grades a budget file with no SCHEMA entry as frozen, and restores itself from
  the base. Part 1 would then need the owner's review as a raise, and every part
  would re-record its rows on a shared file. The derived base needs neither.
- **One PR per released file, or per release batch:** about 76 PRs, or batches
  that cross seams. A seam part pays a module family in one review, and its
  release is one condition.
- **Only the finder harnesses, run by hand:** they live outside the gate, so the
  ten-unit growth since the fork would continue.

## 5. Sibling sites (commands)

- The C5 sites are every long unit in scope: the ratchet's per-file table,
  `c5_long.py` (per-file lines) and `comments.py --tsv OUT` (column `long`).
  All are covered by parts 1 to 13.
- D5-s3-02's class: a docstring that describes another module's behaviour in
  the present tense. `git grep -n -i "one degree above\|one degree \*above" custom_components/heatpump_optimizer/`
  finds `comfort_band.py` (present tense, the finding) and `coordinator.py`
  `_audit_comfort_band` (past tense, true: no edit). No general enumerator exists;
  the D5 ledgers' history and numeric columns (`comments.py` `hist_units`,
  `num_units`) are other criteria, out of scope.
- `comments.py`'s `unresolved_units` (C2) belongs to D5-s4-02, owned by
  `R11-SEAM-learners`. It is out of scope.

## 6. Evidence plan

- **Failing test first (part 1):** the script's `--self-test`. It plants a
  41-word sentence in a copy of `pump_mode.py` (refused). A 40-word sentence is
  the null control (passes). Moving a long docstring to a new file passes, and
  adding one to a new file is refused. A changed code token and a shifted hunk
  each read 1 in `--text-only`. Before the script exists, nothing refuses the
  plant.
- **Reconcile at part 1's head:** the ratchet's total equals `c5_long.py` plus
  `comments.py` `long_units` on the same files, to the unit. Each per-file
  difference is named and fixed in the script, never recorded (this note's
  quick reading was 936 against 931).
- **Each part:** the part's files read 0 in the ratchet and in the harnesses'
  per-file output. The null control is that every file outside the part reads
  what it read at the part's base. `--text-only` reads 0 and 0; `score.py
  --diff` reads NULL; `tests/structure.py` is unchanged.
- **D5-s3-02:** `slider_ceiling.py` `stale_rows` goes from 1 to 0 and
  `docstring_claims_plus_one` from 1 to 0. Record `--perturb` at both ends. The
  harness builds the real `HeatPumpOptimizerClimate`, so the evidence runs the
  code the docstring describes. A text-only part adds no behaviour test.
- **End of group:** `c5_long.py` 0 and `comments.py` `long_units` 0 at the last
  part's head.
- **Goldens:** none move; both claim files stay byte-identical.
- **Mutation targets (part 1 only):** the `> 40` compare, the per-file `<=`, the
  total `<=`, the new-file branch, the base resolution, and each `--text-only`
  arm. Parts carry no mutation proof because they add no code. Any
  `tests/mutation_ledger/` pin that a part moves is re-keyed, never
  re-triaged (ADR-010 part 5); line-neutral parts are expected to move none.

## 7. Hot files, serial position, carries

Part 1 is first on `tests/run.sh`, ahead of `R11-SEAM-comments-tests`.
`tests/README.md` gains one script row, before `R11-SEAM-governance-text`.
`tests/closures.json` has no order: if `R11-PRE-SHARED-FILES` (which generates
it after merge) lands first, part 1 follows that scheme; otherwise the second
to merge regenerates (`gate-scoping.md`). Each later part is last on every file
it touches, by construction of the release command, and the card's script comes
after `R11-SEAM-card` and `R11-SEAM-product-text`. Part 1 changes no pinned
grader, so no p1/p2 split applies. A `ci_predict.py` `BOOTSTRAP` at part 1's
handoff would mean otherwise, and the split then follows `fixer.md`. Received
carries: none.

### Notes for the fixer

- `R11-SEAM-comments-tests` adds `tests/` scope to this group's ratchet script
  rather than writing a second 40-word rule (ADR-001). Its finders' harnesses
  must reconcile with that script the same way. Carry: R11-SEAM-comments-tests (item one-sentence-ratchet)
- If part 1 merges while groups are mid-flight, a branch that adds a long unit
  turns red on the ratchet. The refusal quotes the unit, so the fix is one
  split. Carry: dismissed: the criterion binds every group; nothing to deliver (item inflight-red)
- `cloud_dispatch.py --part` splits by carry index. These parts are by seam, so
  each dispatch names its seam's files from the release command. Carry: dismissed: dispatch practice for the orchestrator, no code owed (item part-by-seam)
