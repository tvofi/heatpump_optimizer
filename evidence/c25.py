import sys; sys.path.insert(0, ".")
import review_packet as rp
roster = "".join(f"Carry {i}: text {i}\n" for i in range(27))
hand = roster + "This part: Carries 25, 24, 10 (0-based roster indexes, texts verbatim below).\n"
gen = roster + "Part 2 of 3: build carries 15-17+19-20; the others are later parts dispatched at this part's handoff; answer none of them\n"
body_ok = "Carry 25: a\nCarry 24: b\nCarry 10: c\n"
print("RESULT hand: assigned", rp.prompt_carries(hand), "unnamed(ok body)", rp.unnamed_carries(body_ok, rp.handoff_carries(hand, 27)))
print("RESULT hand null: body missing 10 -> unnamed", rp.unnamed_carries("Carry 25: a\nCarry 24: b\n", rp.handoff_carries(hand, 27)))
print("RESULT hand null: body naming carry 3 (outside part) -> unnamed", rp.unnamed_carries("Carry 3: x\n", rp.handoff_carries(hand, 27)))
g_ok = "".join(f"Carry {i}: x\n" for i in (15,16,17,19,20))
print("RESULT gen: assigned", rp.prompt_carries(gen), "unnamed(ok body)", rp.unnamed_carries(g_ok, rp.handoff_carries(gen, 27)))
print("RESULT gen null: body naming carry 18 (outside part) instead of 20 -> unnamed", rp.unnamed_carries("".join(f"Carry {i}: x\n" for i in (15,16,17,18,19)), rp.handoff_carries(gen, 27)))
print("RESULT nopart null: whole prompt demanded:", len(rp.handoff_carries(roster, 27)), "unnamed for ok body:", len(rp.unnamed_carries(body_ok, rp.handoff_carries(roster, 27))))
# real prompt of this part
import subprocess
p = subprocess.run(["git","show","8602c93e589360f1f6bd07ae0056a94d6b35001b:PROMPT.md"],capture_output=True,text=True).stdout
print("RESULT real p6 PROMPT: prompt_carries", rp.prompt_carries(p))
