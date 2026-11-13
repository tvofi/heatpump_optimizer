# Proposal triage, session s14, batch 183 (P602-P605)

This batch rules `s7/triage-queue-s7.txt` lines 281 to 284. The bar and the denominators are
batch 141's.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster`, read at 10:50Z.
- `$HPO_STATE_DIR/open-driver/open-driver.log`.
- No GitHub API calls. The CodeQL job durations are the orchestrator's, quoted in line 281.
- Nothing was run to measure line 283. It was read statically, on the orchestrator's instruction.

## P602: CODEQL-PYTHON-CRITICAL-PATH

Verdict: ACCEPT, narrowed to arm (c): a pulse line that names the one unfinished job against its
baseline. It goes as a carry on R10-TICK-RESIDUE-P2, which is not-started and carry_receivable.

Arms (a) and (b) are not triage's to accept, and are routed to the owner:
- (a) paths-ignore on the python leg;
- (b) making `Analyze (python)` non-gating for the PR gate.

Source: queue line 281, 2026-11-11T10:31:01Z, orchestrator s14.

### Measured

- **Job durations.** `codeql / Analyze (python)`: 2173-3623 s over six jobs today. The sibling
  legs: 48-104 s.
- **Cause, already measured in the tree.** `.github/workflows/codeql.yml:113-126` records it as the
  single-threaded extraction of `tests/features.py`, plus a query evaluation that grows with it. The
  python cap is 75 min (`:128-134`). The file says: "The structural cure (splitting
  tests/features.py) is an owner ruling, not this cap".
- **Python bytes on main.** 26.1 MB in total:
  - `tests/`: 9.2 MB, of which `tests/features.py` alone is 3.6 MB;
  - `tools/`: 5.3 MB;
  - `custom_components/`: 3.2 MB.
- **Arm (a).** paths-ignore of `tests/`, or of `tests/` plus `dev/`, narrows the security finding
  set. The workflow's own rule (`:41`) is that its one paths-ignore entry "narrows no finding set".
  The query suite is `security-extended` (`:198`).
- **Arm (b).** Non-gating on PRs changes a required context of the `main` ruleset.

So both (a) and (b) are owner decisions, and so is the features.py split. Triage cannot accept them.
For the owner, the expected effect of either is PR CI wall time falling from 36-60 min to the
next-longest job.

### Arm (c): the slip it removes

- **The slip.** Two near-complete python jobs were cancelled at 10:29Z, misread as hung. Each was
  about 36-60 min of critical-path wall time, and the relaunch restarts the clock. That is about
  70-120 min of critical-path CI lost in one misread.
- **The line.** When exactly one job of the waited run is unfinished, the pulse prints its name,
  elapsed time and baseline: the p50 and max of the last 6 completed jobs of the same name, read
  from the same check-runs listing. For example:
  `CI waits on 1 job: codeql / Analyze (python) 41m of p50 47m / max 60m (normal)`.
- **Cost.** One line per pass, from data the wait already lists. No extra API calls.

## P603: OPENER-STALE-LEVEL-TIP

Verdict: ACCEPT. It goes as a carry on R10-RELAY-ARM-ORDER, which is not-started and
carry_receivable. That group is the same incident's group: the relay pass length starves its
consumers.

Source: queue line 282, 2026-11-11T10:31:33Z, orchestrator s14.

### Measured

- **What the log shows.** `open-driver.log` holds 18 `SKIP ... moved` lines, all on two topics:
  - r10-outside-disinfection-setpoint, 9 lines. This is the top-priority outside PR.
  - r10-process-slim-p2, 9 lines.

  Each pass skipped the topic because the board's sha was not origin's live handoff tip.
- **Why it never cleared.** `open_driver.py:278-279` skips on `moved`, and the board is rewritten
  only once per relay pass.
- **Why P601 does not fix it.** P601's reorder writes the level seconds after the relay arms. It
  still writes it once per pass, and a pass still holds one full prepr per update. So it would not
  have stopped this 45-min starvation.

### Card (carry 2 on R10-RELAY-ARM-ORDER)

**`tools/audit/seat/open_driver.py`.** On `moved`, re-run the candidate checks at the live tip in
`tips` instead of skipping:
- `no-body`, `seen`, `landed` and `fix-branch` are each already computed from live refs;
- open_pr.sh's own refusals cover the rest.

Keep `SKIP moved` only when the live tip is absent.

- **Self-test.** A board line at sha A, with origin's tip at B and B clean, opens at B.
- **Mutation proof.** Restoring the skip fails that check.
- **Null control.** A line whose handoff ref is gone still prints `SKIP moved`.

**File overlap.** R10-SEAT-IDENTITY-P5 also lists `open_driver.py`. The seam is distinct: the
candidate's tip, not identity. The overlap is admitted.

## P604: SELFTEST-FORK-EXHAUSTION

Verdict: ACCEPT arm (a), narrowed: a process cap in the tracked mutant driver
`tools/audit/seat/mutant_run.py`. It opens the new S group R10-MUTANT-RUN-FORKCAP; no receivable
group lists `mutant_run.py`.

REJECTED:
- arm (b), a re-entry guard in `cloud_relay.sh`'s self-test;
- a separate root-cause seat.

Source: queue line 283, 2026-11-11T10:37:31Z, orchestrator s14, and its follow-up relay naming the launcher.

### Measured, by reading only

- **What happened.** A chain of `cloud_relay.sh --self-test` runs nested about 680-700 deep in one
  process group. It exhausted the per-user limit (`ulimit -u` 1333) for about 4 min and stopped every
  local seat. It was launched by an out-of-tree prototype that ran a reverted hunk of the #3448 head.
  The prototype killed only its direct child.
- **The tracked driver groups and kills correctly, but has no cap.** `mutant_run.run_cmd` (`:86-99`)
  already starts the command in a new session (`start_new_session=True`). On timeout it SIGKILLs the
  whole group (`_killpg`, `:102-104`).

  The timeout defaults to 600 s (`:347`), and nothing caps the process count. The chain filled the
  1333 slots in under 4 min. So under the tracked driver the same mutant would still have exhausted
  the host, and held it until the 600 s timeout fired. The group kill bounds how long the outage
  lasts, not whether it happens.
- **pr_bounded.** `pr_bounded` (`pr_args.sh:296-343`) bounds wall time and setsids each entry. It
  runs unmutated code, whose re-entry is guarded by PR_BOUND (`cloud_relay.sh:1862`). It is not the
  exposure, so no card is put on it.
- **Why arm (b) fails.** A re-entry guard inside the self-test is itself mutable code. A mutant that
  deletes or reverts it reproduces the chain, and that is this incident's shape, since a reverted
  hunk made the self-test re-enter. Only the driver, which runs outside the mutated tree, can bound
  every mutant.
- **Why no root-cause seat.** The launcher is identified. The cause is named: an unbounded fork
  under a mutant with no process cap. The countermeasure is this card. A root-cause seat would add
  nothing that the card does not owe.

### Bar

- It removes a slip class that, in one instance, stopped every local seat and the wake loop.
- Exposure grows with every mutant run. P599 and the mutation-vacuous investigation are driving more
  mutant runs over self-tests.
- Cost: a cap check at launch and per poll. No new dependency.

### Card (R10-MUTANT-RUN-FORKCAP)

**`tools/audit/seat/mutant_run.py` `run_cmd`.** Bound the command's process tree. Either of these
works:
- poll the command's session every 0.5 s and `_killpg` it past 256 processes;
- or set an RLIMIT_NPROC soft limit at the user's current count plus 256 in the child.

Report it as a distinct outcome, `FORKCAP`, never as `KILLED`. A cap stop says nothing about
whether the test pins the mutant; counted as a kill, it would hide a survivor.

- **Self-test.** A command that forks a chain without end is stopped within seconds, reported as
  FORKCAP, and leaves no process of its session behind. The user's process count returns to its
  starting level.
- **Mutation proof.** Removing the cap fails that check. Run it under a test-only low cap, for
  example 32, so the proof never approaches the host limit.
- **Null control.** A command that forks a bounded 10 is unaffected.

The finding goes into the mutation-vacuous report: an out-of-tree mutant prototype must run through
`mutant_run.py`, never its own Popen.

## P605: CARRY-LANDED-OWN-GROUP

Verdict: ACCEPT. It goes as a carry on R10-CARRY-AUDIT-P5, which is not-started and
carry_receivable, after R10-BODY-CONTRACT. That group owns the carry-audit seam of a part-N body.

Source: queue line 284, 2026-11-11T10:38:57Z, orchestrator s14.

### Measured

- **What bus.sh passes.** `bus.sh carry_landed` (`:228-237`) runs
  `carry_audit.py landed --body <b> --pr "#N"`, with no `--topic`. The `landed` subcommand accepts
  `--topic` (`carry_audit.py:962-966`).
- **Why the own group is lost.** `own_group` (`:602-610`) falls back to a topic token only for a
  source that is not `#`-prefixed. When the roster's `pr_group` does not name the PR, the own group is
  None. Then the own-carry status exemption (`:643`, `mut:ownstatus`) never applies, and a part-N
  body's "not built in this part ... Carry: <own group>" lines are refused CARRY-MISSING.
- **Cost of the instance.** #3448: 23 lines, one refused reviewer dispatch, one body-repair seat,
  about 15 min.
- **Exposure.** 6 live part-N groups (`-P<n>`), 1 in-progress and 5 not-started.
- **Check behaves correctly.** `check` already resolves the group from `--branch` (`:995`).

### Bar

- It removes a recurring slip class that refuses the dispatch of every later-part body carrying an
  own-group status line.
- Saving: about 15 min and one repair seat per hit, about 90 seat-min over the 6 live part-N groups.
- Cost: one argument in bus.sh. The PR's head ref is already in the `gh api pulls/N` response that
  carry_landed reads.

### Card (carry on R10-CARRY-AUDIT-P5)

**`tools/audit/seat/bus.sh` `carry_landed`.** Read `.head.ref` in the same `gh api` call, map it to
the topic with `topic_grammar.py pr-topic`, and pass `--topic <topic>` to `carry_audit.py landed`.

- **Self-test.** A part-N body with "Carry K: not built in this part ... Carry: <own group>",
  under a stub PR whose head ref is the group's fix branch, passes carry_landed (rc 0).
- **Mutation proof.** Dropping `--topic` returns rc 1, CARRY-MISSING.
- **Null control.** The same line naming another group is still refused.
