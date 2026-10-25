Fix review: merge 50da13119aa07e521077d13d9b912e2fabd404ad

bus-nonce: fb036a4417457ca070bf6d2f9f4c2690

## Round

Round 2: a delta review of the re-cut, after the round-1 block at ee43f3933 (verdict/2827 295f23d3c). Reviewed against `dev/governance/roles/proposal-triage.md` and `dev/governance/roles/fix-review.md`. Both are the same at the merge base c9cbe6b45 and at origin/main 8aee66b77: `git diff c9cbe6b...origin/main -- dev/governance/roles/` is empty. Head measured: `50da13119aa07e521077d13d9b912e2fabd404ad`. It was still the PR head when I wrote this. Roster read: `handoff/audit-r10-roster` 2b7fe35c6.

## Round-1 block items, each closed

1. P142 stale against c24adf589: closed. P142 now reads "Verdict: DEFER -> R10-FLOW-RECORD-PITCH's handoff c24adf589 owns the record cadence." It names what would change the answer ("record merges per 24 h left after that handoff merges, together with the price of a train-less day under `stamp.py`'s rule 5"). It also states that "R10-FLOW-RECORD-PITCH's review of c24adf589 is not bound by any triage carry from this batch". The handoff body really does reject train-only on stamp rule 5 (`ev/record-pitch-body-excerpt.txt`, line 14).
2. P147 unmeasured: closed. "Verdict: DEFER. What would change the answer is the count of seat round trips that asked a ruling already given, each by comment id". The new group R10-STANDING-RULINGS is withdrawn, and it is absent on the roster.
3. P149 done instance: closed. "Verdict: DEFER. What would change the answer is a live group that needs a capability a cloud seat lacks". R10-FLOW-MQ-PROBE is `done` on the roster (`ev/roster-destinations.txt`).
4. P141 behind a frozen handoff: closed. "ACCEPT -> R10-ADVISOR-RESIDUE, as a second sub-PR after the group's handoff". The carry opens "Follow-on sub-PR, after the handoff 367afeb85 merges (not part of that head)". The handoff tip is still 367afeb85, committed at 18:22:34Z, with its body 09c55623a at 18:57:14Z (`ev/p142-p141-rederive.txt`).
5. Title and row range: closed. Both the PR title and `dev/programme/delivery/2827.md` read "P140-P149 (V61-V72 less V66 and V67)".
6. P148 unmeasured: closed. It is now DEFER, owned by the groups that already carry each loop. Every group it names (R10-ORCH-BEATD, R10-ORCH-DISPATCH-REG, R10-FLOW-POSTMERGE) is not-started, so none is done or absorbed.
7. P142's 32 against 31: closed. Instances carries one figure with its command: 31 of 107. I re-ran that command at dfcd8d9be and got 31 and 107 (`ev/p142-p141-rederive.txt`).
- Round-1 finding (RECORD-PITCH reviewer): closed. The P142 bullet above covers it, and so does the body's Forward-carry.
- Round-1 finding (ADVISOR-RESIDUE reviewer): closed. P141's carry text says the move is not part of that head.

## Findings

- P142 cites the rule-5 arm as `stamp.py:1254`. That line is the self-test's slice (`_r5 = _r4_src[_r4_src.rindex("# Rule 5: the window"):]`). The production rule's comment is at `stamp.py:2101`, at both dfcd8d9be and origin/main. This is the same self-test-for-production mis-citation round 1 found in P140's filing. It does not change the ruling, because the rule exists and the handoff body names it. Carry: dismissed: a citation inside a DEFER from which nothing is routed; the rule it names is real (line 2101).
- The file numbers carries 0-based, as `.carry[N]`: P143 "carry 7, P71", P144 "carries 10 and 11", and P148 "BEATD carry 10, 22, DISPATCH-REG carry 5". The file does not say so. Read 1-based, every one of these lands on the wrong entry: for example, 1-based carry 7 of R10-FLY-OPENPR-ATOMIC is P70, not P71 (`ev/carries-cited.txt`). Read 0-based, every citation resolves to the entry the ruling describes. This matches `roster_edit.py drop-carry`'s "0-based index" and round 1's own reading. Carry: dismissed: consistent with the tool's index convention; no ruling is wrong under it.
- P141 states no size for its benefit. I measured it with my own planted move: `_plan_slots` (`coordinator.py:4304-4387` at origin/main) moved verbatim to `payload.plan_slots` and the four call sites re-pointed. Archscore `coord_footprint` went from 2446 to 2419 (-27, matching `logic_stmts(_plan_slots)` = 27), params_over_10 stayed flat at 7, and `score.py --delta` gave dS +0.016, IMPROVES (`ev/p141-planted-move.txt`). The ACCEPT therefore rests on a measured payment, and the follow-on sub-PR's reviewer should expect about -27 at its own base. Carry: R10-ADVISOR-RESIDUE

## Evidence

- The rule applied to every ruling. ACCEPTs: P140, P141, P143, P144. DEFERs: P142, P145-P149. No REJECT.
  - P140 is measured: the carries-not-rendered defect is in the code at `cloud_dispatch.py:283` (round 1 confirmed it; the ruling is unchanged).
  - P141 is measured: -27 footprint, above.
  - P143 is measured. Its open wait is plan-opt card V53 (median 0.99 h), which is out of tree. I spot-checked it from git and the API: on the two topics whose handoff ref has not moved since the open, handoff-to-open was 69 min (#2832) and 72 min (#2833), consistent with that median (`ev/p143-p144-checks.txt`). Its closure-saving split ("about 0.3 h each") is an estimate. The measured wait carries the ACCEPT.
  - P144 is a trial with a named measurement (pool-to-fire latency against the 20-of-25 sample) and a removal criterion ("If the share over 5 min does not fall, remove it"). I re-derived its 187 refs: `dispatch/reviewer-*` refs committed at or before the re-cut number 187. The 25-of-180 match against `cloud-sessions.tsv` is out of tree and not re-derived.
- Destinations. All ACCEPT destinations exist and are not done or absorbed on roster 2b7fe35c6: R10-FLOW-DESIGN-STAGES and R10-ADVISOR-RESIDUE are not-started, and R10-FLY-OPENPR-ATOMIC is not-started after R10-UPDATE-PR-SIGNALS (in progress, #2825 open). No open PR in the recent PR list names one of them. The DEFER owners R10-FLOW-RECORD-PITCH, R10-ORCH-REVIEW-PACKET, R10-ORCH-BEATD, R10-ORCH-DISPATCH-REG and R10-FLOW-POSTMERGE are not-started, none done or absorbed (`ev/roster-destinations.txt`). No roster carry cites `s6-batch27.md` yet, so the dropped R10-ROUND-PLAYBOOK carry the body mentions is not on the roster.
- Re-cuts cite their origins: each re-ruled entry cites verdict 6402367085 and the block item. P143 cites P134, and P148 cites P136. I found no duplicate ruling (round 1's sweep, and the delta adds no new subject).
- `roster_edit.ruling_verdict` on the head's file returns ACCEPT for P140, P141, P143 and P144, DEFER for P142 and P145-P149, and None for P150, the null control (`ev/ruling-verdicts.txt`). The body's figure "(4 ACCEPT, 6 DEFER)" matches `grep` (`ev/merge-scope.txt`).
- Scope: the three-dot diff touches only `dev/programme/triage/s6-batch27.md` and `dev/programme/delivery/2827.md`. No host or home path appears in it, and VERSION, the manifest and the notes are untouched.
- Merge: `git merge-tree --write-tree origin/main 50da131` exits 0 with tree 9842afdac (`ev/merge-scope.txt`).
- CI at this head (check-runs API, 47 runs): every completed check is success or skipped except `governance / delivery-status`. That check's log reads `DELIVERY STATUS OVERDUE` for #2780, #2749, #2775, #2797, #2762 and #2795. It says it is not a required context and blocks no merge, and it does not block. This diff adds only its own row. The body's Red checks section names it and its cheaper detector. When read, `pr-contract` was queued and two `prelude` jobs were in progress.
- Mutation: n/a. The diff writes no code line.
