# Proposal triage, session s14, batch 228

Source: the orchestrator's brief to triage seat s14-37 (2026-11-12), five items A-E, ruled as
P686-P690. Line numbers are at origin/main ef579d9ba6. Roster read at handoff/audit-r10-roster
f5fbbc2b55.

## P686: wire the R10-RCA-PREPR-DARWIN-SELFTEST return into its barrier group

Verdict: ACCEPT
Scope: routing of a root-cause countermeasure; not a proposal.

Source: handoff-body/r10-rca-prepr-darwin-selftest at cce3f946f5e8b48497e2f89486bbf4798a44c6e2, BODY.md.
Instances: three, reproduced in its section 1 (heads cb55127416 red / 89daf6c739 green for (a);
046736a49 red for (b); 1386441425 red / c8780ea33d green for (c)); process state (c).
Ruling: the group lands the analysis verbatim as dev/audit/rca/R10-RCA-PREPR-DARWIN-SELFTEST.md and
cites it from the class's `rca` in dev/audit/config/bugclasses.json; section 5's three conditions
(seat reproduction, measured-read-set selection as a required check, in-job host null controls)
become the lane's acceptance conditions, each red on its instance head and green after. The
Forward-carry items (PATH-level wc stub cannot reach /usr/bin/wc; latent BSD `sed -i` at
tools/audit/seat/pr_args.sh :842 and :935) name the same group and ride in the same carry. Friction
item: dismissed by the body itself (a probe's return is its body); nothing to route.
Destination and severity: carry on R10-PREPR-DARWIN-SELFTEST-LANE (S, medium, not-started).
Figure against 20%: exempt, root-cause countermeasure; the body's cost test gives 217.5 min per
30 days of opener blocked against a break-even of 4.8 min added critical path per selected run,
which the lane must measure (T_mac).
Cost: one workflow job plus null-control steps; the macOS minute multiplier is the owner's call.

## P687: ci_predict compared a head against a four-day-old main

Verdict: DEFER

Instances: one. body_push.sh's predictor printed 5 predicted reds on governance /
instrument-self-tests against 5bc009bc82 (main of 2026-11-08, #3274) for head c8780ea33d at about
03:0xZ, from a worktree whose origin/main read 4aa62003; a re-run 4 minutes later passed.
Cost of the defect: one refused body_push, about 12 min, on a release-blocking hotfix.
Binding: unmeasured cause. tools/pr/ci_predict.py takes the base by merge-base against `--base`
(default origin/main, :967, :1170) and runs CI's tree in a throwaway clone whose origin/main is set
to `tip` (:663-685); where 5bc009bc entered was not located. One instance at 12 min does not show a
rate. What would change it: the source of the stale tip located, or a second instance. Owner:
R10-PREPR-RESIDUE (owns ci_predict.py and body_push.sh).

## P688: cloud fixer and reviewer prompts carry a foreground bounded-wait rule

Verdict: ACCEPT

Instances: R10-HOTFIX-MAIN-IST-PREPR-SCOPE's first seat sat idle 01:45-02:55Z (70 min) with main red
after handing a wait to a background task (ledger-standin.txt, FIRED 2026-11-12T02:57Z line: "idle
since 01:45Z on a background wait, no ref pushed"); the re-fire with an explicit foreground-wait
rule handed off in about 30 min. The ledger holds 7 further no-return re-fires this round
(grep -i -E 'no return' s9/seat-dispatch/ledger-standin.txt), their cause unrecorded; not counted.
Ruling: cloud_dispatch.py's fixer and reviewer prompt text states: never hand a wait to a background
task or subagent and end the turn; wait in the foreground, bounded, re-checking the condition, and
push a ref or write BLOCKED before the session can end. No such text exists today (git grep
foreground/background on tools/audit/seat/cloud_dispatch.py: no match).
Destination and severity: carry on R10-RELAY-NOBODY-STALL (M, medium, not-started; owns
cloud_dispatch.py and seat stalls).
Figure against 20%: exempt, severity medium; 1 of 1 measured instance removed (100%), 70 min of main
red. Cost: a few prompt lines, under 100 tokens per dispatch.

## P689: update_pr BUSY forever on a clean, pushed, idle holder worktree

Verdict: ACCEPT
Scope: part (b) as an instance carry on the existing owner; part (a) DEFER.

Instances: #3479's repair handoff sat unapplied 02:54-03:26Z (32 min) until the orchestrator
detached the holder by hand; a second holder (the merge seat's remerge scratch) caught before it
bit.
Ruling: (b) is already R10-UPDATE-PR-SEAT-WORKTREE's repair (P675: detach a holder under
$HPO_STATE_DIR that is clean, at an origin ancestor, with no process cwd inside, as
tools/audit/worktree_gc.sh reads it). The carry adds these instances and binds the fixer to cover
both holders' paths. (a), an owed line after N BUSY passes, is deferred: once (b) lands a BUSY holder
has a live process, and no such stall is measured. What would change it: a BUSY stall over 13 min
with a live holder after the group merges.
Destination and severity: carry on R10-UPDATE-PR-SEAT-WORKTREE (S, medium, not-started).
Figure against 20%: exempt, severity medium; 2 of 2 instances tonight are inside its repair (100%).

## P690: merge_train re-admits a skipped entry whose head moved under a carrying verdict

Verdict: ACCEPT

Instances: #3454 and #3460 tonight, both outside-derived; `add` answered `ALREADY ... skipped by
this train at this same verdict` (tools/audit/seat/merge_train.py :1302, already_held :1278)
after one was skipped on A5 (head moved by the merge-main bot, review_carry CARRY) and one on a head
red cured by a clean main merge (CARRY); each needed a direct merge by hand under the owner's
deadlock exception.
Ruling: already_held does not hold a skipped entry at the same verdict when the live head differs
from the skipped head and the verdict carries to the live head; it holds as today otherwise.
Destination and severity: carry on R10-TRAIN-RESIDUE-P2 (S, medium, in-progress; owns
merge_train.py residue).
Figure against 20%: exempt, severity medium; 2 of 2 instances removed (100%), each an outside PR,
the queue's first priority. Cost: a few lines in already_held plus two self-test arms and a null
control.
