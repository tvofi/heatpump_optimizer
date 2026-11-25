# Design note: R11-CI-CASE-SELECT, case-level test selection by diff

Revision 2 (answers design review `revise e50b4a1f`, verdict c90cde83: fail-open header arm, backward-only `needs`,
replay without a null; changes in sections 3, Selection rule, Fail-safe and Evidence 5). Owner order (tvofi, 2026-11-25 ~08:55Z, via the orchestrator), at the same priority as #3885: on a pull
request, run only the cases of a selected script whose recorded reads reach the diff. Pushes to `main` and the nightly
stay FULL. Code read at `origin/main` 34c7a3f6100322063f675672cfdf51662ef53959. No predecessor handoff. **No finder
harness: owner report.** The evidence below is the harness. Composes with the parallel #3885 branch
`fix/ci-3885-scope-long-scripts` (30% seeded case sampling, not on origin when this note was written).

## What runs today

`tests/closure.py` `select()` reads `tests/closures.json`, one read set per script recorded by `_exec_record` (an
`open` audit hook plus the end-of-run `sys.modules` sweep) or by strace on Linux (`tests/derive_closures.sh`). A
selected script runs whole. `tests/closures.json`'s `recorded` block gives `tests/features.py` 1616.7 s and
`tests/entities.py` 1338.1 s, ahead of `tests/stress.py` at 928.7 s. Neither long script has callable cases. Each is a
flat module whose cases are the spans between top-level `R.section(...)` statements: 248 in features.py and 64 in
entities.py (`grep -cE '^R\.section' <script>`). The spans share module globals: fixtures, coordinators such as
`_stale_coord` (tests/entities.py:3260) and monkeypatches. `tools/audit/seat/features_block.py` already runs one span
in the namespace the header builds, and derives the earlier bindings that span reads (`--emit-prelude`).

## Owning seam and shape

**Owner: a new tests module, case_select** (its own file, so `tests/closure.py` grows no lines). It holds the span
splitter, the recorder, the table reader and the per-script plan. Callers only: `tests/run.sh` (runs a selected long
script through it), `tests/derive_closures.sh` (records), `tests/harness.py` (one hook in `Results.section`), and
`tests/closure.py` (classifies the new files as gate files). `select()` keeps the script level unchanged. Case
selection runs only inside a script that `select()` already chose.

1. **Unit.** A span is one top-level `R.section(<literal>)` statement up to the next one, cut from the AST. The
   header is everything before the first span. A `section` call inside a function or loop is no boundary. The span
   id is the literal title, suffixed `#2`, `#3` and so on for repeats. The span's text hash is the sha1 of its source
   lines.
2. **Runner.** `case_select run <script> --plan P` executes the header, then each span in order, every one compiled
   from its own source slice into one namespace, as `features_block.run` does. Spans outside the plan are not
   executed. The script's closing `sys.exit(R.close(...))` runs last. Record mode and select mode use this one
   runner, so the recorded units are exactly the executed ones. Output is today's, plus one key line per script:
   `CASES: SCOPED <script> -- <n> of <m> spans (<d> diff, <s> sample, <k> needed)` or
   `CASES: FULL <script> -- <reason>`.
3. **Recording (per span).** It extends `_exec_record` and does not replace it. The per-span read set is the union of
   four sets:
   - (a) `open` audit events while the span runs.
   - (b) the files of code objects started in the span, from `sys.monitoring` `PY_START`. Each callback returns
     `DISABLE`, and `sys.monitoring.restart_events()` runs at each boundary. That is one callback per code object per
     span.
   - (c) static references. For each code object in (b), and for the span's own AST, each name bound by
     `import X` / `from X import N` in its module resolves to X's file. One more hop follows X's module-level
     references. This catches a constant read with no code run, such as `const.FAULT_HOLD_AFTER`.
   - (d) the span's subprocess argv paths, as `_exec_record` collects them.

   Each span also gets **`needs`**: the earlier spans it depends on. Three sources, all unioned:
   - **Static, from the head's AST at plan time** (never only from the table, so an edit's new edges are seen):
     names the span reads that an earlier span binds. Binding is assignment, def, class, `global`, an `X.attr =` /
     `X[k] =` target, and an in-place call on a module-level name (`X.append/extend/update/insert/pop/clear/
     setdefault/add/remove/discard(...)`, `setattr(X, ...)`), each counted as binding X. Top-level in-place calls
     today: 116 in features.py, 24 in entities.py (`grep -cE '^\S+\.(append|extend|update|insert|pop|clear|
     setdefault|add|remove|discard)\('`); calls inside function bodies bind the names the AST resolves to module scope.
   - **Stdlib process state, as a named pseudo-binding.** A span that calls a setter of `random`/`np.random` seed,
     `os.environ`, `time.tzset`, `sys.path`/`sys.modules`, `logging`, `warnings` or `locale` binds the pseudo-name
     `@<setter family>`; a span that reads that family (e.g. any `random.`/`np.random.` call) needs it. Top-level
     setters today: 5 in features.py (including `_random.seed(7)` at :20867 and `_random.seed(11)` at :23302), 2 in
     entities.py. RNG is order-sensitive: every span between a seeder and a selected consumer that also consumes
     that RNG is pulled in. A setter the AST cannot classify (a call through an alias it cannot resolve) makes the
     script FULL.
   - **Dynamic, record mode only**: a container fingerprint (`id()` and, for list/dict/set, length plus a cheap
     content hash) of each module-level global and each non-stdlib module's `__dict__`, before and after each span.
     A span that moves one binds that name or module for every later reader. Header reads are recorded apart,
     under `header`.
4. **Table.** A new file, case_closures json under `tests/`. It is not new keys in `tests/closures.json`, which is
   a gate file, carries the `ledgermerge` driver (.gitattributes), and is read whole by every `select()`. Shape:
   `{"version":1, "recorded_at":<sha>, "files":[<path>...], "scripts":{<script>:{"blob":<git blob of the script>,
   "header_hash":…, "header":[idx…], "spans":{<id>:{"hash":…, "files":[idx…], "needs":[id…], "seconds":s}}}}}`.
   Each path is stored once and spans hold int indices. Expected size: 312 spans × about 80 indices plus a path list
   of about 600 (the two closures hold 603 files), about 200 KB. The fixer measures it and states it. The table is a gate file, with the same rule
   `tests/closures.json` has: a change to it runs the spans whose entry moved. It gets a `ledgermerge` arm that
   unions each span's `files` and `needs`.

```
PR: run.sh -> closure.select (scripts) -> case_select.plan(script, diff, table, base table)
      -> D = diff spans; run = closure(D ∪ pick(rest)) -> case_select run script --plan
main push / nightly / schedule: GATE_SCOPE=full -> no plan -> every span (unchanged path)
```

## Selection rule (per selected script, pull_request only)

A span runs when any of these holds:
- (i) its `files` meet the changed units (`unit_of`, as `select()` uses).
- (ii) it has no recording, or its text hash differs from the table entry (new or edited span).
- (iii) **forward**: some span in (i ∪ ii) is in its `needs*`, transitively. An edited or diff-selected span may
  change what it binds, so every later span that reads those bindings runs, even when its own files miss the diff.
- (iv) it is sampled.
- (v) **backward**: it is in `needs*` of any span selected by (i)-(iv), so each running span has its producers.

The closure is computed to a fixed point: (v) is applied after (iii) and (iv), and (iii) again over whatever (v) added
when that span is itself in (i ∪ ii); `needs` edges come from the head's AST plus the table's dynamic edges.
A span that reads many files gets no special rule. It is selected by (i) as often as its reads say, and the plan prints
the spans whose `files` hold more than half of `custom_components/`, and the (iii) fan-out per diff span. Shared
fixtures run through (v), never by copying. **Sampling composes as a union**: `D = (i ∪ ii)`,
`rest = spans − D − fwd(D)`, then `run = back*(D ∪ fwd(D) ∪ pick(rest))`. The plan logs every selected id with the
rule that chose it, one line per span, into the job log and the uploaded artifact.
The helper shape expected of #3885 is a case_sample module with
`pick(ids: list[str], *, seed: str, fraction: float) -> set[str]`: deterministic in `seed` (the PR head sha), with
the fraction read from one constant. If #3885 lands another shape, this group adapts the call site, never the rule.

## Fail-safe: FULL for the script

The whole script runs, with the reason in its `CASES: FULL` line, when:
- the table is missing, unparseable or at another `version`;
- the header's hash at the head differs from the table's `header_hash`, whatever the `blob` says (a header edit
  rebinds what every span sees, so no span-level rule can scope it);
- the script's `blob` in the table matches neither the merge base nor the head (the table describes another text);
- any changed file is `tests/harness.py`, anything under `tests/hastub/`, the case_select module, the case_sample
  module, `tests/run.sh` or `tests/closure.py`;
- the splitter finds no span;
- a span's id is ambiguous after an edit, meaning two spans with one title whose hashes both moved;
- the AST pass meets a stdlib-state setter it cannot classify, or a `global`/`exec`/`globals()[...]` write at the
  span level;
- the event is not `pull_request`.

A span the table lacks always runs (rule ii). Nothing is ever skipped for want of data.

## CI re-recording (`ci-autofix.md` applies)

- On a pull request the runner records every span it runs (Linux, `strace` path unchanged for the script level) and
  uploads the recordings with `closures-autofix`'s artifact. A span whose fresh set holds a changed-file unit its
  table entry lacks is `CASE UNDER-SCOPED`, repaired by `closures-autofix`'s existing commit (`ci: re-record
  closures`) as a **union** into that span only. A pull request never shrinks an entry.
- A shrink, a new script or a format change goes through a full Linux re-derive, `derive_closures.sh --cases`. It
  runs in CI on `workflow_dispatch`, or on a Linux seat, never off Linux (`gate-scoping.md`). Darwin may only
  `--cases --single <script>` as a union.
- The FULL push to `main` records too, and prints `CASE UNDER-SCOPED` lines without committing, so a wrong entry
  shows on `main` within one burst (the rule-1 backstop).

## Evidence plan (failing first; null control in each)

1. Splitter. Span counts equal the `grep -cE '^R\.section'` count per script. Null: a nested `section` call cuts
   nothing.
2. Runner equivalence. A full-plan run of features.py and entities.py prints the same `ok`/`FAIL` lines, in order,
   as `python3 <script>` on one tree (a diff of the two logs is empty). Null: dropping one span removes exactly that
   span's lines.
3. Recorder. A synthetic two-span script in a temp dir: span B reads a constant of module M and calls no M code, so
   B's set holds M (c). Mutant: drop (c) and the check fails. Span C rebinds `M.f`, so D, which reads M, carries
   `needs:[C]`. Mutant: drop the `id()` snapshot.
4. Selection. Over the synthetic table: rules i-v each select, and each fail-safe trigger gives `CASES: FULL`.
   Cases that fail first: a header edit with the table blob equal to the merge base must give FULL (the revision-1
   arm passes it); an edited span A that binds `x` read by a later span B whose files miss the diff must select B;
   a span that seeds `random` before a sampled consumer must pull in every RNG consumer between them; an in-place
   `L.append` in A must give B (reads `L`) `needs:[A]`. Mutation targets: the `files ∩ changed` test, the
   hash-mismatch arm, the `header_hash` arm alone, the forward closure, the backward closure, the in-place binding,
   the stdlib pseudo-binding, and each FULL trigger.
5. **Soundness replay** (the harness that matters), driven by known mutants, not by history. Source:
   `tests/mutation_ledger/` pins (`{anchor, killed_by, old, reason}`), 5968 in all, of which 4229 name
   `tests/features.py` and 305 `tests/entities.py`. Draw a seeded sample of at least 200 pins from those two (seed
   and size printed; stratified by production file). For each: apply the mutant at the head, plan with the mutated
   file as the only diff at sample fraction 0, run the plan, and require at least one FAIL line. A mutant the plan
   lets pass while the full script fails it is a defect, not a residual. **Null control**, per pin, in the same run:
   the plan with rule (i) disabled for the mutated file (equivalently, a plan restricted to spans whose `files` miss
   it) must let the mutant pass in at least 90% of pins; a null that also kills means the pin does not test
   selection and is reported as such. **Second null**: an unmutated tree under the same plans prints no FAIL. Also
   replay the 3 diffs below and 5 more from `git log --first-parent`: every span whose outcome differs between the
   parent's and the head's full runs must be selected.

## Measurement plan (expected PR seconds; the fixer measures and replaces each estimate)

Each estimate is `T ≈ header + Σ(selected+needed span seconds) + 0.3 × Σ(rest)`, from the table's per-span `seconds`.
The null for each row is the FULL script seconds measured in the same run on the same runner, not the recorded figure.
Today's script-level selection, from `tests/closures.json` at 34c7a3f610:

| merged PR | kind | changed (less ledger/rows) | today | expected |
|---|---|---|---|---|
| #3875 store DOMAINS | production | boost, coordinator, snapshots, store; features.py, entities.py | both whole, 2955 s | features.py and entities.py are edited, so their edited spans run plus every span reading store/boost: est. 40-60% |
| #3887 instrument-self-tests cap | tooling | `.github/workflows/governance.yml` | entities.py whole, 1338 s | the spans reading workflows plus a 30% sample: est. 450-550 s |
| #3596 user-docs verify | docs | `docs/architecture.md`, `docs/configuration.md` | entities.py whole, 1338 s | the doc-claim spans plus a 30% sample: est. 450-550 s |

The floor is the sample. Without #3885's 30%, the last two fall to the header plus a few spans.

## Refusals and risks

- Refused: a per-check (`R.check`) unit. Checks share a span's local setup, and skipping one would need rewriting
  7,637 call sites (the `R.check(` count in the two scripts).
- Refused: rewriting the scripts into functions. That is a 100k-line move, and features_block shows it is not
  needed.
- Risk: hidden cross-span state that neither the static nor the `id()` rule sees, such as a mutated shared object's
  contents. Mitigated by (iii), the soundness replay (5) and FULL main pushes. A miss found there is a recorder
  defect. The forward closure (iii) costs speed on a header-near edit; the measurement table states its fan-out.
- Owner of a `CASE UNDER-SCOPED` repair on `main`: the FULL push only prints it; the next `closures-autofix` run on
  any pull request, or the nightly re-derive (`nightly.yml`, committing via `record/autofix`), commits the union.
- Risk: recording overhead. The fixer measures `sys.monitoring` plus the snapshots on a FULL main run; the budget is
  ≤10% of script seconds, or recording moves to the nightly alone.
- Out of scope: `tests/stress.py` (its memory pass is one span by design; #3825/#3890) and every script under
  300 s.

## Parts (L)

- **P1:** the splitter, the runner, the recorder, the table, `derive_closures.sh --cases`, and evidence 1-3. Nothing
  selects yet. Merges with a recorded table.
- **P2:** plan, selection and fail-safe, `run.sh` wiring and the composition with case_sample (after #3885 merges),
  plus evidence 4-5 and the measurement table.
- **P3:** `closures-autofix` and `CASE UNDER-SCOPED`. Editing `.github/workflows/tests.yml` and `ci-autofix.md` is
  policy: owner approval before merging.

## Notes for the fixer

- Carry: R11-CI-CASE-SELECT (item gate-classify) -- the table and the case_select/case_sample modules are new tracked
  files. Classify them in `tests/closure.py` (gate files), or `tests/entities.py` refuses them.
- Carry: R11-CI-CASE-SELECT (item ledger-arm) -- give the table its own `ledgermerge` arm before the first two
  branches both touch it; the claim-file precedent is `claim-files.md`.
- Carry: R11-CI-CASE-SELECT (item key-line) -- seats key on `CASES:` lines as they do on `MODE:`. Add one sentence
  to `gate-scoping.md` in P3, which is policy.
