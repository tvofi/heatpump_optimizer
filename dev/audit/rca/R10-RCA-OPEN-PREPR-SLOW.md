# R10-RCA-OPEN-PREPR-SLOW: `open_pr.sh`'s full prepr runs 50 to 99+ minutes, or past its bound

Root-cause seat, `root-cause.md`, 2026-11-10. Measured on the local host
between 03:16Z and 04:05Z, all three opens at merge base `b0762725099f`
(`origin/main` at the time). Measurement only: no process was signalled.
Every figure below is a `ps`, `stat`, `sysctl`, `vm_stat`, `iostat` or `git`
reading taken by this seat, unless it is marked **reported** (taken from the
brief) or **proxy** (with what it approximates). Raw readings are in the
seat's scratch `~/hpo-seats/r10s6/rca-slow-prepr/` (`ps-0316.txt`,
`samples.txt`, `p1-durations.txt`, `ric-p1-0326.log`).

## 1. The answer to the brief's question

**Neither a queue nor a hung step. Each open runs the full prepr because no
receipt reached it, and the full prepr is long by itself and CPU- and
memory-starved on this host.**

- **Not a queue.** Each prepr took its heavy slot 0.8, 1.5 and 5.2 minutes
  after its open started (slot files' `taken_at`, against each open's
  `daemonize` line). At 03:16Z the pool was `4/4 slots held [0:run.sh-7500,
  1:prepr-78350, 2:prepr-1903, 3:prepr-8843]` with `queue=run.sh-7423`: the
  three prepr runs **are** three of the four holders, so they queue others
  (`run.sh-7423` was still queued after 10 minutes, and `run.sh-37387` joined
  it). No process in any prepr tree was a `gate_lock.py` waiter, and the
  exclusive lease (`fix-main-selftests`) is not one prepr's steps wait on.
- **Not hung.** Three process-table snapshots at 03:16, 03:19 and 03:22Z, and
  a per-minute sampler from 03:22Z, show each tree's leaf process change
  (`field_coverage.mjs` -> `structure.py`; `body_push.sh zz-lint` -> `tar` ->
  `ci_predict.py --base pmainred`; `policy_lint_mutants.mjs` ->
  `field_coverage.mjs` -> `git grep`) and each `p1.log` gain step lines. The
  silence in the open logs after `REKEY: 0 re-keyed, 0 kept` is by design:
  `app_push.sh` writes prepr's step lines to the per-open `p1.log`
  (`~/hpo-orch/r10s6/pr/<topic>/p1.log`, `~/.local/state/hpo/pr/<topic>/p1.log`),
  not to the open log.
- **Starved, by a varying factor.** 8 CPUs (`hw.ncpu`), 8 GiB
  (`hw.memsize` 8589934592). Load average 244.7 at 03:16Z and 45.0 at 03:26Z;
  127 runnable processes of 631 at 03:16Z. Swap 3.2 to 4.5 GiB used of
  4.0 to 5.0 GiB, compressor holding 321 067 pages, about 50 000
  decompressions a second (`vm_stat 5`), disk 1 500 to 2 500 IOPS
  (`iostat`). A 1-CPU-second Python loop took 1.19 to 1.83 s of wall
  time at 03:18Z (load 225) and **4.02 to 5.93 s** at 03:26Z (load 45): the
  load average is a poor reading of contention on this host, and the
  measured multiplier on a pure-compute step ranged 1.2x to 5.9x within ten
  minutes. A process spawn cost `python3 -I -c pass` 53 to 72 ms, `node -e
  0` 76 to 160 ms, `git rev-parse` 29 to 31 ms, `bash -c true` 14 to 17 ms
  per call; the prepr spawns these by the thousand.

## 2. The three instances, as measured

| open | start (Z) | slot taken | step reached / duration | outcome |
|---|---|---|---|---|
| r10-process-slim-p2, first run | **reported** | | killed by its caller's `timeout 3000` (rc 124) with `pinned graders` the last line: the self-test was running at 50 min | killed |
| r10-process-slim-p2, retry (pid 78350) | 02:26:13 | 02:27:46 | through `self-test` (515 passed), `wave-script`, `claims hygiene`, `closures` skipped by 03:01:34 (35.3 min); step 6d `ci_predict.py --record-self-tests` from 03:01:27, still running at 04:05Z, 64 min in, its leaf then `roster_edit.py --self-test` replayed from a workflow run line (the GRADER arm) | still in 6d at 04:05Z, 99 min after start; its 7200 s bound falls at 04:26Z |
| r10-hotfix-record-issue-continuation (pid 862) | 02:37:38 | 02:38:29 | through `pinned graders` by ~02:56 (18 min); `self-test` 02:56:35 to between 03:19:20 and 03:22:42 (23 to 26 min) | **`REFUSE self-test 509 passed, 6 failed`**; `app_push: REFUSE` by 03:48:52, **71 min** (section 7) |
| r10-arbiter-off-restore (pid 721) | 02:51:19 | 02:56:29 | `brief_lint` by 03:13; `pinned graders` by 03:22:42 (31 min); then the self-test `self-test` 515 passed by 03:42:51 (about 20 min); 6d 1 min; `PRE-PR ... rc=0` and `app_push: PUSHED c19017d6` by 03:44:51: **53 min** | pushed |

The per-step cost is dominated by two steps that run self-tests: prepr's own
`--self-test` (23 to 26 min here; CI's whole `instrument-self-tests` job,
which runs it beside four others on an idle 4-vCPU runner, took 14.0 min in
main's run 42577505324 on 2026-11-09) and step 6d's
`ci_predict.py --record-self-tests`: 1 min on arbiter-off-restore (`MODE: SCOPED`), and
**64 min and still running** on slim-p2 (`MODE: FULL`, 14 changed `tools/`
files), whose 6d replays each pinned grader's CI run line and each changed
file's own self-test. `prepr.sh`'s comment over step 6d still says the step
"costs seconds"; `ci_predict.py`'s header says the GRADER arm takes "minutes
where keyed". Neither premise prices an hour.

## 3. The cause

Two causes multiply.

**C-A: the receipt that should have skipped the full prepr did not reach the
open.** P386 (owner directive 2026-11-04, "a fixer's prepr is not repeated at
open or update") is built: prepr writes `hpo-prepr-receipt` in its checkout's
git dir after a passing full run; `body_push.sh`'s `prepr_trailer` copies it
onto the handoff body as `Prepr: <sha> <tree>` **only when the receipt's sha
equals the code head and the receipt is in the checkout running
`body_push.sh`**; `app_push.sh --reuse`'s `reuse_verdict` then skips the
code steps and the heavy slot. All three opens printed `app_push: REUSE: full
prepr RUNS: handoff-body/<topic>'s tip <sha> carries no one Prepr: <sha>
<tree> trailer`.

Class size, every `handoff-body/*` tip committed 2026-11-06 to 2026-11-10
(`git for-each-ref`, read at 03:30Z):

| tips | count |
|---|---|
| result bodies (no `Code:`), not opens | 12 |
| code bodies carrying a `Prepr:` trailer | 60 |
| code bodies with none | **82 of 142 (58 %)** |
| -- an earlier body on the same ref carried a trailer for the **same** code; the re-push dropped it | 5 |
| -- an earlier body carried a trailer for an **ancestor** code; only main was merged since | 24 |
| -- an earlier trailer, new non-merge code since | 4 |
| -- never a trailer on the ref | 49 |

`git merge-tree --write-tree <receipted code> <merge-base(code, origin/main)>`
equals the code's tree for **29** of those 33 earlier-trailer tips (2 conflict,
2 differ): `reuse_verdict`'s own tree test (d) would have accepted 29 receipts
that `body_push.sh` never carried.

Tonight's three are all in the "never" row, and this seat could not find a
receipt for their code heads (`6604ac08`, `0d5c1124`, `0c12e36e`) in any of
the 45 local worktrees (6 hold one). Two bodies were pushed by the
orchestrator identity from a checkout that never ran the fixer's prepr
(`tvofi`, against code by `hpo-fixer`); slim-p2's body records its fixer's
`PREPR_SKIP_CLOSURES=1` run passing at `b5ddb2a5`, after which main moved
**during that prepr** and the merge conflicted, so its code moved by a
resolution: a full prepr was owed by design, since a resolution is unproved
code.

**C-B: a full prepr is 53 to 99+ minutes on this host, and the heavy-slot cap
does not see why.** The cap is a count, `HEAVY_SLOTS = 4`
(`tests/gate_lock.py`), set on 2026-10-16 (`c09cf12010`) when
`tools/pr/prepr.sh` was 2 734 lines with 123 `st` assertion sites; at the
merge base it is 4 682 lines with 325 sites, and the self-test reports 515
assertions. Four concurrent heavy runs on 8 CPUs and 8 GiB already in swap
give each step the 1.2x to 5.9x multiplier of section 1. The slot lease is
30 minutes (`expires_at` = `taken_at` + 30 min); all three prepr holders were
`live-past-lease` by 03:26Z, the pool's own sign that the cap's premise moved.

## 4. Process state

- **C-A: (c), the process was followed and did not produce the intended
  result.** `open_pr.sh` passed `--reuse`, `app_push.sh` read the tip and fell
  through exactly as written. The design keys the receipt to one checkout's
  git dir and to sha equality, so 29 receipts `reuse_verdict` would accept were
  dropped by `body_push.sh` before the open saw them: a body re-pushed from
  another checkout (5), or a code head moved by a clean merge of main (24).
  For the 49 "never" tips the state is **not established**: whether each fixer
  ran a passing full prepr in the checkout that pushed its body is not
  recorded anywhere this seat can read, because `body_push.sh` prints one
  undifferentiated "no receipt ... in this checkout" line.
- **C-B: (d), the preconditions changed underneath a sound process.** The
  4-slot cap was right for a 123-site prepr; it measured nothing that would
  notice the prepr growing 2.6x in assertion sites, nor the host's memory
  filling, and prepr's step lines carry no time, so a run's per-step cost is
  recoverable only by sampling `ps` as this seat did.

## 5. Cost test

Units: wall-clock minutes of an open, per occurrence, over the 4.3 days
measured (2026-11-06 00:00Z to 2026-11-10 03:30Z).

- **cost(defect)**: open duration, **proxy** = `p1.log` birth to last write
  (`stat -f %B` / `%m`), runs under 240 min: full prepr **median 17 min, p75
  40, n=63**; receipt reused **median 1 min, p75 2, n=59**
  (`p1-durations.txt`). Tonight's full runs: 50 (killed), >= 99 (running), 71 (refused) and 53 min.
  Each also holds one of four heavy slots for its whole duration.
- **P(recurrence)**: 82 code bodies without a trailer in 4.3 days, 19 a day;
  29 of them (6.7 a day) are the ones C1 below reaches.
- **C1 benefit**: 29 x (17 - 1) = 464 open-minutes in 4.3 days at the median,
  about **108 open-minutes a day**, with as many heavy-slot-minutes freed;
  at p75, 29 x 38 = 1 102 minutes.
- **C1 standing cost**: one `git log -1` of the parent tip and one `git
  merge-base --is-ancestor` per `body_push.sh` call: two git spawns at the
  29 to 31 ms measured under load, **about 0.06 s a body push**. Build.
- **C2 standing cost**: none at run time (it changes which line prints).
  Benefit: turns the 49 "never" tips into a measured split for the next seat.
  Build.
- **C3 standing cost**: one `date +%s` per prepr step, about 47 step names at the
  14 to 17 ms a `bash` spawn costs here, **under 1 s a run** against a 53 to
  99+ min run. Benefit is not a number: it is what makes C-B's (d) visible
  without a seat sampling `ps`. Build, on that argument.
- **Lowering `HEAVY_SLOTS` on this host, or moving open-time full prepr runs
  to the cloud: recorded refusal for now.** Fewer slots make each run faster
  and the queue longer; the net is unknown without one idle-host full prepr
  wall time with per-step times, which C3 produces. A cap change is the
  owner's (`gate_lock.py`'s `HPO_HEAVY_SLOTS_OWNER`); deciding it on two
  CPU-loop probes 10 minutes apart that disagree by 4x would be asserting a
  number this seat did not measure.

## 6. Countermeasures, routed

- **C1 (state c), R10-PREPR-RESIDUE.** `tools/audit/seat/body_push.sh`
  `prepr_trailer`: take the candidate receipt from the local
  `hpo-prepr-receipt`, else from the one `Prepr:` trailer on the parent tip
  `body_push.sh` already fetches (`tip`); write it when the receipt's sha is
  an **ancestor of** the code head (not only equal) and its tree is that
  sha's tree. `app_push.sh` `reuse_verdict` re-proves (b) to (e) from git
  objects and fails closed, so a carried receipt can only skip the code steps
  when the head is the clean merge of the receipted code with main. A
  detector must be shown to detect: the arm's self-test drives a re-push from
  a second clone (trailer kept), a clean merge of main past the receipt
  (trailer kept, `reuse_verdict` rc 0), a non-merge commit past it (trailer
  kept, `reuse_verdict` rc 1: the null control), and a receipt on a
  non-ancestor (no trailer).
- **C2 (state c, for the unestablished 49), R10-PREPR-RESIDUE.** The
  no-trailer line names which of: no receipt file in this checkout; a receipt
  at `<sha>`, not an ancestor of the code head; a receipt whose tree is not
  its sha's; the parent tip's trailer absent.
- **C3 (state d), R10-PREPR-RESIDUE.** `tools/pr/prepr.sh`'s step line carries
  the step's elapsed seconds, and the final `PRE-PR:` line the run's, so
  `p1.log` answers "which step, how long" and a later seat can cost a cap
  change from real per-step numbers.
- **C4 (state d), R10-PREPR-RESIDUE.** Step 6d's `--record-self-tests` is the one
  hung-looking step: 64+ min on slim-p2 against a comment that prices it in
  seconds. It is progressing, not hung (its leaf changed between samples). The
  fixer measures per-arm and per-grader wall time on slim-p2's head
  (`6671786843`), corrects the premise in `prepr.sh`'s 6d comment, and bounds
  or defers to CI the GRADER replays that CI's `instrument-self-tests` already
  runs on the pull request, keeping the SELF-TEST READS recording the step
  exists for (`R10-RCA-CLOSURE-ARGV.md`). Its proof: 6d's wall time on that
  head before and after, and the same PREDICT lines both times.

## 7. Outside this RCA, found while measuring

- **r10-hotfix-record-issue-continuation's open will refuse on its own
  defect, not on time.** Its self-test reported `509 passed, 6 failed` at
  03:19 to 03:22Z, the same step its earlier 2.5 h run is reported to have
  refused in; slim-p2's prepr at the same merge base passed all 515. Three
  named failures: `refuses the cloud harness's session-link line under
  Friction by the attribution arm alone` (`tools/pr/prepr.sh:3067`), `the same
  carry passes once carry_line fetches the round branch` (`:3770`), and `the
  ok line names the count and the ref it read`. Re-running the open will not
  pass it; it goes back to its fixer.
- **The caller's 3000 s bound was below the measured duration.** The first
  slim-p2 open was killed at 50 minutes in the self-test; its retry needed
  more than 99 minutes (still running at 04:05Z). No tool sets that bound (`grep -rnE 'timeout (3000|7200)'
  tools/ dev/governance/ .claude/` prints nothing); the orchestrator chose it.

All four carries go to R10-PREPR-RESIDUE. On the round roster
(`handoff/audit-r10-roster`), that is the open group whose files hold
`body_push.sh`, `prepr.sh`, `ci_predict.py` and `gate_lock.py`. R10-HANDOFF-PATH
built P386 and R10-PREPR-CAP built the slot pool, but both are `done`, and
`carry_audit.py` refuses a carry to a done group.
