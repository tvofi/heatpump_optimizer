#!/usr/bin/env python3
"""R10-ARCH-DOCS (#2395): the enumerating commands behind the complete-set sentences of the two wiring pages.

    python3 dev/audit/harnesses/r10_arch_docs_enumerate.py

THE RULE. A sentence of docs/architecture.md or dev/README.md that says all, each, every, no, only, or gives a
count, is a claim about a whole set, and reading one member cannot support it. Each `## N<k>` block below is the
command that lists the set such a sentence is about, over the whole tree: the modules that name the state machine,
the jobs and triggers of every workflow file, the beat's jobs, the writers of the hold list, the ledger's kinds,
the importers and call sites a "one owner" bullet names, every executable reference from one script the
machinery figure draws to another, and each such script's writes to each store the figure draws. It prints what the tree holds and judges nothing: the pull-request body sets
each block beside its sentence, and a block that is empty where the sentence needs a member, or holds a member the
sentence denies, is the finding. Where a block is a zero it carries a control that is not zero.

Prints the blocks in order. Exit is bash's: 0 unless a command of the script could not run.
"""
from __future__ import annotations

import subprocess
import sys


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
SCRIPT = r'''
P=custom_components/heatpump_optimizer; S=tools/audit/seat; W=.github/workflows
echo "## N1 modules that name the state machine in code (not a comment line)"
git grep -nE 'hass\.states\b|\bstates\.(get|keys)\(' -- "$P/*.py" | grep -vE '^[^:]+:[0-9]+:\s*#' | cut -d: -f1 | sort | uniq -c
echo "## N2 ci.yml: events, jobs with needs and uses, prelude outputs"
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('.github/workflows/ci.yml'))
print('events:', sorted(d[True]))
for k, v in d['jobs'].items():
    print(' ', k, '| needs', v.get('needs'), '| uses', v.get('uses'), '| workset-gated', 'workset' in str(v.get('if')))
print('prelude outputs:', list(d['jobs']['prelude']['outputs']))
PY
echo "## N3 every workflow file: its triggers"
python3 - <<'PY'
import glob, yaml
for f in sorted(glob.glob('.github/workflows/*.yml')):
    on = yaml.safe_load(open(f))[True]
    on = on if isinstance(on, dict) else {k: None for k in ([on] if isinstance(on, str) else on)}
    print(' ', f.split('/')[-1], {k: {a: b for a, b in (v if isinstance(v, dict) else {}).items() if a in ('branches', 'tags', 'paths', 'workflows')} for k, v in on.items()})
PY
echo "## N4 units ci.yml calls that lack workflow_call, or carry a pull-request trigger (expect none)"
for u in $(grep -oE 'uses: \./\.github/workflows/[a-z-]+\.yml' $W/ci.yml | sed 's|uses: \./||'); do grep -qE '^  workflow_call:' $u || echo "NO workflow_call $u"; grep -HnE '^  pull_request(_target|_review)?:' $u; done; echo "units called: $(grep -cE 'uses: \./\.github/workflows/' $W/ci.yml)"
echo "## N5 files with a pull-request trigger"; grep -lE '^  (pull_request|pull_request_target|pull_request_review):' $W/*.yml
echo "## N6 workflow files not named on dev/README.md (expect none)"; for f in $W/*.yml; do grep -qF "$f" dev/README.md || echo "NOT ON PAGE $f"; done
echo "## N7 beat jobs: the set of script each job's argv runs, and the job names"
python3 - <<'PY'
import json
d = json.load(open('tools/audit/seat/beatd.jobs.json')); jobs = d['jobs'] if isinstance(d, dict) else d
print(' ', sorted({j['argv'][2] for j in jobs}), [j['argv'][3] for j in jobs])
PY
echo "## N8 beat table and beat_jobs.py: lines naming the relay, the tick, the train, the heartbeat, roster_sync (control: replan.py)"
for pat in 'cloud_relay|orchestrator_tick|merge_train|heartbeat\.sh' 'roster_sync' 'replan\.py'; do for f in $S/beatd.jobs.json $S/beat_jobs.py; do echo "  $pat in $f: $(grep -cE "$pat" $f)"; done; done
grep -nE 'cloud_relay|orchestrator_tick|merge_train|heartbeat\.sh' $S/beat_jobs.py | cut -c1-140
echo "## N9 writes of the hold list under tools/ and .github/ (a redirect into the file)"
git grep -nE 'cloud-handoff-hold' -- tools .github | grep -E '> *"?\$[A-Za-z/{}"]*cloud-handoff-hold|> "\$\(hold_file\)"' | cut -c1-150
git grep -nE '>>? *"?\$\(hold_file\)|>>? *"?\$hf\b' -- tools .github | cut -c1-150
echo "## N10 ledger KINDS by class"
python3 - <<'PY'
import re
src = open('tools/audit/seat/ledger.py').read()
blk = src[src.index('KINDS = {'):]; blk = blk[:blk.index('}')]
pairs = re.findall(r'"([a-z-]+)": "(derived|event)"', blk)
print('  events:', [k for k, c in pairs if c == 'event']); print('  derived:', len([1 for k, c in pairs if c == 'derived']), 'kinds')
PY
echo "## N11 production opens of train-stop (control: postmerge-owed)"
for k in train-stop postmerge-owed; do echo "  $k: $(git grep -nE "\"open\", \"$k\"|ledger_open $k|ledger open $k" -- tools .github | grep -vcE 'self.test|fixture')"; done
echo "## N12 assignments of the thermal parameters"; git grep -nE '_thermal_params = |_thermal_model\.params = ' -- $P | cut -c1-150
echo "## N13 learner modules: homeassistant, store and coordinator imports at module level"
for m in accuracy comfort_learning curve_learning defrost dhw_draws dhw_learning drift snapshots sysid; do echo "  $m: ha=$(grep -cE '^(from|import) +homeassistant' $P/$m.py) store=$(grep -cE '^from +\.store' $P/$m.py) coordinator=$(grep -cE '^from +\.coordinator|^from +\. +import .*\bcoordinator\b' $P/$m.py)"; done
echo "## N14 heat_energy.py homeassistant imports (control: accuracy.py), and its importers"
echo "  heat_energy=$(grep -cE 'homeassistant' $P/heat_energy.py | tr -d '\n') lines naming homeassistant, import lines $(grep -cE '^(from|import) +homeassistant' $P/heat_energy.py); accuracy import lines $(grep -cE '^(from|import) +homeassistant' $P/accuracy.py)"; git grep -nE '^(from|import) .*\bheat_energy\b' -- $P
echo "## N15 calls of model_restart_advice and house_loss_converged"; git grep -nE '(model_restart_advice|house_loss_converged)\(' -- $P | grep -v ':def ' | cut -c1-130
echo "## N16 config_flow.py: every form shown, and whether its schema is the registry's"
grep -nE 'async_show_form\(' $P/config_flow.py | while IFS=: read n rest; do echo "  $n $(sed -n "$((n)),$((n+6))p" $P/config_flow.py | grep -oE 'data_schema=[A-Za-z_.]+\(?' | head -1)"; done; grep -nE '^class .*Flow' $P/config_flow.py | cut -c1-120
echo "## N17 dependency-graph.yml path filters"; python3 -c "import yaml;print(' ',yaml.safe_load(open('.github/workflows/dependency-graph.yml'))[True]['push']['paths'])"
echo "## N18 executable references from one drawn script to another (a literal path, a path under a variable, an import or a module call; comment lines dropped)"
A="cloud_dispatch.py tick_loop.sh cloud_relay.sh bus.sh orchestrator_tick.py beat_jobs.py state_docs.py plan_page.py roster_queue.py roster_edit.py open_pr.sh merge_train.py postmerge.py roster_sync.py heartbeat.sh"
for a in $A; do for b in $A replan.py open_driver.py carry_fold.py; do [ "$a" = "$b" ] && continue; s=${b%.*}
  n=$(grep -nE "(^\s*import +$s\b|^\s*from +$s +import|/ *\"$s\.(py|sh)\"|HERE/$s\.(py|sh)|seat/$s\.(py|sh)|plan/$s\.py|\\$\\{?[A-Za-z_]+\\}?/$s\.(py|sh)|\{[a-z_]+\}/$s\.(py|sh)|tool\(\"$s\"\)|\b$s\.[a-z_]+\()" $S/$a | grep -vE '^[0-9]+:\s*#' | cut -d: -f1 | tr '\n' ' ')
  [ -n "$n" ] && echo "  $a -> $b: lines $n"; done; done
echo "## N19 the figure's arrows and the table's rows"
echo "  arrows $(grep -cE '^    \w+ -->\|"(runs|writes)"\| \w+$' dev/README.md) rows $(grep -cE '^\| [^|]+ \| (runs|writes) \| ' dev/README.md)"
echo "## N20 writes from each drawn script to each drawn store, outside self-tests and docstrings: DRAWN when the figure has that arrow"
python3 - <<'PY'
import ast, re
from pathlib import Path
page = Path('dev/README.md').read_text()
fig = page[page.index('flowchart TB'):]; fig = fig[:fig.index('```')]
label = dict(re.findall(r'^ {8}(\w+)[\[\(]+"([^"<]+)', fig, re.M))
arrows = set(re.findall(r'^    (\w+) -->\|"(runs|writes)"\| (\w+)$', fig, re.M))
files = {}
for nid, text in label.items():
    if re.fullmatch(r'[a-z_]+\.(py|sh)', text.split()[0]) and Path('tools/audit/seat', text.split()[0]).is_file():
        files.setdefault(text.split()[0], set()).add(nid)
PUSH = r'(\bpush\b|"push")'
STORES = {
    'dref': PUSH + r'.*refs/heads/(\{ref\}|dispatch/)',
    'drec': r'>>? *"?\$S/dispatched',
    'bus': r'^\s*append_commit |' + PUSH + r'.*refs/heads/(review|verdict|design|probe|handoff)',
    'ledger': r'ledger\.py"?,? +"?(open|close|attempt)\b|\bledger_(open|close)\b|"(open|close|attempt)", "[a-z][a-z-]+"',
    'pr': r'"gh", "pr", "(create|edit|comment|close|ready)"|\bgh pr (create|edit|comment|close|ready)\b|update_pr\.sh|tool\("app_push"\)|"\$_push"|\$POSTER',
    'main': r'"--merge"|\bpr merge\b',
    'thold': r'git/refs/heads/train-hold',
    'hbref': PUSH + r'.*refs/heads/\$REF|"\$c:refs/heads/\$REF"',
    'board': r'mv -f "\$tmp" "\$out"',
    'roster': PUSH + r'.*refs/heads/\{branch\}|refspec = f"\{head\}:refs/heads/\{branch\}"',
    'sdoc': r'refs/heads/\{state_ref\}',
    'hold': r'>>? *"?\$(\(hold_file\)|hf\b)',
}
TESTY = re.compile(r'self_?test|_checks$|^_?test|fixture|world')
def skipped(path, text):
    """Line numbers inside a self-test function or a docstring."""
    out = set()
    if path.suffix == '.py':
        tree = ast.parse(text)
        for d in ast.walk(tree):
            if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if not isinstance(d, ast.Module) and TESTY.search(d.name):
                    out.update(range(d.lineno, d.end_lineno + 1))
                body = d.body
                if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], 'value', None), ast.Constant) \
                        and isinstance(body[0].value.value, str):
                    out.update(range(body[0].lineno, body[0].end_lineno + 1))
    else:
        start = None
        for i, l in enumerate(text.splitlines(), 1):
            m = re.match(r'^([a-z_]+)\(\) *\{?\s*$', l)
            if m and TESTY.search(m.group(1)):
                start = i
            if start and l.startswith('}'):
                out.update(range(start, i + 1)); start = None
    return out
for fname, nids in sorted(files.items()):
    path = Path('tools/audit/seat', fname); text = path.read_text(); skip = skipped(path, text)
    lines = text.splitlines()
    for st, pat in STORES.items():
        hits = [i for i, l in enumerate(lines, 1) if i not in skip and not l.lstrip().startswith('#') and re.search(pat, l)]
        if hits:
            state = 'DRAWN' if any((n, 'writes', st) in arrows for n in nids) else 'UNDRAWN'
            print(f'  {state} {fname} -> {label[st].strip()}: lines {" ".join(map(str, hits))}')
PY
'''


if __name__ == "__main__":
    sys.exit(subprocess.run(["bash", "-s"], input=SCRIPT, text=True, cwd=ROOT).returncode)
