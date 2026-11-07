R10-HOTFIX-CODEQL-HEADROOM. **The measurement refutes this PR's premise. Do not merge it as a CodeQL cure.**

A dispatched CI run at this head (run 42381006183, job 128428511054) did a real python analysis. It was compared against main's job at the same merge base (job 128423079820 at `a37c58e5f321`):
- `tests/entities.py` extraction fell from 314673 ms to 208291 ms.
- `tests/features.py` extraction rose from 739494 ms to 1333896 ms.
- Query evaluation then ran 21 min and finished 6 of 52 queries. Main finished all 52 in 12m42s.
- `codeql / Analyze (python)` was **cancelled at its 45-minute cap** after 45m05s. Main's job took 26m27s.
- The null control held flat: `closure.py` read 2215 ms against 1769 ms, `structure.py` 2585 ms against 2257 ms.

So wrapping each module-level `try` statement in `def _module_block_<line>():` is not a cure. In `features.py` (169 wrappers) it makes both extraction and query evaluation slower, enough to cancel the job. In `entities.py` (110 wrappers) extraction falls. The ruling on the group, closing it or re-scoping it (for example to the `entities.py` half alone, or to #3232's single 364-line module-scope `try`), is the dispatch seat's. I have not changed the code: the brief allows a change only where the measurement demands one, and the change it points to is a different design, not a repair of this one.

A replicate at the same head (run 42384677444, job 128440898484) repeats the result on a slower runner. Its null control read `closure.py` 3228 ms and `structure.py` 4606 ms, close to main's slowest job (3231 / 4117 ms, `features.py` 1389484 ms). There `features.py` read 2008646 ms and `entities.py` 310210 ms, and the job was again **cancelled at the cap**, with 6 of 52 queries done.

What the change does (unchanged since the last round, which the review cleared as behaviour-neutral):
- Each module-level statement holding a `try` (169 in `features.py`, 110 in `entities.py`) runs inside `def _module_block_<line>():`, called once at its old place. It declares `global` every name it binds.
- `tests/entities.py` gains the guard: no test script past `_GIANT_SCRIPT_LINES` (20000 lines) runs a `try` at module scope. The guard carries its detector's own null control.
- The rewrite is landed as `tools/audit/seat/wrap_module_tries.py`, with its `INSTRUMENTS.md` entry.
- `tests/layout.py`'s guard keys base citations on the stripped line, so the re-indent reads as no new citation.
- `tests/closures.json` records `entities.py`'s inert read of the new tool.

Two corrections to the last body:
- It said "CodeQL runs on a pull request or `main` only (`ci.yml` `on:`)". That was false: `ci.yml`'s `on:` carries `workflow_dispatch`, and a dispatched run analyzes. The run above is one.
- It said "the PR's own `codeql / Analyze (python)` job is the first measurement at this head". That was false too: `tools/pr/codeql_scope.py` `decide` skips the python leg for this diff on a pull request, so that job was a stand-in.

## Head

`0d5934cbbbf8f4343e0c766f0051049fde5fc466`. It is four `git merge`s of `origin/main` on the last handoff `402b18da98cc`, with no rebase:
- `f0b215af2447` merges `a37c58e5f321`.
- `f75915f75c10` merges `b4ec2f332fe3`.
- `2eb791d307e1` merges `1c1ae100b59e`, read at 2026-11-07T15:37:04Z.
- This head merges `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76`, read at 2026-11-07T16:13:44Z.

The CodeQL runs measured `f0b215af2447`. `tests/features.py`, `tests/entities.py`, `tests/closure.py`, `tests/structure.py` and `.github/` are byte-identical between `f0b215af2447` and this head (`git diff --quiet f0b215af2447 0d5934cbb -- <those paths>` rc=0), so the extraction figures describe this head's files.

The scoped scripts and structure ran at `2eb791d307e1`. The last main delta (`1c1ae100b59e` to `4b5d771bdf8f`) is a delivery row and a triage note. It scopes to `MODE: SCOPED -- 0 script(s) run, 33 scoped out` (`tests/closure.py select --diff 1c1ae100b59e`, in a worktree at `4b5d771bdf8f`), so those results describe this head by measured closure. prepr ran again at this head.

## Mutation proof

- The guard: with `tests/features.py` restored to main's text (`git checkout a37c58e5f321 -- tests/features.py`, in a detached worktree at `f75915f75c10`, which this head differs from by three delivery rows only), `PYTHONPATH=tests/hastub python3 tests/entities.py` reads `1 of 2647 ENTITY CHECKS FAILED`, rc=1. The one top-level failure is `FAIL no test script past _GIANT_SCRIPT_LINES runs a try at module scope (CodeQL extraction cost)  [module-scope try lines -> {'entities.py': [], 'features.py': [782, 1676, 2416, 4902, 8321]}]`. At this head the same check is `ok`, with `ALL 2647 ENTITY CHECKS PASSED`.
- Pins: the six seeded ledger pins (4 killed by `tests/features.py`, 2 by `tests/entities.py`) were re-verified by the fix review at `55a2753a6d64`, each `PIN RE-VERIFICATION: 1 reproduced`. I did not re-run them at this head: the wrapped statements are unchanged since that review, and main's merged delta adds checks to both files without touching a wrapper.

## Null control

- CodeQL extraction: `tests/closure.py` and `tests/structure.py`, which this diff leaves alone, read 2215 ms and 2585 ms in the head's job. Main's four jobs read 1769–3231 ms and 2257–4117 ms. A runner-wide slowdown or speedup would have moved them too, and it did not: the `features.py` rise and the `entities.py` fall are this diff's effect, not the runner's.
- Suites: the scoped scripts pass at this head with main's own check additions (Figures).

## Figures

- Main, at this head's first merge base `a37c58e5f321` (job 128423079820, 13:56:12Z to 14:22:39Z, 26m27s, success): `features.py in 739494ms`, `entities.py in 314673ms`, `closure.py in 1769ms`, `structure.py in 2257ms`. Query evaluation `[52/52 eval 12m42s]`. — `gh api repos/tvofi/heatpump_optimizer/actions/jobs/128423079820/logs | grep -E "Extracted file .*tests/(features|entities|closure|structure)\.py in|/52 eval"`
- Main, earlier (jobs 127952679731, 127954661976, 127995766058; 28m18s, 30m51s, 43m16s, all success): `features.py` 817241 / 966935 / 1389484 ms; `entities.py` 349859 / 342523 / 688012 ms; `closure.py` 2111 / 2073 / 3231 ms; `structure.py` 2699 / 2475 / 4117 ms. I read these from the full logs myself; the last round only quoted them. — same `grep` on each job's logs
- Head `f0b215af2447` (run 42381006183, `workflow_dispatch` with inputs empty; job 128428511054, 14:19:18Z to 15:04:23Z, 45m05s, **cancelled**): `entities.py in 208291ms`, `features.py in 1333896ms`, `closure.py in 2215ms`, `structure.py in 2585ms`. Query evaluation started 14:43:02Z; the last line before the cancel is `[6/52 eval 2s]`. — same `grep` on job 128428511054's logs
- Head replicate `f0b215af2447` (run 42384677444, inputs empty; job 128440898484, 15:16:50Z to 16:01:56Z, 45m06s, **cancelled**): `features.py in 2008646ms`, `entities.py in 310210ms`, `closure.py in 3228ms`, `structure.py in 4606ms`. Queries started 15:51:54Z; last line `[6/52 eval 3.6s]`. Against main's job with matching null-control times (127995766058: 3231 / 4117 ms), `features.py` rose 1389 s to 2009 s (+45%) and `entities.py` fell 688 s to 310 s. — same `grep` on job 128440898484's logs
- Change, head against same-base main: `features.py` +80% (739 s to 1334 s), `entities.py` −34% (315 s to 208 s), job 26m27s to over 45m (cancelled), null control flat. `features.py` at the head is also within 4% of main's slowest earlier run (1389 s), so even against the widest main figure it does not fall.
- Files the head's extractor read: 1519 `Extracted file` lines at the head against 1518 in main's same-base job (`grep -c "Extracted file"`). The extra one is the new `wrap_module_tries.py`.
- Scope at this head: `MODE: SCOPED -- 5 script(s) run, 28 scoped out` (`doc_claims.py`, `entities.py`, `features.py`, `harness_headers.py`, `layout.py`), all run at `2eb791d307e1` with `PYTHONPATH=tests/hastub python3 tests/<script>`: `ALL 296 checks PASSED`, `ALL 2647 ENTITY CHECKS PASSED`, `ALL 4905 FEATURE CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `layout self-test: ok` — `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`

## Red checks

Every check run at `f0b215af2447` was read at 2026-11-07T16:05Z, all on one page of 100: 93 runs, of which 4 failed, 3 were cancelled and 1 was queued (`gate` 128453059402, the replicate's). No check has run at this head `2eb791d30` (`total_count` 0).
- `gate` (128439147690, run 42381006183): `FAIL run(s) [42384677444] at this head are still being judged; their gate decides`. The replicate superseded it. Cheaper detector: none is needed; this is the gate's own hand-off.
- `codeql / Analyze (python)` (128440898484, the replicate): cancelled at the cap, like 128428511054 below. Same answer.
- `prelude` (128426266415), `gate` (128428665643) and `pr-contract / pr-contract` (128426388641) are all from run 42380280230. That was my first dispatch, with inputs `pr=3266`, `base=main`, as the brief named them. The prelude refused: `FAIL dispatch pr=3266 does not name the open PR headed by f0b215af2447`. A fixer's ref is never the PR head, so that input form cannot work for a fixer seat. `gate` repeats the prelude's failure (`FAIL prelude: failure`). `pr-contract` failed at `Wait for code scanning and list its open alerts`. Cheaper detector: none is needed, because the prelude is the detector and it refused in 25 s. The finding is a Forward-carry.
- `codeql / Analyze (python)` (128428511054): cancelled at its 45-minute cap. This is the PR's own effect, the measurement above. There is no cheaper detector on a pull request, because `codeql_scope.py` gives a `tests/`-only diff a stand-in. That is the follow-up the last review recorded, and the reason a dispatch was needed.
- `governance / instrument-self-tests` (128428511108): cancelled after 30m14s, in its step `Show the CI predictor (tools/pr/ci_predict.py) predicting pr-contract's carry refusal`, which started at 29 min. Main's same job took 28m42s (run 42379183423) and 25m49s (run 42372556024), so it already runs close to that bound. Whether the larger `features.py` costs the extra minutes is unmeasured. Cheaper detector: none found.

## Forward-carry

- The premise fails: per-statement wrapping of module-scope `try` slows `features.py`'s CodeQL extraction and query evaluation, and the python job no longer fits its cap. The group's design has to change before any fix lands, and only `entities.py`'s half measured a gain. Carry: R10-HOTFIX-CODEQL-HEADROOM
- A fixer cannot dispatch `ci.yml` with `pr=<N>` from its own ref. The prelude refuses any ref that is not the PR's head. Dispatch with inputs empty, the batch-proof form, which still analyzes. A brief asking a fixer for a CodeQL figure should name that form. Carry: R10-HOTFIX-CODEQL-HEADROOM
- The last review's residual is that the guard does not refuse a module-scope `ClassDef` holding a `try`. The measurement answers it: the wrapper form is itself slow for `features.py`, so how the guard scopes it is moot while the premise fails. Carry: dismissed: the measurement shows the wrapper, not the guard's scope, decides the cost; no code
- `tools/audit/seat/features_block.py` runs a block from a marker line to the script's close. A marker inside a wrapped statement starts indented and fails to compile, as a marker inside a module-level `try` already did. Carry: dismissed: no behaviour change for a top-level marker

## Friction

- fixer-codeql-dispatch: contradiction: the brief named dispatch inputs `pr=3266`, `base=main`, and the prelude refuses them for any ref but the PR's head, so the first run (42380280230) went red at the prelude. Carry: R10-HOTFIX-CODEQL-HEADROOM
