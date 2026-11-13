# r10-legacy-control-survey RESULT

Trees: assigned head 4aa98689469d61e57189549c9770f2688d87d4cf; fresh origin/main c7f2fe4270a9f106c640fb1258123034f9046c21. `git diff 4aa9868 c7f2fe4 -- tools/policy dev/programme/carries dev/archive/carries` is empty, and the data file md5 is identical, so the survey holds at both. Read-only: no tracked file changed, no PR.

## 1. The list
Lives in `tools/policy/legacy_control_files.json` (key `files`), read by `readLegacyControlFiles()` in `brief_lint.mjs` (cap literal `LEGACY_CONTROL_CAP` = 14, line 965).
Count by rule: `python3 -c "import json;print(len(json.load(open('tools/policy/legacy_control_files.json'))['files']))"` prints **13** (cap 14).
Members: carry-1067, 1336, 1395, 1398, 1454, 1459, 1463, 1644, 1645, 1659, 1660, 201, 752 (1644 etc. under dev/archive/carries; 1645 and 201 under dev/programme/carries).

## 2. Method
Each member linted with `lintCarryFile(f,{roster:new Map(),legacy:new Set()})`, control errors listed by kind. For every `path:line` in a control the linter's anchor candidates are rebuilt exactly as `checkPathLine` does: clause window of 220 chars around the cite; candidates are quoted phrases, keyword anchors (return, raise, ...) and snake/SCREAM symbols; the cite passes if ANY candidate is in the cited line +-1 (range: as given) or in its enclosing def chain. Neighbours = other lines holding a candidate within +-40 of the cited range. Script: scratchpad survey.mjs (not committed).

Strict rule from the brief: AT RISK = the control's only error is a stale citation AND another anchor line lies within +-40, or it lints clean while listed. Supplement I add after the null control (section 4): also report nearest-other-line distance and file-wide count.

## 3. Table
Only 3 of 13 members have any `path:line` in a control; the other 10 have none, so they cannot go vacuous by drift. No member lints clean today.

| file | control | anchor(s) | cited line state | neighbours with anchor (+-40) / file total | AT RISK | why |
|---|---|---|---|---|---|---|
| carry-1067 | 0, 1 | - | no path:line; errors: no-path (c0), unresolved `lift_consistency.py` (c1) | n/a | no | no citation |
| carry-1336 | 0 | - | no path:line; no-path | n/a | no | no citation |
| carry-1395 | 0 | - | no path:line; no-path | n/a | no | no citation |
| carry-1398 | 0 | - | no path:line; unresolved symbol `no_dhw_gate_counts` + no-path | n/a | no | no citation |
| carry-1454 | 0 | - | no path:line; no-path | n/a | no | no citation |
| carry-1459 | 0 | - | no path:line; no-path | n/a | no | no citation |
| carry-1463 | 0 | - | no path:line; unresolved `polish_cost.py` | n/a | no | no citation |
| carry-1644 | 2 | `owner_missing` (snake identifier) | `coordinator.py:10010` stale; symbol absent from the whole file (11465 lines) | 0 / 0 | no | only error is the stale cite (member would lint clean if it were fixed), but the anchor occurs nowhere, so no unrelated line can drift in. Residual: a future `owner_missing` landing at 10009-10011 |
| carry-1645 | 0 | `_mutated_span` (private identifier, 2 occurrences) | `tests/doc_claims.py:612` stale; anchor at 616 and 622 | 2 / 2 (nearest 4 lines away) | **yes (control-level)** | this control errors only on a stale cite and the anchor is 4 lines off: a 3-line drift of doc_claims.py makes it lint clean. Same control's other cites pass: `:605-619` matches via enclosing def `check_simulate_plan_fields`, `:487` via `check_initial_setup_menu`. Member-level the file stays red today because carry 1 has an independent no-path error, so the VACUOUS refusal does not trip yet; it trips the day carry 1 is repaired or if carry 0 is the last remaining error |
| carry-1645 | 1 | - | no path:line; no-path | n/a | no | no citation |
| carry-1659 | 0,1 | - | no path:line; no-path | n/a | no | no citation |
| carry-1660 | 0,1 | - | no path:line; unresolved `repro_loaders.py` x2 | n/a | no | no citation |
| carry-201 | 2 | `policy_lint` | `CLAUDE.md:20` stale; anchor absent from CLAUDE.md (215 lines) | 0 / 0 | no | stale-only control but no occurrence of the anchor; member pinned red by 9 other no-path controls |
| carry-201 | 4,9-15,23 | - | no path:line; no-path | n/a | no | no citation |
| carry-752 | 0 | - | no path:line; no-path | n/a | no | no citation |

No bare `:N` forms in any member control were found by the class-2b pattern.

## 4. Null control
Pre-repair carry-1412: `git show d65839f2e2^:dev/archive/carries/carry-1412.json` (d65839f2e2 is the re-anchor commit; the list before it also held carry-1412). Linted with the exemption off at 4aa9868 its only control error is `path:line optimizer.py:4671: 'p_max' not found near ...:4671; found at line 32 instead`; anchor `p_max` (a bare identifier, 81 occurrences in a 6138-line file). Cited text `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))` no longer exists in the file.

| row | shape | strict +-40 | supplement (nearest <=100 or >=10 file-wide hits on a bare identifier) | call |
|---|---|---|---|---|
| carry-1412 pre-repair | stale-only, anchor `p_max` | 0 neighbours at today's tree (nearest p_max lines 4626 and 4766, 45 and 95 away) -> strict rule alone says NOT at risk | yes: common identifier, 81 hits, nearest 45 away | **AT RISK** (via supplement only) |
| synthetic member control: `optimizer.py:4607 "where the tank clamp refused heat" ...` (phrase is unique, on line 4612 only; same text at :4612 passes) | stale-only, unique quoted phrase | 0 other lines hold the phrase | no: only one occurrence, which is the real site; the cite can turn clean only when it points at that site, a true repair | **NOT at risk** |

Finding to read honestly: the strict +-40 rule FAILS the first null at today's tree. The incident is real, and I reproduced it from history: `git show <c>:custom_components/heatpump_optimizer/optimizer.py` has p_max on line 4670/4671 at commits 3ed99bc468 (Nov 5), 2580a8b638 and 0714908e3b (Nov 4), so the pre-repair control lints clean at those bases and trips LEGACY-LISTED-CLEAN, while at 4aa9868 and its parent it is 45 lines off. A hot file moves tens of lines between merges, so +-40 is too tight; recommend the supplement (nearest-line distance up to about 100, or a bare identifier with many file-wide hits). Applied to the members, the supplement changes no call: 1644 and 201 have zero occurrences, 1645 already trips the strict rule.

## 5. Repair for each AT RISK member (described, not applied; shape of #3552)
carry-1645 control 0 only: replace the line numbers of the `tests/doc_claims.py:612` citation with a phrase anchor, i.e. name `tests/doc_claims.py` and the symbol `_mutated_span` (or the function holding it) without a line number, as 3552 did for carry-1412 (`dhw_planner.py`, no number). Data-only: one string in `dev/programme/carries/carry-1645.json`. Do NOT delist: carry 1 still has the no-path error, so removing the file from `tools/policy/legacy_control_files.json` would turn `tests / briefs` red until carry 1 also names a path. Delist only in a second step once carry 1 names an existing harness path. Optional hardening for carry-1644 and carry-201: same re-anchor (drop `:10010`, `:20`), also data-only, though neither is at risk.

## 6. Linter run
`node tools/policy/brief_lint.mjs` at 4aa9868, exit 0: `TOTAL: 0 error(s) across 45 file(s)` (line 144; line 142 `CARRY: 44 carry file(s)`); last section lines `LEGACY-CONTROL ok: ... the legacy set is within its cap and each member still needs the exemption` and `LEGACY-LISTED-CLEAN ok: ...`. The fixture sections print deliberate errors (e.g. `8 error(s)`), not tree findings.
