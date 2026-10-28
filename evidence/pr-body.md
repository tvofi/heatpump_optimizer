Builds countermeasure A of `dev/audit/rca/nightly-ha-pyspy-timeout.md` (#2479) in `tests/nightly_ha.py`. **It does not remove the `stable` red, and the real-HA measurement says why: the hang is per process, not per sample.** It lands what is sound: a cheaper red and a bounded retry, each pinned. The per-process residual goes to R10-NIGHTLY-HB-RESPAWN (decision O-4).

Delivery-status: group R10-NIGHTLY-PYSPY-RETRY.

Round 2 repairs round 1's `blocked mutation-vacuous` verdict (`review/2605`, `VERDICT.md`, reviewed head `7651b942…`):

- The real lane's cut is now pinned. The real boot passes no `spy_timeout`, so the cut is `LoopHeartbeat`'s constructor default. `tests/entities.py` now checks that this default `is PY_SPY_TIMEOUT_S`. It also checks that `_async_hb_measure` injects no `spy_timeout` of its own. X5 (default `30.0`) and X2 (`PY_SPY_TIMEOUT_S = 25.0`) are now killed.
- The whole-control bound is pinned. `HB_CONTROL_TRIES * (HB_CONTROL_HOLD_S + HB_CONTROL_REST_S)` must be `< 22.0` s. At this head it is 21.75 s.
- Two behaviour pins are added:
  - The control rests between tries. Two tries with a 1 s rest must take at least the rest plus both spins. This kills X1.
  - The control survives two hung samples and answers on try 3. This kills X3 (`HB_CONTROL_TRIES = 2`).
- The constants' comment at `PY_SPY_TIMEOUT_S` / `HB_CONTROL_TRIES` was corrected. It now says the fresh-spin retry was measured **not** to rescue a real-HA hang (F6, F7). It also says what the retry is kept for: a bounded cost per red, and a retry rather than a fail when a try's sample came back late, missed the spin or answered rc≠0.

What the PR changes, from the base:

- `py-spy dump --nonblocking` is cut at `PY_SPY_TIMEOUT_S` = 5 s instead of 30 s. The RCA measured a healthy sample at ≤ 0.15 s on 710 of 710 in-image samples. That is a small synthetic process, not real HA.
- `hb:positive_control` now runs `_async_hb_control`:
  - It makes up to `HB_CONTROL_TRIES` = 3 fresh spins, with `HB_CONTROL_REST_S` = 1 s of loop time between them.
  - Each spin is sampled once and held until that sample returns, bounded by `HB_CONTROL_HOLD_S` = 6.25 s.
  - It stops at the first try in which the gap, the in-process stack and py-spy's rc=0 section all name `_hb_spin`.
  - `check_hb_positive_control` takes the list of tries and passes only when a single try reads all three.

What is pinned, and what is not:

- Pinned in `tests/entities.py`:
  - Per spin: `HB_DUMP_S + PY_SPY_TIMEOUT_S <= HB_CONTROL_HOLD_S < HB_HANG_S` (60 s).
  - Whole control, every try hung: `HB_CONTROL_TRIES * (HB_CONTROL_HOLD_S + HB_CONTROL_REST_S) < 22` s, against the base's 30 s for one sample. The control rests only between tries, so the tighter figure is 3 × 6.25 + 2 × 1 = 20.75 s.
  - Tries: at least 3, by the two-hang pin.
- Not pinned as a figure: any other stall's dump, which costs at most `HB_MAX_DUMPS` × `PY_SPY_TIMEOUT_S` = 3 × 5 s. That is derived, not measured. Its two factors are bounded by pins: the default cut is the constant, and the whole-control pin forces `PY_SPY_TIMEOUT_S` ≤ 5.08 s at 3 tries.
- Values left free, and why:
  - `PY_SPY_TIMEOUT_S` below 5 s: a cut shorter than a healthy sample times out every try and fails the control loudly, never silently.
  - `HB_CONTROL_REST_S` within the bound: only that a rest happens is pinned, because F7 measured that no rest length rescues a hang.
  - `HB_CONTROL_TRIES` above 3: refused by the 22 s pin, since 4 tries give 29 s.

The first design, measured and replaced: hold one spin and retry py-spy up to 3 times inside it. A real-HA run hung on 3 of 3 attempts inside one held spin (F6), so I replaced it with the try-level retry. Alternatives considered:

- A retry without the hold: the retried sample would read the idle loop and could never name the spin.
- A blocking-mode fallback and a raised timeout: priced under the residual below.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_019vzytMQit4jU5q31MVSTRF

## Disclosed: what this cannot fix

- In 140 real-py-spy heartbeat runs at the two retrying designs (F6 + F7 + F9), 3 hang episodes occurred. Under the two non-blocking designs, every retry the code made hung:
  - in-spin retries: 3 of 3 hung (F6);
  - fresh-spin retries 1 s apart: 3 of 3 hung (F7);
  - the experimental blocking fallback (F9) answered, but only after the process was stopped for 38.5 s.
- If samples hung independently at the RCA's ≈ 7 %, two further hangs in one episode would have P ≈ 0.07² ≈ 0.005. Two episodes, each with both further samples hung, would have P ≈ 2.4e-5 (F10). The hang therefore holds for the life of the HA process. **This PR does not lower the ≈ 7 % false-red rate on `stable`**; it lowers what each red costs.
- The countermeasure that addresses a per-process hang is a container respawn on an all-tries py-spy timeout. Under decision O-4 it is group R10-NIGHTLY-HB-RESPAWN, which runs after this group, and it is not built here (Forward-carry).

## Root cause

`dev/audit/rca/nightly-ha-pyspy-timeout.md`, #2479. This PR builds that RCA's countermeasure A, and it falsifies one of A's premises. The RCA expected "a first attempt that times out, followed by a second rc=0 naming the spin". That is the behaviour of the stub. On real HA the further attempts hung too (F6, F7).

## Head

`5a3c5d2395043b7ce9f82b383be350356c9d5864` merges the authored code head `7bd9c8f3e7f909413f052a29dff4ec1ff094d4a6` and then merges origin/main `6c8903a44` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`e0725a9ede5b282b7097e8f0d31fbfc58ab72415` merges the authored code head `7bd9c8f3e7f909413f052a29dff4ec1ff094d4a6` and then merges origin/main `6c8903a44` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`7bd9c8f3e7f909413f052a29dff4ec1ff094d4a6`. Its first parent is `75910213b`, a merge of `origin/main` at `cd4aaed44b9000057aeff01ee3df9f80dbec8aad` (v7.0.3; tip read 2026-10-22T10:42Z) into the round-1 code head `6712698aeaf98cca27402f7ab96fef3dd95415b1`. That merge brought only the stamp: `VERSION`, the manifest, `RELEASE_NOTES.md`, the claim files, the card and the D6 claims.

`tests/nightly_ha.py` at this head is blob `de2bcb89d6c968f97c0bad9a1bfd7704333fd854`, and round 1's was `91164340df3127e15459a3a0cf7da6a9d73afc24`. The two parse to an identical AST (F11): round 2 changed only comments there. The container runs F5 to F9 read round 1's blob, and the base blob is `30f8263e443ff304b87160b8e8527255fb9de1c9`.

Image for F5 to F9: `homeassistant/home-assistant@sha256:33afb0659d786213264c2211f8d91c5fe87461c56eba6a3a546eb05fc71e89f4`, plus a `threadpoolctl` 3.6.0 layer, as in the RCA.

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` at this head prints `SUMMARY killed=14 survived=0 null=ok`, rc=0. Each mutant is one substitution in `tests/nightly_ha.py`, run against the A15 py-spy block of `tests/entities.py`.

| mutant | result | killed by (at least) |
|---|---|---|
| M1 one try only (`range(1)`) — brief's first | KILLED | "survives one hung py-spy sample…", "…is retried, not accepted", "the control rests between tries…", "…survives two hung samples…", "null control…" |
| M2 plumbing timeout `timeout=30` — brief's second | KILLED | "survives one hung py-spy sample… the hang cut at the sample's timeout…" |
| M3 a try accepted on any non-empty dump — brief's third | KILLED | "survives one hung…", "…is retried, not accepted", "null control…" |
| M4 spin not held past 0.6 s | KILLED | "survives one hung… the spin held across it" |
| M5 `dumped` never set | KILLED | "survives one hung…" |
| M6 the check accepts rc=0 without the spin | KILLED | "passes at the spin…", "…is retried…", "null control…" |
| M7 the control passes no hold | KILLED | "survives one hung…" |
| M8 readings accepted split across tries | KILLED | "passes on any one try that reads all three…" |
| M9 rc ignored | KILLED | "…or names it at rc!=0, is retried, not accepted" |
| M10 the boot skips the control | KILLED | "the real heartbeat boot runs the retried control" |
| **X1** no rest (`await asyncio.sleep(rest)` → `pass`) | KILLED | "the control rests between tries…" |
| **X2** `PY_SPY_TIMEOUT_S = 25.0` | KILLED | "the real lane cuts py-spy at PY_SPY_TIMEOUT_S, and the whole control… under 22 s" |
| **X3** `HB_CONTROL_TRIES = 2` | KILLED | "the control survives two hung samples, answering on try 3…" |
| **X5** `LoopHeartbeat` default `spy_timeout=30.0` | KILLED | "the real lane cuts py-spy at PY_SPY_TIMEOUT_S…" |

X1 through X5 are the reviewer's surviving mutants from round 1, with their substitutions. All four survived round 1's checks, and each is now killed by a check this round adds. The reviewer's X4 (no break) was already killed. X6 (the check reads only the last try) is equivalent, as the reviewer found, because the loop breaks on the first all-true try.

## Null control

- M0, the unmutated copy, passes every check (`M0-null all checks pass`).
- X1's pin has a timing margin (F12). With the rest, the two-try run took 2.604 s against the 2.2 s floor. Under X1 it took 1.603 s. The floor is a lower bound, so host load can only lengthen a run and cannot turn the head red.
- The base fails the hang-once sampler. In-process, it fails after 30.4 s on 1 call (F2). In the container it fails 3 of 3 runs at `timed out after 30 seconds` (F5).
- Power is kept at the head:
  - A sampler that never answers fails `hb:positive_control` after exactly `HB_CONTROL_TRIES` calls, and so does one that answers rc=0 without the spin.
  - The existing arms still fail on rc=1, on a missing py-spy section, and on an idle rc=0.

## Figures

- F1 Gate scope at this head: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. I ran each named script with `PYTHONPATH=tests/hastub` at the round-2 tree, and each passed:
  - `tests/entities.py`: `ALL 2397 ENTITY CHECKS PASSED`, rc=0 (round 1 had 2394; this round adds 3 checks);
  - `tests/config_flow_steps.py`;
  - `tests/debug_collect.py`;
  - `tests/harness_headers.py`.
  - The `run_always` lines passed too: `tests/env_drift.py --claims-only <merge-base>`, `tests/closure.py selftest` and `tests/layout.py`.
  - `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against cd4aaed44b90`.
- F2 Failing test first (round 1, base `b787c7d45951…`, unchanged code since). The hang-once stub was driven in-process through the base's `LoopHeartbeat` and `check_hb_positive_control`. The base prints `hb:positive_control FAIL … py-spy rc=0 names it: False` after 30.4 s with 1 call. The same driver passes at the head with 2 calls. The reviewer re-derived both ends: 30.3 s with 1 call, against 7.1 s with 2 calls.
- F3 Mutation proof: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` (table above).
- F4 `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL`.
- F5 to F10 were not re-taken this round. They are container runs at round 1's `tests/nightly_ha.py` blob, which has the same AST as this head's (F11). Each figure states its rule:
  - F5 Hang-once at both ends: `python3 dev/audit/harnesses/r10_nightly_pyspy_retry.py --tree <tree> --sampler hang-once --runs 3 --image <image+threadpoolctl>`. Base: `ok=0 fail=3`, each at `timed out after 30 seconds`. Head: `ok=3 fail=0`, each `try 2 of 2`. The reviewer reproduced both ends.
  - F6 Real py-spy, first design (in-spin retry; superseded, not at this head): `--sampler real --runs 20` gave `ok=19 fail=1`. The failing run had all 3 attempts time out at 5.0 s inside one held spin.
  - F7 Real py-spy, the try-level design: `--sampler real --runs 60` gave `ok=59 fail=1`. The failing run read `try 3 of 3`, three `TimeoutExpired … 5.0 seconds`. The 59 green runs read `try 1 of 1`, so no single-try hang was rescued.
  - F8 Real py-spy at the base: `--sampler real --runs 20` gave `ok=20 fail=0`.
  - F9 Experiment, not in this diff: a blocking dump after a timed-out non-blocking one. `--runs 80` gave `ok=80 fail=0`, with one episode answering rc=0 after a 38530.4 ms loop gap.
  - F10 Hang correlation from F6, F7 and F9. An episode is a run whose first sample timed out. There were 3 episodes, and under the two non-blocking designs 0 of 4 further samples were rescued. The independence null is ≈ 0.07² per episode, so ≈ 2.4e-5 for two such episodes.
- F11 Comment-only change to `tests/nightly_ha.py` this round: `python3 -c "import ast,subprocess; a=subprocess.check_output(['git','show','6712698a:tests/nightly_ha.py']); b=subprocess.check_output(['git','show','HEAD:tests/nightly_ha.py']); print('AST', 'IDENTICAL' if ast.dump(ast.parse(a))==ast.dump(ast.parse(b)) else 'DIFFERENT')"` prints `AST IDENTICAL`.
- F12 X1 margin: I appended a probe printing `_hb_late[4]` to the harness's `block()` and ran it through its `HEADER` on the unmutated copy and on X1. The results were `late=2.604` and `late=1.603`, against the pinned floor `_HB_REST + 2 * HB_CONTROL_S` = 2.2 s.
- F13 Carry routing:
  - `python3 -I tools/audit/carry_audit.py check --body <this body>` against main's roster prints `CARRY-AUDIT: 3 finding item(s): 2 routed, 0 unrouted, 1 bad destination(s)`. The bad destination is `R10-NIGHTLY-HB-RESPAWN is not a group of the roster`, because the group is so far only on `handoff/audit-r10-roster`.
  - `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` prints `3 routed, 0 unrouted, 0 bad destination(s)`.
  - So the route resolves once that roster lands, and this PR's merge must follow it. I did not work around the check.
- Disclosed load: the mutant harness and `tests/entities.py` ran concurrently on one host. The timing pins are lower bounds, so load can only make them pass more slowly, never pass a mutant that skips the rest.

## Red checks

`none` at this head: the handoff opens no pull request, so no CI has run on it. `nightly-status` grades `main`'s newest nightly run. Under F7 the `stable` lane will keep going red at about the RCA's rate after this merges, until R10-NIGHTLY-HB-RESPAWN lands.

## Unpinned sites

n/a: `prepr.sh` step 6d lists none for this diff. Every new constant and branch is pinned by a mutant above (M1 to M10, X1, X2, X3, X5). The values left free within those pins are stated, with their reasons, in the summary.

## Architecture score

Architecture score: dS +0.0000 (F4). No budget moved (F1, `structure.py`).

## Forward-carry

- Per-process py-spy hang (F6, F7, F10). On real HA a py-spy sample that hangs keeps hanging for the life of the HA process, so a retry inside it cannot rescue the control, and `stable` still false-reds at about the RCA's rate. Decision O-4 (orchestrator, mandate 6329234399) moves it to a new group that runs after this one: a container respawn on an all-tries py-spy timeout (the group and its brief are in `dev/programme/rosters/wave-r10-groups.json`, R10-NIGHTLY-HB-RESPAWN, landing with roster PR #2608). F9 adds that a blocking dump on an affected process returns only after about 38 s of stopped process. Carry: R10-NIGHTLY-HB-RESPAWN
- py-spy 0.4.2's slow walk against CPython 3.14.6, which the RCA left with py-spy's maintainers. Carry: dismissed: upstream (benfred/py-spy), outside this repository; the RCA records the owner

## Friction

- cloud-seat-toolchain: stale: the dispatch says the toolchain is on PATH, but this seat's shell resolved `/usr/local/bin/python3`, which has no numpy. I prefixed `/opt/hpo/venv-ci/bin` by hand, as round 1 did. Carry: dismissed: environment settings are the owner's Project configuration, not a tree change


