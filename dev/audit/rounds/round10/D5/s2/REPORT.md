# D5-s2 report (round 10, baseline 17f1c55fad1b)

Cells: M2+M3 over README.md and docs/*.md (8 files).

## Method
- M2: `links.py` checks every relative link and #anchor (GitHub slugging) across README and docs; paragraph-hash duplication between README and docs (inline, >=80 chars normalised); a version-string grep for stale versions.
- M3: backticked identifiers in the docs checked for existence in custom_components; event table in docs/automations.md checked against notifier.py:EVENT_DATA; how-it-works radiation claim checked against open_meteo.py:_VARIABLE.

## Findings
- D5-s2-01 (low, hygiene): docs/dashboard-card.md "If an upgrade seems to change nothing" shows the card's console banner as `v6.6.8` and says the card version is rewritten on every release; stamp.py rewrites only CARD_VERSION (7.0.0), not the doc sample. Harness `card_banner.py`: banner_mismatch=1; perturb -> 0.

## Non-findings
- 111 internal links, 1 broken: `../dev/archive/backlog.md` from docs/how-it-works.md:1331 -- the finder wall removed the backlog, so this is an export artefact, not a defect (harness gap named).
- 0 duplicated paragraphs between README and docs.
- Backticked identifiers: 6 not found literally; 5 are event names built by f-string in notifier.py (EVENT_*), 1 (`direct_radiation`) is named as what is *not* requested. 0 real misses.
- Event data columns in automations.md match notifier.py:EVENT_DATA.

## Exposure
Read README.md and docs/*.md in full scope (my brief); docs contain version history (v3.9.0..v6.6.5) unverifiable here because RELEASE_NOTES history is out of reach.

## Unfinished
M3 is spot depth: mechanism paragraphs of how-it-works.md (1331 lines) and configuration.md were not traced paragraph by paragraph.
