# `beatd.py`

- `beatd.py` — the one supervised beat (R10-ORCH-BEATD arm (a)): `run
  --state S [--jobs FILE] [--once | --for N]` runs a job table, each job on
  its own thread and process group under `S/beatd/<job>.lock`, SIGTERM at its
  `timeout_s` and SIGKILL 10 s later unless the group has emptied, its leader
  gone or not, before the job lock drops; a `class: orch-checkout` job also holds
  `S/beatd/orch-checkout.lock`, waiting at most `class_wait_s` (default 60)
  before `outcome=busy`. Every start, heartbeat and pass is a line of
  `S/beatd/journal.log`. `status` prints one `JOB` line per job (`late` past
  `interval_s + timeout_s`, `idle` for a watch job with no instance) and the
  alarms `DOWN`, `ALERT lock-owner-dead`, `ALERT pulse-silent` (a `STOPPED`
  line of pulse.py's output in `S/beatd/pulse.txt`) and `STALE-CODE behind=`;
  rc 0, 1 alarm, 2 unreadable. `held` is `beatd.lock`'s one reader for other
  scripts: rc 0 held, 1 free. A job's env carries `HPO_BEATD_JOB`, the real git
  as `HPO_REAL_GIT`, `HPO_GIT_SHIM_LOG` and `beatd_shims` first on `PATH`.
  When: arm (b) lands the job table (`beatd.jobs.json`, absent until then)
  and the rows; until a supervisor unit is applied it runs under
  `daemonize.py` and records `supervisor=none`. Refusal (rc 2, `beatd:
  REFUSE`, zero jobs run): an unknown or missing key, a watch job under 60 s,
  an unreadable table; a first `git` on `PATH` that is absent, a shim, or does
  not answer `git version`. A second `run` exits 75, `ALREADY RUNNING`.
  `--self-test` drives cases (a)1-8 under `/bin/bash`, each with its null
  control, and plants each `MUTANTS` entry (at least one per case) in a temp
  copy, four at a time; a crashing mutant fails, it is never a kill.
