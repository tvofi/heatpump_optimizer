# Direct-push merge commits: their dispositions

A two-parent commit on `main`'s first-parent line that names no pull request is
a direct push: a local merge pushed to `main`, or the record bot merging `main`
into its rows. `tests/delivery_status.py` reports one as UNCHECKED, which makes
the release stamp's `--require-rows` refuse, unless it is dispositioned. A
commit whose first-parent diff touches only `dev/programme/delivery/<N>.md`
rows is `record-only` without a line here. Every other one needs a line below:
its sha (7 to 40 hex), a colon, and why it owes no delivery row, naming the
row or pull request that carries its work when one does.

