# The orchestration machinery: inventory, timing model, and an improved structure

Design / pre-study seat, round 10, 2026-10-20. Repository `tvofi/heatpump_optimizer`.
Read from the worktree at `origin/main` `a2b25bbc5` (the live instruments run from
`~/hpo-seats/r10s3/orch-wt`, a separate checkout; tree paths below are repo-relative
and identical at that head unless a row says otherwise). Live state read between
2026-10-20T11:38Z and T11:56Z, `load1` 42.9–82.6 on 8 cores
(`sysctl -n hw.ncpu`; `uptime`). Every figure names the command that produced it;
the commands and their raw output are in `EVIDENCE.md`, and host paths are written
`~` there and here.

This is not a bug list. It is a structure, and the evidence that motivates each
element.

---

## 1. Method and what was measured

- Inventory from the tree and the live processes, never from a document's account.
  `tools/audit/seat/*` was read at the worktree head; the running processes were read
  with `ps -o pid,ppid,etime,time,stat,command` and `lsof -p`; the state surfaces
  (`~/.local/state/hpo`, `~/hpo-orch/r10s3/orch`, `~/.zcode/bus`, the plan ref, the
  roster ref) were read with `wc`, `grep`, `awk` and `git ls-remote`.
- **No running instrument was stopped, restarted or edited.** The perturbations in
  §3 and §5 run in throwaway directories under the seat scratch with
  `HPO_STATE_DIR`/`HPO_GATE_LOCK_DIR` pointed at them.
- Wall-clock is always reported beside `load1`; most of this box's timings are
  load-dominated, so counts and structural facts carry the claims.
- The tree carries 53 entries in `tools/audit/seat/`, 38 with a `--self-test`, and
  22,793 lines across them (`ls tools/audit/seat | wc -l`;
  `grep -l -- '--self-test' tools/audit/seat/* | wc -l`;
  `wc -l tools/audit/seat/* tools/audit/seat/*.md | tail -1`).

### 1.1 The inventory's row count

The inventory is §2's table. It has **46 rows**, derived from the file itself:

    grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md      # 46
    grep -o '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md |
      sed 's/^| M//' | sort -n | awk 'NR != $1 { print "gap at", $1; bad=1 } END { exit bad }'  # contiguous M01..M46

Composition rule, so the number is not arbitrary: one row per **mechanism the ask
names** (tick, relay, beat, sweep, record beat, bus, train, PR openers/updaters,
gate lease, `wt_sync`, `daemonize`, roster machinery), plus **every instrument that
produces, consumes or repairs one of the four state surfaces** the ask names (plan
ref, state mirror, `#201`, `dev/programme/delivery/`), plus the **out-of-tree plan
generator** the orchestrator added mid-task. Sub-generators are folded into the
instrument that runs them: `plan_table.py`, `resume_doc.py` and `handover_prompt.py`
are one row (M08) because `state_docs.py` is their only runner; `sweep_template.md`
and `sweep_render.py` are one row (M09). Pure libraries with no trigger
(`row_position.py`, `features_block.py`, `moved_paths.py`, `tmp_paths.py`,
`verify_eight.py`, `r10_deeplink_mutants.py`, `shims/`) are not mechanisms and are
excluded; they are counted here so the exclusion is auditable:
`ls tools/audit/seat | wc -l` is 53, and the difference from 46 is the folds and
the additions across `tests/`, the out-of-tree generator and the surfaces.

---

## 2. Inventory

Columns: **trigger / cadence / bound** (what starts it and every limit on how long
it runs); **reads → writes**; **L/E** level-triggered (repeats until disposed) or
edge-triggered (fires once per change); **on unreadable** (what it does when a read
fails); **stop / crash** (how it stops, and what survives a crash of the session
that started it). A `!` marks a row whose behaviour in that column is one of §4's
slips.

| ID | mechanism | trigger / cadence / bound | reads -> writes | L/E | on unreadable | stop / crash |
|---|---|---|---|---|---|---|
| M01 | `tick_loop.sh` | daemonized or a session; sleep 300 s + pass; **no bound on a pass** ! | tree scripts; `--out` board via `.part.$$`+`mv`; one `TICK-PASS` line | L | maps relay rc only; **a relay fail-open prints `relay=ok`** ! | kill the pid; no pidfile, so **two loops can coexist** ! |
| M02 | `orchestrator_tick.py` | run by M01; one full read per pass; **no timeout**; 67–84 API calls (its header) | gh API, git refs, roster ref, `cloud-relay.log`, `bus.sh orphans` -> stdout only | L | `UNREADABLE:` per section (fail closed) — except the OWED fold (M05) ! | parent dies; stateless |
| M03 | `cloud_relay.sh pass` — handoff arm | M01 every pass, or `--loop` 120 s; **no bound: runs `update_pr.sh`/`prepr.sh` inline** ! | open PRs, `handoff/*`, bus -> PR branches, `cloud-relay.log`, `cloud-handoff-failed` | L (OWED) + E (updates) | gh/ls-remote failure -> `return 0` "will retry" ! | parent; body dirs under the state dir always removed |
| M04 | `cloud_relay.sh pass` — probe + relay arm | same | `probe/*`, `cloud-relayed`, bus -> verdict refs, log | L (OWED) + E (relay once) | `return 0` on ls-remote failure ! | parent; ledger is durable |
| M05 | `cloud_relay.sh dispose` / `cloud-disposed` | human act | — -> append `<ref> <sha>` | L | n/a | append-only file |
| M06 | `state_docs.py beat` | daemonized; 300 s; no lock | `origin/main` + roster ref tips -> plan ref, mirror, `beat.tip` | L on a moved tip | **refuses, prints, retries** (fail closed) | tip recorded only on rc 0, so a refused push is retried |
| M07 | `state_docs.py` one-shot (`--push --mirror`) | sweep step 4 / post-merge | same surfaces | E | refuses | runs to completion or refuses |
| M08 | `plan_table.py` / `resume_doc.py` / `handover_prompt.py` | called by M06/M07 | roster (+ live PR state) -> three docs | E | generator exits non-zero | none |
| M09 | `sweep_template.md` + `sweep_render.py` | a harness timer or a human; session cadence; **no bound** | tree paths + session overlay -> a prompt | — (it is prose) | renderer refuses (fail closed) | none; the overlay is scratch and drifts ! |
| M10 | `policy_reread_check.py` | sweep step 0 | transcript + stamp -> OK/OWED, stamp | L | OWED on anything unreadable (fail closed) | stamp file is the state |
| M11 | `record_row.py` (the record beat) | **CI** (`tests.yml` record-autofix; `governance.yml` record), push/schedule/PR | REST merges, tree rows -> `dev/programme/delivery/<N>.md`, a `record:` PR | L (a rowless merge reddens) | refuses | CI; a refusal reddens the job |
| M12 | `bus.sh dispatch/push-verdict/confirm/post` | an orchestrator turn, a reviewer seat | bus state + `review/*` refs -> `verdict/*` refs, `posted` | E | refuses, pushes nothing | state is per-machine; refs are durable |
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
| M32 | `roster_edit.py` | an orchestrator turn | the roster branch -> a formatted dump | E | refuses on lint, unknown group, bad value | **no lock**; **no `set-after` op** ! |
| M33 | plan ref `handoff/audit-r<N>-plan` | written by M06/M07; read by seats | three state docs + evidence at the ref | E | the beat retries a rejected push | the ref is the durable record |
| M34 | state mirror `~/hpo-orch/state` | written by M06/M07 | the same three docs | E | n/a | a local copy; a stale copy is indistinguishable from current |
| M35 | `#201` | one comment per record act | — -> comments (1,875 today) | L in intent, **E in mechanism** | n/a | the issue is the durable record; **newest requires the last page** (the API ignores `sort`) |
| M36 | `dev/programme/delivery/<N>.md` | M11 and M21/M22 | tree -> 791 row files | L (the record job reddens) | n/a | rows are the durable record |
| M37 | out-of-tree plan generator (`~/hpo-orch/r10s3/plan/gen.py`) | sweep step 4 or a human; no self-test | a fetched roster, REST issues/PRs, **a 2026-10-17 scratch edge file** -> `round-10-plan.html` + scratch JSON | E | **writes a page regardless** ! | lives in scratch; its published copy is under a session temp root that no longer exists ! |
| M38 | `ci-watch.sh` | a watcher seat; loop | check-runs -> a per-PR signature file, stdout on a new signature | L in intent, **E by a signature file** | unreadable ruleset alerts BLIND once | dies with the seat |
| M39 | `ref_privacy.py` | before every push an instrument composes | ref name, message, commits -> allow/refuse | E | refuses | stateless |
| M40 | `body_push.sh` | a fixer handoff | `BODY.md` -> `handoff-body/<topic>` | E | refuses on a predicted red | parentless first commit, fast-forward after |
| M41 | `worktree_gc.sh` | after a merge | worktrees/branches/scratch -> deleted | E | `--dry-run` lists | stateless |
| M42 | `approve_held_runs.sh` | after every App push | Action runs -> approvals | E | a no-op is not an error | stateless |
| M43 | `pr_cap.py` | `open_pr.sh`; the tick | open PRs -> count, gate | L | an unreadable list refuses | stateless |
| M44 | `app_approve.sh` / `app_comment.sh` / `gh_comment.py` | an orchestrator turn | a verdict/comment -> an approval/comment, **read back** | E | refuses on a head or SHA mismatch; "posted" never from an exit code | stateless |
| M45 | `failure_logs.sh` | any red whose cause a state line does not carry | check-runs, job logs -> files, an exit code | E | NO-JOB / NO-LOG, never a silent zero | stateless |
| M46 | `prune_refs.py` | closure; dry-run by default | remote refs -> tags + deletions | E | refuses on `main`, on undrained verdict refs | tags before deletions |

### 2.1 What the inventory already shows

Two facts fall out of the columns before any slip analysis:

1. **Only five rows own any bound at all.** M06 (300 s sleep), M15/M16
   (poll counts, `--main-moved-tries`), M18 (`--budget`), M27 (1800 s lease),
   M28 (slot lease). Everything else that waits —
   M01, M03, M21, M25 — waits forever. There is no `timeout` call anywhere in
   `tools/pr/prepr.sh`, `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`
   (`grep -n timeout tools/pr/prepr.sh tools/audit/seat/{open_pr,update_pr}.sh` →
   no matches for a `timeout` command; every hit is the word in prose or a lane name).
2. **The state surfaces have writers with no lock and readers with no schema.**
   M32 (roster), M06/M07 (plan ref), M12 (bus) are read-then-write with no lease;
   M35 (`#201`) has one writer per turn but 1,875 entries and no key.

---

## 3. Timing graph and races

### 3.1 What runs on the box, and under what

Measured at 11:49Z (`ps -eo pid,ppid,etime,time,stat,command`):

- M01 `tick_loop.sh` pid 35000, **PPID 1**, elapsed 1:41, CPU 0:00 — a detached
  shell whose children do the work.
- M06 `state_docs.py beat` pid 35031, PPID 1, elapsed 1:31.
- M29 `wt_sync.sh` loop pid 35037, PPID 1, elapsed 1:34 (`while :; do …; sleep 900`).
- The harness: **one** live Claude process tree (pids 3928/3930). Every other
  shell on the box is a background child of it — the seat work escaped as shells.
- Three heavy slots held by `prepr.sh` (M28), and a `merge_train`-adjacent
  `mutation_table.py` set; `load1` 69.8.

The three daemons are **mutually unaware**. Nothing supervises them; each was
launched once by a `daemonize.py` call or a `nohup`, and each is identified only
by a pid that nothing records.

### 3.2 Concurrency and exclusivity

| resource | writers | exclusivity held | failure observed |
|---|---|---|---|
| `cloud-relay.log` | M03/M04 (any pass) | none (append) | grows ~1,860 OWED lines/h |
| `tick.txt` board | every live M01 | none (`.part.$$`+`mv`) | **two loops ran 27 s apart** (banners at 09:37:39Z and 09:38:06Z) |
| `cloud-disposed` | M05 | append | 210 entries; 201 re-owed at a new sha |
| plan ref | M06 and M07 | **none** | read-then-write; loser's push rejected, retried by the beat |
| roster branch | M32 | **none** | full-file dump; a lost update is possible, reported only by git |
| `state/pr/upd-<branch>` | M22 | flock (75 BUSY) | good: the one correct per-subject lock |
| gate lease / slots | M27/M28 | flock + expiry | **a live holder's slot is stolen at expiry** (demonstrated, §5) |
| train | M15/M16 | pidfile **per state dir** | two trains on two state dirs both merge; the API's `--match-head-commit` is the real serialiser |
| `~/.zcode/bus` | M12/M13 | none | `confirm` is a read-then-write on `posted` |

### 3.3 Races that can be constructed cheaply, and were

1. **Two tick loops.** `grep '^===== daemonize' ~/hpo-orch/r10s3/orch/tick/loop.log`
   finds **six launches of one logical loop**: 18:11:31Z, 18:15:36Z, 06:54:19Z,
   09:37:39Z, 09:38:06Z, 10:11:16Z. The 09:37:39 and 09:38:06 pair is 27 s apart —
   impossible for a loop whose interval is 300 s — so two loops were live at once,
   each running the relay arm and each writing the same board. The sweep's step 5
   starts a *new tick seat* when `alive` is stale; the running thing is
   `tick_loop.sh`, which never writes `alive`. Two mechanisms, one name.
2. **The tick's OWED fold cannot see disposal.** Demonstrated with the real
   `Tick.relay_owed` on a four-line fixture (§5, demonstration E3): a
   `handoff-no-pr` OWED line and a `probe-ref` OWED line both survive a disposal
   recorded in `cloud-disposed`; only the `OWED <utc> <pr>` grammar cancels against
   a `POSTED`.
3. **A live heavy-slot holder is stealable.** Demonstrated in a throwaway lock
   dir (E6): holder A takes the only slot with a 1 s lease and names a live
   process; after the lease expires, B takes the slot **while A's process is
   still alive**. At 1800 s against prepr runs observed at 15+ minutes each under
   `load1` 70+, a prepr that crosses 30 minutes stops being counted.
4. **The relay reports success on total failure.** Demonstrated (E4):
   `cloud_relay.sh pass` in a directory with no remote exits **0** while both
   remote reads print `fatal:` and "will retry". The live log has the same shape
   at 09:37:39Z: two `xcrun: error: invalid active developer path` lines, two
   "will retry" lines, then `TICK-PASS … relay=ok tick=0`.
5. **An unleased state-ref write is real but was not constructed**, because
   constructing it means writing the live plan ref. It is visible in the code
   (`state_docs.py` reads `remote_tip`, builds a commit, pushes; no lock) and in
   the design it is answered by compare-and-swap (§6.6).

### 3.4 The cadence the tick actually achieves

`grep -c '^TICK-PASS' loop.log` = 144 passes over the log's span
(2026-10-19T18:11:31Z → 2026-10-20T11:42:13Z ≈ 17.5 h) = **8.2 passes/h**, not the
12/h its `--interval 300` suggests. Gap statistics over consecutive banners:
median 399 s, max 2,654 s; 5 of 143 gaps exceed 600 s; the derived pass duration
(gap − 300 s) peaks at **2,354 s**. The tick's period is `pass duration + 300`,
and the pass duration is dominated by M03's inline `update_pr.sh`: **a writer runs
inside the reader's loop**. The 44-minute gap (08:53:44Z → 09:37:58Z) sits beside
the broken-git lines above; the 27-minute gap (10:35:52Z → 11:02:36Z) beside a
handoff update.

---

## 4. The observed slips: the mechanism that should have caught each, and why it did not

Each entry is (i) what was measured now, (ii) the mechanism that should have
caught it, (iii) why that mechanism did not, (iv) the process state from
`defect-root-cause.md` §"The process root cause".

### S1 — a 3.9 MB board and a 30,014-line dispatch list, from reprinted OWED lines

**Measured.** `wc -c -l ~/hpo-orch/r10s3/orch/tick/tick.txt` → 3,901,380 bytes,
30,079 lines; last line `DISPATCH LIST: 30014 finding(s)`. `grep -c '^-> OWED:'` →
**29,976**; `grep '^-> OWED:' … | sed -E 's/.* (refs\/heads\/[^ ]+).*/\1/' | sort -u | wc -l`
→ **229 distinct subjects**, a 130.9× amplification. The source log is
`wc -l ~/.local/state/hpo/cloud-relay.log` → 29,976 lines, 3,622,919 bytes; its
OWED lines by kind: 29,814 `handoff-no-pr`, 151 `probe-ref`, 10 `handoff-update`,
1 relay verdict. The relay appends the same OWED line every pass: per-hour counts
are 1,664–2,083 (`grep ' handoff-no-pr ' … | awk '{print substr($2,1,13)}' | sort | uniq -c`).
Those are level facts being written as events, and then re-read as a history.

**Should have caught it.** The tick's own OWED reader — its self-test has a null
control: "an OWED followed by a POSTED prints nothing".

**Why not.** `orchestrator_tick.py:relay_owed` keys the fold on `f[2]`. For the
relay-verdict grammar (`OWED <utc> <pr> <sha> <why>`, `POSTED <utc> <pr> <sha>`)
that is the PR number and the fold works. For `OWED <utc> handoff-no-pr <ref> <sha>`
and `OWED <utc> probe-ref <ref> <sha>`, `f[2]` is the **literal kind token**, and no
`POSTED` line is ever written for them, so every historical line is permanently
"owed". The disposal the producer *does* record (`cloud-disposed`, 210 entries) is
a different file the reader never opens. The self-test's fixture uses only the one
grammar that works, so the instrument's test says cancellation works while three
of four shapes cannot cancel. **The test pinned one grammar; the log carried four.**

Correction of the brief's figure: the dispatch list is 30,014 findings now, not
30,001; `cloud-relay.log` is 29,976 lines (was 29,741 when the brief was written)
and `cloud-disposed` holds 210 refs.

**Process state: (c)** — the process existed (a level line per OWED), was
followed, and produced an unintended result: the level was derived from an
append-only event log instead of from the producer's disposal state.

### S2 — roster `resume.stage` drifts silently

**Measured.** The roster at `origin/handoff/audit-r10-roster` has 93 groups, 47
open; stages `done` 46, `not-started` 36, `in-progress` 7, `queued` 4. Against the
remote refs:
- **R10-I5-DOCS** is `not-started`, while `handoff/r10-i5-docs` and
  `handoff-body/r10-i5-docs` exist **and an `open_pr.sh` for that topic was running
  from 11:33Z to its termination at 11:50Z** (`ps -o pid,etime,command`; the live
  board line `-> R10-I5-DOCS: UNBLOCKED, not started -- start a fixer on
  handoff/r10-i5-docs`). The record would have told the orchestrator to start a
  second fixer for work in flight.
- **R10-SENSOR-PAYLOAD** is `not-started` with both refs present; **R10-CI-LAYOUT**
  is `not-started` with `handoff/r10-ci-layout-p0` present.
- **R10-HANDOFF-ARCHIVE** and **R10-DEPENDABOT-AIOHTTP** are `in-progress` with
  **no ref naming them**.
- **R10-UPDATE-PR-SIGNALS** is `queued`, and the tick prints
  `R10-UPDATE-PR-SIGNALS: in progress (stage queued)` — the display folds
  `in-progress` and `queued` into "in progress".
- 36 open groups name a `resume.branch` the remote does not have; that one is
  expected (it is the branch a group will use), but **8 `resume.commit` values are
  12-hex abbreviations**, and the tick's `group-stale` check only tests
  `len(sha)==40`, so those eight can never be verified (the rest are 40-hex).

**Should have caught it.** A reconciler over the record, or the tick's PLAN
section. `orchestrator.md` §5b already *tells a human* to "read the ref, not the
record".

**Why not.** `resume.stage` is free text written by `roster_edit.py`, which accepts
any non-empty string for `stage` and any string for `branch`; nothing compares
either with `git ls-remote` or the PR API. The human rule existed and was not
followed: **(a) for the machine** (no reconciler exists) and **(b) for the prose**
(the rule existed and was not applied).

**Process state: (a)**, with a (b) component on the prose.

### S3 — the owner-gate age check counts mandate-covered groups as owner-blocked

**Measured.** Of the 47 open groups, **14 carry a non-null `owner_gate`**; the
board prints `-> 14 group(s) blocked on owner disposition; oldest issue #2222 is
5d old`. Six of the 14 carry the exact string `mandated approval under 6175172275`;
ten name the mandate in force in some form (`approved under mandate 6175172275`,
`tvofi approves under the mandate`, …). The mandate is live: the tick's own MAIN
line reads `mandate: in force: mandate 6175172275 (scope all, from
2026-10-14T18:14Z until 2026-10-28T18:14Z)`. The other four (`code-owned: …` or
`policy: …` with no mandate) are plausibly owner acts.

**Should have caught it.** The owner-gate check itself.

**Why not.** `replan()` selects `gated = [g for gid,g in groups.items() if gid in
open_g and g.get("owner_gate")]` — **truthiness on a free-text field** — and then
answers `"blocked on owner disposition"` for all of them. The mandate is read in
`MAIN` and never joined to the gate. The check ran exactly as written and answered
a different question ("does this group have a gate string?") from the one its line
asserts ("no act the owner could take is available").

**Process state: (c)** — followed, wrong result.

### S4 — seats stop writing and hold no child, while the harness calls them running

**Measured.** The seat ledger (`~/hpo-orch/r10s3/orch/SEATS.md`, 209 KB, last
written 09:12Z) ends with `LIVE(8): tick, vent, savbase, sensorpay, pump, refpriv,
review-leaf, review-2345`. At 11:49Z the box has **one** live Claude process tree
and **no** process for any of the eight; the only long-running work is background
shells of the one harness (mutation tables, preprs). The harness's notion of a
seat's state is not readable from the tree; the ledger's is.

**Should have caught it.** A liveness signal the tree can read.

**Why not.** The only signal, `~/hpo-orch/r10s3/orch/tick/alive`, is written by a
**brief** (`briefs/tick-watcher.md`: "`date -u +%FT%TZ > …/alive` each pass"), not
by an instrument: no process on the box contains `alive` in its command line, and
`mcp__scheduled-tasks__list_scheduled_tasks` reports **no scheduled tasks**. The
file's mtime moves (11:49:46Z) because a human/agent turn runs the command, not
because the tick did. The instrument that actually runs (`tick_loop.sh`) never
writes it, so the signal and the thing signalled are different mechanisms.

**Process state: (a)** for the tree (no liveness contract for a seat); **(c)** for
the harness (its state exists and does not describe the work).

### S5 — instruments dead after a session crash, restarted by hand

**Measured.** Six `daemonize` launches of the tick loop (above); each relaunch is a
human act. `daemonize.py`'s docstring is explicit: "No daemon bookkeeping is kept:
the pid is printed and logged, and `kill` by that pid is the stop story." The
sweep's restart is step 5, keyed on the memory-written `alive` file.

**Should have caught it.** A supervisor with a schedule.

**Why not.** There is none. The design chose detachment (correct: a background
task dies at 2 h) and stopped there; nothing restarts, and nothing tells a reader
that a job is dead except a file written by an unrelated mechanism.

**Process state: (a)**.

### S6 — `/usr/bin/git` broke, and every instrument depended on it silently

**Measured live.** At 09:37:39Z the newly launched tick loop's log carries
`xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools),
missing xcrun` twice, then `cloud_relay: could not list handoff refs; will retry`
and `cloud_relay: ls-remote failed; will retry`, then
`TICK-PASS 2026-10-20T09:37:58Z relay=ok tick=0`. The git binary is present now
(`git --version` → 2.54.0 (Apple Git-157); `xcode-select -p` →
`/Library/Developer/CommandLineTools`), so the break was transient. Nothing in the
tree hardcodes `/usr/bin/git` (`grep -rn '/usr/bin/git' tools tests .github .claude`
→ one fixture string in `tests/entities.py`); the dependency is `git` on `PATH`,
which resolves to the Apple shim over CommandLineTools.

**Should have caught it.** The relay pass's rc.

**Why not.** `handoff_arm` and `probe_arm` both `return 0` on an `ls-remote`/`gh`
failure ("will retry"), and `tick_loop.sh` maps rc 0 to `relay=ok`. The check
existed (an exit code) and produced the wrong result **by design**.

**Process state: (c)** — followed, wrong result: the adapter was written to fail
open.

### S7 — `update_pr.sh` starved for 30+ minutes in prepr, no timeout, no progress signal

**Measured live.** Two `open_pr.sh` runs (topics `r10-earlycutoff-coverage`,
`r10-i5-docs`) entered `prepr.sh` at 11:33Z and 11:33:42Z (slot `taken_at`). At
11:49Z they were 15:53 and 15:44 in, shells at 0:00.07 and 0:00.09 CPU, the
heavy-slot lease expiring at 12:03Z. Their `p1.log` shows a line per **completed
step** only; the last completed step was `contract_rerun`. At 11:50:33Z both
logged `Terminated: 15` — killed, with no record of which step was running, how far
it got, or what to resume. (What sent SIGTERM is not established from the tree; the
two were PPID-1 shells. The observation is the *shape*: no timeout and no progress
signal.) `grep -n timeout tools/pr/prepr.sh tools/audit/seat/{open_pr,update_pr}.sh`
finds no `timeout` command.

**Should have caught it.** A per-step timeout and a per-minute progress line; or
the slot lease as a cap.

**Why not.** There is no timeout anywhere in the chain. The slot lease does not
protect the holder either: `take_slot` never renews, and `_free_slot` steals
`owner.expired` **without probing the live pid** (demonstrated, E6). The cap is
enforced by expiry, so the one thing a long run needs — to keep its slot — is the
one thing it cannot do.

**Process state: (a)** for the timeout; **(c)** for the lease (it enforces a cap
by time, not by liveness).

### S8 — the plan page: a scratch instrument carrying constants (added mid-task by the orchestrator)

**Measured now** (`~/hpo-orch/r10s3/plan/gen.py` read at mtime 13:49Z and again at
13:54Z, being edited live, so this is a measurement of a moving file):
- It fetches the roster, then **overrides it**: `groups["R10-ARCH-DOCS"] = {…}`
  with a hardcoded brief and `resume.stage: not-started`, overwriting whatever the
  roster says (the roster does carry the group).
- Its dependency graph prefers a scratch file: `EDGES = json.load(REPLAN-EDGES.json)`
  and `edges = {g: list(EDGES.get(g, groups[g].get("after", []))) …}`. That file's
  mtime is **2026-10-17 23:06**; it names **34 of 93 groups** and **differs from the
  roster's `after` for 27 groups**. Where it has an entry, it wins over the record.
- It carries `LIVE` (14 seats) and `MERGED` (25 group→PR pairs) as constants, and
  `HOURS = {S:5, M:8, L:11, XL:14}` for its ETA; `WAVES.json` is a fourth constant.
- `R10-CI-RATCHET-RED` is `stage: done` with `commit: null` and the note "Folded
  into R10-CI-LAYOUT PR 0 … not dispatched separately" — the page renders it as
  delivered.
- Its publish path (`plan_artifact` in the sweep overlay) is
  `/private/tmp/claude-501/…/scratchpad/round-10-plan.html`, **which does not
  exist** (`ls` → No such file or directory); the generator writes
  `~/hpo-orch/r10s3/plan/round-10-plan.html` instead. Two homes, and the one the
  sweep names is gone.

The orchestrator's five recorded defects (a hardcoded group override, a graph from
scratch, a count from the wrong set, commit prefixes rendered as PR numbers, and
`done` overloaded to mean "absorbed") are the same class: **a claim carried from a
moment instead of derived at render time**.

**Should have caught it.** A self-test, or any reader comparing two figures.

**Why not.** It is scratch: no `--self-test`, `selftest_wiring.py` does not know
it, and `tmp_paths.py` is not run on it. Decision 0013 says an instrument the
programme runs is a tracked, self-tested file; this one has been the plan of
record for days.

**Process state: (a)**.

### S8b — what the page's fifth defect says about the roster schema

`done` is doing two jobs: "this group merged" and "this group was absorbed into
another". The roster has `deferred`/`refused` flags and `DONE_STAGES = ("done",
"rca-done")`, but no "folded" disposition. The consequence is not display-only:
`roster_lib.open_groups()` treats the group as closed, so its `after`-edges stop
constraining — correct for an absorbed group if the absorbing group's edges carry
them, which nothing checks. The design needs an explicit **absorbed** disposition
(§6.4), because a reader cannot distinguish "delivered" from "cancelled" from the
stage alone.

---

## 5. Demonstrations (the perturbation or null control for each claim)

Full commands and output in `EVIDENCE.md`; the shape here.

- **E2 — the board's composition.** `awk '{print $1}' tick.txt | sort | uniq -c`
  → 30,014 lines beginning `->`, 29,976 of them `-> OWED:`; the counts match the
  log's OWED count exactly (29,976), so the board is a projection of the log.
- **E3 — the OWED fold's blind grammar.** `Tick.relay_owed` imported and run on a
  four-line fixture. Result: the relay-verdict OWED cancels against its POSTED (the
  null control holds); the `handoff-no-pr` and `probe-ref` OWED lines print, and
  **still print after `cloud-disposed` records the ref**.
- **E4 — the relay's fail-open.** `cloud_relay.sh pass` with
  `HPO_RELAY_PRS=true` in a directory with no `origin` → **rc 0**, two `fatal:`
  lines, two "will retry". The null control (a working remote) is the live
  144-pass `relay=ok` run.
- **E5 — the tick's period is its own work.** 144 banners over 17.5 h; median gap
  399 s, max 2,654 s; derived pass duration max 2,354 s.
- **E6 — a live slot holder is stolen at expiry.** `gate_lock.take_slot` in a
  throwaway lock dir: A takes the only slot with a 1 s lease and a live named pid;
  after expiry B takes it, `sleeper.poll() is None` (A's process alive). The null
  control is `wait=False` **before** expiry, which raises `BlockingIOError`.
- **E8 — the roster is unverified.** 14/47 open groups carry an owner gate, 10 of
  them naming the live mandate; 9 stage-vs-ref mismatches; 8 non-40-hex
  `resume.commit` values; `R10-I5-DOCS` `not-started` beside a live `open_pr.sh`.
- **E9 — liveness is written by a brief.** No process writes `tick/alive`; no
  scheduled task exists; the file moves anyway.
- **E10 — the plan page carries.** 27/93 groups' edges differ between the scratch
  `REPLAN-EDGES.json` and the roster; the publish path does not exist.
- **E12 — the self-tests pass while the defects are present** (the "a check that
  passes while the bug is present" control): `orchestrator_tick.py --self-test` →
  150 checks, 0 failed; `cloud_relay.sh --self-test` → 74 checks, 0 failed;
  `tick_loop.sh --self-test` → 4 checks, 0 failed. None of the three fails on any
  of S1, S6, S7.

---

## 6. The design

### 6.1 Principles

1. **A level is a state, not a history.** Anything that must repeat until
   disposed is stored as an entry with an identity and a state, and read as the
   state. An append-only log is a journal of events; it is never a level.
2. **One owner per concern, and one writer per fact.** Every stored fact has one
   instrument that writes it and one schema that describes it; every reader imports
   the schema, never re-derives it.
3. **Fail closed at the adapter.** An adapter returns a distinguished
   `UNREADABLE`; the *runner* turns that into a failed pass. No adapter returns
   success for a read it did not make.
4. **Bounded by construction.** Every job has a wall-clock timeout; every output
   line is one per event or one level line per pass; every list is capped and the
   cap reports itself.
5. **Crash recovery is state, not ritual.** A job's progress is a durable file
   whose absence means "not done", and the supervisor restarts it. No human
   restarts anything.
6. **The record is verified, not declared.** A claim written into a record is
   reconciled with the refs and the API by a checker that runs on every pass.

### 6.2 One supervised beat (`beatd`)

A single tree instrument — `tools/audit/seat/beatd.py`, with `--self-test` —
replaces the three hand-launched daemons and owns the schedule:

- a **job table** (in the tree, beside the instrument) naming each job, its
  interval, its timeout, its lock class and its level-line shape. The initial
  table: `tick` (M02, 300 s, timeout 600 s), `relay` (M03/M04, 120 s, timeout
  600 s), `state-docs` (M06, 300 s, timeout 300 s), `sync` (M29, 900 s, timeout
  600 s), `plan-page` (M37, 300 s, timeout 300 s);
- one **single-instance lock per job** (`flock`, keyed by job name) and one for
  `beatd` itself, so a second `beatd` cannot start and a job cannot overlap
  itself;
- a **hard per-job timeout** (`subprocess` with a timeout, SIGTERM then SIGKILL),
  recorded as `outcome=timeout` — S7's missing bound, applied to every job;
- one **journal line per job per pass**, written by `beatd` from the job's result:
  `PASS <utc> <job> start=<utc> dur=<s> outcome=ok|failed|timeout|unreadable
  lines=<n>`, plus a **heartbeat line every 60 s while a job runs**
  (`RUNNING <utc> <job> pid=<pid> elapsed=<s> step=<last>)` — the progress signal;
- `beatd status [--json]` prints the jobs, their last pass, their last outcome and
  the pids — the tree-readable liveness contract S4 lacks. `beatd` writes no
  "alive" file; **its own journal is the liveness file**, and it is written by the
  runner, not by a brief;
- **the reader and the writer are separate jobs.** The relay's handoff arm moves
  out of M03-inside-M01 and becomes its own job with its own timeout, so the
  board's cadence can no longer be dominated by a `prepr.sh` (E5);
- **no `daemonize.py` bookkeeping is added**: `beatd` is still launched once by
  `daemonize.py` (banner, pid); the difference is that a dead `beatd` is visible as
  a stale journal and restarting it is one command that needs no judgement.

Cost: ~350 lines, ~20 s/minute of overhead, one new tracked file, no policy change
to run it.

### 6.3 One obligations ledger

`tools/audit/seat/ledger.py` (with `--self-test`) and a state file
`$HPO_STATE_DIR/obligations.tsv` with **one schema**:

    open  <utc> <kind> <subject> <sha> <why>
    close <utc> <kind> <subject> <sha> <how>
    supersede <utc> <kind> <subject> <old-sha> <new-sha>

- `kind` ∈ `handoff-no-pr`, `probe-ref`, `reviewer-fire`, `relay-post`,
  `record-owed`, `train-stop`, `stage-mismatch`. **One grammar**, so a reader can
  fold every kind with one function.
- A **fold** is `open` entries with no `close` for the same `(kind, subject, sha)`.
  A subject whose `sha` moved is `supersede`d automatically by the producer, so
  "disposed, then moved" opens exactly one new obligation and closes the old one
  as `superseded` — the "cannot silently widen" requirement, made structural.
- **Producers open; actors close.** `cloud_relay.sh` opens `handoff-no-pr` and
  closes it when the PR appears (it already lists open PRs — it has the fact);
  `bus.sh orphans` feeds the same ledger instead of printing a second list; the
  tick *folds and prints*, capped at 20 per kind with
  `OWED <kind>: N open (showing 20); M closed this pass`.
- **`cloud-disposed` is migrated into it** (a one-time import), not kept beside it.
  **No parallel mechanism:** the ledger replaces the disposal file, the tick's log
  scan, and `bus.sh orphans`' separate print.
- `ledger.py --check` refuses an entry with an unknown kind, a short sha, or a
  `close` with no matching `open` — the schema a reader can trust.

Cost: ~250 lines, one state file, a one-time 210-entry import, and the tick's OWED
section shrinks from a whole-log read (3.9 MB/pass) to a fold over an open set
(229 subjects, ~200 lines).

### 6.4 A state reconciler

A job (`reconcile`, 300 s, timeout 300 s; also runnable as
`roster_edit.py --reconcile`) that compares every claim with the repository:

- **stage vs refs/PRs**: `not-started` + a `handoff/`/`fix/` ref or an open PR at
  its branch → `STAGE-MISMATCH <group> recorded=not-started live=in-flight <sha>`;
  `in-progress|queued` + no ref and no PR commit in N hours → `STAGE-MISMATCH
  recorded=<stage> live=no-artifact`; `done` + `resume.commit` not in `main` →
  the existing `group-stale` line. **A `resume.commit` that is not 40-hex is a
  `RECORD-INVALID` line**, not silently skipped (8 today).
- **`owner_gate` becomes structured**:
  `{"class": "code-owned|policy|budget|mandate", "mandate": <id|null>, "paths": [...]}`.
  The reconciler joins it to the in-force mandate (the reader `budget_raise_gate`
  already owns) and prints `GATE-READY <group> (under mandate <id>)` or
  `GATE-OWNER <group> <class>`. "Blocked on owner disposition" is computed as
  *no act the in-force mandate covers* — S3's 14 become 10 ready and 4 owner.
- **an `absorbed` disposition**: `resume.stage: "absorbed"`, plus
  `absorbed_into: <group>`, replaces the overloading of `done`. `roster_lib`
  gains it to `DONE_STAGES` (so edges still stop constraining) but the plan page
  renders it as "absorbed into X", never "delivered", and the reconciler checks the
  absorbing group is open or done itself. This is the answer to S8b.

Cost: ~200 lines; the roster schema change is the owner's (§8).

### 6.5 Fail-closed adapters

- `cloud_relay.sh`: every `ls-remote`/`gh` failure returns a non-zero pass with the
  failing read named; `pass` returns the worst rc of its arms. `tick_loop.sh`
  prints `relay=unreadable` and `beatd` records `outcome=unreadable`. S6's line
  becomes `TICK-PASS … relay=rc=3`, and `beatd status` shows the job red.
- `state_docs.py` already fails closed (M06) — kept as the model.
- `bus.sh watch` already dies on an unreadable ref list (M13) — kept.
- A **shared helper** (`unreadable()` in the ledger or a tiny
  `tools/audit/seat/adapters.sh`) so the rule is one function, not a convention.

### 6.6 Lock classes (three, named)

1. **Exclusive** — anything that *measures* the machine (`stress.py`,
   `harness_headers.py`): M27 unchanged, with `renew` while held.
2. **Pool** — heavy work (`prepr`, `derive_closures`): M28, with two fixes:
   **renew the slot while the holder runs** (a `heartbeat` from the job, or a lease
   longer than the job's timeout — the timeout now exists, so the lease can be
   `timeout + 60 s`), and `_free_slot` **never steals a slot whose named pid is
   alive** (S7/E6). An orphaned slot (pid gone) is still stolen at once.
3. **Per-subject** — any read-then-write on a shared ref or branch: the
   `update_pr.sh` flock is the model (M22). Extend it to `roster_edit` (the roster
   branch), to `state_docs`/`plan-page` (the plan ref, via
   `git push --force-with-lease=<ref>:<tip>` as the compare-and-swap, with the
   loser re-deriving rather than retrying blindly), and to `open_pr` (the per-topic
   worktree).

### 6.7 The plan page: where it lives, what it derives, how it fails

**Decision.** The generator moves into the tree as
`tools/audit/seat/plan_page.py`, with `--self-test`, and it **shares one model
builder with `plan_table.py`**: the roster walk (groups, `after`-edges, open set,
depth, critical path) already lives in `roster_lib.py`, so the model builder is
`roster_lib` plus a small `plan_model()` that adds the live facts (open PRs by
branch, merged PRs, the issue list, the obligations fold). `plan_table.py` and
`plan_page.py` become two renderers of one model — one owner per concern, no
duplicate roster walk.

**What the beat calls.** `plan-page` is a job of §6.2's `beatd`, interval 300 s,
timeout 300 s, after `state-docs` in the same pass. It runs only when an input
moved (roster ref tip, open-PR set, merged set, issue count), the same memo
discipline M06 already uses.

**What it publishes.** One standalone HTML page at the **plan ref**, beside the
three state docs: `handoff/round<N>/state/PLAN.html`, in `state_docs.py`'s write
set, pushed by the same commit as `PLAN-TABLE.md` and mirrored to
`~/hpo-orch/state/PLAN.html`. **One artifact, one path, durable** — not the
session temp root that no longer exists (E10). The write set stays guarded: the
page is one more path in `DOC_NAMES`/`state_of`.

**How it fails.** An unreadable roster, API or ref renders a page whose first line
is `<h1>PLAN UNAVAILABLE — <what could not be read></h1>`, with every figure
replaced by `—` and no table; it never renders zeros. The renderer refuses (exit
1) and the beat records `outcome=unreadable`; the previous page at the ref is left
alone (the refused push is not made), so a reader sees the last good page *with its
timestamp* rather than a plausible-looking empty one.

**Generalization.** No round-10 constant: the round comes from the roster path
(`wave-r<N>-groups.json`), the repo from `--repo`, the paths from the flag set.
Every figure is derived: status from `resume.stage` (+ the reconciler's
`STAGE-MISMATCH` overlay), edges from the roster's `after`, issue counts from
`gh issue list --state open` **excluding PRs** (a separate endpoint, not a
subtraction), PR numbers from `gh pr list`/the merged set, ETA from the roster's
sizes only when the model says a size exists (else `—`), and commit SHAs rendered
as SHAs, never as `#`.

**Self-test: the five recorded defects, each failing-then-passing.** Each case is
a fixture roster plus a fixture API payload:
1. **hardcoded override** — the roster says `done` for a group; the fixture also
   feeds an "in-review" hint in the same shape the old code hardcoded. Arm: the
   rendered status is `done`; the mutant that re-adds the override renders
   `live`.
2. **graph from scratch** — the fixture roster's `after` differs from a fixture
   "scratch edges" file. Arm: the page's blocked set and critical path match the
   roster's; the mutant that prefers scratch edges changes the ETA.
3. **count from the wrong set** — a fixture issue list containing pull requests
   and closed issues. Arm: `open_iss` equals the open, non-PR count excluding
   `#201`; the mutant that subtracts one from `--state all` prints 887.
4. **commit prefix as PR number** — a done group with a `resume.commit` and no
   merge. Arm: the cell is the SHA (or `merged`), never `#<sha8>` or `#done`.
5. **two statuses in one** — a group with `stage: absorbed`, `absorbed_into`.
   Arm: rendered "absorbed into X", not "delivered"; the mutant that maps it to
   `done` prints delivered.
Plus a null control: an all-done roster renders a page with no open rows and the
true totals.

**Seam with R10-ROSTER-OPS.** The replan lived in scratch because `roster_edit.py`
has **no `set-after` op** (`p.add_argument("op", choices=("set-stage",
"wire-issue", "unwire-issue", "append-group", "edit-brief", "append-carry",
"set-resume"))`). R10-ROSTER-OPS owns adding `set-after` (and the `absorbed`
fields); this design consumes it and does not add ops. Until it lands, the page
reads `after` from the roster and a group whose edges need editing is edited by
that group's roster PR.

### 6.8 Cost summary

| element | seconds per pass | lines | policy lines |
|---|---|---|---|
| `beatd` + job table | ~20 | ~350 | 0 (run it) |
| obligations ledger + migration | ~5 (fold 229 rows) | ~250 | 0 |
| reconciler | ~30 (one `ls-remote`, one PR list; no new API class) | ~200 | schema change (§8) |
| fail-closed adapters | 0 | ~60 | 0 |
| slot renewal + no-steal-live | 0 | ~40 | 0 |
| plan page in the tree | ~2 (only on a moved input) | ~400 | 0 |
| **net** | **~55 s per 5 min** | **~1,300** | **1 owner-approved schema change** |

Against the measured cost of the defects: the board alone rewrites **3.9 MB × 8.2
passes/h ≈ 32 MB/h ≈ 0.77 GB/day** (`wc -c tick.txt`; 144 banners over 17.5 h),
and every pass pays the whole-log read. The ledger replaces it with a fold over
229 rows.

---

## 7. Alternatives considered and rejected

1. **Keep the loops and fix each slip in place.** Rejected: five of the eight
   slips share three causes (a level derived from history; liveness by memory;
   fail-open adapters), so per-slip fixes leave the next grammar, the next
   adapter and the next brief to find. It also keeps four schedulers, four
   liveness conventions and no bound.
2. **Move everything into CI.** Rejected: the gate lease, the App identity, the
   per-branch lock and the merge train are deliberately local (one machine, one
   quota, one credential); CI cannot hold a flock on this box, cannot push with
   the same review semantics, and its cadence is minutes-to-hours. The record beat
   (M11) is already CI and stays there — CI owns *record generation*, the box owns
   *dispatch and merge*.
3. **One monolithic orchestrator process that does everything.** Rejected: it
   concentrates write authority, cannot be tested piecewise, and collapses the
   role separation the policy depends on (orchestrator vs seats). The supervisor
   in §6.2 schedules jobs; it does not acquire their authority.
4. **Event-driven webhooks instead of polling.** Rejected for this environment: no
   inbound endpoint, an extra credential surface, and the identity model (0011)
   forbids the extra writer. Named because it is the obvious alternative and the
   reason it does not apply should be on the record.
5. **Make the tick a seat again (a harness background task).** Rejected: measured
   background tasks die at 2 h, and the harness's liveness is not observable from
   the tree — that is S4.
6. **A database for state instead of files and refs.** Rejected on cost: the
   programme's state must be readable by `git` alone (seats have no service), and
   a ledger file plus refs is the same guarantee at zero infrastructure.

---

## 8. Migration

Ordered by dependency; each step is one tree PR with its self-test failing on the
defect it answers and passing once fixed (`defect-root-cause.md`), and no step
needs the next.

**Phase 0 — no policy change, one week of slips closed.**
1. `orchestrator_tick.py:relay_owed` reads the disposal state (initially
   `cloud-disposed` directly; the ledger migration is Phase 1) and keys on
   `(kind, subject, sha)`; the self-test gains the three missing grammars. *Fails
   on S1 (the board), passes after.*
2. `cloud_relay.sh pass` returns non-zero on an unreadable remote; `tick_loop.sh`
   and any caller report it. *Fails on S6, passes after.*
3. `tick_loop.sh` takes a `flock` on its output path (one loop per board) and
   `alive` is written by the loop, not by a brief. *Fails on S5's double start.*
4. `gate_lock.py`: renew a slot while held and never steal a live holder. *Fails
   on E6, passes after.*
5. `prepr.sh` gains `timeout` per step and a 60 s `RUNNING` line. *Fails on the
   step that starved; passes after.*

**Phase 1 — the ledger and the beat.** `ledger.py` + the `cloud-disposed` import;
`cloud_relay`, `bus.sh orphans` and the tick migrated to it. `beatd.py` with the
five jobs; the three hand-launched daemons retired in one switch, with the journal
as the liveness contract.

**Phase 2 — the reconciler and the schema.** `roster_edit.py --reconcile` and the
structured `owner_gate`; the `absorbed` disposition. **Owner approval required**
before merge: this changes the roster schema and therefore what a seat must write.
Seam: R10-ROSTER-OPS supplies `set-after` and the new fields' ops; this design
supplies the reconciler and the rendering. If R10-ROSTER-OPS lands first, Phase 2
drops its schema half and keeps the reconciler.

**Phase 3 — the plan page in the tree.** `plan_page.py` sharing
`roster_lib.plan_model()` with `plan_table.py`, in `state_docs.py`'s write set,
published at the plan ref and the mirror. The scratch generator is retired when
the tree page has rendered a week. Seam: none with R10-CI-LAYOUT (workflows are
outside this surface); the state-docs job is where the two meet, and R10-CI-LAYOUT
does not touch `state_docs.py`.

**Policy changes proposed, not landed** (each names the process state it answers):

| proposal | file | state | why |
|---|---|---|---|
| A periodic instrument in the tree REQUIRES a wall-clock timeout, a single-instance lock and a level line | `tools/audit/seat/INSTRUMENTS.md`, `orchestrator.md` §13 | (a) | there is no bound rule today |
| Liveness is written by the instrument that runs, never by a brief, and `beatd status` is the contract | `orchestrator.md` §13, `INSTRUMENTS.md` | (a) | S4/S5 |
| The obligations ledger is the single source for OWED; no instrument prints a level from an event log | `orchestrator.md` §8/§12 | (c) | S1 |
| `owner_gate` is structured; "blocked on owner disposition" means no in-force mandate covers it | roster schema (`roster_edit.py`, `roster_lib.py`) | (c) | S3 |
| A roster group is `absorbed` (into another), never `done`, when it has no merge of its own | roster schema | (c) | S8b |

---

## 9. What I could not establish

- **What sent SIGTERM** to the two `open_pr.sh` chains at 11:50:33Z. The shape
  (two PPID-1 shells, both `Terminated: 15` at the same second, no timeout in the
  chain) is recorded; the sender is not visible from the tree or the process
  table after the fact.
- **The harness's own view of a seat's state.** I can prove the tree has no
  process for the ledger's 8 LIVE seats and that the liveness file has no writer;
  I cannot read the harness's task list from here, so S4's "(c) for the harness"
  is an inference from the ledger/process mismatch, not a measurement of the
  harness.
- **The exact prepr step running at the kill.** `p1.log` records completed steps
  only; the last was `contract_rerun`. The absence of a progress signal is the
  point, but the step is unknown.
- **Whether the plan ref's unleased writers have ever actually collided.** The
  code shows read-then-write with no lock; I did not construct the race because it
  writes the live plan ref (the brief forbids changing another seat's files).
- **The live `gen.py` beyond 13:54Z.** It is being edited while I read it; the
  measurements above are of the file at 13:49–13:54Z and the design does not depend
  on any single line.
- **The four owner-gated non-mandate groups' true blocking act.** I measured the
  strings; whether the owner has already stated a disposition elsewhere on `#201`
  (1,875 comments) is not established.
