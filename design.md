# Design note: R11-CI-CASE-SELECT-P2 (plan, selection, fail-safe, run.sh wiring)

- Base and code read: `origin/main` b0a4ae22dee63f1cd7a93e14f299e21f4df8e5ba. No predecessor handoff
  (R11-OUTSIDE-CI-3885 is done). P1 merged as #3896 (658fcae30b).
- Extends the approved `design/R11-CI-CASE-SELECT` 25fa1f76 (verdict b7e7f57f). Its rules (i)-(v), the fail-safe list,
  P3 and both verdict carries (rng-consume, pin-count) stand except where section 3 says otherwise.
- Agrees with `design/r11-ci-3885-rest` f139601cee on its C1 (omnibus span) and C2 (over-wide `needs`), and adopts its
  part order. That note has no `design-verdict` ref. This note adds C3 and C4.
- **No finder harness: owner report** (tvofi, 2026-11-25, as the approved note quotes it). The probe in section 6 is
  the harness.

## 0. Routing, for the orchestrator (a decision, not the fixer's)

- A fixer for this group is already stepping. `dispatch/fixer-r11-ci-case-select-p2` is at a59a1b0d9a, and its
  `handoff-wip/r11-ci-case-select-p2` is at 395ab196f5. Its plan, in tests/case_select.py at that SHA, keeps the blob
  arm ("the table's blob is neither the merge base's text nor the head's") and the forward closure from rule (i). C3 and C4 show that this rule saves nothing on either
  script, and that it falls to FULL after the next script edit. Carry: #3885
- #3896's three P2 forward-carries (selectivity, recorder overhead, pin-count) each say "lands in
  dev/programme/carries/carry-3885.json". That file at the base holds only the two light-grading carries. This note
  read them from #3896's body and is now their destination. Carry: #3885
- One group now has two designs, this note and 3885-rest. Review them together, or rule one. Carry: #3885

## 1. Re-measured at the base (`## Figures` holds the literals)

The table is tests/case_closures.json, recorded at f184477ba8, an ancestor of the base. Both script blobs in it
differ from the base's text. The probe (section 6) reads the table's `files`, `needs` and `seconds`.

| diff (one file) | script | rule (i) spans | back*(i), s share | back*(i ∪ fwd(i)), s share |
|---|---|---|---|---|
| docs/configuration.md | entities.py | 1 (`Sensors`, tests/entities.py:543) | F1 | F2 |
| .github/workflows/governance.yml | entities.py | 3, one of them `#558 D6` | F3 | F4 |
| const.py | entities.py | F5 | F6 | F6 |
| any docs or workflow file | features.py | 0 (closure.select does not pick the script) | — | — |

- Re-run on the fixer's re-recorded table, at 395ab196f5, the same rows give the same picture (F7).
- **Selectivity carry.** `python3 tests/case_select.py stats <script>` prints #3896's lines unchanged. The table
  stores the union of (a)-(d), so it cannot say whether (b) or (c) carries the width. The fixer measures that with
  the arm ablation in section 5.
- **Pin-count carry.** The enumerator is `grep -rhoE '"killed_by": *"[^"]+"' tests/mutation_ledger | sort | uniq -c`
  (F8). The replay derives the count at run time and prints it.
- **Recorder overhead: still unmeasured.** No CI job records spans at the base. Recording runs only through
  `derive_closures.sh --cases`. Section 5 owes the measurement.

## 2. Findings that change the approved rule

- **C3: rule (iii) applied to (i) is the whole cost on a diff that is not production.** `Sensors` is one span that
  takes no time. 63 later spans need it, so fwd(`Sensors`) holds every span but one. Rule (iii) exists because
  "an edited or diff-selected span may change what it binds". That holds for (ii), where the text changed. For a
  span selected only by (i), its text is the same, and its bindings move only when the changed file's content flows
  into them. That is decidable once the span has run.
- **C4: the blob arm makes the plan inert.** Of the first-parent merges between 658fcae30b and the base, 16 touched
  entities.py and 13 touched features.py (`git rev-list --first-parent --count 658fcae30b..b0a4ae22de -- <script>`).
  After any one of them, the table's `blob` matches neither the base nor the head of the next pull request. The
  approved arm then forces FULL until a Linux `--cases` re-derive, and P3's autofix unions only `files`. The blob
  arm protects nothing the per-span hash (rule ii), the `header_hash` arm and the static `needs` from the head's AST
  do not already cover. Stale `files` after a production change is a different risk: the blob is blind to it, and
  the FULL main push and P3 carry it.
- C1 and C2 as 3885-rest states them. C1 is why const.py's row reads F6 even with no closure.

## 3. Shape (owner: tests/case_select.py; callers tests/run.sh and tests/closure.py, as approved)

tests/seam_map.json maps package seams only, and no concern needs two owners.

1. **Blob arm replaced.** The script goes FULL when the table's `recorded_at` is not an ancestor of the merge base,
   when `header_hash` differs, or when a span id is ambiguous. A span whose hash moved, or that the table lacks,
   runs by (ii). The `CASES:` line adds `<k> spans stale since <recorded_at>`. `blob` stays in the table as data.
2. **Forward closure gated at run time, for (i)-only spans.**
   - Recording adds a `binds` map to each span: a digest of each name the span binds, static or dynamic. The digest
     is structural over plain data (None, bool, int, float repr, str, bytes, and tuple/list/dict/set with members
     ordered by digest), capped by depth and size, and recorded with the `@state` family fingerprints. Any other
     object digests as **opaque**.
   - The plan builds two sets. `lean = back*(ii ∪ i ∪ fwd(ii) ∪ pick(rest))`, and `full` is the approved
     `back*(i ∪ ii ∪ fwd(i ∪ ii) ∪ pick(rest))`.
   - The runner runs `lean` with its output buffered. After each (i)-only span, it digests that span's binds. If
     every digest equals the table's and none is opaque, it goes on. Otherwise it discards the buffer and re-runs the
     script under `full` in a fresh process, printing
     `CASES: ESCALATED <script> -- <span> moved <name>`.
   - **Invariant.** A span outside `lean` sees, from every producer, a value equal to the recording's, and its own
     text and `files` miss the diff. That is the same premise rule (i) already makes.

```
PR: run.sh -> closure.select -> case_select plan -> (lean, full) -> run lean, digest each (i)-only span
      -- all equal --> emit buffered output, CASES: SCOPED
      -- a digest moved or opaque --> discard, run full, CASES: ESCALATED
main push / nightly / dispatch: no plan -> every span (unchanged)
```

3. **Order:** 3885-rest's P2a (split C1) and P2b (narrow C2) come first, then this group, which is that note's P2c and
   P2d with items 1 and 2 above. Composes with R11-OUTSIDE-CI-3885-SAMPLING (`handoff/r11-outside-ci-3885-sampling`
   d928f6ad) as a union of the sets. If that lands first, this group adapts the call site, never the rule.
4. **Stop rule** (in addition to 3885-rest's): the fixer measures, over the section 5 replay, how often `lean`
   escalates and the seconds share it saves. If the replayed docs, workflow and tooling diffs escalate more than
   half the time, the gate is not shipped and the figures go to the orchestrator.

## 4. Alternatives, and why they lost

- Drop fwd from (i) outright. This is unsound. A span that parses a doc into a global feeds later checks whose
  `files` lack the doc.
- A two-pass plan: run D first only to digest it, then plan. This pays back*(D) twice on every PR. The escalation
  shape pays the extra run only when a digest moves.
- Keep the blob arm and re-record the blob on each PR. That is a Linux re-record of at least the script's seconds
  per pull request.

## 5. Sibling sites, evidence plan, hot files

- **Sibling sites.**
  - `for f in tests/*.py; do grep -cE '^R\.section' $f; done`: dst_checks, optimality, rolling and wood_advisor are
    under the approved 300 s floor, so they are out of scope.
  - `git grep -n '"blob"' -- tests tools`: the table's readers are tests/case_select.py (merge_tables, entry) and the
    plan. tools/ci/shards.py reads only span `seconds`.
- **Failing first: tests/case_select.py `--self-test` rows.**
  - (C4) A table whose blob matches neither base nor head, with `header_hash` equal and one span edited, plans
    SCOPED with that span. Mutant: restore the blob arm.
  - (C3) S reads file f and binds `DOC` parsed from it, and R reads `DOC`. An edit to f that leaves `DOC` equal gives
    SCOPED without R. An edit that moves `DOC` gives ESCALATED, with R's FAIL. Mutants: skip the comparison; treat
    opaque as equal.
  - Null: on an unmutated fixture, every plan prints no FAIL.
- **Fixer's harness under dev/audit/harnesses/.**
  - The section 6 probe as a `stats` arm, so the F-rows have an in-tree enumerator.
  - The arm ablation: record one script with (b) off, then with (c) off, and compare the median `files` per span.
  - The opaque share of the binds of (i)-only spans.
  - The approved evidence 5 soundness replay, with both nulls, run through lean and escalation.
  - The measurement table (#3875, #3887, #3596) against a FULL run on the same runner.
  - Recorder overhead: a plain run and a recording run of each script on one host, interleaved, three of each.
    The budget is 10% of script seconds.
- **No goldens move. No claim file changes.**
- **Hot files:** tests/case_select.py, tests/case_closures.json and tests/run.sh, shared with the sampling group and
  with 3885-rest's P2a/P2b, so they go in series. P3 comes after. No pinned grader in a restoring job gains a
  registration, so there is no p1/p2 split.

## 6. Probe (out of tree; the fixer lands it as the stats arm)

For a changed file f: D = {spans whose `files` hold f's index}. back* walks `needs`, and fwd walks the reverse of
`needs`. The share is Σ `seconds` over the set divided by Σ over the script. The probe reads only the table.

## Figures

- F1 0.00
- F2 1.00 (64 of 65 spans)
- F3 0.85
- F4 0.98
- F5 62 of 65
- F6 0.99
- F7: configuration.md 0.00 against 1.00; governance.yml 0.85 against 0.98; 66 spans
- F8: tests/features.py 4465, tests/entities.py 307

## Notes for the fixer

- Carry: R11-CI-CASE-SELECT-P2 (item digest-determinism) -- record each script twice on one tree and require equal
  `binds` digests before trusting any of them. A digest that moves between two identical runs (time, id, ordering)
  must be opaque, or the gate escalates on every PR.
- Carry: R11-CI-CASE-SELECT-P2 (item escalate-output) -- the lean run's output is buffered and discarded on
  escalation, so a reader sees one run's `ok`/`FAIL` lines, never two.
- Carry: R11-CI-CASE-SELECT-P2 (item stale-since) -- with the blob arm gone, print the stale-span count on every
  `CASES:` line, so a table that is never re-recorded shows on every pull request.
