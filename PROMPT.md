CLOUD DESIGN REVIEWER seat for tvofi/heatpump_optimizer, topic R10-COMBI-TANK-PR-B, at head b8f67a775137a8032d5c71b34ea64165c1d4613a. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render design-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/design-review.md from main, and follow it exactly. Review the design at refs/heads/design/R10-COMBI-TANK-PR-B, SHA 079d303b06dd7f80a300c1f55a33c6a9052c0a54: `git fetch origin 079d303b06dd7f80a300c1f55a33c6a9052c0a54` and open a detached worktree there. The base the note names is judged against b8f67a775137a8032d5c71b34ea64165c1d4613a. Rerun nothing; there is no code.
Output: write verdict.md, whose first line is exactly `Design review: approve 079d303b06dd7f80a300c1f55a33c6a9052c0a54` or `Design review: revise 079d303b06dd7f80a300c1f55a33c6a9052c0a54 <class>` (the class is lower-case letters and dashes), and run `bash tools/audit/seat/bus.sh push-design-verdict R10-COMBI-TANK-PR-B <verdict.md>`, which pushes refs/heads/design-verdict/R10-COMBI-TANK-PR-B and refuses a design that has moved; that push is the return signal. You may push only to that ref. Write no design, open no pull request and push no code.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
PR B of the approved R10-COMBI-TANK design (PR 0 #3268 merged, PR A #3358): the loader wiring an install reaches, the combi seed, display and accounting of the exchange, the web-verified figures, and the Co-authored-by trailer crediting the outside contributor. Outside-sourced (#3225): outside tier. Created by the carries-open audit (orchestrator s13, 2026-11-09) from the carries listed in its carry entries; each carry entry names its source group and index.

After: R10-COMBI-TANK

Carry 0: Moved from R10-COMBI-TANK carry 1 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner ruling 2026-11-06 ~22:02Z (tvofi), verbatim: "Make sure the combi tank design includes thorough investigation of how this and other types of combi tanks works, so the heat transfer is physically sound, and the implementation is general enough for many types of combi tanks." Binding on every R10-COMBI-TANK design note, design review and fixer. The design must survey the MFS 600 S (#3225 datasheet) and the other common combi/multifunction tank types: tank-in-tank, internal DHW coil, external plate exchanger/fresh-water station, stratified buffer with solar/wood coil, dual-zone single vessel. For each it states the heat-transfer path between the space-heating and DHW volumes (conduction/coil UA, stratification, mixing), with physical parameters and sources. The model must conserve energy across both volumes; a null control (no coupling: UA=0) reproduces the separate-tank result. Tank type is configuration, not code branches per vendor. A design review returns revise (class-open) when the survey, the physical model or the generality is missing. Carry: R10-COMBI-TANK

Carry 1: Moved from R10-COMBI-TANK carry 2 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner ruling 2026-11-06 ~22:12Z (tvofi), verbatim: "Bump the waiver for up to 10 rounds before re-cut. The design should be robust, efficient to integrate and be architecturally sound and easily maintainable and it is worth spending time to get this right." Supersedes the 5-round waiver: R10-COMBI-TANK design may take up to 10 design-review rounds before any minimal re-cut (three-round rule waived for this group). Every design review also judges robustness, integration efficiency, architectural soundness and maintainability, and returns revise (class-open) on a design weak in any of them; schedule pressure is not a reason to approve. Carry: R10-COMBI-TANK

Carry 2: Moved from R10-COMBI-TANK carry 3 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner request 2026-11-06 ~22:55Z (tvofi), verbatim: "have a seat with web access verify those figures before PR B". PR B (R10-COMBI-TANK) does not start until a web-capable verification seat's report on the design note's [assumed] / [standard; as recalled] / [datasheet ranges] figures (DIN 4753-8 / EN 12897 test conditions, EU 812/2013 standing loss, coil U range and the 0.85 / 0.95 / 0.75 effectiveness presets, DVGW W 551's 3-litre rule, the MFS 600 S datasheet, EN 12977-4) is folded into PR B's brief; every CORRECTED figure changes the preset table or help text as the report states, and a figure that changes PR A's physics goes to PR A's fixer before its handoff. Carry: R10-COMBI-TANK

Carry 3: Moved from R10-COMBI-TANK carry 4 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Web verification report (orchestrator seat, 2026-11-06 ~22:57Z) folded per carry s12-combi-figures-verify. Binding on PR B (R10-COMBI-TANK). PR A takes only item 1's UA.
1. MFS 600 S preset, per the manufacturer manual 83017400eDE (documents.unidomo.de/de/83017400eDE_MFS.pdf):
   - heating volume 504 l (not 572);
   - potable coil 40 l (not 39), 7.5 m2;
   - standing loss 111 W at 65 C ErP, so 2.66 kWh/24h (not 3.1);
   - UA = 111/45 = 2.47 W/K (not 2.87);
   - C = 0.631 kWh/K;
   - cooling rate at 25 K: 0.106 K/h over 504 l, 0.098 K/h over 544 l.
   The help-text example's "user enters 39 l" becomes 40 l.
2. Standing-loss help text: prefer the ErP standing loss S in W at 65 C, then UA = S/45 K. Label the 20 C ambient [assumed].
3. internal_coil eps 0.85: keep, labelled [assumed; one measured 1.8 kW/K corrugated coil gives 0.89 at 12 l/min].
4. tank_in_tank eps 0.95 stays [assumed]. Change the volume text to "~100-250 l (IEA SHC Task 26 store C: 228 l)".
5. external_station eps 0.75: keep. The help text says:
   - eps falls with flow, 0.88 at 16 l/min to 0.58 at 38 l/min (Remko RK WP table);
   - read it at the typical draw flow;
   - manufacturers recommend primary at or below 60 C against scaling.
   Drop any "70 C cap" claim.
6. Legionella section L:
   - DVGW W 551's 3 l limit is per pipe run downstream of the heater, not the store's potable volume;
   - a one- or two-family house is a Kleinanlage whatever the volume.
   Remove the W 551 exemption citation. Keep default-off for a station on physical grounds (0 l stored potable water), and keep the force toggle. The help text notes W 551 still expects at least 60 C (Grossanlage) or at least 50 C (Kleinanlage) delivery. The owner may re-rule this product default.
7. Section T.1, the EN 12977-4 sentence: soften to "multi-node model with fitted parameters" (unverified).
Carry: R10-COMBI-TANK

Carry 4: Moved from R10-COMBI-TANK carry 6 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner ruling (tvofi, 2026-11-07): the pull request in this group that lands the multi-tank setup carries, in one of its own commits, the trailer
Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>
crediting the outside contributor of #3226 (adopted as #3232). Their commits reached main under the placeholder email noreply@users.noreply.github.com, so GitHub credits an unrelated account, and history is not rewritten (owner ruling, same day). Use exactly that address (GitHub user id 476059); the trailer is a human co-author credit, not a tool attribution, so ref_privacy's attribution guard does not apply. Name it in the body under ## Forward-carry as landed. No README change (owner: skip README). Carry: R10-COMBI-TANK

Carry 5: Moved from R10-COMBI-TANK carry 7 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From this pull request, body item 7907dbfa: PR B must empty `unwired_combi` in `tests/features.py` (`the combi store's fields are reachable from no config key until PR B wires them`) when its loader wires the three fields; the check refuses itself the day a wired field stays in the set. Control: the check's own reading at this head (`probe` None for all three). Carry: R10-COMBI-TANK (item unwired-combi-set) (items 7907dbfa)

Carry 6: Moved from R10-COMBI-TANK carry 8 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From this pull request, body item cc665630: The flux exchange is a feasibility repair adopted without a score, on the fixed space plan; in combi the hot-water channel buys the heat the space side draws from the store (harness `exchange_dhw_kwh=22.135` against `null_dhw_kwh=5.327` on the same day). PR B's display and accounting (the DHW kWh tile, savings attribution) must read the store's charge as one channel or say which split it shows; re-measure with the harness's `exchange` arm at PR B's merge base. Carry: R10-COMBI-TANK (item exchange-accounting) (items cc665630)

Carry 7: Moved from R10-COMBI-TANK carry 9 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From this pull request, body item c45c9022: The exo term in the LP's free recursion and in the legionella run-up walk is killed only by the syntactic census `combi_flux_live` (mutants M2, M4): the later planner stages close what the seed under-buys. PR B, or any stage changing the planner's stages, keeps that census and does not read lp_flux as covering those two sites. Carry: R10-COMBI-TANK (item exo-seed-census-only) (items c45c9022)
