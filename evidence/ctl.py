import sys; sys.path[:0]=['tests']
import replay as r
c=r.controls(); bad=[x for x in c if not x[1]]
print(len(c), len(bad), [x[0] for x in bad])
for x in c:
    if 'headroom' in x[0]: print(x[0], x[1])
sys.exit(1 if bad else 0)
