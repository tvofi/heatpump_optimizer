M = [
("P1 guardrail until = last window's from", "print(guardrail(verdicts, wins[-1][2], a.guardrail, a.p0))", "print(guardrail(verdicts, wins[-1][1], a.guardrail, a.p0))"),
("P2 guardrail until = first window's until", "print(guardrail(verdicts, wins[-1][2], a.guardrail, a.p0))", "print(guardrail(verdicts, wins[0][2], a.guardrail, a.p0))"),
("P3 guardrail N+1", "print(guardrail(verdicts, wins[-1][2], a.guardrail, a.p0))", "print(guardrail(verdicts, wins[-1][2], a.guardrail + 1, a.p0))"),
("N1", "lines < 600", "lines < 700"),
("N3 key PR number first", "key=lambda p: (first[p], p))[-n:]", "key=lambda p: (p, first[p]))[-n:]"),
]
