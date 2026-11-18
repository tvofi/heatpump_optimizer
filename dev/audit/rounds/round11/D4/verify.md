# D4 verification, round 11 (one verifier, three lenses)

Trees: every finding is in a planted scope (D4-s1/s2/s3; the lead D4-s2-51 is scope D4-s2), so every number below was
taken in the private export copy `../audit-r11-px-D4` (plain directory, `PYTHONPATH=tests/hastub`, venv-ci python).
Contention: load1 155-185 on the orchestrator Mac, thread_factor 1.000 (all numbers are counts or static arithmetic,
contention-immune).

Limitation: Playwright and its Chromium are not installed on this box (`$HOME/pwlane`, `$HOME/pw-browsers-lock`,
`~/Library/Caches/ms-playwright` absent); installing is a download needing the owner's yes. The six browser harnesses
(m1_pipes, m1_browser, m3_look) were therefore NOT re-run: V1 for those is "not reproduced"; V2 is a static measurement
of the shipped CSS/JS in the export, recorded with its own metric definition.

| id | V1 (finder harness, export) | perturbation / null | V2 (mine) | V3 reach / class / seam | vote |
|---|---|---|---|---|---|
| D4-s1-01 | not re-run (no Playwright) | not run | `.setup-svg.editing .setup-pipe { stroke-width: 3.5 }`, viewBox width SETUP_W=720, svg width:100%: band = 3.5*w/720 px, under 24 px for every card width < 4937 px; no wider transparent hit path exists for pipes (0) | real HA reachable (editor, pointer); keyboard alt exists (pipeKb tabindex/role=button) but no pointer alt; P9 confirmed; seam_rule enumerates element classes under the floor (all) | verify, medium |
| D4-s1-03 | not re-run | not run | `.hl-fold-head` min-height 32px, absent from the `${targetFloorPx}` floor list (card.js 5120-5151); coarse floor 44 -> 2 buttons per render under floor | reachable on touch; P9; seam enumerates | verify, low |
| D4-s2-01 | 8 (unfilled_placeholders_total) | --perturb -> 0 (to_zero, moved); controls 0 | `_device_prefill_form` passes `{**disclaimer(), **notes}` only; `_WINDOW_PLACEHOLDERS` absent: 2 errors x 4 files = 8 | reachable via config flow device pre-fill; HA frontend renders the brace unfilled; class new (vocabulary/placeholder drift, not P9); seam enumerates every flow error cell | verify, low |
| D4-s2-02 | 1 of 4533 | --perturb-fix-de -> 0; en/sv same key match | de.json reads {entry_id}; en/sv {entry_ids}; services.py:607 passes entry_ids -> 1 | reachable (service call w/o prices, German UI); HA logs format failure and falls back; class new; seam enumerates all leaf strings | verify, low |
| D4-s2-51 | 3 unrendered (en/de/sv) | n/a | config_flow.py:2662 passes tibber_info; config.step.user strings contain no {tibber_info}: 3 | reachable but no user loss: data_description.tibber_token already says "Create one at developer.tibber.com" -> dead code, not a missing hint | weaken, info |
| D4-s3-01 | not re-run | not run | 10 `err.message` splice sites in card.js (grep seam_rule); HA core formats HomeAssistantError translations in English for the websocket message | reachable in real HA with sv/de UI; consequence mixed-language failure line, still readable; class new; seam enumerates all sites | weaken, low |
| D4-s3-02 | not re-run | not run | .hl-stats 2-col grid, .hl-label block 12px, no nowrap, value below label: one wrapped label shifts its value by one 12px line (~14 px) | reachable; cosmetic; class new | unresolved (no executed px) |
| D4-s3-03 | not re-run | not run | static on 14px base: .tooltip 0.78em=10.92, .tt-shared 0.85*0.78*14=9.28, .sp-note 0.8*14=11.2, .layout-verdict 0.85*14=11.9 -> 4 sizes < 12 px, exactly the finder's | reachable; P9 (unfloored text) borderline, accept; seam_rule greps em font-sizes (enumerates) | verify, low |
| D4-s3-04 | not re-run | not run | READABLE constants vs --hpo tokens: light err #ca4c46/#b3261e, ok #24845d/#1c7350, warn #a16900/#8a5a00; dark err #e0574d/#f28b82, warn #ad7e1f/#e3b25a; dark ok equal -> 5 pairs | reachable; consistency defect; P9 (colour token) ok | verify, low |
| D4-s3-05 | not re-run | not run | 136 font-size/padding/margin/gap declarations with literal px/em not reading var(--hpo-*) | reachable; maintainability, no user consequence beyond inconsistency; class new | verify, low |
| D4-s3-06 | en 6/41, sv 3/41 | sentence_titles -> 0 (to_zero) | own grep of en titles: 6 Title-Case ("Heat Pump Optimizer Setup", "Temperature Settings", "Thermal Model & Optimization", "Domestic Hot Water (DHW) Configuration", "Weather Sensitivity Parameters", "Reauthenticate Tibber") | reachable; cosmetic; class new | verify, low |
| D4-s3-07 | de straight 27 / typographic 95; en degree 2 | de_quotes -> 2 (down) | degree items are in en (blueprint) per harness, 0 in de/sv | reachable; cosmetic; class new | verify, low |
