# Evidence for the round-2 review (design revision 2)

Design: `handoff/orch-machinery` at
`14d2ac1cded1b1ff3cf7765b581652850cdc393b`. Round 1 reviewed `2b159e46`.
Read from a detached worktree at that SHA; live state re-read
2026-10-20T12:30Z–12:45Z, `load1` 43–50 on 8 cores. Host paths are written `~`.
Commands and the output I got; a live figure that moved since the design's
12:24Z read is shown with both.

---

## R1. What moved between revisions

    $ git diff --stat 2b159e46 14d2ac1c
     dev/audit/design/orch-machinery/DESIGN.md   | 1291 +++++++++++++--------------
     dev/audit/design/orch-machinery/EVIDENCE.md |  746 +++++++---------
     2 files changed, 972 insertions(+), 1065 deletions(-)
    $ git log --format='%h %cI %s' 2b159e46..14d2ac1c
    14d2ac1cd 2026-10-20T14:23:08+02:00 design: revision 2 of the orchestration machinery

Only the two documents changed. The inventory's M01–M46 rows were diffed row by
row (`git show 2b159e46:…DESIGN.md | grep '^| M'` against the revision): the
changes are additive/corrective (M02 reads, M03 OWED events, M05 203 refs, M06/
M07 one-shot, M12 posted lines, M32 roster_sync, M35 body region, M37 live edit)
and M47–M50 are new. No row regressed a round-1 PASS.

## R2. E1 tree size — the 53rd entry is `__pycache__` (N1-R)

    $ git ls-tree --name-only HEAD tools/audit/seat/ | wc -l
    52
    $ ls tools/audit/seat | wc -l
    52
    $ grep -l -- '--self-test' tools/audit/seat/* | grep -vc '\.md$'
    37
    $ wc -l tools/audit/seat/* tools/audit/seat/*.md | tail -1
    22793 total

The live instrument checkout the design reads from is at the same HEAD:

    $ cd ~/hpo-seats/r10s3/orch-wt; git rev-parse --short HEAD
    a2b25bbc5
    $ ls tools/audit/seat | wc -l
    53
    $ git ls-tree --name-only HEAD tools/audit/seat/ | wc -l
    52
    $ diff <(ls -A tools/audit/seat | sort) <(git ls-tree --name-only HEAD tools/audit/seat/ | sed 's|tools/audit/seat/||' | sort)
    2d1
    < __pycache__
    $ git status --short --ignored tools/audit/seat/
    !! tools/audit/seat/__pycache__/

The 53rd entry is an ignored import cache in a live worktree, not a tree file.
The tree is 52 at both revision heads; the design's explanation ("instruments
land and the count moves") is false because no tree file changed between the
revisions. The 37 self-testing scripts figure is right.

## R3. B1 — the sha-aware disposal figure, and the import's prefixes

    $ grep -c 'cloud-disposed' tools/audit/seat/orchestrator_tick.py
    0
    $ grep -c 'disposed\|cloud-disposed' tools/audit/seat/orchestrator_tick.py
    1
    $ grep -n 'disposed\|cloud-disposed' tools/audit/seat/orchestrator_tick.py
    1693:        """Every open issue must be disposed in a record artifact: a delivery

The combined pattern hits the word "disposed" in `dispositions`' docstring; the
precise pattern is 0. The substance (the tick never opens the disposal file)
holds.

    $ python3 -I -   # sha-aware comparison, handoff-no-pr + probe-ref
    disposed lines: 210 distinct refs: 203 distinct full lines: 209
    owed subjects (handoff-no-pr+probe-ref): 228
    comparable: 202 same: 199 moved: 3
      moved: refs/heads/handoff/audit-r10-plan       b90c1053 -> 6691dd18
      moved: refs/heads/handoff/audit-r10-roster     b932ecc9 -> 89f6bd10
      moved: refs/heads/handoff/r10-ci-layout-p0     dd3a4447 -> 385b3a0d
    disposed with no OWED line: 1
    **disposed refs by prefix: handoff-body 89, handoff 113, probe 1**

The design's 203/210/199/3/1 figures reproduce exactly. The prefix split is the
B10-R evidence: 89 of 203 disposed refs are `refs/heads/handoff-body/...`, which
the stated import rule ("`refs/heads/probe/` vs `handoff/` prefix") does not
classify, so 114 — not 203 — would import.

    $ L=~/.local/state/hpo/cloud-relay.log
    $ for k in handoff-no-pr handoff-update probe-ref reviewer-fire approve-held-runs dispatch; do printf '%-18s %s\n' "$k" "$(grep -c " $k " $L)"; done
    handoff-no-pr      29877
    handoff-update     10
    probe-ref          151
    reviewer-fire      1
    approve-held-runs  0
    dispatch           0
    $ grep -cE '^OWED [0-9T:Z-]+ [0-9]+ ' $L
    0
    $ total OWED: 30039

`handoff-update` (10 live) has no kind in §6.3's table; the two zero-live code
paths have none either.

## R4. E3 — the fold fixture (regression check)

    $ python3 -I -   # real Tick.relay_owed on the four-line fixture
    findings: 2
    findings after dispose: 2

Unchanged: the verdict OWED cancels against its POSTED; the `handoff-no-pr` and
`probe-ref` lines survive a disposal.

## R5. B2 — the mandate's text

    $ gh api repos/tvofi/heatpump_optimizer/issues/comments/6175172275 --jq '.body'
    MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z

    Exceptional round-10 programme mandate, granted by tvofi in session on 2026-10-14.
    It covers codeowner, policy and budget-raise approvals. It is posted at tvofi's
    request and has not been edited.

## R6. B2 — the existing mandate reader

    $ grep -n 'def mandate_state\|MANDATE_GRAMMAR\|MANDATE_COVERS_RAISE' tools/policy/budget_raise_gate.py
    112: rf"MANDATE: agents may approve as {OWNER_LOGIN}, scope (code-owned|budget-raise|all), "
    116: MANDATE_COVERS_RAISE = ("budget-raise", "all")
    344: def mandate_state(cid, comment, thread, at, at_repr, when="review",
    373:     scope, start, until = m.group(1), _when(m.group(2)), m.group(3)
    378:     if scope not in covers:

`mandate_state` is the one mandate reader (the tick's header names it). It parses
`scope (code-owned|budget-raise|all)` and takes a `covers` tuple, so the B2
predicate has its reader. The mapping class→scope is not stated (N10-R); with the
only live mandate at scope `all` the answer is unaffected.

    $ python3 -I -   # open gates at the current roster tip
    open gates: 14
    exact mandated string: 6
    names the mandate: 8 (10 in some form)
    $ grep -n '^  delivery-status\|^  delivery-status-publish' …   # see R18

Six carry the exact string, not the four E8b states (N3-R). The conclusion
(14 ready / 0 owner) holds.

## R7. B3 — commit resolution

    $ for s in 768bfc0c341d 8cc1abc3a27d a96f4be4ac0a 0dac0bf8731a a73f3320c53a f0a4acac7984 7ab3030bbfff c35302773738; do
        n=$(git rev-parse --disambiguate=$s | wc -l); … ancestry …; done
    768bfc0c341d unique=1 ancestor_in_main=True
    8cc1abc3a27d unique=1 ancestor_in_main=True
    a96f4be4ac0a unique=1 ancestor_in_main=True
    0dac0bf8731a unique=1 ancestor_in_main=True
    a73f3320c53a unique=1 ancestor_in_main=True
    f0a4acac7984 unique=1 ancestor_in_main=True
    7ab3030bbfff unique=1 ancestor_in_main=True
    c35302773738 unique=0

Seven resolve uniquely and are ancestors of `origin/main`; the eighth is
unresolved in this clone (it may exist on an unfetched ref). The revised rule —
resolve, verify ancestry, invalid only when ambiguous/unresolvable — is correct.

## R8. B4 — the reconciler's owner

    $ git log -1 --format='%h %ci %s' 541868d6f
    541868d6f 2026-10-20 13:35:54 +0200 roster_edit edit-brief R10-ROSTER-OPS …
    $ python3 -I -c "… print('roster_sync' in brief, brief.count('roster_sync.py'))"
    True 1
    $ for ref in origin/handoff/audit-r10-roster origin/main origin/handoff/r10-roster-ops origin/handoff/orch-machinery; do
        git cat-file -e "$ref:tools/audit/seat/roster_sync.py" && echo PRESENT || echo absent; done
    absent ×4

The requirement is in R10-ROSTER-OPS's brief; the file is on no ref. The design
adds no `--reconcile` op (`grep -n reconcile DESIGN.md` finds only references to
R10-ROSTER-OPS's instrument and the round-1 correction). B4 closed.

## R9. B6 — the WORKERS contract already exists

    $ grep -n 'def workers\|def one_worker\|--workers-file\|workers.json' tools/audit/seat/orchestrator_tick.py
    5:        [--queue FILE] [--train-log FILE] [--workers-file FILE]
    953:    def workers(self) -> None:
    961:            self.unreadable(S, f"workers file {self.workers_file}", str(e)[:120])
    968:    def one_worker(self, S: str, w: dict) -> None:
    3408:    ap.add_argument("--workers-file")
    $ sed -n '953,975p' tools/audit/seat/orchestrator_tick.py
    def workers(self) -> None:
        … json.load(workers_file) … except (OSError, ValueError) -> unreadable …
    def one_worker(self, S, w):
        seat = w.get("seat") or "?"; pr, head = w.get("pr"), w.get("head")
        … dispatched_at parsed; STALLED? / DONE? / OK …

The seat checker is real and takes JSON. The design's `SEAT-STALLED` spelling is
not the code's token (N7-R).

## R10. B7/B8 — the beat's jobs and the liveness migration

    DESIGN §6.2 job table:
    tick 300/900, relay-probe 120/120, handoff 120/3600 (60 s heartbeat),
    state-docs 300/300, sync 900/600, plan-page 300/300, seats 300/120.

    $ ps -eo pid,etime,command | grep 'prepr.sh' | grep -v grep
     7269 29:01 …  14721 24:12 …  14728 24:12 …  63885 42:23 …
     63943 42:22 …  77712 38:12 …  94267 33:38 …  94268 33:38 …
    $ python3 -I tests/gate_lock.py slot-status
    3/4 slots held [0:prepr-94268(expired), 1:prepr-14728(live), 2:prepr-63943(expired)] queue=-

The longest live run is 42:22 = 2542 s, inside the 3600 s handoff bound; the two
expired slots with live holders are the S7 condition, live. The design's
measured maximum at its read was 36:50 = 2210 s. B7 closed on the bound; the
probe arm's 120 s is unmeasured (N9-R).

    $ grep -n 'alive\|alive' tools/audit/seat/sweep_template.md
    41/44: tick_alive …  62: (5) Tick watcher. If {{tick_alive}} is missing or older …

The design now says both halves land in one PR (DESIGN §6.2 compatibility,
§8 Phase 1). B8 closed.

## R11. B13 — the stated stage rule

    rule: topic = basename of resume.branch (else lowercased group id); a ref
    matches when its name minus handoff-body/|handoff/|fix/ and a trailing -pr
    equals the topic or starts with <topic>-.

    $ python3 -I -   # applied at roster tip 89f6bd10
    groups: 93 open: 47
    mismatches: 10
      R10-SENSOR-PAYLOAD not-started in-flight
      R10-I5-DOCS not-started in-flight
      R10-RCA-FRICTION not-started in-flight
      R10-CI-LAYOUT not-started in-flight          # via r10-ci-layout-p0
      R10-DEMAND-OVERBOOK queued no-artifact
      R10-BUFFER-STORE queued no-artifact
      R10-COP-PARTLOAD queued no-artifact
      R10-UPDATE-PR-SIGNALS queued no-artifact
      R10-HANDOFF-ARCHIVE in-progress no-artifact
      R10-DEPENDABOT-AIOHTTP in-progress no-artifact

Exactly the design's 10, including the suffix ref revision 1's rule missed. B13
closed.

## R12. B15 — the inventory

    $ grep -c '^| M[0-9][0-9]' dev/audit/design/orch-machinery/DESIGN.md
    50
    $ … contiguity …
    contiguous 1..50
    $ grep -n 'MERGE-READY' dev/audit/design/orch-machinery/DESIGN.md
    64: … M47 … M50 … and M02's reads now name the `MERGE-READY`/`BLOCKED-UNFIXED` arm.
    77: | M02 | … the approver App's newest `Fix review:` comments (`MERGE-READY` / `BLOCKED-UNFIXED`) and the workers JSON …

M47–M50 are the four missing mechanisms. The MERGE-READY row is accurate: the
arm reads the approver App's newest `Fix review:` comment
(`orchestrator_tick.py:verdict_levels`, `_verdict_authors`). B15 closed.

## R13. E4 — the relay's fail-open (regression check)

    $ HPO_STATE_DIR="$S/state" HPO_RELAY_PRS=true bash cloud_relay.sh pass
    rc=0
    "will retry" lines: 2

Unchanged.

## R14. E5 — cadence (regression check, state moved)

    passes: 149 span h: 18.1
    median/max gap: 401 2654   gaps>600: 6 of 148   max derived: 2354

The design's 144/17.5 h/399/2654/5-of-143 was its read; the claim holds.

## R15. E6 — live slot steal and null control (regression check)

    $ python3 -I - "$T"   # throwaway lock dir
    STOLEN while A alive: True slot 0

Null control before expiry: `BlockingIOError`. The live slot table in R10 shows
two expired slots with live holders, independently corroborating the claim.

## R16. E7 — prepr starvation (regression check)

    $ tail -1 ~/.local/state/hpo/pr/r10-earlycutoff-coverage/p1.log
    Terminated: 15
    $ grep -n 'timeout' tools/pr/prepr.sh tools/audit/seat/open_pr.sh tools/audit/seat/update_pr.sh
    (no matches; rc 1)

Unchanged.

## R17. E8 — roster counts and short commits (regression check)

    groups: 93 open: 47
    open gates: 14
    non-40hex resume.commit: 8
    $ git ls-remote --heads origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' 'refs/heads/fix/*' | wc -l
    (220 at this read; the design's 219 was its read)

All four headline counts reproduce.

## R18. E9, E10, E12, E14, E16, E17, E19 (regression checks)

    $ tail -1 ~/hpo-orch/r10s3/orch/SEATS.md
    07:10Z Owed openers remain … Open-PR cap 6; 5 open now.
    $ grep -n '^LIVE(' … | tail -1
    162:LIVE(8): …                                  # the command correction is right

    $ md5 -q ~/hpo-orch/r10s3/plan/gen.py
    446ce44181804dc5300d18fa000bf078
    $ grep -n 'EDGES = json.load\|len(ISS)\|pr=f"#{MERGED' ~/hpo-orch/r10s3/plan/gen.py.bak
    4:EDGES = json.load(open(B + "REPLAN-EDGES.json"))
    89:    … pr=f"#{MERGED[g]}" if g in MERGED else PR.get(g, "—"),
    148:open_iss = len(ISS) - 1
    (same three lines in gen.py.bak-20261019 at 10, 95, 154)

    $ python3 -I tools/audit/seat/orchestrator_tick.py --self-test | tail -1
    orchestrator_tick self-test: 150 checks, 0 failed
    $ bash tools/audit/seat/cloud_relay.sh --self-test | tail -1
    cloud_relay self-test: 74 checks, 0 failed
    $ bash tools/audit/seat/tick_loop.sh --self-test | tail -1
    tick_loop self-test: 4 checks, 0 failed

    $ grep -n '^  delivery-status:\|^  delivery-status-publish:\|^  record:' .github/workflows/governance.yml
    990:  record:
    1243:  delivery-status:
    1303:  delivery-status-publish:
    $ ls -la tests/delivery_status.py
    -rw-r--r--  1 USER  staff  34937 Oct 20 14:24 tests/delivery_status.py
    $ grep -n '109534061903\|H=3ad6e085' tools/audit/seat/codeql-triage-poll.sh
    14:    JOB=$(… echo 109534061903)
    18:    H=3ad6e085accc2254dbf816ae1a105eb7caeb925c
    $ wc -l ~/.zcode/bus/posted
    546 ~/.zcode/bus/posted

    $ python3 -I tools/audit/seat/selftest_wiring.py --check
    selftest_wiring: 37 self-testing, 37 wired, 0 unwired

    $ for ref in origin/handoff/audit-r10-roster origin/main origin/handoff/r10-roster-ops origin/handoff/orch-machinery; do
        git cat-file -e "$ref:tools/audit/seat/roster_sync.py" && echo PRESENT || echo absent; done
    absent ×4

    $ python3 -I -   # never-disposed subjects at this read
    OWED subjects: 228 disposed refs: 203 never-disposed: 26
    still present: 13 gone: 13

All reproduce. The `.bak` pre-fix expressions are at exactly the quoted lines —
except defect 1, whose pre-fix override is in the live file (N8-R).
