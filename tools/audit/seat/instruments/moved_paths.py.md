# `moved_paths.py`

- `moved_paths.py` — lists every line in the given files that names a path
  `tests/layout.json` marks moved: a retired file, its emptied directory, or
  a lifted prefix. Each hit is tagged FALLBACK when the line also names the
  new path. When: a move, or a review of one, before the push; a reader
  dispositions every STALE? hit. Refusal: none; it enumerates and always
  exits 0.
