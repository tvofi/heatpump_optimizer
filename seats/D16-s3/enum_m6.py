"""D16.M6's universe: every actuator write site (enumerate.py d16-writes' write lines) times each restore trigger.

One item per line: "<write line> | <trigger>". The triggers are the brief's step 6: off (the optimizer's mode set
to Off), unload, remove, and a duty-mode change (an options save, which reloads the entry).
Command (from the export root): python3 dev/audit/rounds/round11/D16/s3/enum_m6.py
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: 32 lines (8 write sites x 4 triggers).
"""
import subprocess
import sys

TRIGGERS = ("off", "unload", "remove", "duty-mode-change")
lines = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d16-writes"], check=True,
                       capture_output=True, text=True).stdout.splitlines()
for w in (l for l in lines if l.startswith("write ")):
    for t in TRIGGERS:
        print(f"{w} | {t}")
