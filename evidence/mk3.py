"""Round-3 reviewer mutant builder: copies tools/audit/seat + tests/throwaway_git.py, applies one plant."""
import sys, shutil
from pathlib import Path
src, dst, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
shutil.copytree(src/"tools/audit/seat", dst/"tools/audit/seat"); (dst/"tests").mkdir()
shutil.copy(src/"tests/throwaway_git.py", dst/"tests/throwaway_git.py")
p = dst/"tools/audit/seat/open_driver.py"; s = p.read_text()
P = {
 # the blocked finding, re-planted exactly as round 2's R-reap-nostem
 "R-reap-nostem": ('        rcf = d / f"{stem(t)}.rc"\n', '        rcf = d / f"{t}.rc"\n'),
 # open side
 "old-launch": ("""        cmd = 'o=$0; l=$1; r=$2; shift 2; bash "$o" "$@" > "$l" 2>&1; echo $? > "$r"'
        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"{stem(topic)}.log"), str(rc), topic, sha, title, group]
""", """        cmd = f'bash {self.opener} "$@" > {d}/{topic}.log 2>&1; echo $? > {rc}'
        argv = ["bash", "-c", cmd, "_", topic, sha, title, group]
"""),
 "R-open-rc-nostem": ('        rc = d / f"{stem(topic)}.rc"\n', '        rc = d / f"{topic}.rc"\n'),
 "R-open-log-nostem": ('str(d / f"{stem(topic)}.log")', 'str(d / f"{topic}.log")'),
 "R-stem-noop": ('    return topic.replace("/", "%2F")\n', '    return topic\n'),
 "R-shift1": ('shift 2; bash', 'shift 1; bash'),
 "R-unquoted-log": ('> "$l" 2>&1; echo $? > "$r"', '> $l 2>&1; echo $? > $r'),
 "R-argv-swap": ('topic, sha, title, group]', 'sha, topic, title, group]'),
 # reap side, beyond the fixer's three
 "R-reap-log-ok": ("reason(d / (stem(t) + '.log'))", "reason(d / (t + '.log'))"),
 "R-fail-log-nostem": ('reason(d / (stem(t) + ".log"))', 'reason(d / (t + ".log"))'),
 "R-reap-alive-dead": ('(None if world.alive(r["pid"]) else -1)', '-1'),
 "R-reap-rc-empty": ('int(rcf.read_text().strip() or -1)', '0'),
}
if name != "M0":
    o, n = P[name]; assert s.count(o) == 1, (name, s.count(o)); p.write_text(s.replace(o, n))

