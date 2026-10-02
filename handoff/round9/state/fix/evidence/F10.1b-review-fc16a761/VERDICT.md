# merge fc16a7619ffac4cc122738499cb4b875ea791ea2

Fix review, PR #1800 (R9-F10.1b), round 2 (delta). Measured head fc16a761 = closures-autofix commit (tests/closures.json only) on 990bd22b = code 3db3eecf + origin/main 0ba354c5 merged + delivery row. Round 1 prep at code head ed71569a, evidence dir F10.1b-review-ed71569a.

Round 1 finding (blocking), now closed: the stub Store modelled only half of upstream's version handling (no downgrade refusal, no save-back after migration) and its contract overclaimed. 3db3eecf adds UnsupportedStorageVersionError(HomeAssistantError) raised before any migration when stored > code version, `await self.async_save(result)` after a migration, INVENTORY text for both, a 5-arm Store contract and P11 block arms.

RESULT lines (reviewer's runs, 990bd22b; fc16a761 differs only in tests/closures.json):
- RESULT ha_contract real HA 2026.9.3 (Python 3.14.7) --contracts-only: ALL 59 contracts PASSED (round 1: 59/59 at base 5dfa6684 and at ed71569a)
- RESULT ha_contract stub: ALL 92 contracts PASSED
- RESULT upstream UnsupportedStorageVersionError at 2026.9.3: subclass of HomeAssistantError True, __init__(storage_key, found_version, max_supported_version), same as the stub
- RESULT upstream Store._async_load_data at 2026.9.3 (round 1 dump ha_upstream_src_2026.9.3.txt): `version > _max_readable_version` raises before migration; `async_save(stored)` after migration; the stub now matches both
- RESULT P11 block (features.py cut at the block): 121 ok, 0 FAIL
- RESULT probe_store_version.py (reviewer's own instrument, not the finder's): downgrade 2->1 no-migrate UnsupportedStorageVersionError; downgrade 2->1 migrating Store UnsupportedStorageVersionError; bump 1->2 migrate loaded twice: save count 2, stored version 2 (upstream behaviour)
- RESULT mutant M6 drop downgrade guard: block 1 FAIL, contract 1 of 92 FAILED (killed; it survived at ed71569a)
- RESULT mutant M7 drop save-back: block 1 FAIL, contract 1 of 92 FAILED (killed)
- RESULT mutant M3 drop version save: block 3 FAIL, contract 1 of 92 FAILED (killed)
- Round 1 (ed71569a), not re-run: M1/M2/M4/M5 killed; finder's harness stub_naive_clock.py (sha1 f73db7cb9d35) via the P11 enumerator divergent=6 of_6 at base, 0 of_6 at head; typing_ruler --mypy with the pinned lock ALL 9 PASSED at both ends. The Store-decode seam figure in the body (0 of 6 at both ends) was not re-derived: its harness imports _rig, absent from this tree.

CI cited, not re-run (fix-review step 11): every check run on fc16a761 is success or skipped, among them fast (3.14), closures, coverage, mutation, typing, briefs, policy-docs, env-matrix, pr-contract, budget-raise-gate, delivery-status, nightly-status, hassfest, validate-hacs, CodeQL, and nightly-ha (2025.2.0) and nightly-ha (stable) in the dispatched Tests run. The stress line inside fast was not read separately; fast's conclusion is success, so the fixer's local stress.py CPU red (287x against 268x) did not recur there. mutation's green is not mutant evidence: the diff writes no production line.

Red checks (step 11): closures went red at 990bd22b, UNDER-SCOPED (tests/guard_pins.py now reads tests/hastub/homeassistant/exceptions.py via the new import in helpers/storage.py); answered by closures-autofix commit fc16a761 and named in the body (ci-autofix.md). No other red on any head of this PR that I read.

Other steps: VERSION, manifest version, RELEASE_NOTES heading, claim files and every *_budgets.json untouched (three-dot against origin/main); no budget raise; structure.py STRUCTURE RATCHET PASSED (round 1). git merge-tree --write-tree origin/main(0ba354c5) fc16a761: exit 0. Head contains current main 0ba354c5. Forward-carry: carry-1649.json entry present and updated for the Store semantics (EG-B4). No structure concern: 0 production lines; the changes are stub, contracts, fixtures, carry.
