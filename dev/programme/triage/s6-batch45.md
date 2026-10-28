# Proposal triage, session s7, batch 45 (P227-P231)

Five entries: V141-V145, written by the orchestrator s8 on 2026-10-28 and quoted from
`proposals.md` as they stand (V145 is a triage escalation the orchestrator routed). Facts read at
origin/main `07295d4ea`; roster at `origin/handoff/audit-r10-roster` `de410e4c9` (212 groups).
Headings carry no proposal id (P219); the `Source:` line is the one place an id is written. The
owner's standing order for this cut is critical path first, then production, then instruments by
time and tokens saved, and no item may be deferred outside round 10: a DEFER here names the
round-10 group that already carries it.

## P227: `open_pr.sh` stops on a stale local `fix/<topic>-pr` left by a merged pull request

Verdict: ACCEPT narrowed -> a carry of **R10-FLY-OPENPR-ATOMIC** (`resume.stage` `done`, 11
carries, owns `tools/audit/seat/open_pr.sh`; its carry 9, P72, already removes the branch on a
REFUSE or STOPPED exit when origin never had it, and this is the same seam on the success side).
The group is reopened first (the P196 route).

Source: `proposals.md` V141 (orchestrator s8, 2026-10-28).

Instances: the filed one plus six measured in the tree and the orchestrator's logs.
- `open_pr.sh:37` renames `BR` to `fix/<topic>-pr` when `fix/<topic>` exists locally, and `:55`
  runs `git worktree add -q -b $BR`; nothing tests the `-pr` name, so a second leftover is fatal.
  `pr_release_wt` (`pr_args.sh:141-152`) detaches on success (`:145`) and keeps the local branch;
  after the merge origin deletes the branch and the local one stays.
- `grep -l "fatal: a branch named" <orchestrator s7 dir>/*.log` lists four logs:
  `handoff-push-roster.log` (`fix/audit-r10-roster-pr`, the filed instance, #2878's leftover),
  `open-pr-buffer-store-r3.log` (`fix/r10-buffer-store-pr`), `handoff-push-cop-partload.log`
  (`fix/r10-cop-partload`) and `push-arch-shapes.log` (`fix/r10-arch-shapes`).
- `git log origin/main --merges --format=%s | grep -c 'tvofi/fix/audit-r10-roster'` = 47
  roster-topic merges; seven of them came from hand-numbered branches `fix/audit-r10-roster-pr10`
  to `-pr16` (#2812, #2823, #2842, #2851, #2857, #2861, #2864), each a `BR=` override after the
  same refusal.
- In the main checkout, `git for-each-ref 'refs/heads/fix/*-pr'` holds 22 branches; 18 of them are
  absent on origin (`git ls-remote --exit-code origin refs/heads/<b>` fails) with a tip contained in
  `refs/remotes/origin/main`.

Cost: a helper of about six lines in `pr_args.sh` (one `ls-remote`, one `for-each-ref --contains`,
one `git worktree list --porcelain` read, one `git branch -D`) and one call line in each of
`open_pr.sh` and `handoff_push.sh`; one self-test row through `pr_args.sh --self-test`, one mutant. No new file, no new check.

Binding: every reopen of a reusable topic (the roster topic reopened 47 times) costs an
orchestrator round trip today, and the predicate cannot lose work: a branch whose tip a remote
ref contains can be re-created from that ref. Narrowed against the filing in three ways: the predicate is one `pr_args.sh` helper,
called on the final `$BR` (after `:37`'s rename) before `open_pr.sh:55` and before
`handoff_push.sh:198` (the same `git worktree add -q -b "$BR"`, and the script behind the two
bare-name logs; both scripts source `pr_args.sh`, `handoff_push.sh:114`); it runs after each
script's `git fetch`, so `refs/remotes/origin/*` is current; and a branch some worktree has
checked out, or one origin could not be asked about, is refused as now. The group's `files` names
only `open_pr.sh`; the carry names the other two.

Carry text (for `roster_edit.py append-carry R10-FLY-OPENPR-ATOMIC`, citing `triage:
dev/programme/triage/s6-batch45.md#P227`): "Delete a merged leftover branch before the openers' `git
worktree add -b` (V141). Today `open_pr.sh:37` renames `BR` to `fix/<topic>-pr` when `fix/<topic>`
exists locally and `:55` runs `git worktree add -q -b $BR` (`handoff_push.sh:198` runs the same);
`pr_release_wt` (`pr_args.sh:141-152`) detaches on success and keeps the local branch, origin
deletes it at merge, and the next open of the same topic stops with `fatal: a branch named ...
already exists` (four opener logs, two from each script; seven hand-numbered roster branches `-pr10`
to `-pr16`; 18 of 22 local `fix/*-pr` branches absent on origin with tips in origin/main). Add one
helper to `pr_args.sh` (both scripts source it), called on the final `$BR` after each script's `git
fetch` and before `open_pr.sh:55` and `handoff_push.sh:198`: when the local branch exists, `git
ls-remote origin refs/heads/$BR` answers empty, its tip is contained in some `refs/remotes/origin/*`
ref (`git for-each-ref --contains <tip> --count=1 refs/remotes/origin`), and no worktree has it
checked out (`git worktree list --porcelain`), delete it with `git branch -D` and print `<script>:
deleted the merged leftover <branch> at <tip>`; in every other case stop as today. The fix touches
`pr_args.sh` and `handoff_push.sh` beside `open_pr.sh`. Controls: a leftover `fix/<t>-pr` absent on
origin, tip in origin/main, no worktree, is deleted and the open proceeds; null controls: the same
branch present on origin is refused as now; a tip no remote ref contains is refused as now; a branch
checked out in a worktree is refused as now; an `ls-remote` failure refuses as now; one mutant
dropping the containment test fails its null arm."

## P228: a red main whose every failing job names a rate limit is left red until someone re-runs it

Verdict: ACCEPT narrowed -> a carry of **R10-FLOW-MAIN-GATE** (`resume.stage` `done`, 1 carry,
owns `merge_train.py`'s main-green read, `main_green` at `merge_train.py:2422-2450`). The group is
reopened first. The orchestrator-sweep block the filing names is not carried: the sweep is a
prompt (`tools/audit/seat/sweep_template.md`) the main loop follows, and the train already reads
main's checks on every batch.

Source: `proposals.md` V142 (orchestrator s8, 2026-10-28).

Instances: two reds on main from one class after the rate-limit countermeasure landed.
- The v7.0.5 stamp `e8cb7e683`, `CI code` run 40596083060 attempt 1
  (`gh api repos/<repo>/actions/runs/40596083060/attempts/1/jobs`): `validate / validate-hacs`
  failed 22:37:27Z on `GitHubRatelimitException: API rate limit exceeded for installation` (job
  122512384418's log); `governance / env-matrix` failed 22:43:03Z on `FAIL pr / nothing skipped in
  a full clone -- skip required-contexts the GitHub API is unreachable` (job 122512384452's log);
  `gate` (job 122526090837) failed 23:09:58Z-23:10:21Z on `FAIL governance / env-matrix: failure
  (this run)`, its judge's line for a failed required job (`tools/ci/gate.py:224`; format pinned
  by its self-test at `:345`), and on none of the three strings below. Attempt 2 started 01:07:45Z
  and ended green 01:17:17Z (`.run_started_at`, `.updated_at`): `gate` red on main for 2 h 07 min,
  2 h 30 min from the first failure (validate-hacs, 22:37:27Z) to the re-run.
- 2026-10-26 04:52Z, `dev/audit/rca/ratelimit-recur.md`: main's push run at `b281d0325` red on
  record, validate-hacs and env-matrix in one dry bucket-hour; the one recovery measured there was
  a re-run (#2850, 17.0 min).

Cost: one arm in `main_green` (both the `--overlap` log-only read and the blocking one) and its
self-test rows in the 5,831-line hot file, plus one jobs listing and one log read per failed job,
only when main reads red at attempt 1.

Binding: the re-run is the measured recovery both times and a real red stays red after it, so the
risk is one spent run. Narrowed against the filing: the trigger is a closed list of the strings
this tree's own tools and CI print for an exhausted or unreachable API (`API rate limit exceeded
for installation`, `RATE-LIMITED reset_epoch=`, `the GitHub API is unreachable`), not an
open-ended "infrastructure cause"; every failed job of the run must match, except the aggregating
`gate` job, which is judged by the jobs its `FAIL <job>: ... (this run)` lines name (it qualifies
only when it names at least one job and every job it names is a failed job of the same run that
matches; any other `FAIL` line, or none, and it does not); the re-run is
`POST .../runs/<id>/rerun-failed-jobs` only when the run is at attempt 1 (the bound is the
attempt counter, so no state is kept and no second re-run can follow); and it fires no sooner than
the printed `reset_epoch`, else 3600 s after the last matching non-`gate` job completed (an
installation bucket resets hourly, `ratelimit-recur.md`), which at the stamp is env-matrix's
22:43:03Z, so a re-run due at 23:43:03Z, about 1 h 25 min before the hand re-run. The `gate` job is
re-run with the others, since `rerun-failed-jobs` takes every failed job of the run.
The root cause stays with the rate-limit groups (`R10-RECORD-API-O1`, not-started); this arm is
recovery, not the countermeasure.

Carry text (for `roster_edit.py append-carry R10-FLOW-MAIN-GATE`, citing `triage:
dev/programme/triage/s6-batch45.md#P228`): "Re-run a rate-limited red main once (V142). In
`merge_train.py`'s `main_green` (2422-2450), in both the `--overlap` log-only read and the blocking
wait: when a required context is red at main's tip, list the failed jobs of its workflow run; when
the run is at attempt 1 and EVERY failed job other than `gate` has a log containing one of `API rate
limit exceeded for installation`, `RATE-LIMITED reset_epoch=` or `the GitHub API is unreachable`,
and a failed `gate` job (the aggregator, `tools/ci/gate.py:224`) qualifies only when its log's `FAIL
<job>: ... (this run)` lines name at least one job and every job they name is a failed, matching job
of the same run, POST `repos/<repo>/actions/runs/<id>/rerun-failed-jobs` once, no sooner than the
printed `reset_epoch` (else 3600 s after the last matching non-`gate` job completed; before then log
`INFRA-RED <ctx> run <id>: rate-limited, re-run due at <time>` and go on as today), and log
`INFRA-RERUN <ctx> run <id> attempt 1 (<matched string>)`. The attempt counter is the bound: a run
at attempt 2 or later is never re-run, and the arm keeps no state. Any failed job other than `gate`
whose log matches none of the strings, a `gate` that does not qualify, or an unreadable log, leaves
today's behaviour. Instances: the v7.0.5 stamp `e8cb7e683` (run 40596083060: validate-hacs and
env-matrix failed on the installation rate limit at 22:37-22:43Z, `gate` red 23:10Z on `FAIL
governance / env-matrix: failure (this run)` until the hand re-run went green at 01:17Z; this rule
re-runs it at 23:43Z) and `b281d0325` on 2026-10-26 (`dev/audit/rca/ratelimit-recur.md`). Controls:
a fixture of the stamp's shape (validate-hacs and env-matrix failing on the rate-limit strings,
`gate` failing on `FAIL governance / env-matrix: failure (this run)`), past the reset, is re-run
once and logged; null controls: one failed job with any other failure is not re-run; a `gate` red
whose `FAIL` line names a job that failed on a non-infra cause is not re-run; a `gate` red naming a
job absent from the run's failed jobs is not re-run; the same run at attempt 2 is not re-run; before
the reset nothing is re-run and the INFRA-RED line names the due time; one mutant accepting
any-match instead of every-match fails the mixed arm."

## P229: a reviewer can be dispatched at a PR head that lacks its own handoff

Verdict: ACCEPT narrowed -> a carry of **R10-ORCH-REVIEW-PACKET** (`resume.stage` `done`, 10
carries, owns `bus.sh` and `review_packet.py`). Its reopen is already queued (batch 41, P213), so
this op is a plain append behind it. The sweep half of the filing is not carried: `bus.sh
orphans` already prints `repair=update` for a `fix/<t>` head strictly behind its handoff
(`bus.sh:692`, printed at `:697`).

Source: `proposals.md` V143 (orchestrator s8, 2026-10-28).

Instances: one, #2887. `git log -1 --format='%H %P' fdf33f466` = `fdf33f466...` with parents
`fc841f51d` and `07295d4ea` (main): the bot's merge-main of the OLD head; `git merge-base
--is-ancestor a5f40d84c fdf33f466` fails, so the PR head lacked the fixer's handoff tip
`a5f40d84c`. A body seat's ancestry check caught it before a reviewer was dispatched.

Cost: one signal in `review_packet.py` (`SIGNALS`, `:122`), which already reads
`repos/<repo>/pulls/<pr>` (`:324`) and so has the head branch name with no new API call; one `git
fetch` of `handoff/<t>` and one `merge-base --is-ancestor`; `bus.sh dispatch` already turns a
packet `REFUSE` into a refused dispatch that records nothing (`bus.sh:467`). Three self-test rows,
one mutant.

Binding: a review round on the wrong tree is an opus seat plus a re-dispatch; the check is one
ancestry read on a path every dispatch already walks. Narrowed: the topic is read from the PR's
head branch (`fix/<t>` or `fix/<t>-pr`, `open_pr.sh`'s two spellings); a PR with no
`handoff/<t>` ref, or a branch of any other shape, is not refused; the signal is
`handoff-not-applied: handoff/<t> <tip> is not an ancestor of <head>`. Controls: #2887's shape
(head = merge of the old head and main, handoff tip outside it) refuses; null controls: a head
containing the handoff tip renders; a PR with no handoff ref renders; one mutant inverting the
ancestry test fails both.

Carry text (for `roster_edit.py append-carry R10-ORCH-REVIEW-PACKET`, citing `triage:
dev/programme/triage/s6-batch45.md#P229`): "Refuse a reviewer dispatch at a head that lacks its own
handoff (V143). Add a signal `handoff-not-applied` to `tools/audit/seat/review_packet.py`
(`SIGNALS`, `:122`): from the pull request it already reads (`repos/<repo>/pulls/<pr>`, `:324`) take
the head branch; when it is `fix/<t>` or `fix/<t>-pr` and `origin/handoff/<t>` exists (one `git
fetch origin handoff/<t>`), refuse with `REFUSE handoff-not-applied: handoff/<t> <tip> is not an
ancestor of <head>` when `git merge-base --is-ancestor <tip> <head>` fails. `bus.sh dispatch`
already refuses on a packet REFUSE and records nothing (`bus.sh:467`). Instance: #2887, head
`fdf33f466` = merge of the old head `fc841f51d` and main `07295d4ea`, lacking the fixer's handoff
tip `a5f40d84c`; caught by a body seat before dispatch. A branch of any other shape, or a missing
handoff ref, is not refused. Controls: #2887's shape refuses; null controls: a head containing the
handoff tip renders; a PR with no handoff ref renders; a non-`fix/` branch renders; one mutant
inverting the ancestry test fails the refusal and the first null arm."

## P230: the sweep's loop block and the resume prompt do not list the cloud relay loop

Verdict: DEFER -- owned by **R10-ORCH-BEATD** (`not-started`, 35 carries). Its carry 1 makes the
relay one of the beat's detached jobs (the "handoff job", with `heartbeat` registered as a beat job
by its carries 1 and 5), and its carry 28 owns the detection of a must-run loop that died
unnoticed (two loops dead about 16 h on 2026-10-25). Nothing is carried.

Source: `proposals.md` V144 (orchestrator s8, 2026-10-28).

Instances: one. The relay was not running at rotation and was restarted by hand as pid 15079
(`ps -o pid,etime,command -p 15079` shows it running `cloud_relay.sh pass --confirm`).
- The sweep script the filing names is the orchestrator's own state file, not in the tree
  (`git ls-files | grep -c orch_sweep` = 0, P224); its loop list is
  `for frag in "tick_loop.sh" "state_docs.py" "wt_sync.sh" "roster-loop.sh"` and `grep -c -F
  cloud_relay` on it is 0.
- `tools/audit/seat/handover_prompt.py` has no loop list (`grep -c -i loop` on it is 0), so its half of the filing is a new section, not two lines.

Cost: the tree half is a new handover section in a file R10-ORCH-BEATD will regenerate.

Binding: the tree half belongs to the group that turns these loops into supervised jobs, whose
carry 28 already records the class; a second list in `handover_prompt.py` would go stale when the
beat lands. The two-line edit to the orchestrator's own sweep script is not a tree change and
needs no ruling: it is the orchestrator's to make (sent to it, not carried).

## P231: a `--bot-prs` batch holds the approver beat off the record PR it waits on, silently

Verdict: ACCEPT narrowed -> (a) a carry of **R10-TRAIN-OVERLAP-GRADE** (`resume.stage` `done`, 15
carries, owns `merge_train.py`; its reopen is queued from batch 44, P220, and the orchestrator has
confirmed it). Arm (b) is owned by **R10-RECORD-HOLD-APPROVE** (`not-started`, critical path,
P198), whose brief already is this defect: move `nightly.yml`'s train-hold block after the approver
App's review, so a held beat still approves. Nothing new is carried for (b).

Source: `proposals.md` V145 (triage s8 escalation, routed by orchestrator s8, 2026-10-28).

Instances: #2893, the v7.0.5 stamp's record PR (P221's instance): the merge seat's ledger, 22:19Z
and 22:44Z, records `gh pr merge` refused by `main-protect-checks` for want of an approving review,
the approver beat suppressed by the train's hold, and a merge 49 s after the hold was released.
R10-RECORD-HOLD-APPROVE's brief records the first instance (#2856, about 3 h at REVIEW_REQUIRED).
- `merge_train.py:1110`, in `sweep_bots`: `self.run(["gh", "pr", "merge", n, ...])` with its return
  discarded; the following `gh pr view` logs only `BOT #<n> not merged at <h> (OPEN null)`.

Cost: (a) two lines (keep the code and text, put `gh`'s last refusal line in the `BOT ... not
merged` line) and one self-test row. (b) nothing new.

Binding: (a) is cheap and turns a silent stall into a named one at the next sweep. (b) as filed --
the train requesting the beat -- would put a second approval path into the 5,831-line hot file for
the defect R10-RECORD-HOLD-APPROVE fixes in `nightly.yml` with no change to `merge_train.py`; one
owner, one fix. Controls for (a): a fixture `gh pr merge` refusal text appears verbatim in the `BOT`
line; null control: a merged PR logs `BOT #<n> MERGED` as today; one mutant dropping the text
fails the first arm.

Carry text (for `roster_edit.py append-carry R10-TRAIN-OVERLAP-GRADE`, citing `triage:
dev/programme/triage/s6-batch45.md#P231`): "Name `gh pr merge`'s refusal in the train's record-PR
sweep (V145 arm a). `merge_train.py:1110`, in `sweep_bots`, discards the return of `gh pr merge`, so
a refused record PR logs only `BOT #<n> not merged at <h> (OPEN null)` (#2893, the v7.0.5 stamp's
record PR, refused by `main-protect-checks` for want of an approving review). Keep the code and
output, and put `gh`'s last non-empty output line (up to 200 characters) in the `BOT ... not merged`
line as `refused: <text>`. Arm (b), the approver beat held off by the train's hold, is
R10-RECORD-HOLD-APPROVE's brief (nightly.yml) and is not built here; no second approval path in
merge_train.py. Controls: a fixture `gh pr merge` refusal text appears verbatim in the BOT line;
null control: a merged PR logs `BOT #<n> MERGED` as today; one mutant dropping the text fails the
first arm."
