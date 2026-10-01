"""R9-F10.9b: which coverage-stage scripts the new rule measures, per merged PR.

For each `Merge pull request #N` on origin/main's first-parent line (N >= 1795),
check out the merge M in a scratch worktree and run that tree's own
`tests/closure.py select --diff M^1 --json`; a script the plan skips is reused,
every other one measured. Seconds are main's coverage job at 90335cbd
(run 36889470932, job 110461123411, its `ran tests/<s>.py ... wall=` lines).
"""
import json, os, re, subprocess, tempfile
COV = {'features': 854, 'entities': 122, 'doc_claims': 5, 'wood_advisor': 1,
       'config_flow_steps': 44, 'structure': 9, 'typing_ruler': 0, 'ha_contract': 0,
       'manual_plan': 10, 'open_meteo': 1, 'solar_alignment': 1, 'guard_pins': 1,
       'finite_boundary': 105, 'deployment_shape': 4, 'golden': 253, 'plan_view': 2,
       'frontend': 0}
def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout
for line in git('log', '--first-parent', '--merges', '--format=%H %s', '-40', 'origin/main').splitlines():
    h, subj = line.split(' ', 1)
    m = re.search(r'#(\d+)', subj)
    if not m or int(m.group(1)) < 1795:
        continue
    wt = tempfile.mkdtemp()
    subprocess.run(['git', 'worktree', 'add', '-q', '--detach', wt, h], capture_output=True)
    try:
        out = subprocess.run(['python3', 'tests/closure.py', 'select', '--diff', h + '^1', '--json'],
                             cwd=wt, capture_output=True, text=True,
                             env={**os.environ, 'PYTHONPATH': 'tests/hastub'})
        plan = json.loads(out.stdout)
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', wt], capture_output=True)
    skip = plan.get('skip', {}) if plan['mode'] == 'scoped' else {}
    run = [s for s in COV if f'tests/{s}.py' not in skip]
    print(f"#{m.group(1)} {h[:8]} {plan['mode']:6} measured {len(run):2}/17 "
          f"{sum(COV[s] for s in run) / 60:5.1f} of {sum(COV.values()) / 60:.1f} min")
