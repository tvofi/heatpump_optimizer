R11-PRE-PRODUCT-READS part 1 of 2 (design `design/R11-PRE-PRODUCT-READS` at 8daf118368, `Design review: approve` at a08d8f47c9): `tools/audit/product_reads.py`, which reads decision 0018's `operation` and `generality` off a seat's cell ledger and counts a row only on a witness the read produced itself; decision 0018 names this group as the builder of `regret`, `operation` and `generality`'s examined count, and R11-PRE-ROUND-METRICS for `escapes` and `unowned` (design 3.6). Part 2 (`regret`: the same-information oracle and the install-day record) is the approved plan's second pull request. No production file and no file under `tests/` other than `tests/layout.json` is edited. Universes are imported from `tools/audit/enumerate.py` (R11-PRE-BRIEFS-CENSUS, merged as #3625), never enumerated a second time.

How each read witnesses, per the design:
- `operation` (3.2): each cited script runs unedited under a launcher (wrappers on `harness.Results.check`, `FakeServices.async_call` installed as a plain function per n1, `FakeEntry`, `pump_arbiter.apply`, the coordinator's constructor, and `log_held` in each importing module's namespace through a post-import hook), twice as it is, then once per cited (site, cell state) with the payload from that site perturbed **only in `apply` passes whose recorded state is the cell's** (v2-1). The state is read off the plan the coordinator holds at `apply` entry by plain indexing; a token with no table entry prints `state not recorded`. Writes outside every pass are printed per site, never witnessed (v2-2).
- v2-3 answered: `arbiter_inputs()` is not read-only for this read: it calls `pump_arbiter.live_power_kw`, which reads through `InputReader` (`inputs.py` binds `log_held`), so an extra call could record a hold the code under test never made. The wrapper reads `coord._optimization_result` and `coord.effective_config` (else `_config`) directly.
- `generality` (3.3): a level row counts only when the read's own run, with that level's observable switched to the next level of its axis in the recorded configuration, turns the check FAIL or changes its detail; a pair only when both its levels are witnessed in one configuration of one script (`--pairs-out` writes them in `enumerate.py d12-cells --pairs --ledger`'s format). Bundle and install-report rows are printed and never counted.
- One departure, raised here: `restart` is read as "not the first coordinator **built** on its entry object" for the real class, and, for a test's own fake coordinator that is never built through it (e.g. `tests/guard_pins.py`'s `Coord`), "not the first seen at `apply`" on that entry object. The design names construction only; with construction only, every fake-coordinator pass would print `state not recorded` and F5's checks could never be witnessed. Keyed on the entry object, not `entry_id`, because `FakeEntry()` defaults every entry to one id.
- At this base `d16-writes --cells` prints duty x {running, restart, upgrade, unavailable} (the census formula, NEW-DIMENSIONS not merged): `upgrade` prints `state not recorded`; the plan-state rows (idle, dhw-only, both, partial, full, min-cold-tank, baseline) are in the table and pinned by direct arms, read the day the formula changes (n10).

## Head

b7f3db72d040ea86803ce5dbd13957e1cce89ee0. Merge base 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c; origin/main 95e81782ffb2c03f0157cc5f26f7a12cc035fdd6 at 2026-11-16T18:54:54Z, `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict). One commit on the reviewed head face7218ab, touching only `tools/audit/product_reads.py`'s self-test (fixture script, fixture `tests/profiles.py`, fixture objective, ledgers and arms); no line the reads execute against a real tree changes.

The group's roster carries, at `handoff/audit-r10-roster` e9f1c10d5a: Carry 0 (the seam ruling) is honoured by n6 below, this group building no escapes record. Carry 1 (part 2, the regret oracle and its guide), Carry 2 (n8, `C_same` NO-READ) and Carry 3 (n11, `escapes_hand.tsv`'s row shape) are round 1's own forward-carries, landed on the roster at e9f1c10d5a; each is part 2's or the round-metrics instrument's work and is not re-carried here.

prepr: passed rc=0 at b7f3db72d040ea86803ce5dbd13957e1cce89ee0

Block answered (round-2 verdict at 4616068573, `mutation-vacuous`): `moved()`'s detail-only half (`(not b["ok"] or b["detail"] != a["detail"])`) is now pinned in both reads by a check that stays ok while only its detail moves, each beside a null whose detail does not move:
- operation: fixture check `differs-detail` (`r.check("differs-detail", True, str(sent(off)))`) cited for the running write cell reads `moved\ttarget=differs plan=21.0 sent=22.0`; null `steady-detail` (`str(sent(held))`, a pass that writes nothing, so the perturbed site never reaches its detail) reads `not witnessed: the check does not move`.
- generality: fixture check `mode-detail` (`True, str(e.data.get("mode"))`) cited for `level mode=m1` reads `witnessed (configuration 0)`; null `mode-steady` (`str(e.data.get("a_entity"))`, a detail the switched level does not reach) reads `reached (configuration 0): the check does not move with the level switched`.

The verdict's Finding (Carry: R11-PRE-PRODUCT-READS, `carried()`'s profile-kind test unpinned) is answered in the same commit, as the verdict proposed: the fixture's `tests/profiles.py` gains `weather(profile, s)` comparing `p1` and `w2`, the fixture objective a `climate` compare axis on it, and the script ends with `prices("p1", 0)` then `weather("p1", 0)` (configurations 6 and 7) and checks on each return. `level price_shape=p1` citing `price-late` reads `witnessed (configuration 6)` (with the kind test dropped it is carried by the later `weather` configuration 7 and reads `reached`); `level climate=p1` citing `weather-late` reads `witnessed (configuration 7)` (the null, unchanged under the mutant).

## Mutation proof

Rule: the reviewer's two specs from the verdict commit 4616068573 (`ev/mutants_moved_halves.json`, `ev/mutants_reviewer_spec.json`), run unchanged with `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'python3 -I tools/audit/product_reads.py --self-test'` at b7f3db72d0; and the tracked driver over every added line of the diff, `python3 tools/audit/seat/mutant_run.py --diff 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c...HEAD --cmd 'python3 -I tools/audit/product_reads.py --self-test' --report-only --max-mutants 700` (the verdict's command, unchanged).

The mutant list for this script is the reviewer's targeted spec, which already carries `moved-detail-ignored` and `carried-profile-kind-off`; it was run as it stands, adding nothing to and removing nothing from it. No in-tree mutant list exists for `product_reads.py` (its in-tree pin is the self-test, driven by the diff driver), so none was created: a new tracked file would need closure classification outside this repair's scope.

`ev/mutants_moved_halves.json`, rc=0: its `NULL` is the driver's own built-in no-op, SURVIVED, so the command is sound.

~~~text
SURVIVED NULL
KILLED moved-ok-half-dropped
KILLED moved-detail-ignored
~~~

`ev/mutants_reviewer_spec.json`, rc=0, every row. `NULL` is the driver's built-in no-op; `null-noop` is the reviewer's own no-op control (a comment-only edit), and both SURVIVED as they must. Every other row, 23 of them, is KILLED, including `moved-detail-ignored` (the block) and `carried-profile-kind-off` (the Finding).

~~~text
SURVIVED NULL
KILLED pair-same-axis-guard-off
KILLED operation-fail-at-head-branch-off
KILLED target-compare-always-plan
KILLED perturb-site-restriction-dropped
KILLED unlisted-writer-off
KILLED hold-reached-before-state-check
KILLED presence-carried-ignores-level
KILLED gen-fail-at-head-off
KILLED hasses-first-pass
KILLED construction-ordinal-off
KILLED entry-switch-ordinal-shift
KILLED absent-to-present-noop
KILLED profile-switch-noop
KILLED ledger-colcount-off
KILLED ledger-source-check-off
KILLED ledger-no-coloncolon-off
KILLED carried-profile-kind-off
KILLED carried-entry-guard-off
KILLED moved-detail-ignored
KILLED nondet-detail-ignored
KILLED outside-pass-count-any
KILLED counted-reached-dropped
KILLED gen-pairs-cross-script
SURVIVED null-noop
~~~

Driver at b7f3db72d0, every SURVIVED line (rc=0 under `--report-only`):

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
SURVIVED tools/audit/product_reads.py:710 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:726 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:737 CONST_SWAP  arms, fails = 1, []
SURVIVED tools/audit/product_reads.py:741 CONST_SWAP  arms += 2
SURVIVED tools/audit/product_reads.py:742 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:743 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:775 CONST_SWAP  out = read_operation(root, led, 5)
SURVIVED tools/audit/product_reads.py:780 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:781 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:781 CONST_SWAP  arm("null: the target half reads the plan's set-point", next(l for l in out if l.startswith(ops[1][0]) and S + "payload" in l).endswith("target=plan"), True)
SURVIVED tools/audit/product_reads.py:782 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:782 CONST_SWAP  arm("planted (i): a constant-condition check does not move", v(2), "not witnessed: the check does not move")
SURVIVED tools/audit/product_reads.py:785 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:786 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:787 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:788 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:789 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:790 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:791 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:794 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:795 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:800 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:801 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:801 CONST_SWAP  arm("planted: a set-point the plan does not hold", full[(ops[17][0], S + ops[16][1])], "moved\ttarget=differs plan=21.0 sent=22.0")
SURVIVED tools/audit/product_reads.py:802 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:802 CONST_SWAP  arm("null: a pass with no `now` reads the clock", v(18), "moved")
SURVIVED tools/audit/product_reads.py:803 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:804 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:805 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:806 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:807 CONST_SWAP  arm("null: a check that stays ok while only its detail moves under the perturbed payload: moved", full[(ops[23][0], S + ops[22][1])],
SURVIVED tools/audit/product_reads.py:820 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:821 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:825 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:827 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:828 CONST_SWAP  ps = {"duty": "control", "plan": True, "k": None, "plan_state": None, "ordinal": 1}
SURVIVED tools/audit/product_reads.py:829 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:829 CONST_SWAP  arm("token: baseline is a plan held and no step covering now", (token_holds("baseline", ps, None), token_holds("baseline", {**ps, "k": 1}, None)), (True, False))
SURVIVED tools/audit/product_reads.py:830 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:831 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:845 CONST_SWAP  gout = read_generality(root, gl, 5, pairs_out=po)
SURVIVED tools/audit/product_reads.py:852 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:852 CONST_SWAP  arm("null: a check on a key's presence, its level switched: witnessed", g(1), "witnessed (configuration 0)")
SURVIVED tools/audit/product_reads.py:853 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:856 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:857 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:858 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:859 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:862 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:863 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:864 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:864 CONST_SWAP  arm("null: two keys of one axis carry two levels in one configuration", (g(12), g(12)), ("witnessed (configuration 5)",) * 2)
SURVIVED tools/audit/product_reads.py:865 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:866 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:867 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:872 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:884 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:889 CONST_SWAP  next(l for l in read_generality(root, gl, 5) if l.startswith("level grid=g1\t")).endswith("no witness: no observable in the stub"), True)
SURVIVED tools/audit/product_reads.py:891 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:893 CONST_SWAP  for name, fn in (("operation", lambda: read_operation(root, led, 2)), ("generality", lambda: read_generality(root, gl, 1))):
SURVIVED tools/audit/product_reads.py:896 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:902 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:908 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:910 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:911 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:914 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:916 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:916 CONST_SWAP  return 2
SURVIVED tools/audit/product_reads.py:918 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:924 CONST_SWAP  mk = lambda s, d, f=None, n=3: NS(timestamps=[_T0 + timedelta(minutes=15 * i) for i in range(n)], power_schedule=[s] * n,
SURVIVED tools/audit/product_reads.py:925 CONST_SWAP  dhw_power_schedule=[d] * n, optimal_setpoints=[40.0] * n, duty_floor_kw=f)
SURVIVED tools/audit/product_reads.py:930 CONST_SWAP  ("no configured maximum reads no partial", mk(4.0, 0.0), {}, None),
SURVIVED tools/audit/product_reads.py:931 CONST_SWAP  ("now past the plan has no k", NS(timestamps=[_T0 - timedelta(hours=3), _T0 - timedelta(hours=1, minutes=45)],
SURVIVED tools/audit/product_reads.py:932 CONST_SWAP  power_schedule=[4.0, 2.0]), cfg, None),
SURVIVED tools/audit/product_reads.py:933 CONST_SWAP  ("no power schedule reads no state", NS(timestamps=[_T0, _T0 + timedelta(minutes=16)]), cfg, None),
SURVIVED tools/audit/product_reads.py:934 CONST_SWAP  ("dhw past its end reads 0", NS(timestamps=[_T0 - timedelta(minutes=16), _T0], power_schedule=[0.5, 0.5],
SURVIVED tools/audit/product_reads.py:935 CONST_SWAP  dhw_power_schedule=[2.0], duty_floor_kw=None), cfg, "partial")]
SURVIVED tools/audit/product_reads.py:938 CONST_SWAP  _T0 = __import__("datetime").datetime(2027, 1, 1, tzinfo=__import__("datetime").timezone.utc)
SURVIVED tools/audit/product_reads.py:951 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:965 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:966 CONST_SWAP  return int(r.stdout.strip() or -2)
SURVIVED tools/audit/product_reads.py:991 CONST_SWAP  ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
SURVIVED tools/audit/product_reads.py:997 CONST_SWAP  ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
SURVIVED tools/audit/product_reads.py:1004 RETURN_DEL  pass
SURVIVED tools/audit/product_reads.py:1004 CONST_SWAP  return 1
SURVIVED tools/audit/product_reads.py:1016 GUARD_OFF  if False:
SURVIVED tools/audit/product_reads.py:1017 CALL_DEL  pass
SURVIVED tools/audit/product_reads.py:706 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:741 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:756 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:783 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:792 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:796 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:798 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:807 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:809 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:811 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:814 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:822 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:832 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:854 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:860 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:868 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:870 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:873 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:877 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:880 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:885 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:888 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:890 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:894 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:903 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:906 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:907 STMT_DEL  pass
SURVIVED tools/audit/product_reads.py:913 STMT_DEL  pass
driver rc=0
~~~

</details>

## Unpinned sites

Every survivor above, by line at b7f3db72d0, with its disposition. The production-side set (lines above the self-test, under 698) is identical, line and operator, to the one the round-2 verdict accepted at face7218ab (compared with `diff`, below); the self-test lines are renumbered by this repair's added fixture lines. All are equivalent or outside what the command can see; none is in a counted predicate: `moved()`'s two halves and `carried()`'s profile-kind test are now each killed (`## Mutation proof`).

- `:34` CONST_SWAP (`sys.path.insert(1, ...)`): equivalent; `enumerate` resolves at either index, and the launcher rebuilds `sys.path` before any script runs. Accepted by round 1.
- `:38` `RUN_TIMEOUT_S` 900 -> 901: a bound on a hung child, read by no verdict. Accepted by round 1.
- `:76` `_perturb`'s offset 7.0 -> 14.0: any non-zero offset is a different payload. Accepted by round 1.
- `:107` CMP_BOUND `0 < s` -> `0 <= s`: equivalent; `s == 0` returns `idle` or `dhw-only` two branches earlier. Accepted by round 1.
- `:128` (`token_holds`' last `return None`) and `:147` (`find_spec`'s last `return None`) RETURN_DEL: equivalent; a function falling off its end returns None.
- `:138` CONST_SWAP `rsplit(".", 2)[-1]`: equivalent; the last component is the same with any maxsplit >= 1.
- `:153` CALL_DEL `os.chdir(repo)`: equivalent under `run_script`, which starts the child with `cwd=repo`; kept for a launch from any other caller.
- `:155` CONST_SWAP `sys.path[2:]`: equivalent in measurement. With it applied, a probe planting the fixture and importing `homeassistant` in the child prints `.../tests/hastub/homeassistant/__init__.py`, and `now-none-payload` (whose wrapper imports `homeassistant.util.dt`) is ok; the stub still resolves, so no arm can separate the two.
- `:193` GUARD_OFF of the absent -> present branch: equivalent; with `from=None` the next branch's `d.get(k) == None` matches the absent key and writes it into data and options both, and the merged configuration carries the level the same. Its STMT_DEL (`data[k] = ...` deleted, the review's `:195`) is killed by `null: an absent level gains its key`.
- `:245`/`:246` (`patch_holds` on a module with no `log_held`) and `:269` (`patch_profiles` on a profiles module lacking `prices` or `weather`): equivalent; the mutant sets a wrapper of None that nothing calls, because the module has no such name for any code to call. The fixture now defines `weather`, so this guard is reached only by a real profiles module missing one of the two names.
- `:283` CONST_SWAP `sys.meta_path.insert(1, ...)`: equivalent on CPython, whose `meta_path` holds BuiltinImporter, FrozenImporter, PathFinder: index 1 is still before the PathFinder that loads the package.
- `:344` CONST_SWAP `capture_output=False`: no verdict reads the child's streams (the record is the JSON file); the flag keeps a child's stderr out of the read's stdout.
- `:370` CONST_SWAP `max(2, self.jobs)`: a worker count; each run is independent.
- `:408` and `:524` CMP_BOUND `<` -> `<=` on `seq`: equivalent; checks, writes, holds and configurations draw from one `itertools.count()`, so no two `seq` are equal.
- `:439` and `:570` CONST_SWAP `runs[key(s, 1)]`: equivalent; run 1 is run 0 unchanged, and these lines count the writes, holds and configurations each run makes, which are identical in both runs of the fixture. They are printed lines; no verdict reads them.
- `main` and the helpers below the self-test: `:991` (`__doc__.split("\n")[1]`, argparse's description) and `:997` (`--jobs` default `or 2`) print or schedule, no verdict; `:1004` (`return 0` after `_launch`, RETURN_DEL and CONST_SWAP): equivalent, `run_script` reads the child's record file and never its exit code; `:1016`/`:1017` (the `if __name__ == "__main__"` entry point): outside what the command can see, as accepted in round 2 (with it deleted the self-test command runs nothing and exits 0, the shape of every self-test entry point in that governance step). `:965`/`:966` are `_only_latch`'s probe cleanup and its `or -1` fallback, test scaffolding (round 2's `:943`/`:944`).
- The self-test itself (`plant` through `_exit`): each survivor deletes or swaps one fixture line, arm call or helper statement and the self-test still passes. Deleting an assertion or a duplicated fixture fails nothing by construction; none is a line the reads execute. Keys: :710 CALL_DEL, :726 CALL_DEL, :737 CONST_SWAP, :741 CONST_SWAP, :742 GUARD_OFF, :743 CALL_DEL, :775 CONST_SWAP, :780 CALL_DEL, :781 CALL_DEL, :781 CONST_SWAP, :782 CALL_DEL, :782 CONST_SWAP, :785 CALL_DEL, :786 CALL_DEL, :787 CALL_DEL, :788 CALL_DEL, :789 CALL_DEL, :790 CALL_DEL, :791 CALL_DEL, :794 CALL_DEL, :795 CALL_DEL, :800 CALL_DEL, :801 CALL_DEL, :801 CONST_SWAP, :802 CALL_DEL, :802 CONST_SWAP, :803 CALL_DEL, :804 CALL_DEL, :805 CALL_DEL, :806 CALL_DEL, :807 CONST_SWAP, :820 CALL_DEL, :821 CALL_DEL, :825 CALL_DEL, :827 CALL_DEL, :828 CONST_SWAP, :829 CALL_DEL, :829 CONST_SWAP, :830 CALL_DEL, :831 CALL_DEL, :845 CONST_SWAP, :852 CALL_DEL, :852 CONST_SWAP, :853 CALL_DEL, :856 CALL_DEL, :857 CALL_DEL, :858 CALL_DEL, :859 CALL_DEL, :862 CALL_DEL, :863 CALL_DEL, :864 CALL_DEL, :864 CONST_SWAP, :865 CALL_DEL, :866 CALL_DEL, :867 CALL_DEL, :872 CALL_DEL, :884 CALL_DEL, :889 CONST_SWAP, :891 CALL_DEL, :893 CONST_SWAP, :896 CALL_DEL, :902 CALL_DEL, :908 CALL_DEL, :910 CALL_DEL, :911 CALL_DEL, :914 GUARD_OFF, :916 RETURN_DEL, :916 CONST_SWAP, :918 RETURN_DEL, :924 CONST_SWAP, :925 CONST_SWAP, :930 CONST_SWAP, :931 CONST_SWAP, :932 CONST_SWAP, :933 CONST_SWAP, :934 CONST_SWAP, :935 CONST_SWAP, :938 CONST_SWAP, :951 CALL_DEL, :706 STMT_DEL, :741 STMT_DEL, :756 STMT_DEL, :783 STMT_DEL, :792 STMT_DEL, :796 STMT_DEL, :798 STMT_DEL, :807 STMT_DEL, :809 STMT_DEL, :811 STMT_DEL, :814 STMT_DEL, :822 STMT_DEL, :832 STMT_DEL, :854 STMT_DEL, :860 STMT_DEL, :868 STMT_DEL, :870 STMT_DEL, :873 STMT_DEL, :877 STMT_DEL, :880 STMT_DEL, :885 STMT_DEL, :888 STMT_DEL, :890 STMT_DEL, :894 STMT_DEL, :903 STMT_DEL, :906 STMT_DEL, :907 STMT_DEL, :913 STMT_DEL.

Production-side comparison, the rule: `git show 4616068573:ev/mutants_diff_driver.txt | grep ^SURVIVED | awk '{split($2,a,":"); if (a[2]<698) print $2, $3}'` against the same filter over this head's driver output, `diff old new && echo LOW-SURVIVORS-IDENTICAL` -> `LOW-SURVIVORS-IDENTICAL`.

## Null control

- `python3 -I tools/audit/product_reads.py --self-test` prints `SELF-TEST passed (85 arms)` at b7f3db72d0 (79 at face7218ab; six arms added: the two detail-only rows and their two nulls, and the price/climate pair).
- Each added null passes at the head and its planted twin is killed by its mutant: `moved-detail-ignored` and `carried-profile-kind-off` each KILLED above, while `NULL` and `null-noop` SURVIVED in the same runs.
- Before the repair, at face7218ab, the verdict's run of `ev/mutants_moved_halves.json` printed `SURVIVED moved-detail-ignored` (`ev/mutants_moved_halves.txt` at 4616068573); at this head the same spec prints `KILLED moved-detail-ignored`.

## Figures

- `operation` live, seed ledger `dev/audit/rounds/round11/product-reads/operation.tsv`, at b7f3db72d0: `python3 -I tools/audit/product_reads.py operation --ledger dev/audit/rounds/round11/product-reads/operation.tsv` -> exit 0, `RESULT read=operation universe=456 examined=2 moved=4 reached=1` (19 s wall), identical to round 2's figure at face7218ab; `outside every pass ... inputs.py:722	1`, `outside every pass ... pump_arbiter.py:1610	3`, no `unlisted writer` line.
- `generality` live, seed ledger `dev/audit/rounds/round11/product-reads/generality.tsv`, at b7f3db72d0: exit 0, `RESULT read=generality universe=18897 examined=3 levels=3 pairs=0 reached-only=4` (101 s wall), identical to round 2.
- Universes, the rule: `python3 -I tools/audit/enumerate.py d16-writes --cells | wc -l` and `python3 -I tools/audit/enumerate.py d12-cells --pairs | wc -l`, each printed again as `universe=` on the read's RESULT line.
- `python3 -I tools/ci/selftest_scope.py static` at b7f3db72d0: `120 gated step(s), 0 problem(s)`; the step's run text is unchanged, so no re-record.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. Architecture score: `python3 -I tools/audit/archscore/score.py --diff 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c` -> `dS +0.0000` (no package file changes).
- Scope: `tests/closure.py select` prints `MODE: FULL` (`tools/ci/selftest_closures.json changes the gate itself`); CI runs every script.

## Red checks

none

## Forward-carry

- n6, the interface of design 3.5 (one command printing each escape in the window with id, released version, found-by, owning dimension or `none`, objective bug or owner report, then a count line; absent input prints unread), and its gap: `unowned` also counts owner reports that are no objective bug. Its seam is R11-PRE-ROUND-METRICS' by Carry 0, which is carries-open, so `carry_audit.py` keeps it with the producer for the relay to fold; this group builds no escapes record. Carry: R11-PRE-PRODUCT-READS
- n7: the seed run prints no `unlisted writer`, and the self-test now proves the read prints one when a write comes from a package site the census does not list, so there is no run-measured finding for the sibling design's F3. Carry: dismissed: no unlisted writer on the seed run, nothing measured to carry

## Friction

- fixer.md: contradiction: `refs/heads/handoff-wip/r11-pre-product-reads` still held round 1's BLOCKED note (2dde9cbe79, not an ancestor of the PR head), so a fast-forward-only step push of the code could not land; the step was pushed as a commit with the code's tree and both as parents, which is a fast-forward and loses neither. Carry: dismissed: the relay's ref hygiene, recorded here for it
