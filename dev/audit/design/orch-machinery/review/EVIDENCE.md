# Evidence for the independent review of the orchestration-machinery design

Design under review: `handoff/orch-machinery` at
`2b159e4662f87e4cbfdb96c6b00bdffa9bc49ed1`. Read from a detached worktree at that
SHA; live state re-read 2026-10-20T12:07Z–12:20Z, `load1` 43.1–50.5 on 8 cores.
Host paths are written `~`; the owner column of `ls -la` is not reproduced.
Where a live state figure moved since the design's 11:38Z–11:56Z read, both the
design's figure and mine are named.

Commands are shown with the output I got. A command whose live state had moved
away is marked UNVERIFIED in `REVIEW.md`, never PASS.

---

## V1. Inventory row count and tree size (design E1)

    $ grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md
    46
    $ grep -o '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md |
        sed 's/^| M//' | sort -n | awk 'NR != $1 { print "gap at", $1; bad=1 } END { if (!bad) print "contiguous 1.." NR; exit bad }'
    contiguous 1..46

The row count is right. The two tree-size figures beside it are not:

    $ ls tools/audit/seat | wc -l
    52
    $ git ls-tree --name-only HEAD tools/audit/seat/ | wc -l
    52
    $ git ls-tree --name-only a2b25bbc5 tools/audit/seat/ | wc -l   # the design's read head
    52
    $ grep -l -- '--self-test' tools/audit/seat/* | wc -l
    38
    $ grep -l -- '--self-test' tools/audit/seat/* | grep -v '\.md$' | wc -l
    37
    $ grep -l -- '--self-test' tools/audit/seat/*.md
    tools/audit/seat/INSTRUMENTS.md
    $ wc -l tools/audit/seat/* tools/audit/seat/*.md | tail -1
    22793 total

So the design's "53 entries" is 52 at its own cited head, and its "38 with a
`--self-test`" counts `INSTRUMENTS.md`, a document: 37 scripts carry one. The
22,793-line figure reproduces.

## V2. The board and the relay log (design E2/S1)

    $ date -u +%FT%TZ
    2026-10-20T12:07:16Z
    $ wc -c -l ~/hpo-orch/r10s3/orch/tick/tick.txt
      30101 3904304 ~/hpo-orch/r10s3/orch/tick/tick.txt
    $ tail -1 ~/hpo-orch/r10s3/orch/tick/tick.txt
    DISPATCH LIST: 30038 finding(s)
    $ grep -c '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt
    30000
    $ grep '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt |
        sed -E 's/.* (refs\/heads\/[^ ]+|[a-z-]+) .*/\1/' | sort -u | wc -l
    229
    $ python3 -I -c "print(round(30000/229,1))"
    131.0

Design at 11:38Z: 30,014 findings, 29,976 OWED, 229 subjects, 130.9x. Mine at
12:07Z: 30,038 findings, 30,000 OWED, 229 subjects, 131.0x. The state grew; the
claim (the board is a projection of the log) holds. The design's own S1 text
says "30,014 findings"; the review brief says 30,006 OWED — the design's 29,976
was the OWED count at its read.

OWED lines by kind, from the board:

    $ grep '^-> OWED:' ~/hpo-orch/r10s3/orch/tick/tick.txt |
        sed -E 's/^-> OWED: OWED( [0-9T:Z-]+)? ([a-z-]+).*/\2/' | sort | uniq -c
    29838 handoff-no-pr
       10 handoff-update
      151 probe-ref
        1 reviewer-fire

The source log:

    $ wc -l -c ~/.local/state/hpo/cloud-relay.log
    30013 3627393 ~/.local/state/hpo/cloud-relay.log
    $ grep -c '^OWED ' ~/.local/state/hpo/cloud-relay.log
    30013
    $ grep -c '^POSTED ' ~/.local/state/hpo/cloud-relay.log
    0
    $ wc -l < ~/.local/state/hpo/cloud-disposed
    210

The live log carries **zero** POSTED lines: in the live data nothing cancels,
including the `reviewer-fire` shape. Its grammar is `OWED reviewer-fire <pr>
<head40> <nonce> <utc>` — no leading timestamp — so its `f[2]` is the PR number
(the design's "three of four shapes cannot cancel" is right on the code's key,
but the fourth is closed by nothing in the live log either).

Existence of the log's subjects on the remote (keys kept as full
`refs/heads/...`, which the first cut of this analysis got wrong by stripping
`refs/heads/` from one side only — corrected here):

    $ python3 -I -   # last OWED ref-subject set vs git ls-remote origin
    log ref-subjects: 234
      still exist remotely: 215
      gone from remote: 19
    never-disposed: 32  still exist: 13  gone: 19
    owed+disposed: 202  last==disp: 199  moved: 3
    of owed+disposed, still exist: 202  gone: 0
    of moved: handoff/audit-r10-plan (current 6691dd18),
              handoff/audit-r10-roster (current 3a8846a2),
              handoff/r10-ci-layout-p0 (current dd3a4447)

So 215 of the 234 subjects still exist; 19 are gone. 202 carry a disposal (all
202 still exist); at the read that produced the block above, 200 of the 202 were
at exactly their disposed sha and the two that were not are the live plan/roster
state refs, which move. 32 subjects never had a disposal, of which 13 still
exist and 19 are gone. Two of the always-owed refs — `handoff/audit-r10-plan`
and `handoff/audit-r10-roster` — are long-lived state refs, not handoff
branches, so the relay's `handoff-no-pr` rule owes them permanently.

### V2a. The "re-owed at a different sha" figure — the design's claim fails

The design's E2 command compares **ref names only**:

    $ comm -12 <(grep ' handoff-no-pr ' ~/.local/state/hpo/cloud-relay.log | awk '{print $4}' | sort -u) \
               <(awk '{print $1}' ~/.local/state/hpo/cloud-disposed | sort -u) | wc -l
    201

It cannot show "at a different sha". Comparing the shas does:

    $ python3 -I -   # the last OWED sha for each ref vs its disposed sha
    owed+disposed: 202
    last-owed sha == disposed sha: 199
    last-owed sha != disposed sha: 3
    first-owed sha == disposed sha: 192
    sample same: [('refs/heads/handoff-body/audit-r10-roster', 'c025e447', 'c025e447'), ...]
    sample diff: [('refs/heads/handoff/audit-r10-plan', '6691dd18', 'b90c1053'),
                  ('refs/heads/handoff/audit-r10-roster', 'ef7a9340', 'b932ecc9'),
                  ('refs/heads/handoff/r10-ci-layout-p0', '385b3a0d', 'dd3a4447')]

199 of 202 disposed refs were last owed at **exactly** the sha they were disposed
at; only 3 moved after disposal. The design's "201 re-owed at a new sha" (S1,
§3.2, E2) is a claim its own command does not test and the data contradicts. The
three that moved are the three live moving branches (plan ref, roster,
ci-layout-p0), which is the relay's documented rule firing correctly — not a
201-entry failure.

## V3. The fold's blind grammar (design E3)

    $ python3 -I - <<'PY'
    ... Tick.relay_owed over a four-line fixture ...
    PY
    OWED: OWED 2026-10-19T18:11:44Z probe-ref refs/heads/probe/y deadbeef...
    OWED: OWED 2026-10-19T18:11:44Z handoff-no-pr refs/heads/handoff/x deadbeef...
    findings: 2
    OWED: ... probe-ref ...
    OWED: ... handoff-no-pr ...
    findings after dispose: 2

Identical to the design's E3. The verdict OWED cancels against its POSTED (the
null control holds); the two ref-keyed lines survive a disposal. Source
confirmed: `relay_owed` has an explicit `OSError -> self.unreadable(...)` branch,
and the only reader of `cloud-disposed` is `cloud_relay.sh`'s own `disposed()`
predicate:

    $ grep -n 'cloud-disposed' tools/audit/seat/*.py tools/audit/seat/*.sh
    tools/audit/seat/cloud_relay.sh:140:  local f=.../cloud-disposed; [ -f "$f" ] && grep -qxF "$1 $2" "$f"; }
    tools/audit/seat/cloud_relay.sh:147:  ... echo "$1 $2" >> "$state/cloud-disposed" ...

## V4. The relay's fail-open (design E4)

    $ S=$(mktemp -d ~/hpo-seats/r10s3/rev-orch-machinery-ev/relaydemo.XXXXXX); cd "$S"
    $ HPO_STATE_DIR="$S/state" HPO_RELAY_PRS=true \
        bash .../tools/audit/seat/cloud_relay.sh pass > out 2>&1
    $ echo "rc=$?"; cat out
    rc=0
    fatal: 'origin' does not appear to be a git repository
    fatal: Could not read from remote repository.
    ...
    cloud_relay: could not list handoff refs; will retry
    fatal: ...
    cloud_relay: ls-remote failed; will retry

rc 0 with both remote reads failing, and nothing written under the throwaway
state dir. The live instance is the same shape:

    $ sed -n '27536,27540p' ~/hpo-orch/r10s3/orch/tick/loop.log
    ===== daemonize pid=11552 2026-10-20T09:37:39Z argv: bash ... tick_loop.sh ...
    xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: ...
    cloud_relay: could not list handoff refs; will retry
    xcrun: error: invalid active developer path (...), missing xcrun at: ...
    cloud_relay: ls-remote failed; will retry
    TICK-PASS 2026-10-20T09:37:58Z relay=ok tick=0 out=~/hpo-orch/r10s3/orch/tick/tick.txt

`tick_loop.sh:26-27` maps rc 0 to `relay=ok`, so the fail-open is carried
faithfully into the board line.

## V5. Tick launches and cadence (design E4/E5)

    $ grep -c '^===== daemonize' ~/hpo-orch/r10s3/orch/tick/loop.log
    6
    $ grep -n '^===== daemonize' ~/hpo-orch/r10s3/orch/tick/loop.log
    1:... pid=46070 2026-10-19T18:11:31Z ...
    246:... pid=48658 2026-10-19T18:15:36Z ...
    23558:... pid=30511 2026-10-20T06:54:19Z ...
    27536:... pid=11552 2026-10-20T09:37:39Z ...
    27542:... pid=12205 2026-10-20T09:38:06Z ...
    28593:... pid=35000 2026-10-20T10:11:16Z ...

The 09:37:39 / 09:38:06 pair is 27 s apart against a 300 s interval: two loops.
Recomputed cadence:

    passes: 146
    span h: 17.7
    gaps min/median/mean/max: 74 400 440 2654
    gaps >600s: 6 of 145
    derived pass durations max 2354
    passes/h: 8.2
    largest gaps:
      08:53:44 -> 09:37:58 2654
      10:35:52 -> 11:02:36 1604
      06:35:35 -> 06:55:19 1184
      20:28:28 -> 20:47:46 1158
      19:39:09 -> 19:50:31  682

Design: 144 passes, 8.2/h, median 399, max 2654, 5 of 143 >600. Mine: 146,
8.2/h, median 400, max 2654, 6 of 145. PASS.

## V6. Live slot holder stolen at expiry (design E6)

    $ python3 -I - "$T" <<'PY'   # throwaway lock dir, gate_lock.take_slot
    A took slot 0 pid 25120 expires 2026-10-20 12:06:19+00:00
    A's named pid alive? True
    B STOLE the slot while A's process is alive: slot 0 now holder-B

Null control (the same call shape before expiry): `B blocked before expiry (null
control holds): all 1 heavy slots held: 0:holder-A until ...`.

Source: `_free_slot` steals on `owner.expired or _orphaned(pool, owner)`; the
expiry arm does not probe the named pid (`tests/gate_lock.py:474-494`).

Live context at 12:12Z, three `prepr.sh` holders, all named pids alive:

    $ python3 -I tests/gate_lock.py slot-status
    /tmp/hpo-gate.lock/slots: 3/4 slots held [0:prepr-94268(live), 1:prepr-14728(live), 2:prepr-63943(live)] queue=-
    $ for p in 94268 14728 63943; do ps -p $p -o pid=,etime=; done
    14728 10:18
    94268 19:44
    63943 28:28
    # slot-002 (prepr-63943) taken_at 11:43:34Z, expires_at 12:13:34Z

The design's E6 live figures were 12:03:33Z leases on the 11:33Z runs; the state
moved, the shape is identical, and at 12:13:34Z a slot is stealable while its
holder has run 28:28 — the design's own S7 condition, live.

## V7. Prepr starvation (design E7)

State moved: the two `open_pr.sh` processes are gone. The durable artifacts
survive:

    $ tail -3 ~/.local/state/hpo/pr/r10-earlycutoff-coverage/p1.log
      ok       codeowners_gap         RESULT uncovered_files=0 count
      skip     brief_lint             no pinned path changed, so CI's briefs job reads this head's copy
      ok       contract_rerun         contract_rerun self-test: 24 checks, 0 failed
    Terminated: 15
    $ tail -3 ~/.local/state/hpo/pr/r10-i5-docs/p1.log
      ... (same shape)
    Terminated: 15

Tree fact, re-run:

    $ grep -n 'timeout' tools/pr/prepr.sh tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh
    (no output; rc=1)

There is no `timeout` anywhere in the chain, including in prose — the design's
parenthetical "every hit is the word in prose or a lane name" is itself wrong,
though the load-bearing claim is stronger for it.

Live now, three preprs at 10:18, 19:44 and 28:28 elapsed (see V6).

## V8. Roster facts (design E8)

Roster tip at my read: `51297e362a9be9a214e985b65d87cea7e2dbd9d6`
(design's E14 cites `541868d6f` as the roster tip at its read).

    groups: 93
    stages: {'done': 46, 'not-started': 36, 'in-progress': 7, 'queued': 4}
    open (not done/rca-done): 47
    owner_gate set (open): 14
    non-40hex resume.commit: 8
    CI-RATCHET-RED: {'stage': 'done', 'branch': 'handoff/r10-ci-ratchet-red', 'commit': None, ...}
    open gates: 14

All four headline counts reproduce exactly. Open gates now:

    R10-I5-DOCS            code-owned: tests/stress.py (comment only)
    R10-BRIEFS-FOLD        policy: dimension briefs
    R10-REPLAY-LANE        code-owned: .github/workflows/
    R10-REPLAY-SCOPED      code-owned: .github/workflows/
    R10-TRAIN-HOLD         code-owned: .github/workflows/ (… approved under mandate 6175172275)
    R10-POLICY-LINT-FAMILY policy: tools/policy/ is in POLICY_GLOBS; tvofi approves under the mandate
    R10-MERGE-SUBJECT-HARDEN policy: tools/policy/agreement.mjs … under the mandate
    R10-CI-LAYOUT          Code-owned (…) and policy (…) … under mandate 6175172275 (scope `all`, to 2026-10-28)
    R10-SETPOINT-BOOST     mandated approval under 6175172275
    R10-CEILING-PROBE      mandated approval under 6175172275
    R10-DEMAND-OVERBOOK    mandated approval under 6175172275
    R10-BUFFER-STORE       mandated approval under 6175172275
    R10-COP-PARTLOAD       mandated approval under 6175172275
    R10-UPDATE-PR-SIGNALS  mandated approval under 6175172275

Ten name the mandate; four do not. The four non-mandate gates are all
`code-owned:` or `policy:` — the classes the mandate's own text covers (V8b).

    $ python3 -I -   # open groups naming a resume.branch the remote lacks
    open groups naming a branch the remote lacks: 36

36 reproduces exactly. The stage-vs-ref walk: the design's EVIDENCE does not
carry the program ("the full program is in the seat log"), so I re-implemented
the rule it states. Result at 12:1xZ: **10** mismatches, not 9, and a different
set:

    R10-SENSOR-PAYLOAD      not-started but a ref names it
    R10-I5-DOCS             not-started but a ref names it
    R10-RCA-FRICTION        not-started but a ref names it      (new)
    R10-STAMP               in-progress but no ref names it      (new)
    R10-DEMAND-OVERBOOK     queued but no ref names it
    R10-BUFFER-STORE        queued but no ref names it
    R10-COP-PARTLOAD        queued but no ref names it
    R10-UPDATE-PR-SIGNALS   queued but no ref names it
    R10-HANDOFF-ARCHIVE     in-progress but no ref names it
    R10-DEPENDABOT-AIOHTTP  in-progress but no ref names it

Of the design's nine, seven reproduce (SENSOR-PAYLOAD, I5-DOCS, the four queued,
HANDOFF-ARCHIVE, DEPENDABOT-AIOHTTP); CI-LAYOUT does not under a branch-exact
match, and RCA-FRICTION and STAMP are new. CI-LAYOUT reproduces only under a
**prefix** match (see V8a). The exact nine are therefore UNVERIFIED; the class
is corroborated.

Named examples re-checked:

    $ git ls-remote --heads origin 'refs/heads/handoff/*i5-docs*' 'refs/heads/handoff-body/*i5-docs*' 'refs/heads/handoff/*ci-layout*'
    cfba198b... refs/heads/handoff-body/r10-i5-docs
    dd3a4447... refs/heads/handoff/r10-ci-layout-p0
    7a7102eb... refs/heads/handoff/r10-i5-docs
    $ grep -n 'R10-I5-DOCS\|R10-UPDATE-PR-SIGNALS\|R10-CI-LAYOUT' ~/hpo-orch/r10s3/orch/tick/tick.txt
    30046:-> R10-I5-DOCS: UNBLOCKED, not started -- start a fixer on handoff/r10-i5-docs
    30061:-> R10-CI-LAYOUT: UNBLOCKED, not started -- start a fixer on handoff/r10-ci-layout
    30070:   R10-UPDATE-PR-SIGNALS: in progress (stage queued)
    $ grep -n 'blocked on owner disposition' ~/hpo-orch/r10s3/orch/tick/tick.txt
    30091:-> 14 group(s) blocked on owner disposition; oldest issue #2222 is 5d old -- surface them to the owner

### V8a. The suffix-ref case — the design's own nine needs a rule it did not state

R10-CI-LAYOUT's roster branch is `handoff/r10-ci-layout`; the ref that exists is
`handoff/r10-ci-layout-p0`. A rule reading "a `handoff/` ref at its branch" (the
design's §6.4 wording) prints no mismatch for CI-LAYOUT; the design's E8 lists it
as one of the nine, so the harness that produced the nine used a prefix match the
design does not state. A reconciler implementing §6.4 as written would miss one
of the nine it cites.

### V8b. The mandate's published text

    $ gh api repos/tvofi/heatpump_optimizer/issues/comments/6175172275 --jq '.body'
    MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z

    Exceptional round-10 programme mandate, granted by tvofi in session on 2026-10-14.
    It covers codeowner, policy and budget-raise approvals. It is posted at tvofi's
    request and has not been edited.

Under §6.4's stated rule — "blocked on owner disposition is computed as *no act
the in-force mandate covers*" — every one of the 14 gates is covered (the
mandate covers codeowner, policy and budget-raise, scope all). The correct
figure is **14 ready, 0 owner**, not "10 ready and 4 owner". The 10/4 split is
exactly the "does the gate string mention the mandate?" test S3 criticises.

### V8c. The eight short `resume.commit` values resolve

    $ for s in 768bfc0c341d 8cc1abc3a27d a96f4be4ac0a 0dac0bf8731a a73f3320c53a f0a4acac7984 7ab3030bbfff c35302773738; do git cat-file -t "$s"; done
    commit ×7; c35302773738: fatal: Not a valid object name
    $ for each of the seven: git merge-base --is-ancestor "$(git rev-parse $s)" origin/main
    768bfc0c341d IN MAIN
    8cc1abc3a27d IN MAIN
    a96f4be4ac0a IN MAIN
    0dac0bf8731a IN MAIN
    a73f3320c53a IN MAIN
    f0a4acac7984 IN MAIN
    7ab3030bbfff IN MAIN

Seven of the eight are valid, unambiguous prefixes of commits in `main`; only
`c35302773738` does not resolve. The records are not invalid: the length test is.

### V8d. `roster_edit.py` has no `set-after`

    $ grep -n 'add_argument("op"' -A1 tools/audit/seat/roster_edit.py
    364:  p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue",
                                       "append-group", "edit-brief", "append-carry", "set-resume"))

PASS. `roster_edit.py` has no `flock`/lock either:

    $ grep -n 'flock\|lock' tools/audit/seat/roster_edit.py
    (no output)

A live `roster_edit.py set-resume` (pid 36629) was mutating the roster during
this read, confirming an unleased writer.

## V9. Liveness (design E9/S4)

    $ ls -la ~/hpo-orch/r10s3/orch/tick/alive
    -rw-r--r--  1 USER staff 21 Oct 20 14:05 .../tick/alive        # local 14:05 = 12:05Z
    $ ps -eo pid,ppid,etime,command | grep -F "tick/""alive" | grep -v grep
    (empty)
    $ ps -eo command | grep -F 'date -u +%FT%TZ' | grep -v grep
    /bin/zsh -c ... 'export PATH=...; sleep 300; date -u +%FT%TZ'    # an agent turn's background task

No process writes the file; a transient background task runs the brief's
command. `mcp__scheduled-tasks__list_scheduled_tasks` → `No scheduled tasks found.`
The design's E9 command does **not** reproduce:

    $ tail -1 ~/hpo-orch/r10s3/orch/SEATS.md
    07:10Z Owed openers remain (no PR carries them): ... Open-PR cap 6; 5 open now.
    $ grep -n 'LIVE(8): tick, vent, savbase, sensorpay, pump, refpriv, review-leaf, review-2345' ~/hpo-orch/r10s3/orch/SEATS.md
    162: LIVE(8): tick, vent, savbase, sensorpay, pump, refpriv, review-leaf, review-2345.

The LIVE line is at line 162 of 893, not the file's last line. Also the design
says the ledger was "last written 09:12Z"; `ls -la` shows 09:12 **local**
(07:12Z), and the file's last entry is 07:10Z. The conclusion survives (the line
exists, and no process matches vent/savbase/sensorpay/pump/refpriv); the quoted
command does not produce its quoted output.

    $ ps -eo pid,ppid,etime,time,command | grep 'claude --output-format'
    3930 3928 02:41:18 14:07 /path/claude-code/2.1.299/...
    (one harness tree; pids 3928/3930 as the design says)

## V10. The live daemons

    $ ps -eo pid,ppid,etime,command | grep -E 'tick_loop|state_docs|wt_sync' | grep -v grep
    35000     1 02:00:37 bash tools/audit/seat/tick_loop.sh --out ...
    35031     1 02:00:37 .../python3 -u tools/audit/seat/state_docs.py beat --push --mirror ...
    35037     1 02:00:37 bash -c while :; do bash tools/audit/seat/wt_sync.sh --scratch ...; sleep 900; done

Three PPID-1 daemons, no pidfile in any of them:

    $ grep -n 'pidfile\|pid-file\|alive' tools/audit/seat/tick_loop.sh tools/audit/seat/state_docs.py tools/audit/seat/wt_sync.sh
    (no output)
    $ grep -c '^synced' ~/hpo-orch/r10s3/orch/wtsync.log
    394

## V11. The plan generator

    $ ls -la ~/hpo-orch/r10s3/plan/gen.py
    -rw-r--r-- 1 USER staff 12293 Oct 20 13:54 .../plan/gen.py
    $ md5 -q ~/hpo-orch/r10s3/plan/gen.py
    446ce44181804dc5300d18fa000bf078

The file is unchanged since 13:54 and is the file the design's E10 cites (12293
bytes, mtime 13:54). Read in full. The five recorded defects, checked against
**this** file:

1. **hardcoded override** — present, lines 17-19:
   `groups["R10-ARCH-DOCS"] = {"...", "resume": {"stage": "not-started"}}`.
   The roster currently also says `not-started`, so the stage override is
   harmless today; the brief and size are still hardcoded.
2. **graph from scratch** — **absent**. Lines 52-55:
   `# ... A scratch REPLAN-EDGES.json used to override them; it was dated
   2026-10-17 ... One source: the roster.` and
   `edges = {g: list(groups[g].get("after") or []) for g in groups}`.
   Both backups carry the defect (`gen.py.bak`, `gen.py.bak-20261019`:
   `EDGES = json.load(open(B + "REPLAN-EDGES.json"))`).
3. **count from the wrong set** — **absent**. Line 176 reads
   `plan-issues-open.json` (written from `gh issue list --state open`) and
   excludes `#201`: the corrected set.
4. **commit prefix as PR number** — **absent**. Line 117 renders
   `f"#{MERGED[g]}" if str(MERGED[g]).isdigit() else "merged"`; line 94 renders
   a non-digit as "folded into another group (no merge of its own)".
5. **`done` for absorbed** — **partial**. `R10-CI-RATCHET-RED` (`stage: done`,
   `commit: null`) renders status "folded into another group (no merge of its
   own)" but the row's pill class is `done` and its PR cell is `merged`; the
   schema still has one stage doing two jobs.

The scratch-edge fact itself still reproduces:

    $ python3 -I -   # REPLAN-EDGES.json vs roster after-edges
    groups: 93 in EDGES: 34 absent from EDGES: 59
    groups whose edges differ: 27

The publish path is gone:

    $ ls '/private/tmp/claude-501/...-audit-round-10-orchestration-eaa727/.../scratchpad/round-10-plan.html'
    No such file or directory
    $ ls -la ~/hpo-orch/r10s3/plan/round-10-plan.html
    -rw-r--r-- 1 USER staff 80944 Oct 20 13:54 ...

The generator's remaining carried claims (constants) in this file: `LIVE` (14
entries), `MERGED` (25 group→PR pairs), `PR = {"R10-DEEPLINK-CENSUS": "#2345",
"R10-PUMP-MODEL": "opening"}`, `HOURS`, `WAVES.json`. The `LIVE` constant is
cleared by the roster overlay for any group not `in-progress`-class, and all 25
`MERGED` entries are `done` in the roster today — they are stale-risk, not
currently wrong.

## V12. The model-builder claim

    $ grep -n '^def \|^class ' tools/audit/seat/roster_lib.py
    ... groups_of, is_open, open_groups, depth_of, critical_path, waves_of, ...
    $ grep -n '^def \|^class ' tools/audit/seat/plan_table.py
    ... gantt, swimlanes, detail, eta, render, _fixture_roster, _self_test, main
    $ sed -n '1,40p' tools/audit/seat/plan_table.py
    (imports roster_lib; uses roster_lib.critical_path)

The roster walk the model builder would add already lives in `roster_lib`; the
shared-model proposal is sound. `plan_table.py` has `--self-test`.

## V13. Self-tests pass with the defects present (design E12)

    $ python3 -I tools/audit/seat/orchestrator_tick.py --self-test | tail -1
    orchestrator_tick self-test: 150 checks, 0 failed
    $ bash tools/audit/seat/cloud_relay.sh --self-test | tail -1
    cloud_relay self-test: 74 checks, 0 failed
    $ bash tools/audit/seat/tick_loop.sh --self-test | tail -1
    tick_loop self-test: 4 checks, 0 failed

Identical. None fails on S1, S6 or S7.

## V14. State surfaces (design E14/E15/E16)

    $ git ls-tree --name-only origin/main dev/programme/delivery/ | wc -l
    791
    $ gh api repos/tvofi/heatpump_optimizer/issues/201 --jq '.comments'
    1875
    $ gh api 'repos/.../issues/201/comments?per_page=100&sort=created&direction=desc' --jq '.[0].created_at'
    2026-09-01T23:24:46Z          # the API ignores sort/direction: page 1 is the oldest
    $ git --version
    git version 2.54.0 (Apple Git-157)
    $ xcode-select -p
    /Library/Developer/CommandLineTools
    $ git -C ~/heatpump_optimizer worktree list | wc -l
    90                              # design: 92
    $ df -h / | tail -1
    ... 8.4Gi free                  # above the 6 GiB floor

## V15. Mechanisms the inventory does not name

    $ grep -ci 'codeql-triage-poll' dev/audit/design/orch-machinery/DESIGN.md
    0
    $ find . -name '*undispatched*' -not -path './.git/*'
    (none)
    $ sed -n '1243,1252p;1303,1310p' .github/workflows/governance.yml
    delivery-status:        if: pull_request ... timeout-minutes: 5
                            run: python -I -S tests/delivery_status.py --check
    delivery-status-publish: if: push to main ... permissions: issues: write
                            # edits #201's delimited body region

`delivery-status-publish` is a second writer to `#201` (the issue **body**),
distinct from M35's "one comment per record act". `tests/delivery_status.py` is
the credential-free ledger builder (`--emit`). `codeql-triage-poll.sh` is a
tracked 36-iteration poll loop with a hardcoded head sha and job id. The tick's
`MERGE-READY` arm (`orchestrator_tick.py:645-677`) reads `review/*` verdict refs
and prints a flagged level; M02's reads column does not name it.

## V16. New self-testing files must be wired into workflows

    $ sed -n '1,30p' tools/audit/seat/selftest_wiring.py
    "Refuse a self-testing seat instrument that no CI step runs." ... "a file
    directly under tools/audit/seat/ (not *.md) is SELF-TESTING when its text
    matches `--self-test`" ... "It is WIRED when some step of a
    .github/workflows/*.yml file has a `run:` line ... naming
    tools/audit/seat/<file> and then `self-test` later on that same line."
    $ grep -n 'selftest_wiring' .github/workflows/governance.yml
    479: ... selftest_wiring.py --self-test ...
    481: ... selftest_wiring.py --check

So `beatd.py`, `ledger.py` and `plan_page.py`, each proposed with `--self-test`,
must be named in `.github/workflows/*.yml` — and `tests.yml`/`governance.yml` are
R10-CI-LAYOUT's files (V17).

## V17. The seams

R10-ROSTER-OPS's brief, at the roster revision the design's own E14 cites as the
tip (`541868d6f`), added 2026-10-20T13:35:54+02:00 = **11:35:54Z**, before the
design's 11:38Z read:

    $ git -C ~/heatpump_optimizer log --format='%h %cI %s' -S'roster_sync' origin/handoff/audit-r10-roster
    541868d6f 2026-10-20T13:35:54+02:00 roster_edit edit-brief R10-ROSTER-OPS (tools/audit/seat/roster_edit.py)

The brief now says: "Add a `roster_sync.py --apply` run by `state_docs.py beat`
that derives only what the repository measures — a group whose `resume.branch`
has a MERGED pull request becomes `done` at that merge commit; one whose
`resume.branch` has an OPEN pull request becomes `in-progress` with its
number ... must go out through `roster_edit.py`'s load-validate-dump and lint
gate." Its `files` list is `roster_edit.py`, `r10_roster_ops_mutants.py`,
`INSTRUMENTS.md`.

R10-CI-LAYOUT's `files` list:

    ['.github/workflows/tests.yml', '.github/workflows/governance.yml', '.github/workflows/ci.yml']

The design's E14 `beat.tip` is `a2b25bbc5 541868d6f...` — the roster tip it read
is the commit that assigns `roster_sync.py` to R10-ROSTER-OPS.
