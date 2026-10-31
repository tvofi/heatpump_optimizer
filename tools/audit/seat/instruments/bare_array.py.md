# `bare_array.py`

- `bare_array.py` — refuses a bare `"${name[@]}"` in a tracked `tools/**/*.sh`
  script under `set -u` (`--check [--ref <commit>]`, `--self-test`). When:
  after touching any shell script under `tools/`, or before pushing; CI's
  `governance / instrument-self-tests` runs both. Refusal: every site on its
  own line, `path:line: text` — macOS `/bin/bash` 3.2 dies on an empty array's
  bare expansion under `set -u`, which CI's bash 5 expands cleanly. The way
  out is the guard `${name[@]+"${name[@]}"}`, or `# never-empty: <reason>`
  on the line or on a comment-only line directly above it; a line ending in
  `# mut:<name>` takes the reason above, and a reason placed after that marker
  is refused in every file, because it unanchors the self-test's mutant.
