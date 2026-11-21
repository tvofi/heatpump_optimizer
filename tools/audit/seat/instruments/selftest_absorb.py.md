# `selftest_absorb.py`

- `selftest_absorb.py` — the consumer of main's `selftest-closures` artifacts
  (P-R11-SELFTEST-ABSORB; dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md). When:
  run by the beatd row `selftest-absorb` every 1800 s; by hand only to
  regenerate or review. `beat` reads main's newest ci.yml push runs, classes
  each by its `governance / instrument-self-tests` drift step (`red` on
  failure, `owed` on success with a `selftest-absorbed` artifact, which is the
  drift step's `ABSORB OWED` note, `clean` otherwise), and absorbs the
  artifacts of every red or owed run back to the last clean one with
  origin/main's tip's own `selftest_scope.py absorb` in a scratch clone, so a
  merge since the runs cannot outrun it. rc 0 `CLEAN`; rc 1 `OWED <n> read(s),
  <m> step(s)`, and with `--push` the table committed on the tip and
  force-pushed as `handoff/selftest-absorb` through `tools/pr/app_push.sh
  --branch-only` (`unchanged` when that ref already holds it on that tip); rc 4
  `RECORD-OWED` when absorb adds nothing and a refusal remains or the tip's
  own run is red, which only `selftest_scope.py record` (Linux) repairs; rc 2
  `UNREADABLE`. `verify --head SHA` is the standing pull request's review
  (`dev/governance/roles/fix-review.md`): the head changes the table alone, a
  re-run at the head's parent over its commit message's `--run` ids is
  byte-identical, and the parent's `selftest_scope.py grows` finds no read
  dropped. `--self-test`: the root cause's runs (defect, fixed, null) over a
  faked GitHub and git, and one mutant per branch.
