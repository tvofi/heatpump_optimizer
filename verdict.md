Fix review: blocked 361040baf232104dd3e842ff06015760d1de61c5 trace-gap: the prepr re-record drops .gitattributes, tests/env_drift.py and tools/merge/ledger_merge.py, which prepr reads on CI's fresh checkout, so main would refuse UNDER-SCOPED step prepr again

bus-nonce: 3b41847eb265354496f3cb53123062e7

## Block

Round 1. The three files the re-record removes are not a real narrowing. They come from a trace gap in the recording environment, and the gap depends on that environment.

- The path: `tools/pr/prepr.sh:1980` (inside `--self-test`, cwd at the repo root) runs `bash .claude/hooks/session-start.sh --self-test`. That reaches `report()` (`.claude/hooks/session-start.sh:89-104`). When `git config --get merge.claimnotes.driver` is empty, `report()` runs `python3 tests/env_drift.py --install-merge-driver`. When `merge.ledgermerge.driver` is empty, it runs `python3 tools/merge/ledger_merge.py --install`. Those installs read `.gitattributes`.
- Why the recording missed them: the fixer's seat, like mine, had both drivers set in `.git/config` because the session-start hook installed them when the session opened (`git config --show-origin` gives `file:.git/config` for both). So the 861 s record never took that branch, and the three reads vanished. The same applies to "the first seat's independent run gave the identical diff": both seats share this environment, so the second run is not an independent check.
- CI takes the branch: the job uses `actions/checkout`, `governance.yml` installs neither driver anywhere (no `install-merge-driver` and no `ledger_merge.py --install` in the file), and a fresh checkout has no `merge.*.driver` config. On main's red run the refusal listed only `mutant_guard.py` and `mutant_run.py` as misses. That fits CI having read the three files, which the old table still covered.
- Measured (my own instrument; strace, not the finder's whole-job trace): in a fresh `git clone --no-local` at the head, with no driver config (`git config --get-regexp 'merge\..*\.driver'` rc=1), `strace -f -e openat,execve bash .claude/hooks/session-start.sh --self-test` opens `.gitattributes` (2 calls), `tests/env_drift.py` (2 opens + 1 exec) and `tools/merge/ledger_merge.py` (2 opens + 1 exec), and exits rc=0: `ev/hook.reads.txt` (8 lines). Null control: the same command in the same clone, once the drivers are installed, opens none of the three (0 lines, `ev/hook2.reads.txt`). Every path that differs between the two runs is one this diff deletes.
- The consequence: once merged, the first main push re-runs instrument-self-tests on a fresh checkout. It will measure those three reads against an entry that no longer names them and refuse `UNDER-SCOPED step prepr: files misses ['.gitattributes', 'tests/env_drift.py', 'tools/merge/ledger_merge.py']`. That swaps one red on main for another.
- The cure, cheapest first: keep the three files in the prepr entry beside the three it gains, so the entry is the old one plus `mutant_guard.py`, `mutant_run.py` and `figure_block.py`. Or re-record in a clone where `git config --unset merge.claimnotes.driver` and `git config --unset merge.ledgermerge.driver` were run first. A record taken where the hook has already set up the clone cannot see this branch.

## Findings

- Follow-up: `selftest_scope.py record` measures whatever per-clone git config the recording seat has, so a seat whose session-start hook already installed the merge drivers drops reads that CI's fresh checkout makes. The same gap can narrow any gated step that runs the session-start self-test. One countermeasure would be for `record` to run against a scratch clone with no `merge.*.driver` config, or to refuse while those drivers are set. This review does not settle it. Carry: R10-HOTFIX-MAIN-IST-PREPR-SCOPE
- Follow-up: the body's root-cause countermeasure (run `selftest_scope.py check` in prepr/ci_predict when a gated step's script changes) is unbuilt, and the body names R10-HOTFIX-PREPR-WC-PAD as the owner of prepr.sh. Carry: R10-HOTFIX-PREPR-WC-PAD

## Evidence

- Head reviewed: 361040baf232104dd3e842ff06015760d1de61c5 (`ev/HEAD.txt`). Body: BODY.md at a71a0532313161327edf5960a3dc0120c51ebacb names the same head. Base b737e88eee4f. origin/main is ef579d9ba689.
- The diff is `tools/ci/selftest_closures.json` only (+3/-3, prepr `files`). VERSION, the manifest and RELEASE_NOTES.md are untouched (0 paths).
- `git merge-tree --write-tree origin/main 361040baf` rc=0 (tree 5e4f61791ad3). It merges cleanly.
- `selftest_scope.py static`: 112 gated step(s), 0 problem(s).
- `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- There is no pull request yet, so there is no review packet and no CI on this head to read. No red is owed a `## Red checks` answer (`instrument-self-tests` is not in `merge_train.py owed-reds`).
- The body's figures, re-derived in my seat's environment, where the drivers are set: `selftest_scope.py record --step prepr --out <scratch>` gave OK 901.5 s, 0 failed, 0 broken traces (`ev/record.log`). The recorded prepr entry equals the head's on files, probes, dirs, run_sha, index and objects. `drift()` on that measurement with main's b737e88ee table gives `UNDER-SCOPED step prepr: files misses ['dev/audit/harnesses/mutant_guard.py', 'tools/audit/seat/mutant_run.py', 'tools/pr/figure_block.py']` plus `note: over-scoped step prepr: 3 files no longer measured`. With the head's table it gives no prepr refusal (`ev/drift_cmp.prepr.txt`). So the mutation proof and the null control reproduce as the body states, but only in an environment where the drivers are already installed. My harness passed only the prepr step to `drift()`, so the other entries print as EXTRA; that is an artifact and I drop those lines.
- The full `check --traces` over CI's whole-job traces was not run. I could not re-derive "0 refusals" for any step but prepr, and the body says the same.
- Disclosure: the strace instrument above is mine, not the finder's harness (fix-review.md step 9). It traces the one sub-path in question, not the whole job.
