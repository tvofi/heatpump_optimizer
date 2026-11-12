# reviewer's driver (not the fixer's): each mutant = one exact replacement in its own worktree copy of the head
import subprocess, sys, pathlib, concurrent.futures as cf
W = pathlib.Path(sys.argv[1]); HEAD = sys.argv[2]; REPO = "/home/user/heatpump_optimizer"
F = "tools/audit/seat/merge_train.py"
ONLY = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
M = {
 "A drop stamp_hold_wait() in land": ("            self.stamp_hold_wait()\n", ""),
 "B drop `if not self.real: return` in the wait": ("        if not self.real:\n            return\n        waited = 0\n", "        waited = 0\n"),
 "E negative age -> None (fail open)": ("        except ValueError:\n            return None\n        return age\n", "        except ValueError:\n            return None\n        return age if age >= 0 else None\n"),
 "K hold_refresh in the wait -> pass": ("            self.hold_refresh()  # the record beat", "            pass  # the record beat"),
 "R unreadable date -> 60.0": ("        except ValueError:\n            return None\n        return age\n", "        except ValueError:\n            return 60.0\n        return age\n"),
 "L drop waited += poll": ("            waited += STAMP_HOLD_POLL_S\n", ""),
 "M bound max(age, waited) -> age": ("            if max(age, waited) >= STAMP_HOLD_MAX_AGE_S:", "            if age >= STAMP_HOLD_MAX_AGE_S:"),
 "T bound -> if False": ("            if max(age, waited) >= STAMP_HOLD_MAX_AGE_S:", "            if False:"),
 "U bound max(age, waited) -> waited (age ignored)": ("            if max(age, waited) >= STAMP_HOLD_MAX_AGE_S:", "            if waited >= STAMP_HOLD_MAX_AGE_S:"),
 "V refresh moved after the sleep": ("            self.hold_refresh()  # the record beat reads train-hold stale at HOLD_MAX_AGE_S; this wait runs to 7200\n            self.sleep(STAMP_HOLD_POLL_S)\n", "            self.sleep(STAMP_HOLD_POLL_S)\n            self.hold_refresh()\n"),
 "X10 >= -> >": ("(stamp, i) >= best[name][0]", "(stamp, i) > best[name][0]"),
 "X14 stamps[0] -> stamps[-1]": ("stamp = stamps[0] if stamps", "stamp = stamps[-1] if stamps"),
 "X16 drop context fallback": ('c.get("name") or c.get("context") or "?"', 'c.get("name") or "?"'),
 "X17 drop real guard in record_drafts": ('        if not self.real:\n            return\n        for item in queue:\n            if "draft" not in item:', '        for item in queue:\n            if "draft" not in item:'),
}
def run(item):
    i, (name, (a, b)) = item
    wt = W / f"m{i}"
    subprocess.run(["git", "-C", REPO, "worktree", "add", "-q", "--detach", str(wt), HEAD], check=True)
    src = wt / F; orig = src.read_text()
    if orig.count(a) != 1:
        return f"{name}: NOT-APPLIED (count {orig.count(a)})"
    src.write_text(orig.replace(a, b))
    try:
        p = subprocess.run(["bash", "-c", f"ulimit -v 2097152; exec python3 {F} --self-test"], cwd=wt, capture_output=True, text=True, timeout=200)
        out = p.stdout + p.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
        tail = out.strip().splitlines()[-1:]
        return f"{name}: {'KILLED' if p.returncode else 'SURVIVED'} rc={p.returncode} {tail} {fails[:5]}"
    except subprocess.TimeoutExpired:
        return f"{name}: KILLED-by-timeout (200 s, no termination)"
with cf.ThreadPoolExecutor(5) as ex:
    for r in ex.map(run, [(i, kv) for i, kv in enumerate(M.items()) if (ONLY is None or kv[0].split()[0] in ONLY)]):
        print(r, flush=True)
