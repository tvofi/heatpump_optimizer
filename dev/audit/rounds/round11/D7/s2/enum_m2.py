"""D7.M2 enumerator (round 11, D7-s2): the shipped sysid presets, one per line (tests/stress.py BUILDINGS).

Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/enum_m2.py
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: 3 lines.
"""
import contextlib
import io
import sys

sys.path[:0] = ["tests"]
with contextlib.redirect_stdout(io.StringIO()):  # stress.py prints a banner on import
    from stress import BUILDINGS  # noqa: E402

print("\n".join(BUILDINGS))
