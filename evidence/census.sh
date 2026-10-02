#!/bin/bash
# usage: census.sh <dir>  -> prints RESULT errors=<n> and error lines
cd "$1" || exit 2
c=$(mktemp -d)
env -u PYTHONPATH -u MYPYPATH /Users/timmalmstrom/hpo-seats/1852-review/venv/bin/python -m mypy --strict --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental --cache-dir "$c" --python-version 3.14 custom_components/heatpump_optimizer > "$c/out.txt" 2>&1
grep ': error:' "$c/out.txt"
echo "RESULT errors=$(grep -c ': error:' "$c/out.txt")"
rm -rf "$c"
