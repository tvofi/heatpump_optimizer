"""Polling REST calls the approved umbrella design adds, per head and per hour.
Usage: python3 -I api_model.py <ev dir>
Measured inputs:
  - verdict-prelude waits: the design's own measure/rev/verdict_wait.txt (probe/design-ci-rev4),
    'naive all' row: sum 8.10 runner-hours over 22 heads (copied to design_verdict_wait.txt here);
  - code heads per hour at peak: heads_per_hour.txt (Tests pull_request runs, 05-07Z: 10, 9, 11).
Assumptions (ESTIMATES, each named): one REST call per poll iteration (a runs listing at the
head; the design's prelude also needs each earlier run's status, which the listing carries);
gate-sweep worst case = its full 600 s bound at 5 s, one sweep per CI run, 2 CI runs per head.
The GITHUB_TOKEN limit, 1,000 requests per hour per repository, is GitHub's documented figure
(not measured here); the 07:46Z refusals read 'API rate limit exceeded for installation'
(incident_ratelimit_lines.txt)."""
import sys, pathlib, re, statistics
EV = pathlib.Path(sys.argv[1])
t = (EV/"design_verdict_wait.txt").read_text()
m = re.search(r"naive\s+all\s+n\s+(\d+).*?sum\s+([\d.]+) runner-hours over (\d+) heads", t)
n_ev, hours, heads = int(m.group(1)), float(m.group(2)), int(m.group(3))
wait_s = hours*3600; per_head = wait_s/heads
hh = [int(x) for x in re.findall(r"T0[567]Z tests_pr_runs=\s*(\d+)", (EV/"heads_per_hour.txt").read_text())]
hph = statistics.median(hh)
print(f"verdict waits: {n_ev} events, {wait_s:.0f} s over {heads} heads = {per_head:.0f} s of polling per head (measured, design)")
print(f"peak code heads per hour: {hh} -> median {hph} (measured)")
print("interval_s  prelude_calls/head  prelude_calls/h@peak  sweep_worst_calls/head  sweep_worst/h@peak  total_worst/h  share_of_1000/h")
for I in (5, 10, 30, 60):
    pc = per_head / I; sw = 2 * (600 / max(I, 5))
    print(f"{I:10d}  {pc:18.0f}  {pc*hph:20.0f}  {sw:22.0f}  {sw*hph:18.0f}  {(pc+sw)*hph:13.0f}  {(pc+sw)*hph/1000:14.2f}")
