# D3-top6 result (local run; replaces the cloud box BLOCKED.md, which is stale)

Final, 2026-11-19T06:30:57Z. Seat D3-s1, step D3.M3.

- T1: M22 re-drive SURVIVED in the fast net, then KILLED in the T3 full net.
- T2: six full gates. KILLED: fb16, 4b37, bdcf, 0e17 (local and cloud agree), and 8e82 (cloud gate, killed by features.py, cloud null green; the local repeat was stopped while it waited for a heavy slot). SURVIVED: d931 (tariff.py:744), finding D3-s1-02 (low).
- T3: the t3-p1..3 boxes never moved. The original cloud box D3-top6 ran the full net instead: 35 results, 16 SURVIVED. It then full-gated 10 of the 15 remaining survivors, and all 10 SURVIVED (carried as leads; probes are owed).
- Totals: universe 35, examined 30, not reached 5 (the five survivors still owe a full gate, listed in REPORT.md Unfinished). Kills 19, survivors 16 (11 confirmed by a full gate, 5 owe one).
- Findings: 1 (D3-s1-02). check_report: ok D3-s1 (seats/D3-s1/CHECK.txt).
