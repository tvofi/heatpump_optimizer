# R10-RCA-FIXER-NOBODY-STALL: cloud fixers that stop between code and body

The root-cause result for this class was returned to the orchestrator's out-of-tree
queue (line 295, 2026-11-11T12:06:50Z; its addendum, line 296). That queue is not in
the tree and a cloud seat cannot read it. This file lands the analysis as the tree
records it, in the triage rulings that accepted its countermeasures:
`dev/programme/triage/s6-batch189.md` P611 (the measurements and arms),
`dev/programme/triage/s6-batch194.md` P617 (countermeasures C1 and C2, the bar) and
`dev/programme/triage/s6-batch209.md` (the bar re-check). Host paths and session ids
are dropped. Each figure is quoted with the ruling that measured it; the ones this
group re-took are marked as such.

## 1. The class

A cloud fixer is dispatched by a commit on `dispatch/fixer-<topic>` and returns on
`handoff/<topic>` (code) and then `handoff-body/<topic>` (body, the return signal).
A fire that pushes code and never a body leaves the relay nothing to apply: the
handoff arm holds it as `HELD-NOBODY`, and before this group nothing owed the fire.

P611's census, 2026-11-04 to 11-11 (a fire is one dispatch commit, commits under
10 min apart counting as one; its window runs to the next fire on the topic):

- 628 fires over 212 topics. 460 returned a body. 124 (19.7%) returned code with no
  body; 113 of those were re-fired and 11 were still open. 50 of the 124 had no body
  at any earlier fire. 20 pushed a body before code; 24 returned nothing.
- From a code-without-body fire to its re-fire: median 174 min where a body existed
  earlier, 196 min where none did.
- For the 460 healthy fires, last code commit to body: median 10 min, p75 28, p90 48.
- Null control: were the claim false, `code-no-body` would be near zero and the four
  named stops would class as `body`. All four class as `code-no-body`.

## 2. Cause

Three mechanisms, each named by its ruling:

- **C1, a refusal with no record (P617).** The cloud brief renders "Never work around
  a hook or a refusal; report it in your result instead" and "on REFUSE stop: report
  its line as your result and start no work" (`cloud_dispatch.py`). The fixer text
  routes only a question and a CARRY-LANDED exit to BLOCKED.md. A cloud seat's only
  return is a pushed ref, so a seat that obeys a refusal leaves no record. Three of
  the four named stops (r10-relay-arm-order, r10-gh-read-residue-p2,
  r10-hotfix-combi-census-main-red) have a wip tip and no BLOCKED.md.
- **C2, a free-form stop parsed by shape (P611 arm (a), P617).** `carry_fold_arm`
  read `body_push: REFUSED <KIND>` anchored at column 0. 3 of the 8 CARRY-LANDED
  BLOCKED.md files had the line indented and printed "names no refusal line ...
  nothing folded" every pass; the 5 at column 0 were the ones folded (the null
  control). Re-measured in P617: owed carry-fold lines for 65 topics against FOLDED
  lines for 6.
- **Detection (P611 arm (b)).** `noreturn_arm` counted any moved code ref as a return,
  and the ledger's `no body ref` escalation waits `AGING_DEFAULT`, 4 h. A code-only
  stop was owed by neither for 4 h.

The RCA's own control: wakes against dispatch commits, 27% against 27% within 60 s,
rules out "the seats are woken by dispatches" as the stall mechanism (P617).

## 3. Process state

**(c): the process was followed and did not produce the intended result.** Each
mechanism ran as written. The refusal rule was obeyed and left no ref. The fold arm
ran every pass and read one of three shapes. The no-return arm ran every pass and
read code as a return. A firmer instruction would not move any of them; the
countermeasures change what each reads or writes.

## 4. Cost test

From P617, per week: about 96 real stalls (116 x 33/40 from the RCA's sample). C2
covers about 23 and C1 9 to 35, so 32 to 58 a week (33-60% of the class), each worth
at least 60 min of critical-path latency (silent 125-196 min median against a healthy
10). Standing cost: C1 is rendered text plus one push per stop; C2 adds nothing per
run, since body_push already writes the kept-body commit.

The detector (RELAY-NOBODY-OWED, this group's carry 5) costs one `git ls-remote` per
`dispatch/fixer-*` tip aged between `HPO_RELAY_NOBODY_SECS` and the window per pass,
where the no-return arm read those aged past `HPO_RELAY_NORETURN_SECS`: git only, no
GitHub API call. Re-measured by this group at 2026-11-16T18:29Z
(`git for-each-ref` over the fetched dispatch refs): 47 tips aged 3600-172800 s
against 43 aged 7200-172800 s, 4 more reads a pass.

## 5. Countermeasures and where each lands

- **Detection, RELAY-NOBODY-OWED** (P611 arm (b)): `cloud_relay.sh` `noreturn_arm` owes
  `seat-no-body` once a fire's newest code is older than `HPO_RELAY_NOBODY_SECS`
  (default 3600, above the healthy p90 of 48 min) with no body since the fire. Landed
  by R11-PRE-RELAY-REBUILD part 2, carry 5.
- **C1, STOP-TO-BLOCKED** and **C2, REFUSAL-RECORD**: accepted in P617 on
  R10-RELAY-NOBODY-STALL; P611 arm (a) (the indent regex) is superseded by C2 and not
  built.
- **Rejected:** `body_push.sh` writing the roster from a cloud fixer (P611 arm (c)): a
  roster writer the seat contract withholds. **Deferred:** the turn-end and
  frugal-guard candidate (P618), until three more silent sessions are read.

## 6. Correction to the record

The RCA's SILENT class may be one smaller (P617): its addendum reads that
r10-prepr-residue's 00:26Z fire pushed a BLOCKED.md at 00:29:22Z, but that ref was
since rebuilt and holds no BLOCKED.md in its history. C1's share is a range, so this
moves nothing.
