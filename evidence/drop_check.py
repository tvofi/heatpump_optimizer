# step 14: which scripts' closures already contained a citation source, and does
# the carve-out silence an orphan/inert_reads signal for any of them?
import sys, subprocess, json; sys.path.insert(0,"tests")
import closure as C
srcs = sorted(f for f in subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
              if C._is_citation_source(f))
holders = {}
for s, files in json.loads(C.CLOSURES.read_text())["closures"].items():
    hit = sorted(set(files) & set(srcs))
    if hit: holders[s] = hit
print("scripts whose recorded closure already held a citation source (besides entities.py):")
for s, h in holders.items():
    if s != "tests/entities.py": print("   ", s, len(h), h[:4])
print("entities.py holds:", len(holders.get("tests/entities.py", [])))
print("orphan_files() over the head table:", len(C.orphan_files()) if hasattr(C,"orphan_files") else "n/a")
