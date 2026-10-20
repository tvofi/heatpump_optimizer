# Evidence for the orchestration-machinery design

Commands and their output for every quantified claim in `DESIGN.md`. Host paths are
written `~` and the owner column of an `ls -la` output is shown as `USER` (the docs were committed to a ref; `ref_privacy.py` exists so a push
does not publish the host). Times are UTC unless marked local. `load1` is quoted
beside every timing claim.

Run from the design worktree unless a command names another directory:

    git -C ~/heatpump_optimizer worktree add ~/hpo-seats/r10s3/orch-design/wt \
        -B handoff/orch-machinery origin/main
    cd ~/hpo-seats/r10s3/orch-design/wt      # HEAD a2b25bbc5 at the time of writing

Live state read 2026-10-20T11:38Z–11:56Z, `load1` 42.9–82.6 on 8 cores
(`sysctl -n hw.ncpu` → 8; `uptime` → `load averages: 42.95 57.47 60.92`).

---

## E1. Inventory row count (derived, not carried)

    $ grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md
    46
    $ grep -o '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md |
        sed 's/^| M//' | sort -n |
        awk 'NR != $1 { print "gap at", $1; bad=1 } END { if (!bad) print "contiguous 1.." NR; exit bad }'
    contiguous 1..46

False-result control: a copied count would not match this command after any edit;
the second command fails if a row id is missing or duplicated.

Tree size the rows are drawn from:

    $ ls tools/audit/seat | wc -l
    53
    $ grep -l -- '--self-test' tools/audit/seat/* | wc -l
    38
    $ wc -l tools/audit/seat/* tools/audit/seat/*.md | tail -1
    22793 total

---

## E2. The board is a projection of the relay log (S1)

    $ wc -c -l ~/hpo-orch/r10s3/orch/tick/tick.txt
    30079 3901380 ~/hpo-orch/r10s3/orch/tick/tick.txt
    $ tail -1 ~/hpo-orch/r10s3/orch/tick/tick.txt
    DISPATCH LIST: 30014 finding(s)
    $ awk '{print $1}' ~/hpo-orch/r10s3/orch/tick/tick.txt | sort | uniq -c | sort -rn | head -3
    30014 ->
        8 ==
        3 roster
    $ grep -c '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt
    29976
    $ grep '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt |
        sed -E 's/.* (refs\/heads\/[^ ]+|[a-z-]+) .*/\1/' | sort -u | wc -l
    229
    $ python3 -I -c "print(29976/229)"
    130.8995633187773
    $ grep '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt |
        sed -E 's/^-> OWED: OWED( [0-9T:Z-]+)? ([a-z-]+).*/\2/' | sort | uniq -c
    29814 handoff-no-pr
       10 handoff-update
      151 probe-ref
        1 reviewer-fire

The source log, same count:

    $ wc -l -c ~/.local/state/hpo/cloud-relay.log
    29976 3622919 ~/.local/state/hpo/cloud-relay.log
    $ grep ' handoff-no-pr ' ~/.local/state/hpo/cloud-relay.log | awk '{print substr($2,1,13)}' |
        sort | uniq -c | tail -4
     1827 2026-10-20T08
      875 2026-10-20T09
     1040 2026-10-20T10
      862 2026-10-20T11
    $ grep ' handoff-no-pr ' ~/.local/state/hpo/cloud-relay.log | awk '{print $4}' | sort -u | wc -l
    213
    $ wc -l < ~/.local/state/hpo/cloud-disposed
    210
    $ comm -12 <(grep ' handoff-no-pr ' ~/.local/state/hpo/cloud-relay.log | awk '{print $4}' | sort -u) \
               <(awk '{print $1}' ~/.local/state/hpo/cloud-disposed | sort -u) | wc -l
    201

201 of the 210 disposed refs are re-owed at a different sha (the ref moved after
disposal); the relay's own rule — "a disposed ref that moves is owed again" — is
correct for a one-shot probe ref and permanent for a moving branch.

**Write volume.** 144 banners over the log's span (E5) → 8.2 passes/h:

    $ python3 -I -c "b=3901380; print(round(b*8.2/1e6,1),'MB/h', round(b*8.2*24/1e9,2),'GB/day')"
    32.0 MB/h 0.77 GB/day

**The parser's key.** Source, `tools/audit/seat/orchestrator_tick.py:relay_owed`:

    for row in rows:
        f = row.split()
        if len(f) >= 3 and f[0] == "OWED":
            owed.setdefault(f[2], []).append(row.strip())
        elif len(f) >= 3 and f[0] == "POSTED":
            owed.pop(f[2], None)

`f[2]` is the PR for the verdict grammars and the literal kind token for
`handoff-no-pr` / `probe-ref`. No `POSTED` is ever written for those kinds.

---

## E3. Demonstration — the fold's blind grammar (real code, fixture)

    $ python3 -I - <<'PY'
    import importlib.util, tempfile, os
    spec=importlib.util.spec_from_file_location("tick","tools/audit/seat/orchestrator_tick.py")
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    t=object.__new__(m.Tick); t.findings=[]; t.sections={}; t.api_calls=0
    d=tempfile.mkdtemp(); log=os.path.join(d,"relay.log")
    open(log,"w").write(
    "OWED 2026-10-19T18:11:44Z handoff-no-pr refs/heads/handoff/x deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\n"
    "OWED 2026-10-19T18:11:44Z probe-ref refs/heads/probe/y deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\n"
    "OWED 2026-10-19T18:20:00Z 7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa bus.sh confirm failed\n"
    "POSTED 2026-10-19T18:25:00Z 7 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n")
    t.relay_log=log
    t.relay_owed("REPLAN")
    for f in t.findings: print(f["text"])
    print("findings:",len(t.findings))
    open(os.path.join(d,"cloud-disposed"),"w").write("refs/heads/handoff/x deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\n")
    t.findings=[]; t.sections={}
    t.relay_owed("REPLAN")
    for f in t.findings: print(f["text"])
    print("findings after dispose:",len(t.findings))
    PY
    OWED: OWED 2026-10-19T18:11:44Z probe-ref refs/heads/probe/y deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
    OWED: OWED 2026-10-19T18:11:44Z handoff-no-pr refs/heads/handoff/x deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
    findings: 2
    OWED: OWED 2026-10-19T18:11:44Z probe-ref refs/heads/probe/y deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
    OWED: OWED 2026-10-19T18:11:44Z handoff-no-pr refs/heads/handoff/x deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
    findings after dispose: 2

Null control that passes: the relay-verdict OWED (`… 7 … bus.sh confirm failed`)
followed by `POSTED … 7 …` prints **nothing** — the one grammar the self-test pins.

---

## E4. Demonstration — the relay's fail-open (S6)

    $ S=$(mktemp -d ~/hpo-seats/r10s3/orch-design/relaydemo.XXXXXX); cd "$S"
    $ HPO_STATE_DIR="$S/state" HPO_RELAY_PRS=true \
        bash ~/hpo-seats/r10s3/orch-design/wt/tools/audit/seat/cloud_relay.sh pass > "$S/out" 2>&1
    $ echo "rc=$?"; cat "$S/out"
    rc=0
    fatal: 'origin' does not appear to be a git repository
    fatal: Could not read from remote repository.

    Please make sure you have the correct access rights
    and the repository exists.
    cloud_relay: could not list handoff refs; will retry
    fatal: 'origin' does not appear to be a git repository
    fatal: Could not read from remote repository.

    Please make sure you have the correct access rights
    and the repository exists.
    cloud_relay: ls-remote failed; will retry

The live instance, in the running loop's own log:

    $ grep -n '^===== daemonize' ~/hpo-orch/r10s3/orch/tick/loop.log
    1:===== daemonize pid=46070 2026-10-19T18:11:31Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    246:===== daemonize pid=48658 2026-10-19T18:15:36Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    23558:===== daemonize pid=30511 2026-10-20T06:54:19Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    27536:===== daemonize pid=11552 2026-10-20T09:37:39Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    27542:===== daemonize pid=12205 2026-10-20T09:38:06Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    28593:===== daemonize pid=35000 2026-10-20T10:11:16Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    $ sed -n '27536,27540p' ~/hpo-orch/r10s3/orch/tick/loop.log
    ===== daemonize pid=11552 2026-10-20T09:37:39Z argv: bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
    cloud_relay: could not list handoff refs; will retry
    xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
    cloud_relay: ls-remote failed; will retry
    TICK-PASS 2026-10-20T09:37:58Z relay=ok tick=0 out=~/hpo-orch/r10s3/orch/tick/tick.txt

Two launches 27 s apart (`09:37:39`, `09:38:06`) of a loop whose interval is 300 s
is the double-start: the second is the sweep's restart ritual starting a *second*
mechanism beside the live one. `tick_loop.sh` contains no `alive` write and no
pidfile (`grep -n 'alive\|pidfile\|flock' tools/audit/seat/tick_loop.sh` → none).

False-result control: on a healthy pass the same line would print `relay=ok` with
no `fatal:`/`xcrun` lines above it; the defect is the *combination*, which the
self-test does not exercise (`tick_loop.sh --self-test` stubs a relay that exits 0
or N, never one that fails a read).

---

## E5. The tick's achieved cadence

    $ python3 -I - <<'PY'
    import re,datetime,statistics
    import os
    lines=open(os.path.expanduser('~/hpo-orch/r10s3/orch/tick/loop.log'),encoding='utf-8',errors='replace').read().splitlines()
    ts=[datetime.datetime.fromisoformat(m.group(1)) for l in lines if (m:=re.match(r'TICK-PASS (\S+) ',l))]
    gaps=[(b-a).total_seconds() for a,b in zip(ts,ts[1:])]
    print("passes:",len(ts))
    print("gaps min/median/mean/max: %.0f %.0f %.0f %.0f"%(min(gaps),statistics.median(gaps),statistics.mean(gaps),max(gaps)))
    print("gaps >600s:",sum(1 for g in gaps if g>600),"of",len(gaps))
    print("derived pass durations max %.0f"%max(g-300 for g in gaps if g>300))
    PY
    passes: 144
    gaps min/median/mean/max: 74 399 438 2654
    gaps >600s: 5 of 143
    derived pass durations max 2354

Eight largest gaps:

      08:53:44 -> 09:37:58 2654
      10:35:52 -> 11:02:36 1604
      06:35:35 -> 06:55:19 1184
      20:28:28 -> 20:47:46 1158
      19:39:09 -> 19:50:31  682

False-result control: 300 s interval with an instantaneous pass would give every
gap ≈300 s and no gap over 600 s; five gaps of 682–2,654 s is the signal.

---

## E6. Demonstration — a live slot holder is stolen at expiry (S7)

    $ T=$(mktemp -d ~/hpo-seats/r10s3/orch-design/lockdemo.XXXXXX)
    $ python3 -I - "$T" <<'PY'
    import sys, time, os, subprocess, pathlib
    sys.path.insert(0,"tests"); import gate_lock
    d=sys.argv[1]; sleeper=subprocess.Popen(["sleep","60"])
    i,o=gate_lock.take_slot("holder-A", lock_dir=pathlib.Path(d), slots=1, lease_seconds=1, owner_pid=sleeper.pid)
    print("A took slot",i,"pid",o.pid,"expires",o.expires_at)
    time.sleep(2); print("A's named pid alive?", sleeper.poll() is None)
    try:
        j,o2=gate_lock.take_slot("holder-B", lock_dir=pathlib.Path(d), slots=1, lease_seconds=30, wait=False, owner_pid=os.getpid())
        print("B STOLE the slot while A's process is alive: slot",j,"now",o2.label)
    except BlockingIOError as e: print("B blocked:",e)
    sleeper.kill()
    PY
    A took slot 0 pid 97905 expires 2026-10-20 11:53:11.542037+00:00
    A's named pid alive? True
    B STOLE the slot while A's process is alive: slot 0 now holder-B

Null control: `wait=False` **before** expiry raises `BlockingIOError` (the same
call shape); the steal needs the expired lease.

Live context: the two `prepr.sh` runs held slots whose leases expired at
`12:03:33Z` and `12:03:42Z` while they had run 15+ minutes:

    $ cat /tmp/hpo-gate.lock/slots/slot-000
    label=prepr-48004
    expires_at=2026-10-20T12:03:33.110897+00:00
    taken_at=2026-10-20T11:33:33.110897+00:00
    pid=48004
    $ python3 -I tests/gate_lock.py slot-status
    /tmp/hpo-gate.lock/slots: 3/4 slots held [0:prepr-48004(live), 1:prepr-48265(live), 2:prepr-63943(live)] queue=-
    $ python3 -I tests/gate_lock.py status
    /tmp/hpo-gate.lock: expired label=r10-stamp expires_at=2026-10-20T11:10:05.554391+00:00 flock_available=True queue=-

The single lease is also abandoned-expired (`r10-stamp`), which is the crash state
`take()` steals — correct for the exclusive lease, wrong as the *only* protection
for the pool.

---

## E7. The prepr starvation (S7)

    $ ps -o pid,ppid,etime,time,stat,command -p 47539,47826,48004,48214,48265 2>/dev/null | cut -c1-140
     47539     1    16:09   0:00.04 Ss   bash tools/audit/seat/open_pr.sh r10-earlycutoff-coverage ecaf178cbd4eef5e3b30425bd4693bef8ceb4b24 …
     47826     1    15:59   0:00.04 Ss   bash tools/audit/seat/open_pr.sh r10-i5-docs 7a7102eb844cf4f549d52af241b7bdc8e5a74797 …
     48004 48003    15:53   0:00.07 S    bash ~/.local/state/hpo/pr/r10-earlycutoff-coverage/wt/tools/pr/prepr.sh …
     48265 48264    15:44   0:00.09 S    bash ~/.local/state/hpo/pr/r10-i5-docs/wt/tools/pr/prepr.sh …
    $ tail -2 ~/.local/state/hpo/pr/r10-earlycutoff-coverage/p1.log
      ok       contract_rerun         contract_rerun self-test: 24 checks, 0 failed
    Terminated: 15

Both chains were PPID 1 (orphaned from the session that started them), zero CPU in
the shell, a line per completed step only. Both logged `Terminated: 15` at
11:50:33Z (local 13:50:33).

No timeout in the chain:

    $ grep -n 'timeout' tools/pr/prepr.sh tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh
    (no `timeout` command; all hits are prose or a lane name)

False-result control: a bounded run would show either a `timeout` refusal line or
a progress line newer than the last completed step; neither exists.

---

## E8. The roster is unverified (S2, S3, S8b)

    $ git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json > /tmp/r10roster_branch.json
    $ python3 -I - <<'PY'
    import json,collections
    r=json.load(open('/tmp/r10roster_branch.json'))
    print("groups:",len(r['groups']))
    print("stages:",dict(collections.Counter((g.get('resume') or {}).get('stage') for g in r['groups'])))
    print("open (not done/rca-done):",sum(1 for g in r['groups'] if (g.get('resume') or {}).get('stage') not in ('done','rca-done')))
    print("owner_gate set:",sum(1 for g in r['groups'] if g.get('owner_gate') and (g.get('resume') or {}).get('stage') not in ('done','rca-done')))
    PY
    groups: 93
    stages: {'done': 46, 'not-started': 36, 'in-progress': 7, 'queued': 4}
    open (not done/rca-done): 47
    owner_gate set: 14

Owner gates that name the live mandate (10 of 14; six exactly
`mandated approval under 6175172275`):

    R10-SETPOINT-BOOST    'mandated approval under 6175172275'
    R10-CEILING-PROBE     'mandated approval under 6175172275'
    R10-DEMAND-OVERBOOK   'mandated approval under 6175172275'
    R10-BUFFER-STORE      'mandated approval under 6175172275'
    R10-COP-PARTLOAD      'mandated approval under 6175172275'
    R10-UPDATE-PR-SIGNALS 'mandated approval under 6175172275'
    R10-TRAIN-HOLD        'code-owned: .github/workflows/ (workflow change, approved under mandate 6175172275)'
    R10-POLICY-LINT-FAMILY 'policy: tools/policy/ is in POLICY_GLOBS; tvofi approves under the mandate'
    R10-MERGE-SUBJECT-HARDEN 'policy: tools/policy/agreement.mjs is in POLICY_GLOBS; tvofi approves under the mandate'
    R10-CI-LAYOUT         '… approved at their merged head by the CODEOWNER session under mandate 6175172275 …'

The mandate, from the tick's own MAIN section:

    mandate: in force: mandate 6175172275 (scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z)

Stage-vs-ref mismatches (9), from

    $ git ls-remote --heads origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' 'refs/heads/fix/*' | wc -l
    219

and the roster walk in `EVIDENCE`'s script (the full program is in the seat log;
the result):

    ('R10-SENSOR-PAYLOAD', 'not-started', 'not-started but a ref names it')
    ('R10-I5-DOCS',        'not-started', 'not-started but a ref names it')
    ('R10-CI-LAYOUT',      'not-started', 'not-started but a ref names it')
    ('R10-DEMAND-OVERBOOK','queued',      'in-progress/queued but no ref names it')
    ('R10-BUFFER-STORE',   'queued',      'in-progress/queued but no ref names it')
    ('R10-COP-PARTLOAD',   'queued',      'in-progress/queued but no ref names it')
    ('R10-UPDATE-PR-SIGNALS','queued',    'in-progress/queued but no ref names it')
    ('R10-HANDOFF-ARCHIVE','in-progress', 'in-progress/queued but no ref names it')
    ('R10-DEPENDABOT-AIOHTTP','in-progress','in-progress/queued but no ref names it')

`R10-I5-DOCS` beside a live opener:

    $ git ls-remote --heads origin 'refs/heads/handoff/*i5-docs*' 'refs/heads/handoff-body/*i5-docs*'
    cfba198bcbd1dfb3352d7c491d6be7f71fd695bd  refs/heads/handoff-body/r10-i5-docs
    7a7102eb844cf4f549d52af241b7bdc8e5a74797  refs/heads/handoff/r10-i5-docs
    $ grep -n 'R10-I5-DOCS' ~/hpo-orch/r10s3/orch/tick/tick.txt
    30023:-> R10-I5-DOCS: UNBLOCKED, not started -- start a fixer on handoff/r10-i5-docs

while `ps` (E7) showed an `open_pr.sh` for `r10-i5-docs` running 11:33–11:50Z.

The contradictory display line:

    $ grep -n 'R10-UPDATE-PR-SIGNALS' ~/hpo-orch/r10s3/orch/tick/tick.txt
    30046:   R10-UPDATE-PR-SIGNALS: in progress (stage queued)

The source (`orchestrator_tick.py:plan`) prints `"in progress (stage {stage})"` for
every non-deferred, non-blocked, non-`UNBLOCKABLE_STAGES` stage, so `queued` is
rendered "in progress".

Eight `resume.commit` values are not 40-hex (the tick's `group-stale` tests only
`len(sha)==40`, so these can never be verified):

    ('R10-VENT-DETECTOR','768bfc0c341d') ('R10-SAV-BASELINE','8cc1abc3a27d')
    ('R10-TICK-DRIVERS','a96f4be4ac0a') ('R10-DIAG-REPLAY','0dac0bf8731a')
    ('R10-REF-PRIVACY','a73f3320c53a') ('R10-RCA-STRUCTURE-BLIND','f0a4acac7984')
    … (8 total)

`R10-CI-RATCHET-RED` — `done`, no commit, absorbed:

    'resume': {'stage': 'done', 'branch': 'handoff/r10-ci-ratchet-red', 'commit': None,
               'next_step': 'fixer',
               'note': 'Folded into R10-CI-LAYOUT PR 0 … not dispatched separately.'}

---

## E9. Liveness is written by a brief, not by an instrument (S4, S5)

    $ grep -rl 'tick/alive' ~/hpo-orch/r10s3 ~/hpo-seats/r10s3
    ~/hpo-orch/r10s3/orch/briefs/tick-watcher.md
    ~/hpo-orch/r10s3/orch/sweep-overlay.json
    ~/hpo-orch/r10s3/orch/briefs/sweep-current.txt
    ~/hpo-orch/r10s3/orch/sweep-prompt.txt
    $ grep -n 'alive' ~/hpo-orch/r10s3/orch/briefs/tick-watcher.md
    … `date -u +%FT%TZ > ~/hpo-orch/r10s3/orch/tick/alive` each pass (the sweep's liveness signal).
    $ ps -eo command | grep -F 'alive' | grep -v grep      # no live writer
    (empty)
    $ ls -la ~/hpo-orch/r10s3/orch/tick/alive
    -rw-r--r--  1 USER          staff  21 Oct 20 13:49 ~/hpo-orch/r10s3/orch/tick/alive

`mcp__scheduled-tasks__list_scheduled_tasks` → `No scheduled tasks found.` The file
moves when an agent turn runs the command; the instrument that runs (`tick_loop.sh`)
never writes it.

The seat ledger's claim vs the process table:

    $ tail -1 ~/hpo-orch/r10s3/orch/SEATS.md
    LIVE(8): tick, vent, savbase, sensorpay, pump, refpriv, review-leaf, review-2345.
    $ ps -eo pid,ppid,etime,command | grep -E 'claude --output-format' | grep -v grep | wc -l
    2
    $ ps -eo pid,ppid,etime,command | grep -E ' (vent|savbase|sensorpay|pump|refpriv) ' | grep -v grep
    (empty)

False-result control: a supervised system would show a process per live seat or a
journal line naming each; neither exists.

---

## E10. The plan generator (S8, added mid-task)

    $ ls -la ~/hpo-orch/r10s3/REPLAN-EDGES.json ~/hpo-orch/r10s3/plan/gen.py
    -rw-r--r--  1 USER          staff   1610 Oct 17 23:06 ~/hpo-orch/r10s3/REPLAN-EDGES.json
    -rw-r--r--  1 USER          staff  12293 Oct 20 13:54 ~/hpo-orch/r10s3/plan/gen.py
    $ python3 -I - <<'PY'
    import json
    import os
    E=json.load(open(os.path.expanduser('~/hpo-orch/r10s3/REPLAN-EDGES.json')))
    R=json.load(open('/tmp/r10roster_branch.json')); G={g['group']:g for g in R['groups']}
    diff=[(k,sorted(g.get('after') or []),sorted(E.get(k,[]) if k in E else sorted(g.get('after') or [])))
          for k,g in G.items() if sorted(g.get('after') or []) != sorted(E.get(k, g.get('after') or []))]
    print("groups:",len(G),"in EDGES:",len(E),"absent from EDGES:",sum(1 for k in G if k not in E))
    print("groups whose edges differ:",len(diff))
    PY
    groups: 93 in EDGES: 34 absent from EDGES: 59
    groups whose edges differ: 27

Generator source (read at 13:49Z; it is being edited live):

    EDGES = json.load(open(B + "REPLAN-EDGES.json"))
    edges = {g: list(EDGES.get(g, groups[g].get("after", []))) for g in groups}   # scratch wins
    groups["R10-ARCH-DOCS"] = {... "resume": {"stage": "not-started"}}            # roster override
    LIVE = {...14 seats...}; MERGED = {...25 group→PR...}; HOURS = {"S":5,...}    # carried
    open_iss = len([i for i in json.load(open(B + "plan-issues-open.json")) if i["number"] != 201])

The publish path the sweep names does not exist:

    $ ls ~/hpo-orch/r10s3/plan/round-10-plan.html
    ~/hpo-orch/r10s3/plan/round-10-plan.html
    $ ls '/private/tmp/claude-501/…/scratchpad/round-10-plan.html'
    No such file or directory

True open issues excluding `#201` (the corrected figure, 45):

    $ gh issue list -R tvofi/heatpump_optimizer --state open --limit 200 --json number \
        --jq '[.[] | select(.number != 201)] | length'
    45

(`gh api 'repos/…/issues?state=open' --paginate --jq '[.[] | select(.pull_request==null)] | length'` → 46, including `#201`; 3 open pull requests are not issues in that listing's sense.)

`roster_edit.py` has no `set-after`:

    $ grep -n 'op", choices' tools/audit/seat/roster_edit.py
    p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue", "append-group",
                                  "edit-brief", "append-carry", "set-resume", …

---

## E11. The sweep's overlay has drifted

    $ cat ~/hpo-orch/r10s3/orch/sweep-overlay.json   (the session-local overlay)
    transcript: ~/.claude/projects/-Users-…-audit-round-10-orchestration-eaa727/9d5c75e8-….jsonl
    plan_artifact: /private/tmp/claude-501/…-audit-round-10-orchestration-eaa727/…/scratchpad/round-10-plan.html
    plan_generator: python3 ~/hpo-orch/r10s3/plan/gen.py
    $ ls -la ~/.claude/projects/-Users-…-audit-round-10-orchestration-eaa727/9d5c75e8-….jsonl
    -rw-------  1 USER          staff  92219016 Oct 20 08:18 …9d5c75e8-….jsonl
    $ ls -lat ~/.claude/projects/ | head -3
    drwx------  4 … -Users-…--claude-worktrees-peaceful-clarke-53d260
    drwx------ 17 … .
    drwx------  3 … -Users-…--claude-worktrees-audit-round-10-fixing-de8016

The overlay names a transcript that last grew at 08:18Z (the orchestrator session
was resumed under a new id); `policy_reread_check.py` against it still answers `OK`
because the stamp is newer than the last compaction in that file:

    $ python3 -I tools/audit/seat/policy_reread_check.py \
        --transcript ~/.claude/projects/…/9d5c75e8-….jsonl \
        --stamp ~/hpo-orch/r10s3/orch/policy-read.stamp
    OK (read 2026-10-20T11:22:27Z > compaction 2026-10-20T05:51:47.219Z)

A check reading a *different session's* transcript cannot see this session's
compactions.

---

## E12. The self-tests pass while the defects are present (the control against a check that lies)

    $ python3 -I tools/audit/seat/orchestrator_tick.py --self-test | tail -1
    orchestrator_tick self-test: 150 checks, 0 failed
    $ bash tools/audit/seat/cloud_relay.sh --self-test | tail -1
    cloud_relay self-test: 74 checks, 0 failed
    $ bash tools/audit/seat/tick_loop.sh --self-test | tail -1
    tick_loop self-test: 4 checks, 0 failed

None of the three fails on S1 (the OWED fold), S6 (the fail-open adapter) or S7
(no timeout). This is the demonstration `defect-root-cause.md` asks for, in the
direction that matters: a check that passes while the bug is present converts an
open defect into a closed one.

---

## E13. Worktrees and residue (crash-survival surface)

    $ git -C ~/heatpump_optimizer worktree list | wc -l
    92
    $ git -C ~/heatpump_optimizer worktree list --porcelain | awk '/^worktree /{print substr($0,10)}' |
        sed -E 's|^/private/var/folders/.*|/private/var/folders/...|; s|^.*/hpo-seats/[^/]+/[^/]+/.*|~/hpo-seats/<seat>/...|' |
        sort | uniq -c | sort -rn | head -4
     48 /private/var/folders/...
     23 ~/hpo-seats/<seat>/...

48 worktrees live under the session temp root (mutation tables, `env_drift`
baselines) with no process after the run; `git worktree list` sees them, nothing
collects them. `df -h /` → 9.1 GiB free at 13:49Z, which is above the sweep's
6 GiB floor.

---

## E14. State surfaces

    $ git ls-tree --name-only origin/main dev/programme/delivery/ | wc -l
    791
    $ gh api 'repos/tvofi/heatpump_optimizer/issues/201' --jq '.comments'
    1875
    $ gh api 'repos/tvofi/heatpump_optimizer/issues/201/comments?per_page=100&sort=created&direction=desc' \
        --jq '.[0:1] | .[] | .created_at'
    2026-09-01T23:24:46Z
    $ gh api 'repos/tvofi/heatpump_optimizer/issues/201/comments?per_page=100&page=19' \
        --jq '.[-3:][] | [.created_at, .user.login] | @tsv'
    2026-10-20T11:05:14Z  tvofi
    2026-10-20T11:21:34Z  hpo-author[bot]
    2026-10-20T11:28:02Z  tvofi

The first query (with `sort=created&direction=desc`) returns the **oldest**
comment — the endpoint ignores both — so "the newest record on `#201`" requires the
last page (page 19 of 19). Any check that reads page 1 reads the beginning of the
programme.

    $ tail -20 ~/hpo-orch/r10s3/beat.log | head -6
    round state: handoff/audit-r10-plan at handoff/round10/state/
    generated handoff/round10/state/NEXT-SESSION-PROMPT.md: 3236 bytes
    generated handoff/round10/state/PLAN-TABLE.md: 21688 bytes
    generated handoff/round10/state/RESUME-CURRENT.md: 1497 bytes
    pushed handoff/audit-r10-plan at 9ba5ac1b588ccaa9f2a03229d11703c768d193ca
    $ cat ~/hpo-orch/r10s3/beat.tip
    a2b25bbc5518b5cb212429fdd623b5d33634fd08 541868d6f2c2b1684d610d8627dfb785fef8d15d

The beat's memo is a file, and the tip is written only on a 0 — the one state
store in the machinery that already recovers correctly from a refused push.

---

## E15. Processes at measurement time

    $ ps -eo pid,ppid,etime,time,stat,command | awk 'length($0)<220' | grep -E 'python|bash|node'
    35000     1 01:34:06  bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    35031     1 01:31:47  ~/.local/state/hpo/venv-ci/bin/python3 -u tools/audit/seat/state_docs.py beat --push --mirror ~/hpo-orch/r10s3/state --watch-ref refs/heads/main --tip-file ~/hpo-orch/r10s3/beat.tip
    35037     1 01:34:06  bash -c while :; do bash tools/audit/seat/wt_sync.sh --scratch ~/hpo-orch/r10s3/orch; sleep 900; done
    … (mutation_table.py, features.py, card.mjs, prepr.sh children)
    $ ps -o pid,ppid,etime,time -p 3928,3930
     3928  1007 02:17:22 0:00.00
     3930  3928 02:17:22 10:35.79

Three daemons, all PPID 1, all identified only by a pid nothing records. One live
harness process tree. `lsof -p 35031` → stdout/stderr to
`~/hpo-orch/r10s3/orch/state-beat.log`; `lsof -p 35037` → `wtsync.log`.

    $ grep -c '^synced' ~/hpo-orch/r10s3/orch/wtsync.log
    382

---

## E16. Git availability (S6's premise, and the null control)

    $ which -a git
    /usr/bin/git
    /opt/homebrew/bin/git
    $ git --version
    git version 2.54.0 (Apple Git-157)
    $ xcode-select -p
    /Library/Developer/CommandLineTools
    $ grep -rn '/usr/bin/git' tools tests .github .claude
    tests/entities.py:19252: … f'103 execve("/usr/bin/git", …) = 0\n'

The breakage in E4 was transient: the same command succeeds now. Nothing in the
tree hardcodes `/usr/bin/git`; the dependency is `git` on `PATH`, which resolves to
the Apple shim over CommandLineTools — so a missing CommandLineTools breaks every
instrument at once, and the only thing that could notice is a pass rc that the
relay does not produce.
