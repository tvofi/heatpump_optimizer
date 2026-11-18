# RCA: `nightly-ha (stable)` reddens on a py-spy timeout inside `hb:positive_control`

The root-cause seat for the recurring `nightly-ha (stable)` red. It ran beside any
fix, never as the fixer (`dev/governance/roles/root-cause.md`). It names three
instances: #2379 (job 117649075688) and #2411 (jobs 117704407933 and
117738343906). The class search below counts **8 since 2026-10-08**, and none of
them was on the 3.13 floor.

**Defect.** Each instance fails the same two of 64 checks,
`['hb:positive_control', 'run:exit_status']`. The second is only the container's
exit code after the first. Each failed log carries the same line, from the
heartbeat watcher's `LoopHeartbeat.dump`:

```
py-spy did not run: TimeoutExpired: Command '['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid', '1']' timed out after 30 seconds
FAIL hb:positive_control  [a 600 ms spin read as 600.3 ms; dump names the spin: True; py-spy rc=0 names it: False]
```

The heartbeat itself works on every instance. The 600 ms spin is measured at
600.2 to 600.3 ms, and the in-process Python stack names `_hb_spin`. The only
thing missing is py-spy's own section.

## 1. Cause

**The check's verdict rests on one sample from an external sampler racing a live
process.** `check_hb_positive_control` (`tests/nightly_ha.py`) passes only when a
dump contains `py-spy rc=0:` followed by `_hb_spin`. `LoopHeartbeat.dump` makes
exactly one `py-spy dump --nonblocking` call per stall, with `timeout=30`. The
spin lasts `HB_CONTROL_S` = 0.6 s, so no later call could name it anyway. Both the
requirement and `--nonblocking` came in one commit, `ab45a5f7c` (#1870 review
round 1, 2026-10-03). Its commit message says the rc=0 section "pins the
SYS_PTRACE cap and the staging (both survived as mutants)".

`--nonblocking` reads the target's memory without stopping it. Against CPython
3.14.6 in the `stable` image, py-spy 0.4.2 sometimes does not return within
30 s. That non-return is the whole defect: one miss in a run reddens the lane.

**Which side moved.** Neither did. The `stable` image ran Python 3.14 from the
check's first real measurement. Tests run 37083412666, stable job 111088617669
(2026-10-03, digest `3e6710a7`), already runs `python3.14/asyncio`. py-spy has
been pinned at 0.4.2 since #1870. The check was racy from its first day. It first
showed red on 2026-10-09 because, at a 6.7% rate, the first ~10 runs are green
with probability about 0.5.

**Reproduced.** I used the exact failing image, `ghcr.io/home-assistant/home-assistant:stable`
with digest `sha256:33afb0659d78…`, the same digest as the five instances from
10-16 to 10-18. A local layer added only the `threadpoolctl` wheel, because the
container has no network and could not pip-install it. Runs used the hash-pinned
py-spy 0.4.2 wheel.

- **The lane's own heartbeat container.** I staged it with `_stage(…, two_zone_dhw=True)`,
  launched it with `docker_command(…, ["--heartbeat-only"], ("SYS_PTRACE",))` and
  ran it 60 times on a 4-CPU host: **1 of 60 reproduced the defect exactly**
  (run 15, `FAIL hb:positive_control [a 600 ms spin read as 600.5 ms; dump names the
  spin: True; py-spy rc=0 names it: False]` with the same `TimeoutExpired … 30
  seconds` line). The other 59 were `ok`, with py-spy at `rc=0` naming the spin.
  During the hang a host-side sampler read py-spy's `/proc/<pid>/stat` every second.
  It stayed in state `R` throughout, at 28.7 s of CPU in 29 s of wall time (utime
  7.49 s, stime 21.24 s, `CLK_TCK` 100). So py-spy is not blocked on anything: it
  is busy in a long loop of remote-memory reads, which is the 74% kernel time.
- **A synthetic self-dump in the same image.** A 0.6 s spin was dumped by a
  watcher thread 0.25 s in, with 8 to 32 busy threads or thread create/exit churn:
  710 dumps, 0 timeouts, at most 0.15 s each. **18 returned rc=1**
  (`Failed to call get_stack_trace … Failed to copy PyCodeObject … Bad address`),
  which is a torn read of a frame being popped. With `RUST_LOG=info`, 2 of 200
  logged `Interpreter address from symbol is invalid` and fell back to the BSS
  scan. That fallback costs nothing in a small process. The same harness on host
  glibc CPython 3.14.7: 105 dumps, 0 failures.

So the race is real and measured in the image. **The mechanism of the 30-s
non-return inside py-spy is not established.** py-spy 0.4.2's walks are bounded,
at 4096 threads and 4096 frames each (`stack_trace.rs:104,218`;
`python_spy.rs:342`). Its address-validation fallback re-walks every candidate's
threads (`python_process_info.rs:553`). Either bound, reached over a torn
pointer cycle, is consistent with a 30-s, CPU-bound, read-dominated run: 4096 × 4096
frame reads at several syscalls each. No backtrace was captured to say which: the
one local hang came before a sampler attached gdb. The local rate (1 of 60) is
below CI's (8 of 120). At CI's rate, 1 or fewer in 60 has P ≈ 0.08, so the
local host may race less often, but the sample does not separate them. The CI log
cannot say more, because on a timeout `dump` keeps no py-spy stderr. That is an
upstream question with the py-spy maintainers. It does not change the
countermeasure: a verdict that needs one racy sample to succeed is wrong whatever
the race's mechanism.

**What else the cause reaches.** The same single sample has a second red route,
rc=1 on a torn read. It was measured at 2.5% in the synthetic and seen 0 times in
120 CI stable runs: during the spin the loop holds the GIL, so HA's other threads
barely move their frames. Every other `hb:` arm dumps only on a real stall, and
those arms read `0 dump(s)` on all 8 instances. So py-spy runs once per green
heartbeat boot, and this check is its only verdict.

## 2. Process state: (c), followed and did not produce the intended result

The process for a new check was followed: a failing test first, twelve mutants
each killed by its own check (M8, no `--cap-add`, and M12, py-spy not staged,
among them), a null control, an adversarial review in two rounds, and a real-HA
dispatch. The #1870 body records each one.

It did not produce the intended result for one reason. **The pin was validated on
a single real-HA run.** #1870's body: "Real Home Assistant, Tests run 37083412666
at this head: `ALL 62 checks PASSED` on both images … py-spy (`--nonblocking`)
returns rc 0 naming `_hb_spin`". One green run is what a 6.7% false-red check
produces 93% of the time. The mutation proof shows the check fails when the wiring
is removed. Nothing in the process asks how often it fails when the wiring is
present. The repository has no rule on a check's false-red rate: `flake` and
`flaky` appear nowhere under `dev/governance/`, `.claude/` or `CLAUDE.md`.

**A cheaper detector existed, on one condition.** The heartbeat container alone takes
about 70 s per run on a host with Docker, against about 3 min for the CI lane, and it
reproduces the defect (section 1). The #1870 seat had no Docker daemon. Its body says
so: "the four `hb:` checks have never run inside Home Assistant". So its only
detector was CI, one run at a time.

Not (b): nothing that existed was skipped. Not (d): Python 3.14 was under the
check from its first measurement (section 1).

**Why recurrence went unseen until the eighth instance.** Each red-check answer
was written inside one pull request. Both read it as an isolated runner event. #2379:
"a slow runner is the likely reason" (not measured; the failed jobs ran 3.2 to
3.7 min against 2.8 to 3.0 green, which is the 30-s timeout plus the container's
error exit). #2411: "one timeout is not yet a recurrence". By then the class stood
at 6. A seat sees its own PR's runs. The only cross-run grader, `nightly-status`,
reads the newest `main` run alone, and **none of the 8 instances was on `main`**:
all 8 are `workflow_dispatch` runs of PR branches.

## 3. Class search

`GET /repos/…/actions/workflows/tests.yml/runs`: the 400 most recent runs
(2026-10-16 to 2026-10-18), plus the 40 latest `schedule` and 100 latest
`workflow_dispatch` runs, which reach back to 2026-09-09. Then every
`nightly-ha (…)` job in those runs, 300 jobs, and the log of every failed one
since 2026-10-08.

| window 2026-10-08 → 2026-10-18 | jobs | failed | py-spy timeout | other cause |
|---|---|---|---|---|
| `nightly-ha (stable)`, Python 3.14.6 | 120 | 15 | **8** | 7: `a16:debug_inline`/`a16:debug_capped` on 10-08 (both arms, a separate cause), 1 with no check output (10-09, both arms) |
| `nightly-ha (2025.2.0)`, Python 3.13.1 | 120 | 7 | **0** | 7, the same A16 and no-output pairs |

The 8 py-spy instances, each with `hb:positive_control` + `run:exit_status` and
`py-spy did not run: TimeoutExpired` twice in the log: 113611720490 (10-09),
113738022964 (10-09), 114253986438 (10-10), 117221134956 (10-16), 117649075688
(#2379, 10-18), 117704407933 (#2411, 10-18), 117731309720 (10-18) and 117738343906
(#2411, 10-18), on 7 branches. They span three `stable` digests (`1b64d38f`: 3; `130241f2`: 0;
`33afb065`: 5) and one runner image (`20261012.601` on all those read). By event:
`schedule` 0 of 11 (its one red, 10-08, is the A16 pair), `workflow_dispatch` 8 of
101, `pull_request` 0 of 8. Green
`stable` runs on the same digest and runner read `Python v3.14.6`, `py-spy rc=0`,
naming the spin. Same image, same runner, both outcomes: it is a race, not an
environment change.

Rate: **8 / 120 = 6.7% of `stable` runs; 0 / 120 on the floor.** Per release cycle:
3 in v6.7.17 → v7.0.0 (10-08 to 10-14) and 5 so far in the open cycle (10-14 to
10-18).

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, in wall-clock per
release cycle (about 6 days, v6.7.17 → v7.0.0).

- **P(recurrence), measured:** 6.7% of `stable` runs at about 11 runs a day (120 in 10.5 days), so
  **3 to 5 instances per cycle** (section 3).
- **cost(defect) per instance:** a re-dispatch of the lane (3.0 to 3.7 runner-min),
  plus a red-check answer and log reading by the PR's seat, plus the fix
  reviewer's read of it. Estimated 20 to 30 seat-min; the two answers above run to
  a paragraph each with log quotes. None has yet reached `main`. Over a
  cycle's ~6 schedules it will in about one cycle in three (1 − 0.933^6 = 0.34),
  and then
  `nightly-status` holds red for the orchestrator. Per cycle: **about 1 to 2.5
  seat-hours**, plus this seat once.

**Countermeasure A: the root cause, a fixer's change, not built here.** The
positive control's py-spy leg should tolerate one bad sample and still pin the
wiring. The spin is held until the dump has returned, under a bound, and py-spy
is retried with a short per-attempt timeout until one rc=0 names `_hb_spin`.

- Standing cost on a healthy run: py-spy returned in **≤ 0.15 s on all 710
  in-image samples**, and on 59 of 60 lane runs. So the spin grows by
  about 0.15 s once per heartbeat boot: **≈ 2 s a day across ~11 runs**.
- Cost on a bad sample: one per-attempt timeout instead of the current 30 s.
- The wiring pins survive. No cap gives rc≠0 on every attempt, and no staged
  binary gives no py-spy section. Both still fail.
- #2379's objection, "up to a further 30 s on every run", prices a retry as paid
  on every run. It is paid only on a failed attempt.
- **Verdict: built, by a fixer.** About 2 s a day against 1 to 2.5 seat-hours per
  cycle.

**Countermeasure B: a rule (refused).** The rule would be: a check whose verdict
reads one sample of a racing process carries a measured false-red rate before it
merges.

- Seeing a 6.7% rate with 95% power takes 45 runs (1 − 0.933^45 = 0.955). That is
  45 × 3 min = **2.25 runner-hours per such check** in CI, or about 45 × 70 s =
  **53 min** on a host with Docker: the heartbeat container alone, as reproduced
  here.
- P measured: **1** such check in the nightly-ha lane's history. A15's py-spy leg
  is the lane's only verdict on an external sampler of a live process. The other
  arms read HA's own state or logs.
- The rule's cost lands on every such check; the defect's cost lands on the
  flaky fraction of them, and that fraction rests on a sample of 1.
- **Refused**, and recorded here. The rule would also be policy, which is the
  owner's call. Countermeasure A removes this instance's cost.

**Countermeasure C: a cross-run count before "not a recurrence" (proposed; policy;
not landed).** Before a red check is answered as not this PR's, count that check's
failures across the lane's runs over the last 7 days.

- The jobs API answers it: one list call per run plus one log fetch per failed
  job. It is a few minutes per answer, and a seat already reading the log can run
  it.
- Benefit, measured from this class: the RCA would have opened at the third
  instance (10-10) instead of the eighth. Five reds at 20 to 30 seat-min each is
  about **2 hours saved**, against 3 to 5 nightly-ha red-check answers per cycle (the
  measured rate) × 3 min = **9 to 15 min per cycle**.
- It addresses section 2's second finding: the seat could not see the class.
- It changes how a red-check answer is written (`defect-root-cause.md`'s
  Enforcement, or `steward` S8), so it is **for tvofi**. It is drafted here, not
  landed.

## 5. Carry for the fixer (countermeasure A)

- **Where.** `tests/nightly_ha.py`: `LoopHeartbeat.dump`, `_hb_spin` and its
  caller in the positive control (`call_soon(_hb_spin, HB_CONTROL_S)`, then
  `asyncio.sleep(HB_CONTROL_S + 0.2)`), and `check_hb_positive_control`.
- **Pins to update.** `tests/entities.py` pins `"--nonblocking"` in `dump`'s source
  and `check_hb_positive_control`'s arms through `_HB_BOTH` and `_hb_ctl`.
- **The arms a fix keeps red.**
  - `py-spy rc=1: Permission denied` (no cap) fails every attempt.
  - A missing binary leaves no py-spy section.
  - An idle `rc=0` section, without `_hb_spin`, still fails.
- **Add.**
  - A first attempt that times out, followed by a second rc=0 naming the spin,
    passes.
  - Every attempt timing out fails.
- **Demonstration owed (`defect-root-cause.md`).**
  - Stage a py-spy wrapper that hangs on its first call in the heartbeat
    container. Expected: red at the base, green at the fix.
  - Real py-spy at the fix: green over repeated runs.
- **Out of the fix's scope.** Why py-spy 0.4.2 stalls against CPython 3.14.6. That
  is py-spy's owner (benfred/py-spy), with this reproduction.

## Reproduce

```
# class search: every nightly-ha job of tests.yml, with the failed ones' logs
GET /repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?per_page=100&page=1..4
GET /repos/tvofi/heatpump_optimizer/actions/runs/<run>/jobs?filter=all
GET /repos/tvofi/heatpump_optimizer/actions/jobs/<job>/logs      # grep 'py-spy did not run'

# the lane's heartbeat container, N times, on the failing digest
docker pull ghcr.io/home-assistant/home-assistant:stable          # sha256:33afb0659d78…
# + a layer with the threadpoolctl wheel (the container has no network)
python3 -c 'import nightly_ha as n; c, d = n._stage(T, two_zone_dhw=True);
  subprocess.run(n.docker_command(IMG, c, d, 240.0, ["--heartbeat-only"], ("SYS_PTRACE",)))'
# with py-spy 0.4.2 (tests/requirements-nightly-ha.txt) on PATH
```
