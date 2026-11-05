import sys; sys.path[:0]=['tests','tests/hastub']
import replay
r=replay.mask_checks()
bad=[x for x in r if not x[1]]
for n,ok,w in r:
    if 'R10' in n or 'allowlist' in n or 'non_id' in n or 'clean_export' in n or 'planted' in n: print('RESULT', n, ok, w)
print('RESULT mask_checks total', len(r), 'failed', len(bad), [b[0] for b in bad])
