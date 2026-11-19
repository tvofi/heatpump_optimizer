#!/usr/bin/env python3
"""D5-s10: are session-start.sh's header claims about its own report true -- "The fifth and sixth lines, and the
trap the other three could not see"?

Metric: behind_pos / tip_pos = 1-based line positions of `behind main:` and `origin/main at:` in the output of
.claude/hooks/session-start.sh:report, run for real in a scratch repository; claimed_pos = the ordinals the header
states (fifth, sixth); other_items = how many items the header's own "WHY THESE" list carries besides
"being BEHIND main" (claimed: three). mismatches = (behind_pos != 5) + (tip_pos != 6) + (other_items != 3).
Count key: the line positions in the report the hook prints, and the item rows of the hook's own header.

Command (from the export root; --repo is any git checkout holding --ref):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s10/session_start_lines.py \
      --repo /home/user/heatpump_optimizer --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 [--perturb]
Expected at baseline 92d38ecb (box B12, round 11): behind_pos=4 tip_pos=5 other_items=4 mismatches=3, exact.
Perturbation: --perturb inserts one printf line in report() before `behind main:` in the hook copy: behind_pos
and tip_pos each move up by one (4 -> 5, 5 -> 6) and mismatches falls 3 -> 1.
Writes only under a mkdtemp root.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, re, shutil, subprocess, tempfile, time
from pathlib import Path

HOOK = ".claude/hooks/session-start.sh"
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7}
NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    c0, h0 = time.process_time(), time.thread_time()
    hook = subprocess.check_output(["git", "-C", a.repo, "show", f"{a.ref}:{HOOK}"], text=True)
    header = hook.split("WHY THESE", 1)[1].split("THE DISTANCE LINES", 1)[0]
    # an item row starts at column 4; its description column (and every continuation row) at column 28
    items = [l[4:28].strip() for l in header.splitlines() if re.match(r"^#   \S", l)]
    m = re.search(r"The (\w+) and (\w+) lines, and the trap the other (\w+)", " ".join(re.sub(r"(?m)^#\s*", " ", header).split()))
    claimed = (ORD[m.group(1).lower()], ORD[m.group(2).lower()], NUM[m.group(3).lower()])
    if a.perturb:
        hook = hook.replace("  if [ -n \"$behind\" ]; then\n    printf 'behind main:",
                            "  printf 'perturb:        x\\n'\n  if [ -n \"$behind\" ]; then\n    printf 'behind main:", 1)
    root = Path(tempfile.mkdtemp(prefix="d5s10_ss_"))
    try:
        t = root / "repo"
        (t / ".claude/hooks").mkdir(parents=True)
        (t / HOOK).write_text(hook)
        g = lambda *x: subprocess.run(["git", "-C", str(t), *x], capture_output=True, text=True)
        g("init", "-q", "-b", "feature")
        g("add", "-A")
        g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed")
        g("update-ref", "refs/remotes/origin/main", "HEAD")
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(t), HPO_PREFIX=str(root / "none"))
        env.pop("HPO_SEAT_ROLE", None)
        out = subprocess.run(["bash", str(t / HOOK)], cwd=t, env=env, text=True, capture_output=True, stdin=subprocess.DEVNULL).stdout
        lines = out.splitlines()
        pos = lambda pre: next((i + 1 for i, l in enumerate(lines) if l.startswith(pre)), 0)
        behind, tip = pos("behind main:"), pos("origin/main at:")
        others = [i for i in items if not i.lower().startswith("being behind")]
        print(f"RESULT report_lines={len(lines)} count")
        print(f"RESULT behind_pos={behind} line")
        print(f"RESULT tip_pos={tip} line")
        print(f"RESULT claimed_pos={claimed[0]},{claimed[1]} line")
        print(f"RESULT header_items={len(items)} count ({'; '.join(items)})")
        print(f"RESULT other_items={len(others)} count (claimed {claimed[2]})")
        # the header also cites "HANDOVER trap 11": is there an 11th numbered trap in the one handover?
        ho = subprocess.run(["git", "-C", a.repo, "show", f"{a.ref}:dev/programme/HANDOVER.md"], capture_output=True, text=True).stdout
        traps = ho.split("## Traps that cost a session", 1)[-1] if "## Traps" in ho else ""
        found = bool(re.search(r"(?m)^\s*(?:11[.)]\s|.*\btrap 11\b)", traps))
        print(f"RESULT handover_trap_11_found={int(found)} bool (null: the traps section exists={int(bool(traps))})")
        mism = (behind != claimed[0]) + (tip != claimed[1]) + (len(others) != claimed[2])
        print(f"RESULT mismatches={mism} count")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    pc = time.process_time() - c0
    print(f"RESULT thread_factor={pc / max(time.thread_time() - h0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
