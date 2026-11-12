# Proposal triage, session s14, batch 229

Source: the orchestrator's brief to triage seat s14-38 (2026-11-12), jobs 1-4 plus one proposal and a
mid-task addition, ruled as P691-P696. Line numbers are at origin/main 45adb0c3b4. Roster read at
handoff/audit-r10-roster 3bd8bac624. Rulings are the orchestrator's under mandate 6715477401 (scope all),
made by triage s14-38.

## P691: R10-FIXER-MD-SPELLING-CORPUS measurement carries (0, 1, 5)

Verdict: DISMISS
Scope: carries 0 (owner measure-first, (a)+(b)), 1 (coverage term), 5 (not-measured status note).
Evidence: (a) is in the tree, dev/governance/roles/fixer.md:27-35 ("The diff's survivors are yours
before the handoff ... Set prepr.sh's MUTANT_CMD"), last landed by #3455 (merge 046736a49f). (b) never
landed: tools/pr/prepr.sh:4568-4583 still skips when MUTANT_CMD is unset. A grep of dev/governance,
tools/pr, .claude/skills, CLAUDE.md and HANDOVER.md finds no sentence asserting the saving, the
repair-round hours or the 10-diff wall time. Nothing in the tree rests on the unmeasured figures and the
owner's saving-versus-time condition is unmet, so (b) stays unlanded. Note for main: the owner's text
asked for a recorded refusal "with both numbers"; this dismissal records it without numbers.
Ops: three mark-carry dismissed, then set-stage done --at-sha 046736a49f (last merge, #3455).

## P692: the playbook-reflection carry

Verdict: NO-OP
Evidence: already marked [moved: R10-ROUND-PLAYBOOK-FINAL] (idx 2 and 6); the destination holds it
("From r10-fixer-md-spelling-corpus, body items 1d630dea and a629d56d ..."). Nothing to queue.

## P693: R10-COMBI-TANK-PR-B census carries

Verdict: IMPLEMENTED
Evidence: tests/features.py:12381-12389 sets _CB_VENDOR_BASE = 0 (R10-HOTFIX-COMBI-CENSUS-MAIN-RED);
git grep -iE 'alpha.?innotec|mfs ?[0-9]|luxtronik' over custom_components/heatpump_optimizer/*.py at
origin/main returns 0 lines. Cured by #3466, merge 7a8e1c659a (2026-11-11T18:32+01:00).
Also marked: the Bankaifan co-author carry (exact trailer present once in #3398's commits).
Stays unverified (budget): moved carries 0-3 and 5-7 (survey, waiver, web figures, MFS preset,
unwired_combi, exchange accounting, exo census). set-stage done over them writes carries-open.

## P694: R10-COMBI-TANK-PR-B stage

Verdict: ACCEPT
Ops: set-stage done --at-sha cbd23f1c8b (#3398 merge; head 141f8af1 is an ancestor of origin/main).

## P695: a CLOSURE accept never lapses

Verdict: ACCEPT
Scope: tools/audit/seat/gantt_drift.py:20-22, :95; self-test :200-205.
Evidence: acks.txt line 104 (2026-11-05T06:31Z CLOSURE accept, one slip of about a day) re-baselines
every later slip; 2026-11-12 baseline 11-14T14:51Z against live 11-16T11:12Z, a 44 h slip, printed only
as GANTT-BASELINE re-baselined. It hid a closure slip from the owner's plan-ETA requirement.
Destination and severity: carry on R10-TICK-RESIDUE-P3 (not-started; the owner R10-FLY-GANTT-DRIFT is
absorbed), high. Figure against 20%: exempt, a hidden 44 h slip on the round closure.
Immediate step for main (local state, no tree change): append a CLOSURE act line so tonight's slip shows.

## P696: R10-STANDING-CONTRACTS-P2 twins and meta-notes

Verdict: ACCEPT
Evidence: idx 24, 25 equal idx 28, 29 once the "From r10-standing-contracts-p2, body item ..." prefix and
"(items ...)" suffix are stripped; idx 26 is the same sentence as idx 30, which carries more (the
owner-routed ruling), so 30 is kept. Idx 28 and 29 are meta-notes with no work of their own.
Ops: drop idx 24, 25, 26 by --match; dismiss 28, 29. Pending 31 before, 26 after. Idx 0-4 untouched.
Idx 5-23 and 27 not checked against main (budget): owed to the next seat.
