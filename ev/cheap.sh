#!/bin/bash
cd $HOME/wt/head; O=$HOME/W/ev
t(){ n=$1; shift; "$@" > $O/$n.log 2>&1; echo "rc=$? $n: $(python3 -c "import sys;l=[x for x in open('$O/$n.log',errors='replace').read().splitlines() if x.strip()];print(' || '.join(x[:260] for x in l[-3:]))")"; }
t structure python3 tests/structure.py
t ci_predict python3 tools/pr/ci_predict.py
t brief_lint node tools/policy/brief_lint.mjs
t entities env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py
t env_drift env PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main
t plan_view env PYTHONPATH=tests/hastub python3 tests/plan_view.py
t card node tests/card.mjs
t no_copies python3 tests/closure.py no-copies
echo CHEAPDONE
