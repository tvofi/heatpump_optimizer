# `prepr.sh`

- `prepr.sh` — the pre-PR self-check on your own branch and body: head SHA
  freshness, claim files byte-identical, the MODE line, carry destinations,
  body headings, and the scoped-closure selection. When: always, before
  handing a branch off. Refusal: each blocked reason names the artifact —
  a branch that fails prepr locally would have burned a review round instead. The ancestry-reds read makes one call per commit of the branch, carrying the red names, the run total and any pending run; a read holding at least one run and none pending is kept an hour under `$HPO_STATE_DIR/prepr-ancestry/` (`PREPR_ANCESTRY_TTL_S`), so a repeat run reads only what changed.
