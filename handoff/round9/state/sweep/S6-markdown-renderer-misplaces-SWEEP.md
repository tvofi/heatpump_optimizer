# Class sweep — "markdown the renderer misplaces"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D5-s1-04** (verified, low — `configuration.md:181-187` a paragraph inserted
inside the "4 · Hot water" table orphans its last three rows into raw-pipe paragraph text (GFM:
a table ends only at a blank line or another block); `configuration.md:633-638` prose directly
under the "Heating system" table with no blank line is swallowed into six table rows).

## Enumerator

`tools/audit/round9/D14/sweep/markdown-renderer-misplaces/enumerate.sh` reuses the finder's own
harness verbatim (`tools/audit/round9/D5/s1/md_tables.mjs`), which already runs the actual
`markdown-it@14.1.0` (GFM) token stream over all 8 user docs (`README.md` +
`docs/{architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md`) —
it IS the class enumerator, not merely the finder's own positive control.

Positive control: re-running it reproduces `misrendered_lines=9` (`swallowed_prose_lines=6`,
`orphaned_table_rows=3`), both groups at exactly the finding's own line numbers.
Null control: `files_checked=8` with 0 misrendered lines outside `configuration.md` — every other
doc's tables render intact.
Perturbation: `--perturb` (a blank line before every swallowed line, and every orphaning
paragraph moved below its table) drops `misrendered_lines` to 0 — documented in the harness
header, the judge's own perturbation.

## Disposition

| seam | disposition | note |
|---|---|---|
| `configuration.md:181-187` (anti-legionella rows orphaned) | **instance** | D5-s1-04 itself. |
| `configuration.md:633-638` (fuel-price prose swallowed into the Heating system table) | **instance** | D5-s1-04 itself. |
| Every other table across the 8 scanned docs (`README.md`, `architecture.md`, `automations.md`, `dashboard-card.md`, `ecl110.md`, `how-it-works.md`, `setup.md`, and the rest of `configuration.md`) | **guarded** | `files_checked=8`, `misrendered_lines=9` — the enumerator confirms no misrendered table exists outside the two named spots. |

## Count

N = 1 verified finding (D5-s1-04, covering both spots as one mechanism — a doc paragraph placed
without the blank line GFM tables require) + 0 additional sweep-confirmed instances (the full
8-file scan found nothing else). **rca = false** (N=1 < 3, not a ledger class, not barriered).

## Barrier proposal

Add `md_tables.mjs`'s check (`misrendered_lines == 0` across the doc set) as a CI step gating doc
changes — cheap (one `markdown-it` parse of 8 files, well under 1s) and directly prevents this
class from recurring on future doc edits. Estimated gate cost: under 1s plus a one-time `npm
install` (or vendor `markdown-it` to avoid the install in CI).
