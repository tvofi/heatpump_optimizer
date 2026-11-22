import subprocess, sys, shutil, pathlib
wt = pathlib.Path.home() / "wt"
M = [
 ("A timeout guard drops 'hung and'", "tools/audit/seat/merge_train.py", "not (hung and hung <= set(unreached or ()))", "not (hung <= set(unreached or ()))"),
 ("B ungated counted unreached", "tools/audit/seat/merge_train.py", "for x in steps if x.gated and x.id not in", "for x in steps if x.id not in"),
 ("C push-only not subtracted", "tools/audit/seat/merge_train.py", "_red_steps(head_steps) - SELFTESTS_PUSH_ONLY - set(unreached or ())", "_red_steps(head_steps) - set(unreached or ())"),
 ("D two-dot diff", "tools/audit/seat/merge_train.py", 'f"{base}...{head}"', 'f"{base}..{head}"'),
 ("E no merge base reads all inherited", "tools/audit/seat/merge_train.py", "return selftest_unreached(git, at[0], head) if at[0] else None", "return selftest_unreached(git, at[0], head) if at[0] else set()"),
 ("F unreadable diff read as empty set", "tools/audit/seat/merge_train.py", "if diff is None or wf is None or table is None:\n        return None", "if diff is None or wf is None or table is None:\n        return set()"),
 ("G FULL read as scoped", "tools/audit/seat/merge_train.py", 'if plan["mode"] != "SCOPED" or not steps:', 'if not steps:'),
 ("H base tree workflow", "tools/audit/seat/merge_train.py", 'git("show", f"{head}:{st.WORKFLOW}"), git("show", f"{head}:{st.TABLE}")', 'git("show", f"{base}:{st.WORKFLOW}"), git("show", f"{base}:{st.TABLE}")'),
 ("I review_packet git_out swallows to empty", "tools/audit/seat/review_packet.py", "        except Unavailable:\n            return None", "        except Unavailable:\n            return \"\""),
 ("J review_packet scope ignored", "tools/audit/seat/review_packet.py", "lambda: merge_train.selftest_unreached(git_read or git_out, base, head)", "lambda: None"),
 ("K timeout never added", "tools/audit/seat/merge_train.py", "        names.insert(0, JOB_TIMED_OUT)", "        pass"),
 ("L ci_rerun cap off-by-one", "tools/audit/seat/ci_rerun.py", '>= MAX_ATTEMPT:', '> MAX_ATTEMPT:'),
]
TESTS = ["python3 tools/audit/seat/merge_train.py --self-test", "python3 tools/audit/seat/review_packet.py --self-test", "python3 -I tools/audit/seat/ci_rerun.py --self-test"]
for name, f, old, new in M:
    if old is None: continue
    p = wt / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"RESULT {name}: NOT-APPLIED (count {src.count(old)})"); continue
    p.write_text(src.replace(old, new))
    try:
        killed = []
        for t in TESTS:
            r = subprocess.run(t, shell=True, cwd=wt, capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                fl = [l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")][:1]
                killed.append(f"{t.split()[-2] if '-I' not in t else t.split()[-2]}: {fl[0].strip() if fl else 'rc '+str(r.returncode)}")
        print(f"RESULT {name}: {'KILLED by ' + ' | '.join(killed) if killed else 'SURVIVED'}", flush=True)
    finally:
        p.write_text(src)
