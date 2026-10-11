# R9-RO-PC1: a prose count survives a byte-identical merge, because coverage keys on sentences

This is the root-cause seat's analysis of a class that cost three resolution rounds on
2026-10-09 (#2024, #2065, #2066). The seat followed `dev/governance/roles/root-cause.md`;
the countermeasure is the census arm group `R9-RO-PC1` carries. Measurements were taken at
`origin/main` `d0f085ffb` and reproduced in detached worktrees under
`/Users/timmalmstrom/hpo-seats/rca-prose-counts/`.

**Trigger:** the defect reached pull requests that every existing instrument read as green,
and each occurrence consumed a full resolution round — 110.0, 110.1 and 138.7 wall-clock
minutes, measured from first to last artifact mtime in each round's evidence directory
(`orch-resume-1009/ux9-recarry`, `live-power-clamp/scratch/r5`, `live-cop-floor/ev/r9`).

## 1. The defect, reproduced

Two seats cut from the same tip `d0f085ffb`:

- `seatA` = `e8d7be6cc` adds `abs_probe.py`, edits `docs/architecture.md` `74 modules` →
  `75`, `27 of the 74` → `27 of the 75`, `The other 46` → `47`, and inserts its map row
  after `const.py`.
- `seatB` = `7a5818618` adds `zip_probe.py`, makes **the byte-identical three prose edits**,
  and inserts its map row after `presets.py`.
- `mergeAB` = `ac3af92bf` is `git merge` of B into A: **rc 0**, `Auto-merging
  docs/architecture.md`, **zero conflicted files** (`logs/merge-repro.txt`).

The merged prose reads `75 modules` / `27 of the 75` / `The other 47`; the merged tree holds
**76** modules and **48** HA-free. The prose sentences are identical on both sides, so `ort`
sees one change; the map rows are on different lines, so both survive. The count is false
**and** git reports nothing — which is exactly the shape of the three incidents.

What does catch it at that tree: `dev/audit/rounds/round4/D6/claims.py` reports
`claims_false=1` with `FALSE C32`, and `tests/entities.py` names three FAILs (the opening
counts, the HA boundary, the HA-free count) — `logs/claims-merged.txt`,
`logs/entities-merged.txt`. So the sentences *are* read. The escape is not in the check; it
is in the unit it is keyed on.

## 2. Process state: (c) — followed, did not produce the result

Not an absence of checks; a coverage gap in what they key on.

- `tests/entities.py:1053-1068`, the #939 block: *"every figure below is DERIVED — the module
  list from the directory, the boundary from an AST walk, the pages from `_OPTION_PAGES`, the
  services from services.yaml … never carried"*. State-(c) machinery: it exists, it ran, and
  it is correct — **for `architecture.md`**.
- `dev/audit/rounds/round4/D6/claims.py:737` C32 matches `r"(\d+) modules, of which"` —
  **that sentence, in that file**. C34/C37/C39 likewise. None touches `docs/setup.md` or the
  `options pages` phrasing.
- `tests/doc_claims.py:36-40` states the promise the class breaks: *"the claim set is derived
  by scanning the reader documents … Neither side is a hand-maintained enumeration: a new
  sentence of the same shape enters the check the moment it lands."* For **counts** that
  promise is kept once. `check_multistart_starting_points` (lines 961-972) is corpus-wide —
  `multistart_count_claims(CORPUS)`, and its own null control fires on a stale count. No
  equivalent census exists for modules, services, option pages, fields or sensors.
- `tests/closure.py:543-547` keeps `docs/architecture.md` off `INERT`, so a false count there
  does redden a pull request — but at `entities.py`'s **259.6 s** or `harness_headers.py`'s
  **220.7 s** recorded CI seconds (`tests/closures.json`), not at the cheap gate's. The cheap
  gate's own recorded seconds are in that same file: `doc_claims.py`, **8.6 s**.

Not (a): the checks exist and caught incidents 1 and 3. Not (b): the resolution seats ran
them (DELTA.md §2, §4). Not (d): no precondition moved — the un-pinned sentences were never
covered at all.

## 3. The enumeration, and the headline

`git grep -noE '[0-9]+ (modules?|files|entities|scenarios|checks|pairs|scripts|services|sensors|buttons|switches|rows|platforms|option[s]? pages|pages|commands|fields|keys|selectors)' -- README.md docs/ ':(exclude)docs/design'`

answers **22 instances, 1 false positive** (4.5% — `README.md:948`, where the digits inside
`ECL110` collide with `+ sensors`). That grammar is unanchored, which is what admits the false
positive at all; the same grep with a `\b` before the digits answers **21 instances, 0 false
positives**, and that is the grammar `logs/enumeration.txt` was produced with
(`enumerate_final.py`) — so the two counts are two commands, not two runs of one. Per-instance
read/unread verdicts, each decided by
perturbation rather than by regex-guessing, are in `logs/enumeration.txt`; an earlier
attribution by regex over-fired and was discarded.

**Headline: 6 unprotected instances.** Three inside the 22 — `README.md:692` *all 31 fields*,
`configuration.md:9` and `setup.md:263`, both *the 23 options pages*. Three that the
digit-noun pattern itself misses — `README.md:824` *22 you can edit*,
`dashboard-card.md:723` *its five pages*, `ecl110.md:91` *All eight settings*. Two further
instances (`architecture.md:176`, `:204`) are read by `entities.py` **only**: protected, but
at the 259.6 s lane rather than the cheap one. (The seat's own `/usr/bin/time` measured
`claims.py` at 2.30/2.54 s on its box; `claims.py` is a round harness and not a recorded
closure script, so `tests/closures.json` carries no seconds for it, and that figure is not
comparable to the 8.6 s the cheap gate's entry records.)

Ground truth for the six, one `entities.py` run over all seven planted counts at once
(`logs/entities-all7.txt`): `BASELINE reds=29` → `PLANTED reds=29, NEW=0` — *no check name
moved; none of the planted counts is read*. On the same planted tree, the every-pull-request
gate answers `claims.py claims_false=0`, `doc_claims.py ALL 160 checks PASSED`,
`harness_headers.py ALL 109 HARNESS HEADER CHECKS PASSED` (`logs/hh-planted2.txt`).
**Four instruments, zero red, three sentences false.**

That run also corrected a measurement of the seat's own: an earlier pass reported four
instances as PROTECTED because `a8:register_once` prints a **set** whose order changes between
runs, and a detail-level diff read the re-order as a new red. Red is keyed on the check name.

Adjacent and larger, one instance probed: the **60 `steps` cells** in `configuration.md`'s
tables. C30/C31 (`claims.py:703-714`) compare Default and min/max; **nothing compares
`step`** — planting `0.5 steps` → `0.7 steps` left every instrument green.

## 4. Cost test, wall-clock both sides

| | number | instrument |
|---|---|---|
| `cost(defect)` per occurrence | **110.0 / 110.1 / 138.7 min** wall — the three resolution rounds of 2026-10-09 | `stat` mtimes, first to last artifact per evidence dir |
| exposure | 11 resolution merges and 8 pull-request merges to main that day; **24** resolution merges since 2026-10-01 carried a new production module across; 7 modules added since 10-01 | `git log --merges`, `--diff-filter=A` |
| `cost(countermeasure)` recurring | **10.8 ms** per `claims.py` run (a corpus regex scan over `README.md` + 12 docs); the standalone arm as a whole is 2.37 s against `claims.py`'s 2.30/2.54 s — indistinguishable, because the AST walk (412 ms) and the `config_flow` import (482 ms) are already paid by `claims.py:189` | `/usr/bin/time -p`, `/tmp/t-base*.txt` vs `/tmp/t-arm*.txt` |

135 pull-request merges since 2026-10-01 × 10.8 ms ≈ **1.5 s per cycle**, against roughly
**6.0 hours** (358.8 min) spent on three instances in one day. The test passes by three orders of
magnitude. P(recurrence) is measured, not guessed: 3 in one day, and the exposure event
recurs about 2.7 times a day.

## 5. Countermeasure

One census arm added to `tests/doc_claims.py` beside `check_multistart_starting_points`, in
that file's own idiom: count **shapes** (not sentences) enumerated over the reader corpus, each
compared to a **derived** measurement — the package glob this script already parses, an AST
walk of those same trees, `config_flow._OPTION_PAGES` with the pages the translation catalog
renders a field on, and `doc_claims.registered_service_fields()` for the service count and for
each named service's field count (never a second reading of `services.yaml`). A narrow shape
claims its span first, so `The other 46 modules` reads as the HA-free count and not also as a
module total, and `27 of the 75 modules` yields both the importer count and the total. Reuse,
no parallel instrument;
`tests/README.md:237` (*a test must never re-implement what it is testing*) is respected
because the arm re-uses the registered helpers rather than re-deriving the schema.

Prototype: `census_arm2.py` (ten shapes, `README.md` plus `docs/*.md`). Runs owed and taken:

- **Failing** (`logs/arm-final-planted.txt`): `26 options pages` planted in `setup.md:263` and
  `configuration.md:9` → `FALSE configuration.md:9 option_pages: documented=26 measured=23`,
  `FALSE setup.md:263 …`, `claims_false=2`, **rc=1** — on a tree where all four existing
  instruments are green.
- **Passing** (`logs/arm2-pass.txt`, `logs/census-corrected.txt`): the same three sentences
  corrected → `prose_counts_checked=16 shapes=10 docs=8 claims_false=0`, **rc=0**.
- **Null control** (`logs/census-null.txt`): `origin/main` tip untouched → rc=0 with
  `checked=16`, so it is not green by skipping.
- **Fail-closed** (`logs/arm-failclosed.txt`): removing `docs/setup.md` and
  `docs/configuration.md` → `REFUSED no occurrence of the option_pages shape`,
  `claims_false=2`, **rc=1** — the file's own anchor rule, inherited.
- **At the reproduction** (`logs/census-at-repro.txt`): rc=1 with three FALSE rows (75 against
  76 twice, 47 against 48).

What landed, and where it differs from the prototype: `check_prose_tree_counts` in
`tests/doc_claims.py`, eleven shapes over `CORPUS` — README.md, the user docs and the shipped
blueprints, with the record documents (`plan-*`, `audit-*`, `HANDOVER.md`, `backlog.md`)
excluded by the corpus the file already argues for — plus `tools/audit/prose_counts_census.py`,
which re-derives the class's seams from the corpus and refuses a noun with no disposition.
One of the prototype's ten shapes was dropped and two added (the `N modules, of which M
import` opening sentence, which the arm must read or the bare module shape would swallow its
total, and the `N service definitions` map comment), and the prototype's two `fields` shapes
became one keyed on the service the sentence names — an unregistered name is refused rather
than compared, because `All N fields` inside a service paragraph is already priced by
`check_service_fields` and a second, weaker reader of that sentence would be the worse code.
The four arms, each shown moving at the landed head, are in the pull request's body; the
printed counts are the arm's own and are not carried here.

Ratchet: `tests/structure.py` measures `PACKAGE_DIR` only (lines 206, 381), so test-script
lines are uncapped, and `tests/doc_claims.py` appears in no `policy_budgets.json` `files` or
`roles` entry — the arm costs no budget and does not raise the fixer role's cap. Note
`tests/entities.py` **is** inside the fixer role's `opens` (cap 5852), which is a further
reason the arm belongs in `doc_claims.py`.

Moratorium (decision 0012, `dev/governance/decisions/0012…:58-65`): this is not a new policy
file, not a `.claude/rules/*` rule and not a new lint class — it is one arm added to the
instrument that **already is** the I5 barrier, extending that barrier's **unit**.
`dev/governance/roles/root-cause.md` §2: *the countermeasure changes the unit, not the arm
count.* If a review reads it as a new lint class, the exception that applies is the
landed-barrier one, and the branch comes back to the owner rather than merging.

## 6. Class disposition, and what is deliberately not folded here

`dev/audit/config/bugclasses.json`: folded into `I5` — *Docs, comments or a compliance
checklist drift stale against the code* — already `barriered` by `tests/doc_claims.py`. The
fold appends this id to `I5.rca`, lists `#2024 #2065 #2066` as `non_round_instances` (per
`_counting`, incidents are listed, not counted), and extends `I5.barrier`'s *Not reached:*
clause with the honest new limit — prose counts in a document whose arm keys on a specific
sentence, plus the sixty `steps` cells, unread because C30/C31 compare only Default and
min/max.

**Not** the same class as `R9-RO-10` (stale retired *paths*, guarded by the layout guard and
rule-binding): its truth condition is *does this path exist*; a stale count's is *does this
number equal the tree's measurement*, which no path check can see. They share only the word
stale.
