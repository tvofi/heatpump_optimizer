Fix review: merge b46f8832d5ea31651ef66294f8d0263c6c3b8732

bus-nonce: b9f1481c8cc8067c4a37d56bdad24b6c

## Round

Round 2. I measured head b46f8832d5ea31651ef66294f8d0263c6c3b8732 from detached worktrees at that SHA. Round 1 blocked 822946aae49ec0cec8e9a9d1812334dae14aee04 as `class-open` (verdict/3062 at 68c79cae3). `review_carry.py 822946aae b46f8832d` prints `FRESH-REVIEW`: the branch-only commits are ea1cb7a80 (tests) and 415a27e1b (fix), and the rest are main merges. The merge base is c3b7c964f, which is origin/main. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role files are current.

## Findings

- Carry 22 (two-zone `house_heat_loss_coefficient`) stays open. Its forward-carry, that the sysid sizer `HousePlant.of_params` should read the zone loss before the field is hidden, still has no owning group. The body keeps it on this group's list. That is a pending route, not a control. Carry: R10-UX-HEALTH
- Carries 14 (the "driving scale") and 17 (the P9 storage reset) are untouched by this part and still wait on orchestrator decisions. Carry: R10-UX-HEALTH
- The history-phrasing copies under `docs/` are not changed by this diff: `configuration.md` "exactly as before" ×2 and "does, as before", `dashboard-card.md` "exactly as before", and `how-it-works.md` "as before" and "exactly as before v5.3.0". The body routes them to R10-USER-DOCS-VERIFY, and that group resolves on the roster ref (packet carry_audit). Round 1 had named R10-USER-DOCS-FINAL for this item. Carry: R10-USER-DOCS-VERIFY

## Evidence

- HEAD: `ev/HEAD.txt` holds b46f8832d5ea31651ef66294f8d0263c6c3b8732. It matches the PR's live head (the `pull_request_read` head.sha) and the first SHA under the body's `## Head`.
- Merge: `git merge-tree --write-tree origin/main b46f8832d` (origin/main c3b7c964f) exits 0, with tree bddb47ef6 (`ev/merge_tree.txt`). No conflict, so no claim driver ran.
- Three-dot diff against c3b7c964f: 9 files. strings.json, en.json and sv.json have 14 lines each. Then the card JS (9), `r10_two_zone_hhl_inert.py` (99), delivery/3062.md (1), card.mjs (19), closures.json (1) and entities.py (39).
- Item 1, the leaf: `peak_tariff_offpeak_factor` now reads "1.0 treats every hour the same." in strings.json and en.json, and "1,0 behandlar varje timme lika." in sv.json. The fixer's own sibling `two_zone_mode` ("keeps the old rule" / "behåller den gamla regeln") is rewritten in all three. Both rewrites state current behaviour.
- Item 1, the widened net (`ev/net.py`: en `worked before|\bbefore\.`, sv `tidigare|fungerade tidigare|som förut`, over every string leaf):
  - At the round-1 head 822946aae: strings 1, en 1, sv 3 (`ev/net_round1.txt`).
  - At this head: strings 0, en 0, sv 2 (`ev/net_head.txt`). The two sv hits are `heat_pump_dhw_booster_entity` "något tidigare" and `dhw_elastic_legionella_enabled` "en dag eller två tidigare". Both are time adverbs ("a little earlier") and describe current behaviour, as round 1 judged.
  - The only catalogues are strings.json and translations/{en,sv}.json. The card JS's "as before", "was before" and "before." hits are all code comments, not UI text.
  - The one sv `den gamla` hit left is "den gamla valutan", a currency the user changed. That is a runtime state.
  - The net returns no further hit, so the class is closed at this head.
- Item 2, the check fails first on the leaf. I planted the old wording back in all three catalogues (`ev/plant_leaf.diff`) and ran `tests/entities.py`. It prints `FAIL strings.json|en.json|sv.json: no UI text describes how the integration used to behave [1: options.step.grid.data_description.peak_tariff_offpeak_factor]`, one per file, and `3 of 2500 ENTITY CHECKS FAILED`, rc=1 (`ev/entities_planted.txt`).
- Item 2, the null: the clean head prints all three history checks ok and `ALL 2500 ENTITY CHECKS PASSED`, rc=0 (`ev/entities_head.txt`). The FAIL lines in that log are the self-tests' own negative controls.
- I ran the head's `_HISTORY_MARKERS` directly on chosen phrases (`ev/markers_probe.txt`):
  - They hit "keeps the old rule", "behåller den gamla regeln", "how it worked before" and "som det fungerade tidigare".
  - They miss "något tidigare", "den gamla valutan", "förutse", "Used to read your hourly electricity prices" and "before each deadline". So the new bare `förut` and `numera` do not catch `förutse`, and current-behaviour text stays out.
- Round-1 finding 1, the unmetered unconverged bar, is now pinned. I applied round 1's narrower mutant `hl.learned ? (observable ? 1 : 0) : house ? house.share : 0` at card JS line 9673 (`ev/card_mutant_narrow.diff`). `node tests/card.mjs` (after `tests/plan_view.py`, rc=0) then prints `FAIL UX-HEALTH D: with no power meter a still-learning heat loss draws no learned bar either (#2499)` and `1 CARD CHECK(S) FAILED`. Both metered nulls and the converged check stay ok (`ev/card_mutant_narrow.txt`). The restored head prints `ALL CARD CHECKS PASSED` (`ev/card_head.txt`). The body now states the unconverged arm as intended.
- Round-1 evidence at the new head: the card JS is unchanged since round 1 (the round-2 commits touch only the catalogues and tests). The carry 22 harness prints exactly round 1's figures (`ev/carry22_harness.txt`): two_zone_max_dkw=0.000000, two_zone_max_dcost=0.000000, single_zone_max_dkw=4.921374, two_zone_sysid_steps=1.738,3.386,None and single_zone_sysid_steps=1.738,3.386,None. The body's 4.999993 is a macOS figure. I could not re-derive it on Linux, and only its non-zero sign matters.
- Standing items:
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (`ev/structure.txt`).
  - Scoped gate: `tests/closure.py select` prints `MODE: SCOPED -- 12 script(s) run, 21 scoped out.`, matching the body (`ev/scoped_select.txt`).
  - Claim files, VERSION, RELEASE_NOTES.md and manifest.json: the three-dot diff is empty for each.
  - The delivery row `dev/programme/delivery/3062.md` is present and shows open, R10-UX-HEALTH.
- Body figures I did not re-derive: the census counts 87/87/35 → 79/79/28 come from the fixer's out-of-tree `hist_census.py`, which is not in the tree. My own net (above) is narrower and was built by me. The body's macOS browser-lane result is also not re-derived; CI's `tests / browser` decides it.
- CI: `merge_train.py classify b46f8832d` printed `GREEN b46f8832d5ea31651ef66294f8d0263c6c3b8732 pending: none red: none` (rc=0, `ev/classify.txt`). The PR's check-runs listing at this head (55 runs, one page of 100) shows every run concluded success or skipped, none red. That includes `governance / instrument-self-tests`, `gate`, `pr-contract / pr-contract`, `tests / browser`, `tests / mutation` and `tests / closure-scope`. The body's `## Red checks` names `governance / instrument-self-tests` red at the earlier head 8ad138bb5. It answers that as main's uutils-sleep red, fixed by #3086, which this head merges. The aggregate `gate`/`pr-contract` reds are tied to it. That answer stands, and nothing is red at this head.
- Head re-read before return: `git ls-remote origin refs/heads/fix/r10-ux-health-p3` printed b46f8832d5ea31651ef66294f8d0263c6c3b8732, so the head did not move.
