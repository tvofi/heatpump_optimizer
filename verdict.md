Fix review: blocked 54fd5072b6b165c4bd3eab3900e5009332132d6a mutation-survivor: build_docs.mjs fragment-keeping redirect line survives deletion, doc_claims stays 411/411

bus-nonce: 931c11d4252bba20d2998a8c176df15f
pending-ci: gate

## Block

The body states that `tools/site/build_docs.mjs`'s new `MOVED` map "writes `ecl110.html` on the site as a redirect to `heat-curve.html` that keeps the fragment". The fragment is kept only by the redirect page's `<script>location.replace(${JSON.stringify(target)} + location.hash)</script>`: the `<meta http-equiv="refresh">` beside it drops the fragment. Deleting that script line (mutant m4, `ev/m4_mutant.diff`) leaves `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at `ALL 411 checks PASSED` rc 0 (`ev/doc_claims_m4-js-fragment-dropped.txt`). The `MOVED_PAGES` check tests only `url={to}"` in the page and the pointer link in the tree. So a link to an old deep anchor such as `ecl110.html#...` can silently land at the top of the new page, and nothing in the diff detects it. `prepr.sh`'s draw mutates only `.py` lines, so this `.mjs` site was never drawn. `fixer.md` step 2: "The diff's survivors are yours before the handoff". The body has no `## Unpinned sites` disposition for it.

Owed: a killing check, for example the same `MOVED_PAGES` check also requiring `location.hash` in the built redirect page, shown red under m4 and green at the head. The alternative is to drop "keeps the fragment" from the body and code. After that change, re-run steps 2–8 of `fixer.md`.

## Findings

none

## Evidence

- Round: first verdict on this PR. The packet's `## Review scope: full` holds because no verdict on `verdict/3663` names the reviewed head `c00ad6ba0a`, so the whole three-dot diff was reviewed at `54fd5072b6b165c4bd3eab3900e5009332132d6a` (`ev/HEAD.txt`).
- Mutation proof (step 1), `tests/doc_claims.py` at the head: baseline `ALL 411 checks PASSED`. m1 `MOVED = {}` gives `1 of 411 checks FAILED` (`site redirect to nothing`). m2 pointer page link changed to `other.md` gives 1 FAILED (`links docs/heat-curve.md: False`). m3 meta-refresh target changed to `index.html` gives 1 FAILED. m5 `MOVED` target changed to `docs/setup.md` gives 1 FAILED (`redirect to setup.html`). m6 `docs/ecl110.md` deleted gives 1 FAILED. m4 (the block) survives. The body's two named mutants reproduce exactly as stated. Logs: `ev/doc_claims_*.txt`.
- Production delta under `custom_components/` is `strings.json` and `translations/{en,de,sv}.json` only, with no `.py` line. Key sets are identical to the merge base `367c3b9cac` in all four files: no key added or removed, and no `{placeholder}` set changed. `strings.json == translations/en.json`. This supports the body's claim that no option key, entity id or translation key changes.
- Census (the fixer's instrument, not a finder's: an owner item, so no finder harness is named; sha1 `269ed873594fde8f91389eb4de9c306d4c4e32ca` matches the body). Re-run at `b3831ff64e`, at the merge base `367c3b9cac` and at the head, and every row of the body's table re-derives: total 632/632/560, ECL110 115→33, Danfoss 16→20, Luxtronik 72→75, SHI 22→25, everything else flat (`ev/census_*.txt`). Null control: ` Thermia` appended to README line 64 prints `Thermia 1`, `total 561`; restored prints `total 560` (`ev/null_control_thermia.txt`). The class rule is the census over the whole user-facing surface. I spot-checked the remaining ECL110/Danfoss head hits against the body's dispositions (example, attribution, old address, `ecl110_*` identifier view) and found no hit outside them.
- README limitation "an entity whose range excludes 0 is refused as an offset" matches `custom_components/heatpump_optimizer/heat_curve.py:299-322` (`range_excludes_zero`).
- No `custom_components/` code links to `docs/ecl110.md`. Remaining in-tree references are history (`RELEASE_NOTES.md`, archives, rosters) and the closure lists.
- `python3 -I tools/audit/check_scopes.py --self-test --repo .` at the head prints `SELF-TEST passed (every perturbed scope refused)` rc 0, and plain `--repo .` prints `ok coverage ... unclassified=0` (`ev/check_scopes_selftest_head.txt`). This is the body's repair of the `governance / instrument-self-tests` red at `c00ad6ba0a`. That check is not in the `merge_train.py owed-reds` set, and the body answers it anyway.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (`ev/structure_head.txt`). `tests/env_drift.py --claims-only 367c3b9cac...` prints `claims hygiene: ... ok`. The diff touches no golden, claim file, budget file or mutation ledger.
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched against the merge base (step 5).
- `git merge-tree --write-tree origin/main 54fd5072b6` (origin/main `6f422812d5`) exits rc 0 with `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`). No conflict.
- The body's `## Head` names `54fd5072b6b165c4bd3eab3900e5009332132d6a`, which is the head measured (step 7).
- CI at this head: `merge_train.py classify 54fd5072b6... --pr 3663` printed `WAIT 54fd5072b6b165c4bd3eab3900e5009332132d6a pending: gate red: none` on every poll from 16:30 UTC until 17:00:29 UTC, about 30 minutes; the head was still `54fd5072b6` at the remote then. The packet's `introduced-red` refusal is "unreadable: instrument-self-tests queued". The block above does not depend on CI.
