CLOUD REVIEWER seat for PR #2828 of tvofi/heatpump_optimizer, at head 5d093b09f4a1043f11f3d23123040481fa11fbfb. Bus nonce: b4844795302db6dc0794e3015c2d7134. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin 5d093b09f4a1043f11f3d23123040481fa11fbfb`; the PR body is in the PR. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree`) and read CI on this head from the check-runs API.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 5d093b09f4a1043f11f3d23123040481fa11fbfb` or `Fix review: blocked 5d093b09f4a1043f11f3d23123040481fa11fbfb <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: b4844795302db6dc0794e3015c2d7134`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads no item there as a finding unless it hands something on (deferred, for a later, follow-up, minor, advisory, residual, still has to, not blocking ...; a check that does not block is evidence only in the clause saying it is not a required check and does not block, never in the rest of its sentence: a nit or defect beside it is a finding), and the merge train parks a verdict holding a finding with no `Carry:`. Put the evidence files in `ev/` beside it, and make at least one file under `ev/` contain the full 40-hex head `5d093b09f4a1043f11f3d23123040481fa11fbfb` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=seat -c user.email=seat@users.noreply.github.com commit-tree $T -m "verdict 2828 5d093b09f4a1043f11f3d23123040481fa11fbfb") && git -C $R push -q origin $C:refs/heads/probe/rev-2828-b4844795`. That ref is the return signal. Do not post comments, approve or merge.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
DELTA review of #2828 (triage batch 28, dev/programme/triage/s6-batch28.md, rulings P150-P157) at the re-cut head, against dev/governance/roles/proposal-triage.md and dev/governance/roles/fix-review.md. The previous head was blocked; the blocked verdict is attached below. THE RULE TRIAGE APPLIES, which you check on every ruling: an unmeasured benefit is DEFER; an ACCEPT stands only when it is (a) measured (the Instances: field carries the command or log reference beside each figure and you re-derive at least one), (b) measure-first (the destination group's first step is the measurement, with a removal criterion), or (c) a trial with a named measurement and a removal criterion. An even trade is REJECT. For each finding in the attached verdict, say whether the re-cut closed it, with the line that does. Re-check every ruling's Source:, Instances:, Cost:, Binding: and that every ACCEPT names a destination group that is LIVE on the roster at origin/main (exists, not done, not absorbed, not merging or in the train spool); a DEFER names a group that is not done or absorbed; a ruling that re-cuts an earlier one cites it; no ruling duplicates another or an existing group. Check the body's verdict figures against the file, that the pull request changes only the batch file and its delivery row, and that no host or home path appears. Report a ruling you would change, with the evidence, and say merge or blocked.
No host or home paths in anything you push; cite repo-relative paths only.

=== THE BLOCKED VERDICT TO CLOSE (attached) ===
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

bus: verdict/2828 at d98d49170cdb1a09c4323ba81a1ab8cf0e1efa2f, confirmed from reviewer-2828 (review/2828 at 0189942c0280d4e1e2339194100ee70d44f13bbf); evidence: ~/.zcode/bus/verdicts/2828/d98d49170cdb1a09c4323ba81a1ab8cf0e1efa2f/evidence

