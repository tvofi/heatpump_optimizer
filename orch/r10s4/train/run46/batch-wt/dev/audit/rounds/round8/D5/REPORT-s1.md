# D5 seat s1 report — docs structure, reader paths, mechanism spot-checks

Baseline: `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree:
`/home/claude/audit-r8/seats/D5-s1` (export copy, no `.git`).

## Method

Followed D5.md method steps 1-3 (this seat's assigned scope; step 4, code
comments, is seat s2's).

1. **Reader paths.** Walked the new-user HACS-install-to-first-plan path
   (README "Installation" through "Quick start" through "Your first week"),
   the feature-configuration path (ECL110, hydronic-layout catalog, capacity
   tariff / grid-fee settings in `docs/configuration.md`), and confirmed the
   developer/test path only has the one entry point (`tests/README.md`,
   linked from README's Documentation table — not separately deep-audited,
   see Unfinished).
2. **Structure.** Wrote `s1_linkcheck.py` (every internal link/anchor in
   README.md and 9 reader-facing docs, GitHub-slug-accurate anchor matching)
   and `s1_dupcheck.py` (5-word-shingle Jaccard paragraph duplication between
   README and docs/*.md). Also ran an ad hoc heading-depth-jump scan (no
   harness committed for this one since it found nothing and needed no
   perturbation design — see non_findings).
3. **Content.** Spot-checked mechanism paragraphs against code for
   `docs/ecl110.md` in full (activation threshold, curve-learning cap,
   weather-anticipation window, first-order-lag smoothing, option count) and
   the hydronic-layout-catalog section of `docs/configuration.md` against
   `ThermalModelParams.topology_layout` in `thermal_model.py`. Also checked
   two numeric claims in README (sensor count, service count, storage-file
   count) against the code that produces them.

## Findings

**D5-s1-01** (low, hygiene): README's "Quick start" flowchart and the prose
paragraphs beneath it use two different numbering tracks for the same four
screens (Temperatures, Hot water, Weather sensitivity, and the building-
description branch), because the prose spends a number on the unnumbered
"finish menu" decision node in the diagram. A new user matching a prose
step number ("4 · Temperatures") back to the diagram to see where they are
lands on the wrong node. Harness: `s1_stepnum.py`, `RESULT
mismatched_labels=3`, drops to 0 under a `--fix` perturbation that renumbers
the prose to match the diagram. See `report-s1.json` for full evidence.

## Non-findings

See `report-s1.json`'s `non_findings` array for the full list with commands
and values. In summary, everything else checked held:

- 0 broken internal links/anchors across README.md and 9 reader-facing docs
  pages (after excluding the three deliberately-stripped export files named
  in `COMMON.md`/`BASELINE.md`: `docs/audit-2026-08.md`,
  `docs/audit-2026-09.md`, `docs/backlog.md` — these are **not** findings,
  they are the known preparation artefact).
- 0 near-duplicate paragraphs (README vs docs/*.md).
- README's numeric claims that were spot-checked against code all matched
  exactly: "Sensors (59 total)" (59), "12 services are registered" (12),
  "twelve files under `.storage/`" (12 `QuarantiningStore(...)`
  constructions).
- `docs/ecl110.md`'s every checked mechanism paragraph (activation
  threshold, curve-learning weekly cap and cool-only direction, 8-hour
  weather-anticipation window, first-order-lag smoothing, all eight ECL110
  option defaults and ranges) matched `optimizer.py`, `curve_learning.py`
  and `const.py` exactly.
- `docs/configuration.md`'s hydronic-layout-catalog derivation rule matched
  `ThermalModelParams.topology_layout` in `thermal_model.py` exactly,
  including the claim that `valve_upper_direct_slab` is reachable only
  through the layout-editor override and never derived.
- No heading-depth jump (e.g. H1 straight to H3) in README.md or any
  reader-facing docs/*.md file.

This dimension, in the scope this seat covered, is unusually clean: the
documentation's mechanism paragraphs and structural numbers all matched the
code. The one real finding is a pure navigation/numbering inconsistency, not
a factual error.

## Harnesses

- `tools/audit/round8/D5/s1_linkcheck.py` — internal link/anchor checker.
- `tools/audit/round8/D5/s1_dupcheck.py` — README/docs paragraph near-
  duplication (Jaccard shingle similarity).
- `tools/audit/round8/D5/s1_stepnum.py` — Quick-start diagram-vs-prose step
  numbering consistency (D5-s1-01's harness).

All three: run from the tree root with
`PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D5/<name>.py`.
Each restores any production file it mutates in a `finally` block (verified:
`diff README.md /home/claude/audit-r8/export/README.md` and the same for
`docs/architecture.md` are empty after every run, including the
perturbation runs).

## Exposure

Read `docs/*.md` and README.md, as the brief requires, and
`docs/plan-2026-09-open-issues.md` in passing while scanning for orphaned
documents (that file cites many past PR/issue numbers as historical
record — a leftover-row ledger, not used to steer any check here). No
GitHub access, no `docs/audit-*.md`, no `docs/backlog.md` present in this
export (see non-findings above for how that was handled).

## Unfinished (within the ~90-minute budget)

- Did not exhaustively spot-check `docs/dashboard-card.md` or
  `docs/automations.md` mechanism paragraphs against `card.mjs`/the
  automation-relevant entity/service code — only README, `docs/ecl110.md`
  and the hydronic-layout section of `docs/configuration.md` were spot-
  checked, chosen because the D5 brief names ECL110 and two-tank/capacity-
  tariff-adjacent configuration explicitly as the feature-configuration
  reader path to walk.
- Did not sweep `docs/decisions/`, `docs/delivery/`, `docs/superpowers/` or
  `docs/plan-*.md` for orphans/duplication — judged process record, not the
  reader-facing "docs structure, flow and content" this seat's method steps
  1-3 are about; flagging this choice per `finding-propagation.md` in case
  a later seat's brief expects otherwise.
- Did not fetch external (http/https) links to verify reachability.
