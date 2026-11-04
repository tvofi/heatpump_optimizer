# Proposal triage, session s8, batch 68 (P299-P300)

The rolling batch (V182) after batch 67 (#2983, merged at `b646e8306`). Facts were read at
origin/main `b646e8306`, on the roster branch `origin/handoff/audit-r10-roster` (`4c91e6877`), in
the orchestrator's state directory (`seat-ledger.md`, `s7/launch-ledger.txt`,
`s7/roster-queue-s7.txt`, `s7/orch_sweep.sh`, `s7/seat-launch.sh`, `s7/roster-s8-loop.py`,
`s7/HANDOVER-s8.md`) and from `ps`.

## P299: a standing seat's alive file is fresh while no seat exists

Verdict: ACCEPT narrowed, in two halves, because the instrument the filing names is out of the
tree and the in-tree owner of this class has closed without building it.
- (a) In tree: a new S fly-in, **R10-FLY-SEAT-ALIVE-ID** (`groups/R10-FLY-SEAT-ALIVE-ID.json`). It
  builds the `--seat-alive` arm of `tools/audit/seat/pulse.py` with per-seat-id entries and a
  `FOREIGN` reading, and `tools/audit/seat/sweep_template.md` step (1b) runs it.
- It takes over two carries that R10-ORCH-BEATD left unbuilt: P46's arm (`s6-batch2.md#P46`) and
  P97's per-id entry (`s6-batch21.md#P97`).
- (b) Out of tree: the orchestrator makes the filing's nonce check in its own `orch_sweep.sh` and
  seat briefs now, as P236 ruled for the same scripts (`s6-batch48.md#P236`). That half is sent to
  the orchestrator and not carried.
- The filing's form is narrowed in two ways. The nonce is compared with the newest launch of the
  role that has no stop line, never with "any live launch". The board's `ok` wording changes,
  because a fresh file was never a seat.

Source: `s7/triage-queue-s7.txt` line 13 (orchestrator s8, 2026-10-30T09:33:31Z, slip).
`orch_sweep.sh` printed `ok merge seat beat 50s ago` while no merge seat existed. An orphaned
41 h-old zsh loop, pid 29401, left behind by a past seat's Bash call, kept touching
`s7/merge.alive`. The live train ran across a session handover with no seat watching it.

Instances. This is the same class as P188 (`s6-batch32.md`) and P204 (`s6-batch36.md`): an alive
file written by a process that is not the seat the board names.
- **This one.** `seat-ledger.md:2463` reads `orch s8: stopped orphan beat loop pid 29401 (touched
  merge.alive with no seat); launched merge seat e9e6d824886e8e82` at 09:33:22Z. A loop 41 h old
  at 09:33Z started about 16:30Z on 2026-10-28. That is before the last s7 merge launch,
  `8741ed6aeec213f0` at 21:31:35Z (`awk '$3=="merge"' s7/launch-ledger.txt`). So it was a
  predecessor's loop, the case step (1d) of the sweep's P188 interim says to stop by PID at
  relaunch (`sweep.md:47`). That step was not taken at the 21:31Z relaunch.
- **The window it masked, measured.** The merge seat's last own line is `seat-ledger.md:2454`
  (`merge s7 SLIP for triage`, after 08:29:43Z). `s7/HANDOVER-s8.md` dates the handover about
  09:20Z, and the relaunch is 09:33:16Z. The s8 sweep's ListAgents step found the missing seat
  13 min after the handover. The board's `ok` line covered at most about 1 h.
  - In that time the train ran on and merged #2982 (09:22:58Z), #2981 (09:23:38Z) and #2983
    (09:32:03Z) (`git log --first-parent origin/main`).
  - The s8 seat's first pass then found `#2978/#2973 verdicts name old heads, left out`
    (`seat-ledger.md:2464`).
- **P188, two instances (2026-10-25).** The w41 `loop.sh` touched `dispatch.alive` with its agent
  gone, for up to 22 min, and an hour after w43 had replaced it. `roster.alive` was fresh with no
  roster process.
- **P204 (2026-10-27).** Two triage writers shared `triage.alive` for 90 min.
- **A live writer of the same shape.** `s7/roster-s8-loop.py`, the s8 roster seat's scratch
  runner, is a `while True` loop that touches `roster.alive` every 300 s whatever its agent is
  doing. `ps` shows it not running at 2026-10-30T09:51Z, so it is not counted, but it is the
  shape P51 rejects.
- **Count.** Four instances in round 10, so this is an audit class (`defect-root-cause.md`), and
  it owes a barrier, not a refusal.
- **The barrier's owner closed without building it.** R10-ORCH-BEATD carries P46 (`--seat-alive`),
  P97 (one alive entry per seat id, DUPLICATE) and P63 (a generation token). On the roster branch
  its `resume` is `{'stage': 'done', 'pr': 2916, 'commit': '0b17333c2'}`. #2916, "R10-ORCH-BEATD
  arm (a): supervised beat engine and beat git shim", merged 2026-10-29T02:59:05Z. At origin/main,
  `git grep -n 'seat-alive\|DUPLICATE seat' -- tools/audit/seat/pulse.py` finds nothing. Main's
  roster copy still reads `in-progress`, but the roster branch is the live record. So the three
  carries are stranded on a done group.
- **The gap in P97 that this instance shows.** P97 reads one alive entry per seat id "beside the
  per-role file". It does not say what a role reads when the per-role file is fresh and no id
  entry is. That is pid 29401's shape: an unattributed writer, and no seat.
- **The launch ledger is itself red right now.** `seat-launch.sh --dup merge` prints `DUPLICATE: 2
  live launches for role 'merge'` (8741ed6a, e9e6d824). `--dup triage` prints the same
  (25222de4, ef0ff4b2). No `--stop` was written for the dead s7 nonces at the s8 relaunches,
  though `seat-launch.sh`'s header names that as the dispatcher's obligation. "Newest launch
  without a stop" is still well defined under that noise. "The live launch" is not, which is
  narrowing 1.

Cost:
- (a) is one S fly-in: about 40 lines in `pulse.py` (`--seat-alive SEAT=FILE[:MIN]` plus
  `--launch-ledger FILE`), one sentence in `sweep_template.md` step (1b), and fixture rows. It
  runs on a sonnet fixer and an opus reviewer, one pull request, about 2 to 3 seat-hours.
- It adds no API call. At run time it is one local read per sweep. It adds no standing CPU.
- `pulse.py` and `sweep_template.md` are not capped files.
- (b) is about 10 lines in `orch_sweep.sh`'s standing-seats loop, plus one word per standing
  brief (`echo <nonce> >` in place of `touch`). It is out of tree
  (`git ls-files | grep -c 'orch_sweep\|seat-launch'` = 0). It adds no review round.
- No capped file is touched. The `--budgets` rows of the files nearest the seam stay as they are,
  and this ruling adds nothing to them:
  - `dev/governance/roles/standing-merge.md` 37/37 lines, 507/507 words.
  - `standing-roster.md` 27/27, 368/368.
  - `standing-dispatch.md` 39/39, 509/509.
  - `proposal-triage.md` 36/36, 489/489.
  The nonce reaches each seat through its brief, which is out of tree.

Binding:
- **Benefit.** Four instances of one class in one round. The newest put a false `ok` on the board
  for up to about 1 h over a live train. A false `ok` is the failure this check exists for
  (`orch_sweep.sh`'s own header: the 10 h dead merge seat).
- **The tree needs its own half.** The out-of-tree checks decay: `seat-launch.sh --dup`, the
  out-of-tree barrier P204 deferred to, reads DUPLICATE for two roles today and nobody has
  repaired it. A tree arm with fixtures does not decay that way.
- The class rule binds anyway.
- **Rejected in the filing's form: "the nonce of the newest live seat-launch.sh entry".** "Live"
  in `seat-launch.sh` means "no stop line". The ledger reads DUPLICATE for two roles today, so it
  is ambiguous. Narrowed to the newest launch line for the role with no stop line, compared by
  equality.
- **Recorded limit, not carried.** A nonce does not tell a seat from its own orphaned loop: P188's
  first 22 min, where the agent died and its `loop.sh` went on writing w41's id. P63's generation
  token and P51's rule (a seat waits in a `run_in_background` job it re-arms on its own turn,
  never a detached `while` loop) own that sub-case. P63 is stranded on R10-ORCH-BEATD as well, and
  re-routing it is the orchestrator's call, not this ruling's.

Group brief (for `roster_edit.py append-group`, `groups/R10-FLY-SEAT-ALIVE-ID.json`, citing
`triage: dev/programme/triage/s6-batch68.md#P299`). The brief is in the group file. It re-routes
P46 and P97 from R10-ORCH-BEATD (done at #2916, both unbuilt) and adds P299's FOREIGN arms.

To the orchestrator, not carried (out of tree, P236 precedent):
1. Each standing brief has its seat write its launch nonce into `<role>.alive` on every pass.
   `orch_sweep.sh`'s standing-seats loop then reads the content and compares it with the newest
   unstopped launch for the role (`awk '$3==r' launch-ledger.txt | tail -1`, less stopped
   nonces). A mismatch or an empty file prints `FOREIGN BEAT <role>` with rc=1. The `ok` line
   reads `ok <role> beat <n>s ago, nonce <8>` and names presence as ListAgents' (step 1d).
2. Write `seat-launch.sh --stop` for the dead s7 nonces now: merge `8741ed6aeec213f0` and triage
   `ef0ff4b26c23dd66`. Until then the board's seat-launches section reads DUPLICATE for both roles
   on every sweep.
3. R10-ORCH-BEATD is `done` with P46, P63 and P97 unbuilt. This ruling re-routes P46 and P97 to
   the new group. P63 (`s6-batch5.md#P63`, the seat generation token) needs its own re-route or
   a recorded drop.

## P300: the roster queue runner passes a trailing comment as arguments, and marks nothing

Verdict: ACCEPT, in two parts, both carries on **R10-ORCH-ROSTER-SCHEMA** (`carries-open`, M). It
owns the roster write path (`roster_edit.py`, `roster_lib.py`), and `tools/audit/seat/roster_queue.py`
joins its files.
- (a) ACCEPT as already carried, narrowed. The group has held this exact fix since 2026-10-25.
  Its carry reads: "the line grammar strips an unquoted trailing `#` comment before splitting".
  It was never built. The filing's form, `shlex.split(ln, comments=True)`, is REJECTED: it cuts
  a `#` in the middle of a word as well (measured below). The carry gains two control rows.
- (b) ACCEPT narrowed: a `--mark` flag in `run`. Each applied line is rewritten in the queue file
  as `#done <line>` or `#refused <line>`, the convention the queue already uses. The write must
  never lose a line the orchestrator appends meanwhile.

Source: `s7/triage-queue-s7.txt` line 14 (orchestrator s8, 2026-10-30T09:41:50Z, instrument
defect).

Instances:
- **The defect, reproduced at origin/main.** `parse_line` (`roster_queue.py:77-90`) calls
  `shlex.split(ln)`. `parse_line('set-stage G done  # #2955 merged aced2589')` returns
  `('set-stage', 'G', 'done', ['#', '#2955', 'merged', 'aced2589'])`, so the comment reaches
  `roster_edit.py` as four arguments.
- **The filing's fix over-reaches.** `shlex.split(..., comments=True)` turns
  `append-carry G @/p/b#1.txt` into `['append-carry', 'G', '@/p/b']`, and `append-carry G text#2 x`
  into `[..., 'text']`. So does a `shlex.shlex` with `whitespace_split=True` and `commenters='#'`.
  The live queue holds one such argument: `#refused drop-carry R10-FLY-OPENPR-ATOMIC --match
  's6-batch8.md#P70'`. It is safe only because it is quoted; unquoted, it would be cut. A comment
  is a `#` at the start of an unquoted word, as in a shell.
- **Count in this session's queue** (`s7/roster-queue-s7.txt`, 374 lines):
  - 181 are `#done` and 136 are `#refused`.
  - Of the `#done` lines, 16 carry ` # ` after the op. They were applied by hand or by a later
    stripped re-run.
  - Of the `#refused` lines, 3 carry ` # `. That is 19 lines in all, the filing's figure.
- **The earlier instance.** R10-ORCH-ROSTER-SCHEMA's carry records the same defect on 2026-10-25
  (queue lines 262-277, 16 drop-carry ops refused and re-run by hand).
- **The marking gap.** `run_queue` takes FIRST..LAST and writes only a report. Every seat that
  runs it keeps its own cursor or marking in a scratch wrapper. Measured: `s7/roster-loop.sh`
  (90 lines, s7) and `s7/roster-s8-loop.py` (111 lines, s8). The s8 wrapper's `mark()`
  read-modify-writes the queue file with `open(Q, "w")`, with no guard against a concurrent
  `>>` append. It also holds every commented line back for hand processing, which is the
  workaround the filing names. That is two re-implementations in two sessions, each with its own
  defect, and orchestrator.md section 13 names a scratch copy of a tree instrument a defect.

Cost:
- (a) is about 5 lines in `parse_line` and three self-test rows, inside a group already open.
- (b) is about 25 lines: a `--mark` flag, and a rewrite that re-reads the file, prefixes the
  matched line, and replaces the file atomically (`os.replace` from a temp file in the same
  directory), with two self-test rows.
- Neither adds a file, API call or standing CPU. `roster_queue.py` is not a capped file.
- R10-ORCH-ROSTER-SCHEMA is M with 30 carries. These two are on its write path and touch one
  file it does not yet list.

Binding:
- **Benefit.** The comment defect cost 16 refusals on 2026-10-25 and 19 in s7. The marking gap
  produced two untracked wrappers in two sessions, and both repeated defects the tree runner
  should own. The s8 wrapper's non-atomic rewrite can drop a line the orchestrator appends during
  a pass.
- **Cost.** About 30 lines in a group already open on the same seam. That clearly favours the
  fix.
- (a) narrowed: the filing's `comments=True` would silently truncate any `#` inside an unquoted
  word, such as a path or a `--match` anchor. That would turn a loud refusal into a quiet wrong
  edit, a worse failure than the one it fixes.

Carry text (a) (for `roster_edit.py append-carry R10-ORCH-ROSTER-SCHEMA`, citing
`triage: dev/programme/triage/s6-batch68.md#P300`): "Amends this group's 2026-10-25 trailing-comment
carry (P300, queue 2026-10-30T09:41Z: 19 more lines refused or held in s7/s8).
- `tools/audit/seat/roster_queue.py` `parse_line` (77-90) drops a comment that starts at an
  unquoted word beginning with `#`, and only that: shell semantics. Do NOT use
  `shlex.split(ln, comments=True)` or `shlex.shlex(commenters='#')`. Both cut a `#` in the middle
  of a word (`@/p/b#1.txt` -> `@/p/b`, measured).
- Add `tools/audit/seat/roster_queue.py` to this group's files.
- Self-test rows:
  - `set-stage G done  # #2955 merged aced2589` parses to `('set-stage', 'G', 'done', [])`.
  - Null: `append-carry G @/p/b#1.txt` keeps `@/p/b#1.txt`.
  - Null: `drop-carry G --match s6-batch8.md#P70`, unquoted, keeps `s6-batch8.md#P70`.
  - A quoted `'a # b'` stays one argument.
- One mutant: restore the plain `shlex.split(ln)`, and the comment row fails."

Carry text (b) (for `roster_edit.py append-carry R10-ORCH-ROSTER-SCHEMA`, citing
`triage: dev/programme/triage/s6-batch68.md#P300`): "`tools/audit/seat/roster_queue.py run`
gains `--mark` (P300).
- After each op's report line, the queue line it applied is rewritten in place as `#done <line>`
  when pushed (and the read-back did not print FAILED), else as `#refused <line>`.
- The rewrite re-reads the queue file at write time and matches the exact line text, first
  unmarked occurrence. It writes through a temp file in the same directory and `os.replace`, so
  a line another writer appended after the run's first read is kept.
- `run` with `--mark` also accepts `all` for FIRST..LAST, meaning every unmarked op line, so a
  seat needs no cursor.
- Lines already starting with `#` (`#done`, `#refused`, `#held`, `#note`) are never applied,
  which is today's skip, now documented.
- Basis: the s7 and s8 roster seats each wrapped the runner in an untracked loop
  (`roster-loop.sh` 90 lines, `roster-s8-loop.py` 111 lines) for this marking alone. The s8
  `mark()` rewrites with `open(Q, 'w')` and no guard.
- Self-test rows:
  - A pushed op marks `#done`; a refused op marks `#refused`.
  - A line appended to the queue between the run's first read and the mark survives.
  - Null: without `--mark` the queue file is byte-identical after the run.
- One mutant: write the run-start snapshot instead of re-reading, and the appended-line row
  fails."
