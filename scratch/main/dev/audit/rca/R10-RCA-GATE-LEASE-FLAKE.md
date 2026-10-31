# R10-RCA-GATE-LEASE-FLAKE: a "wall-clock" gate-lease check is a real race in `tests/gate_lock.py`

Root-cause seat, `dev/governance/roles/root-cause.md`, 2026-10-24, mandate
6329234399. Measured at `origin/main` `0c3640761`.

Trigger: `tests / fast (3.14)` red on unrelated PRs with
`FAIL gate lease priority: concurrency control: two waiters released in one poll,
exactly one holds the slot  [queued=True overlaps=1 order=['b', 'a']]`
(job 120835946109, run 40081490403, #2692). The red-check trigger of
`defect-root-cause.md` applies: the same failure was reachable earlier and
cheaper, by a deterministic test.

## 1. Cause: production, not the check

The check is not flaky timing. `overlaps=1` means two takers held the one slot
at once, and that is a defect in `tests/gate_lock.py`, which is the lease that
admits `prepr.sh` / `update_pr.sh` / `app_push.sh` runs. Two non-atomic file
operations on the owner file:

1. `Owner.create` did `os.open(O_EXCL)` and then wrote. Between the two the slot
   file exists and is empty. `_read_at` parses an empty file as no owner;
   `_free_slot` treats an unparseable slot as a broken holder and
   `path.unlink`s it ("no live holder to lose"). A rival in that window deletes the
   creator's slot, creates its own, and both return holding slot 0.
2. `Owner.write` (renew / same-label refresh in `take_slot`) did `write_text`,
   which truncates first. A waiter's `_free_slot` reading in the truncation
   window sees an empty slot and unlinks a live holder's slot the same way.

(2) is the wider cause behind the reported one: the same `unparseable == free`
rule is reached by every torn write, create or renew.

Reproduced at `origin/main`, deterministically, by hooking `Owner._text` so a
rival `take_slot` runs while "a"'s slot file exists and is empty:
`winners=['rival', 'a']`. For (2), a reader loop against 20000 `write` calls read
the file as no owner 15007, 15133 and 17618 times in three runs.

Direction check (`root-cause.md` s1): `git log -S"O_EXCL" -- tests/gate_lock.py`
shows the create-then-write shape from `c09cf1201` (2026-10-16, #2267, the slot
pool). The check `one_winner` came later (`131f81957`, 2026-10-20) and is the
detector; production is what moved wrong, not the test.

## 2. Process state: (c)

A concurrency-control test existed (`one_winner`, "exactly one holds the slot")
and ran on every `fast` job. It was followed and did not produce the intended
result: its race window is microseconds wide, so it detected the defect only when
a loaded runner stretched the window. To a reader a failure that appears about
once a day looks like timing noise; this is the opposite, a probabilistic
detector for a real defect. The countermeasure is therefore a detector that
reaches the window by construction, not a firmer instruction (which would be the
(b) mistake).

## 3. Counts (last seven days of failed runs; bulk-listed once, no 403 or rate-limit line in any call)

Failed-run list `actions/runs?status=failure&created>=2026-10-17`, capped by the
API at 1000 (earliest returned 2026-10-20). Scanned: all 64 failed `CI *` runs
(all their failed jobs), and the `fast`/`ci-ratchet` failed jobs of the 210
failed `Tests` runs from 2026-10-22 onward (the older `Tests` runs, about 281, were
not scanned). 21 failed `fast (3.14)` jobs were read in full; the `a3:`/`a4:`/`hb:`
FAIL lines in them are the suite's own expected-fail null controls and are not
counted.

| run | job | when (UTC) | line |
|---|---|---|---|
| 39874068348 attempt 2 (`fix/r10-loop-cpu`) | 120155413953 | 2026-10-23 00:23 | FAIL gate lease priority ... `overlaps=1 order=['b', 'a']` |
| 39894127333 (`fix/r10-flow-toolkit-measure-pr`) | 120220882995 | 2026-10-23 03:29 | same line |
| 40081490403 (#2692, `fix/r10-replay-scoped`) | 120835946109 | 2026-10-24 09:45 | same line |

3 instances in a 2.4-day scanned window out of 21 red `fast` jobs (the other 18
are other causes; 0 of the 43 `ci-ratchet` reds show it). Local reports of "5
gate-lease and heartbeat wall-clock checks" under load were not reproducible from
logs; the `hb:` lines in CI logs are controls. Lower bound; unscanned runs may add.

## 4. Class reach

The class: a write a concurrent reader can see torn, where that reader treats an
unparseable file as garbage and deletes it. Rule that enumerates its seams, every
content writer in the module (test cases excluded):
`grep -nE "write_text\(|os\.open\(|\.touch\(|\.write\(" tests/gate_lock.py`.
Each seam it returns, with its disposition:

| writer | reader of a torn file | disposition |
|---|---|---|
| `Owner.create` (slot and single-lease create) | `_read_at`, `_free_slot` unlinks | closed here: staged file `os.link`ed in |
| `Owner.write` (renew, refresh, take) | `_read_at`, `_free_slot` unlinks | closed here: `_write_whole` (staged, `os.replace`) |
| `mark_unleased` (the unleased witness) | `_unleased` (`slots_status`) unlinks as unparseable | closed here: `_write_whole`; found by the fix review of round 1 |
| `_ticket_tmp` / `_enqueue` (tickets) | `_queue` | already atomic: private temp, then `os.link` / `os.replace` |
| `flock_context`'s `holding` marker | `.exists()` only, content never parsed | not in the class |
| `_ensure_lock_dir`'s `flock` touch, `flock_context`'s `os.open` | no content | not in the class |

`rg O_EXCL` outside this file: none, and no other file writes the lock
directory's files (`git grep` for `unleased-` and the lock path returns only
prose and `prepr.sh`'s call of the CLI). The single lease (`take`) reads a torn
owner as None, then `create` fails and it retries: safe, but spins; with both
owner writers whole it no longer sees one.

## 5. Cost test

- Defect cost: the failed `fast` job ran 25 min (attempt 1 of the 2026-10-24 job:
  09:20:10-09:45:09), 12 min (03:17:59-03:29:48) and 35 min (attempt 2,
  23:47:57-00:23:16); a rerun of that job is owed each time. Blocked opens:
  none measured (no PR was refused; each cost a rerun). Measured total: 72
  job-minutes of red over the window, plus the unmeasured rerun and the review-head
  wait. Not counted: the production exposure, a fifth heavy run admitted past the
  4-slot cap.
- P(recurrence): 3 in 2.4 days measured, so about 1.25 per day while the code stands.
- Countermeasure standing cost: the four new cases take about 2.2 s of a
  `gate_lock.py --accept` run (wall, local, three runs each: 9.2-9.6 s with
  them, 7.0-7.2 s with their four `cases` entries removed); zero ongoing
  maintenance. The production change is one shared writer and its three callers.
- Verdict: about 2 s per run against about 30 job-minutes times 1.25 per day: build.

## 6. Countermeasure (built in this branch, `tests/gate_lock.py`)

State (c) fix: deterministic or high-rate cases and the production repair.

- `Owner.create` writes a sibling temp file and `os.link`s it into place: the file
  appears at the path complete, and `link` fails if it exists, as `O_EXCL` did.
- `_write_whole` writes a sibling temp file and `os.replace`s it; `Owner.write`
  and `mark_unleased` both call it.
- Case `torn_create`: a rival takes inside `Owner._text`, i.e. while "a"'s create is
  in flight. Asserts exactly one winner.
- Case `torn_write`: a reader polls `_read_at` against 4000 rewrites; asserts it is
  never None.
- Case `torn_marker`: a reader polls `_unleased` against 4000 `mark_unleased`
  rewrites (1000: the reverted writer loses it thousands of times in that span); asserts the live marker is never missing.
- Case `pool_contents`: after a take, a same-label re-take and a marker, the pool
  directory holds exactly `flock`, `slot-000` and the marker: no staging file
  outlives its write.

Demonstrated on the defect and fixed (`PYTHONPATH=tests/hastub python3
tests/gate_lock.py --accept`); each mutant is one edit to the fixed tree, the
counts of torn or missing polls are thread-timing counts, reproducible in order
of magnitude only:

| tree | failing cases | total |
|---|---|---|
| fixed | none | `ALL 33 ... PASSED`, three runs |
| `Owner.create` reverted to `O_EXCL`-then-write (round 1) | `torn_create` `winners=['rival', 'a']` | 1 FAILED |
| `mark_unleased` back to `write_text` | `torn_marker` | 1 of 33 FAILED |
| `Owner.create`'s `finally: tmp.unlink` removed (M4) | `pool_contents`, a `.create-*-slot-000` left | 1 of 33 FAILED |
| `_write_whole` back to `path.write_text` | `torn_write`, `torn_marker` | 2 of 33 FAILED |

Null control: the fixed tree passes all 33 three times; the pre-existing
`one_winner` and the other cases are unchanged and pass (nothing loosened, no
timing parameter touched).

## 7. Not verified

- The original natural-timing race (`one_winner`) was not re-triggered under load
  before and after; the deterministic cases stand in for it.
- `tests/entities.py` cannot run in this seat (no `paho`); CI owns it.
- A crash between a staged write and its `link` or `replace` leaves a dot-file
  in the lock or pool directory; nothing globs it, and it is not cleaned.
  `pool_contents` pins the no-crash path only.
- `torn_write` and `torn_marker` are high-rate, not deterministic: they detect a
  reverted writer by thousands of missed polls per run, but a zero is a sample.
