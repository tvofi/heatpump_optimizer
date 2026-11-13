# r10-legacy-control-survey: RESULT

Survey at origin/main `c7f2fe4270a9f106c640fb1258123034f9046c21` (the dispatch head 4aa98689 is an ancestor; the list is unchanged in kind). Read-only: no tracked file changed; a temporary untracked probe copy of `brief_lint.mjs` (one added export line) and a scratch worktree were used and removed.

## 1. The list

- Lives in `tools/policy/legacy_control_files.json` (`files`), read by `readLegacyControlFiles()` in `tools/policy/brief_lint.mjs`; cap `LEGACY_CONTROL_CAP = 14` is a literal in the grader.
- Count by rule: `python3 -c "import json;print(len(json.load(open('tools/policy/legacy_control_files.json'))['files']))"` prints **13** (cap 14; carry-1412 already delisted by #3552 data PR d65839f2e2).
- Members: carry-1067, 1336, 1395, 1398, 1454, 1459, 1463, 1644, 1645, 1659, 1660, 201, 752 (`.json`), under `dev/archive/carries` except 1645 and 201 (`dev/programme/carries`).
- Method: each member linted with `lintCarryFile(f, {roster: new Map(), legacy: new Set()})`, control errors listed by kind; every `path:line` in every control re-run through the linter's own `clauseWindow` -> `anchorCandidatesFor` -> `checkPathLine` (anchor candidates = quoted phrases (>=4 chars), keywords `return/raise/...`, snake_case/SCREAM symbols from the +-220-char clause around the cite; ANY candidate found in the cited line +-1 (single line) or the exact range, or in its enclosing scope, makes the cite pass). Neighbours counted +-40 lines of the cited range, plus total occurrences and nearest distance.

## 2. Table (one row per member)

Control-error kinds with legacy off. "Sole error" = the only control error is a stale `path:line`.

| file | control | anchor (linter-extracted) | cited line state at main | other lines with anchor within +-40 | AT RISK | why |
|---|---|---|---|---|---|---|
| carry-1067 | 0, 1 | none (no `path:line`) | no citation | n/a | no | errors: no-path (c0), unresolvable path `lift_consistency.py` (c1); no path:line to drift |
| carry-1336 | 0 | none | no citation | n/a | no | no-path error only |
| carry-1395 | 0 | none | no citation | n/a | no | no-path error only |
| carry-1398 | 0 | none | no citation | n/a | no | unresolved symbol `no_dhw_gate_counts` + no-path |
| carry-1454 | 0 | none | no citation | n/a | no | no-path error only |
| carry-1459 | 0 | none | no citation | n/a | no | no-path error only |
| carry-1463 | 0 | none | no citation | n/a | no | unresolvable path `polish_cost.py` |
| carry-1644 | 2 | `owner_missing` (snake_case symbol, the only candidate) | `coordinator.py:10010` (file has 11463 lines): STALE, anchor absent from the file | 0 (0 occurrences in the whole file and in the tracked tree outside this carry) | no | it IS a sole-stale-citation file (the one at-risk shape), but the anchor is a prototype-lint counter name that is not in coordinator.py at all, so no drift can bring it into the +-1 window short of someone adding that identifier there. Latent, not at risk |
| carry-1645 | 0 | `_mutated_span` (symbol) at `tests/doc_claims.py:612` | STALE: anchor at 616 and 622 (4 and 10 lines away) | 2 (nearest 4) | no (shielded) | the citation is fragile (a 3-5 line shift of tests/doc_claims.py makes it clean), but control 1 still has a no-path error, so the file cannot lint clean and `assertLegacyControl` cannot go VACUOUS while that stands. Watch: if control 1 is ever repaired alone, this becomes at-risk. The other two cites pass today: `doc_claims.py:605-619` (matched `check_simulate_plan_fields` by enclosing scope, defined at 570) and `doc_claims.py:487` (matched `check_initial_setup_menu` by scope; also `## Initial setup` 3 times, 1 near, at 490) |
| carry-1659 | 0 | none | no citation | n/a | no | no-path error only |
| carry-1660 | 0, 1 | none | no citation | n/a | no | unresolvable path `repro_loaders.py` x2 |
| carry-201 | 2 | `policy_lint` (symbol) at `CLAUDE.md:20` | STALE, anchor absent from CLAUDE.md (214 lines) | 0 | no | plus nine no-path errors (controls 4, 9-15, 23): cannot lint clean |
| carry-752 | 0 | none | no citation | n/a | no | no-path error only |

Listed-but-clean members: **none** (every one has at least one control error). AT RISK members under the brief's rule (sole stale citation AND >=1 anchor line within +-40, or listed and clean): **none**.

Only three members carry a `path:line` in a control at all (1644, 1645, 201); the other ten fail on missing/unresolvable paths, which line drift cannot change.

## 3. Null control, with an honest failure of the +-40 rule

Pre-repair carry-1412: the control re-anchored by 87eb346e08 (PR 3525; parent caacd43b4e, data delist d65839f2e2 = 3552). Before repair, its only control error was `optimizer.py:4671` with anchor candidate `p_max` (from `` `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))` ``). Reconstructed at caacd43b4e and again with the identical text at origin/main (`optimizer.py` is unchanged between them):

| shape | sole stale error | anchor | occurrences in file | nearest occurrence | within +-40 | classifier call |
|---|---|---|---|---|---|---|
| carry-1412 pre-repair (`optimizer.py:4671`, `p_max`) | yes (`'p_max' not found near ...:4671; found at line 32 instead`) | `p_max`, a short common identifier | 81 | 45 lines (4626) | 0 | **+-40 rule: NOT at risk (miss by 5 lines).** Widened rule (below): AT RISK |
| synthetic: same cite with the unique quoted phrase `"future_solar_6_12h / max(typical_heat_loss"` (the phrase the repair used) | yes | the phrase; 1 occurrence | 1 | 1015 lines | 0 | NOT at risk under both rules |

The brief's +-40 rule therefore does not call the known-bad shape at risk: the 1412 incident needed only a ~44-line shift of `optimizer.py` (any open PR adding that much above line 4671), and with 81 `p_max` lines in an 11k-line file, one lands in the +-1 window after a shift of a few dozen lines. A fixed +-40 radius is the wrong instrument; the discriminator that separates the two rows is anchor commonness. **Widened rule used for the verdicts above:** AT RISK when the control's only errors are stale `path:line` AND (the anchor has >=1 occurrence within +-40 OR >= 10 occurrences in the file), or when listed and clean. Re-applying that rule to the 13 members changes no verdict: 1644 (0 occurrences) and 201 (0, and shielded) are not at risk; 1645 is shielded by its second error and its anchor has only 2 occurrences. So the answer is robust to the radius, and the null control is called correctly only by the widened rule; the +-40 rule as specified is recorded as failing its own null control.

## 4. Repairs for AT RISK members

None are at risk, so no 3552-shaped repair is owed. For the two latent cases, described, not applied:

- carry-1644 control 2 (the only member one repair from lint-clean, and so the one that would then be refused by `staleLegacyMembers` as listed-but-clean): re-anchor by phrase: replace `the one stray being coordinator.py:10010` with `the one stray being coordinator.py, found by the phrase "on/off convention"` (a phrase the carry's own remeasure line already greps for), and delist `carry-1644.json` from `tools/policy/legacy_control_files.json` in the same data-only PR (cap 14 unchanged; set becomes 12). Do both in one PR or the base-vs-head lint reddens (`LEGACY-CONTROL VACUOUS: listed carry lints clean`).
- carry-1645 control 0: replace `tests/doc_claims.py:612` by the phrase-anchored form (`tests/doc_claims.py, the `_mutated_span` assignment`) only together with a repair of control 1's missing path, then delist; repairing control 0 alone changes nothing the lint can see and repairing control 1 alone leaves a drifting cite.

## 5. brief_lint summary

`node tools/policy/brief_lint.mjs` at origin/main c7f2fe4270 (73 s wall): the legacy lines read `LEGACY-CONTROL ok: ... the legacy set is within its cap and each member still needs the exemption` and `LEGACY-LISTED-CLEAN ok: a listed carry that lints clean is refused, one that needs the exemption is not, and the vacuous check is told apart`. Overall summary line: `TOTAL: 0 error(s) across 45 file(s)` (`CARRY: 44 carry file(s)`); no VACUOUS line; the only non-zero sections are the intentional negative fixtures under tools/policy/fixtures/ (carry-990002/3/4 etc.); the only non-fixture warnings are one each in carry-1922 and carry-2075.
