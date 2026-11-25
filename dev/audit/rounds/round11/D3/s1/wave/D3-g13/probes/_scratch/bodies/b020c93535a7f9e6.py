OLD = "if self._opened is None:"
NEW = "if False:"
MUT = mutated(defrost, W.peek, OLD, NEW)
moved = []
for name, (seq, at) in SEQS.items():
    b, m = drive(seq, at), drive(seq, at, MUT)
    if b != m:
        moved.append(name)
# fresh window (the only state where _opened is None), peeked with every stamp shape
fresh = {"aware": s(0), "naive": s(0, N0), "none": None, "int": 5, "str": "x"}
for name, now in fresh.items():
    w = W()
    b = W.peek(w, now)
    try:
        m = MUT(w, now)
        m = (m.duty, m.events, m.observed, m.seconds)
    except Exception as exc:  # noqa: BLE001
        m = f"raises {type(exc).__name__}"
    b = (b.duty, b.events, b.observed, b.seconds)
    print(f"RESULT fresh_{name}: baseline={b} mutant={m}")
    if b != m:
        moved.append(f"fresh_{name}")
print(f"RESULT inputs_moved={len(moved)} of {len(SEQS) + len(fresh)} ({','.join(moved)})")
footer()
