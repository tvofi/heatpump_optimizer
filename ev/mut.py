import subprocess, sys, pathlib, shutil
SRC = pathlib.Path("/root/wt/tools/audit/seat/merge_train.py")
orig = SRC.read_text()
M = {
 "A drop the call in land": ("            self.stamp_hold_wait()\n            guard()\n", "            guard()\n"),
 "B drop `if not self.real: return`": ("        if not self.real:\n            return\n        while True:\n            age = self.stamp_hold_age()", "        while True:\n            age = self.stamp_hold_age()"),
 "C age bound >= -> >": ("            if age >= STAMP_HOLD_MAX_AGE_S:", "            if age > STAMP_HOLD_MAX_AGE_S:"),
 "D take-over keeps waiting (no return)": ("{STAMP_HOLD_MAX_AGE_S}s; its holder is dead\")\n                return\n", "{STAMP_HOLD_MAX_AGE_S}s; its holder is dead\")\n"),
 "E future-dated hold read as its (negative) age": ("        return age if age >= 0 else None", "        return age"),
 "F drop the poll sleep": ("            self.sleep(STAMP_HOLD_POLL_S)\n", ""),
 "G drop the wait log": ("            self.log(f\"STAMP-HOLD: a stamp is running", "            (f\"STAMP-HOLD: a stamp is running"),
 "H drop the take-over log": ("                self.log(f\"STAMP-HOLD taken over", "                (f\"STAMP-HOLD taken over"),
 "I wait placed once before the loop": None,
 "J future-dated hold treated as live (age 0)": ("        return age if age >= 0 else None", "        return age if age >= 0 else 0.0"),
}
for name, sub in M.items():
    if sub is None: continue
    a, b = sub
    if orig.count(a) != 1:
        print(f"{name}: NOT-APPLIED (count {orig.count(a)})"); continue
    SRC.write_text(orig.replace(a, b))
    try:
        p = subprocess.run([sys.executable, str(SRC), "--self-test"], cwd="/root/wt", capture_output=True, text=True, timeout=400)
        fails = [l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip().startswith("FAIL")]
        tail = (p.stdout + p.stderr).strip().splitlines()[-1:] 
        verdict = "KILLED" if p.returncode != 0 else "SURVIVED"
        print(f"{name}: {verdict} rc={p.returncode} {tail} {fails[:4]}")
    except subprocess.TimeoutExpired:
        print(f"{name}: KILLED-by-timeout (hang)")
    finally:
        SRC.write_text(orig)
