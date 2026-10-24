"""The new tests/entities.py check's block, run alone (reviewer-built, copied verbatim
from tests/entities.py lines 22582-22603 at 8f3e72f4). argv[1]=stamp.py path. cwd=repo root."""
import sys, tempfile, importlib.util
from pathlib import Path
sys.path.insert(0, "tests")
import env_drift as _env_drift
spec = importlib.util.spec_from_file_location("stamp_under_test", sys.argv[1])
_stamp = importlib.util.module_from_spec(spec); spec.loader.exec_module(_stamp)
try:
    _stcov_version = Path("VERSION").read_text().strip()
    _stcov_next = _stamp.bump(_stcov_version, "patch")
    _stcov_after, _, _ = _stamp.rewrite_claims(
        Path(_env_drift.CLAIM_FILE).read_text(), _stcov_next, "t")
    _stcov_decl, _stcov_claims = _env_drift._parse_claims(_stcov_after)
    with tempfile.TemporaryDirectory() as _stcov_dir:
        _stcov_path = Path(_stcov_dir) / _env_drift.CLAIM_FILE
        _stcov_path.parent.mkdir(parents=True)
        _stcov_path.write_text(_stcov_after)
        _stcov_md = _env_drift._may_drift(_stcov_dir)
    _stcov_problem = (
        _env_drift.may_drift_coverage_error(_stcov_md, _stcov_claims, _stcov_decl, _stcov_next)
        or _env_drift.may_drift_error(_stcov_md, _stcov_claims))
    ok = _stcov_problem is None and not _stcov_claims
    detail = f"claims={sorted(_stcov_claims)} problem={_stcov_problem!r}"
except Exception as e:
    ok = False; detail = f"{type(e).__name__}: {e}"
print(f"RESULT stcov={'pass' if ok else 'fail'} {detail[:600]}")
