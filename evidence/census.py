import re, sys
from pathlib import Path
ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import record_row as rr
files = sorted(ROOT.glob("dev/programme/delivery/*.md"))
numeric = [p for p in files if re.fullmatch(r"\d+\.md", p.name)]
merged = open_ = 0
outside = multiline = prose = 0
for p in numeric:
    n = int(p.stem)
    lines = p.read_text(encoding="utf-8").splitlines()
    if len(lines) == 1 and rr.rowed_line(n, lines[0]):
        st = rr.line_status(lines[0])
        if st and st[0] == "open": open_ += 1
        elif st and st[0] == "merged": merged += 1
        else: prose += 1  # single line but status no writer emits
    else:
        outside += 1
        if len(lines) != 1: multiline += 1
        else: prose += 1
print(f"RESULT: numeric={len(numeric)} merged={merged} open={open_} outside={outside} multiline={multiline} prose_status={prose}")
print(f"RESULT: total={merged+open_+outside} (expect 503=248+104+151)")
