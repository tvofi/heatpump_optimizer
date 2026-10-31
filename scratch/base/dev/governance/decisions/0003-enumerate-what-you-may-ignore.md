---
status: accepted
supersedes: []
superseded-by: []
---

# 0003 — An enumeration of what you must catch cannot be completed

## Why this is here

`0002` names a cause: an assertion whose only witness is its author's model of
the thing it asserts. This one names a *shape* that the same two days produced
independently, at four separate places, and that has a mechanical answer rather
than a procedural one. Recorded separately because the countermeasures are
different: `0002`'s is a mutation lane, and this one's is a rule about which
direction a list is written in.

## The four

**One. Document extensions.** `#615` spent five review rounds closing one at a
time: `.MD` and `.txt`, then `.rst`, then `.mdx/.adoc/.org/.text/.mdown/.mkd/
.rest/.asciidoc`, then `.mdc` — nine real files in this tree. Each round closed
the extensions it had been shown and each shipped a body claiming the rest were
covered. Three of those five blocks were introduced by the previous round's fix.

**Two. A resolver that returns nothing when it cannot decide.** `resolveCited`
resolved a basename only when exactly one tracked file matched. That reads as
caution and is an allowlist of spellings the check can see: a destination named
after any capped policy file made the citation ambiguous and left every cap in
silence, for the cost of one file. Measured — `docs/COMMON.md` cited as
`COMMON.md`, `docs/fixer.md` as `fixer.md`, `docs/gate-scoping.md` as
`gate-scoping.md`, all reporting nothing, against `docs/Zednotes.md` reporting
one.

**Three. A hand-kept copy of a list production also keeps.** The mutation lane
needs the names of the corpus checks. A second copy of that list is this defect
one level up: a check added later would be missing from it, and the lane would
report every check it knew about as pinned.

**Four. A list nobody compares against the thing it describes.**
`NOT_A_DOCUMENT` was first written with plausible extensions — css, html, ts,
toml, jpeg, woff — sixteen of which no tracked file has. `CORPUS_EXCLUDED` named
a file the archive pass deletes, which would have left an exclusion naming
nothing: a destination waiting to be used, because a file written at that path
later leaves every cap with no diff for a reviewer to see.

## The decision

**Write the list in the direction that can be bounded, and bound it.**

1. **Prefer a blocklist over an allowlist whenever the complement is
   measurable.** Ask "is this path CODE" — a list bounded by `git ls-files` —
   rather than "is this path a DOCUMENT", which is a list that cannot be
   finished. An extension in neither list must default to the *reported* answer,
   never to the silent one. This is what makes the blocklist safe to be
   incomplete, and it is the whole reason the inversion works.
2. **A list is only bounded if it is checked against the thing it claims to
   describe, in BOTH directions.** No dead weight — nothing the tree does not
   have — and no floor breach — nothing the corpus has already established
   belongs on the other side. One assertion alone is half a bound: `deadWeight`
   passed happily while `txt` was added to the blocklist, because the tree does
   have `.txt`.
3. **A floor list does not have to be complete, and that is not a contradiction.**
   `NEVER_NOT_A_DOCUMENT` names the formats already established as documents. It
   only refuses writing a known one into the blocklist; the blocklist still
   decides the default. A list that is not load-bearing for the default can be
   partial without being a hole.
4. **Import the enumeration from production rather than copying it.** Two
   hand-kept lists that must agree are a defect generator. Where a copy is
   unavoidable, byte-compare it (`rules_sync --check`, `fragments_sync`).
5. **A resolver that cannot decide must REPORT, not stay silent.** Silence is
   indistinguishable from "there was nothing there", which is exactly the state
   an escape wants. Resolve an ambiguous basename to every candidate and let the
   caller's existing filter drop the ones that are already accounted for. Where
   reporting is genuinely wrong, say so out loud and say why — `checkProvenance`
   prints a skip line rather than returning `[]` when the clone cannot answer.

## The distinction that keeps rule 5 honest

**"No" and "I cannot look" are different answers, and a tool that conflates them
is the same defect wearing the other face.** `git merge-base --is-ancestor`
exits 1 for "not an ancestor" and 128 for "I do not have that object"; a bare
`catch` read both as "not an ancestor" and turned every shallow clone into a
false refusal. Rule 5 says report rather than go silent; it does not say report
a refusal you have not established.

## Consequences

- The corpus scan can never again be closed one extension at a time, because it
  no longer asks which extensions are documents.
- Adding a genuinely new code or data extension to the tree costs one blocklist
  entry, and the dead-weight assertion refuses it if the tree does not have it.
  That is the intended cost.
- An ambiguous basename now reports every candidate. On a tree still holding
  frozen write-once evidence this reports that evidence, which is a true finding
  about uncapped documents rather than a false positive — the archive pass
  classifies it by deletion, which is why the widening lands there.
- **Not closed:** an extension added to the tree and blocklisted in the same
  change passes both assertions. Named rather than left to be found.

## Evidence

    node .claude/workflows/policy_lint.mjs        # TOTAL 0; the acceptance's pins
    node .claude/workflows/policy_lint_mutants.mjs

The four escape spellings, and the one-file collision, are driven in the pull
requests that closed them; each names its own head SHA, and none of the branch
SHAs survives its squash, which is why this file cites none of them.
