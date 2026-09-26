# Round 9 judge notes

Collected by the orchestrator. Verifier notes are relayed information; check each one against its report.

## Intake judge flags
Round-9 exposure flags for the judge (orchestrator, 2026-09-26).
(1) Driver Prepare step 1 copied tools/audit/round3..round8 into every finder tree. The boxes ran handoff/round9/r9-strip-rounds.sh (498 removed, 235 gate-read kept). Seats that ran partly BEFORE the strip: B1 D0-s1 and D3-s1; B8 D14-s1..s3; B10 D4-s1; the B4 seats (strip about 12 min into the fan-out); the B6 seats.
(2) B8 D14-s3 read docs/audit-2026-09.md rows (rounds 1, 2, 4, 6, 7) to locate fixes, and recorded it under exposure.
(3) B9 D14-s4 read, but did not cite, the docstrings of round3/D2/dst_window_factors.py, round5/D1/seat-b/h5_dst_age_seams.py and 80 lines of harnesses/j5_gil.py before the strip. This bears on D14-s4-01 and D14-s4-02.
(4) B3 D13-s1 imports the brief-named instruments tools/audit/round4/D11/{dora_keys,governance_cost}.py (gate-read, kept by the strip). It read their headers only.
(5) B2 D0-s2 listed round8/ directory names before the strip and opened no file. B3 D11-s1 ran ls on round8/D11 once.
(6) Several REPORT.md files were rendered by the box host from the seat's JSON. reports-Bn.json is authoritative.
(7) D3 quiet window NOT run, by tvofi's rule of 2026-09-26: no heavy D3 re-runs. D3 findings rest on the seats' pre-screen evidence.
(8) Catch-up batch: D3-s2 is in (registered with the lead findings); D3-s3 is still to come.

## Verifier notes and pre-dedup, from RESUME.md (dated lines)
- 2026-09-26T13:20Z: Phase C briefs written: /mnt/project-files/audit-r9/judge/J.md (strongest), R1.md, R2.md (haiku). Waiting for G1-V2, G1-V3, G3-V2 leads units, then PANEL.json + NOTES.md, then send to coordinator.
- 2026-09-26T13:05Z: pre-dedup done (intake/predup.json, .md in /mnt/project-files/audit-r9/intake/): 6 clusters over 154 findings (high: D11-s1-04+D11-s2-03, D5-s1-06+D6-s2-05; medium: D8-s1-03+D12-s2-01, D12-s1-01+D12-s1-02; low checks: D1-s5-01+D1-s5-51, D8-s2-02+D8-s2-03), 1 judge conflict (D6-s1 non-finding vs D6-s2-03). Goes to the Phase C judge. 20 format-rejected findings: normalising on the recommended option (sonnet seat, register branch), tvofi card pending.
- 2026-09-26T13:08Z: verifier returns: G2-V3 complete @990663e1 (judge notes: D8-s2-03 fix conflicts with D8-s2-02's; D10-s1-01 seam misses services.py:629 assign_entity; D8-s3-01 sort and D8-s2-03 window not measured). G3-V1 complete @ad73e2d1 (judge notes: D9-s2-02 paired harness 1.149x/0 offenders; D9-s1-01 fix loses parity on Fortran-order batches; D2-s2-03 finder perturbation tautological, replaced by coil-off arm). G1-V3 catchup @8afed0b1, leads still running. Complete so far: G1-V1, G2-V1, G2-V2, G2-V3, G3-V1, G4-V1, G4-V2.
- 2026-09-26T13:10Z: G3-V2 batch 1 @d2ce9437 (leads still running). Judge notes: D14-s4-02 fix must also step run_fixture in UTC (8/96 left otherwise); D9-s1-04 1z shoulder share 0.023; D9-s2-02 x5 did not turn red here; D2-s1-01, D2-s3-02 to low.
- 2026-09-26T13:12Z: G3-V3 complete @7802f77f. Judge notes: D9-s1-71 weaken to low (share 0.058 vs 0.094; seam misses ~8 call sites); D9-s2-71 topology_layout pinned no_valve in all 51 plants, class proposed 'new: sweep coverage gap'. Complete: G1-V1, G2-V1, G2-V2, G2-V3, G3-V1, G3-V3, G4-V1, G4-V2 (8/12).
- 2026-09-26T13:14Z: tvofi chose 'Normalise, re-admit' (card, 13:02Z). G1-V2 catchup @b56908c9: D3-s3-01..05 all verify; suite-blindness rests on recorded prescreen (not re-run). G1-V2 leads still running.
- 2026-09-26T13:16Z: G4-V3 complete @8da0652c (D11 3/5 weakens; D11-s1-04+D11-s2-03 one phenomenon, I3; D11 GitHub-API harnesses not re-run; D6-s2-05 use D6/verify-v3/s2_05_own_perturb.py; D7-s1-02 to low). Complete 9/12; open: G1-V2 leads, G1-V3 leads, G3-V2 leads.
- 2026-09-26T13:22Z: G1-V3 complete @95cbe2bf. Judge notes: D1-s2-52 raise to high (5/5 stores lost, real restart race); D1-s5-52 raise to high (-127.0 published as available), same mechanism as D1-s1-03 and D1-s2-02 (no plausibility bound) -> dedup candidate; D1-s2-51/52, D1-s5-52 to P2. Complete 10/12; open: G1-V2 leads, G3-V2 leads.
- 2026-09-26T13:25Z: register @b6eaffbb: 20 re-admitted (tvofi 13:02Z), 149 registered / 0 rejected. Normalised bodies /mnt/project-files/audit-r9/intake/normalised.json; log normalise_log.md (flag: D12-s2-01/02/03 cpu_or_wall 'neither' mapped to 'count'). Still owed on the register: D3-s3 rows (5) and LC's rows; CORPUS_EXCLUDED fix for entities.py.
- 2026-09-26T13:35Z: LC done @00e3fad9: 2 findings (D1-s2-91 medium, D3-s1-91 medium, both titles normalised), 4 leads closed (routes: two deferred-entry D3-s3 leads left to the fixer). Evidence @79aa98ec verify/G1-lc.json; sent as unit 'lc' to G1-V1/V2/V3. Register seat adding D3-s3 + LC rows (sonnet). All intake now in: 156 findings.
- 2026-09-26T13:38Z: G3-V2 complete @e62fb888 (leads 5/0/0/0; D9-s1-71 CPU share inside null band; D2-s4-81 independent subgrid excluded timber_crawlspace). Complete 11/12 main; open: G1-V2 leads, and 'lc' unit on G1-V1/V2/V3.
- 2026-09-26T13:42Z: panel tally script /mnt/project-files/audit-r9/judge/panel.py (run: python3 panel.py <repo-worktree> PANEL.json). Draft: 154 findings; 99 unanimous, 51 split, 3 disputed (D0-s1-01, D0-s2-01, D8-s2-03), 1 killed (D1-s2-01); 12 G1 leads await G1-V2's vote, and the 2 'lc' findings await all three G1 votes.
- 2026-09-26T13:45Z: G1-V1 lc @9e0a60f1: D1-s2-91 verify medium, D3-s1-91 verify medium (:8112 rests on grep only). Waiting: G1-V2 leads+lc, G1-V3 lc.
- 2026-09-26T13:47Z: G1-V3 lc @3b449903: both verify medium; D1-s2-91 -> P2, same phenomenon as D1-s2-51 (dedup candidate for the judge); D3-s1-91 I1, seam rule partial. Waiting only on G1-V2 (leads + lc).
- 2026-09-26T13:50Z: register complete @089d3470: 156 accepted from 42 seats, 0 rejected; LC leads rows added. Only the CORPUS_EXCLUDED fix remains before the register can become a PR (Mac).
- 2026-09-26T13:52Z: G1-V2 lc @2be2c155: both verify medium (D3-s1-91 :8112 now executed too). Only G1-V2 leads (12 findings) outstanding.
