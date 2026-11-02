import sys, shutil
from pathlib import Path
src, dst, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
shutil.copytree(src/"tools/audit/seat", dst/"tools/audit/seat"); (dst/"tests").mkdir()
shutil.copy(src/"tests/throwaway_git.py", dst/"tests/throwaway_git.py")
p = dst/"tools/audit/seat/open_driver.py"; s = p.read_text()
P = {
 "old-launch": ("""        cmd = 'o=$0; l=$1; r=$2; shift 2; bash "$o" "$@" > "$l" 2>&1; echo $? > "$r"'
        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"{stem(topic)}.log"), str(rc), topic, sha, title, group]
""", """        cmd = f'bash {self.opener} "$@" > {d}/{topic}.log 2>&1; echo $? > {rc}'
        argv = ["bash", "-c", cmd, "_", topic, sha, title, group]
"""),
 "live-false": ("        elif topic in runs:\n", "        elif False:\n"),
 # reviewer's own 5
 "R-stem-noop": ('    return topic.replace("/", "%2F")\n', '    return topic\n'),
 "R-reap-nostem": ('        rcf = d / f"{stem(t)}.rc"\n', '        rcf = d / f"{t}.rc"\n'),
 "R-unquoted-log": ('> "$l" 2>&1; echo $? > "$r"', '> $l 2>&1; echo $? > $r'),
 "R-backoff-n": ('    return min(BACKOFF_S * 2 ** max(n - 1, 0), BACKOFF_MAX_S)', '    return min(BACKOFF_S * 2 ** max(n, 0), BACKOFF_MAX_S)'),
 "R-seen-on-fail-pop": ('            fails.pop(key, None)\n', ''),
 "R-cap-ge": ('        if live >= cap:\n', '        if live > cap:\n'),
 "R-shift1": ('shift 2; bash', 'shift 1; bash'),
}
if name != "M0":
    o, n = P[name]; assert s.count(o) == 1, (name, s.count(o)); p.write_text(s.replace(o, n))
