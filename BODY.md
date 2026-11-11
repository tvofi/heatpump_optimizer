Triage batch 192 rules P614 (queue line 292, `brief_lint.mjs` passing a directory-qualified path through its basename), 2026-11-11. It holds one ruling.

- **P614, REJECT: BRIEF-LINT-BASENAME-PATH.** The mechanism is real: `lookupPath` (`tools/policy/brief_lint.mjs:158-163`) falls back to any tracked file with the same basename. `tools/pr/ref_privacy.py` resolves to `tools/audit/seat/ref_privacy.py`. But it measures far under the bar.
  - On the roster at `d48ffabbf1` (461 groups), 140 of 2,391 slash path tokens resolve only through the basename. 19 of those are in the 48 live groups.
    - 91 are correct citations whose leading dot `PATH_TOKEN_RE` drops: `.github/...` is read as `github/...`.
    - 2 are escaped-newline artifacts, and 33 are not paths into this tree.
    - 14 name a wrong directory, and all 14 are in done or absorbed groups, mostly old locations from before a file moved.
    - Live briefs carry 0.
  - Null control: the proposed refusal, run over the same tokens, fires 140 times with 14 true. That is 10.0% precision, and 0% on live briefs, until the tokenizer is fixed too.
  - A wrong directory costs a seat one failed read and one search: under 1% of fixer tokens even at worst.
  - Re-open trigger: once the tokenizer keeps the leading dot, 3 or more live briefs at one roster head carry such a path, or a verdict records a review round lost to one.

The diff is one file against the merge base: `dev/programme/triage/s6-batch192.md`, the ruling. No product behaviour changes.

## Head

`13710a3bb7b9105ce4f44c46440337d2938f1cc1`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P614 as REJECT, and a citation of P614 is refused as "not an ACCEPT ruling (REJECT)", so no carry can cite it.
- With the verdict flipped to ACCEPT in the file text, the same citation passes (`None`).

## Null control

- P615 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...13710a3bb7b9105ce4f44c46440337d2938f1cc1`: 1 file, 2 commits. The second commit only rewords the moved-path examples so that `tests/layout.py --guard` passes (0 refusals).
- The figures come from `wave-r10-groups.json` at roster `d48ffabbf1`, tokenized with `PATH_TOKEN_RE` and resolved against `git ls-tree -r --name-only ee64358be7`, and from `resolvePathToken` run at `ee64358be7`, as cited in P614.

## Red checks

none

## Forward-carry

none

## Friction

none
