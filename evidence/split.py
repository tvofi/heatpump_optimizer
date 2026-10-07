import re, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def split(p):
    d = {}; cur = None
    for l in open(p):
        if l.startswith('diff --git '):
            cur = l.split(' b/', 1)[1].strip(); d[cur] = []
        elif cur and not l.startswith('index '):
            d[cur].append(re.sub(r'^@@ -\d+(,\d+)? \+\d+(,\d+)? @@', '@@', l))
    return d
a = split('diff_46b9b4fd.patch'); b = split('diff_baadb840.patch')
for k in sorted(set(a) | set(b)):
    if a.get(k) != b.get(k):
        print(('NEW ' if k not in a else 'GONE ' if k not in b else 'CHG '), k)
if len(sys.argv) > 1:
    import difflib
    k = sys.argv[1]
    sys.stdout.writelines(difflib.unified_diff(a.get(k, []), b.get(k, []), 'old', 'new', n=1))
