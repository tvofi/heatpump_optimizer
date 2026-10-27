Fix review: merge 43f436a03b9a4729ed0eb8efe7c09014e2cb98d2

# Fix review — PR #2867, triage record s6 batch 35 (P199–P203)

Measured at `origin/main` `6fe5170cd7ce01e60ffebfc93e598c216e628fa3`, which is
also this branch's merge base and the head's parent, and at the head
`43f436a03b9a4729ed0eb8efe7c09014e2cb98d2`. Round 1. No `bus-nonce:` line: this
review was dispatched by the orchestrator's brief without one, so it proposes a
verdict and the orchestrator records it; nothing here was relayed.

The head is a triage record: two added files (`dev/programme/triage/s6-batch35.md`,
`dev/programme/delivery/2867.md`), no code, no VERSION, no manifest, no
`RELEASE_NOTES.md` heading, no budget file, no claim file, no fixture. `dev/programme/`
is INERT in `tests/closure.py`, so neither new file selects a closure.
`git merge-tree --write-tree origin/main HEAD` exits 0. The head's 55 check-runs
hold 0 non-green; `gate` and `pr-contract` each ran in two suites and both are
success in both. Nothing in that report owes a root cause.

**All five rulings stand as ruled.** The record does its job: five verdicts, three
live carry destinations, two rejects that lose no finding. What does not hold is a
set of figures and citations, listed under Findings — six miscounts or misquotes,
one understated critical-path cost, one undated census, one unresolvable path
pair — of which the one with a consequence is P201's close-out count, short by
five. No blocking class applies: none of the unsoundness classes in `fix-review.md`
is engaged, because each ruling's decisive measurement reproduces.

RESULT: measurements below are my own; `evidence/` holds each command's output.

## P199 — ACCEPT narrowed into R10-FLOW-WIP: confirmed

The dead-train instances reproduce exactly. `for d in train/s*/; do grep -qE
"TRAIN (DONE|STOPPED)" "$d"/* || echo "$d"; done` in the orchestrator's train state
dir prints `s38/`, `s44/`, `s60/` — 3 dirs of the loop's population of 27. All
three are **not running**, not merely unfinished: no `merge_train.py` process is
live (`pgrep -f merge_train.py` empty), `s60/train.pid` 71741 is gone, `s38` has no
`rc`, and `s44` has `rc=143` with `TRAIN_RC=143 end=2026-10-26T03:01:39Z`.

The cause is the one the record names. `current-queue.json -> queue58.json` and
`current.log -> s58/train.log`, both mtime 16:59Z; `sweep_mech.sh:26` passes that
pair to `tick_loop.sh --interval 300`; `orchestrator_tick.py:508-521` computes
`open_` from the caller's queue, so the `train not alive` arm (517-520) can only
fire on a queue the caller supplies, and a dead train's own `queue.open` is never
read. A fresh tick at 23:17Z still prints the s58 tail, now ending `TRAIN DONE |
TRAIN_RC=0 end=2026-10-26T16:59:07Z` — the same line the record quotes.

Blindness and critical-path figures: s60 launched 17:01:45Z (`seat-ledger.md`
line 1113), last log 17:02Z, found dead 18:21:51Z (line 1124) = **79m51s**; #2858
merged 18:30:14Z (line 1125) = **88m12s** after the last log. The 88 holds. The
record's "79 minutes" truncates 79m51s (80m06s from launch) — see F4.

- Destination: `R10-FLOW-WIP` is live on main's in-tree roster **and** on
  `origin/handoff/audit-r10-roster` (`stage: not-started`, size S, files
  `tools/audit/seat/pr_cap.py`, `orchestrator_tick.py`, `INSTRUMENTS.md` — exactly
  the record's list), `after: R10-FLOW-PULL` which is `done`. `carry_audit.py`
  reading main's roster finds it.
- The rejected `train.sh` arm is right to be rejected: `train.sh:35-36` says
  "Foreground by design: the caller detaches (`nohup ... &`) and owns the
  schedule". The record cites :34-35; the sentence is one line lower (F6).

## P200 — ACCEPT narrowed into R10-ORCH-REVIEW-PACKET: confirmed

The cap is real and it binds the file the carry edits.
`node tools/policy/policy_lint.mjs --budgets` at the head prints the row as
`tools/audit/briefs/fix-review.md  140 lines, cap 140; 2448 tokens, cap 2451`, and
`wc -l dev/governance/roles/fix-review.md` is 140. The printed name is the canon
spelling: `tests/layout.json`'s `retired` entry maps
`tools/audit/briefs/fix-review.md` to `dev/governance/roles/fix-review.md`, so the
row measures the role file. 0 lines and 3 tokens of headroom, as recorded — an
append fails the lint, so the carry must pay by deletion.

The relay checks are the ones listed. `cloud_relay.sh`'s `relay()` requires: the
ref `refs/heads/probe/rev-<pr>-<nonce first 8>`; the 40-hex head and 32-hex nonce;
the commit subject exactly `verdict <pr> <head>`; a `verdict.md` in the tree; the
first line `Fix review: merge <40>` or `Fix review: blocked <40> <class>: <reason>`
with `class` matching `[a-z-]+`; a `bus-nonce: <32 hex>` line; and an `ev/`
directory. `fix-review.md` line 7 states the `push-verdict` verb, an evidence
directory, a file in it naming the head, and the nonce line. So the ref name, the
subject, the first-line literal and the `ev/` name are unstated — four, as
recorded. `verdict.md`'s existence is a fifth the record does not list (F1).

The defect count composes: 4 repairs on rev-2745 (`seat-ledger.md` line 1131) + 1
on rev-2849 (line 1078) + 2 on rev-2853/rev-2858 (line 1166) = seven on four
verdicts. `brief-rev-2858.txt` does state the first line, the nonce line, `ev/`
with a file naming the 40-hex head, and `refs/heads/probe/rev-2858-7540ca11`.

- Destination: `R10-ORCH-REVIEW-PACKET` live on both rosters (`not-started`, M,
  files `bus.sh`, `review_packet.py`, `dev/governance/roles/fix-review.md`,
  `INSTRUMENTS.md`) — exactly the record's list. Its brief already edits
  `fix-review.md`, so the marginal lines ride that round.
- The sentence "That is exactly the four the #2745 probe cost" does not hold (F1).

## P201 — REJECT as a duplicate of #2733: confirmed

The routing invariant the record says does not exist is measured absent. At the
record's own roster tip `9937317d8` the branch holds 208 groups, 70 open. The open
issue set at that read reconstructs exactly: today's 71 open issues plus #2494
(closed 22:31:43Z) plus #2509 (closed 22:47:57Z), with nothing created since
(#2867 is this pull request), = 73. Joining every number against **every** group's
`issues` and `fixes`: **72 of 72 beside #201 resolve to a live group, 0 to none, 0
to done or absorbed only.** Re-run on today's 70, the same result. The four filings
an earlier read called unowned are on live groups: #2835 `R10-FRICTION-GATE-SCOPING`,
#2840 `R10-FRICTION-MUTATION-SURVIVOR`, #2855 `R10-RCA-FRICTION-RESIDUE`, #2860
`R10-FRICTION-REGRESSION`. The PR half reproduces too: at the branch, five of the
six then-open PRs resolve through `resume.pr` (#2854 `R10-HEAT-METER`, #2853
`R10-FLOW-JIDOKA`, #2819 `R10-ARCH-SHAPES`, #2745 `R10-SAV-COMFORT`, #2678
`R10-DEPENDABOT-SETUPTOOLS`), and #2866 is the roster record PR. (On main's
in-tree roster `R10-DEPENDABOT-SETUPTOOLS` does not exist yet and #2678 reads
unowned — the branch is the reader, which is why it must land.)

The duplicate is the same mechanism, not the same words. #2733's body: "invariant
3 (an open issue has a live owner) is a tick report line from the cached issue
list, report-only on push" — the same line from the same cache. #2733 is listed by
`R10-ORCH-ROSTER-SCHEMA` (live, `not-started`) and by `R10-ROUTING-INVARIANTS`
(`absorbed`, note naming the same absorption); `roster-queue.txt` lines 207/303/305
wire it. A second ruling would dispatch a second builder. **No finding is lost**:
the PR half is routed as prose to a live group (dispatch item 3) and the record
says so in the entry.

- The "23 also listed by a done or absorbed group" figure does not reproduce (F2),
  and it drives dispatch item 5's "other 22" (F3).

## P202 — REJECT: confirmed for the proposal as filed

A5 is in the tree, in the words the record quotes. `merge_train.py:331-339`: "Every
`CI` run is a check suite of its own, so one head carries one `gate` per run: an
older red (R-9's defer red) beside a newer green. GitHub's ruleset refuses a merge
while ANY suite at the head carries a non-success required run (#2009,
budget_raise_gate.stale_run; M-2 was decided on that reading, plan/ci-layout
EXECUTION.md 5), so GATE is read per suite and its worst suite stands for it, never
the newest alone." `latest_runs()` 346-357 implements it; `proof_watch.py:201-203`
reuses that reader; the self-test pins it at 4237-4252 ("an older failing suite is
red"); `at_head()` calls `cross_check` under `if GATE in req` (1695-1696) and
`cross_check` raises "a disagreement is a refusal (A5)" (1175); `platform_gate`
387-414.

The decisive point is stronger than the record argues, and I checked it because it
decides the reject: `platform_gate` itself reads **every** `isRequired` `gate` run
(409-413, `bad = [conclusion for n in gates if conclusion not in PLATFORM_PASS]`).
Relaxing `latest_runs` alone therefore cannot admit anything — `cross_check`'s own
reader would still see the older red. The proposal as filed changes at most which
stop line prints first, and V122's stated candidate touches only that function.

The instance is real and is now unreplayable, exactly as the record says.
`121687736029` is `gate`, failure, suite `109335532941`, 16:05:56–16:06:51Z;
`121690658158` is `gate`, success, suite `109335533266`, 16:11:01–16:11:39Z; both
at head `30c940e5`. That head now lists three `gate` runs, all success at
20:54–20:55Z, one of them in suite `109335532941` — the red was superseded by a
re-run **in its own suite**, which is why "now returns only successes" holds.

What I could not measure, and what still would change the answer: whether GitHub's
own evaluation at 20:30Z would have permitted a merge at `30c940e5` with that red
standing. #2864 merged at 21:16:05Z, after the 20:54 re-runs, so the merge is not
that evidence. The record says this and names the counterexample it needs; that is
the honest disposition and it is why the reject is sound for the proposal as filed.

- Destination for the flip (a live head that merges past an older required red):
  `R10-TRAIN-OVERLAP-GRADE`, live, `queued`, files `merge_train.py` — as recorded.
- The instance's timing and citation are wrong (F6).

## P203 — ACCEPT narrowed into R10-ORCH-ROSTER-SCHEMA: confirmed

34 of 34 reproduces exactly. With the roster loader at the record's tip
`9937317d8`: 208 groups, 70 open, **34** with a non-empty `owner_gate`; 32 name a
mandate (6175172275, 6319294694 or 6329234399), 3 begin `policy:`, 2 begin
`code-owned:`, 3 rows match more than one kind, and **none of the 34 states a
decision still to be taken**. The board reproduces the line the record quotes:
"34 group(s) blocked on owner disposition; oldest issue #2259 is 11d old".

The cause reproduces at `orchestrator_tick.py:1808-1827`: `gated = [... if gid in
open_g and g.get("owner_gate")]` — the presence of any string is the whole test —
`flag=True` at 1827, and one `gh api .../issues/<n>` read at 1815 for the oldest
gated issue's `created_at`. `gate_kind` exists nowhere in the tree today (grep).
The tick reads the roster through `roster_lib` (1101-1109), so the classifier
belongs there.

288 calls/day is derived, not carried: `sweep_mech.sh:26` runs the tick with
`--interval 300`, so 86400/300 = 288, and the age read is one call per tick
whenever any gated group exists (1814-1816). On today's roster the carried arm
makes it zero.

- Destination: `R10-ORCH-ROSTER-SCHEMA` live on both rosters (`not-started`, M,
  files `roster_lib.py`, `roster_sync.py`, `roster_edit.py`), 22 carries on both.
- One Instances parenthetical names the wrong group (F7).

## Findings (each non-blocking; the ruling above stands)

- **F1 — the record's four are not "#2745's four", and the count is five.**
  `## P200` says "That is exactly the four the #2745 probe cost". #2745's four
  repairs were the ref name, the `blocked ` marker, the bus-nonce line and the
  `ev/` file naming the head (`seat-ledger.md` 1131; V120). The record's four
  unstated are the ref name, the **subject**, the first-line grammar and the `ev/`
  directory name. The subject comes from rev-2849, not #2745; and the nonce line,
  one of #2745's four, **is** stated by `fix-review.md` line 7. Three of four
  coincide, not four. And `verdict.md`'s existence is a relay check on none of
  either list — state five, or say why the file name is exempt. The cost figure
  the ruling rests on (0 lines / 3 tokens) is unaffected.
  Carry: R10-ORCH-REVIEW-PACKET
- **F2 — P201's "23 of the 72 are also listed by a done or absorbed group" does
  not reproduce.** At the record's own tip and issue set I measure **29** (done or
  absorbed) and **26** (done only, `rca-done` included). No variant I tried gives
  23. The routing figure it sits beside (72 of 72 live) does reproduce.
  Carry: R10-ORCH-ROSTER-SCHEMA
- **F3 — dispatch item 5's "the other 22 issues" is short by five.** 29 minus the
  two now-closed = 27, not 22; closing on 22 leaves five open against the round's
  completion criterion. The tick's own open-issue count self-reveals this at the
  next pass, so it is not silent — but re-derive before closing.
  Carry: R10-ORCH-ROSTER-SCHEMA
- **F4 — "79 minutes" truncates.** 17:02Z last log to 18:21:51Z found is 79m51s;
  from the 17:01:45Z launch it is 80m06s. The 88-minute figure holds (88m12s). The
  79 also appears in `seat-ledger.md` 1199, so the truncation is inherited.
  Carry: R10-FLOW-WIP
- **F5 — the record flags s44 as "no end line"; s44 recorded its exit in another
  form.** `train/s44/train.log` ends `TRAIN_RC=143 end=2026-10-26T03:01:39Z`. The
  carried detector tests only `TRAIN (DONE|STOPPED)`, so it will keep reporting
  s44 as `DEAD TRAIN` forever, which is defensible only if the arm means "not
  running" rather than "died silently". The record's own bullet discloses the
  `TRAIN_RC=143`, so this is a design choice to make explicit, not a false
  instance. Also `train.sh` is cited as :34-35; the quoted sentence is :35-36.
  Carry: R10-FLOW-WIP
- **F6 — P202's instance timing and its ledger citation are wrong.** The record
  says "s61b and then s62 merged the same PRs at 20:45Z and 20:56Z
  (`seat-ledger.md` lines 1145 and 1150)". Line 1150 is the "v7.0.5 tag absent"
  hold. The merges are s61b `#2865` at 20:45Z (line 1148) and s62 `#2864` at
  **21:16:05Z** (line 1182) — different PRs, and the later one 46 minutes after
  the stop, not 10. The 10-minute figure (line 1145, noticed at the 20:40 sweep)
  is right; the record understates the critical-path cost. The ruling is
  unaffected because its ground is A5, not the cost.
  Carry: #201
- **F7 — P203 names the wrong second `code-owned:` group.** The 34's two
  code-owned gates are `R10-ARCHSCORE-SPELLINGS` and **`R10-REPLAY-REAL-DAY`**
  (`code-owned: tests/replay.py ...`). `R10-DEPENDABOT-SETUPTOOLS` has no
  `owner_gate` at all and is not among the 34. The fixture "of the 34 gate strings"
  must be built from the roster, not from this prose.
  Carry: R10-ORCH-ROSTER-SCHEMA
- **F8 — dispatch item 1 names `R10-FLY-WIP`, which exists on neither roster.**
  The ruling's destination is `R10-FLOW-WIP`. `roster_edit.py` cites the ruling
  and will find the right name; a seat working from the dispatch list will not.
  Carry: R10-FLOW-WIP
- **F9 — two citation paths do not resolve in the tree.** `s7/tick.txt` is the
  state dir's `tick.txt` (contents at lines 3-6 and 152 match); `carries/fold-R10-FLY-POOL-INSTRUMENT.md`
  and `carries/fold-R10-FLY-RECORD-BEAT.md` are the state dir's `carries/`, not
  `dev/programme/carries/` (which holds only `carry-<N>.json`). Both fold files
  exist and do carry the deferrals verbatim, so the instruction is followable by
  the orchestrator and not by a seat reading the tree.
  Carry: #201
- **F10 — MF3's merge census has no cutoff.** "383 first-parent commits past the
  cutoff" names neither a date nor a commit, and earlier batches always name their
  window. I reproduced 382/369/13 at 2026-10-19T00:00Z and 134/132/2 since
  `09b1d002c^`; the 383 needs a cutoff one merge earlier. The figure is real, but
  as written it is not re-derivable, which is why it is here and not in the
  verified list.
  Carry: #201

## Verified, so no follower has to redo it

- #2494's evidence holds at `origin/main`: `09b1d002c` is an ancestor, its diff is
  69+/6-, `git log -S"shell continuation line is refused" -- tools/policy/agreement.mjs`
  finds it, and `node tools/policy/agreement.mjs --self-test` prints `SELF-TEST 180
  of 180 probes held`. The merge-shape census reproduces as **382 first-parent
  commits, 369 merges, 369 in the host's `Merge pull request #N from owner/branch`
  shape, 0 squash-shaped, 0 in neither, 13 single-parent** since
  2026-10-19T00:00Z; the record's 383/370 needs a cutoff one merge earlier that it
  does not name (F10). The direction of the claim — no squash-shaped merge in the
  judged history — holds.
- #2509's close rests on artifacts in the tree: `R10-MUTANT-SKIP` is `done` with
  `resume.pr=2749`, `6b5d2a8169d64ab9ec276cfa2670ae32b2e2053b` is "Merge pull
  request #2749 from tvofi/fix/r10-mutant-skip" and is in `origin/main`, and
  `dev/audit/harnesses/r10_mutant_skip/` holds `matrix.tsv`, `replay.py` and
  `null_drive.py`. `matrix.tsv` carries **6077** data rows against the 595 the
  issue's own plan states — the record quotes the plan, so a follower measuring
  "595" against the tree will miss.
- Both closes came after the record's triage commit (authored 22:11Z, committed
  22:24Z): #2494 at 22:31:43Z, #2509 at 22:47:57Z. Items 4 and 5 of the dispatch
  list were current when written and are now done; the delivery-row commit at
  23:16Z did not restate them.
- MF1: 0 matches for `pool|POOL` in `tools/audit/seat/cloud_dispatch.py` (747
  lines), no `tools/audit/seat/pool.py` tracked. MF2: `UPDATED_FOR` at
  `orchestrator_tick.py:137` with its use at 1564, the `updated-for:` rules at
  `tests/entities.py:16330-16355`, and the ancestry read at
  `.github/workflows/nightly.yml:59`. MF5: `R10-COP-PARTLOAD` is `queued`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, exit 0 (`evidence/structure.txt`).

## What a follow-up seat must be told

1. Do not close on P201's "other 22": the measured count of issues also listed by
   a done or absorbed group is 29 (27 after the two closes). Re-derive at the
   roster tip you read.
2. Build P203's fixture from the roster's gate strings. The prose's second
   code-owned name is wrong; the gated pair is `R10-ARCHSCORE-SPELLINGS` and
   `R10-REPLAY-REAL-DAY`.
3. Decide P199's arm semantics: "not running" (flags s44 for ever) or "died
   without recording" (accept `TRAIN_RC=` as an end line). Write it down either
   way; the control list has no s44 shape.
4. Dispatch item 1's group is `R10-FLOW-WIP`.
5. #2864's head `30c940e5` is still the only P202 instance; its red was superseded
   by a re-run in suite `109335532941` at 20:54, so it cannot be replayed. A new
   head where an older required red stands beside a newer green, and GitHub
   permits the merge, is the one thing that reopens P202.
6. The record's own MF4 quotes 595 rows; the delivered matrix is 6077 rows.

## Evidence (under `evidence/`)

`train-dirs.txt` (per-directory end-line table, population 27),
`train-dead-checks.txt` (rc, pid, log tails, pid liveness, live train processes),
`tick-wiring.txt` (the symlink pair, `sweep_mech.sh:26`, the board's TRAIN
section), `ledger-lines.txt` (the cited `seat-ledger.md` lines),
`fix-review-cap.txt` (the budget row, `wc -l`, the layout move, line 7),
`relay-checks.txt` (`cloud_relay.sh` 190-230), `check-runs.txt` (the two cited
runs, the head's `gate` runs now, the head's totals), `roster.txt` (the 34 gates
with their kinds at `9937317d8`, the issue join, the destination groups, the PR
join), `measure-first.txt` (MF1-MF4, the replay rows, the census),
`open-issues.txt` / `open-issues-join.txt`, `open-prs.txt`, `structure.txt`.
