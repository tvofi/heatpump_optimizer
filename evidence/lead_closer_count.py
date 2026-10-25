# Reviewer's count: lines, in the guard's scanned .md files, whose text holds a
# ')' with no '(' before it on the same line (the shape that ends the head's
# forward read before the program). Run from the repo root at the head.
import subprocess, re
fs = [f for f in subprocess.run(['git','ls-files','tools','.claude/workflows'],capture_output=True,text=True).stdout.split('\n')
      if f.endswith('.md') and not re.match(r'tools/audit/round\d', f) and '/fixtures/' not in f]
n = tot = 0
for f in fs:
    for line in open(f, encoding='utf-8', errors='replace'):
        tot += 1; d = 0
        for c in line:
            if c == '(': d += 1
            elif c == ')':
                d -= 1
                if d < 0: n += 1; break
print(f'LEAD-CLOSER {n} of {tot} line(s) over {len(fs)} .md file(s)')
