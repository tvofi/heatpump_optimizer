HOTFIX r10-hotfix-mutant-run-darwin. Since #3475, `tools/audit/seat/mutant_run.py` lists `/proc` in `family()` and `_reap()`. macOS has no `/proc`, so every run there raised `FileNotFoundError`, `tools/pr/prepr.sh --self-test` failed its `mutants_line` fixtures on the orchestrator's macOS host, and every pull request opened from that host was refused.

The fix has two halves.

**The readers.** One process-table reader, `_ptable()`, returns `(pid, state, ppid, pgrp, session)`. It lists the procfs root; on `FileNotFoundError` it reads `ps -axo pid=,stat=,ppid=,pgid=`, takes the session from `os.getsid`, and drops the `ps` process's own row. `family()` and `_reap()` both read that table. The environment-token read is `_carries()`, False where no `<root>/<pid>/environ` exists. A `ps` that fails raises `OSError`, never an empty table, which would switch the fork cap off silently.

**The platform is injected, not patched.** The procfs root is `PROCFS[0]`, taken from `MUTANT_RUN_PROCFS` (default `/proc`); a root that does not exist is a host without procfs. The first seat's self-test emulated macOS by monkeypatching `os.listdir` and `Path.read_text`/`read_bytes`, and its null control read the host's real `/proc`: on macOS that control could not hold (2 of 64 checks failed). The self-test now reads the table three ways on every host: with no procfs root, through a faked procfs root it writes from the live table (`<pid>/stat`, `<pid>/environ`), and through the host's own `/proc`. Where the host has none, that third leg is one printed, counted `skip`. A staged `ps` on PATH supplies the rows no live table yields on demand: a row whose session `os.getsid` refuses, a line that is no row, a `Zs` zombie in the command's group. Two driver runs pin that the root the environment names is the one the driver reads.

Skips are counted. Every case the host cannot run goes through one `skip()` and the self-test prints `mutant_run self-test: <n> skipped` above the summary line, whose text `governance.yml` greps and which is therefore unchanged in shape. A check pins the count against the two host facts it depends on: four without a child subreaper, one without `/proc`, none on a Linux host with both.

Carry 0 of the roster group (the orchestrator's macOS run: at fdfd99d535 the driver's self-test fails 2 of 64 checks on Darwin, both null controls that need a real proc filesystem; owed, a stated precondition and a skip named in the tally, or an emulated table, with no skip hiding a Linux failure) is built in this pull request, both ways: the table is emulated through the faked root on every host, and the host-`/proc` leg states its precondition and is a counted, printed skip where the host has none. Re-measured on this Mac: 64 checks, 2 failed at fdfd99d535; 71 checks, 0 failed, 5 skipped at this head. The Linux half of its control (the host leg runs unskipped and the tally reads 0 skipped) is Linux CI's to confirm.

Alternatives considered:
- Skip the two null controls on a host without `/proc` and stop there. It lost: the procfs readers would then run nowhere but Linux CI, and the defect this hotfix repairs is exactly a reader one platform never ran.
- Keep the monkeypatch and add a fake `/proc` by patching more calls. It lost to one injectable root: the production readers take the root as data, so no test patches the standard library.
- The brief's candidate patch (a second `ps` loop inside `family()`, `_reap()` returning nothing). It lost at the first seat: it duplicated the descendant walk, `ps` counted itself as a child, and a refused `getsid` dropped the whole row.

Scope beyond the brief's two files, by the orchestrator's ruling of 2026-11-12: `dev/audit/harnesses/mutant_run_diff_shards.py` (the shard runner the survivor figures below came from, fixer.md step 18) and its one `tests/closures.json` inert-read entry, written by `python3 tools/pr/ci_predict.py --apply-inert`.

## Head

b49a16c2f7a11194e9eb2662d3e992c864c6fb7d. Every figure below was measured at its parent 3dccd18a95617b752a1be6fce24f5dc7df3bd57f, and so was the `Prepr:` receipt (full `tools/pr/prepr.sh`, rc 0, at 3dccd18a95); the delta to this head is one file, `dev/audit/harnesses/mutant_run_diff_shards.py`, which now finds the checkout with the canonical `repo_root` walk in place of `Path(__file__).resolve().parents[3]`. That delta answers a red the scoped gate found after the first handoff: `tests/harness_headers.py`'s inline scan refused the depth root (`harness_headers.inline_scan()` rc 1 at 3dccd18a95, rc 0 at this head). No full prepr was re-run at this head. 3dccd18a95 was measured on macOS (Darwin, arm64) with origin/main 19baca76181cb019d9b1cfd93ee6bc0a08e20047 as merge base, at 2026-11-12T17:35Z. `tools/audit/seat/mutant_run.py` is byte-identical between d823c55e4d, where the mutant figures were taken, 3dccd18a95 and this head: `git diff --quiet d823c55e4d HEAD -- tools/audit/seat/mutant_run.py && echo IDENTICAL` prints `IDENTICAL`.

## Mutation proof

Command: `python3 -I tools/audit/seat/mutant_run.py --spec <spec> --cmd '<the self-test, its output kept per run>'`, the spec being the twelve edits below. Output: `SURVIVED NULL`, then one line per mutant; the failing checks are from the kept output of the same runs, on macOS.

| mutant | edit | result | checks that go red (macOS) |
|---|---|---|---|
| `procfs_leg_reads_ps` | `os.listdir(PROCFS[0])` lists a path that never exists, so the table is always `ps` | KILLED | faked root: `a failing ps is never read: the table is procfs`; `a driver whose MUTANT_RUN_PROCFS names an empty root sees no process` |
| `no_procfs_leg_no_ps_fallback` | `except FileNotFoundError:` becomes `except NotADirectoryError:` | KILLED | the no-procfs leg ends in `FileNotFoundError` at its first `family()` call, rc 1, no summary line |
| `no_procfs_leg_failed_ps_is_empty_table` | `if ps.returncode:` becomes `if False:` | KILLED | no procfs: `a failing ps refuses (OSError), never an empty table that turns the cap off` |
| `host_leg_never_skipped` | the skip predicate of the host-`/proc` leg becomes `if False:` | KILLED | host leg: `found by its token (the environ leg)`, `a failing ps is never read`; and `skip: each case this host cannot run is counted, once` |
| `skip_not_counted` | `skips += 1` becomes `skips += 0` | KILLED | `skip: each case this host cannot run is counted, once` |
| `env_root_ignored` | `PROCFS` no longer reads `MUTANT_RUN_PROCFS` | KILLED | `a driver whose MUTANT_RUN_PROCFS names an empty root sees no process` |
| `zombie_state_not_sliced` | `state[:1]` becomes `state` | KILLED | no procfs: the staged-`ps` check (`a Zs zombie in the command's group is not counted`) |
| `refused_getsid_keeps_last_session` | `session = None` becomes `pass` | KILLED | no procfs: the staged-`ps` check (`a row whose session os.getsid refuses takes no other row's`) |
| `reap_collects_nothing` | `_reap`'s predicate becomes `if False:` | KILLED | `_reap() collects a dead child it does not skip`, with no procfs and through the faked root |
| `token_matched_as_substring` | `mark in env.split(b"\0")` becomes `mark in env` | KILLED | faked root: the session, ppid and token arms (the near-miss token is found) |
| `ps_counts_itself` | `if int(pid) == ps.pid:` becomes `if False:` | KILLED | `family() finds the driver's descendants by ppid, zombies excluded`, with no procfs and through the faked root (whose table is written from `ps` here) |
| `stat_split_after_first_paren` | `stat.rindex(")")` becomes `stat.index(")")` | KILLED | faked root: the session, ppid, token and `_reap` arms (every faked comm holds `) `) |

A mutant per leg: `no_procfs_leg_*` fail the no-procfs leg, `procfs_leg_reads_ps`, `token_matched_as_substring` and `stat_split_after_first_paren` fail the procfs leg through the faked root, and `host_leg_never_skipped` shows what the skip guards on a host without `/proc`. On Linux the host leg runs unskipped, and the same procfs mutants are expected to fail it there; that is Linux CI's to confirm.

Failing test first: at the merge base 19baca7618 `python3 -I tools/audit/seat/mutant_run.py --self-test` on this Mac prints 4 `ok` lines and 5 `FAIL` lines and then ends in a `FileNotFoundError` traceback with no summary line, rc 1. At the first seat's tip fdfd99d535 it prints `64 checks, 2 failed`, both `no-procfs: with /proc present (null control)` arms (the environ leg, and a failing `ps` never read).

## Unpinned sites

Measurement: the diff's mutants are `mutant_run.py`'s own `diff_mutants` over `19baca7618...HEAD`, which is exactly the lines the two seats added (the narrowest base there is); the command is `python3 -I tools/audit/seat/mutant_run.py --self-test`. One self-test takes about a minute on this host, so the full list was run in four shards with `dev/audit/harnesses/mutant_run_diff_shards.py`, which calls the driver's own `added_lines`, `diff_mutants`, `Workspace` and `run_cmd`; no full serial `--diff` pass was run. `tools/pr/prepr.sh`'s diff-mutant step (`MUTANT_CMD`, the serial driver, the first 40 mutants) is the cross-check. The survivor triage ledger cannot hold these: `tests/mutation_table.py`'s key grammar admits only `custom_components/` anchors, so each survivor is answered here.

Result on macOS at d823c55e4d: 128 mutants, 92 KILLED, 36 SURVIVED, 0 FORKCAP. All 36 are in `tools/audit/seat/mutant_run.py`'s self-test half (line 640 on); no survivor is in a production reader (`_ptable`, `_carries`, `family`, `_reap`, `PROCFS`). The first seat reported 16 on Linux at fdfd99d535; the count is higher here because this seat added checks, and every added `check(...)` call is one deletable statement. One of the first pass's survivors was a real gap, now closed: deleting `session = None` in `_ptable` let a `ps` row whose `os.getsid` is refused keep the previous row's session; the staged-`ps` check kills it (`refused_getsid_keeps_last_session` above).

Each line is `line OPERATOR`, the mutated statement, and its disposition.

Unmeasured on macOS (Linux-only arm), 12. The cloud reviewer measures these on Linux; none is claimed killed or equivalent here:
- `656 CONST_SWAP` `prev = _subreaper(2)` in `_can_subreap`: unmeasured on macOS (Linux-only arm); `prctl` is absent here, so the probe returns -1 whatever its argument.
- `657 CMP_BOUND` `return prev > 0 and ...`: unmeasured on macOS (Linux-only arm); `prev` is -1 here.
- `657 CONST_SWAP` `return prev >= 1 and ...`: unmeasured on macOS (Linux-only arm); same line.
- `1026 STMT_DEL` `name = f"forkcap: a daemon that ..."`: unmeasured on macOS (Linux-only arm); here only the `skip` line reads `name`, and no check reads a skip line's text.
- `1030 CALL_DEL` `write_spec([bad])`: unmeasured on macOS (Linux-only arm); the daemon cases are skipped here.
- `1031 STMT_DEL` `rc, out, _ = drive(...)` of the daemon cases: unmeasured on macOS (Linux-only arm).
- `1033 CONST_SWAP` `capture_output=False` on the daemon cases' `pgrep`: unmeasured on macOS (Linux-only arm).
- `1033 STMT_DEL` the same `left = subprocess.run(...)`: unmeasured on macOS (Linux-only arm).
- `1034 CALL_DEL` `check(name, rc == 0 and not left)`: unmeasured on macOS (Linux-only arm).
- `1034 CONST_SWAP` `check(name, rc == 1 and not left)`: unmeasured on macOS (Linux-only arm).
- `1036 CALL_DEL` `os.kill(int(pid), signal.SIGKILL)`: unmeasured on macOS (Linux-only arm).
- `1070 CONST_SWAP` `skips == (1 if _can_subreap() else 4) + ...`: unmeasured on macOS (Linux-only arm); the mutated arm is the host with a subreaper.

A deleted assertion, 12. The mutant removes a `check(...)` call; no other check observes that a check is missing, and the summary line's count is not pinned (`governance.yml` reads `[1-9][0-9]* checks`). Not equivalent: each is the self-test made weaker, answered by the proof mutant that turns the same assertion red while it is present:
- `719 STMT_DEL` `procfs: a Linux host has one, so its leg below is not skipped there`: a statement about the host; no proof mutant reddens it on macOS, where it holds because the host has no `/proc`.
- `732 STMT_DEL` `the premise: the exited child is still a zombie when the table is read`: red only if the child is no zombie within 5 s; no proof mutant reddens it.
- `761 STMT_DEL` the staged-`ps` check: red under `zombie_state_not_sliced` and `refused_getsid_keeps_last_session`.
- `763 STMT_DEL` `family() finds a command by its session`: red under `token_matched_as_substring` and `stat_split_after_first_paren`.
- `765 STMT_DEL` `family() finds the driver's descendants by ppid, zombies excluded`: red under `ps_counts_itself`.
- `767 STMT_DEL` `a process outside the command's session is found by its token`: red under `token_matched_as_substring` and `host_leg_never_skipped`.
- `770 STMT_DEL` `_reap() collects a dead child it does not skip`: red under `reap_collects_nothing`.
- `772 STMT_DEL` `a failing ps ...`: red under `procfs_leg_reads_ps` and `no_procfs_leg_failed_ps_is_empty_table`.
- `964 STMT_DEL` `a driver whose MUTANT_RUN_PROCFS names an empty root sees no process`: red under `env_root_ignored` and `procfs_leg_reads_ps`.
- `967 STMT_DEL` `a driver whose MUTANT_RUN_PROCFS names no directory caps the same chain from ps`: on macOS this run takes the host's own path, so no proof mutant separates it here; on Linux it is the one driver-level run of the `ps` path.
- `1009 CALL_DEL` `subreaper: a Linux host has one, so no case below is skipped there`: a statement about the host, as line 719.
- `1069 STMT_DEL` `skip: each case this host cannot run is counted, once`: red under `skip_not_counted` and `host_leg_never_skipped`.

Timing only, in `_zombie`'s poll loop, 3. Equivalent in outcome: the loop waits for `true` to exit unreaped, and the child is a zombie on the first or second poll whatever the bound or the pause:
- `671 CONST_SWAP` `for _ in range(51):`
- `674 CALL_DEL` `time.sleep(0.1)` deleted
- `674 CONST_SWAP` `time.sleep(0.2)`

Not reached on a passing tree, 2. `_zombie`'s closing `return False` runs only when the child never became a zombie, which is the failure the premise check reports:
- `675 CONST_SWAP` `return True`
- `675 RETURN_DEL` `pass`

The staged `ps` removed from under its check, 4. Each leaves the staged-`ps` check reading the live table, where `family(lone.pid, "")` is `[lone.pid]` as well; a weaker self-test, not a production change. The check's force while the stage is in place is the two proof mutants above:
- `748 GUARD_OFF` `if False:` for `if not procfs:` (the whole staged block)
- `750 CALL_DEL` `stale.wait()` deleted (the stale pid then still answers `os.getsid`, with a session that is not the command's)
- `755 STMT_DEL` the staged `ps`'s `chmod(0o755)` (PATH lookup then passes it over)
- `756 STMT_DEL` the staged directory's `os.environ["PATH"]` assignment

An assertion weakened, 1:
- `771 CONST_SWAP` `dead.pid not in {row[1] for row in _ptable()}`: the set becomes states, never a pid, so the check cannot fail; its force is `reap_collects_nothing`, which turns the unmutated check red.

Cleanup, 2. Equivalent in outcome: each `sleep 30` child then exits by itself, and no check reads it:
- `777 CALL_DEL` `p.kill()`
- `778 CALL_DEL` `p.wait()`

`tools/pr/prepr.sh`'s own diff-mutant step at this head (the serial driver, `MUTANT_MAX` 40) is the cross-check: its `diff mutants` line is quoted under Figures.

## Null control

- With the injection removed the old failure returns: mutant `host_leg_never_skipped` runs the host-`/proc` leg on this Mac and fails the same two arms the first seat's tip failed (table under Mutation proof).
- The faked procfs root and the staged `ps` are read only inside their blocks: the checks after each block read the live table again (`_reap() collects a dead child it does not skip` reads it and passes on all legs).
- An empty procfs root is the control for the driver-level run: the same chain, cap and command print `FORKCAP ret_hi` on the host's table and `SURVIVED ret_hi` when `MUTANT_RUN_PROCFS` names an empty directory.
- The summary line `governance.yml` greps keeps its shape: the last line of the self-test's output is `mutant_run self-test: 71 checks, 0 failed`, and the `skipped` line is the one above it.

## Figures

<!-- figure-block: scope-line mb=19baca76181cb019d9b1cfd93ee6bc0a08e20047 head=b49a16c2f7a11194e9eb2662d3e992c864c6fb7d -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->
- `python3 -I tools/audit/seat/mutant_run.py --self-test` on macOS at the merge base 19baca7618: 4 ok, 5 FAIL, then a `FileNotFoundError` traceback, rc 1.
- `python3 -I tools/audit/seat/mutant_run.py --self-test` on macOS at fdfd99d535: 64 checks, 2 failed.
- `python3 -I tools/audit/seat/mutant_run.py --self-test` on macOS at this head: 71 checks, 0 failed, 5 skipped (one host-`/proc` leg, four child-subreaper cases, each printed with its reason).
- `bash tools/pr/prepr.sh --self-test` on macOS: 537 passed, 5 failed at the merge base (the orchestrator's measurement, the five being `mutant_run` reading `/proc`); 542 passed, 0 failed at this head (the `self-test` line of this head's `tools/pr/prepr.sh` run).
- `python3 tools/audit/seat/mutant_run.py --diff 19baca76181cb019d9b1cfd93ee6bc0a08e20047...HEAD --list`: 128 mutants. Run in four shards by `python3 dev/audit/harnesses/mutant_run_diff_shards.py 19baca76181cb019d9b1cfd93ee6bc0a08e20047...HEAD <i> 4`: 92 KILLED, 36 SURVIVED, 0 FORKCAP, each survivor listed under Unpinned sites.
- `MUTANT_CMD="python3 -I tools/audit/seat/mutant_run.py --self-test" bash tools/pr/prepr.sh <body>` at this head: rc 0, `self-test 542 passed, 0 failed`, and its `diff mutants` line reads 8 survivors among the first 40 mutants of the serial driver. Those 8 (`656 CONST_SWAP`, `657 CMP_BOUND`, `657 CONST_SWAP`, `671 CONST_SWAP`, `674 CALL_DEL`, `674 CONST_SWAP`, `675 CONST_SWAP`, `675 RETURN_DEL`) are the same set as the shard pass's survivors among mutants 0 to 39: a `diff` of the two sorted lists is empty.
- `python3 tools/pr/ci_predict.py`: no closures, fast, governance or instrument red predicted, after `--apply-inert` wrote the harness's inert-read entry.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (the `merged structure` line of `tools/pr/prepr.sh`).

What only Linux CI can confirm, none of which this macOS seat measured:
- the host-`/proc` leg of `_procless_checks` (skipped here, counted), i.e. that the real procfs readers pass the six arms the faked root passes here;
- the four child-subreaper cases (skipped here, counted) and the `skips == 0` arm of the skip-count check;
- the 12 mutants listed `unmeasured on macOS (Linux-only arm)` under Unpinned sites;
- the `ps` leg against Linux procps output (`stat` there is a multi-letter state as on macOS; the first seat ran that leg green on Linux at fdfd99d535, before this seat's changes);
- the scoped closure recordings: off Linux `tools/pr/prepr.sh` step 6b leaves them to CI's `closures` and `closures-autofix`, and no `tests/derive_closures.sh` run, full or `--single`, was made here (the diff adds no selectable script).

## Red checks

- `tests / fast (3.14)`: read at pull-request head 6b16a9f896 (which carries 3dccd18a95) it was still in progress, so this is the red the scoped gate predicts there, not one read from CI: `tests/harness_headers.py` fails `every inlined walk matches the canonical helper and no depth root remains` with `FAIL depth seams: dev/audit/harnesses/mutant_run_diff_shards.py:29: ROOT = Path(__file__).resolve().parents[3]`. Cause: the harness added in this pull request took its root by depth. Fixed at this head (rc 1 to rc 0, above). Cheaper detector: `harness_headers.inline_scan()` on a diff that adds or edits a file under `dev/audit/harnesses/`; it takes seconds, and neither `tools/pr/prepr.sh` nor `tools/pr/ci_predict.py` runs it today, so the only detector before CI is the scoped gate's `run_always` tail. This seat ran that gate after the handoff, which is the process slip.

The red this hotfix answers was not a CI check: it was `tools/pr/prepr.sh --self-test` on the macOS host, which Linux CI cannot see. The cheaper detector is now in the tree: the self-test's no-procfs leg and its `MUTANT_RUN_PROCFS` driver run execute the macOS path on Linux CI in `instrument-self-tests`, at a few seconds per run, so a reader that works only with `/proc` fails there before it reaches a macOS seat.

The first seat's hold, `closures failed while being recorded: tests/entities.py`, did not recur here: on macOS step 6b records nothing. Its body named the cause it measured on Linux (the recorded script inherits `HPO_GATE_PRIORITY=2` from `prepr.sh`, and two gate-lease priority checks in `tests/entities.py` fail under it, at main with no diff); that is not this diff's and was not re-measured on this host.

## Forward-carry

none

## Friction

none
