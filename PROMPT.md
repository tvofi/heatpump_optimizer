CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-ghc-research, at head a37c58e5f32123b4028e90983799dc2aa81816f8. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at a37c58e5f32123b4028e90983799dc2aa81816f8 (`git fetch origin a37c58e5f32123b4028e90983799dc2aa81816f8`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-ghc-research <result.md>`, which pushes refs/heads/handoff-body/r10-ghc-research; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
RESEARCH PROBE, R10-GENERIC-HEAT-CURVE-PERSISTENT defaults (owner-ordered 2026-11-07, #201 comment 6708164102). Read-only: no code, no PR. Use web search and web fetch. Return your result as RESEARCH.md on handoff-body/r10-ghc-research (body_push.sh's result form) and stop.

Context. The integration will steer a heat pump's heating curve by writing a Home Assistant `number` entity mapped to a controller parameter. Kind `offset` is a volatile whole-curve offset in K: the reference is Luxtronik Smart Home Interface holding heating_offset, address 10002, -20..20 K. Kind `persistent` is a curve parameter the controller stores in NON-VOLATILE memory, for example the Luxtronik parallel shift or foot point over the parameter interface (TCP 8889). Kind `persistent` writes baseline + displace and restores the baseline when switched off, so it may write such a parameter many times a day. The owner wants DEFAULT numbers that are as generic as possible across controllers and brands.

Three defaults to research:
- O5a band: the maximum deviation in K from the user's baseline (it bounds what a crash can leave behind).
- O5b daily write budget: the maximum writes per day to a non-volatile controller parameter, sized against flash/EEPROM endurance with margin for a 10-15 year life.
- O5c minimum dwell between two writes. Include the thermal response time of flow and return temperatures after a curve change, which bounds how often a change is useful.

Research each with citations (URL plus the exact claim):
1. Non-volatile write endurance in heat-pump and HVAC controllers: Luxtronik 2.0/2.1 (alpha innotec, Novelan, Siemens/Buderus variants); NIBE, Daikin Altherma, Vaillant aroTHERM, Stiebel Eltron, Mitsubishi Ecodan and Panasonic Aquarea where known; generic MCU EEPROM and NOR flash. Do controllers write through to flash on every change? Find forum or manufacturer warnings about frequent parameter writes over Modbus or the parameter interface (python-luxtronik, ha-luxtronik, loxwiki, openHAB luxtronik binding, Home Assistant forums), and any rate limits that integrations enforce.
2. Existing practice: write limits or minimum intervals that comparable projects use (Home Assistant integrations, evcc, openHAB, ioBroker, SG-Ready guidance, smart-grid parameter offsets), and their reasons.
3. Comfort and efficiency range of a curve parallel shift: manufacturer manual ranges, and SG-Ready "increased operation" offsets (often +2..+5 K).
4. Thermal response: time constants of flow and return temperatures after a curve change, for radiators and for floor heating.

Deliverable, RESEARCH.md, under 150 lines:
- For each of O5a, O5b and O5c: a recommended generic default, a min/max range for user override, and the derivation with its arithmetic.
- Every number traced to a source and marked measured, documented or estimated. Never present an estimate as sourced, and say so where sources disagree or none exist.
- A note on any brand that needs a different default.
