<!-- Landed from dev/programme/triage/s6-batch115-rca-topic-family.md (triage P377) by R10-TICK-LEVELS part 2. Its countermeasure (section 4) is tools/audit/seat/topic_grammar.py. -->

# RCA: instruments keyed on an exact topic miss its split parts (`<topic>-p<N>`)

Root-cause seat, 2026-11-02T16:39Z. Facts read at origin/main `ea59e9a09`, the round roster
`handoff/audit-r10-roster` `2c50a2cfc`, a full `git ls-remote origin` snapshot (8453 refs, 235
`dispatch/fixer-*`), `gh pr list --state all` (158 PRs created since 2026-10-30), the session's seat ledger, the batch 106/112/115 triage files, and
the session-local `blind_spots.py` and its backup. The simulators were session-local scratch scripts (`sim.py`, and `sim2.py`, the same with bare `-<N>` included); their figures are quoted below.

## 1. Cause

**Named cause.** The topic string is the join key between five records: the dispatch ref
(`dispatch/fixer-<topic>`), the return refs (`handoff/`, `handoff-wip/`, `handoff-body/<topic>`),
the PR head (`fix/<topic>[-pr]`), the roster group (`<TOPIC>` upper-cased), and the ledgers. Nothing
defines the topic's grammar in one place. Every instrument parses the relation it needs from the
exact string itself. Splitting work into parts adds `-p<N>` and changes the topic partway through
that work. Each join that crosses a split then misses, unless its author thought of parts.

**Reproduced, not accepted.** Instance by instance:

1. **Opener (topic -> group).** The session-local opener upper-cased the topic. Each part topic
   logged `NEEDS-TITLE` (P363: `r10-fly-train-defaults-p2`, `r10-roster-ops-2-p1`,
   `r10-sav-comfort-p2`, plus a title override for `r10-ux-health-p3`; P370: `r10-deps-actions-bump-p1`
   at 03:24Z). This is fixed in the tree: `open_driver.resolve()` (commit `20cfab74c`) tries the
   exact name, then one `-p<N>` stripped, then one `-<N>` stripped, behind a body check. The fix
   is private to the opener.
2. **`noreturn_arm` (dispatch -> return).** Confirmed from the refs:
   `dispatch/fixer-r10-agreement-bootstrap` `b3f577cb` is at 08:08:44Z. Every exact-topic
   return ref predates it: handoff and handoff-wip at 05:41Z, handoff-body at 06:37Z, and
   fix/ at 07:14Z. The seat returned on `handoff/r10-agreement-bootstrap-p1`, which then
   merged as #3173. **A sharper cause than "the arm forgot parts": the orchestrator's own
   ruling told the seat to use the part topic.** The r2 PROMPT.md (commit `766ac672`, line 4) has
   the seat step-push to `handoff-wip/r10-agreement-bootstrap`, the family topic. Line 10 then
   has it hand part 1 off as `handoff/r10-agreement-bootstrap-p1` with
   `body_push.sh r10-agreement-bootstrap-p1`. So one seat writes under two topics. The dispatch
   ref records only the first. The part name exists only as free text in the prompt.
3. **`blind_spots.py` (PR -> handoff, and "a seat is on it").** **Misattributed in part.**
   - The script's measured misses are #3085 (4 RED-UNOWNED lines, 15:37Z-16:09Z) and the #3174
     retake. Both come from P375's class: a fire named only by its payload file, and handoff-wip
     motion that was never read. `r10-closeout-cleanup` is not a part topic.
   - I ran the original `cands` against the new ones over all 158 PRs since 10-30. That set holds
     16 part-topic PRs, and each one carries its own exact `handoff/` and `handoff-body/` refs.
     So the old `-(pr|2)` strip missed no code or body ref. The new `-p\d+` strip changes the
     result for one PR only: #2992 (`r10-train-overlap-grade-p3`, merged), whose
     `handoff-wip` now resolves to the family's.
   - The patched line 61 takes the **max** handoff-wip time over both candidates. A part PR's red
     is therefore silenced by motion anywhere in its family. That is right when the family seat
     is the one working on the part, which is instance 2's prompt shape. It masks the red when a
     sibling part's seat is the one moving.
   - So instance 3 is a site of the class. It is not a measured miss of the class.

**How far the class reaches (search of `tools/audit/seat` at `ea59e9a09`).** The topic grammar
is parsed independently at six places:

| site | relation | part handling | status |
|---|---|---|---|
| `open_driver.py:88-109` `resolve` | topic -> group | exact, then `-p<N>`, then `-<N>`, behind a body check | correct, private |
| `roster_sync.py:259-275` `matches` | group topic -> PR heads | `name == t or startswith(t + "-")`, longest topic wins | correct, private |
| `cloud_relay.sh:533,540` (sed/awk) | PR head -> topic | strips `fix/` and `-pr` | correct (PR and handoff share the part topic) |
| `open_driver.py:272` | topic -> PR exists | `fix/<topic>` or `fix/<topic>-pr` | correct |
| `cloud_relay.sh:612-614` `noreturn_arm` | dispatch -> return | exact only | **defect** |
| `blind_spots.py:46,61` (session) | PR -> handoff / wip | strips `-pr`, `-2` and (patched) `-p<N>`, max wip | stand-in; its tracked form is R10-TICK-PR-BUCKETS carry 6 plus b115-P375, **not built** |

The same grammar is written three different ways: `startswith(t+"-")`, `-p(\d+)`, and
`-(pr|2|p\d+)`. Those ways disagree about bare `-<N>`. `R10-ROSTER-OPS-2`, `R10-STALE-PATHS-2`
and `R10-TICK-DRIVERS-2` are real groups, so the opener treats a bare `-<N>` as a part, roster_sync
treats it as a prefix match won by the longer topic, and blind_spots strips only `-2`.
The next tracked tick level is R10-TICK-PR-BUCKETS: not started, carries 6 and b115-P375. It will
write a seventh site unless it is handed a shared reader.

## 2. Process state: (a), the process did not exist

- No policy file, role contract or instrument defines the topic grammar. A
  `git grep` for `-p<N>`, `<topic>-p` and "part topic" across `dev/governance`,
  `tools/audit/seat`, `tools/pr`, `.claude` and `CLAUDE.md` finds only `open_driver.py` (with its
  `.md` and the INSTRUMENTS.md line) and `roster_sync.py:43`. Both are a consumer's private
  rule, not a definition.
- Decision 0013's "check the instrument inventory before hand-rolling" (CLAUDE.md, Instruments)
  lists merge, push, body, gate and watch loops. Topic parsing has no entry, and none existed to
  find.
- It is not (d). Part topics predate the defective arm. #3005 (`r10-cop-gate-p5-pr`) was created
  2026-10-30T17:23Z. The `noreturn_arm` commits are dated 2026-10-31 17:30Z to 18:16Z, and it went
  live when #3065 merged: orch-wt2 fast-forwarded to `a568a2e12` at 14:58Z on 2026-11-02.
- It is not (b). No author or seat skipped a rule. P363's triage fixed its own site as the
  ruling directed. Nothing asked triage to search the class's sibling instruments, and that is
  how the class reached a second and third site.
- The split-in-prompt naming (instance 2) is part of the same absence. Nothing makes a split
  ruling name its part topics on the dispatch record. The record keeps the family topic, and the
  part name lives only in prose.

## 3. Cost test, measured

All times are UTC, read from the seat ledger and the PR API. Wall-clock is per occurrence.

| instance | false or missed lines | wall-clock |
|---|---|---|
| opener | 4 part-topic `NEEDS-TITLE` (3 of 69 RESULT lines 10-31 17:36Z to 11-01 19:27Z; 1 of 88 by 11-02 03:24Z); 1 title override (`r10-ux-health-p3`); a 19:47Z turn writing 3 more overrides | sav-comfort-p2 (CP head) 19:21Z to 19:35Z, **14 min**; roster-ops-2-p1 19:08Z to 19:19:28Z, **11 min**; deps-actions-bump-p1 03:24Z to 03:29:40Z, **5 min**; fly-train-defaults-p2 01:09Z to 13:23Z = 12 h 14 min, **confounded** with that day's opener-repair outage, so not counted. Two triage rulings (P363, P370) and a carry (built, `20cfab74c`) |
| `noreturn_arm` | 1 false `OWED seat-no-return` (16:09:47Z). That is **1 of 1 fires** since the arm went live; 3 ledger lines to dispose of it | 16:09:47Z to 16:26:08Z, **16 min**. The dispatch seat's 16:23:15Z OWED-ACK said "renders resume fixer now". It was caught at 16:25:48Z, so a duplicate **opus** resume fixer was avoided by a hand check, not by any instrument. One triage ruling (P376) and this seat |
| `blind_spots` | **0** lines attributable to this class (section 1) | 0. Its 4 #3085 lines and the #3174 retake belong to P375 |

Measured total: **6 false or missed lines**: 4 NEEDS-TITLE, 1 forced override and 1 false OWED.
On top of those, 3 overrides were written in advance. The measured holds add up to **46 min**.
One near-duplicate opus seat was avoided by a hand check. Three triage rulings and one RCA seat
came out of it.

**P(recurrence).** 13 of the 235 dispatched topics on origin split into parts in 3 days
(10-30 to 11-02), and 16 of the 158 PRs are part PRs (10%). Splitting is now a standing repair
move: the r2 prompt cites "the split that already solved this class twice". With the opener
fixed, the live exposure is `noreturn_arm`. Over all 235 dispatch refs it produced 1 false fire
on 13 splits, about 0.3 per day. A tracked RED-UNOWNED level built without a reader would add a
second exposure, of the same size as the #3085 class: 4 lines in 32 min.

**Countermeasure, standing cost.** A pure function with no I/O of its own. In `noreturn_arm` it
costs one extra `git ls-remote` with three patterns, made only for an aged dispatch whose exact
refs did not move. In the current window that is 1 of 34 dispatches, about 0.5 s per 120 s
pass. Everywhere else it costs about 0 s.

    cost(countermeasure, recurring) ~ 0.5 s/pass  <<  16 min x 0.3/day (+ an opus duplicate-seat risk)

**Verdict: build.** The class has three or more instances, which makes it an audit class that owes
a barrier (`defect-root-cause.md`). The cost test picks the barrier's form: one shared reader, not
a fourth per-site rule.

## 4. Countermeasure: one topic grammar in `tools/audit/seat`

It addresses state (a): it creates the definition that did not exist, and every site reads it.

**Demonstrated, by simulating the two rules over the real refs** (`sim.py`, read-only):

- **Fails on the defect.** The exact rule (today's `noreturn_arm`) finds no return for
  `r10-agreement-bootstrap`, which fires.
- **Passes once fixed.** The family rule finds `handoff/r10-agreement-bootstrap-p1` moved after
  the dispatch, so it does not fire.
- **Null control, it does not go green by skipping.**
  - Over all 235 dispatch refs, 55 have no exact-topic return.
  - The family rule clears exactly 1 of them (`r10-agreement-bootstrap`) and still reports 54.
  - Across the 13 split families, it changes the verdict only where the exact refs did not move.
  - Of the 34 dispatches in the arm's window now, the exact rule fires 1 (the false one) and the
    family rule fires 0.
- **Bare `-<N>`.** Including it in the family changes nothing on today's refs (`sim2.py`: same
  55/54/1). It is still excluded, because `R10-ROSTER-OPS-2` and the other `-<N>` names are
  distinct groups whose motion must never count as another group's return. That reason is a
  risk, not a measurement, and it is stated as one.

The fixer still owes the in-tree proof: a self-test row for each consumer, run red on the defect
and green on the fix, with a mutant.

### Carry brief, routable to R10-TICK-PR-BUCKETS (recommended) or R10-OPENER-REUSE

Route to **R10-TICK-PR-BUCKETS**. It is `not-started`, and it would otherwise build the seventh
site (carry 6 plus b115-P375's tracked RED-UNOWNED level). It also owns `ledger.py` and
`orchestrator_tick.py`. R10-OPENER-REUSE (`carries-open`, owns `open_pr.sh` and `update_pr.sh`) is
the fallback; only the `open_driver` move is native to it. Either way the carry adds
`cloud_relay.sh` (hot) and `roster_sync.py` to the group's files.

> From the root-cause seat for the topic-family class (2026-11-02; triage P363, P370, P376; RCA in
> `dev/programme/triage/s6-batch115-rca-topic-family.md`, to be landed as `dev/audit/rca/topic-family.md` and cited
> by `rca` in `bugclasses.json` in this PR). The topic is the join key between dispatch, return,
> PR and roster records. Its grammar is parsed separately at six sites, and the sites disagree.
> `noreturn_arm` (`cloud_relay.sh` 595-626) keys on the exact dispatch topic. It false-fired
> `SEAT ENDED NO RETURN r10-agreement-bootstrap` at 16:09Z on 11-02, after the seat had returned
> on `handoff/r10-agreement-bootstrap-p1` (merged #3173), because the split ruling named the part
> topic only in the prompt's prose.
>
> Change: add `tools/audit/seat/topic_grammar.py`, one module that owns the grammar, with a CLI
> for bash callers:
> (1) `pr_topic(head)`: strip `fix/` and one trailing `-pr`.
> (2) `family(topic)`: the base is the topic less one trailing `-p<N>`; the family is the base
>     plus every `<base>-p<N>`. A bare `-<N>` is never a family member, because
>     R10-ROSTER-OPS-2, R10-STALE-PATHS-2 and R10-TICK-DRIVERS-2 are distinct groups.
> (3) `family_refs(topic, ls_remote_text, kinds)`: the listed `refs/heads/<kind>/<member>` refs
>     whose member full-matches the family. Never a prefix: `handoff-wip` step refs and sibling
>     topics such as `r10-deeplink-census` against `r10-deeplink` must not match.
> (4) `group_of(...)`: `open_driver.resolve`'s exact, then `-p<N>`, then `-<N>` order, moved
>     unchanged, with its body check.
> (5) `owner_topic(head, topics)`: `roster_sync.matches`'s longest-topic rule, moved unchanged.
>
> Consumers:
> - `noreturn_arm` asks for the exact refs as today. When none moved, it lists the three kinds
>   for `<topic>-p*` and counts a moved family member as a return.
> - `open_driver.py` and `roster_sync.py` import (4) and (5). Their behaviour is unchanged and
>   their existing self-tests stay green.
> - `cloud_relay.sh:533,540` call (1).
> - The tracked RED-UNOWNED level this group builds reads (2) for "a seat is on it": handoff-wip
>   motion anywhere in the PR's family. A family seat writes the part's wip under the base topic
>   (r2 PROMPT.md `766ac672`, line 4).
>
> Rows:
> - `r10-agreement-bootstrap` dispatched at T, with only `handoff/…-p1` moved after T: no fire.
> - `r10-roster-ops` dispatched, with only `handoff/r10-roster-ops-2` moved: fire.
> - `r10-deeplink` with `handoff/r10-deeplink-census` moved: fire.
>
> Null controls: a dispatch whose family moved nothing still fires, and over origin's 235
> dispatch refs, 55 have no exact return and the family rule clears exactly 1. One mutant counts
> a bare `-<N>` as a family member and must fail the `r10-roster-ops` row. A second matches by
> prefix and must fail the `r10-deeplink` row.
>
> Not in scope: renaming topics, and changing what `cloud_dispatch.py` writes. If the fixer finds
> it cheaper for a split ruling to dispatch each part under its own `dispatch/fixer-<topic>-p<N>`,
> it says so in the body. The reader is still owed, because a seat can split on its own.

**Orchestrator's own stand-in, outside the carry and the orchestrator's operational call.**
`blind_spots.py:46` should keep exact-first for `handoff/` and `handoff-body/`, where the change
is harmless. Line 61's max-over-family wip should be recorded as the family rule above, not as a
fix for a measured miss: it has silenced none to date. It can mask a part PR's red when a sibling
part is the one moving.

## 5. Recording

This seat opens no PR and files no issue, by its brief. Still owed:
- The landing PR carries the in-tree RCA document (`dev/audit/rca/topic-family.md`) and its
  `bugclasses.json` entry with `rca`. Without that entry, `fold_ledger.py check` will keep
  listing the class as having no barrier and no RCA document.
- There is no issue to receive a **Root cause** section. P376 is a triage LOG, and this class
  has no issue.
