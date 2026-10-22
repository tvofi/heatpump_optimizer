Builds countermeasure A of `dev/audit/rca/nightly-ha-pyspy-timeout.md` (#2479) in `tests/nightly_ha.py`. **It does not remove the red, and the real-HA measurement says why: the hang is per process, not per sample.** It lands what is sound and holds the rest for the orchestrator's call (see **Disclosed: what this cannot fix**).

Delivery-status: group R10-NIGHTLY-PYSPY-RETRY.

What changes:

- `py-spy dump --nonblocking` is cut at `PY_SPY_TIMEOUT_S` = 5 s instead of 30 s. The RCA measured a healthy sample at ≤ 0.15 s on 710 of 710 in-image samples, so 5 s is more than 30× that.
- `hb:positive_control` now runs `_async_hb_control`. It makes up to `HB_CONTROL_TRIES` = 3 **fresh** spins with `HB_CONTROL_REST_S` = 1 s of loop time between them. Each spin is sampled once and held until that sample returns (`_hb_spin(..., hold)`, bounded by `HB_CONTROL_HOLD_S` = 6.25 s). It stops at the first try where the gap, the in-process stack and py-spy's rc=0 section all name `_hb_spin`. `check_hb_positive_control` takes the list of tries and passes only when one try reads all three.
- Worst-case wait, stated as the brief asks:
  - Every try hung: HB_CONTROL_TRIES × (HB_CONTROL_HOLD_S + HB_CONTROL_REST_S) ≈ 22 s, against the base's 30 s for one sample.
  - Any other stall's dump: 3 × 5 s at most (`HB_MAX_DUMPS`), against 3 × 30 s.
  - Every bound is under `HB_HANG_S` = 60 s, which `entities.py` pins.
- I first built the RCA's literal design: hold one spin and retry py-spy up to 3 times inside it. A real-HA run hung on **3 of 3** attempts inside one held spin (Figures F6), so I replaced it with the try-level retry above. Alternatives considered:
  - Retry inside one held spin: measured to hang on every attempt.
  - Retry without the hold: a retried sample would read the idle loop and could never name the spin.
  - The two that lost on cost: blocking-mode fallback and a raised timeout (below).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
https://claude.ai/code/session_0136kzeMuhF6B5YsJxT84c7L

## Disclosed: what this cannot fix

- In 140 real-py-spy heartbeat runs at the two retrying heads (F6 + F7 + F9), **3 hang episodes** occurred. **Every one hung on every retry the code made**:
  - in-spin retries: 3 of 3 hung (F6);
  - fresh-spin retries 1 s apart: 3 of 3 hung (F7);
  - the experimental blocking fallback (F9) answered, only after stopping the process.
- If samples hung independently at the RCA's ≈ 7 %, two further hangs would have P ≈ 0.07² ≈ 0.005 per episode. Seeing it twice of two is evidence that whatever slows py-spy is fixed for the life of the process. A retry inside the same HA process cannot rescue it. So this PR **does not lower the ≈ 7 % false-red rate on `stable`**; it lowers what each red costs, from 30 s to ≈ 22 s.
- F9 is an experiment, not in this diff. After a non-blocking timeout, the next try ran py-spy **without** `--nonblocking`. It answered rc=0 naming the spin, but the process sat stopped under ptrace for 38.5 s. The watcher thread was frozen too, so the 5 s timeout could not fire. So on an affected process py-spy's walk appears **slow, not endless**: 30 to 40 s, consistent with the RCA's 28.7 s of CPU in 29 s. That walk is too long to hold HA's loop for: it is near `HB_HANG_S`, and the RCA's reason for `--nonblocking` stands.
- A pass on one nightly proves nothing about a 7 % race, and neither do these runs:
  - 59/60 at the final head against 20/20 at the base does not separate the rates. At 7 %, 0 of 20 has P ≈ 0.23.
  - The local hang rate (3 in 140, ≈ 2 %) sits below CI's 6.7 %, as the RCA also saw (1 of 60).
  - What the runs do establish is the correlation, which is a property of each episode rather than of the rate.
- Countermeasures that would remove the red. Each needs a design decision this fixer seat may not make, so they are carried, not built:
  - (a) Count a py-spy **timeout** as inconclusive rather than red. The wiring pins the RCA cares about still fail: no `SYS_PTRACE` gives rc=1 `Permission denied` fast, and an unstaged binary gives no py-spy section. A timeout can only come from a staged binary that ran. This changes what the check asserts, so it belongs to the owner and the designer.
  - (b) Re-run the whole heartbeat container on a py-spy timeout, since the defect is per process. That reaches into `_run_outside`, wider than this brief allows.
  - (c) Raise the non-blocking timeout past the slow walk (for example 60 s), with the spin held for it. That blocks HA's loop for as long, and it was refused for that reason.

## Root cause

`dev/audit/rca/nightly-ha-pyspy-timeout.md`, #2479. This builds that RCA's countermeasure A, and this body changes one of its premises. "A first attempt that times out, followed by a second rc=0 naming the spin" describes the behaviour of the stub. On real HA, measured here, the second attempt hung too. That finding goes forward in Forward-carry below.

## Head

`6712698aeaf98cca27402f7ab96fef3dd95415b1`, a merge of `origin/main` at `04c1dd77990b97ae144e48cd29655853783532f2` (tip read 2026-10-22T09:43:32Z). The last two merges (from `8a4c438e7d9a`) brought only `dev/programme/delivery/*.md` rows and `dev/programme/rosters/wave-r10-groups.json`. After the first of them, at `357458427570f9d12d740dac8cfcad7db4f3c8a4`, `tests/entities.py` (`ALL 2394 ENTITY CHECKS PASSED`) and `tests/structure.py` were re-run. After both, F1's scope reads the same `MODE: SCOPED -- 4 script(s) run`, and `tools/pr/ci_predict.py --base origin/main` predicts no red. Base for the before-runs: `b787c7d45951243a05b6522437b60a01288f0dfd`.

The container runs F5 to F8 read `tests/nightly_ha.py` blob `91164340df3127e15459a3a0cf7da6a9d73afc24`, which is this head's blob (`git rev-parse HEAD:tests/nightly_ha.py`). The base blob is `30f8263e443ff304b87160b8e8527255fb9de1c9`. Image: `homeassistant/home-assistant@sha256:33afb0659d786213264c2211f8d91c5fe87461c56eba6a3a546eb05fc71e89f4`, the digest of the RCA's five 10-16..10-18 instances, plus a layer holding the `threadpoolctl` 3.6.0 wheel because the container has no network (as in the RCA).

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` at the head prints `SUMMARY killed=10 survived=0 null=ok`. Each mutant is one substitution in `tests/nightly_ha.py`, run against the A15 py-spy block of `tests/entities.py`:

| mutant | result | killed by |
|---|---|---|
| M1 retry reduced to one try (`range(tries)` → `range(1)`) — brief's first | KILLED | "survives one hung py-spy sample…", "…is retried, not accepted", "null control…" |
| M2 per-sample timeout removed (`timeout=30`) — brief's second | KILLED | "survives one hung py-spy sample… the hang cut at the sample's timeout…" |
| M3 a try accepted on any non-empty dump instead of naming the spin — brief's third | KILLED | "survives one hung…", "…is retried, not accepted", "null control…" |
| M4 spin not held past 0.6 s | KILLED | "survives one hung… the spin held across it" |
| M5 `dumped` never set (spin held to the bound) | KILLED | "survives one hung…" (gap < `HB_CONTROL_HOLD_S`) |
| M6 the check accepts rc=0 without the spin | KILLED | "passes at the spin…", "…is retried…", "null control…" |
| M7 the control passes no hold to `_hb_spin` | KILLED | "survives one hung…" |
| M8 the check accepts the three readings split across tries | KILLED | "passes on any one try that reads all three…" |
| M9 rc ignored (`py-spy rc=` for `py-spy rc=0:`) | KILLED | "…or names it at rc!=0, is retried, not accepted" |
| M10 the heartbeat boot skips the control | KILLED | "the real heartbeat boot runs the retried control" |

M9 survived the first test set: a sampler that names the spin at rc=1 was accepted. The `torn` stub (rc=1 naming `_hb_spin`, then a good sample) was added and kills it. That rc=1 route is real: one hang-once run of the first design read `rc=1` on its second attempt before an rc=0 on its third.

## Null control

- Unmodified tree: the hang-once sampler against the base fails **3 of 3** runs. Each one prints the CI line verbatim: `py-spy did not run: TimeoutExpired: … timed out after 30 seconds` (F5). The same stub in-process against the base fails after 30.4 s on 1 call (F2).
- Power kept at the head (`tests/entities.py`, "null control: …"):
  - a sampler that never answers still fails `hb:positive_control` after exactly `HB_CONTROL_TRIES` calls;
  - so does one that answers rc=0 without the spin;
  - the existing arms still fail on rc=1 `Permission denied`, on no py-spy section, and on an idle rc=0.
- M0 (the unmutated copy) passes every check.

## Figures

- F1 Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 4 script(s) run`: `tests/config_flow_steps.py`, `tests/debug_collect.py`, `tests/entities.py`, `tests/harness_headers.py`. Each was run with `PYTHONPATH=tests/hastub` and passed at `328510e009f70298c2a3fed38bd639b71a1308df`, this head's first parent, as did the `run_always` lines `tests/env_drift.py --claims-only`, `tests/closure.py selftest` and `tests/layout.py`, plus `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`). The instruments print their own counts.
- F2 Failing test first: the hang-once stub in-process through the base's `LoopHeartbeat` and `check_hb_positive_control`. The base prints `hb:positive_control FAIL … py-spy rc=0 names it: False` after 30.4 s with 1 sampler call; the same driver at the head passes with 2 calls. The committed checks themselves fail at the base on import, because `_async_hb_control` does not exist there.
- F3 Mutation proof: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` (table above).
- F4 `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL`.
- F5 Hang-once at both ends: `python3 dev/audit/harnesses/r10_nightly_pyspy_retry.py --tree <tree> --sampler hang-once --runs 3 --image <image+threadpoolctl>`.
  - Base: `SUMMARY sampler=hang-once runs=3 ok=0 fail=3`, each at `timed out after 30 seconds`.
  - Head: `ok=3 fail=0`, each reading `try 2 of 2`.
- F6 Real py-spy, first design (in-spin retry, 3 attempts × 5 s; superseded, not at this head): `--sampler real --runs 20` read `ok=19 fail=1`. The failing run printed `in 3 attempt(s)` with all three `timed out after 5.0 seconds` inside one held spin (gap 15417.9 ms).
- F7 Real py-spy at the head: `--sampler real --runs 60` reads `ok=59 fail=1`. The failing run printed `try 3 of 3`, three `TimeoutExpired … 5.0 seconds`, gap 5302.0 ms. The 59 green runs read `try 1 of 1`: no single-try hang was rescued.
- F8 Real py-spy at the base: `--sampler real --runs 20` reads `ok=20 fail=0`.
- F9 Experiment, not in this diff. The head plus a `spy_blocking` flag drops `--nonblocking` on every try after a timed-out one. `--sampler real --runs 80` reads `ok=80 fail=0`, one episode: try 1 timed out at 5 s, then try 2 (blocking) gave `rc=0` naming the spin after a 38530.4 ms loop gap.
- F10 Hang correlation (from F6, F7, F9): 3 episodes, and the 2 under the two non-blocking retry designs were rescued by 0 of their 4 further samples. The null for independence is about 0.07² per episode, so two such episodes would have P ≈ 2.4e-5. The rule: an episode is a run whose first sample timed out.
- Disclosed load: F9 overlapped one gate run (`tests/entities.py` and others), and the start of F7 overlapped the in-process mutant run, on the same host. F5, F6 and F8 ran alone.

## Red checks

`none` at this head: no CI has run on it, because the handoff opens no pull request. `nightly-status` grades `main`'s newest nightly run, and this branch cannot change it until it merges. Under F7 the `stable` lane still goes red at about the RCA's rate after merge, so `nightly-status` (and through it `pr-contract`, train 16) remains exposed.

## Unpinned sites

n/a: `prepr.sh` step 6d lists none for this diff; every new constant and branch is pinned by a mutant above (M1 to M10).

## Architecture score

Architecture score: dS +0.0000 (F4). No budget moved (F1, `structure.py`).

## Forward-carry

- The RCA's countermeasure A premise, "a first attempt that times out, followed by a second rc=0 naming the spin", fails on real HA: the hang persists per process across in-spin retries and fresh-spin retries (F6, F7, F10). A blocking dump on an affected process completes after about 38 s of stopped process (F9). The next countermeasure for the `stable` red is a design call among (a) inconclusive-on-timeout, (b) re-run the container, and (c) a longer non-blocking timeout, priced above; this group's goal is unmet, so it is the group to re-scope, in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-NIGHTLY-PYSPY-RETRY
- py-spy 0.4.2's slow walk against CPython 3.14.6: the RCA left it with py-spy's maintainers. F9 adds that a blocking dump of an affected process returns rc=0 after about 38 s, so the walk is slow, not endless. Carry: dismissed: upstream (benfred/py-spy), outside this repository; the RCA records the owner

## Friction

- cloud-seat-toolchain: stale: the dispatch says the toolchain is on PATH, but this seat's shell resolved `/usr/local/bin/python3` with no numpy or voluptuous and no Docker daemon running. I prefixed `/opt/hpo/venv-ci/bin` by hand and started `dockerd`. Carry: dismissed: environment settings are the owner's Project configuration, not a tree change
