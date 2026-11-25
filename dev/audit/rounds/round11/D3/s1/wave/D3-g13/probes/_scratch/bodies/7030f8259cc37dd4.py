OLD = "if delta is not None and delta > 0:"
NEW = "if delta is not None and delta >= 0:"
MUT = mutated(defrost, W._accrue, OLD, NEW)


class WM(W):
    pass


WM._accrue = MUT
moved = []
# every sequence, peeked and closed, in aware UTC, naive and mixed stamps
for name, (seq, at) in SEQS.items():
    b, m = drive(seq, at), drive(seq, at, cls=WM)
    bc, mc = drive(seq, at, peek_fn=W.close), drive(seq, at, peek_fn=WM.close, cls=WM)
    print(f"RESULT {name}: baseline={b}/{bc} mutant={m}/{mc}")
    if b != m or bc != mc:
        moved.append(name)
# direct: delta exactly 0.0, -0.0, negative, nan-free; the exact float accumulated
for d0 in (0.0, -0.0, -5.0, 1e-9, 7.0):
    wb, wm = W(), WM()
    for w in (wb, wm):
        w._state, w._since, w._seconds_on = True, T0, 3.0
        w._accrue(T0 + timedelta(seconds=d0))
    same = (wb._seconds_on == wm._seconds_on) and (str(wb._seconds_on) == str(wm._seconds_on))
    print(f"RESULT direct_delta={d0}: baseline_seconds_on={wb._seconds_on!r} mutant={wm._seconds_on!r} same={int(same)}")
    if not same:
        moved.append(f"direct{d0}")
print(f"RESULT sequences_moved={len(moved)} of {len(SEQS) + 5} ({','.join(moved)})")
footer()
