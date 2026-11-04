# Proposal triage, session s12, batch 120 (P384 and P385)

The rolling batch after batch 119. Facts were read at origin/main `2a9cd3476`, at the round's roster
branch `origin/handoff/audit-r10-roster` (`37843c16d`), in the opener's and relay's logs, and in the
session transcripts.

**Numbering.** The queue files these as P375 and P376. Those numbers already name rulings on main
(`s6-batch115.md#P375`, `#P376`), with different subjects. P383 is in batch 119, which is on
`handoff/triage-s12-batch119` and not yet on main. These entries take the next free numbers, and each
title names the number it was filed under.

## P384: `train.sh` finds no seat venv under the programme state dir (filed as P375)

Verdict: REJECT. The binding cost is a fixer and a reviewer round on `train.sh`, whose every roster
group is done, against a refusal that took one seat 10 min (10:11Z to 10:21Z) and has come up on three occasions. One local command answers
it for every instrument at once. The answer changes if a later round's state dir repeats the refusal
with the symlink in place, or if a group already editing `train.sh` opens.

Source: the orchestrator's queue line of 2026-11-04T19:56:40Z, from the merge seat. `train.sh add`
takes its venv from `HPO_STATE_DIR/venv-ci`, while the handoff's environment sets `HPO_STATE_DIR` to the
programme state dir. It proposes resolving the venv independently of that dir.

Instances:
- **The refusal: 6 real ones in 3 sessions.** Tool results in session transcripts of the last 10 days
  whose text holds `train.sh: REFUSE: no seat venv at /`: one on 2026-10-29 at 17:22Z, four from one
  seat on 2026-11-04 from 10:11Z to 10:21Z, and one on 2026-11-04 at 19:12Z. `train.log` holds none
  (`grep -c 'no seat venv'` prints 0), because the refusal comes before the train starts.
- **The cause.** `venv-ci` does not exist in the programme state dir, and `~/.local/state/hpo/venv-ci`
  does (`ls -d`). The refusal prints the path it tried, and by the filer's line a seat overrides the
  variable to get past it.
- **`train.sh` is the one arm with no fallback.** `train.sh` lines 403 to 406 and 446 to 451 read only
  `${HPO_STATE_DIR:-$HOME/.local/state/hpo}`. The `seat-python` shims try `$STATE` and then the default
  (`shims/seat-python3` line 28). The comment at line 442 rules out an ambient fallback, and the default
  dir is not ambient, so a code fix would be sound. It is the cost that loses.
- **Who could carry it.** No open group owns the file. Every roster group whose `files` name `train.sh`
  is done (R10-FLOW-AUTOTRAIN, R10-TRAIN-UPGRADE, R10-FLY-TRAIN-DEFAULTS). A fix is a new fly-in, and its
  self-test arm for an absent venv needs a fake `HOME`, because the host's default now satisfies it.
- **Rule run: a symlink, on a scratch directory.** `ln -s ~/.local/state/hpo/venv-ci <dir>/venv-ci`,
  then:
  - `[ -f <dir>/venv-ci/bin/python3 ]`, the test `train.sh` runs, passes;
  - that interpreter runs Python 3.14.7, reports `sys.prefix` under the scratch directory and imports
    the venv's `yaml` 6.0.1.
  - `train.sh add` itself was not run with it, because a real add moves the queue.

Cost:
- Tracked fix: about 5 lines in two arms of `tools/audit/seat/train.sh` (484 lines on main), one
  self-test arm, a new group, a fixer, a reviewer and a CI run.
- `train.sh` is not a policy file, so it has no `policy_lint.mjs --budgets` row. This ruling touches no
  capped file.
- Local: one command, no disk (the venv is 152M, shared), no standing cost.

Binding:
- **Why REJECT and not a carry.** The trade is one refusal that names its own path, at most 10 min measured
  per occasion, against a whole fly-in with a round closing.
- **What stays with the orchestrator, one operation and no roster op:** `ln -s
  ~/.local/state/hpo/venv-ci "$HPO_STATE_DIR/venv-ci"` on this host. The merge seat then needs no
  override, and `update_pr.sh` line 36 and the shims find the same interpreter.

## P385: the update arm retries a handoff whose update was refused (filed as P376)

Verdict: ACCEPT, narrowed to one carry on R10-HANDOFF-PATH, and not as filed. The filed key would have
blocked every one of the 22 updates that this retry got through. The defect sits in a session-local
driver beside the relay, and the relay already refuses to repeat a key. What the tracked path lacks is
the opposite: any retry of a refusal that clears on its own.

Source: the orchestrator's queue line of 2026-11-04T20:33:24Z. #3195 refused on unpinned sites at
19:23Z, was retried at 20:01Z for about 27 min of prepr in a heavy slot, with the same body. It
proposes keying a retry on the handoff or body ref having moved since the refusal.

Instances:
- **The instance took two instruments, not one retry.**
  - `cloud-relay.daemon.log` lines 7869 to 7873: at 19:23:12Z the relay's handoff arm ran `update_pr.sh`
    for `e0a411f21`, and it refused on `unpinned sites`. The relay recorded the key: line 95 of
    `cloud-handoff-failed`.
  - `driver4.out` lines 2 and 3: at 20:01Z the opener driver started its own update of the same sha. Its
    `fails.txt` had no row for it, because the refusal was the relay's.
- **The filer's "same refusal" was not observed.** The 20:01Z run ended `rc=-15` at 20:32Z, with no
  REFUSE line in its log (`drv-r10-sav-comfort-p3-2001.log`). The run lasted about 31 min; the filer's
  figure for its prepr is about 27. Who stopped it was not read.
- **The relay already keeps the filed rule.** `cloud_relay.sh` lines 478 to 483 skip a key in
  `cloud-handoff-failed`, and a failed body-only run's key takes the body sha. The relay's log holds no
  repeat: 6 parsed refusals, 0 of them the same topic, sha and class (Python over `is ahead of` lines
  followed by a `REFUSE` line).
- **R10-HANDOFF-PATH carry 8 owns the rest of that key:** `(topic, handoff sha, body sha)`, so a body
  repair re-triggers it, and the reason kept. It is not built.
- **The tracked opener has no update arm.** `open_driver.py` line 11: "The OPEN arm only:
  cloud_relay.sh's handoff arm owns update_pr.sh." So this retry exists only in the session-local
  `driver4.py`.
- **Rule run: the driver's update arm against the relay's failed keys.** All of `driver4.log` and
  `driver4.out`, `RESULT handoff-update` lines, each key read against `cloud-handoff-failed` (94 rows):

  | result | runs | key in the relay's failed list |
  |---|---|---|
  | rc 0 | 22 | 22 |
  | rc not 0 | 23 | 23 |

  Every key this arm ran had a relay refusal on record (the list keeps no time, so the order is inferred:
  a relay update that succeeded would have left nothing to update). 22 of 45 got through **at the same
  handoff sha**.
  The filed key's handoff half blocks all 22. Its body half would release only those whose body moved:
  not read, since the body refs' history for these topics was not traced and most `.why` reasons were
  never kept (15 rows of 94, carry 8's "unrecoverable").
- **The same-sha retries inside the driver.** From `driver4.log`, a retry after a refusal at the same
  sha, by class of the earlier refusal, with its minutes:

  | earlier refusal | retries | outcome | minutes |
  |---|---|---|---|
  | `ancestry reds` | 6 | 2 through (22 min), 3 the same refusal (18), 1 a different refusal (36) | 54 not through |
  | `carry` BAD-DEST (#3089) | 2 | the same refusal | 5 not through |
  | app_push dirty worktree | 1 | the same refusal | 16 not through |
  | `ci predict` or a failed push | 2 | a different refusal | 27 not through |

  `ancestry reds` clears without a ref moving, as CI settles. A body-content refusal does not. The filed
  waste is the second row plus #3195, about 36 min over the log's 5 days.
- **Rule run: a class-keyed retry on the same instances.** Body-content refusals (`unpinned sites`,
  `carry`) wait for the body ref to move; others retry with backoff:
  - #3195 19:23Z `unpinned sites`: no retry until the body moves, so the 31 min is spared.
  - #3089 BAD-DEST: no retry until the body moves, so 5 min is spared.
  - #3085, `r10-replay-real-day` and `r10-record-s9-owed` on `ancestry reds`: retried, and the two
    `r10-replay-real-day` retries that got through still get through (the null control).

Cost:
- About 10 lines in `handoff_arm` of `tools/audit/seat/cloud_relay.sh`, beside carry 8's edit to the same
  key, and three fixture arms. No new file, check or API call, in a group not yet started
  (`R10-HANDOFF-PATH`, stage `not-started`, no `after`).
- `cloud_relay.sh` is not a policy file, so it has no `policy_lint.mjs --budgets` row.
- Without it: when `driver4.py` retires for the beat's `opener` row, which runs `open_driver.py`, a refused
  update has no retry at all, and the 22 of 45 become hand work on a standing `OWED handoff-update` line.

Binding:
- **Why ACCEPT.** This is the finding that changes a later stage: the design for the beat folds the
  driver's retry semantics into `open_driver.py` (design note `21210036`, §7 item 20), which has no update
  arm, and R10-HANDOFF-PATH carry 5 names the driver, so the relay's half is on nobody's list
  (`finding-propagation.md`). The measured benefit is the
  22.
- **Why not the filed form.** The benefit it names is about 36 min in 5 days, and the key it names blocks
  the route that delivered 22 updates. A local patch to `driver4.py` for those 36 min is a marginal
  trade and is not owed: `MAXTRY` already bounds a key at 3 tries.
- **Carry text for R10-HANDOFF-PATH:** the relay's handoff arm retries an update refusal that clears
  without a ref moving. Today a key in `cloud-handoff-failed` never reruns (`cloud_relay.sh` line 480), and
  `open_driver.py` is "the OPEN arm only", so once the session-local driver retires nothing retries a
  refused update. That driver's update arm got 22 of its 45 runs through at the same handoff sha after the
  relay had refused it. In `handoff_arm`, with carry 8's reason kept: a refusal whose step is `unpinned
  sites`, `carry` or another body-content step stays recorded until the body ref moves (carry 8's key). Any
  other refusal, such as `ancestry reds` or `ci predict`, reruns on a backoff of at least 30 min, at most
  three tries, then stays as today's OWED `handoff-update` line with its reason. Fixture arms: (a)
  `ancestry reds`, then clean, updates on the retry; (b) `unpinned sites` with the same body does not rerun
  and with a new body does; (c) three refusals of a retryable class stop and print the OWED line. Mutant:
  retrying every class fails (b). triage: dev/programme/triage/s6-batch120.md#P385
