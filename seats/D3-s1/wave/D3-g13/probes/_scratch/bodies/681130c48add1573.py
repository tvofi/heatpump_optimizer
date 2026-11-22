OLD = "seconds_on += max(0.0, open_for) if open_for is not None else 0.0"
NEW = "seconds_on += (0.0) if open_for is not None else 0.0"
MUT = mutated(defrost, defrost.DefrostWindow.peek, OLD, NEW)
moved = []
for name, (seq, at) in SEQS.items():
    b, m = drive(seq, at), drive(seq, at, MUT)
    print(f"RESULT {name}: baseline={b} mutant={m}")
    if b != m:
        moved.append(name)
b = drive(*SEQS["carried_level_reobserved"])
m = drive(*SEQS["carried_level_reobserved"], peek_fn=MUT)
print(f"RESULT duty_baseline={b[0]}")
print(f"RESULT duty_mutant={m[0]}")
print(f"RESULT observed_baseline={int(b[2])} mutant={int(m[2])}")
print(f"RESULT any_defrost_baseline={int(b[1] > 0 or b[0] > 0)} mutant={int(m[1] > 0 or m[0] > 0)}")
print(f"RESULT sequences_moved={len(moved)} of {len(SEQS)} ({','.join(moved)})")
# Null control: a window whose flag closed before the peek (on_off_peek) and one never on: unchanged.
print(f"RESULT null_delta={int(drive(*SEQS['on_off_peek']) != drive(*SEQS['on_off_peek'], peek_fn=MUT))} count")
footer()
