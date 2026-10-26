# R10-RCA-RATELIMIT-RECUR: the rate-limit red recurred after M0-M2

Root-cause seat for the recurrence of `API rate limit exceeded for installation`
on required checks, at 2026-10-26 04:52Z, after the countermeasure of
`dev/audit/rca/install-ratelimit.md` (M0, M1, M2; #2629, merged `97b4fddf2`)
had landed. It ran beside any fix, never as the fixer
(`dev/governance/roles/root-cause.md`). Measured at origin/main `b281d0325`.

**Defect.** One bucket-hour, 04:07:04Z to 05:07:04Z (`reset` 1792991224),
ran dry at 04:52:18Z and stayed dry for 14.8 min. In that interval every
required check that read the API failed:
`RATE-LIMITED reset_epoch=1792991224` (`gate`, `prelude`, `refresh` of
`tools/ci/`), `API rate limit exceeded for installation` (arch-score,
pr-contract), `GitHubRatelimitException` (validate-hacs), and env-matrix's
`the GitHub API is unreachable` arm. Five pull-request heads went red
(#2848, #2849, #2850, #2832, #2843), with main's push run at `b281d0325`
(record, validate-hacs, env-matrix), Nightly's record-autofix and merge-main at
`b281d0325`, and seven Gate sweep runs (04:52:43Z to 05:01:45Z). The logs of
those last three groups were not read; they ended `failure` inside the dry
interval. One recovery was measured: #2850's
gate went red at 04:53:57Z and its re-run went green at 05:10:55Z, 17.0 min later.

## 1. Cause

### 1.1 What M0 measured

M0 prints the bucket before and after the record job's window walk. These are
the readings of that hour, from the record job of each push to main
(`RATE_LIMIT before:` and `RATE_LIMIT after:`, governance.yml's two
`GITHUB_TOKEN rate limit` steps):

| UTC | push | reading | used |
|---|---|---|---|
| 04:23:52 | `21b45524d` (#2844) | before | 225 |
| 04:28:30 | | after | 1,718 |
| 04:28:49 | `0dfc063fa` (#2846) | before | 1,722 |
| 04:33:47 | | after | 2,667 |
| 04:41:37 | `bdf69a5c3` (#2838) | before | 2,968 |
| 04:47:32 | | after | 4,443 |
| 04:49:40 | `df478d40b` (#2847) | before | 4,478 |
| 04:52:18 | | after | 5,000 (`remaining` 0) |
| 05:05:29 | `b281d0325` (direct push) | before | 5,000 (`remaining` 0) |

**The bucket is 5,000 calls an hour.** That is the `limit` in every reading
of this hour, and in every reading section 4's scan found.

### 1.2 Who spent it

Two readers walk the release window `<last v* tag>..main` with
`GITHUB_TOKEN` on every push to main. The earlier record names one of them.

- **Governance `record`** (the earlier record's consumer). After M1 it costs
  `W + 3P` per run: `record_api_calls.sh v7.0.4` at each push prints
  731, 735, 739 and 743 calls.
- **Nightly `record-autofix`, step "Enumerate the window's merges"**
  (`nightly.yml`, `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`). It runs
  `record_row.py --enumerate`, which made two reads per merge,
  `/commits/<sha>/pulls` and then `/pulls/<n>`. That is 364, 366, 368 and 370
  calls at the four pushes (`enumerate_api_calls.py v7.0.4` at each push,
  over 182 to 185 merges). It has no concurrency group: Nightly's group is
  the run id. Step times were 04:23:29–04:26:19, 04:24:10–04:26:47,
  04:40:47–04:43:37 and 04:44:45–04:47:10.

The ledger is each reading interval's delta, less each reader's calls inside
it. Where an enumerate step crosses a reading, its calls are split in
proportion to time, which assumes a steady read rate (each step took 145–170 s
for 364–370 reads).

| interval | delta | record | enumerate | rest | rest per min |
|---|---|---|---|---|---|
| 04:07:04–04:23:52 | 225 | 0 | 49 | 176 | 10.5 |
| 04:23:52–04:28:30 | 1,493 | 731 | 315 + 366 | 81 | 17.5 |
| 04:28:30–04:28:49 | 4 | 0 | 0 | 4 | — |
| 04:28:49–04:33:47 | 945 | 735 | 0 | 210 | 42.3 |
| 04:33:47–04:41:37 | 301 | 0 | 108 | 193 | 24.6 |
| 04:41:37–04:47:32 | 1,475 | 739 | 260 + 370 | 106 | 17.9 |
| 04:47:32–04:49:40 | 35 | 0 | 0 | 35 | 16.4 |
| **to 04:49:40** | **4,478** | **2,205 (49.2 %)** | **1,468 (32.8 %)** | **805 (18.0 %)** | **18.9** |

At 04:49:40Z the fourth record run started with 522 calls left and needed 743.
The bucket ran out at 04:52:18Z, and its `--stats` read was the first 403.
"Rest" is every other reader together: pull-request CI (pr-contract,
arch-score, `prelude`/`gate`/`refresh` polls), Gate sweeps, merge-main and
env-matrix. M0's lines cannot split it further, and it does not need splitting.
Over the 42.6 min to 04:49:40 it took 18.9 calls a minute, about 1,130 an hour.
Its one high interval, 42.3 a minute in 04:28:49–04:33:47, holds the CI starts
of #2849 and #2850 (04:29:45, 04:31:28, 04:33:10).

**The two O(window) readers spent 82.0 % of the bucket that ran dry.**
The hour held five pushes to main. Its demand without the limit was about
6,660 calls: record 3,691 (five runs), enumerate 1,838 (five runs) and the
rest at 18.9 a minute for 60 min. That is 133 % of 5,000.

### 1.3 What the merged countermeasures bounded

- **M1** works as built. The harness counts `W + 3P` per run, and the
  readings agree: the 04:28:49–04:33:47 run, with no enumerate beside it,
  read 945 in all for its 735-call walk.
- **M2** bounded nothing in this hour. No push arrived while one run was
  going and another was already pending, so all four runs ran. The group keeps
  one going and one pending and only drops a superseded pending run. Pushes
  that are minutes apart pass through it unchanged.
- **The enumerate** was outside both. It never had a window cache or a
  concurrency group, because the earlier record did not count it.

### 1.4 Why it recurs: per-push demand grows with the window

No stamp has been made since `v7.0.4` (2026-10-22 13:48Z). By `b281d0325` the
window held 189 first-parent commits and 185 merges, against 91 when the earlier
record measured it. Each merge adds about six calls to every later push
(record `W + 3P`, enumerate `2M`). The per-push budget left after the rest is
(5,000 − 1,130) / pushes per hour. At five pushes an hour that is 774 calls,
which the two readers exceed once the window holds about 129 merges. This is the
earlier record's own warning ("a slow release still grows it"), now measured.

The bucket has run dry at least once before in this release cycle. Section 4's scan
found the 02:07:01Z–03:07:01Z hour dry at 03:06:48Z: the
`b709a4c50` record run read `used` 3,815 at 03:03:19 and 5,000 at 03:06:49.
That run's own `--stats` and `--sunset` read 403 (`pulls/2751`, `pulls/2845`).
The reset came 13 s later. Whether a required check read in those 13 s was not
measured.

## 2. Process state: (c)

**The process.** `install-ratelimit.md` section 3, "How far the class reaches",
searched "every `GITHUB_TOKEN` reader whose call count scales with something
other than one PR head" and concluded "No other O(window) reader found".
Section 1.1 set Nightly aside as an App-token workflow: "App installation tokens
are minted only in `nightly.yml` (ledger-, record- and approver-writer) ...
separate buckets". The countermeasure was sized from that search: M1 and M2
act on `governance.yml`'s record job alone. O-1's measure of "the demand after
M1+M2" is `record_burst_replay.py`, which replays the record job alone (its
docstring), and the record's harness `record_api_calls.sh` counts that job
"before policy-docs, env-matrix and the other jobs".

**It was present and followed.** Section 3 exists and lists five readers. M0,
M1 and M2 landed as written (#2629). M1's count is exact (section 1.3).

**It did not produce the intended result.** At the earlier record's own
measured head `04c1dd779`, `nightly.yml` record-autofix's step "Enumerate the
window's merges" already read with `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`
(`git show 04c1dd779:.github/workflows/nightly.yml`, the step at line 572). It
had done so since `72a4d77bb` (2026-10-04, then in `tests.yml`). The search
classified each job by the token it mints. The record-autofix job mints the
record-writer App token for its writes, and its comment says so: "every write
... rides the App installation token minted below, never GITHUB_TOKEN". Its
reads use the workflow token, one step earlier. So the search's unit was the
job's minted credential, not each step's `env`, and it missed the reader that
spent 32.8 % of the bucket that ran dry.

Not (a): a diagnosis, a class search and a countermeasure existed. Not (b):
each was carried out as written. Not (d): the window's growth, the one
precondition that changed, was predicted in the earlier record (section 1.4),
and a change the process predicted did not happen underneath it. The
countermeasure therefore changes the unit: it counts reads per step on the
bucket that went dry, both readers in the same instrument, and it bounds the
reader that was missed.

## 3. How far the class reaches

Rule: `grep -nE -- "--since|describe --tags" .github/workflows/*.yml` lists
every workflow step that derives the release window. At `b281d0325` it returns
exactly two steps that read with `GITHUB_TOKEN`:

- `governance.yml` `record`, which reads `W + 3P` per push. M1 and M2 bound it.
  The rest is O-1's (section 4).
- `nightly.yml` `record-autofix` "Enumerate the window's merges", which read
  `2M` per push. This record's countermeasure M4 halves it.

Programs that take the window themselves, from `git describe` in the code
rather than the workflow: `git grep -l -E "describe.*--tags|--match.*v\*"
b281d0325 -- '*.py' '*.mjs' '*.sh'` returns 7 files. Each is dispositioned by
whether CI runs it as a window-walking `GITHUB_TOKEN` reader:

- `dev/audit/harnesses/record_api_calls.sh`: an offline harness; no workflow
  runs it.
- `tests/entities.py`: pins the workflows' text; its `gh` strings are pinned
  text or a test stub, not a read.
- `tests/delivery_status.py`: walks the window in git only. Its `_gh` helper
  has no caller. The `delivery-status` job around it reads #201's body once
  and edits it at most once (governance.yml, step "Regenerate the ledger and
  put it in #201's region"): two calls, not a function of the window.
- `tools/policy/agreement_py.py`: its one `gh api` string is the self-test's
  stub dispatch; CI runs it as `--self-test` and `--restore`.
- `tools/policy/record-predicate/sweep.mjs`: does read the API (`gh api` in
  its fetch helper). CI runs it only as `--self-test` (governance.yml, the
  step that names `sweep.mjs --self-test`), which made 0 `gh` calls under a
  logging stub (fix review of #2852).
- `dev/audit/rounds/round3/D11/conformance.py` (a `gh api graphql` read) and
  `dev/audit/rounds/round7-fix/governance/report_step_driver.py`: round
  harnesses; no workflow names either.

None is a window-walking reader in CI.

Other per-push `GITHUB_TOKEN` readers scale with something smaller:

- `merge_main_bot.py` makes 1 listing plus 1–6 `mergeable` reads per open pull
  request (11 open at this writing).
- `ci-ratchet` reads a fixed listing.
- `delivery-status` reads and edits #201 once each.

All of these are inside the measured rest.

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, per release
cycle, in wall-clock.

- **P(recurrence), measured.** `scan` is every `governance / record` log of
  every push run of `ci.yml` on main from 2026-10-23T23:53Z to 2026-10-26T05:04Z.
  It found 43 bucket-hours with an M0 reading. Two of them ran dry, 10-26 02:07Z
  and 10-26 04:07Z. Eight more reached ≥ 4,000 by their last reading:
  10-24 18:03Z, 20:03Z and 21:04Z, 10-25 05:04Z, 06:04Z, 13:05Z and 14:05Z,
  and 22:06Z. That last reading is a lower bound on the hour's peak. Hours
  with no push to main have no reading and are not counted. The two dry hours
  are two of the three bucket-hours from 02:07Z to 05:07Z on 10-26, the
  scan's last. The window only grows until a stamp, so the rate does not fall
  on its own. Earlier
  instances of the class: 2026-10-14 (HANDOVER item 44), 2026-10-19
  (R10-FOLLOWER-DEBOUNCE), and 2026-10-22 06:27Z, 08:40Z and 09:44Z
  (`install-ratelimit.md`).
- **cost(defect), per dry hour.** At least five PR heads × 17.0 min (the one
  measured recovery) = 85 min of merge-train wall-clock, plus main's push
  verdict at `b281d0325` and the seat time of a red that is not the head's.
- **cost(countermeasure, recurring).** Below, per option.

### M4 (built here): the enumerate reads once per merge

`/commits/<sha>/pulls` already returns the pull request with the
`number`, `title`, `state`, `head.ref` and `merge_commit_sha` the row needs.
The enumerate needs that object to match the merge, so the second read,
`/pulls/<n>`, returned the same fields. Checked on one live pair: both reads for
`df478d40b` returned `#2847`, the same title, `closed`, `record/autofix` and the
same merge SHA. `enumerate_merges` now takes the matched object.

- Per push: 370 → 185 calls at `b281d0325` (`enumerate_api_calls.py v7.0.4`
  with the base and the fixed `record_row.py`). For the 04Z hour that is
  −919 calls.
- Standing cost: negative, 72–87 s less runner time per push to main
  (185 reads at 0.39–0.47 s a read, from the four step times above).
- Test, written first: record_row's self-test "enumerate_merges reads one map
  per merge and nothing else" failed at the base and passes at the fix.
  Mutating the fix back to the second read fails it again. Null control: a
  window of direct pushes reads nothing.
- **Verdict: passes.** Negative standing cost, and positive expected saving.

**M4 alone does not stop the recurrence.** With it, the 04Z hour's demand would
have been about 5,740, still 115 % of the bucket.

### M3 = decision O-1: its condition is now met

O-1 (orchestrator, mandate 6329234399) moves `--stats` and `--sunset` off the
push arm to the weekly schedule and the stamp, with an App installation token as
the fallback. Its condition was "only if the measured demand after M1+M2 still
exceeds the measured limit". Measured: 6,660 against 5,000 in the 04Z hour.

- On the push arm the record job then reads `W` alone (`--record`, 185–189
  calls), so −555 a push.
- For the 04Z hour: about 3,910 without M4 (78 % of the bucket), and about 2,990
  with it (60 %).
- The window a burst of five pushes can carry grows from about 129 merges to
  about 387 (2 calls per merge per push, against 6).
- Standing cost: negative, about −4 min of runner time per push (555 reads at
  about 0.42 s).
- The cost not in calls: the friction histograms, the friction filer, which
  reads their output, and the sunset report run weekly and at the stamp instead
  of on every push. `install-ratelimit.md` names that cadence as #959 option B,
  the owner's call.
- **Verdict: passes.** Standing cost is negative against at least 85 min per dry
  hour, at two dry hours in this cycle's last three bucket-hours. **Not built
  here.** It is
  the record job's workflow, and its cadence is the owner's. The dispatch
  carries it (section 5).

**The load is not irreducible.** Readers other than the two window walks spent
about 1,130 calls an hour, 23 % of the bucket. The two walks were 83 % of the
dry hour's demand (5,529 of about 6,660), re-reading merged pull requests,
which no longer change. P192 arm (b) stays closed.

### Refused: a static census of window-walking `GITHUB_TOKEN` steps

A census would pin, for example in `tests/entities.py`, the set that section
3's rule returns, so that a third reader is declared at review. It is refused.
This record found the missed reader from M0's two log lines and step times
alone, in one bucket-hour, with the residual accounting of section 1.2.
`enumerate_api_calls.py` now counts the second reader beside
`record_api_calls.sh`. In seven weeks the class has two readers (09-09 and 10-04).
A census adds a ratchet-counted check and a `field_coverage.mjs` registration
for each workflow edit, and its one catch is a reader that M0's lines already
expose within an hour of a burst. The cost test asks for a recurring cost below
85 min × P(a third reader). No P is measured beyond 2 readers in 7 weeks, so
the census is not built.

## 5. Owner and carries

- **M4** is this pull request (`tools/audit/seat/record_row.py`, and its
  harness `dev/audit/harnesses/enumerate_api_calls.py`).
- **O-1** goes to the orchestrator: its condition holds, measured. The
  dispatch carries these points:
  - Demand is `record + enumerate + rest`.
  - `record_burst_replay.py` replays the record job alone, so it underreads
    by the enumerate's share. Take the two harnesses together, with the rest
    from the M0 lines.
  - The friction-cadence change is put to the owner unless the mandate covers
    it.
  - A second M0 pair around Nightly's enumerate step would print its spend
    directly instead of by inference: two `gh api rate_limit` reads, which are
    not counted against the limit.
- **The stamp** resets `W`. With neither M4 nor O-1, a stamp is the only thing
  that lowers per-push demand. That cadence is the orchestrator's (`web-stamp`).
