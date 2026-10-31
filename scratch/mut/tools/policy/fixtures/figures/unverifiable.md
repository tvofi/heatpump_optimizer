Commands this check cannot analyse. Every one is reported and none is refused:
the per-line report is what lets a seat see which figures were examined, and a
refusal here would be the check having an opinion it cannot support.

## Figures

- An inline script rather than a file:
  `python3 -c "import json;print(len(json.load(open('tests/closures.json'))['recorded']))"`
- A program outside the set this knows, in a block, so it is reported rather
  than dropped:

      pip download homeassistant==2026.9.1 --no-deps -d "$D"

- A path that is a shell variable, not a literal: `bash $T/old.sh --self-test`
- A git command, whose flags this deliberately does not check:
  `git diff --name-only origin/main...HEAD -- VERSION`

## Red checks

none
