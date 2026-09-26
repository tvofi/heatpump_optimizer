#!/usr/bin/env bash
# D14 sweep, class "markdown the renderer misplaces". Finding: D5-s1-04 (verified, low).
# The finder's own harness already scans every user doc (README.md + 7 docs/*.md files), so
# it IS the class enumerator; reused verbatim.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
T=$(mktemp -d)
npm install --prefix "$T" markdown-it@14.1.0 >/dev/null 2>&1
NODE_PATH="$T/node_modules" node tools/audit/round9/D5/s1/md_tables.mjs
