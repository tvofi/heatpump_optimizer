Fix review: blocked af391637b4446a6ad2cf283c0fda80dd0d3da7de class-open: the merged head fails its own census on main's tools/pr/codeql_scope.py:88 docstring (closure selftest 1 of 124 FAILED), and stamp.py merge_is_record_class, the twin of the policy_lint site fixed here, still detects renames
bus-nonce: e638a91e7031eb8da8a999b9f5ca1c71

Round 3. Reviewed from a detached worktree at `af391637b4446a6ad2cf283c0fda80dd0d3da7de`. The roles diff against main was empty. I judged the delta since round 2 (`89d2b9465`): the fix commit `0a61981e0`, its merge `73d82db25`, and the main merge `af391637b`, which brings in #2405 (`55dc8d9c2`). Evidence: `~/hpo-seats/r10s3/review-2406/evidence-r3/`. Next round is the fourth: under `fixer.md`, that is a re-cut, not a repair.

## Fixed since round 2, and pinned

- RESULT JS twin: `card_rig.mjs` `threeDotFiles`, `card_browser.mjs` `gridScope`, `stop-selfcheck.sh` (including `--cached`) and the two `policy_lint.mjs` diffs all carry `--no-renames`.
- RESULT parity pin (`evidence-r3/parity-pin.txt`). I drove the predicate from `card.mjs:10792-10812`, copied verbatim, against this tree. The `card` lane needs a Home Assistant payload this box cannot build, so this is my own driver of their predicate.
  - At the head: `PIN PASS`.
  - With `--no-renames` dropped from `card_rig` alone: `PIN FAIL`.
  - With both twins reverted together: `PIN FAIL`, because the pin also requires `--no-renames`.
  - So the pin is not vacuous, and the two copies cannot drift together unseen.
- RESULT census: with `--no-renames` dropped from `card_rig.mjs:838`, the census refuses `tests/card_rig.mjs:838` (`evidence-r3/r3-mutants.txt`). The globs now read `.mjs`. My own enumeration over `--name-only` found no diff call split across lines without a backslash (`evidence-r3/nameonly-r3.txt`).
- RESULT owed steps (step 10): both now sit in `R10-TICK-DRIVERS.carry` at roster `97344315a`, on the `handoff/audit-r10-roster` tip. Each carries its control: two SHAs in the memo plus a roster-only regenerate, and the census plus codeql_scope's self-test. The fixer prompt reads `carry` from the group, so a later seat will see them. Not blocking, but note that the beat restart is an orchestrator action. It now waits behind a group gated `after: R10-REF-PRIVACY` whose `files` do not include `state_docs.py`. A post-merge beat item would reach it sooner.
- RESULT merges: `73d82db25` and `af391637b` have trees equal to `git merge-tree --write-tree` of their parents. `git merge-tree --write-tree origin/main(55dc8d9c2) HEAD` returns rc 0.

## Blocking 1: the head is red on its own census (the resolution delta of the main merge)

`python3 tests/closure.py selftest` at the head gives `1 of 124 closure shrink pins FAILED`:

```
FAIL no rename-detecting --name-only diff under RENAME_SITES  [tools/pr/codeql_scope.py:88: """(changed_files, porcelain `git diff --name-only`) over a throwaway repo]
```

`tools/pr/codeql_scope.py` does not exist at `0a61981e0`. It arrived with #2405 in the main merge `af391637b`, and `tools/pr/*.py` has been in the census since round 2. The line is docstring prose, and the census skips only lines that open with `#`, `//`, `*` or `/*`. So the merge is textually clean and semantically red. `tests/run.sh:480` runs the selftest as `run_always`, so `fast (3.14)`, still in progress at 15:24Z, should go red on this head. The body's `ALL 124 closure shrink pins PASSED` and `closure.rename_sites(): ([], [])` were measured before the merge. At the head named in `## Head`, both figures are false (steps 7 and 8).

Remedy: add a `RENAME_ALLOW` entry for the docstring, or tag it `# rename-null-control`, or have `codeql_scope.changed` delegate now, since #2405 has merged and that is the carried item. Then re-take the figures at the head. Before re-merging main, re-run the census: it now reads every `tools/pr/*.py` that main adds.

## Blocking 2: the class is still open at one twin (step 6)

`tools/release/stamp.py:1708` `merge_is_record_class` runs `git diff --name-only <sha>^1 <sha>` with renames on. Its comment (`stamp.py:1677`) and `policy_lint.mjs:2294` both name it the copy of `policy_lint.mjs` `mergeRecordClass`, which this round gave `--no-renames`. That is the round-2 shape again: one twin fixed, the other left. Probe on this head (local commit, never pushed: `git mv custom_components/heatpump_optimizer/__init__.py dev/programme/delivery/99999.md`; `evidence-r3/stamp-twin-probe.txt`):

```
stamp.merge_is_record_class: True
policy_lint's command (--no-renames): custom_components/heatpump_optimizer/__init__.py dev/programme/delivery/99999.md
stamp's command:                      dev/programme/delivery/99999.md
```

So the stamp reads a commit that deletes the integration's entry point as record-class, which exempts it from its row, while `policy_lint` reads the same commit as code. `tools/release/` is outside `RENAME_SITES`, which is why the census passed it. Remedy: give `stamp.py` `--no-renames`, add `tools/release/*.py` to `RENAME_SITES`, and if possible extend the existing copy check in `policy_lint` (`THE STAMP'S COPY`, `policy_lint.mjs:4381`) to compare the two commands. Every other residual I enumerated is plumbing, `ls-tree`, an empty-tree or `--name-status` site handled correctly, or audit evidence under `dev/audit/`.

## Other steps

- RESULT lane_skip self-test at head: `54/54`.
- RESULT checks (step 11; `evidence-r3/checkruns-r3.tsv`): `instrument-self-tests` and `env-matrix` concluded success. `fast (3.14)`, `browser`, `coverage` and `Analyze (python)` were in progress at 15:24Z. Nothing was red yet, but Blocking 1 predicts `fast`.
- RESULT version, claims and budgets: none of them is touched in the delta.
- Not blocking: `_RENAME_EXEMPT` still exempts `--cached`, which detects renames in the index. Today's `--cached` sites only count lines after a pinned restore. Say so in the body, or drop the exemption.
- RESULT head (step 12): `gh pr view` reported `af391637b4446a6ad2cf283c0fda80dd0d3da7de` when I wrote this.
