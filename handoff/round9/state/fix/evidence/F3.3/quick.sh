cd /tmp/claude-0/f33/wt
a=$(grep -n '^R.section("P1/P2/N-min-gap' tests/features.py | cut -d: -f1); b=$(grep -n '^R.section("P5 — sysid' tests/features.py | cut -d: -f1)
{ sed -n 1,85p tests/features.py; echo 'import json as _si_json'; sed -n "$((a-1)),$((b-2))p" tests/features.py; echo 'sys.exit(R.close("F33"))'; } > /tmp/claude-0/f33/_f33_quick.py
cp /tmp/claude-0/f33/_f33_quick.py tests/_f33_quick.py
PYTHONPATH=tests/hastub /tmp/claude-0/f33/venv/bin/python tests/_f33_quick.py 2>&1 | grep -v RuntimeWarn | tail -9 | cut -c1-${W:-400}
rm -f tests/_f33_quick.py
