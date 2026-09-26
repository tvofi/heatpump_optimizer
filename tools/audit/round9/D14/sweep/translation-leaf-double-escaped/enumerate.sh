#!/usr/bin/env bash
# D14 sweep, class "translation leaf double-escaped".
# Finding: D4-s2-03 (verified, medium -- the dhw_min_too_close error text in strings.json/
# translations/{en,sv}.json (config AND options flow) carries a literal "\uXXXX" escape sequence
# in the JSON string VALUE itself (double-escaped: once for JSON, once more baked into the text),
# so after json.loads the frontend's ICU MessageFormat prints the backslash-u sequence verbatim
# instead of the intended character. escaped_error_texts_reached=4 (config+options x en+sv),
# garbled_chars_en=1, garbled_chars_sv=9; null control escaped_other_error_texts=0 (every other
# error text of both flows); seam count escaped_texts_all_files=6 (strings.json + en.json +
# sv.json x config/options). The finder's own harness already scans every translation file, so
# it IS the class enumerator; reused verbatim.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D4/s2/escaped_text.py
