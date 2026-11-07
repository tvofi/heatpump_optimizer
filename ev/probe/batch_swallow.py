# Reviewer's own probe: a FIRST TERM landing in batch 1's normal-completion unwind.
import sys, time, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[3])
import merge_train as m
rec = open(sys.argv[1], 'a')
def run(argv, cwd=None, stdin=None):
    rec.write(' '.join(argv) + '\n'); rec.flush()
    if argv[:3] == ['git', 'worktree', 'remove']:
        rec.write('UNWINDING\n'); rec.flush(); time.sleep(2)
    return 0, ''
if sys.argv[2] == 'base':
    m.Train.unwind = lambda self: (self.release_worktrees(), self.hold_release())
m.queue_batches = lambda q: [[{"pr": 1}], [{"pr": 2}]]
m.Train.queue_open = lambda self, b: None
m.Train.queue_close = lambda self: None
m.Train.queue_take = lambda self, b, k: k < len(b)
m.Train.seen_mark = lambda self, *a, **k: None
def _batch(self, b, name, total):
    rec.write(f'BATCH {name}\n'); rec.flush()
    self.held = True; self.made_wts = [Path('/x')]
    return False
m.Train._batch = _batch
t = m.Train('o/r', Path(tempfile.mkdtemp()), None, 'r', (), 1, run=run, log=lambda s: None)
t._seen = {}
m.stop_on_signal()
try:
    rc = t.batch([], 'T')
    rec.write(f'RETURNED rc={rc}\n')
except SystemExit as e:
    rec.write(f'SYSTEMEXIT {e.code}\n')
rec.flush()
