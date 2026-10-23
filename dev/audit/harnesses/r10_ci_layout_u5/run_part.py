#!/usr/bin/env python3
"""R10-CI-LAYOUT P2b, unit U5b: tests/run.sh's RUN_PART switch, driven.

    python3 dev/audit/harnesses/r10_ci_layout_u5/run_part.py [--mutant]

Runs this tree's tests/run.sh serially (GATE_JOBS=1, GATE_SCOPE=full) with a
stub PYTHON that runs nothing, once per part, and reads which test scripts the
run executed (a `##########` banner) and which it skipped on purpose (a
`SKIP:` line), and its exit:

  RUN_PART unset   every wired script runs, the architecture-score pair too
                   (the null: a local run is unchanged);
  RUN_PART=fast    the pair is skipped by name, naming `tests / arch-instrument`,
                   and every other script runs exactly as unset;
  RUN_PART=arch    the pair runs and nothing else, and the run's own
                   accounting passes (rc 0).

--mutant drops the fast part's skip (the payment) from a copy of run.sh: the
fast part must then read as unchanged from unset, which this check refuses.
Exit 0 when every line reads as stated (under --mutant: when the fast line is
refused and only it).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAIR = {"tests/arch_score.py", "tests/arch_score_head.py"}
SKIP_FAST = re.compile(r'(  if \[ "\$RUN_PART" = fast \]; then\n).*?(  else\n)(.*?)(  fi\n)', re.S)


def drive(run_sh: Path, part: str | None) -> tuple[int, set[str], set[str], str]:
    with tempfile.TemporaryDirectory() as td:
        stub = Path(td) / "py"
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
        env = {k: v for k, v in os.environ.items() if k not in ("RUN_PART", "GATE_SCOPE", "HPO_CI_METRICS")}
        env.update(PYTHON=str(stub), GATE_JOBS="1", GATE_SCOPE="full", TMPDIR=td)
        if part is not None:
            env["RUN_PART"] = part
        p = subprocess.run(["bash", str(run_sh)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    out = p.stdout + p.stderr
    ran = {m for line in out.splitlines() if line.startswith("########## ")
           for m in re.findall(r"tests/[\w.-]+\.(?:py|mjs)", line)[:1]
           if not line.startswith("########## gate_lock")}
    skipped = set(re.findall(r"^SKIP: (tests/[\w.-]+\.(?:py|mjs))", out, re.M))
    return p.returncode, ran, skipped, out


def main(argv: list[str]) -> int:
    mutant = "--mutant" in argv
    run_sh = ROOT / "tests" / "run.sh"
    with tempfile.TemporaryDirectory() as td:
        if mutant:
            text = run_sh.read_text()
            if len(SKIP_FAST.findall(text)) != 1:
                print("FAIL --mutant: the fast part's skip branch is not where this harness looks")
                return 2
            run_sh = Path(td) / "run.sh"
            # Keep the `else` arm's lines (the pair's `run` lines) on both sides.
            run_sh.write_text(SKIP_FAST.sub(lambda m: m.group(3), text))
            shutil.copymode(ROOT / "tests" / "run.sh", run_sh)
            # run.sh cds to its own parent's parent; run it from the tree's tests/.
            real = ROOT / "tests" / f".run_part_mutant_{os.getpid()}.sh"
            real.write_text(run_sh.read_text())
            run_sh = real
        try:
            rc0, ran0, sk0, out0 = drive(run_sh, None)
            rcf, ranf, skf, outf = drive(run_sh, "fast")
            rca, rana, ska, outa = drive(run_sh, "arch")
        finally:
            if mutant:
                run_sh.unlink()
    lines = []

    def say(label: str, ok: bool, detail: str) -> None:
        lines.append((ok, label))
        print(f"{'ok  ' if ok else 'FAIL'} {label}: {detail}")

    say("unset: the pair runs (null)", PAIR <= ran0, f"rc={rc0} ran {len(ran0)} script(s), pair ran: {sorted(PAIR & ran0)}")
    named = all(re.search(rf"^SKIP: {re.escape(s)} \(.*tests / arch-instrument", outf, re.M) for s in PAIR)
    say("fast: the pair is skipped by name, and nothing else moves",
        rcf == rc0 and PAIR <= skf and not (PAIR & ranf) and named and ranf == ran0 - PAIR,
        f"rc={rcf} ran {len(ranf)}, pair skipped {sorted(PAIR & skf)}, named the job: {named}, "
        f"other scripts as unset: {ranf == ran0 - PAIR}")
    say("arch: only the pair runs, and its accounting passes",
        rca == 0 and rana == PAIR, f"rc={rca} ran {sorted(rana)}")
    bad = [label for ok, label in lines if not ok]
    if mutant:
        want = ["fast: the pair is skipped by name, and nothing else moves"]
        print(f"MUTANT {'KILLED' if bad == want else 'SURVIVED'}: refused {bad}")
        return 0 if bad == want else 1
    print(f"RESULT {'PASS' if not bad else 'FAIL'} ({len(bad)} failed)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
