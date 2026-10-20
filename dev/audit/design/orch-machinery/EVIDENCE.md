# Evidence for the orchestration-machinery design (revision 2)

Commands and output for every figure in `DESIGN.md`. Host paths are written `~`
and the owner column of an `ls -la` output is shown as `USER` (the docs go to a
ref; `ref_privacy.py` exists so a push does not publish the host). Times are UTC
unless marked local. `load1` is quoted beside every timing claim.

Run from the design worktree unless a command names another directory:

    git -C ~/heatpump_optimizer worktree add ~/hpo-seats/r10s3/orch-design/wt \
        -B handoff/orch-machinery origin/main
    cd ~/hpo-seats/r10s3/orch-design/wt      # HEAD a2b25bbc5

Live state re-read 2026-10-20T11:38Z–12:24Z, `load1` 42.9–82.6 on 8 cores
(`sysctl -n hw.ncpu` → 8; `uptime` → `load averages: 42.95 57.47 60.92`).
Revision 1's ERRORS are corrected here and listed in DESIGN.md §10; the
reviewer's perturbed figures (its V2, V8, V11, V16, V17) are re-derived below.

---

## E1. Inventory row count and tree size

    $ grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md
    50
    $ grep -o '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md |
        sed 's/^| M//' | sort -n |
        awk 'NR != $1 { print "gap at", $1; bad=1 } END { exit bad }'
    (no gap; exit 0)
    $ git ls-tree --name-only HEAD tools/audit/seat/ | wc -l
    52
    $ ls tools/audit/seat | wc -l
    53
    $ ls -A tools/audit/seat | grep -i pycache
    __pycache__
    $ git status --ignored --porcelain tools/audit/seat | head -1
    !! tools/audit/seat/__pycache__/
    $ grep -l -- '--self-test' tools/audit/seat/* | grep -vc '\.md$'
    37
    $ wc -l tools/audit/seat/* tools/audit/seat/*.md | tail -1
    22793 total

N1-R correction: the tree holds **52** entries at both revision heads; a live
checkout's `ls` returns 53 because of an ignored `__pycache__/`. No tree file
changed between revisions, so revision 2's "instruments land" explanation was
false. The 37 self-testing scripts figure stands.

---

## E2. The disposal figure, sha-aware (B1 correction)

Revision 1 compared ref **names** (`comm`) and concluded "201 re-owed at a
different sha". The sha-aware comparison:

    $ python3 -I - <<'PY'
    import collections
    L=os.path.expanduser('~/.local/state/hpo/cloud-relay.log')
    D=os.path.expanduser('~/.local/state/hpo/cloud-disposed')
    last={}
    for line in open(L):
        f=line.split()
        if len(f)>=5 and f[0]=='OWED' and f[2] in ('handoff-no-pr','probe-ref'):
            last[(f[2],f[3])]=f[4]
    ...
    PY
    disposed lines: 210 distinct refs: 203
    last-owed sha == disposed: 199 different: 3
      moved: ('refs/heads/handoff/audit-r10-roster', 'b932ecc9…', '0321c901…')
      moved: ('refs/heads/handoff/r10-ci-layout-p0', 'dd3a4447…', '385b3a0d…')
      moved: ('refs/heads/handoff/audit-r10-plan', 'b90c1053…', '6691dd18…')
    disposed refs with no OWED line in the log: 1

So of **202 comparable** dispositions, **199 sit at exactly their disposed sha**
and **3 moved** (the plan ref, the roster and `r10-ci-layout-p0` — the branches
that move) (N6-R: 210 lines, 203 distinct refs, **209 distinct lines** — seven
repeated ref entries, one an exact duplicate; the import takes the last
disposition per ref). The ledger is still required for the reason that survives:

    $ awk '$1=="OWED" && ($3=="handoff-no-pr"||$3=="probe-ref"){print $4}' ~/.local/state/hpo/cloud-relay.log | sort -u | wc -l
    228
    $ grep -c 'cloud-disposed' tools/audit/seat/orchestrator_tick.py
    0
    $ grep -c 'disposed' tools/audit/seat/orchestrator_tick.py
    1        # the word in dispositions' docstring; the precise pattern is the claim

The tick never opens `cloud-disposed` (the precise pattern is 0; the looser
`disposed` matches one docstring word). 203 disposals silence nothing.

The board remains a projection of the log (unchanged, PASS):

    $ wc -c -l ~/hpo-orch/r10s3/orch/tick/tick.txt
    30079 3901380
    $ grep -c '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt
    29976
    $ grep '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt |
        sed -E 's/.* (refs\/heads\/[^ ]+|[a-z-]+) .*/\1/' | sort -u | wc -l
    229

---

## E3. Demonstration — the fold's blind grammar

    $ python3 -I - <<'PY'   # the real Tick.relay_owed on a four-line fixture
    ...
    PY
    OWED: OWED 2026-10-19T18:11:44Z probe-ref refs/heads/probe/y deadbeef…
    OWED: OWED 2026-10-19T18:11:44Z handoff-no-pr refs/heads/handoff/x deadbeef…
    findings: 2
    OWED: OWED 2026-10-19T18:11:44Z probe-ref refs/heads/probe/y deadbeef…
    OWED: OWED 2026-10-19T18:11:44Z handoff-no-pr refs/heads/handoff/x deadbeef…
    findings after dispose: 2

Null control: the relay-verdict OWED (`… 7 … bus.sh confirm failed`) followed by
`POSTED … 7 …` prints nothing. Source: `orchestrator_tick.py:relay_owed` keys on
`f[2]`, the PR for one grammar and the literal kind token for the others.

---

## E4. Demonstration — the relay's fail-open, and the double start

    $ HPO_STATE_DIR="$S/state" HPO_RELAY_PRS=true bash tools/audit/seat/cloud_relay.sh pass
    rc=0
    fatal: 'origin' does not appear to be a git repository
    cloud_relay: could not list handoff refs; will retry
    fatal: 'origin' does not appear to be a git repository
    cloud_relay: ls-remote failed; will retry

Live, in the running loop's log:

    $ grep -n '^===== daemonize' ~/hpo-orch/r10s3/orch/tick/loop.log
    1:     pid=46070 2026-10-19T18:11:31Z
    246:   pid=48658 2026-10-19T18:15:36Z
    23558: pid=30511 2026-10-20T06:54:19Z
    27536: pid=11552 2026-10-20T09:37:39Z
    27542: pid=12205 2026-10-20T09:38:06Z
    28593: pid=35000 2026-10-20T10:11:16Z
    $ sed -n '27536,27540p' ~/hpo-orch/r10s3/orch/tick/loop.log
    ===== daemonize pid=11552 2026-10-20T09:37:39Z argv: bash tools/audit/seat/tick_loop.sh …
    xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun …
    cloud_relay: could not list handoff refs; will retry
    xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun …
    cloud_relay: ls-remote failed; will retry
    TICK-PASS 2026-10-20T09:37:58Z relay=ok tick=0 out=~/hpo-orch/r10s3/orch/tick/tick.txt

Two launches 27 s apart under a 300 s interval: two loops. `tick_loop.sh` has no
`alive` write and no pidfile (`grep -n 'alive\|pidfile\|flock'` → none), and the
sweep template's step 5 restarts a tick *seat* on a stale `alive`.

False-result control: a healthy pass prints `relay=ok` with no `fatal:`/`xcrun`
lines; the defect is the combination, which the self-test never exercises
(`tick_loop.sh --self-test` stubs a relay that exits 0 or N).

---

## E5. The tick's achieved cadence

    passes: 144
    gaps min/median/mean/max: 74 399 438 2654
    gaps >600s: 5 of 143
    derived pass durations max 2354

Eight largest gaps: 08:53:44→09:37:58 (2654 s), 10:35:52→11:02:36 (1604),
06:35:35→06:55:19 (1184), 20:28:28→20:47:46 (1158), 19:39:09→19:50:31 (682).

False-result control: a 300 s interval with an instantaneous pass gives every gap
≈300 s and none over 600 s.

---

## E6. Demonstration — a live slot holder is stolen at expiry

    A took slot 0 pid 97905 expires 2026-10-20 11:53:11.542037+00:00
    A's named pid alive? True
    B STOLE the slot while A's process is alive: slot 0 now holder-B

Null control: `wait=False` before expiry raises `BlockingIOError`. Live context:

    $ cat /tmp/hpo-gate.lock/slots/slot-000
    label=prepr-48004
    expires_at=2026-10-20T12:03:33.110897+00:00
    taken_at=2026-10-20T11:33:33.110897+00:00
    pid=48004
    $ python3 -I tests/gate_lock.py status
    /tmp/hpo-gate.lock: expired label=r10-stamp expires_at=2026-10-20T11:10:05.554391+00:00 flock_available=True queue=-
    $ ps -eo pid,etime,command | grep 'prepr.sh' | grep -v grep | cut -c1-90
     7269 23:29 bash tools/pr/prepr.sh ~/hpo-seats/r10s3/fix-stamp/body.md
    14728 18:40 bash tools/pr/prepr.sh ~/hpo-seats/r10s3/dependabot-aiohttp/body/BODY.md
    63943 36:50 bash tools/pr/prepr.sh ~/hpo-seats/r10s3/record-body/repro/generated-at-head.md
    77712 32:40 bash tools/pr/prepr.sh ~/hpo-seats/r10s3/record-body/repro/generated-at-head.md
    94268 28:06 bash tools/pr/prepr.sh ~/hpo-seats/r10s3/fix-stamp/body.md

Five live runs at 18:40–36:50 elapsed against a 1800 s (30 min) lease: the
longest is already past it and stealable.

---

## E7. Prepr starvation, and the bound a job needs (B7)

    $ ps -o pid,ppid,etime,time,stat,command -p 47539,47826,48004,48265
     47539     1    16:09   0:00.04 Ss   bash tools/audit/seat/open_pr.sh r10-earlycutoff-coverage …
     47826     1    15:59   0:00.04 Ss   bash tools/audit/seat/open_pr.sh r10-i5-docs …
     48004 48003    15:53   0:00.07 S    bash …/prepr.sh …
     48265 48264    15:44   0:00.09 S    bash …/prepr.sh …
    $ tail -2 ~/.local/state/hpo/pr/r10-earlycutoff-coverage/p1.log
      ok       contract_rerun         contract_rerun self-test: 24 checks, 0 failed
    Terminated: 15

Both PPID 1, ~0.1 s CPU in the shell, a line per completed step only, both
`Terminated: 15` at 11:50:33Z. No timeout in the chain:

    $ grep -n 'timeout' tools/pr/prepr.sh tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh
    (no matches)

At the 12:20Z re-read, five live runs at 18:40–36:50 (E6). A job timeout below
that kills healthy work every pass, so `beatd`'s `handoff` job is bounded at
3600 s with a 60 s heartbeat, separate from `relay-probe` (120 s).

---

## E8. The roster: mismatches, short commits, gate coverage

93 groups, 47 open, 14 open gates (unchanged):

    $ python3 -I -c "…"   # roster walk
    groups: 93  stages: {'done': 46, 'not-started': 36, 'in-progress': 7, 'queued': 4}
    open (not done/rca-done): 47  owner_gate set: 14

**E8a — the matching rule applied (B13).** Topic = basename of `resume.branch`
(else the lowercased group id); a ref matches when its name, minus
`refs/heads/{handoff-body,handoff,fix}/` and a trailing `-pr`, equals the topic or
starts with `<topic>-`. At 12:20Z:

    open groups: 47 mismatches: 10
    ('R10-SENSOR-PAYLOAD', 'not-started', 'in-flight', 'r10-sensor-payload', [handoff-body/…, handoff/…])
    ('R10-I5-DOCS', 'not-started', 'in-flight', 'r10-i5-docs', …)
    ('R10-RCA-FRICTION', 'not-started', 'in-flight', 'r10-rca-harness-friction', …)
    ('R10-CI-LAYOUT', 'not-started', 'in-flight', 'r10-ci-layout', [handoff-body/r10-ci-layout-p0, handoff/r10-ci-layout-p0])
    ('R10-DEMAND-OVERBOOK', 'queued', 'no-artifact', …)
    ('R10-BUFFER-STORE', 'queued', 'no-artifact', …)
    ('R10-COP-PARTLOAD', 'queued', 'no-artifact', …)
    ('R10-UPDATE-PR-SIGNALS', 'queued', 'no-artifact', …)
    ('R10-HANDOFF-ARCHIVE', 'in-progress', 'no-artifact', …)
    ('R10-DEPENDABOT-AIOHTTP', 'in-progress', 'no-artifact', …)

Revision 1's nine omitted `R10-RCA-FRICTION` (its topic differs from its group
id) and stated a prefix rule it did not define; the set moves as seats work, so
the exact count is a reading, not a constant. `R10-I5-DOCS` beside a live opener:

    30023:-> R10-I5-DOCS: UNBLOCKED, not started -- start a fixer on handoff/r10-i5-docs

and the live `open_pr.sh` for it ran 11:33–11:50Z (E7).

**E8c — the short commits (B3 correction).**

    R10-VENT-DETECTOR 768bfc0c341d unique=1 ancestor_in_main=True
    R10-SAV-BASELINE 8cc1abc3a27d unique=1 ancestor_in_main=True
    R10-TICK-DRIVERS a96f4be4ac0a unique=1 ancestor_in_main=True
    R10-DIAG-REPLAY 0dac0bf8731a unique=1 ancestor_in_main=True
    R10-REF-PRIVACY a73f3320c53a unique=1 ancestor_in_main=True
    R10-RCA-STRUCTURE-BLIND f0a4acac7984 unique=1 ancestor_in_main=True
    R10-OPENPR-SILENT 7ab3030bbfff unique=1 ancestor_in_main=True
    R10-TICK-SELFTEST-CI c35302773738 unresolved here (may exist on an unfetched ref)

Seven resolve uniquely and are ancestors of `origin/main`; the length test
(`len(sha)==40`) is the defect, not the records.

**E8b — gate coverage under the mandate (B2 correction).** See E18 for the
mandate's text. Every one of the 14 open gates is class `code-owned` or `policy`
(**six** carry the exact string `mandated approval under 6175172275`; ten name
the mandate in some form; four name neither, all still `code-owned`/`policy`
classes). Under the design's predicate — is the gate's class covered by the
in-force mandate? — the answer is **14 ready / 0 owner**. Revision 1's 10/4 asked
whether the gate's *free text* named the mandate, which is S3's defect in a new
form.

Absorbed, with no merge of its own:

    'R10-CI-RATCHET-RED': {… 'resume': {'stage': 'done', 'commit': None,
      'note': 'Folded into R10-CI-LAYOUT PR 0 … not dispatched separately.'}}

---

## E9. Liveness (S4), with revision 1's command corrected (N2)

    $ tail -1 ~/hpo-orch/r10s3/orch/SEATS.md
    07:10Z Owed openers remain (no PR carries them): r10-roster-ops … Open-PR cap 6; 5 open now.
    $ grep -n '^LIVE(' ~/hpo-orch/r10s3/orch/SEATS.md | tail -1
    162:LIVE(8): tick, vent, savbase, sensorpay, pump, refpriv, review-leaf, review-2345.
    $ stat -f '%Sm' ~/hpo-orch/r10s3/orch/SEATS.md
    Oct 20 09:12:22 2026                      # local; 07:12Z
    $ ps -eo pid,ppid,etime,command | grep -E 'claude --output-format' | grep -v grep | wc -l
    2
    $ grep -rl 'tick/alive' ~/hpo-orch/r10s3 ~/hpo-seats/r10s3
    …/orch/briefs/tick-watcher.md  …/orch/sweep-overlay.json  …/sweep-current.txt  …/sweep-prompt.txt
    $ ps -eo command | grep -F 'alive' | grep -v grep
    (empty)
    $ ls -la ~/hpo-orch/r10s3/orch/tick/alive
    -rw-r--r--  1 USER  staff  21 Oct 20 13:49 …/tick/alive

`mcp__scheduled-tasks__list_scheduled_tasks` → `No scheduled tasks found.` The
`LIVE(8)` line is at 162 of 893, not the tail; the mtime is 09:12 local (07:12Z).
The file moves when an agent turn runs the command; no instrument writes it.

The seat checker that already exists (and that `beatd status` is **not**):

    $ sed -n '953,1014p' tools/audit/seat/orchestrator_tick.py
    def workers(self) -> None: … def one_worker(self, S, w) -> None:
        # STALLED? no PR pushed after the stall window; DONE? the PR head moved
        # since dispatch; OK (CI completed since dispatch)
    # input: --workers-file (JSON {seat, pr, head, dispatched_at, agent_kind})

The input is JSON already; the session keeps prose instead.

---

## E10. The plan generator, with the live-repair correction (B12)

    $ md5 ~/hpo-orch/r10s3/plan/gen.py
    446ce44181804dc5300d18fa000bf078        # unchanged since revision 1's read
    $ grep -n 'REPLAN-EDGES\|EDGES.get\|groups\["R10-ARCH-DOCS"\]\|plan-issues-open' ~/hpo-orch/r10s3/plan/gen.py
    10:open(B + "plan-issues-open.json","w") …
    17:groups["R10-ARCH-DOCS"] = {… "resume": {"stage": "not-started"}}     # PRESENT
    52:# The dependency graph is the roster's own `after` edges. A scratch REPLAN-EDGES.json used to …
    $ grep -n 'REPLAN-EDGES\|len(ISS)\|pr=f"#{MERGED' ~/hpo-orch/r10s3/plan/gen.py.bak
    4:EDGES = json.load(open(B + "REPLAN-EDGES.json"))                      # pre-fix shape
    148:open_iss = len(ISS) - 1                                            # pre-fix shape
    89:  pr=f"#{MERGED[g]}" if g in MERGED else PR.get(g, "—")             # pre-fix shape

At the cited file: defect 1 is **present**; 2, 3 and 4 were **repaired** while
revision 1 was reading it; 5 is **partial** (the status text says folded, the pill
class is still `done`). The `.bak` files are the recovered pre-fix source, so the
self-test arms are mutation pins over fixtures (DESIGN §6.7), not references to
the live file.

The scratch graph and publish path (unchanged):

    $ python3 -I - <<'PY'
    E=json.load(open('~/hpo-orch/r10s3/REPLAN-EDGES.json')); R=json.load(open('/tmp/r10roster_now.json'))
    …
    PY
    groups: 93 in EDGES: 34 absent from EDGES: 59 groups whose edges differ: 27
    $ ls '~/hpo-orch/r10s3/plan/round-10-plan.html'
    …/plan/round-10-plan.html
    $ ls '/private/tmp/claude-501/…/scratchpad/round-10-plan.html'
    No such file or directory

---

## E11. The unreadable contract the new readers must keep (B11)

The current model, `orchestrator_tick.py:relay_owed`:

    try: … open(self.relay_log) …
    except FileNotFoundError:   self.line(S, "cloud-relay log: none yet …"); return
    except OSError as e:        self.unreadable(S, "cloud-relay log", str(e)[:100]); return

First run is not a failure; an unreadable file is `UNREADABLE`. The design keeps
that split for `ledger.py` (both stores), `roster_sync.py` (ref/PR reads) and
`beatd.jobs.json` (refuse to start).

---

## E12. Self-tests pass with the defects present

    $ python3 -I tools/audit/seat/orchestrator_tick.py --self-test | tail -1
    orchestrator_tick self-test: 150 checks, 0 failed
    $ bash tools/audit/seat/cloud_relay.sh --self-test | tail -1
    cloud_relay self-test: 74 checks, 0 failed
    $ bash tools/audit/seat/tick_loop.sh --self-test | tail -1
    tick_loop self-test: 4 checks, 0 failed

None fails on the OWED fold, the fail-open adapter or the missing timeout.

---

## E13. Worktrees and residue

    $ git -C ~/heatpump_optimizer worktree list | wc -l
    92
    $ … | sed -E 's|^/private/var/folders/.*|/private/var/folders/...|' | sort | uniq -c
     48 /private/var/folders/...
     23 ~/hpo-seats/<seat>/...

48 worktrees under the session temp root with no process; nothing collects them.
`df -h /` → 9.1 GiB free at 13:49Z (above the sweep's 6 GiB floor).

---

## E14. State surfaces, and the four mechanisms revision 1 missed (B15)

    $ git ls-tree --name-only origin/main dev/programme/delivery/ | wc -l
    791
    $ gh api repos/tvofi/heatpump_optimizer/issues/201 --jq '.comments'
    1875
    $ gh api 'repos/…/issues/201/comments?per_page=100&sort=created&direction=desc' --jq '.[0].created_at'
    2026-09-01T23:24:46Z          # the endpoint ignores sort: this is the OLDEST
    $ gh api 'repos/…/issues/201/comments?per_page=100&page=19' --jq '.[-3:][] | [.created_at,.user.login] | @tsv'
    2026-10-20T11:05:14Z  tvofi
    2026-10-20T11:21:34Z  hpo-author[bot]
    2026-10-20T11:28:02Z  tvofi

The missing mechanisms:

    $ grep -n '^  delivery-status:\|^  delivery-status-publish:\|^  record:' .github/workflows/governance.yml
    990:  record:
    1243:  delivery-status:            # pull_request; timeout-minutes: 5
    1303:  delivery-status-publish:    # push to main; issues: write; concurrency cancel-in-progress
    $ sed -n '1303,1317p' .github/workflows/governance.yml
      delivery-status-publish:
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        permissions: {contents: read, issues: write}
        concurrency: {group: delivery-status-publish, cancel-in-progress: true}
        # Regenerate the ledger and put it in #201's region
    $ ls -la tests/delivery_status.py
    -rw-r--r--  1 USER  staff  34937 Oct 20 13:43 tests/delivery_status.py   # the credential-free ledger builder
    $ cat tools/audit/seat/codeql-triage-poll.sh | head -4
    # Dismiss the 3 #1769 evidence-alerts … for i in $(seq 1 36); do sleep 600 …
    $ grep -n 'JOB=$(gh api … .*109534061903\|H=3ad6e085' tools/audit/seat/codeql-triage-poll.sh
    16: JOB=$(… echo 109534061903)
    23: H=3ad6e085accc2254dbf816ae1a105eb7caeb925c
    $ grep -n 'MERGE-READY\|BLOCKED-UNFIXED' tools/audit/seat/orchestrator_tick.py | head -3
    647: MERGE-READY: #N <head8>   merge at the current head, CLEAN or UNSTABLE;
    677: self.line(S, f"MERGE-READY: #{n} {head[:8]}", flag=True)

`bus.sh`'s own posted state (B16):

    $ wc -l ~/.zcode/bus/posted ~/.zcode/bus/dispatched
    546 ~/.zcode/bus/posted
    686 ~/.zcode/bus/dispatched
    $ grep -n 'logline OWED\|printf .OWED reviewer-fire' tools/audit/seat/cloud_relay.sh
    93,157,211,215,218,221,223,231   # the relay still appends OWED lines to its log

So `#201` has a comment writer and a body-region writer; `bus.sh confirm` already
owns `posted`; the relay keeps a second OWED store.

---

## E15. Processes

    $ ps -eo pid,ppid,etime,time,stat,command | awk 'length($0)<220' | grep -E 'python|bash|node'
    35000     1 01:34:06  bash tools/audit/seat/tick_loop.sh --out ~/hpo-orch/r10s3/orch/tick/tick.txt
    35031     1 01:31:47  …/venv-ci/bin/python3 -u tools/audit/seat/state_docs.py beat --push --mirror …
    35037     1 01:34:06  bash -c while :; do bash tools/audit/seat/wt_sync.sh --scratch …; sleep 900; done
    … mutation_table.py, features.py, card.mjs, prepr.sh children
    $ lsof -p 35031 | awk '$4 ~ /^[12]w/{print $9}'
    ~/hpo-orch/r10s3/orch/state-beat.log
    $ lsof -p 35037 | awk '$4 ~ /^[12]w/{print $9}'
    ~/hpo-orch/r10s3/orch/wtsync.log

Three daemons, all PPID 1, identified only by a pid nothing records.

---

## E16. Git availability and the CI-wiring seam (B5)

    $ git --version; xcode-select -p
    git version 2.54.0 (Apple Git-157)
    /Library/Developer/CommandLineTools
    $ grep -rn '/usr/bin/git' tools tests .github .claude
    tests/entities.py:19252: … f'103 execve("/usr/bin/git", …) = 0\n'

The breakage was transient; the dependency is `git` on `PATH`. CI wiring:

    $ python3 -I tools/audit/seat/selftest_wiring.py --check
    selftest_wiring: 37 self-testing, 37 wired, 0 unwired
    $ python3 -I -c "import json;r=json.load(open('/tmp/r10roster_now.json'));print([g.get('files') for g in r['groups'] if g['group']=='R10-CI-LAYOUT'])"
    [['.github/workflows/tests.yml', '.github/workflows/governance.yml', '.github/workflows/ci.yml']]

Any new `--self-test` file must be named by a `run:` line in one of those three
files — exactly R10-CI-LAYOUT's file list.

---

## E17. The reconciler's owner (B4): R10-ROSTER-OPS's brief

    $ git log -1 --format='%h %ci %s' 541868d6f2c2b1684d610d8627dfb785fef8d15d
    541868d6f 2026-10-20 13:35:54 +0200 roster_edit edit-brief R10-ROSTER-OPS (tools/audit/seat/roster_edit.py)
    $ git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | …
    R10-ROSTER-OPS brief:
      "… Additionally (tvofi, 2026-10-20): make the FACTUAL half of roster upkeep mechanical
       inside the beat … Add a `roster_sync.py --apply` run by `state_docs.py beat` that derives
       only what the repository measures — a group whose `resume.branch` has a MERGED pull request
       becomes `done` …; one whose `resume.branch` has an OPEN pull request becomes `in-progress`
       with its number … It must never overwrite a human-written `deferred` or `refused` stage,
       must be a dry run by default with `--apply` to write … go out through `roster_edit.py`'s
       load-validate-dump and lint gate. …"
    $ for ref in 541868d6f origin/handoff/audit-r10-roster origin/main origin/handoff/r10-roster-ops; do
        git cat-file -e "${ref}:tools/audit/seat/roster_sync.py" && echo PRESENT || echo absent; done
    absent ×4
    $ git log --all --oneline -- tools/audit/seat/roster_sync.py
    (empty)

The **requirement** is in R10-ROSTER-OPS's brief at `541868d6f`; the file exists
on no ref yet. The design therefore names R10-ROSTER-OPS as the single owner and
adds only three predicates to that brief (gate coverage, absorbed-edge closure,
commit resolution) — it does not add a second reconciler.

---

## E18. The mandate's text (B2)

    $ gh api repos/tvofi/heatpump_optimizer/issues/comments/6175172275 --jq '.body'
    MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z

    Exceptional round-10 programme mandate, granted by tvofi in session on 2026-10-14.
    It covers codeowner, policy and budget-raise approvals. It is posted at tvofi's
    request and has not been edited.

Under "is the gate's class covered by the in-force mandate?", all 14 open gates
(`code-owned`/`policy` classes) are ready.

---

## E19. Never-disposed subjects and vanished refs (B10)

    OWED subjects: 228  disposed refs: 203  never-disposed subjects: 26
      gone from origin: 13  still present: 13
      still present: handoff-body/{r10-earlycutoff-coverage, r10-i5-docs,
        r10-merge-pr-mandate, r10-rca-harness-friction, r10-roster-ops,
        r10-setpoint-boost}, handoff/{r10-earlycutoff-coverage, r10-i5-docs,
        r10-merge-pr-mandate, r10-rca-harness-friction, r10-roster-ops,
        r10-setpoint-boost}, handoff/orch-machinery

The counts move (the reviewer measured 19 of 32 gone at 12:07Z). A ledger without
a `subject-absent` close would carry the vanished half forever; a ledger that
treats `handoff/audit-r*-plan` and `handoff/audit-r*-roster` as handoff branches
carries two permanent obligations. Both are answered in DESIGN §6.3.

---

## E20. The import's classification and the live OWED shapes (B10-R)

    $ awk '{print $1}' ~/.local/state/hpo/cloud-disposed | sort -u |
        sed -E 's#(refs/heads/[a-z-]+/).*#\1#' | sort | uniq -c
     89 refs/heads/handoff-body/
    113 refs/heads/handoff/
      1 refs/heads/probe/
    $ wc -l < ~/.local/state/hpo/cloud-disposed; sort -u ~/.local/state/hpo/cloud-disposed | wc -l
    210
    209
    $ awk '{print $1}' ~/.local/state/hpo/cloud-disposed | sort | uniq -c | awk '$1>1'
       2 refs/heads/handoff/audit-r10-roster
       6 refs/heads/handoff/r10-rca-worktree-vanish
       2 refs/heads/probe/cloud-seat-20261018

Three classification arms, not two: `refs/heads/probe/` → `probe-ref`;
`refs/heads/handoff/` **and `refs/heads/handoff-body/`** → `handoff-no-pr`
(89 + 113 + 1 = 203). Seven repeated ref entries (one exact duplicate line,
six same-ref-different-sha re-disposals); the import takes the **last**
disposition per ref.

    $ awk '$1=="OWED"{print ($2 ~ /^[0-9]{4}-/ ? $3 : $2)}' ~/.local/state/hpo/cloud-relay.log | sort | uniq -c
    29890 handoff-no-pr
       10 handoff-update
      151 probe-ref
        1 reviewer-fire
    $ grep -c 'logline OWED "approve-held-runs\|logline OWED "dispatch' tools/audit/seat/cloud_relay.sh
    2          # both code paths exist, 0 live lines at this read

`handoff-update` (10 live lines) is the fifth live shape; in the ledger it is a
derived kind whose state is `handoff-failed.tsv` (`<topic> <code-sha>`), closed by
a successful update or superseded when the ref moves; `approve-held-runs` and
`dispatch` are reasons on it, not kinds. A relay OWED shape with no ledger kind is
a refusal.

---

## E21. Timing anchors for the relay jobs (N9-R)

    $ uptime
    load averages: 50.04 50.21 47.69
    $ /usr/bin/time -p sh -c 'git ls-remote --heads origin "refs/heads/probe/*" >/dev/null'
    real 0.99   user 0.06   sys 0.09
    $ /usr/bin/time -p bash tools/audit/seat/cloud_relay.sh --self-test
    cloud_relay self-test: 74 checks, 0 failed
    real 56.54  user 12.14  sys 15.54     # ~8 relay fixtures => ~7 s per relay
    $ uptime
    load averages: 145.66 75.27 57.07     # the self-test itself loads the box

The probe pass is one `ls-remote` (0.99 s at load1 50); a relay pass adds fetch,
archive, grading and `push-verdict` (~7 s per ref in the fixture path, which also
loads the box). The `relay-probe` 120 s timeout is therefore a **first cut**, not
an end-to-end measurement of a pass with several refs — stated as such in §6.2.

---

## E22. The mandate scope grammar and the class mapping (N10-R)

    $ grep -n 'MANDATE_GRAMMAR\|MANDATE_COVERS' tools/policy/budget_raise_gate.py | head -5
    112: MANDATE_GRAMMAR = re.compile(rf"MANDATE: agents may approve as {OWNER_LOGIN}, scope (code-owned|budget-raise|all), …")
    116: MANDATE_COVERS_RAISE = ("budget-raise", "all")
    121: MANDATE_COVERS_POLICY = ("all",)
    $ sed -n '117,121p' tools/policy/budget_raise_gate.py
    # What covers the merge train landing a POLICY head …: only `all`. A `code-owned`
    # scope licenses an approval of a code-owned path, and a `budget-raise` scope a
    # raise; neither is the owner's written authority for the train to land their
    # written record.

Mapping: `code-owned` ← `code-owned|all`; `budget` ← `budget-raise|all`;
`policy` ← `all` only. The only live mandate is scope `all`, so 14/0 is unchanged
by the mapping; a narrower mandate would be read correctly.
