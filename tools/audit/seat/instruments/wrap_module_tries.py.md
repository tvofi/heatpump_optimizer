# `wrap_module_tries.py`

- `wrap_module_tries.py` — rewrites each top-level statement of a test script
  whose body, outside a def, class or lambda, holds a `try` into
  `def _module_block_<line>():` declaring `global` every name it binds, called
  once at its old place. When: `tests/entities.py` refuses "no test script past
  _GIANT_SCRIPT_LINES runs a try at module scope", because CodeQL's Python
  extractor is slow on such a `try` (#3232 cancelled the 45-minute python job).
  Refusal: an annotated name or a star import in a statement to wrap, neither
  legal under `global`; it asserts each wrapped statement's AST and the order
  of the rest unchanged. `--dry` prints the count without writing.
