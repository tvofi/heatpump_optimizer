"""PREPR-SLOT-LIVELOCK (R10-PREPR-RESIDUE carry 7): can a nested heavy step queue?

    python3 dev/audit/harnesses/prepr_slot_nested.py            # rc 0: no livelock
    python3 dev/audit/harnesses/prepr_slot_nested.py --mutant   # rc 1: label export removed

An outer prepr holding a slot runs step 3h (`take_slot`, then a nested heavy
step). The nested step must join the outer slot rather than queue for a second
one while the pool is full. The harness drives prepr's REAL `take_slot` (the
function text cut from tools/pr/prepr.sh) against the REAL tests/gate_lock.py in
a private HPO_GATE_LOCK_DIR; it never sets HPO_SLOT_LABEL itself:

  outer    pool 3/4 held by live pids; take_slot takes the free slot and the
           label is whatever the real take path exported.
  nested   with the pool now 4/4, a fresh shell inherits that environment and
           calls take_slot, as a nested heavy step does. It must return at once
           and add no ticket to slot-status's queue.
  bare     the null control: the same nested call WITHOUT the label. It must
           still be waiting at the bound AND slot-status must list its ticket
           in the queue, so the arm differs from `nested` by evidence, not by a
           timeout the other arm also misses.
  warn     the outer take fails (unusable lock dir): no slot, no label (:4192).
           The nested call must not queue either, it only warns.
  static   prepr's `--self-test` branch (what step 3h's nested run executes)
           makes no real take_slot call (the stubbed rows that drive the function in a subshell are not calls), so it cannot queue in any arm.

--mutant deletes the `export HPO_SLOT_LABEL` line from the cut function: the
`nested` arm then queues and the harness exits 1.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
PREPR = ROOT / "tools" / "pr" / "prepr.sh"
BOUND_S = 8


def take_slot_text(mutant: bool) -> str:
    src = PREPR.read_text()
    m = re.search(r"^take_slot\(\) \{.*?^\}\n", src, re.S | re.M)
    assert m, "take_slot not found in prepr.sh"
    text = m.group(0)
    if mutant:
        text = "\n".join(ln for ln in text.splitlines()
                         if "export HPO_SLOT_LABEL" not in ln) + "\n"
    return text


def shell(script: str, env: dict[str, str], bound: int) -> tuple[bool, str]:
    p = subprocess.Popen(["bash", "-c", script], cwd=ROOT, env=env, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         start_new_session=True)
    try:
        out, _ = p.communicate(timeout=bound)
        return True, out
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9)
        out, _ = p.communicate()
        return False, out or ""


def main() -> int:
    mutant = "--mutant" in sys.argv
    fn = take_slot_text(mutant)
    lock = tempfile.mkdtemp(prefix="hpo-slot-nested-")
    holders = [subprocess.Popen(["sleep", "3600"]) for _ in range(3)]
    base = {k: v for k, v in os.environ.items() if k != "HPO_SLOT_LABEL"}
    base["HPO_GATE_LOCK_DIR"] = lock
    # take_slot with prepr's own helpers stubbed to print; python3 stays real.
    pre = ('say() { echo "$1 $2 $3"; }; exit_on_signals() { :; }; '
           'SLOT_LABEL=prepr-$$; SLOT_TAKEN=""\n' + fn)

    def status(env: dict[str, str]) -> str:
        return subprocess.run([sys.executable, "tests/gate_lock.py", "slot-status"],
                              cwd=ROOT, env=env, capture_output=True, text=True).stdout

    def queue(env: dict[str, str]) -> str:
        m = re.search(r"queue=(\S+)", status(env))
        return m.group(1) if m else "?"

    results: dict[str, int] = {}
    try:
        for i, h in enumerate(holders):
            subprocess.run([sys.executable, "tests/gate_lock.py", "slot-take", "--label",
                            f"held-{i}", "--owner-pid", str(h.pid), "--no-wait"],
                           cwd=ROOT, env=base, check=True, capture_output=True)
        # outer: the real take path, in a shell that stays alive (owner pid) while
        # the nested arms run, and prints what it exported.
        outer = subprocess.Popen(
            ["bash", "-c", pre + 'take_slot; echo "LABEL=${HPO_SLOT_LABEL:-}"; '
             'echo READY; exec sleep 3600'],
            cwd=ROOT, env=base, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, start_new_session=True)
        label = ""
        for ln in outer.stdout:  # type: ignore[union-attr]
            if ln.startswith("LABEL="):
                label = ln.strip()[6:]
            if ln.strip() == "READY":
                break
        full = status(base)
        print(full.strip())
        results["pool_full"] = int("4/4 slots held" in full)
        results["outer_exported_label"] = int(bool(label))
        nested_env = {**base, **({"HPO_SLOT_LABEL": label} if label else {})}
        # nested: inherits what the outer exported, pool full.
        t0 = time.time()
        fin, out = shell(pre + "take_slot; echo DONE", nested_env, BOUND_S)
        results["nested_finished"] = int(fin and "DONE" in out)
        results["nested_queue_empty"] = int(queue(base) == "-")
        results["nested_joined"] = int("joined" in out)
        print(f"nested: {out.strip()!r} ({time.time() - t0:.1f}s)")
        # bare: no label, same call.
        bare = subprocess.Popen(["bash", "-c", pre + "take_slot; echo DONE"], cwd=ROOT,
                                env=base, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, start_new_session=True)
        time.sleep(BOUND_S)
        results["bare_finished"] = int(bare.poll() is not None)
        results["bare_queued"] = int(queue(base) != "-")
        print("bare slot-status:", status(base).strip())
        os.killpg(bare.pid, 9)
        os.killpg(outer.pid, 9)
        # warn: the outer take cannot reach a usable lock dir.
        broken = tempfile.NamedTemporaryFile(prefix="hpo-slot-broken-", delete=False)
        wenv = {**base, "HPO_GATE_LOCK_DIR": broken.name}
        fin, out = shell(pre + 'take_slot; echo "LABEL=${HPO_SLOT_LABEL:-}"; take_slot; echo DONE',
                         wenv, BOUND_S * 2)
        results["warn_no_label"] = int("LABEL=\n" in out + "\n" and "LABEL=prepr" not in out)
        results["warn_finished"] = int(fin and "DONE" in out and "WARN" in out)
        print("warn:", out.strip().splitlines()[-3:])
        # static: no take_slot in the --self-test branch.
        src = PREPR.read_text()
        a = src.index('if [ "${1:-}" = "--self-test" ]; then')
        b = src.index("\n  exit 0\nfi\n", a)
        results["selftest_branch_takes_slot"] = int(bool(re.search(r"^\s*take_slot\s*$|&& take_slot$", src[a:b], re.M)))
    finally:
        for h in holders:
            h.kill()
    for k, v in results.items():
        print(f"RESULT {k}={v}")
    want = {"pool_full": 1, "outer_exported_label": 1, "nested_finished": 1,
            "nested_queue_empty": 1, "nested_joined": 1, "bare_finished": 0,
            "bare_queued": 1, "warn_no_label": 1, "warn_finished": 1,
            "selftest_branch_takes_slot": 0}
    bad = {k: (results.get(k), v) for k, v in want.items() if results.get(k) != v}
    print("RESULT verdict=" + ("ok" if not bad else f"FAIL {bad}"))
    return int(bool(bad))


if __name__ == "__main__":
    sys.exit(main())
