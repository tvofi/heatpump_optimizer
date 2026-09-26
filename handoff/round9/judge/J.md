# Round 9, Phase C: the judge (J)

Model: the strongest available (judging). One judge for the whole round (PLAN §6, judge.md via #1627).

## First
Read CLAUDE.md, every file in .claude/rules/, tools/audit/briefs/judge.md (your contract) and COMMON.md, verifier.md, root-cause.md and D14.md. Follow them. PLAN: /mnt/project-files/audit-r9/PLAN.md §6.

## Standing rules
- Call the owner "tvofi", never "Tim".
- No heavy D3 re-runs (tvofi 11:37Z). That means no mutation pre-screens, pools, full gate or quiet-window runs. You judge D3 findings on the seats' recorded evidence plus the verifiers' in-memory mutant checks, and mark them "quiet window not run (tvofi rule)".
- Cloud seat: never open, approve or merge PRs, never comment on GitHub, never file issues, never run gh.
- Resume rule: after every milestone (dedup done, JUDGE-INPUT pushed, verdicts done) send the orchestrator (session_01WgT4h2uvK9kbxQbWc5MJis) a message naming the branch and commit.
- Model routing: the mechanical re-runs belong to the two haiku runner threads (R1, R2), not to you. Re-run by hand only what is disputed, void, by-hand or out of tolerance.

## Inputs (all on GitHub, repo tvofi/heatpump_optimizer)
- Findings and evidence are on `handoff/audit-r9-evidence` (baseline 1936d5ca, v6.7.1), at `tools/audit/round9/`. Group files are at `verify/G<n>-findings.json`, `G<n>-leads.json` and `G1-catchup.json`.
- The register is `handoff/audit-r9-register`, in the Round 9 section of `docs/audit-2026-09.md`. It holds 149 findings, of which 20 were "format normalised at intake" by tvofi's decision at 13:02Z. The normalised bodies are at /mnt/project-files/audit-r9/intake/normalised.json.
- Panel is at /mnt/project-files/audit-r9/judge/PANEL.json. The orchestrator computes it from the 12 votes files using audit-verify.js's panel rules. It lists `killed` (two or more refutes, each with an executed number), `disputed` (one refute) and `survived`, with every vote's severity and class suggestion.
- The verifier reports are on the branches `handoff/audit-r9-verify-g<1-4>-v<1-3>`, at `tools/audit/round9/<dim>/verify-v<k>*.md`.
- The pre-dedup candidates are at /mnt/project-files/audit-r9/intake/predup.json and predup.md. They are candidates, not merges.
- The judge flags and the verifiers' judge notes are at /mnt/project-files/audit-r9/judge/NOTES.md.

## Order of work (judge.md, dedup first)
1. **Dedup the whole set.** This is tvofi's 12:52Z rule: dedup at the efficient phase, before re-measuring.
   - Start from predup. The high-confidence pairs are D11-s1-04+D11-s2-03 (verifier G4-V3 agrees: one phenomenon, I3) and D5-s1-06+D6-s2-05.
   - Decide the medium and low candidates yourself.
   - Keep one canonical per phenomenon and record the merged ids.
   - The D6-s1 non-finding vs D6-s2-03 conflict is "not comparable" (different metric definitions). Rule on it; do not average.
2. **Write JUDGE-INPUT.json.** It holds the canonical survivors plus the disputed findings, in finding.schema shape. Killed findings are out.
   - Exclude D3 mutation findings from the batch. Give them `judge_batch: {run: "by-hand"}` and judge them on the recorded evidence.
   - For D6-s2-05, override the perturbation with the verifier's `D6/verify-v3/s2_05_own_perturb.py`, because the finder's perturbation does not move its own metric.
   - For D2-s2-03, use G3-V1's coil-off arm.
   - Push JUDGE-INPUT.json to a new branch `handoff/audit-r9-judge`, cut from `handoff/audit-r9-evidence`, at `tools/audit/round9/judge/JUDGE-INPUT.json`. Then message the orchestrator, who starts the runners.
3. While the runners measure, read every verifier report for the disputed findings and the weakens.
4. **Read the runner rows.** These are the files `rows-1.json`/`.md` and `rows-2.json`/`.md` on the branches `handoff/audit-r9-runner-1` and `-2`. Re-run by hand anything `void`, `by-hand`, out of tolerance, or with `tree edited`.
   - The D9 CPU numbers are provisional. That covers D9-s1-71, D9-s2-71, D9-s1-04 and D9-s2-02. Use the runners' quiet-box re-takes. A result inside the null-noise band is `unreproduced`, not `verified`.
5. **Verdicts and classes.**
   - Every surviving finding gets `verified` / `weakened(sev)` / `refuted` / `unreproduced` and exactly one class.
   - Classes come from the existing class list in D14.md or as `new: <name>`, following the verifier class corrections in NOTES.md.
   - A finding whose harness does not move under its own perturbation is **void** (judge.md).
6. **Output.** Write `JUDGE.md`, `JUDGE.json` (per finding: canonical id, merged ids, verdict, severity, class, evidence rows) and `yield.json` (the per-step yield for rotation.json) on `handoff/audit-r9-judge`.
   - Also write the class list with counts N per class. Flag `rca: true` where N ≥ 3 or where the class already has a barrier. The known one is "user state not surviving restart", barriered by RC2.
   - Copy all of it to /mnt/project-files/audit-r9/judge/. Message the orchestrator with the commit, the verdict counts and the RCA classes.

## Known inputs for your notes
The known inputs are in NOTES.md. They include:
- D1-s2-01 is killed: three refutes, stub-only.
- D8-s2-03's fix conflicts with D8-s2-02's.
- D10-s1-01's seam misses services.py:629.
- D14-s4-02's fix must also step run_fixture in UTC.
- D9-s1-01's vectorised fix loses parity on Fortran-order batches.
- D13's enum_gap.mjs needs origin/main pinned to 1936d5ca.
- D11 GitHub-API harnesses were not re-run; they rest on the committed snapshot.
