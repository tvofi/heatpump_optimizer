# `product_reads.py`

- `product_reads.py` — reads decision 0018's `operation` and `generality`
  terms off a seat's cell ledger, counting a row only on a witness the read
  itself produced. Path: `tools/audit/product_reads.py`; its docstring
  states both rules. When: a D16 seat's actuator-write ledger (`operation`,
  rows `<d16-writes --cells item>\t<script>::<check>`) or a D12 seat's
  level ledger (`generality`, rows `<level>\t<source>\t<script>::<check>`),
  and at a round's close for the objective record. The universes are
  `enumerate.py`'s, imported, never enumerated again. Each cited script
  runs unedited under a launcher in a child process: twice as it is (a
  check differing between the two is `nondeterministic`), then once per
  cited site with the payload perturbed in passes of the cell's state, or
  once per cited level with that level's observable switched. `--jobs`
  runs them in parallel; one run costs what the script costs.
  `--pairs-out` writes the pairs both of whose levels were witnessed in
  one configuration, as rows `enumerate.py d12-cells --pairs --ledger`
  reads. Refusal: exit 2 on a missing or empty universe or ledger, or a
  row naming no item. `--self-test` plants a fake tree with each planted
  and null control of the design at `design/R11-PRE-PRODUCT-READS`.
