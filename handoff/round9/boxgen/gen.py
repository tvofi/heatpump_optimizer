import sys, os
baseline = sys.argv[1]; out = sys.argv[2]
BOXES = {
 'B1': ('D0-s1 D3-s1', 'D5-s1 D6-s1 D10-s1'), 'B2': ('D0-s2 D3-s2', 'D5-s2 D6-s2 D10-s2'),
 'B3': ('D0-s3 D3-s3', 'D11-s1 D11-s2 D13-s1'), 'B4': ('D9-s1 D2-s1', 'D1-s1 D1-s2 D8-s3'),
 'B5': ('D9-s2 D2-s2', 'D1-s3 D1-s5 D7-s3'), 'B6': ('D2-s4 D12-s1 D1-s4', 'D7-s1 D8-s1'),
 'B7': ('D12-s2 D12-s3 D7-s2', 'D2-s3 D8-s2'), 'B8': ('D14-s1 D14-s2 D14-s3', ''),
 'B9': ('D14-s4 D14-s5', 'D4-s2'), 'B10': ('', 'D4-s1 (Chromium, alone)'),
}
PRE = open(os.path.join(os.path.dirname(__file__), 'pre.md')).read()
for b, (h, l) in BOXES.items():
    extra = ''
    if b == 'B10':
        extra = "\n- Chromium: this box runs the browser lane. Install it the way `tools/audit/briefs/D4.md` says since #1632 (npm ci from the committed lock in `tests/pwlane/`); record the Chromium path in BASELINE.md.\n- The leads seat also runs on this box, but only later, in the intake run (`from: \"intake\"`), which the orchestrator starts after every box has pushed. Do not start it yourself.\n"
    if b in ('B3',):
        extra = "\n- D11 and D13 read `main`'s history and the GitHub API (their briefs); use the GitHub MCP tools, read-only.\n"
    if b == 'B8':
        extra = "\n- All three seats are D14, which mutates production to prove detectors move: each isolated seat gets its OWN worktree (the driver does this). Per tools/audit/README.md since #1632: perturb in memory, or make on-disk edits only in the seat's own worktree.\n"
    txt = f"""# Round 9, phase A — box {b}

{PRE}
## Your box
- Round 9, baseline `{baseline}` (the stamped main SHA). Box `{b}`: compute-heavy seats: {h or '(none)'}; light seats: {l or '(none)'}.
- Where results go: the driver's collector pushes your seats' harnesses, REPORT.md files and `tools/audit/round9/reports-{b}.json` to branch `handoff/audit-r9-find-{b}`. That branch is the deliverable.{extra}
## Steps
1. Setup (this container is fresh): in your checkout of github.com/tvofi/heatpump_optimizer run `git fetch --unshallow --tags origin` (skip if already full), `git fetch origin main`, and confirm `git cat-file -e {baseline}^{{commit}}`. Install merge drivers: `python3 tests/env_drift.py --install-merge-driver` and the ledgermerge driver per `.gitattributes` / tests/README.md. Build a Python 3.14 venv with `tests/requirements-ci.txt` (hash-pinned; `--require-hashes`, `--build-constraint tests/requirements-build.txt`) plus orjson at the pin in `tests/requirements-typing.txt` (BASELINE.md needs it since #1632). Node 22 is expected.
2. Run the find driver for your box only. It is the workflow `.claude/workflows/audit-find.js` at origin/main (read it first). Run it with the Workflow tool (scriptPath = that file in your checkout), args: `{{"round": 9, "baseline": "{baseline}", "repo": "<absolute path of your checkout>", "rotation": <parsed tools/audit/rotation.json at origin/main>, "scopes": <parsed tools/audit/scopes.json at origin/main>, "box": "{b}"}}`. tvofi asked for round 9 to run according to the plan, and this driver is the plan's instrument (PLAN.md §3 R1, §4). If the Workflow tool is unavailable to you, run the same thing by hand: do the driver's Prepare step, then start one Agent sub-seat per seat of your box with exactly the prompt the driver's `finder()` builds for it (at most three compute-heavy seats at once), then the collector step. Either way, check the Prepare step's `check_scopes.py` exit code is 0 before any seat runs.
3. When your box has pushed, send the round-9 orchestrator (session `session_01WgT4h2uvK9kbxQbWc5MJis`; if that session is inactive, send it to the coordinator from `mcp__hearthbot__get_channel_session_id`) one message: box, branch, commit, per seat: reported or missing, number of findings, leads raised, and anything unfinished. Post one short reply in your own thread with the same line.
4. Do not verify, judge, dedup or file anything. Do not open, approve or merge pull requests, comment on GitHub or file issues.
"""
    open(os.path.join(out, f'{b}.md'), 'w').write(txt)
print('wrote', len(BOXES))
