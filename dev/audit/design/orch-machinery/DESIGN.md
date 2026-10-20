# The orchestration machinery: inventory, timing model, and an improved structure

Design / pre-study seat, round 10, 2026-10-20. Revision 2, against the design
review at `review/orch-machinery-design` @ `76b6a5be` (CHANGES-REQUIRED, 47 rows:
19 PASS, 24 FAIL, 4 UNVERIFIED). Repository `tvofi/heatpump_optimizer`.

Read from the worktree at `origin/main` `a2b25bbc5`; the live instruments run from
`~/hpo-seats/r10s3/orch-wt`. Tree paths below are repo-relative and identical at
that head unless a row says otherwise. Live state was re-read between
2026-10-20T11:38Z and T12:24Z, `load1` 42.9–82.6 on 8 cores
(`sysctl -n hw.ncpu`; `uptime`). Every figure names the command in `EVIDENCE.md`;
host paths are written `~` there and here.

This is not a bug list. It is a structure, and the evidence that motivates each
element. Where revision 1 was wrong, §10 lists the correction and what replaced
it.

---

## 1. Method and what was measured

- Inventory from the tree and the live processes, never from a document's account.
  `tools/audit/seat/*` was read at the worktree head; running processes with
  `ps -o pid,ppid,etime,time,stat,command` and `lsof -p`; the state surfaces
  (`~/.local/state/hpo`, `~/hpo-orch/r10s3/orch`, `~/.zcode/bus`, the plan ref,
  the roster ref) with `wc`, `grep`, `awk`, `gh api` and `git ls-remote`.
- **No running instrument was stopped, restarted or edited.** The perturbations in
  §5 run in throwaway directories with `HPO_STATE_DIR`/`HPO_GATE_LOCK_DIR` pointed
  at them.
- Wall-clock is always reported beside `load1`; most of this box's timings are
  load-dominated, so counts and structural facts carry the claims.
- Tree size at the read head: **52 tracked entries** under `tools/audit/seat/`
  (`git ls-tree --name-only HEAD tools/audit/seat/ | wc -l` → 52; a live
  checkout's `ls` returns 53 because of an ignored `__pycache__/`, `git status
  --ignored` shows it as `!!`); **37 self-testing scripts** (`grep -l --
  '--self-test' tools/audit/seat/* | grep -vc '\.md$'`; `INSTRUMENTS.md` is a
  document and does not count as a script); 22,793 lines across the directory
  (`wc -l tools/audit/seat/* … | tail -1`). No tree file changed between the
  design's two revisions; the row count in §2 is derived from this file, not from
  these.

### 1.1 The inventory's row count

The inventory is §2's table. It has **50 rows**, derived from the file itself:

    grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md      # 50
    grep -o '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md |
      sed 's/^| M//' | sort -n | awk 'NR != $1 { print "gap at", $1; bad=1 } END { exit bad }

**Composition rule, and the trigger qualifier.** A row is a *mechanism* when it
runs on a trigger — a schedule, a push or pull-request event, a session turn, a
loop, or another instrument — and it reads, writes or repairs one of the four
state surfaces the ask names (plan ref, state mirror, `#201`,
`dev/programme/delivery/`) or a surface a mechanism in this inventory writes. A
library with no trigger joins the row of its only runner. A shared library gets
its own row only where it is the *sole* implementation of a surface's value and a
reader must know where the fact is built (`tests/delivery_status.py`, M49).

Applied, not asserted: `plan_table.py`, `resume_doc.py` and `handover_prompt.py`
fold into M08 (their only runner is `state_docs.py`); `sweep_template.md` and
`sweep_render.py` are one row (M09); `carry_audit.py` folds into M02's CARRY
section; `row_position.py`, `features_block.py`, `moved_paths.py`,
`tmp_paths.py`, `verify_eight.py`, `r10_deeplink_mutants.py` and `shims/` have
no trigger and no surface, and are excluded. This revision adds four rows
revision 1 missed: M47 `delivery-status`, M48 `delivery-status-publish`, M49
`tests/delivery_status.py`, M50 `codeql-triage-poll.sh`; and M02's reads now name
the `MERGE-READY`/`BLOCKED-UNFIXED` arm.

---

## 2. Inventory

Columns: **trigger / cadence / bound**; **reads → writes**; **L/E** level- or
edge-triggered; **on unreadable**; **stop / crash**. `!` marks a row whose
behaviour in that column is one of §4's slips.

| ID | mechanism | trigger / cadence / bound | reads -> writes | L/E | on unreadable | stop / crash |
|---|---|---|---|---|---|---|
| M01 | `tick_loop.sh` | daemonized or a session; sleep 300 s + pass; **no bound on a pass** ! | tree scripts; `--out` board via `.part.$$`+`mv`; one `TICK-PASS` line | L | maps relay rc only; **a relay fail-open prints `relay=ok`** ! | kill the pid; no pidfile, so **two loops can coexist** ! |
| M02 | `orchestrator_tick.py` | run by M01; one full read per pass; **no timeout**; 67–84 API calls (its header) | gh API; git refs; roster ref; `cloud-relay.log`; `bus.sh orphans`; **the approver App's newest `Fix review:` comments (`MERGE-READY` / `BLOCKED-UNFIXED`) and the workers JSON -> stdout only** | L | `UNREADABLE:` per section (fail closed) — except the OWED fold (M05) ! | parent dies; stateless |
| M03 | `cloud_relay.sh pass` — handoff arm | M01 every pass, or `--loop` 120 s; **no bound: runs `update_pr.sh`/`prepr.sh` inline** ! | open PRs, `handoff/*`, bus -> PR branches, `cloud-relay.log`, `cloud-handoff-failed`, **OWED events for the same set** | L (OWED) + E (updates) | gh/ls-remote failure -> `return 0` "will retry" ! | parent; body dirs under the state dir always removed |
| M04 | `cloud_relay.sh pass` — probe + relay arm | same | `probe/*`, `cloud-relayed`, bus -> verdict refs, log | L (OWED) + E (relay once) | `return 0` on ls-remote failure ! | parent; ledger durable |
| M05 | `cloud_relay.sh dispose` / `cloud-disposed` | human act | — -> append `<ref> <sha>` (210 lines, **203 distinct refs**) | L | n/a | append-only file |
| M06 | `state_docs.py beat` | daemonized; 300 s; no lock | `origin/main` + roster ref tips -> plan ref, mirror, `beat.tip` | L on a moved tip | **refuses, prints, retries** (fail closed) | tip recorded only on rc 0 |
| M07 | `state_docs.py` one-shot / `beat --once --tip-file` | sweep step 4 / post-merge / the beat's job | same surfaces | E | refuses | runs to completion or refuses |
| M08 | `plan_table.py` / `resume_doc.py` / `handover_prompt.py` | called by M06/M07 | roster (+ live PR state) -> three docs | E | generator exits non-zero | none |
| M09 | `sweep_template.md` + `sweep_render.py` | a harness timer or a human; session cadence; **no bound** | tree paths + session overlay -> a prompt | — (prose) | renderer refuses (fail closed) | none; the overlay is scratch and drifts ! |
| M10 | `policy_reread_check.py` | sweep step 0 | transcript + stamp -> OK/OWED, stamp | L | OWED on anything unreadable (fail closed) | stamp file is the state |
| M11 | `record_row.py` (the record beat) | **CI** (`tests.yml` record-autofix; `governance.yml` record), push/schedule/PR | REST merges, tree rows -> `dev/programme/delivery/<N>.md`, a `record:` PR | L (a rowless merge reddens) | refuses | CI; a refusal reddens the job |
| M12 | `bus.sh dispatch/push-verdict/confirm/post` | an orchestrator turn, a reviewer seat | bus state + `review/*` refs -> `verdict/*` refs, `posted`/`posted-signed` (546 lines) | E | refuses, pushes nothing | state is per-machine; refs durable |
| M13 | `bus.sh watch` | nudge step 1; 60 s; exits on first event | four ref families -> `refs` state file | E | dies rc 1 | restarted by the next turn |
| M14 | `bus.sh orphans` | tick every pass; sweep | `handoff*`, `fix/*`, `main` -> stdout only | L | the tick treats "no summary" as UNCHECKED (fail closed) | stateless |
| M15 | `merge_train.py run` | orchestrator; 300 s polls, 240 s heartbeat, `--main-moved-tries` 3; **no wall timeout** | API, refs -> merges, recarry worktrees, log | E | stops | worktrees removed on the way out; **no auto-resume** ! |
| M16 | `merge_train.py batch` (`--overlap`) | same | same + `batch/*` proofs | E | stops / drops an entry | same |
| M17 | `train.sh` | orchestrator, detached | argv -> `train.log`, `rc`, `train.pid` | E | refuses (no venv, live pidfile) | pidfile; stale pidfile taken over |
| M18 | `proof_watch.py` | daemonized; `--budget`; flock per pinned head | check-runs -> a merge | E | aborts, logs | flock keyed on the head |
| M19 | `queue_pre_flight.py` | before a train | API, refs -> PASS/PARK/FAIL | E | exit 1 | stateless |
| M20 | `merge_pr.sh` | orchestrator | verdict/head -> a merge | E | refuses before the merge call | stateless |
| M21 | `open_pr.sh` | orchestrator / sweep | handoff refs, body -> a branch, a PR, a row | E | refuses | **no lock and no timeout**; leaves `state/pr/<topic>/wt` and a `p1.log` ending mid-step ! |
| M22 | `update_pr.sh` | orchestrator; cloud relay's handoff arm | branch + code sha + main -> a branch | E | refuses; **75 BUSY** on a held per-branch flock | flock in a holder process that exits with the parent |
| M23 | `handoff_push.sh` | legacy path only | as M21 | E | refuses | as M21 |
| M24 | `delivery_row.sh` | sourced by M21/M22/M23 | worktree -> one row commit | E | returns non-zero | `ensure_row` is idempotent |
| M25 | `prepr.sh` | M21/M22/M26, a seat | tree, branch, body -> stdout; takes a heavy slot (M28) | E | refuses per step | slot released on EXIT/TERM/INT/HUP; **no timeout, no per-minute progress line** ! |
| M26 | `app_push.sh` / `tools/pr/push.sh` | M21/M22/M23 | worktree + body -> a pushed branch/PR | E | contract refusal before the push | stateless |
| M27 | `tests/gate_lock.py` lease | `stress.py`, `harness_headers.py` | lock dir -> owner file, tickets | L (renewable 1800 s) | expired/orphan stolen | expired owner file is the crash state |
| M28 | `tests/gate_lock.py` slot pool | every `prepr.sh` | lock dir -> 4 slot files, a FIFO ticket queue | L | **an expired slot is stolen even while its named pid is alive** ! | released on EXIT; SIGKILL leaves it until expiry |
| M29 | `wt_sync.sh` | daemon loop (900 s here) | every worktree + the scratch -> `wip-sync/*` refs | L | skips a worktree whose slug would name the host, with the reason | snapshots are durable refs |
| M30 | `daemonize.py` | a launcher, once | argv -> a log with a banner first, unbuffered | — | `--cwd` missing refuses | **no bookkeeping by design**: the printed pid and `kill` are the stop story |
| M31 | `roster_lib.py` | imported | which roster / which ref -> a parsed dict | — | `RosterNotFound` (never a silent fallback) | stateless |
| M32 | `roster_edit.py` (and the `roster_sync.py --apply` requirement in R10-ROSTER-OPS's brief) | an orchestrator turn; **the beat** for sync | the roster branch -> a formatted dump; sync derives stage from PRs | E | refuses on lint, unknown group, bad value; sync refuses an unresolvable read | **no lock**; **no `set-after` op** in the tree ! |
| M33 | plan ref `handoff/audit-r<N>-plan` | written by M06/M07; read by seats | three state docs + evidence at the ref | E | the beat retries a rejected push | the ref is the durable record |
| M34 | state mirror `~/hpo-orch/state` | written by M06/M07 | the same three docs | E | n/a | a local copy; a stale copy is indistinguishable from current |
| M35 | `#201` | one comment per record act; **`delivery-status-publish` rewrites a delimited body region on every push to main** (M48) | — -> comments (1,875) + body region | L in intent, **E in mechanism** | n/a | the issue is durable; **newest requires the last page** (the API ignores `sort`) |
| M36 | `dev/programme/delivery/<N>.md` | M11 and M21/M22 | tree -> 791 row files | L (the record job reddens) | n/a | rows are the durable record |
| M37 | out-of-tree plan generator (`~/hpo-orch/r10s3/plan/gen.py`) | sweep step 4 or a human; no self-test; **being edited live** ! | a fetched roster, REST issues/PRs, a 2026-10-17 scratch edge file (removed 2026-10-20) -> `round-10-plan.html` + scratch JSON | E | **writes a page regardless** ! | scratch; the publish path the sweep names does not exist ! |
| M38 | `ci-watch.sh` | a watcher seat; loop | check-runs -> a per-PR signature file, stdout on a new signature | L in intent, **E by a signature file** | unreadable ruleset alerts BLIND once | dies with the seat |
| M39 | `ref_privacy.py` | before every push an instrument composes | ref name, message, commits -> allow/refuse | E | refuses | stateless |
| M40 | `body_push.sh` | a fixer handoff | `BODY.md` -> `handoff-body/<topic>` | E | refuses on a predicted red | parentless first commit, fast-forward after |
| M41 | `worktree_gc.sh` | after a merge | worktrees/branches/scratch -> deleted | E | `--dry-run` lists | stateless |
| M42 | `approve_held_runs.sh` | after every App push | Action runs -> approvals | E | a no-op is not an error | stateless |
| M43 | `pr_cap.py` | `open_pr.sh`; the tick | open PRs -> count, gate | L | an unreadable list refuses | stateless |
| M44 | `app_approve.sh` / `app_comment.sh` / `gh_comment.py` | an orchestrator turn | a verdict/comment -> an approval/comment, **read back** | E | refuses on a head or SHA mismatch; "posted" never from an exit code | stateless |
| M45 | `failure_logs.sh` | any red whose cause a state line does not carry | check-runs, job logs -> files, an exit code | E | NO-JOB / NO-LOG, never a silent zero | stateless |
| M46 | `prune_refs.py` | closure; dry-run by default | remote refs -> tags + deletions | E | refuses on `main`, on undrained verdict refs | tags before deletions |
| M47 | `delivery-status` (CI) | **pull-request event**; 5-minute job timeout | tags + `origin/main` -> the delivery ledger, a check | E | a shallow clone is refused (it would report an empty window) | CI |
| M48 | `delivery-status-publish` (CI) | **push to main**; 5-minute timeout; `issues: write`; concurrency group `delivery-status-publish`, cancel-in-progress | `origin/main` -> **a delimited region of `#201`'s body**, wholesale per push | E (newer supersedes) | the body it cannot read is left alone and the job reddens | CI |
| M49 | `tests/delivery_status.py` | imported by M47/M48 and the tick's STATE/REPLAN | git history -> the ledger (who merged, what has a row, what is overdue) | — | parse failure raises | stateless |
| M50 | `codeql-triage-poll.sh` | a seat, once, for one incident; **36 × 600 s = 6 h**; hardcoded job id `109534061903` and head `3ad6e085` ! | code-scanning alerts, one checks query -> dismissals, a rerun | E | prints PARTIAL/TIMEOUT, exit 1 | scratch-shaped; nothing in the tree restarts it |

### 2.1 What the inventory shows

1. **Five rows own any wait bound at all.** M06 (300 s sleep), M15/M16 (poll
   counts), M18 (`--budget`), M27 (1800 s lease), M28 (slot lease). Everything
   else that waits — M01, M03, M21, M25, M50 — waits on a fixed count or forever.
   There is no `timeout` command in `tools/pr/prepr.sh`,
   `tools/audit/seat/open_pr.sh` or `tools/audit/seat/update_pr.sh`
   (`grep -n timeout …` → no match).
2. **The state surfaces have writers with no lock and readers that re-derive the
   format.** M32 (roster), M06/M07 (plan ref), M12 (bus), M48 (the `#201` body
   region written wholesale under a concurrency group) are read-then-write with no
   lease; M35 has 1,875 entries and no key.
3. **One surface has two writers revision 1 did not name.** `#201` is written as
   *comments* by M12/M44 and as a *body region* by M48 (and appended by M11's
   beat). One surface, several writers, no shared schema.

---

## 3. Timing graph and races

### 3.1 What runs on the box

Measured at 11:49Z (`ps -eo pid,ppid,etime,time,stat,command`):

- M01 `tick_loop.sh` pid 35000, **PPID 1**, elapsed 1:41, CPU 0:00.
- M06 `state_docs.py beat` pid 35031, PPID 1, elapsed 1:31.
- M29 `wt_sync.sh` loop pid 35037, PPID 1, elapsed 1:34.
- The harness: **one** live Claude process tree (pids 3928/3930). All seat work
  escaped as background shells of it.
- Heavy slots held by `prepr.sh` (M28), and a `mutation_table.py` set; `load1` 69.8.

The three daemons are mutually unaware. Nothing supervises them; each was launched
once and is identified only by a pid nothing records.

### 3.2 Concurrency and exclusivity

| resource | writers | exclusivity held | failure observed |
|---|---|---|---|
| `cloud-relay.log` | M03/M04 (any pass) | none (append) | ~1,860 OWED lines/h; 29,976 lines |
| `tick.txt` board | every live M01 | none (`.part.$$`+`mv`) | **two loops 27 s apart** (09:37:39Z, 09:38:06Z) |
| `cloud-disposed` | M05 | append | **203 distinct refs, 210 lines; 199 last-owed at the disposed sha, 3 moved**; the tick never opens it |
| plan ref | M06 and M07 | **none** | read-then-write; loser's push rejected, retried by the beat |
| roster branch | M32 | **none** | full-file dump; a lost update is possible |
| `state/pr/upd-<branch>` | M22 | flock (75 BUSY) | correct |
| gate lease / slots | M27/M28 | flock + expiry | **a live holder's slot is stolen at expiry** (E6) |
| train | M15/M16 | pidfile per state dir | two trains on two state dirs both merge; the API's `--match-head-commit` is the real serialiser |
| `~/.zcode/bus` | M12/M13 | none | `confirm` is a read-then-write on `posted` |
| `#201` body region | M48 | a concurrency group, cancel-in-progress | newer supersedes; a body write from another job (the orchestrator's) can interleave |

### 3.3 Races constructed, and the correction to revision 1

1. **Two tick loops.** `grep '^===== daemonize' …/loop.log` finds six launches of
   one logical loop (18:11:31Z, 18:15:36Z, 06:54:19Z, 09:37:39Z, 09:38:06Z,
   10:11:16Z). The 09:37:39/09:38:06 pair is 27 s apart under a 300 s interval:
   two loops live at once, each running the relay arm and writing the same board.
   The sweep's step 5 starts a *new tick seat* when `alive` is stale; the running
   thing is `tick_loop.sh`, which never writes `alive`.
2. **The tick's OWED fold never opens the disposal file.** Real `Tick.relay_owed`
   on a four-line fixture (E3): a `handoff-no-pr` and a `probe-ref` OWED line both
   survive a disposal recorded in `cloud-disposed`; only the `OWED <utc> <pr>`
   grammar cancels against a `POSTED`. **Correction to revision 1:** the claim
   that "201 disposed refs were re-owed at a different sha" compared ref *names*,
   not shas, and is false. The sha-aware comparison (E2) gives **199 of 202
   comparable disposed refs at exactly their disposed sha, 3 moved** (the plan
   ref, the roster and `r10-ci-layout-p0` — the branches that move), and one
   disposed ref with no OWED line in this log. The ledger is still required for
   the reason that survives repro: **the tick never opens `cloud-disposed` at
   all**, so the 203 disposals it holds silence nothing, and the board prints
   29,976 lines over 229 subjects.
3. **A live heavy-slot holder is stealable.** E6: holder A takes the only slot
   with a 1 s lease and names a live process; after expiry B takes the slot while
   A is alive. Live context: five `prepr.sh` runs at 18:40–36:50 elapsed when
   re-read at 12:20Z; the lease is 1800 s and never renewed.
4. **The relay reports success on total failure.** E4: `cloud_relay.sh pass` with
   no remote exits **0** while both reads print `fatal:`; the live log has the
   same shape at 09:37:39Z beside two `xcrun` failures, then `relay=ok tick=0`.
5. **An unleased state-ref write is real but was not constructed** — it would write
   the live plan ref. It is answered by compare-and-swap (§6.6).

### 3.4 The cadence the tick achieves

`grep -c '^TICK-PASS' loop.log` → 144 passes over 17.5 h = **8.2 passes/h**;
median gap 399 s, max 2,654 s; 5 of 143 gaps over 600 s; derived pass duration
(gap − 300 s) peaks at **2,354 s**. The period is `pass duration + 300`, and the
pass duration is dominated by M03's inline `update_pr.sh`: a writer runs inside
the reader's loop.

---

## 4. The observed slips

Each entry: (i) what was measured, (ii) the mechanism that should have caught it,
(iii) why not, (iv) the process state from `defect-root-cause.md`.

### S1 — a 3.9 MB board and a 30,014-line dispatch list

**Measured.** `wc -c -l tick.txt` → 3,901,380 bytes, 30,079 lines; last line
`DISPATCH LIST: 30014 finding(s)`; `grep -c '^-> OWED:'` → 29,976 over **229
distinct subjects** (130.9×); the log is 29,976 lines / 3,622,919 bytes, ~1,860
OWED lines/h. Correction to revision 1: the disposal is not 201-for-1 stale; the
sha-aware figure is 199/202 at the same sha and 3 moved (E2). The surviving
defect is that `relay_owed` keys on `f[2]` — the PR for the verdict grammar, the
literal kind token for the others — and **never opens `cloud-disposed`**, so 203
disposals silence nothing.

**Should have caught it.** The tick's own OWED reader; its self-test's null
control ("an OWED followed by a POSTED prints nothing").

**Why not.** The self-test fixture uses only the one grammar that works; the log
carries four. The test pinned one shape.

**Process state: (c)** — followed, wrong result: a level derived from an
append-only history.

### S2 — roster `resume.stage` drifts silently

**Measured at 12:20Z.** 93 groups, 47 open. With the matching rule **stated and
applied** — topic is the basename of `resume.branch` (else the lowercased group
id), a ref matches when its name, minus the `handoff-body/`/`handoff/`/`fix/`
prefix and a trailing `-pr`, equals the topic or starts with `<topic>-` — the
mismatches are **10** (E8): four `not-started` with refs in flight
(`R10-SENSOR-PAYLOAD`, `R10-I5-DOCS`, `R10-RCA-FRICTION`, `R10-CI-LAYOUT` — the
last matched through the `-p0` suffix, which revision 1's rule did not state) and
six `in-progress`/`queued` with no artifact. `R10-I5-DOCS` was `not-started`
while an `open_pr.sh` for it ran 11:33–11:50Z and the tick said "start a fixer".
`R10-UPDATE-PR-SIGNALS` is `queued` and the tick prints "in progress
(stage queued)". **Correction to revision 1:** the eight 12-hex `resume.commit`
values are not "invalid". Seven resolve uniquely and are ancestors of
`origin/main`; only `c35302773738` does not resolve here (E8c). The record is
right and the *length test* (`len(sha)==40`) is wrong.

**Should have caught it.** A reconciler; §5b of `orchestrator.md` tells a human
to read the ref, not the record.

**Why not.** `resume.stage` is free text; nothing compares it with refs/PRs. R10-
ROSTER-OPS's brief now requires `roster_sync.py --apply` to derive the factual
half (§6.4) — revision 1 proposed a second reconciler beside it, which is the
same defect one level up.

**Process state: (a)** for the machine; **(b)** for the prose rule.

### S3 — the owner-gate age check

**Measured.** 14 open groups carry `owner_gate`; the board prints "14 group(s)
blocked on owner disposition". The mandate's published text (`#201` comment
6175172275) reads: *"agents may approve as tvofi, scope `all` … covers codeowner,
policy and budget-raise approvals"*. **Correction to revision 1:** under the
design's own predicate (is the gate's class covered by the in-force mandate?) the
answer is **14 ready / 0 owner**, not 10/4. Revision 1's 10/4 asked whether the
gate's *free text* named the mandate — S3's defect in a new form.

**Should have caught it.** The owner-gate check.

**Why not.** Truthiness on free text, and the mandate read in another section
never joined to it.

**Process state: (c)**.

### S4 — seats stop writing while the harness calls them running

**Measured.** `SEATS.md` (209 KB, last written 07:12Z) carries
`LIVE(8): tick, vent, savbase, sensorpay, pump, refpriv, review-leaf, review-2345`
at line 162; the box has one harness tree and no process for those seats. The
liveness file `tick/alive` has **no writer process** and no scheduled task, yet
moves (E9).

**Should have caught it.** A liveness contract the tree can read.

**Why not.** The only signal is written by a brief, and it describes the tick, not
the seats. `orchestrator_tick.py` *already has* the right mechanism — a WORKERS
section that judges a seat from its work (PR head moved, CI completed since
dispatch, stall window) — but its input is the orchestrator's prose ledger and no
`workers.json` is kept. `beatd`'s journal reports jobs, not seats; revision 1
conflated them.

**Process state: (a)** for the tree; **(c)** for the harness.

### S5 — instruments dead after a session crash, restarted by hand

**Measured.** Six `daemonize` launches of one loop; each relaunch a human act.
`daemonize.py` keeps no bookkeeping by design.

**Should have caught it.** A supervisor with a schedule.

**Why not.** None exists.

**Process state: (a)**.

### S6 — `/usr/bin/git` broke, and every instrument depended on it silently

**Measured live.** At 09:37:39Z the log carries two `xcrun: error: invalid active
developer path …` lines and two "will retry" lines, then `relay=ok tick=0`. The
binary works now. Nothing hardcodes `/usr/bin/git`; the dependency is `git` on
`PATH`.

**Should have caught it.** The relay pass's rc.

**Why not.** Both arms `return 0` on an unreadable remote; `tick_loop.sh` maps rc
0 to `relay=ok`. The check existed and was written to fail open.

**Process state: (c)**.

### S7 — `update_pr.sh` starved in prepr, no timeout, no progress signal

**Measured.** Two chains ran 15+ minutes, shells at ~0.1 s CPU, step lines only,
then both logged `Terminated: 15` at 11:50:33Z. At 12:20Z five `prepr.sh` runs
were live at 18:40–36:50 elapsed. No `timeout` in the chain.

**Should have caught it.** A per-step timeout and a progress line; or the slot
lease as a cap.

**Why not.** No timeout anywhere; the slot is never renewed and is stolen at
expiry from a live holder (E6), so the cap is a time limit rather than a
concurrency limit.

**Process state: (a)** for the timeout; **(c)** for the lease.

### S8 — the plan page: a scratch instrument carrying constants

**Measured.** At `gen.py` (md5 `446ce441…`, mtime 13:54Z, unchanged since; **being
edited live by the orchestrator**): a hardcoded `groups["R10-ARCH-DOCS"]` override
is **present**; the scratch `REPLAN-EDGES.json` preference is **removed** (a
comment says "used to … One source: the roster"); the open-issue count is
**corrected** (`--state open` minus `#201`); the PR cell no longer prints
`#<commit8>`; the "folded" status is **partial** (the status text says folded, the
pill class is still `done`). The two `.bak` files retain the pre-fix shapes
(`EDGES = json.load(REPLAN-EDGES.json)`, `open_iss = len(ISS) - 1`,
`pr=f"#{MERGED[g]}"`). **Correction to revision 1:** three of the five defects
were repaired *while revision 1 was reading the file*, so a self-test arm that
points at the live file cannot fail on them. The `.bak` files are the recovered
pre-fix source and the arms are built from fixtures (§6.7).

The engine-level defect stands: its dependency graph was a 2026-10-17 scratch
file naming 34 of 93 groups and differing from the roster's `after` for 27; the
publish path the sweep names does not exist; and it carries `LIVE`, `MERGED`,
`HOURS`, `WAVES.json` as constants.

**Should have caught it.** A self-test, or any reader comparing two figures.

**Why not.** It is scratch: no `--self-test`, no CI wiring, `tmp_paths.py` not run.

**Process state: (a)**.

### S8b — `done` means both "merged" and "absorbed"

`R10-CI-RATCHET-RED` is `stage: done`, `commit: null`, note "Folded into
R10-CI-LAYOUT PR 0". `DONE_STAGES` closes it, so its `after`-edges stop
constraining and nothing checks that the absorbing group carries them. `done`
does two jobs; the design adds `absorbed` with a verified edge closure (§6.4).

---

## 5. Demonstrations

Full commands and output in `EVIDENCE.md`; the shape here.

- **E2 — the disposal figure, sha-aware.** 203 distinct disposed refs (210 lines);
  199 last-owed at exactly the disposed sha; 3 moved (the plan ref, the roster,
  `r10-ci-layout-p0`); 1 disposed ref has no OWED line. Of 202 comparable, 199
  same. The reader-never-opens-disposal defect is reproduced separately (E3).
- **E3 — the OWED fold's blind grammar.** On a four-line fixture the verdict OWED
  cancels against its POSTED (null control) and the `handoff-no-pr` / `probe-ref`
  lines survive a disposal.
- **E4 — the relays' fail-open.** `cloud_relay.sh pass` with no remote → **rc 0**,
  two `fatal:`, two "will retry".
- **E5 — the tick's period.** 144 banners over 17.5 h; median 399 s, max 2,654 s;
  derived duration max 2,354 s.
- **E6 — a live slot holder is stolen at expiry.** A takes the only slot with a
  1 s lease and a live pid; B takes it after expiry; the null control blocks
  before expiry.
- **E7 — prepr starvation.** Step lines only; `Terminated: 15`; five live runs at
  18:40–36:50 elapsed at the re-read.
- **E8 — the roster.** 10 stage-vs-ref mismatches under the stated rule; 7 of 8
  short commits resolve uniquely and are ancestors of `main`, 1 unresolves; 14/0
  gate coverage under the mandate's text.
- **E9 — liveness.** No writer process, no scheduled task; the `LIVE(8)` line is
  at line 162, not the file's tail, and its mtime is 07:12Z.
- **E10 — the plan generator.** Current vs `.bak` per defect; the scratch edge
  file differs from the roster for 27 groups; the publish path does not exist.
- **E12 — the self-tests pass with the defects present.** 150/74/4 checks, 0
  failed.
- **E17 — the reconciler's owner.** R10-ROSTER-OPS's brief at `541868d6f` requires
  `roster_sync.py --apply` run by the beat; the file exists on no ref yet.

---

## 6. The design

### 6.1 Principles

1. **A level is a state, not a history.** An obligation is computed from the live
   world or stored as an entry with an identity and a state; an append-only log is
   a journal of events and is never a level.
2. **One owner per concern, one writer per fact.** Every stored fact has one
   instrument that writes it; every reader imports the schema.
3. **Fail closed at the adapter.** An adapter returns `UNREADABLE`; the runner
   fails the pass. No adapter returns success for a read it did not make.
4. **Bounded by construction.** Every job has a wall-clock timeout above its
   measured work; every output is one line per event or one level per pass; every
   list is capped and the cap reports itself.
5. **Crash recovery is state, not ritual.** A job's progress is a durable file
   whose absence means "not done"; the supervisor restarts it.
6. **The record is verified, not declared.** A claim is reconciled with refs and
   the API by the instrument that owns it.

### 6.2 One supervised beat (`beatd`)

`tools/audit/seat/beatd.py` (with `--self-test`) replaces the hand-launched
daemons and owns the schedule. Its **job table** is a tracked file beside it
(`beatd.jobs.json`), and **an unreadable or malformed table refuses to start**
(principle 3) rather than running zero jobs.

| job | interval | timeout | heartbeat | lock |
|---|---|---|---|---|
| `tick` | 300 s | 900 s (one full read measured ~4 min) | 60 s | one per job |
| `relay-probe` | 120 s | 120 s (**first cut**: the probe pass measured 0.78 s, a fixture relay ~6.5 s; see E21) | — | one per job |
| `handoff` | 120 s | **3600 s** (measured runs 18:40–36:50) | 60 s | one per job; `update_pr`'s per-branch flock still applies |
| `state-docs` | 300 s | 300 s | — | one per job |
| `sync` | 900 s | 600 s | — | one per job |
| `plan-page` | 300 s | 300 s | — | one per job |
| `seats` | 300 s | 120 s | — | one per job |

- **The relay's two arms are two jobs.** `relay-probe` never waits behind a
  handoff update; `handoff` owns the long work and its bound is above the measured
  maximum. One update per pass, so a queue of handoffs drains without one pass
  running for an hour.
- **The reader and the writer are separate.** `tick` never runs a writer.
- **`state-docs` runs the one-shot form**: `state_docs.py beat --once
  --tip-file … --push --mirror …` — one pass, the memo on disk, exits. Not the
  internal loop (whose 300 s sleep a 300 s timeout would kill every pass).
- **One line per job per pass, written by the runner**: `PASS <utc> <job>
  start= dur= outcome=ok|failed|timeout|unreadable lines=`, plus a 60 s
  `RUNNING <utc> <job> pid= elapsed= step=` while a job runs.
- **Liveness contract.** `beatd status [--json]` reports jobs. **Seats are a
  different object and get a different contract** (S4): `orchestrator_tick.py`'s
  existing WORKERS section is the seat checker, and its input becomes a
  machine-readable `workers.json` — `{seat, pr, head, dispatched_at, agent_kind}` —
  that the session's seat ledger is rendered from. The checker keeps the existing
  grammar: a seat with no PR after the stall window prints `<seat>: STALLED? …
  (Nh since dispatch)` and a PR whose head moved prints `<seat>: DONE? …`, exactly
  as `orchestrator_tick.py:one_worker` prints them today (no new token).
  The prose ledger stops being the source of truth.
- **Compatibility during migration**: `beatd` writes `tick/alive` on every `tick`
  pass, and the sweep template's step 5 is edited in the same pull request to read
  `beatd status` instead. Without both halves, a stale `alive` starts a second
  tick mechanism (the S5 double start, made permanent).

Cost: ~400 lines plus a job table, ~20 s/minute of overhead, one new tracked file,
no policy change to run it.

### 6.3 One obligations ledger

`tools/audit/seat/ledger.py` (with `--self-test`) is the one module. It has **two
stores and one derived fold**, all with one schema, and one writer per fact:

- **`dispositions.tsv`** — the durable record of *acts*: `<ref> <sha> <utc> <how>`.
  Written **only through `ledger.py`'s CLI** (called by `cloud_relay.sh dispose`
  and by `open_pr.sh`/`update_pr.sh` when they apply a handoff), so there is one
  writer module. This replaces `cloud-disposed`.
- **`events.tsv`** — append-only `open`/`close` for **event obligations**
  (`reviewer-fire`, `verdict-unposted`, `train-stop`), which cannot be recomputed.
- **The derived fold** — every **derived obligation** is computed each pass from
  the live world and never stored: `handoff-no-pr`, `handoff-update`, `probe-ref`,
  `stage-mismatch`, `absorb-edge-missing`, `record-owed`. It cannot leak, because
  it is not an accumulator.
- **One schema, one parser.** Two kinds of obligation, distinguished by how they
  close:

| kind | class | producer | closer / resolution predicate |
|---|---|---|---|
| `handoff-no-pr` | derived | handoff job | an open PR at the topic (the job sees it); or `open_pr.sh`/`update_pr.sh` applies the ref (a disposition); or **`subject-absent`** when the ref is gone from `origin` |
| `handoff-update` | derived | handoff job | a successful update removes the topic's entry from `handoff-failed.tsv`; a moved `handoff/<topic>` supersedes the entry (the next pass retries at the new sha); or `subject-absent`. Its `why` carries the relay's failure reason, including the two zero-live code paths (`approve-held-runs`, `dispatch`), which are reasons on this obligation, not kinds of their own |
| `probe-ref` | derived | probe job | `cloud_relay.sh dispose`; or `subject-absent` |
| `stage-mismatch` | derived | `roster_sync.py` | the predicate is false on a later pass (it is recomputed, not accumulated) |
| `absorb-edge-missing` | derived | `roster_sync.py` | the edges carry (recomputed) |
| `record-owed` | derived | record job | `record_row.py` lands the row (recomputed from the merge window) |
| `reviewer-fire` | event | handoff job | the orchestrator's dispatch, which writes the close in the same command |
| `verdict-unposted` | event | confirm arm | **`bus.sh confirm` success — the bus's own writer closes it** |
| `train-stop` | event | train | a later train at the same head passes the step; or the orchestrator's disposition |

- **No second store.** `relay-post` is dropped: `bus.sh confirm` already owns
  `posted`/`posted-signed` (546 lines) and is the `verdict-unposted` closer.
  **The relay stops appending OWED lines to `cloud-relay.log`**; the file is
  rotated once and kept read-only as history. The board's meaning changes from
  history to the open set — stated in `sweep_template.md` and `INSTRUMENTS.md`
  where the sweep reads it (N7).
- **State refs are not handoff branches.** `handoff/audit-r*-plan`,
  `handoff/audit-r*-roster` and `wip-sync/*` are exempt from `handoff-no-pr` by
  name, so the two long-lived state refs stop being permanent obligations.
- **`subject-absent`** closes any obligation whose subject no longer exists on
  `origin`; at the re-read, 13 of 26 never-disposed subjects are already gone (E19).
- **The import** is one-time and idempotent: 210 lines → **203 distinct refs**,
  taking the **last disposition per ref** (7 repeated ref entries: one exact
  duplicate line and six same-ref-different-sha re-disposals, which are the
  relay's legitimate move rule; deduping lines would be wrong). The kind is
  inferred by prefix with **three arms**: `refs/heads/probe/` → `probe-ref`;
  `refs/heads/handoff/` **and `refs/heads/handoff-body/`** → `handoff-no-pr` (the
  relay's own kind already spans both — 113 and 89 refs respectively); the one
  `probe` ref is `probe-ref`. Each is closed at its **current** sha. A ref whose
  prefix matches no arm is refused and reported, not guessed. **The relay's OWED
  vocabulary is closed**: its five shapes map to the five kinds above, and an OWED
  shape with no ledger kind is a refusal — so the day a new shape is added, the
  relay stops rather than writing an obligation nothing reads.
- **Unreadable contract** (B11): a *missing* store is "first run" (the current
  `FileNotFoundError` branch), an **unreadable** store is `UNREADABLE` and the
  pass fails; neither prints a clean board.

Cost: ~300 lines, two state files, a 203-entry import; the tick's OWED section
shrinks from a 3.9 MB/pass log read to a fold over 229 live subjects and 203
dispositions.

### 6.4 The record verifier: R10-ROSTER-OPS owns it

**Decision (B4).** R10-ROSTER-OPS's brief, added at roster commit `541868d6f`
("roster_edit edit-brief R10-ROSTER-OPS"), already requires
`roster_sync.py --apply` run by `state_docs.py beat`, deriving `resume.stage` from
a MERGED or OPEN PR on `resume.branch` and writing through `roster_edit.py`'s
lint gate. **That instrument is the reconciler. This design does not add a
second one.** It contributes three predicates, to be added to that brief by the
orchestrator (a roster edit, not this design's to land):

1. **Gate coverage.** `owner_gate` becomes structured
   `{class: code-owned|policy|budget|mandate, mandate: <id|null>, paths: [...]}`.
   The predicate is **class × mandate coverage**: parse the in-force mandate's
   scope and map each class to the scopes that cover it, at
   `tools/policy/budget_raise_gate.py`'s own grammar
   (`MANDATE_GRAMMAR`, `scope (code-owned|budget-raise|all)`):
   `code-owned` ← `code-owned|all`; `budget` ← `budget-raise|all`
   (`MANDATE_COVERS_RAISE`); **`policy` ← `all` only** (`MANDATE_COVERS_POLICY`,
   the file's own ruling that neither `code-owned` nor `budget-raise` licenses
   landing a policy head). `GATE-READY` when the class is covered,
   `GATE-OWNER <class>` when it is not. With the only live mandate at scope `all`
   the answer is **14 ready / 0 owner** — revision 1's 10/4 was wrong (B2).
2. **Absorbed-edge closure.** `resume.stage: "absorbed"` with `absorbed_into:
   <group>` joins `DONE_STAGES` **only when every `after` edge of the absorbed
   group is present on the absorbing group or in its transitive closure**;
   otherwise `ABSORB-EDGE-MISSING` and the stage stays open (B9). A slip recorded
   as absorbed is not a slip lost.
3. **Commit resolution.** A `resume.commit` is resolved by prefix
   (`git rev-parse --disambiguate`): unique and an ancestor of `origin/main` is
   fine; ambiguous or unresolvable is `RECORD-INVALID <group> <why>`. The length
   test is removed (B3): seven of the eight short values are valid.

**The stage-matching rule** (B13) is stated above (topic from `resume.branch`,
match `<topic>` or `<topic>-*`); at the re-read it gives **10** mismatches, a set
that moves as seats work.

**Unreadable** (B11): an unreadable `ls-remote` or PR list prints `UNREADABLE` and
the pass fails; it never prints "no mismatches".

**Seam.** R10-ROSTER-OPS supplies the instrument, the write and the lint gate; this
design supplies the three predicates and consumes the resulting `resume.stage`
in the tick's PLAN section and the plan page.

### 6.5 Fail-closed adapters

- `cloud_relay.sh`: every `ls-remote`/`gh` failure returns non-zero with the
  failing read named; `pass` returns the worst rc of its arms. `tick_loop.sh`
  prints `relay=unreadable`; `beatd` records `outcome=unreadable`.
- The **new readers** (B11): `ledger.py` (missing vs unreadable as above);
  `roster_sync.py` (unreadable read → UNREADABLE); `beatd`'s job table
  (unreadable → refuse to start).
- `state_docs.py`, `bus.sh watch`, `policy_reread_check.py` already fail closed and
  are the model.
- The rule is one helper, not a convention.

### 6.6 Lock classes

1. **Exclusive** — machine measurements (`stress.py`, `harness_headers.py`): M27,
   renewed while held.
2. **Pool** — heavy work (`prepr`, `derive_closures`): M28 with **renewal while
   held** and **no steal of a slot whose named pid is alive** (E6); the lease is
   `job timeout + 60 s`.
3. **Per-subject** — read-then-write on a shared ref or branch: `update_pr.sh`'s
   flock is the model (M22). Extend it to `roster_edit`/`roster_sync` (the roster
   branch), to `state_docs`/`plan-page` (the plan ref, via
   `git push --force-with-lease=<ref>:<tip>` as compare-and-swap), and to
   `open_pr` (the per-topic worktree). **The loser re-derives and retries; it
   never retries a stale commit.** This is a seat-visible behaviour and is in the
   policy list (§8).

### 6.7 The plan page in the tree

**Where.** `tools/audit/seat/plan_page.py`, sharing **one model builder** with
`plan_table.py`: the roster walk already lives in `roster_lib.py`; a small
`plan_model()` adds the live facts (open PRs by branch, merged PRs, the open
issues, the obligations fold). Two renderers, one model.

**What the beat calls.** The `plan-page` job (300 s, timeout 300 s) after
`state-docs`; it regenerates only when an input moved (roster tip, open-PR set,
merged set, issue count), the memo discipline M06 uses.

**What it publishes.** One page at the **plan ref**:
`handoff/round<N>/state/PLAN.html`, in `state_docs.py`'s write set, pushed by the
same commit as `PLAN-TABLE.md` and mirrored to `~/hpo-orch/state/PLAN.html`. One
artifact, one durable path.

**How it fails.** An unreadable roster or API renders `<h1>PLAN UNAVAILABLE —
<what could not be read></h1>`, every figure `—`, no table; it exits 1 and the
beat records `outcome=unreadable`; the last good page is left at the ref with its
timestamp. Never a page of zeros.

**Generalization.** Round from the roster path, repo from `--repo`, every figure
derived: status from `resume.stage` plus the reconciler's output; edges from the
roster's `after`; open issues from `gh issue list --state open` **excluding PRs**
(an endpoint, not a subtraction); PR numbers from the PR API; ETA only where the
roster has a size; commit SHAs rendered as SHAs, never `#`.

**Self-test: mutation pins built from fixtures, not from the live file (B12).**
Three of the five defects were repaired in the live generator while revision 1 was
reading it, so each arm carries the **pre-fix expression as a fixture** and a
**mutant renderer line**; the arm passes on the corrected renderer and fails on
the mutant. Provenance: defects 2, 3 and 4 are recovered from `gen.py.bak` at
lines 4, 148 and 89; **defect 1's pre-fix expression is in the live file as
`groups["R10-ARCH-DOCS"] = {… "stage": "not-started"}`, and the fixture
reproduces that shape** (a hardcoded override whose stage contradicts the
roster's), not an invented "in-review" hint; defect 5 is partial (status text
folded, pill class `done`).

| arm | fixture | mutant that must fail the arm |
|---|---|---|
| 1 hardcoded override | a roster saying the group `done`, plus the live pre-fix shape `groups[...] = {… "stage": "not-started"}` | re-add that override before the walk |
| 2 graph from scratch | a roster `after` plus a fixture "scratch edges" file that differs | prefer the scratch file (`EDGES.get(g, …)`) |
| 3 count from the wrong set | an issue list containing PRs and closed issues | `len(all_issues) - 1` |
| 4 commit prefix as PR | a done group with a `resume.commit`, no merge | render `f"#{commit8}"` |
| 5 two statuses | a group with `stage: absorbed`, `absorbed_into` | map absorbed to `done` and render "delivered" |

Plus a null control: an all-done roster renders no open rows and the true totals.

**Seam with R10-ROSTER-OPS.** `roster_edit.py` has no `set-after` op
(`choices=("set-stage","wire-issue","unwire-issue","append-group","edit-brief",
"append-carry","set-resume")`); R10-ROSTER-OPS owns adding it and the `absorbed`
fields. This design consumes them.

### 6.8 Cost

| element | seconds per pass | lines | policy (see §8) |
|---|---|---|---|
| `beatd` + job table | ~20 | ~400 | none to run |
| obligations ledger + import | ~5 | ~300 | none |
| three predicates in `roster_sync` | ~30 | ~120 | B4/B14(i): that brief's vocabulary |
| fail-closed adapters | 0 | ~80 | B14(iv): every caller's rc contract |
| slot renewal + no-steal-live | 0 | ~40 | none |
| plan page in the tree | ~2 on a moved input | ~400 | B14(ii): the plan path moves |
| new-file CI wiring (N5) | — | 3 `run:` lines + `INSTRUMENTS.md` entries | B5: R10-CI-LAYOUT's files |
| **net** | **~55 s per 5 min** | **~1,340** | **eight proposals (§8 rows i–viii; `grep -c '^\| [ivx]* \| '` → 8)** |

The board alone rewrites **3.9 MB × 8.2 passes/h ≈ 32 MB/h ≈ 0.77 GB/day**; the
ledger replaces it with a fold over 229 subjects and 203 dispositions.

---

## 7. Rejected alternatives

1. **Fix each slip in place.** Rejected: five of the eight share three causes (a
   level from history; liveness by memory; fail-open adapters); the next grammar,
   adapter and brief remain.
2. **Move everything into CI.** Rejected: the gate lease, the App identity, the
   per-branch lock and the train are local; CI cannot hold this box's flock or
   push with the same review semantics, and its cadence is minutes-to-hours. CI
   already owns record generation (M11, M47/M48) and stays there.
3. **A monolith.** Rejected: it concentrates write authority, cannot be tested
   piecewise, and collapses the role separation.
4. **Webhooks.** Rejected: no inbound endpoint, an extra credential surface, and
   identity 0011 forbids the extra writer.
5. **Make the tick a seat.** Rejected: background tasks die at 2 h and the
   harness's liveness is not tree-readable.
6. **A database.** Rejected: state must be readable by `git` alone.

---

## 8. Migration, seams, and policy

Each phase is one tree PR with its self-test failing on the defect it answers
(`defect-root-cause.md`); each is independently runnable.

**Phase 0 — no policy change.**
1. `relay_owed` reads the disposal state and keys on `(kind, subject, sha)`; the
   self-test gains the three missing grammars. *Fails on the board (E2/E3).*
2. `cloud_relay.sh pass` returns non-zero on an unreadable remote; callers report
   it. *Fails on E4.* **This changes every caller's rc contract — policy (§8
   table, row iv).**
3. `tick_loop.sh` takes a `flock` on its board; `beatd` (or, before it, the loop)
   writes `alive`. *Fails on the double start (E4).*
4. `gate_lock.py`: renew a slot while held and never steal a live holder. *Fails
   on E6.*
5. `prepr.sh` gains `timeout` per step and a 60 s `RUNNING` line. *Fails on E7.*

**Phase 1 — the ledger and the beat.** `ledger.py` (two stores, derived fold) and
the `cloud-disposed` import; the relay's OWED log writes retired; `beatd` with the
seven jobs; the sweep template's step 5 edited to read `beatd status`, and
`alive` written by `beatd` until the edit is in every rendered sweep. Retire the
three hand-launched daemons in one switch. *(B8: both halves in one PR, or the
sweep starts a second tick.)*

**Phase 2 — the record verifier.** R10-ROSTER-OPS lands `roster_sync.py --apply`
(its brief's requirement); the orchestrator appends the three predicates above to
that brief; the tick's PLAN section consumes the result. This design adds no
instrument and no op here. **Owner approval** for the roster schema additions
(`owner_gate` structure, `absorbed`, `absorbed_into`).

**Phase 3 — the plan page.** `plan_page.py` sharing `plan_model()` with
`plan_table.py`, in `state_docs.py`'s write set, published at the plan ref and the
mirror. **CI wiring is R10-CI-LAYOUT's** (B5): `beatd.py`, `ledger.py` and
`plan_page.py` each carry `--self-test`, so `selftest_wiring.py --check`
(37/37 wired today) refuses them unwired, and the `run:` lines live in
`tests.yml`/`governance.yml`/`ci.yml` — the three files R10-CI-LAYOUT's four PRs
edit, one of which re-records `script_runs_per_push`. **Ordering:** each
instrument lands **with its wiring**, after R10-CI-LAYOUT's last PR or as a
listed file in it; an instrument cannot land earlier and stay unwired, because
`instrument-self-tests` is a required check and a merge that reddens it cannot
land. *(B5, N5.)*

**Overlap and retirement (N4).** During the overlap the plan of record is the plan
ref (`PLAN.html`); the scratch generator is run only to compare, never published.
It is retired when **two consecutive merges to `main`** have produced
`handoff/round<N>/state/PLAN.html` at the ref (observable with `git show` at each
merge) and the sweep's overlay names the ref path. The first of those merges sets
the read path for every brief; the second retires the scratch generator and its
`.bak` files.

**Policy changes proposed, not landed.** Each states the process state it answers
and needs the owner's approval before merge (CLAUDE.md: a change to what a seat
must do is policy).

| # | proposal | files | state answered |
|---|---|---|---|
| i | a periodic tree instrument requires a wall-clock timeout, a single-instance lock and a level line; the `STAGE-MISMATCH`/`GATE-READY`/`RECORD-INVALID`/`ABSORB-EDGE-MISSING` vocabulary a seat acts on | `INSTRUMENTS.md`, `orchestrator.md` §13, R10-ROSTER-OPS's brief | (a) |
| ii | the plan of record moves to `handoff/round<N>/state/PLAN.html` and the mirror; every brief and the sweep name that path | `sweep_template.md`, briefs naming the plan | (a) |
| iii | lock-contention behaviour: the loser of a roster/plan-ref/`open_pr` race re-derives; it does not retry a stale commit | `INSTRUMENTS.md`, `orchestrator.md` | (c) |
| iv | `cloud_relay.sh pass` returns non-zero on an unreadable read; every caller's rc contract changes | `INSTRUMENTS.md`, the sweep, `tick_loop.sh` callers | (c) |
| v | liveness is written by the instrument that runs, never by a brief; the seat ledger is a rendered `workers.json` | `orchestrator.md` §13, `INSTRUMENTS.md` | (a) |
| vi | the obligations ledger is the single source for OWED; no instrument prints a level from an event log | `orchestrator.md` §8/§12 | (c) |
| vii | `owner_gate` is structured and "blocked on owner disposition" means no in-force mandate covers it | roster schema (`roster_edit.py`, `roster_lib.py`) | (c) |
| viii | a roster group is `absorbed` (into another), never `done`, when it has no merge of its own, and only with the edge closure | roster schema | (c) |

---

## 9. What I could not establish

- What sent SIGTERM to the two `open_pr.sh` chains at 11:50:33Z; the shape is
  recorded, the sender is not.
- The harness's own view of a seat's state; S4's harness half is inference from
  the ledger/process mismatch.
- The exact prepr step running at the kill (completed steps are logged).
- Whether the plan ref's unleased writers have collided; constructing it writes
  the live plan ref.
- The live `gen.py` beyond 13:54Z; it is being edited by the orchestrator while
  read. The design does not depend on a line of it.
- The exact mismatch set at any single instant: live state moves (10 at 12:20Z;
  the review measured a different set).
- `c35302773738` (R10-TICK-SELFTEST-CI's short commit) — it may exist on an
  unfetched ref; it does not resolve in this clone.

---

## 10. Corrections to revision 1

| revision 1 said | what is true | source |
|---|---|---|
| "201 re-owed at a different sha" | 199 of 202 comparable at the same sha; 3 moved. The ledger is required because the tick never opens the disposal file | E2 |
| the owner gates "become 10 ready and 4 owner" | 14 ready, 0 owner under the mandate's text (scope all; codeowner, policy, budget-raise) | E18 |
| eight short `resume.commit` values are `RECORD-INVALID` | seven resolve uniquely and are ancestors of `main`; one unresolves; the length test is the defect | E8c |
| "Seam: R10-ROSTER-OPS supplies ops; this design supplies the reconciler" | R10-ROSTER-OPS's brief owns `roster_sync.py --apply`; this design adds no second reconciler, only three predicates | E17 |
| "Seam: none with R10-CI-LAYOUT" | the three new self-tests must be wired into `tests.yml`/`governance.yml`/`ci.yml`, which are R10-CI-LAYOUT's files | E16 |
| `beatd status` answers S4 | it reports jobs; seats are the tick's WORKERS contract over a `workers.json` | E9 |
| relay job timeout 600 s | below measured work (18:40–36:50); the handoff job is bounded at 3600 s, separate from the probe | E7 |
| the migration keeps the sweep working | it must write `alive` and edit the sweep in the same PR | E9, sweep template |
| `absorbed` verifies the destination exists | it must verify the absorbing group carries the absorbed group's `after` edges | E8 |
| every kind has a closer | kinds are split derived/event, each with a closer; `subject-absent` closes a vanished subject; state refs are exempt | E19 |
| `relay-post` is a ledger kind | dropped; `bus.sh confirm` is the closer for `verdict-unposted` | E14 |
| the ledger and reconciler need no unreadable rule | both, and the job table, fail closed | E11 |
| the five plan-page defects are present at `gen.py` | 2, 3 and 4 were repaired live; arms are mutation pins over fixtures | E10 |
| the stage rule matched the nine | the stated rule (topic-suffix) gives 10; revision 1 used a prefix it did not state | E8 |
| §6.8 "policy lines 0" | eight proposals in §8; four further seat-visible effects named | §8 |
| 53 entries, 38 self-test files | **52 tracked entries** (a live `ls` returns 53 because of an ignored `__pycache__/`), 37 self-testing scripts | E1 |
| `#201` has one writer | `delivery-status-publish` rewrites a body region; `tests/delivery_status.py` builds the ledger; four mechanisms were missing | E14 |

---

## 11. Corrections in revision 3 (round-2 review, `46cd9d44`)

The structure and the row count are unchanged; two ledger clauses and nine
figures were wrong.

| round-2 item | correction | evidence |
|---|---|---|
| B10-R import refuses 89 refs | the import has **three** classification arms: `probe/` → `probe-ref`; `handoff/` **and `handoff-body/`** → `handoff-no-pr` (113 + 89 + 1 = 203 refs, last disposition per ref) | E20 |
| B10-R a live kind is missing | **`handoff-update`** is a derived kind (10 live lines), state `handoff-failed.tsv`, closed by a successful update, superseded by a moved ref; `approve-held-runs` and `dispatch` are its reasons; a relay OWED shape with no ledger kind is a refusal | E20 |
| N1-R "53 entries" | **52 tracked entries**; `ls`'s 53 is an ignored `__pycache__/`; no tree file changed between revisions | E1 |
| N2-R the combined grep | the precise pattern `grep -c 'cloud-disposed'` → **0**; the looser `disposed` matches one docstring word | E2 |
| N3-R four exact mandate strings | **six** carry the exact string; ten name the mandate; 14/0 unaffected | E8b |
| N4-R "7 duplicate lines" | 210 lines, 203 refs, **209 distinct lines**: seven repeated ref entries, one an exact duplicate; the import takes the last disposition per ref | E2, E20 |
| N5-R five proposals | **eight** (§8 rows i–viii), derived with `grep -c '^\| [ivx]* \| '` → 8 | §6.8 |
| N6-R land earlier and stay red | struck: an instrument lands **with its wiring**; a required check cannot be merged red | §8 Phase 3 |
| N7-R `SEAT-STALLED` | the existing grammar: `<seat>: STALLED? …` / `<seat>: DONE? …`, as `one_worker` prints | §6.2 |
| N8-R arm 1's fixture | the fixture reproduces the live pre-fix shape `groups[...] = {… "stage": "not-started"}`, not an invented hint; provenance of the other three is `gen.py.bak:4,148,89` | §6.7 |
| N9-R relay-probe bound unmeasured | marked a **first cut** with its anchors: probe pass 0.99 s at load1 50; a relay fixture ~7 s (74 checks in 56.5 s) | E21 |
| N10-R class → scope unstated | stated from `budget_raise_gate.py`: `code-owned` ← `code-owned\|all`; `budget` ← `budget-raise\|all`; `policy` ← `all` only | E22 |
