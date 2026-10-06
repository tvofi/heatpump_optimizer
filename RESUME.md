# R9-UX-5 resume

stage: handed off
branch: handoff/r9-ux-actions
updated: 2026-10-06T22:26:00Z

Merged origin/main (6001b09a) before the handoff. Tip 495accb5 bundles the hot-water idle arrays into IdleContext so classify_dhw_steps stays within the ten-parameter line. The resume note is not in the code ancestry.

Green on that tree before the merge, and entities.py again after it (2189): card.mjs, card_drift.mjs (tooltip_hover and shared_steps_hover claimed), doc_claims.py (160), structure.py, env_drift.py --all (reason leaves only; 31 claims), plan_view.py.

features.py: every UX-5 check passed, including the setback floor after _resolve_away. The one red check is R9-F2.1 P3, same objective pair on origin/main.

Playwright is not installed here. docs/img/card was not regenerated. CI's card_browser lane writes those pictures.
