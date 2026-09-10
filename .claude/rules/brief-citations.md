---
description: Wave-brief citations must be linter-resolvable; do not leave them only in plan markdown
paths:
  - ".claude/workflows/*.json"
  - "docs/plan*.md"
  - "docs/HANDOVER.md"
  - "tools/audit/briefs/**"
---
# Brief-linter citations

`node .claude/workflows/brief_lint.mjs` (path #416 lands) lints each group's `brief` in `.claude/workflows/wave-*-groups.json` and each carry in `.claude/workflows/carry-<N>.json`. It does not read `docs/plan-*.md`, `docs/HANDOVER.md`, or `tools/audit/briefs/`.

**Where they go.** New programme plans and wave briefs put load-bearing citations in `wave-*-groups.json` (or the linter's input set) in a form that script can resolve. Do not leave critical citations only in free-form markdown. Extending the plan format means extending the linter in the same PR. Do not weaken the linter to fit a citation.

`resume.stage: done` skips a brief. `after:` must name a group in the same file.

**What resolves**

1. **Paths** (`dir/file.ext` or a unique basename) — in the tree, or in the same brief as a tag SHA (7–40 hex, at least one `a-f`) or `audit-round2-evidence` that actually carries them. A tag-only path without its tag is an error. Negation ("does not exist") is skipped.
2. **`path:line`** (`foo.py:123` or `foo.py:123-145`) — the range exists, and a quoted phrase, a keyword (`return`/`raise`/`assert`/…), or a nearby snake_case identifier is found there or in the enclosing `def`/`class`. No extractable anchor is only a warning. Bare `:123` works only next to a `module.symbol`.
3. **Symbols** — `snake_case` (≥2 segments), `SCREAMING_SNAKE`, or `module.symbol`, found in the tracked tree (not `.claude/` or `tools/audit/round2/`) or at a cited tag. Probe-output names (`min_ink_gap`) fail unless tagged.
4. **Metrics and counts** — a metric names a key of `tests/structure_budgets.json`; a literal (`coordinator_loc 10394 <= 10394`) is always an error, and a stated count the tree answers must equal what it answers. Re-measure at your merge base; derive a count, never carry one (#581).

**VERSION** — `VERSION x.y.z` or `VERSION a -> b` must match the live `VERSION` file (arrow checks `b`). Do not pin a version a later stamp will invalidate.

**When the symbol you must name does not exist yet.** A backticked identifier is a symbol citation, so a brief that names what a *planned* item will add fails the linter for doing its job. This bit three times in one session — twice on symbols the lane existed to introduce, once on a Home Assistant name absent from this tree at any tag. A tag citation does not rescue those: there is no tag at which they exist.

Three remedies, in order of preference, and **weakening the linter is not among them**:

1. **Do not backtick it.** Name it in prose — *the configuration-URL field*, *the repair notice's learn-more link*. The citation rule exists to check claims about the tree, and a symbol that is not in the tree yet is not such a claim.
2. **Cite the artifact that does exist** — the issue, the upstream document, the file the symbol will land in.
3. **Where it genuinely exists at a tag, cite the tag**, which is what tag citations are for.

The linter's ref path also resolves at the cited tag, so verify a tag citation actually carries the symbol rather than assuming the tag rescues it.

```
# BAD — only in docs/plan-*.md, or a moved range with no live anchor
tests/entities.py:6042-6062 "does not run ahead"

# GOOD — in the group's brief, re-anchored, quoted phrase still at the range
tests/entities.py:7305 "does not run ahead"
```
