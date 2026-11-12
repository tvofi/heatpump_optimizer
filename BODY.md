# R10-RCA-PREPR-DARWIN-SELFTEST: `prepr.sh --self-test` fails only on the macOS seat, three times in round 10

This is the root-cause seat for the class, following `dev/governance/roles/root-cause.md`
and `dev/governance/rules/defect-root-cause.md`. It is a read-only probe at
`b737e88eee4fe879b0f5412a6730bf8eff46b823`. It read the third instance's repair
(`handoff/r10-hotfix-prepr-wc-pad`, heads `1386441425905fd0d7bb0571f1bac61ff5d7777b` and
`c8780ea33db1c31ff1d38144c70af3d1b3f25eda`) as evidence and changed nothing there. The
content below is meant for `dev/audit/rca/R10-RCA-PREPR-DARWIN-SELFTEST.md`.

## 1. The three instances, reproduced on Linux with the macOS host's divergence emulated

The seat has no macOS host. It reproduced each instance by emulating, on a Linux
container, the one host property each instance depends on. Every row is a full
`bash tools/pr/prepr.sh --self-test` run from a detached worktree at the named head.

- **BSD `wc` emulation:** `unshare -m` plus `mount --bind <stub> /usr/bin/wc`. The stub
  right-aligns every count to width 8, as macOS prints it (`printf 'x\n' | wc -l` gives
  `       1`). Because it is mounted at `/usr/bin/wc` and not put on `PATH`, it also reaches
  stubs that call `/usr/bin/wc` by absolute path.
- **Seat shim emulation:** `tools/audit/seat/seat_venv.sh --install-shims <dir>`, with that
  directory first on `PATH`. The venv is at `$HOME/.local/state/hpo/venv-ci`, and
  `HPO_STATE_DIR` is unset, which is the macOS seat's layout (`seat_venv.sh:47`). Under any
  other `HOME`, the shim prints `no pinned interpreter at <HOME>/.local/state/hpo/venv-ci/...`
  and exits 127. The seat measured this directly.

| instance | head | host emulated | result | failing arm |
|---|---|---|---|---|
| (a) R10-HOTFIX-PREPR-SELFTEST-DARWIN, defect | `cb5512741638029289deb392b30bc246fa667387` (`89daf6c73^`) | seat shim | rc 2, 513 passed, 1 failed, 386 s | `a body naming only repository-relative paths and ~/ text passes (null control) (got 1, wanted 0)` |
| (a), fixed | `89daf6c7398d91d567aa229efcd310d8e98cd790` (#3343) | seat shim | rc 0, 514 passed, 0 failed, 386 s | none |
| (b) #3455 wc string compare | `046736a49` (#3455 merged) | BSD wc | rc 2, 536 passed, 1 failed, 396 s | `and the in-place run leaves the work tree clean (got        0, wanted 0)` |
| (c) R10-HOTFIX-PREPR-WC-PAD, first handoff | `1386441425905fd0d7bb0571f1bac61ff5d7777b` | BSD wc | rc 2, 537 passed, 1 failed, 397 s | `the padding wc stub pads its count, ... (null control) (got               1, wanted        1)` |
| (c), repaired | `c8780ea33db1c31ff1d38144c70af3d1b3f25eda` | BSD wc | rc 0, 540 passed, 0 failed, 397 s | none |
| control | `c8780ea33db1c31ff1d38144c70af3d1b3f25eda` | none (GNU) | rc 0, 540 passed, 0 failed, 396 s | none |

Instance (a) failed on the macOS seat with `got 127` (#3343's body). Under the emulation it
fails the same arm with `got 1`. The failing arm and its direction match; the return code does
not. This seat did not establish why the code differs. Each instance is green on Linux CI at
its own head: (a) and (b) merged through `instrument-self-tests`.

Instance (c) was isolated directly. On a GNU host, `printf 'x\n' | wc -l` through the
`1386441425` stub gives `       1`, which is the expected value, so the arm passes. On the BSD
host it gives `              1`, because the stub prefixes seven spaces to a count the host has
already padded. The fixer's own emulation put a padding `wc` first on `PATH`. The stub escaped
that emulation by calling `/usr/bin/wc` by absolute path, so the emulation could not reach
the stub.

## 2. Cause

**Named cause:** `prepr.sh --self-test` asserts on output from host programs that differ
between the operator's macOS seat and every Linux host that runs the self-test before a merge:

- (b) and (c): BSD `wc` pads its count to width 8.
- (a): the seat's `python3` is a shim that resolves its venv under `$HOME`.

The `st` helper compares strings (`tools/pr/prepr.sh:1936`, `[ "$1" = "$2" ]`). Any host
formatting difference in a captured value therefore becomes a failure.

Which side moved: in each instance the self-test changed and the hosts did not. `89daf6c73`
changes an arm added earlier. `003f89cf9c` (#3455) adds the unstripped
`st "$(mg status --porcelain | wc -l)" 0`. `1386441425` adds the double-padding stub. The
seat shim predates round 10's instances (§3).

**How far the class reaches.** The search covered tracked `*.sh` under `tools/` and
`.claude/hooks/`, read-only.

- Unstripped `wc` output compared as a string: one site, `tools/pr/prepr.sh:2413` at
  `b737e88`. That is instance (b), still on main because (c)'s repair is unmerged. Every other
  `wc` comparison either strips with `tr -d ' '` or compares numerically.
- GNU-only `sed -i` with no suffix argument appears in `pr_args.sh --self-test`, at
  `tools/audit/seat/pr_args.sh:842` and `:935`. BSD `sed` would take the expression as the
  backup suffix. This is a latent instance if a macOS seat runs that self-test. The seat did
  not run it on macOS, and nothing in the tree shows a macOS seat running it. CI runs it on
  Linux (`governance.yml:415`).
- `readlink -f` appears once, at `tools/audit/seat/cloud-setup.sh:63`. That script is
  Linux-only.
- `timeout` appears at `prepr.sh:4107`, inside an arm. macOS has no `timeout` unless coreutils
  is installed. The seat did not test whether the macOS seat has it; prepr's self-test reaches
  that arm, so a macOS lane answers the question.
- The neighbouring macOS divergence, bash 3.2's empty-array-under-`-u` (`34f200999`), already
  has a static Linux-side barrier, `bare_array.py --check`. That is the precedent for a check
  of one divergence. It is not a barrier for the class.

## 3. Process state: (c), the process was followed and did not produce the intended result

The process exists. `governance.yml:412` runs `prepr.sh --self-test` in `instrument-self-tests`
whenever `selftest_scope.py` selects `prepr`, and on every push to main. It ran green on (a)'s
and (b)'s heads, and both merged. For (c), the fixer followed `fixer.md`: the handoff carries a
null control for the very hazard (`the padding wc stub pads its count`), and that control
passed on the Linux host where the fixer ran it.

It did not produce the intended result because the unit is wrong. `instrument-self-tests` is
`runs-on: ubuntu-latest` (`governance.yml:271`), no workflow under `.github/workflows/` runs on
macOS, and the cloud seats are Linux. The only host that executes the self-test on macOS is
the operator's seat. Commit `8132eb313` ("a fixer's prepr is not repeated at open or update",
P386) says the macOS host does not re-run the fixer's prepr for the fixer's own change at open.
So a host-divergent arm first runs on macOS at a later open, which is the most expensive point,
because it blocks the opener.

Rejected states:

- Not (a): a check for the property existed; it ran on the wrong host. `root-cause.md` §2
  classes a check present in CI but absent from the path that needed it as (c).
- Not (b): no rule required a macOS run, and the fixer's run was obeyed and green.
- Not (d): the seat shim landed in `e3860e5b6` on 2026-10-03, and `ref_privacy.py`'s
  self-test has routed around it since `20b642bb3` on 2026-10-16. Both predate the instances,
  so no precondition changed under the process.

A firmer instruction such as "remember BSD `wc` pads" would have failed (c) outright. The fixer
of (c) knew that `wc` pads; the emulation they built could not reach their own stub.

## 4. Cost test

Unit: wall-clock per occurrence, over a 30-day window, which stands in for the release cycle.

- **cost(defect):** the brief's measured opener holds are (b) 70 min and (c) 75 min, mean
  72.5 min. The hold for (a) was not measured; #3343's body was pushed at 19:30 and the PR
  merged at 23:47 the same day, which bounds the hold at most and does not measure it.
- **P(recurrence):** the measured frequency is 3 instances in round 10 (2026-11-08,
  -11, -12) and zero other prepr-self-test macOS failures in the 30 days since 2026-10-13, per
  `git log --since=2026-10-13 -i -E --grep='macos|darwin|bsd' -- tools/ .claude/hooks`. That is
  3 per 30 days, so 3 × 72.5 = **217.5 min per 30 days** of opener blocked.
- **cost(countermeasure, recurring):** a macOS job runs on every PR that selects `prepr`. The
  lower bound on that set is the 45 first-parent merges that touched `tools/pr/prepr.sh` in the
  same 30 days. The selection set is larger, because it also reads every file in the prepr
  closure. The job runs in parallel with the Linux jobs, so its standing wall-clock is
  `max(0, T_mac − T_critical)` per selected run. The self-test alone measured 386–397 s here;
  `T_mac`, which adds runner queueing and the seat venv build, was not measured. The
  **break-even is 217.5 / 45 = 4.8 min added to the critical path per selected run**, and it
  falls as the selection set grows.

**Verdict:** the test cannot be closed with the numbers in hand. It passes only if the lane PR
measures `T_mac` against `instrument-self-tests`' duration on the same heads and the added
critical-path time is under about 4.8 min per run. The class owes a barrier regardless: three
instances in one round makes it an audit class under `defect-root-cause.md`, and the cost test
here picks the barrier's form, not whether one is built. GitHub's macOS minute billing
multiplier is money, not wall-clock. It falls outside the unit and is the owner's call.

## 5. Countermeasure: the P684 lane is the right form, but only with three conditions the triage text does not state

R10-PREPR-DARWIN-SELFTEST-LANE puts a path-filtered macOS CI job running
`prepr.sh --self-test` in front of the merge. That changes the unit, which is what state (c)
calls for, and it covers the BSD userland open-endedly. That matters because the class search
found a latent `sed -i` divergence that no enumerated emulation names.

The alternative is a Linux emulation step, the bind-mount plus shim harness of §1, at measured
~390 s per run in the job's background slot. It reached all three instances. It covers only the
divergences someone has enumerated, so it is a check of known shapes, not a class barrier.

**As stated in the triage, the lane would pass instance (a).** A stock GitHub macOS runner has a
plain `python3` and no seat shim, so the planted-`HOME` arm never meets a shim. The lane must
also do the following:

1. **Reproduce the seat, not just the OS.** Build the seat venv with `seat_venv.sh`, install the
   shims with `seat_venv.sh --install-shims <dir>`, put that directory first on `PATH`, and
   leave `HPO_STATE_DIR` unset. Invoke prepr as the opener's path invokes it, with the same
   `bash`: macOS `/bin/bash` is 3.2.
2. **Selection by the measured read set, not a hand path list.** Run when `selftest_scope.py`
   selects `prepr` (`selftest_closures.json`'s `prepr` entry), and on every push to main, as
   `instrument-self-tests` does. Make it a required check when selected; an advisory job is not
   a barrier.
3. **Host null controls inside the job**, so that it cannot go green on a host that lost the
   divergence:
   - `[ "$(printf 'x\n' | wc -l)" = "       1" ]`;
   - `python3 -c 'import sys; print(sys.executable)'` resolves under `$HOME`;
   - the self-test's `N passed, 0 failed` line must be present, with N equal to the Linux
     count at the same head, so that a Darwin skip cannot turn green.

**What the lane must demonstrate.** It needs `workflow_dispatch` runs on macOS at these heads,
each with its self-test summary line in the lane's PR body:

- **Red, each on the named arm in §1:** `cb5512741638029289deb392b30bc246fa667387` for (a),
  `046736a49` for (b), and `1386441425905fd0d7bb0571f1bac61ff5d7777b` for (c).
- **Green:** `89daf6c7398d91d567aa229efcd310d8e98cd790` for (a) fixed, and
  `c8780ea33db1c31ff1d38144c70af3d1b3f25eda` for (c) repaired. Instance (b) has no fixed head
  of its own; the repaired head in this row is its fix.
- **Measured:** `T_mac`, with that run's `instrument-self-tests` duration as the cost test's
  missing term.

If the macOS lane fails the 4.8 min break-even, the Linux emulation step of §1 is the
fallback. It must be recorded as a known-shape check, with the `pr_args.sh` `sed -i` sites
named as uncovered.

## Figures

- Self-test results: `bash tools/pr/prepr.sh --self-test` per head in §1. Logs are in the
  seat's scratch and were not pushed.
- Instance frequency over 30 days: `git log --no-merges --since=2026-10-13 -i -E --grep='macos|darwin|bsd' --format=%h b737e88 -- tools/ .claude/hooks`.
- PRs touching prepr in 30 days: `git log --merges --first-parent --since=2026-10-13 --format=%h b737e88 -- tools/pr/prepr.sh | wc -l` printed 45.

## Forward-carry

- The lane's three conditions and its demonstration heads (§5), and the finding that a
  `PATH`-level `wc` stub cannot emulate a BSD host for a stub that calls `/usr/bin/wc` (§1).
  Carry: R10-PREPR-DARWIN-SELFTEST-LANE
- The latent BSD `sed -i` sites at `tools/audit/seat/pr_args.sh:842` and `:935`, which are
  unverified on macOS. Carry: R10-PREPR-DARWIN-SELFTEST-LANE

## Friction

- This seat is a probe and posts nothing, so the `Root cause` section for the qualifying issue
  is owed by the orchestrator, from this body. Carry: dismissed: a probe's return is its body,
  per the brief
