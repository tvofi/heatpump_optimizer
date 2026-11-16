R11-PRE-PRODUCT-READS part 1 of 2 (design `design/R11-PRE-PRODUCT-READS` at 8daf118368, `Design review: approve` at a08d8f47c9): `tools/audit/product_reads.py`, which reads decision 0018's `operation` and `generality` off a seat's cell ledger and counts a row only on a witness the read produced itself; decision 0018 names this group as the builder of `regret`, `operation` and `generality`'s examined count, and R11-PRE-ROUND-METRICS for `escapes` and `unowned` (design 3.6). Part 2 (`regret`: the same-information oracle and the install-day record) is the approved plan's second pull request. No production file and no file under `tests/` other than `tests/layout.json` is edited. Universes are imported from `tools/audit/enumerate.py` (R11-PRE-BRIEFS-CENSUS, merged as #3625), never enumerated a second time.

How each read witnesses, per the design:
- `operation` (3.2): each cited script runs unedited under a launcher (wrappers on `harness.Results.check`, `FakeServices.async_call` installed as a plain function per n1, `FakeEntry`, `pump_arbiter.apply`, the coordinator's constructor, and `log_held` in each importing module's namespace through a post-import hook), twice as it is, then once per cited (site, cell state) with the payload from that site perturbed **only in `apply` passes whose recorded state is the cell's** (v2-1). The state is read off the plan the coordinator holds at `apply` entry by plain indexing; a token with no table entry prints `state not recorded`. Writes outside every pass are printed per site, never witnessed (v2-2).
- v2-3 answered: `arbiter_inputs()` is not read-only for this read: it calls `pump_arbiter.live_power_kw`, which reads through `InputReader` (`inputs.py` binds `log_held`), so an extra call could record a hold the code under test never made. The wrapper reads `coord._optimization_result` and `coord.effective_config` (else `_config`) directly.
- `generality` (3.3): a level row counts only when the read's own run, with that level's observable switched to the next level of its axis in the recorded configuration, turns the check FAIL or changes its detail; a pair only when both its levels are witnessed in one configuration of one script (`--pairs-out` writes them in `enumerate.py d12-cells --pairs --ledger`'s format). Bundle and install-report rows are printed and never counted.
- One departure, raised here: `restart` is read as "not the first coordinator **built** on its entry object" for the real class, and, for a test's own fake coordinator that is never built through it (e.g. `tests/guard_pins.py`'s `Coord`), "not the first seen at `apply`" on that entry object. The design names construction only; with construction only, every fake-coordinator pass would print `state not recorded` and F5's checks could never be witnessed. Keyed on the entry object, not `entry_id`, because `FakeEntry()` defaults every entry to one id.
- At this base `d16-writes --cells` prints duty x {running, restart, upgrade, unavailable} (the census formula, NEW-DIMENSIONS not merged): `upgrade` prints `state not recorded`; the plan-state rows (idle, dhw-only, both, partial, full, min-cold-tank, baseline) are in the table and pinned by direct arms, read the day the formula changes (n10).


## Head

e924e4987894c2e656116ff51d7652019ecbfb80. Merge base 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c; origin/main e352724335c136b65562cd3e71f728549ad04a82 at 2026-11-16T15:19:42Z, `git merge-tree --write-tree origin/main HEAD` reports no conflict. Repair of round 1's block at 3beb89a81a: four commits on it; the live reads in `## Figures` ran at the first of them (832005745a, the arms and the three removed redundancies); `git diff --stat 832005745a e924e49878 -- tools/audit/product_reads.py` touches only the self-test (two arms and their helpers).

## Mutation proof

Rule: the tracked driver over every added line of the diff, `python3 tools/audit/seat/mutant_run.py --diff 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c...HEAD --cmd 'python3 -I tools/audit/product_reads.py --self-test' --report-only --max-mutants 700`, at e924e49878 (the verdict's command, unchanged); and the reviewer's targeted spec (`evidence/mutants_reviewer_spec.json` on `verdict/3665`) through `mutant_run.py --spec`.

Reviewer spec, at e924e49878, its NULL surviving so the command is sound:

~~~text
SURVIVED NULL
KILLED pair-same-axis-guard-off
KILLED operation-fail-at-head-branch-off
KILLED target-compare-always-plan
KILLED perturb-site-restriction-dropped
KILLED unlisted-writer-off
KILLED hold-reached-before-state-check
KILLED presence-carried-ignores-level
rc=0
~~~

`moved-base-ok-dropped` is not in that run: its guard was removed (below), so its `old` text occurs 0 times and the driver refuses the whole spec on it (`mutant_run: refusing: mutant moved-base-ok-dropped: old text occurs 0 times`); the other seven are the spec's own entries, unedited. The redundancy the reviewer named (`:415` and `moved`'s `a["ok"]`, each alone equivalent) is gone: `moved()` is called only on a check that passed at the head, because both reads print `FAIL at the head` first, and that verdict is pinned by `planted: a FAIL at the head` in each read.

Arms added for the review's named survivors (self-test now 79 arms, each killing the named mutant in the driver run below unless listed under `## Unpinned sites`): an `absent` level row (`:194`/`:195`, presence-carried-ignores-level); the real coordinator class built twice on one entry and the second applied first (`:257`-`:264`, the construction ordinal) with `effective_config` differing from `_config` (`:228`); six malformed ledger rows (wrong column count both ways, no `::`, a source outside `census.SOURCES`) and the refusal's line number after a comment line (`:325`, `:326`, `:329`, `:330`); a profile configuration after an entry, between it and the check (`:491`/`:492`); a second reachable write site (perturb-site-restriction-dropped); a hold cited for `duty=off` (hold-reached-before-state-check); two keys of one axis carrying two levels in one configuration (pair-same-axis-guard-off); a `target=differs` write and a write with no set-point (`:456`-`:465`); an aliased `svc.async_call` the census does not list (unlisted-writer-off, `:440`-`:450`); writes and holds outside every pass; a pass with no `now` (`:221`/`:223`); a FAIL at the head and an unknown check in each read (`:415`/`:416`, `:541`-`:544`); a launcher that dies before writing its record (`:349`); the script's own raise printed with the unknown check (`:291`); the recorders keeping each wrapped return value and `sys.argv` (`:166`, `:250`, `:284`); the pair rows printed in the universe listing and the per-script lines (`:563`/`:564`, `:572`/`:573`); a read with no `--ledger` exiting 2 and a read that prints its RESULT exiting 0 (`main`).

Removed instead of pinned, each a redundancy: `w["perturbed"]` (`:182`, never read); `rec["passes"]`' `hass` popped before the record is written (`:292`/`:293`), now kept in a list beside the passes; the pair sort (`:559`), since `itertools.combinations` of a sorted set yields ordered pairs.

Every SURVIVED line the driver printed at e924e49878 (`rc=0` under `--report-only`):

<details><summary>driver output</summary>

~~~text
SURVIVED tools/audit/product_reads.py:34 CONST_SWAP  sys.path.insert(1, str(Path(__file__).resolve().parent))
SURVIVED tools/audit/product_reads.py:38 CONST_SWAP  RUN_TIMEOUT_S = 901
SURVIVED tools/audit/product_reads.py:76 CONST_SWAP  return {k: (v + 14.0 if _num(v) else f"{v}~perturbed" if isinstance(v, str) and k != "entity_id" else v) for k, v in data.items()}
SURVIVED tools/audit/product_reads.py:107 CMP_BOUND  elif _num(p) and 0 <= s < float(p):
SURVIVED tools/audit/product_reads.py:128 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:138 CONST_SWAP  short = name.rsplit(".", 2)[-1]
SURVIVED tools/audit/product_reads.py:147 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:153 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:155 CONST_SWAP  sys.path[:] = [str((repo / spec["script"]).parent), str(repo / "tests")] + [x for x in sys.path[2:] if x != str(Path(__file__).resolve().parent)]
SURVIVED tools/audit/product_reads.py:193 GUARD_OFF  elif False:
SURVIVED tools/audit/product_reads.py:245 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:246 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:269 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:283 CONST_SWAP  sys.meta_path.insert(1, _Hook(patches))
SURVIVED tools/audit/product_reads.py:344 CONST_SWAP  capture_output=False, text=True, timeout=RUN_TIMEOUT_S)
SURVIVED tools/audit/product_reads.py:370 CONST_SWAP  with concurrent.futures.ThreadPoolExecutor(max(2, self.jobs)) as ex:
SURVIVED tools/audit/product_reads.py:408 CMP_BOUND  at_site = [e for e in evs if e["site"] == r["site"] and (c is None or e["seq"] <= c["seq"])]
SURVIVED tools/audit/product_reads.py:439 CONST_SWAP  rec = runs[key(s, 1)]
SURVIVED tools/audit/product_reads.py:524 CMP_BOUND  before = [i for i, cfg in enumerate(base["configs"]) if c and cfg["seq"] <= c["seq"] and carried(cfg, o, r["level"])]
SURVIVED tools/audit/product_reads.py:570 CONST_SWAP  rec = runs[key(s, 1)]
SURVIVED tools/audit/product_reads.py:703 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:718 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:728 CONST_SWAP  arms, fails = 1, []
SURVIVED tools/audit/product_reads.py:732 CONST_SWAP  arms += 2
SURVIVED tools/audit/product_reads.py:733 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:734 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:765 CONST_SWAP  out = read_operation(root, led, 5)
SURVIVED tools/audit/product_reads.py:770 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:771 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:771 CONST_SWAP  arm("null: the target half reads the plan's set-point", next(l for l in out if l.startswith(ops[1][0]) and S + "payload" in l).endswith("target=plan"), True)
SURVIVED tools/audit/product_reads.py:772 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:772 CONST_SWAP  arm("planted (i): a constant-condition check does not move", v(2), "not witnessed: the check does not move")
SURVIVED tools/audit/product_reads.py:775 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:776 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:777 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:778 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:779 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:780 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:781 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:784 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:785 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:790 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:791 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:791 CONST_SWAP  arm("planted: a set-point the plan does not hold", full[(ops[17][0], S + ops[16][1])], "moved\ttarget=differs plan=21.0 sent=22.0")
SURVIVED tools/audit/product_reads.py:792 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:792 CONST_SWAP  arm("null: a pass with no `now` reads the clock", v(18), "moved")
SURVIVED tools/audit/product_reads.py:793 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:794 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:795 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:796 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:806 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:807 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:811 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:813 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:814 CONST_SWAP  ps = {"duty": "control", "plan": True, "k": None, "plan_state": None, "ordinal": 1}
SURVIVED tools/audit/product_reads.py:815 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:815 CONST_SWAP  arm("token: baseline is a plan held and no step covering now", (token_holds("baseline", ps, None), token_holds("baseline", {**ps, "k": 1}, None)), (True, False))
SURVIVED tools/audit/product_reads.py:816 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:817 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:829 CONST_SWAP  gout = read_generality(root, gl, 5, pairs_out=po)
SURVIVED tools/audit/product_reads.py:836 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:836 CONST_SWAP  arm("null: a check on a key's presence, its level switched: witnessed", g(1), "witnessed (configuration 0)")
SURVIVED tools/audit/product_reads.py:837 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:840 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:841 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:842 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:843 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:846 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:847 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:848 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:848 CONST_SWAP  arm("null: two keys of one axis carry two levels in one configuration", (g(12), g(12)), ("witnessed (configuration 5)",) * 2)
SURVIVED tools/audit/product_reads.py:849 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:850 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:862 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:867 CONST_SWAP  next(l for l in read_generality(root, gl, 5) if l.startswith("level grid=g1\t")).endswith("no witness: no observable in the stub"), True)
SURVIVED tools/audit/product_reads.py:869 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:871 CONST_SWAP  for name, fn in (("operation", lambda: read_operation(root, led, 2)), ("generality", lambda: read_generality(root, gl, 1))):
SURVIVED tools/audit/product_reads.py:874 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:880 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:886 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:888 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:889 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:892 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:894 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:894 CONST_SWAP  return 2
SURVIVED tools/audit/product_reads.py:896 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:902 CONST_SWAP  mk = lambda s, d, f=None, n=3: NS(timestamps=[_T0 + timedelta(minutes=15 * i) for i in range(n)], power_schedule=[s] * n,
SURVIVED tools/audit/product_reads.py:903 CONST_SWAP  dhw_power_schedule=[d] * n, optimal_setpoints=[40.0] * n, duty_floor_kw=f)
SURVIVED tools/audit/product_reads.py:908 CONST_SWAP  ("no configured maximum reads no partial", mk(4.0, 0.0), {}, None),
SURVIVED tools/audit/product_reads.py:909 CONST_SWAP  ("now past the plan has no k", NS(timestamps=[_T0 - timedelta(hours=3), _T0 - timedelta(hours=1, minutes=45)],
SURVIVED tools/audit/product_reads.py:910 CONST_SWAP  power_schedule=[4.0, 2.0]), cfg, None),
SURVIVED tools/audit/product_reads.py:911 CONST_SWAP  ("no power schedule reads no state", NS(timestamps=[_T0, _T0 + timedelta(minutes=16)]), cfg, None),
SURVIVED tools/audit/product_reads.py:912 CONST_SWAP  ("dhw past its end reads 0", NS(timestamps=[_T0 - timedelta(minutes=16), _T0], power_schedule=[0.5, 0.5],
SURVIVED tools/audit/product_reads.py:913 CONST_SWAP  dhw_power_schedule=[2.0], duty_floor_kw=None), cfg, "partial")]
SURVIVED tools/audit/product_reads.py:916 CONST_SWAP  _T0 = __import__("datetime").datetime(2027, 1, 1, tzinfo=__import__("datetime").timezone.utc)
SURVIVED tools/audit/product_reads.py:929 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:943 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:944 CONST_SWAP  return int(r.stdout.strip() or -2)
SURVIVED tools/audit/product_reads.py:969 CONST_SWAP  ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
SURVIVED tools/audit/product_reads.py:975 CONST_SWAP  ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
SURVIVED tools/audit/product_reads.py:982 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:982 CONST_SWAP  return 1
SURVIVED tools/audit/product_reads.py:994 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:995 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:699 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:732 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:747 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:773 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:782 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:786 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:788 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:797 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:800 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:808 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:818 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:838 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:844 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:851 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:855 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:858 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:863 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:866 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:868 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:872 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:881 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:884 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:885 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:891 STMT_DEL  pass
rc=0
~~~

</details>

## Unpinned sites

Every survivor above, by line at e924e49878, with its disposition. All are equivalent or outside what the command can see; none is in a counted predicate.

- `:34` CONST_SWAP (`sys.path.insert(1, ...)`): equivalent; `enumerate` resolves at either index, and the launcher rebuilds `sys.path` before any script runs. Accepted by round 1.
- `:38` `RUN_TIMEOUT_S` 900 -> 901: a bound on a hung child, read by no verdict. Accepted by round 1.
- `:76` `_perturb`'s offset 7.0 -> 14.0: any non-zero offset is a different payload. Accepted by round 1.
- `:107` CMP_BOUND `0 < s` -> `0 <= s`: equivalent; `s == 0` returns `idle` or `dhw-only` two branches earlier. Accepted by round 1.
- `:128` (`token_holds`' last `return None`) and `:147` (`find_spec`'s last `return None`) RETURN_DEL: equivalent; a function falling off its end returns None.
- `:138` CONST_SWAP `rsplit(".", 2)[-1]`: equivalent; the last component is the same with any maxsplit >= 1.
- `:153` CALL_DEL `os.chdir(repo)`: equivalent under `run_script`, which starts the child with `cwd=repo`; kept for a launch from any other caller.
- `:155` CONST_SWAP `sys.path[2:]`: equivalent in measurement. With it applied, a probe planting the fixture and importing `homeassistant` in the child prints `.../tests/hastub/homeassistant/__init__.py`, and `now-none-payload` (whose wrapper imports `homeassistant.util.dt`) is ok; the stub still resolves, so no arm can separate the two.
- `:193` GUARD_OFF of the absent -> present branch: equivalent; with `from=None` the next branch's `d.get(k) == None` matches the absent key and writes it into data and options both, and the merged configuration carries the level the same. Its STMT_DEL (`data[k] = ...` deleted, the review's `:195`) is killed by `null: an absent level gains its key`.
- `:245`/`:246` (`patch_holds` on a module with no `log_held`) and `:269` (`patch_profiles` on a profiles module with no `weather`): equivalent; the mutant sets a wrapper of None that nothing calls, because the module has no such name for any code to call.
- `:283` CONST_SWAP `sys.meta_path.insert(1, ...)`: equivalent on CPython, whose `meta_path` holds BuiltinImporter, FrozenImporter, PathFinder: index 1 is still before the PathFinder that loads the package.
- `:344` CONST_SWAP `capture_output=False`: no verdict reads the child's streams (the record is the JSON file); the flag keeps a child's stderr out of the read's stdout.
- `:370` CONST_SWAP `max(2, self.jobs)`: a worker count; each run is independent.
- `:408` and `:524` CMP_BOUND `<` -> `<=` on `seq`: equivalent; checks, writes, holds and configurations draw from one `itertools.count()`, so no two `seq` are equal.
- `:439` and `:570` CONST_SWAP `runs[key(s, 1)]`: equivalent; run 1 is run 0 unchanged, and these lines count the writes, holds and configurations each run makes, which are identical in both runs of the fixture. They are printed lines; no verdict reads them.
- `main`: `:969` (`__doc__.split("\n")[1]`, argparse's description) and `:975` (`--jobs` default `or 2`) print or schedule, no verdict; `:982` (`return 0` after `_launch`, RETURN_DEL and CONST_SWAP): equivalent, `run_script` reads the child's record file and never its exit code; `:994`/`:995` (the `if __name__ == "__main__"` entry point): outside what the command can see, because with the entry point deleted `python3 -I tools/audit/product_reads.py --self-test` runs nothing and exits 0, the same shape as every other self-test entry point in that governance step; the step greps no `SELF-TEST passed` line, and changing its run text needs another re-record (757 s), so it is not changed here.
- The self-test itself (`plant` through `_exit`, lines 698-967): each survivor deletes or swaps one fixture line, arm call or helper statement and the self-test still passes. Deleting an assertion or a duplicated fixture fails nothing by construction; none is a line the reads execute. Keys: :699 STMT_DEL, :703 CALL_DEL, :718 CALL_DEL, :728 CONST_SWAP, :732 CONST_SWAP, :732 STMT_DEL, :733 GUARD_OFF, :734 CALL_DEL, :747 STMT_DEL, :765 CONST_SWAP, :770 CALL_DEL, :771 CALL_DEL, :771 CONST_SWAP, :772 CALL_DEL, :772 CONST_SWAP, :773 STMT_DEL, :775 CALL_DEL, :776 CALL_DEL, :777 CALL_DEL, :778 CALL_DEL, :779 CALL_DEL, :780 CALL_DEL, :781 CALL_DEL, :782 STMT_DEL, :784 CALL_DEL, :785 CALL_DEL, :786 STMT_DEL, :788 STMT_DEL, :790 CALL_DEL, :791 CALL_DEL, :791 CONST_SWAP, :792 CALL_DEL, :792 CONST_SWAP, :793 CALL_DEL, :794 CALL_DEL, :795 CALL_DEL, :796 CALL_DEL, :797 STMT_DEL, :800 STMT_DEL, :806 CALL_DEL, :807 CALL_DEL, :808 STMT_DEL, :811 CALL_DEL, :813 CALL_DEL, :814 CONST_SWAP, :815 CALL_DEL, :815 CONST_SWAP, :816 CALL_DEL, :817 CALL_DEL, :818 STMT_DEL, :829 CONST_SWAP, :836 CALL_DEL, :836 CONST_SWAP, :837 CALL_DEL, :838 STMT_DEL, :840 CALL_DEL, :841 CALL_DEL, :842 CALL_DEL, :843 CALL_DEL, :844 STMT_DEL, :846 CALL_DEL, :847 CALL_DEL, :848 CALL_DEL, :848 CONST_SWAP, :849 CALL_DEL, :850 CALL_DEL, :851 STMT_DEL, :855 STMT_DEL, :858 STMT_DEL, :862 CALL_DEL, :863 STMT_DEL, :866 STMT_DEL, :867 CONST_SWAP, :868 STMT_DEL, :869 CALL_DEL, :871 CONST_SWAP, :872 STMT_DEL, :874 CALL_DEL, :880 CALL_DEL, :881 STMT_DEL, :884 STMT_DEL, :885 STMT_DEL, :886 CALL_DEL, :888 CALL_DEL, :889 CALL_DEL, :891 STMT_DEL, :892 GUARD_OFF, :894 CONST_SWAP, :894 RETURN_DEL, :896 RETURN_DEL, :902 CONST_SWAP, :903 CONST_SWAP, :908 CONST_SWAP, :909 CONST_SWAP, :910 CONST_SWAP, :911 CONST_SWAP, :912 CONST_SWAP, :913 CONST_SWAP, :916 CONST_SWAP, :929 CALL_DEL, :943 CALL_DEL, :944 CONST_SWAP.

## Null control

- `python3 -I tools/audit/product_reads.py --self-test` prints `SELF-TEST passed (79 arms)` at e924e49878. Null arms, each beside its planted twin: a payload-comparing check cited for its own cell is `moved` with `target=plan`, and with another site's write only it does not move; the fixture with no site perturbed turns no check but the planted `always-fails`; a hold under the per-module patch is `reached` (in `pump_arbiter`, `off_restore` and the coordinator module), and a recorder wrapping `log_latch.log_held` once the package is imported records 0 holds (r1); the real coordinator class built second is `restart`; an absent level gaining its key, a present one losing it and an option level switched are `witnessed`; two levels of two axes in one configuration make their pairs, two of one axis make none.
- Each new arm was run against its own mutant (driver and spec above). Two by hand before the commit: `if not a.read or not a.ledger:` -> `if False:` and the success `return 0` -> `return 1` each turn the self-test to exit 1.
- Live, `tests/guard_pins.py` under the launcher at 832005745a: `script tests/guard_pins.py	checks=88	writes outside every pass=4`, the same 88 as its own `ALL 88 GUARD PIN CHECKS PASSED`.

## Figures

- `operation` live, seed ledger `dev/audit/rounds/round11/product-reads/operation.tsv`, at 832005745a: `python3 -I tools/audit/product_reads.py operation --ledger dev/audit/rounds/round11/product-reads/operation.tsv` -> exit 0, `RESULT read=operation universe=456 examined=2 moved=4 reached=1` (33 s wall), identical to the round-1 head's figure: the removed redundancies change no verdict. `outside every pass ... pump_arbiter.py:1610	3`, `outside every pass ... inputs.py:722	1`; no `unlisted writer` line, now a line the self-test proves the read prints when one exists (n7).
- `generality` live, seed ledger `dev/audit/rounds/round11/product-reads/generality.tsv`, at 832005745a: exit 0, `RESULT read=generality universe=18897 examined=3 levels=3 pairs=0 reached-only=4` (160 s wall), identical to round 1.
- Universes, the rule: `python3 -I tools/audit/enumerate.py d16-writes --cells | wc -l` and `python3 -I tools/audit/enumerate.py d12-cells --pairs | wc -l`, each printed again as `universe=` on the read's RESULT line.
- `python3 -I tools/ci/selftest_scope.py static`: `120 gated step(s), 1 problem(s)` (`STALE ... ['self-tests-outside-seat']`) with `tools/ci/selftest_closures.json` from 3beb89a81a; `120 gated step(s), 0 problem(s)` at e924e49878. Re-recorded on Linux with `python3 tools/ci/selftest_scope.py record --step self-tests-outside-seat` (757 s, `0 failed [], 0 broken trace(s)`); the run also rewrote the `probes` of six other steps (`open-pr`, `policy-lint-mutants`, `pr-args`, `push-names-the-host`, `temp-or-machine-path`, `update-pr`), which were reverted: only the `self-tests-outside-seat` entry changes (`run_sha`, five added read paths).
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. Architecture score: `python3 -I tools/audit/archscore/score.py --diff 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c` -> `dS +0.0000` (no package file changes).
- Scope: `tests/closure.py select` prints `MODE: FULL` (`tools/ci/selftest_closures.json changes the gate itself`); CI runs every script.

## Red checks

- `governance / instrument-self-tests` (round 1, at 3beb89a81a; not in `merge_train.py owed-reds`, a block by `fix-review.md` step 11): cause, the PR's one-line addition of `product_reads.py --self-test` to `governance.yml`'s `self-tests-outside-seat` step without re-recording that step's read set, so `selftest_scope.py static` refused the step as STALE. Fixed by the re-record above. Cheaper detector: `python3 -I tools/ci/selftest_scope.py static`, run locally whenever a workflow step's run text changes; standing cost 0.11 s wall (`time python3 -I tools/ci/selftest_scope.py static`). Process state (a): it is on no local path, neither `tools/pr/prepr.sh` nor any `.claude/hooks/` script names it (`grep -n selftest_scope tools/pr/prepr.sh .claude/hooks/*` prints nothing), so the first detector a branch meets is CI. Not built here: a step in `prepr.sh` is a gate-file change outside this group's seam, and the countermeasure is owed by a separate root-cause seat (`defect-root-cause.md`). Carry: dismissed: the countermeasure belongs to the root-cause seat this rule names, not to the fix

## Forward-carry

- Part 2 of the approved plan: the regret oracle script under `tools/audit/` and its guide (design 3.4, the grid and the install-day record, with section 6's regret controls). Carry: R11-PRE-PRODUCT-READS
- n8, measured in round 1 (`ATTRIBUTE_KEYS` holds no forecast): D15 step 9 asks a seat for `C_same` per install-day, which no bundle can give; part 2 prints it NO-READ with that reason, and the brief's wording is part 2's to align, its owning group being carries-open. Carry: R11-PRE-PRODUCT-READS
- n6, the interface of design 3.5 (one command printing each escape in the window with id, released version, found-by, owning dimension or `none`, objective bug or owner report, then a count line; absent input prints unread), and its gap: `unowned` also counts owner reports that are no objective bug. Its seam is R11-PRE-ROUND-METRICS' by Carry 0, which is carries-open, so `carry_audit.py` keeps it with the producer for the relay to fold; this group builds no escapes record. Carry: R11-PRE-PRODUCT-READS
- n11: `dev/audit/rounds/round10/objective/escapes_hand.tsv` is a hand-read escapes ledger with owner and ruling columns; the round-metrics instrument should read rows of that shape; routed as n6. Carry: R11-PRE-PRODUCT-READS
- n7: the seed run prints no `unlisted writer`, and the self-test now proves the read prints one when a write comes from a package site the census does not list, so there is no run-measured finding for the sibling design's F3. Carry: dismissed: no unlisted writer on the seed run, nothing measured to carry

## Friction

- fixer.md: contradiction: `refs/heads/handoff-wip/r11-pre-product-reads` held round 1's BLOCKED note (2dde9cbe79, not an ancestor of 3beb89a81a), so the brief's fast-forward-only step push could not land there, and deleting the ref was refused by this seat's permission guard; the repair ran with no step ref. Carry: dismissed: the relay's ref hygiene, recorded here for it
