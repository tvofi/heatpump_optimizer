import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1])
M = [
 ("ghapi", "tools/ci/ghapi.py", "            meter.slept(path, clock() - t0)\n", "            pass\n"),
 ("ghapi", "tools/ci/ghapi.py", "                meter.api_s += clock() - t0\n", "                pass\n"),
 ("ghapi", "tools/ci/ghapi.py", "            self.api_s += self.clock() - t0\n", "            pass\n"),
 ("ghapi", "tools/ci/ghapi.py", "        self.calls += 1\n", "        pass\n"),
 ("ghapi", "tools/ci/ghapi.py", 'self.naps.append((path.split("?")[0], round(seconds, 3)))', 'self.naps.append((path, round(seconds, 3)))'),
 ("ghapi", "tools/ci/ghapi.py", "        t0 = clock and clock()\n        _sleep(nap)", "        _sleep(nap)"),
 ("prelude", "tools/ci/prelude.py", "changed, meter, fast=shards.outputs)", "changed, get or ghapi.get, fast=shards.outputs)"),
 ("prelude", "tools/ci/prelude.py", "    print(line, file=sys.stderr)\n", "    pass\n"),
 ("prelude", "tools/ci/prelude.py", '                fh.write(f"### prelude timing\\n\\n`{line}`\\n")\n', "                pass\n"),
 ("prelude", "tools/ci/prelude.py", '"defer": [int(i) for i in defer.split()]', '"defer": []'),
 ("prelude", "tools/ci/prelude.py", '        outcome = "defer" if out.get("defer") else "ok"\n', '        outcome = "ok"\n'),
 ("prelude", "tools/ci/prelude.py", '            outcome = "rate-limited"\n', "            pass\n"),
 ("prelude", "tools/ci/prelude.py", '"local_s": r(max(0.0, wall_s - meter.api_s - meter.sleep_s))', '"local_s": r(wall_s)'),
 ("prelude", "tools/ci/prelude.py", 'int(env.get("GITHUB_RUN_ATTEMPT") or 1)', '1'),
 ("prelude", "tools/ci/prelude.py", "        report(timing(", "        0 and report(timing("),
]
for name, f, a, b in M:
    p = wt / f; src = p.read_text()
    n = src.count(a)
    if n != 1: print(f"BADANCHOR count={n} {f}: {a!r}"); continue
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run(["bash", "-c", "python3 -I tools/ci/ghapi.py --self-test && python3 -I tools/ci/prelude.py --self-test"], cwd=wt, capture_output=True, text=True, timeout=600)
        fails = [l for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l][:3]
        print(("KILLED" if r.returncode else "SURVIVED"), f, repr(a.strip())[:70], "|", fails)
    finally:
        p.write_text(src)
