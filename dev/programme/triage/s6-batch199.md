# Proposal triage, session s14, batch 199 (P623-P625)

Sources:
- Roster `handoff/audit-r10-roster` at `334095b9b6`, where the group records and the triage batches
  125, 127, 177 and 194 were read.
- origin/main `0a2139b1dd`.
- `git ls-remote origin 'refs/heads/*'`, taken 2026-11-11 at about 13:40Z: 6791 refs.
- The seat gh shim's call log, `$HPO_STATE_DIR/gh-calls.log` and `.1`, for 12:25:00Z-13:25:30Z
  (1557 lines). Its blind spot is stated in `tools/audit/seat/gh_calls.py`: calls made through a gh
  that is not the shim are not logged.

## P623: R10-FLY-CLOUD-FRUGAL-OFF disposition

Verdict: REJECT, superseded. The later owner directive binds, and the group is already closed as
`refused` on the roster. No stage line is owed. Its stale refs go to `prune_refs.py` under P624.

Source: triage queue line 300, 2026-11-11T13:17:47Z, orchestrator s14: DISPOSITION OWED.

Instances:
- **The earlier ruling, 2026-11-04.** `s6-batch125.md` P390 records the owner ruling (tvofi,
  2026-11-04): "Turn it off in the cloud". It routes that ruling to R10-FLY-CLOUD-FRUGAL-OFF. The
  group's brief opens with the same quote and sets the guard's override variable in
  `.claude/settings.json`.
- **The later directive, 2026-11-06 at about 22:40Z.** It is quoted in queue line 67 and recorded in
  `s6-batch127.md` P398 (tvofi, 2026-11-06): "Drop the frugal change. Instead, have the seats use
  subagents as required". Queue line 67 adds "(R10-FLY-CLOUD-FRUGAL-OFF refused)". Main renders it to
  every cloud role as `FRUGAL_LINE` in `tools/audit/seat/cloud_dispatch.py`, ending "never set
  FRUGAL_ALLOW_INLINE". P618 (`s6-batch194.md`) rejected setting it again on 2026-11-11.
- **The roster already agrees.** The group's `resume` is `stage: refused`, with the note "tvofi
  2026-11-06 22:35Z: drop the frugal change; seats use subagents for discovery reads as the guard
  requires; handoff-wip 668a3bf0 abandoned unmerged". The group is not open. An owed-sweep line that
  calls it open is reading the leftover refs, not the roster.
- **What the owed line keeps seeing.** Two refs remain: `handoff-wip/r10-fly-cloud-frugal-off`
  `668a3bf0` and `dispatch/fixer-r10-fly-cloud-frugal-off` `3ef92843`. A dry `prune_refs.py --topic
  r10-fly-cloud-frugal-off` (offline: `--refs-file` from the ls-remote above, `--prs-file` `[]`)
  plans `would-tag archive/...` and then `would-delete` for both. No `handoff/` code ref exists, so
  there is no cherry refusal.

Cost: none in the tree. The owner applies no settings edit, and no agent edits a settings or permission
file.

Binding: the 2026-11-06 directive is later than the 2026-11-04 ruling and reverses it in terms. Setting
the variable now would reverse an owner directive.

## P624: dispose for handoff-wip refs

Verdict: REJECT widening `cloud_relay.sh dispose`. ACCEPT narrowed instead: the existing instrument
is `tools/audit/seat/prune_refs.py --topic T --apply`, which the orchestrator runs for the topics it
clears. The two topics it refuses keep the 12-hour ack until R10-CLOSEOUT-CLEANUP, which owns
`prune_refs.py` and the round's ref closeout.

Source: triage queue line 301, 2026-11-11T13:17:47Z, orchestrator s14: INSTRUMENT GAP.

Instances:
- **Widening `dispose` would not silence the line.** `dispose` (`cloud_relay.sh:319`) writes the
  ledger. `carry_fold_arm` (`cloud_relay.sh:805`) prints `OWED carry-fold` for any handoff-wip tip
  whose BLOCKED.md is not CARRY-LANDED alone, and it never calls `disposed`, unlike `probe_arm`
  (`:341`). A widened `case` would therefore record a disposal that the arm ignores. The real change
  is the case, a `disposed` check in the arm, and two self-test arms in a hot instrument.
- **The existing route, measured.** I ran a dry `prune_refs.py --topic` offline against the ls-remote
  above. `topic_matches` (`prune_refs.py:522`) takes every `handoff*` family, so `handoff-wip/`
  is included.

  | topic | handoff-wip tip | dry plan |
  |---|---|---|
  | r10-ext-3226-recut (PR 3232 merged) | `455050aa` | archive and delete 2 refs |
  | r10-combi-tank-pr (PRs 3358 and 3398 merged) | `1e061619` | delete 4 refs (tips on main) |
  | r10-fly-cloud-frugal-off (P623) | `668a3bf0` | archive and delete 2 refs |
  | r10-ci-edit-runner (PR 3303 closed) | `f4e09423` | REFUSED: `handoff/r10-ci-edit-runner` has a `+` cherry line |
  | r10-process-slim (recut as 3451) | `9d81a62d` | REFUSED: `handoff/r10-process-slim` has a `+` cherry line |

  So 3 of the 5 owed tips clear today with no code change. The live run reads the open pull requests
  itself and refuses a topic that has one.
- **Null control.** The two refused topics are refused because their code refs carry content that is
  not on main. That refusal is the guard working as intended, and a `dispose` would bypass it.

Cost of the rejected widening: about 3 lines and 2 self-test arms in `tools/audit/seat/cloud_relay.sh`,
plus a fixer, a review and a merge.

Benefit: 2 residual tips. Each is acked about twice a day until closure, roughly 10 acks in all.

Binding: the change falls well under the 20% bar on every measure, and nothing stops a merge.

## P625: core-bucket exhaustion (REST quota)

Verdict: ACCEPT narrowed (a), as a carry onto R10-GH-READ-RESIDUE-P3 (not started; its item 1 is the
ETag-conditional read helper, P596). DEFER (b) to R10-GH-READ-RESIDUE's P449 carry (the unattributed
core-bucket drain), inside round 10. REJECT (c).

Source: triage queue line 303, 2026-11-11T13:25:42Z, orchestrator s14: QUOTA.

Instances:
- **The log.** It holds 1557 shim-logged calls for 12:25:00Z-13:25:30Z, about 31% of the 5000
  bucket. The ruleset reads are 235: 115 to `rulesets` and 112 to `rulesets/23698884`, plus 8 more
  matched by the plain `grep -c rulesets`. They are 15.1% of the logged calls and 4.7% of the bucket.
- **Per process.** The 235 ruleset calls come from 120 processes: 115 made 2 calls and 5 made 1. Each
  process reads the ruleset once. A per-process memo therefore saves nothing, and only a cache shared
  across processes cuts the reads.
- **Callers.** By the log's caller field, `merge_train.py` makes 114 calls (96, 10 and 8 under three
  checkouts). Pull-request worktrees under `pr/` make 64 (update and prepare runs), the beat checkout
  44, and the tick 6. The sites in the tree:
  - `merge_train.py:3240-3247` (`_checks_rule`, two reads);
  - `orchestrator_tick.py:1852-1861` (`required`, two reads).
- **Conditional reads are free.** P596 measured it (`s6-batch177.md`): 5 conditional reads that
  answered 304 moved core used by 0. The ruleset changes only when the orchestrator narrows or
  restores it by hand, so a 304 is the expected answer. An ETag read is exact: unlike a TTL cache, it
  never serves a stale required set after a toggle.
- **The share that is not attributed.** About 3440 calls of the 5000 are not in the log. Line 303
  assigns them to cloud seats. This seat's own REST reads also count there: 13 job-log reads and
  run-listing calls made at about 13:24-13:25Z through a gh outside the shim. The figure is therefore
  a residual, not a measurement per seat.
- **The exhaustion's cost this hour.** The bucket hit 0 at 13:24:54Z and reset at 13:25:23Z, so it
  stayed spent for about 29 s. A cut of about 230 calls per hour would have kept this hour under
  5000 (1557 + 3440 - 230 = 4767). How long the 12:24Z exhaustion lasted is not measured.

Ruling:
- **(a) ACCEPT narrowed, as a carry onto R10-GH-READ-RESIDUE-P3.**
  - Build P3 item 1's conditional-read helper once, in the shared read module `tools/audit/seat/gh_read.py`,
    and not only on TickRun.gh. Route both ruleset sites through it: `merge_train.py` `_checks_rule`
    and `orchestrator_tick.py` `required`.
  - The stored ETag and body sit under the state directory, shared across processes.
  - Expected cut: about 230 of 235 ruleset calls per hour, on top of item 1's 210-350, for 440-580
    per hour in all, or 9-12% of the bucket.
  - Self-test: a 304 serves the stored required set with no second read. A changed ruleset (a 200)
    replaces it.
  - Null control: with no stored ETag, the plain read is made.
  - Proof after the merge: `gh_calls.py --top` shows the rulesets endpoints at 2 or fewer per process
    and the 304 share, against this hour's 235.
  - This is not an exemption ACCEPT. It rides an accepted group at marginal cost: two more call sites
    on one helper.
- **(b) DEFER.** A per-cloud-seat REST budget, or the conditional path inside cloud seats, cannot be
  priced: no instrument counts cloud calls per seat. What would change it is the P449 carry on
  R10-GH-READ-RESIDUE, which attributes the drain. When that lands with numbers per seat, (b) is ruled
  against them.
- **(c) REJECT.** A longer tick interval while open PRs exceed N delays every owed line the tick
  reports. P3 item 1 already cuts the same tick reads (issue comments and check-runs, 210-350 per
  hour) at no latency cost. The binding cost is the delay, which is unmeasured and borne by programme
  completion time.

Cost:
- About 25 lines in `gh_read.py`, moved there from P3's planned TickRun.gh helper rather than added to
  it, and two call-site edits.
- P3's files gain `tools/audit/seat/merge_train.py` and `tools/audit/seat/gh_read.py`.
- No new group, check or lane.

Binding: bucket exhaustion stops reviewers' packets, relay posts and train reads. The cut uses the
mechanism already accepted and measured as free.
