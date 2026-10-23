#!/usr/bin/env python3
"""Reviewer's mutant driver for #2668: each mutant in a fresh `git clone --shared` of the head."""
import subprocess, sys, tempfile, pathlib, re

HEAD = "9ef0633bcd6f31482a3ccf0f8da901431e5c6e01"
SRC = "/Users/timmalmstrom/hpo-seats/r10s5/rev-2668/wt"
M = {
    "M1": ("tools/audit/seat/handoff_push.sh",
           'python3 -I "$SEAT/ref_privacy.py" guard --ref "$BR" --commits "$CODE" --over refs/remotes/origin/main \\',
           "true \\", "bash tools/audit/seat/handoff_push.sh --self-test"),
    "M2": ("tools/audit/seat/body_push.sh", 'guard --ref "$REF" --commits "$C"',
           'guard --ref "$REF" --message "body: $TOPIC"', "python3 -I tools/audit/seat/ref_privacy.py --self-test"),
    "M3": ("tools/audit/seat/body_push.sh",
           'python3 -I "$(dirname "$0")/ref_privacy.py" guard --ref "$REF" --commits "$C"', "true",
           "python3 -I tools/audit/seat/ref_privacy.py --self-test"),
    "M4": ("tools/audit/seat/ci_probe.py", "ref_privacy.refusal(short, messages, emails=emails)",
           "ref_privacy.refusal(short)", "python3 -I tools/audit/seat/ci_probe.py --self-test"),
    "M5": ("tools/pr/app_push.sh", '--commits "$3" \\\n    --over refs/remotes/origin/main -C "$1"',
           '--commits "$3" -C "$1"', "bash tools/pr/app_push.sh --self-test"),
    "M6": ("tools/audit/seat/ref_privacy.py", 'fence = ["--remotes"] if over is None else [over]',
           'fence = ["--remotes"]', "python3 -I tools/audit/seat/ref_privacy.py --self-test"),
    "M7": ("tools/audit/seat/pr_args.sh", "pr_args.sh pr_cap.py ref_privacy.py; do", "pr_args.sh pr_cap.py; do",
           "bash tools/audit/seat/pr_args.sh --self-test"),
    "M8": ("tools/audit/seat/r9_rc_bus_fetchhead.sh", '  cp "$HERE/ref_privacy.py" "$W/seat/tools/audit/seat/"\n', "",
           "bash tools/audit/seat/r9_rc_bus_fetchhead.sh tools/audit/seat/handoff_push.sh handoffpush"),
    # reviewer's own: handoff_push judges first-published only (drops --over)
    "M9": ("tools/audit/seat/handoff_push.sh", '--commits "$CODE" --over refs/remotes/origin/main',
           '--commits "$CODE"', "bash tools/audit/seat/handoff_push.sh --self-test"),
}
ev = pathlib.Path(sys.argv[1])
for name in sys.argv[2:] or list(M):
    path, old, new, cmd = M[name]
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", SRC, td + "/c"], check=True)
        subprocess.run(["git", "-C", td + "/c", "checkout", "-q", "--detach", HEAD], check=True)
        p = pathlib.Path(td, "c", path)
        t = p.read_text()
        assert t.count(old) == 1, (name, t.count(old))
        p.write_text(t.replace(old, new))
        r = subprocess.run(cmd, shell=True, cwd=td + "/c", capture_output=True, text=True)
        out = r.stdout + r.stderr
        (ev / f"mutant-{name}.txt").write_text(f"$ {cmd}\nrc={r.returncode}\n{out}")
        fails = [l for l in out.splitlines() if re.search(r"FAIL|failed|verdict:|REFUSE", l)]
        print(f"RESULT {name} rc={r.returncode} :: " + " | ".join(fails[-6:])[:900], flush=True)
