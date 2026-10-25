Fix review: blocked 9f76c09780ae7f88ef9c13ad7f6d1b15c590bc68 verdict-word: P152-P157 ACCEPT an unmeasured benefit and P157's carry re-carries P144

bus-nonce: 343e38390e9830ad751191596d655621

Round 1. Reviewed at head 9f76c09780ae7f88ef9c13ad7f6d1b15c590bc68 (merge base c9cbe6b45 = origin/main), against `dev/governance/roles/proposal-triage.md` and `dev/governance/roles/fix-review.md` from main (no role drift: merge base equals origin/main).

## Block

1. **P152-P157: ACCEPT on an unmeasured benefit.** `proposal-triage.md`: "an unmeasured benefit is DEFER, never ACCEPT". None of the six rulings measures the benefit of the proposal it accepts. Each cites a prize or a population and states its saving as 0 h in round 10:
   - P155's own Binding says "Round 11, starting with its plan, can price it" and "Closure saving: negative in round 10 if built now". That is the definition of an unmeasured benefit.
   - P156: "Measuring is cheap: conflicts and serial-routed entries per file from the train logs". The measurement is named, not taken.
   - P157: "needs a round of catch data before any retirement is honest".
   - P153 prices CI minutes per recarry (920 s) but counts no recarries that a cache would have hit.
   - P152 and P154 cite a population (verdict-to-merge median 1.89 h; 14 PRs blocked 3 or more times) with no share attributed to the proposal.
   
   Each ruling already names what would change its answer. The contract's word for that is DEFER.
   
   Re-cut: DEFER P152-P157, each naming its measurement. The owner's acceptance ("tvofi-accepted idea 11-16") can reach R10-ROUND-PLAYBOOK as an owner-sourced carry citing tvofi, the route that playbook carry 1 (index 1, "Round-11 decision item (tvofi, 2026-10-25 ...)") took. It should not route through a triage ACCEPT the contract forbids. `roster_edit.triage_refusal` accepts the P157 citation only because the file says ACCEPT (ev/figures.txt), so the gate cannot catch this; the verdict word is the only control.
2. **P157's carry text duplicates P144.** P157's carry text ends "Plus V65's trigger-rights daemon (P144)". Batch 27 (origin/triage/s6-batch27, #2827, not yet on main) already gives P144 its own carry text for `append-carry R10-ROUND-PLAYBOOK` on the same daemon (ev/p144-batch27.txt). If both route, the playbook holds the item twice, under two citations. The brief requires that no ruling duplicates another ruling or an existing group. Drop the P144 sentence from P157's text, or cite P144's carry as the owner of the item.
3. **P150 and P151: ACCEPT that routes nothing.** Each ruling says "no new carry". Every arm is either already carried (R10-FLOW-JIDOKA carries 16 and 18, R10-ORCH-ROSTER-SCHEMA carry 16, P135 -> R10-ORCH-REVIEW-PACKET, P154) or rejected (the UTC generator and the UTC lint). The contract's word for "the group already owning the item" is DEFER, and the timestamp arm is a REJECT naming its binding cost. An ACCEPT here makes `ruling_verdict` answer ACCEPT for a citation that has no carry to authorise. Re-cut: `Verdict: DEFER` (owned by the named carries) with the REJECT arm stated.

The body's `## Figures` line (8 ACCEPT) must follow the re-cut counts.

## Findings

- P152 cites `merge_train.py:4880` for "bisects a red pair". At both dfcd8d9be and c9cbe6b45 that line is a self-test asserting "a pair on a red main merges nothing and is not bisected". The bisect mechanism is real (the proof-branch flow at `merge_train.py:129`), but the cited line does not show it. Re-anchor the citation in the re-cut. Carry: dismissed: rides the re-cut this verdict requires, in this PR
- The plan-opt figures (verdict-to-merge median 1.89 h with n=110, PR run wall median 920 s, the 14/14 blocked-PR counts, window B 174/16/52, window C 63/16/14/14, and round-trip median 1.45 h to 2.35 h) name an out-of-tree study as their reference and no command. I could not re-derive any of them (fix-review.md step 8). `proposal-triage.md` requires "the command or log reference beside its figure: cite it, don't carry it". After the re-cut these figures support DEFER rulings rather than ACCEPTs, but each still owes its enumerator or log path. Carry: dismissed: rides the re-cut this verdict requires, in this PR

## Evidence

- Scope: the three-dot diff touches only `dev/programme/triage/s6-batch28.md` (+81) and `dev/programme/delivery/2828.md` (+1). `git merge-tree --write-tree origin/main <head>` exits 0, so there is no conflict (ev/merge.txt).
- No host or home path in either file: a grep for home-directory and temp-directory prefixes prints nothing (ev/figures.txt).
- Verdict count: 8 entries, 8 `Verdict: ACCEPT`, matching the body. `roster_edit.ruling_verdict` reads P150-P157 as ACCEPT and returns None for P158, which re-runs the body's null control (ev/figures.txt).
- Destinations at origin/main and at handoff/audit-r10-roster 32ffe43c0 (ev/roster.txt):
  - Live: R10-ROUND-PLAYBOOK not-started, no PR, not in the spool. Its brief is the round-11 playbook, so it owns a round-11 backlog. R10-FLOW-JIDOKA in-progress. R10-ORCH-REVIEW-PACKET not-started. R10-ORCH-ROSTER-SCHEMA not-started.
  - Moving code out of coordinator.py, as P156 says: R10-ARCH-SHAPES in-progress (PR 2819) and R10-ADVISOR-RESIDUE not-started.
  - Done, as P157 says: R10-GATE-YIELD and R10-FLY-YIELD-GUARD.
- Carry numbers are 0-based, as earlier batches cite them (s6-batch26.md P131 "carry 14"). Each resolves to the item claimed (ev/roster.txt):
  - JIDOKA 11: "P-Q (triage batch 9)" carry_audit in --body-check. "P-Q" is that carry's own label, not a placeholder.
  - JIDOKA 16: P67 `--fill-red`.
  - JIDOKA 18: P78 ref_privacy.
  - ROSTER-SCHEMA 16: `roster_lib.is_open` and DONE_STAGES.
- Re-derived code citations, at dfcd8d9be and at c9cbe6b45 (ev/citations.txt):
  - `app_push.sh:89` and `:442`
  - `tools/audit/seat/open_pr.sh:17`, `update_pr.sh:3` and `:24` (head_note)
  - `carry_audit.py:334` (done refusal), `roster_lib.py:33` (DONE_STAGES)
  - `prepr.sh:1417` (unnamed-red), `prepr.sh:278` (claims_check)
  - `merge_train.py:5435` (batch/<tag>-<n>), `:1071` (gh pr merge)
  - `tests.yml:43`, `:47` and `:363`
  - `D13.md:19-24` (first-pass yield)
  - Files present: `tools/policy/fixtures/policy-rot/prepr/wrong-head.md`, `head_note.py`, `figure_lint.mjs`, the `tools/policy/fixtures/figures/` set, `designer.md`, `design-review.md` and `architect-planner.md`.
  - `coordinator.py` is 11299 lines at both commits, matching P156.
- One re-derivation per ruling:
  - P150: head_note route.
  - P151: carry_audit.py:334.
  - P152: merge_train.py:5435 and :1071.
  - P153: tests.yml:47 and :363.
  - P154: figure_lint fixtures.
  - P155: designer.md and design-review.md.
  - P156: 11299 lines.
  - P157: D13.md:19-24 and the two done yield groups.
- Not re-derived: the plan-opt figures (see Findings) and P150's "#2822 round 2" `+01:00` instance.
- Batch 27 (P140-P149), which this file continues and cites (P141, P142-P149, P144), is not on main. It is open on origin/triage/s6-batch27 (#2827). A roster op citing P144 resolves only once it lands.
- CI at the head (ev/ci.txt): `governance / delivery-status` is red. It grades main, and this diff adds only its own row, so the red is not this PR's (defect-root-cause.md). Several lanes were still queued or running and no `pr-contract` run existed at read time. This blocked verdict does not turn on CI.
- Steps 1-6 and 14 (mutation, harness, claims, version, class) do not apply: the diff is a ruling record with no code, fixture or budget. VERSION, the manifest and RELEASE_NOTES are untouched.
