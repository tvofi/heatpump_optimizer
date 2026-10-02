"""Fix-review 1848 mutants (reviewer's own runner). Usage: mutants.py <ID> <worktree>"""
import sys, pathlib
MT = "tests/mutation_table.py"; WF = ".github/workflows/tests.yml"; NS = "tests/nightly_status.py"
M = {
 "M0": [(MT, 'DRAIN_SUBJECT = "ci: record nightly kills"\n', 'DRAIN_SUBJECT = "ci: record nightly kills"\n# reviewer null control: a comment only\n')],
 "M1": [(MT, "pool.extend(dict(s, drivers=drivers) for s in group)", "pool.extend(dict(s, drivers=drivers) for s in group[:1])")],
 "M2": [(MT, "if not drivers or len(pool) + len(group) > cap:", "if len(pool) + len(group) > cap:")],
 "M3": [(MT, 'f"{seed}:{a}".encode()', 'f"0:{a}".encode()')],
 "M4": [(MT, "reads = [script, *closures.get(script, ())]", "reads = [script]")],
 "M5": [(MT, "    if measured_at != head:\n        if changed is None:", "    if False:\n        if changed is None:")],
 "M6": [(MT, 'if code != "??" or not path.startswith(DRAIN_ROWS):', 'if not path.startswith(DRAIN_ROWS):')],
 "M7": [(MT, "ok = status in DRAIN_QUIET", "ok = True")],
 "M8": [(MT,
   '    d = Path(pins_dir)\n    try:\n        status = (d / "status").read_text().strip()\n    except OSError:\n        return "skip-no-measurement"\n    if status != "measured":\n        return status or "skip-no-measurement"\n    try:\n        measured_at = (d / "head").read_text().strip()\n        pins = json.loads((d / "pins.json").read_text())\n    except (OSError, ValueError):\n        return "skip-no-measurement"\n    if measured_at != head:\n        if changed is None:',
   '    d = Path(pins_dir)\n    try:\n        measured_at = (d / "head").read_text().strip()\n        pins = json.loads((d / "pins.json").read_text())\n        status = (d / "status").read_text().strip()\n    except (OSError, ValueError):\n        return "skip-no-measurement"\n    if status != "measured":\n        return status or "skip-no-measurement"\n    if measured_at != head:\n        if changed is None:')],
 # reviewer's own
 "A1": [(WF, "  mutation-ledger:\n    needs: [recheck-gate]\n    if: >-\n      always() && (\n        github.event_name == 'schedule'\n",
             "  mutation-ledger:\n    needs: [recheck-gate]\n    if: >-\n      always() && (\n        github.event_name == 'schedule'\n        || github.event_name == 'pull_request'\n")],
 "A2": [(WF, "      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5\n        with:\n          ref: main\n          fetch-depth: 0\n",
             "      - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5\n        with:\n          fetch-depth: 0\n"),
        (WF, "fetch -q origin main && git reset -q --hard origin/main ||", "fetch -q origin main ||")],
 "A3": [(WF, '          echo "::add-mask::$tok"\n', "")],
 "A5": [(MT, '(c.endswith("/") and path.startswith(c))', 'False')],
 "A6": [(MT, '        if changed is None:\n            return "skip-head-moved"\n', '        if changed is None:\n            changed = []\n')],
 "A7": [(WF, "if diff is not None and diff.returncode == 0", "if diff is not None")],
 "A9": [(NS, 'REQUIRED_LANES = ("mutation-ledger", "mutation-nightly", "nightly-ha", "slow")', 'REQUIRED_LANES = ("mutation-nightly", "nightly-ha", "slow")')],
 "A10": [(WF, "    if: always() && needs.mutation-ledger.result == 'success'\n", "    if: always() && needs.mutation-ledger.result == 'success' && (github.event_name != 'workflow_dispatch' || github.ref == 'refs/heads/main')\n")],
}

M.update({
 "R_A7": [(MT, "    return diff.stdout.split() if diff.returncode == 0 else None", "    return diff.stdout.split()")],
 "R_B1a": [(WF, "      always() && github.ref == 'refs/heads/main' && (\n        github.event_name == 'schedule'", "      always() && (\n        github.event_name == 'schedule'")],
 "R_B1b": [(WF, "      always() && github.ref == 'refs/heads/main'\n      && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')", "      always()\n      && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')")],
 "R_B1c": [(WF, "      && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')\n", "      && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch' || github.event_name == 'push')\n")],
 "R_B2a": [(WF, "    environment: ledger\n", "")],
 "R_B2b": [(MT, '               "skip-nothing-drivable")', '               "skip-nothing-drivable", "skip-no-writer")')],
 "R_P1": [(MT, '    if git("rev-parse", "HEAD^") != git("rev-parse", "origin/main"):\n        out.append("HEAD\'s parent is not origin/main")\n', '')],
 "R_P2": [(MT, '        if code != "A" or not path.startswith(DRAIN_ROWS):', '        if not path.startswith(DRAIN_ROWS):')],
 "R_P3": [(MT, '    if git("log", "-1", "--format=%s", "HEAD") != DRAIN_SUBJECT:\n', '    if False:\n')],
 "R_P4": [(MT, '    if len(commits) != 1:', '    if len(commits) > 1 and False:')],
 "R_P5": [(WF, "bad = m.drain_push_problems(); print", "bad = []; print")],
 "R_P6": [(MT, 'return r.stdout.strip() if r.returncode == 0 else "\\0"', 'return r.stdout.strip()')],
})

mid, wt = sys.argv[1], pathlib.Path(sys.argv[2])
for f, old, new in M[mid]:
    p = wt / f; t = p.read_text(); n = t.count(old)
    assert n == 1, f"{mid}: {f}: {n} matches"
    p.write_text(t.replace(old, new))
print(f"{mid} applied")
