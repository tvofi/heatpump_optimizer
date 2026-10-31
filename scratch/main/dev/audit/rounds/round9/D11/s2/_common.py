"""Shared helpers for the D11-s2 harnesses (round 9). Not a harness itself.

Thread pin first, then a temp root under $TMPDIR, a baseline clone, and the
RESULT tail (thread_factor, load1, swapins) the harness contract requires.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import shutil, subprocess, tempfile, time

_T0P, _T0T = time.process_time(), time.thread_time()
NODE = shutil.which("node") or "/opt/node22/bin/node"
ROOT = os.getcwd()


def temp_root(tag):
    d = tempfile.mkdtemp(prefix=f"d11s2-{tag}-")
    os.environ["HPO_PLANDATA"] = os.path.join(d, "plandata")
    os.makedirs(os.environ["HPO_PLANDATA"], exist_ok=True)
    return d


def clone(dest):
    """A throwaway clone of this tree's HEAD, so a perturbation never touches
    the tree under audit (tools/audit/README.md: on-disk edits go in a tree of
    their own)."""
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", ROOT, dest], check=True)
    head = subprocess.run(["git", "-C", dest, "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    return head


def node(clone_dir, *args):
    p = subprocess.run([NODE, *args], cwd=clone_dir, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def tail():
    pt, tt = time.process_time() - _T0P, time.thread_time() - _T0T
    print(f"RESULT thread_factor={pt / tt if tt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = "n/a"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = line.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
