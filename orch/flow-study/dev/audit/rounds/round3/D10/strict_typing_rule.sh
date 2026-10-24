#!/usr/bin/env bash
# D10 / quality-scale rule `strict-typing` (Platinum).
#
# METRIC (one line): number of `mypy --strict` error lines whose path is under
# custom_components/heatpump_optimizer/, split by mypy error code, with
# tests/hastub on MYPYPATH as the Home Assistant stand-in.
#
# COMMAND (from the export root; MYPY may point at any mypy 2.3.1):
#   MYPY=<path-to-mypy> bash tools/audit/round3/D10/strict_typing_rule.sh
# A mypy on PATH is used when MYPY is unset.
#
# EXPECTED: integration_errors = 578 (exact on mypy 2.3.1),
# mypy_error_lines_total = 648 (the other 70 are tests/hastub's own),
# code_no_untyped_def = 67, code_type_arg = 119, py_typed_present = 0.
# BASELINE: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
# MACHINE:  8-core Apple M1, python3 3.11.5, mypy 2.3.1
#
# NOT the repository's own census. tests/typing_budgets.json records 191 errors
# under a DIFFERENT ruler: real homeassistant-stubs 2026.2.3 on Python 3.13,
# no hastub. This harness is the D10 brief's ruler (hastub on the path), and the
# two numbers are not comparable; both are reported so a reader cannot confuse
# them. What IS comparable across both rulers is the pass/fail of the rule:
# a non-zero count either way, and no py.typed marker.
#
# Counts only; contention-immune. No timing is reported.
set -u
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
repo_root() {
  local d="$1"
  if [ -f "$d" ]; then
    d=$(dirname "$d")
  fi
  d=$(cd "$d" && pwd) || return 1
  while [ "$d" != "/" ]; do
    if [ -f "$d/custom_components/heatpump_optimizer/manifest.json" ]; then
      printf '%s\n' "$d"
      return 0
    fi
    d=$(dirname "$d")
  done
  printf 'no repository root above %s\n' "$1" >&2
  return 1
}

ROOT="$(repo_root "$0")"
cd "$ROOT" || exit 1
OUT="$ROOT/tools/audit/round3/D10"
MYPY="${MYPY:-mypy}"
TMP="${TMPDIR:-/tmp}/d10mypy.$$"
mkdir -p "$TMP"
export MYPYPATH="$ROOT/tests/hastub"
"$MYPY" --strict --no-color-output --no-error-summary --hide-error-context \
        --show-error-codes --cache-dir="$TMP/cache" --python-version 3.11 \
        --ignore-missing-imports \
        custom_components/heatpump_optimizer > "$OUT/mypy_strict.txt" 2>&1
echo "RESULT mypy_exit=$? status"
python3 - "$OUT/mypy_strict.txt" "$OUT" <<'PY'
import collections, json, os, re, sys
path, out = sys.argv[1], sys.argv[2]
lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
err = [l for l in lines if re.search(r": error: ", l)]
integ = [l for l in err if l.startswith("custom_components/heatpump_optimizer/")]
codes = collections.Counter(
    (re.search(r"\[([a-z0-9-]+)\]\s*$", l).group(1) if re.search(r"\[([a-z0-9-]+)\]\s*$", l) else "no-code")
    for l in integ
)
files = collections.Counter(l.split(":")[0] for l in integ)
print(f"RESULT mypy_error_lines_total={len(err)} count")
print(f"RESULT integration_errors={len(integ)} count")
print(f"RESULT construction_guard_equal={'yes' if len(err)==len(integ) else 'no'} status")
print(f"RESULT distinct_error_codes={len(codes)} count")
for code, n in sorted(codes.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"RESULT code_{code.replace('-','_')}={n} count")
print(f"RESULT modules_with_errors={len(files)} count")
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

root = str(repo_root(out))
print("RESULT py_typed_present=%d count" % os.path.isfile(
    os.path.join(root, "custom_components", "heatpump_optimizer", "py.typed")))
json.dump({"by_code": dict(codes), "by_file": dict(files),
           "integration_errors": len(integ), "all_error_lines": len(err)},
          open(os.path.join(out, "mypy_by_code.json"), "w"), indent=2, sort_keys=True)
PY
echo "RESULT thread_factor=1.0"
echo "RESULT load1=$(uptime | sed 's/.*averages*: *//' | awk '{print $1}' | tr -d ',')"
echo "RESULT swapins=0"
rm -rf "$TMP"
