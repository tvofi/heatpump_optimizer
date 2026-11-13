# `enumerate.py`

- `enumerate.py` — prints one audit universe, one item per line, so a finder
  reports `universe=N examined=n` against a command and not a recollection
  (`COMMON.md`, "The denominator"). Path: `tools/audit/enumerate.py`. When: a
  dimension brief names it as a step's enumerator (`d0-grid`, `d0-modules`,
  `d1-stores`, `d1-excepts`, `d1-lifecycle`, `d3-sites`, `d14-classes`,
  `d16-writes`, `d17-features`), or `rotation.json` names it for a rotation.
  Refusal: exit 2 on a missing source or an empty universe. `--self-test`
  plants a fake repo per parser and is the null control.
