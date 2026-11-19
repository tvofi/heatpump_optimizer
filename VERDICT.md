Fix review: merge cd6c9c67853452969a4e2ab5e6afd5240402a305
bus-nonce: 779589898c1ae189df21b32facc56dd4

Scope: full, first round; three-dot diff against f64ff8e12e is one file, dev/audit/rounds/round11/ISSUES.json, 57 lines each changing a class's `number` from null to an integer; no other line changes; the file parses as JSON.

Check against GitHub (evidence/issue-crosscheck-cd6c9c67853452969a4e2ab5e6afd5240402a305.txt): all 57 numbers, #3744 to #3800, are distinct and exist as open issues; for every class the issue's title equals the draft's title, its label set equals the draft's labels, and it carries `class:<class>` for the class the file records. The `[R11-` title search returns exactly these 57 issues, so no class has a second issue.

Gate: re-read live, all required checks green at the head (gate, pr-contract, tests/*, governance/*).

Notes (paperwork, not blocking):
- The PR body says each issue body is "the body as drafted plus an Owning roster groups section". In 16 issues the filed body rewrites the draft's `$HOME/venv-ci/bin/python3` to `python3`, and #3766 rewrites `--out /tmp/w.json` to `--out w.json`. The issues' meaning is unchanged; the body does not mention the rewrite.
- I2 (#3761) leaves out D3-s2-01, as the PR body says, and the issue says so too.
