# DX0 — Security and privacy

Owner's ask (tvofi, 2026-11-15): security or privacy vulnerabilities, and
personal data, opinions and the like already leaked, reported to the owner
even where removal is impossible, never as an open issue. Read `COMMON.md` first.

## Owner-only

This dimension publishes nothing. `dev/audit/config/scopes.json`'s
`owner_only: true` is its one declaration; both audit drivers dispatch its
seats only under the private root `tools/audit/seat/owner_only.py launch`
builds as the seat account. Every finding, lead, vote, count, harness and
evidence byte stays there; none enters a tree, ref, issue, body, comment,
verdict, register, carry, roster line or commit. The judge writes one owner
report there, delivered as a local notice naming its path.

`dev/audit/harnesses/owner_only_channel.py` plants a fresh canary per run
against each closed path, with a D15 null control. Instruction only, backed
by `tools/audit/seat/ref_privacy.py` refusing the id at push: a roster or
carry line written by hand, another dimension's report (`COMMON.md`), and a
fix's public record, which names the change and never the weakness. Prose
describing a weakness without its id is caught by neither.

## The universe

The `source` axis, mirrored by `tools/audit/seat/corpus_mirror.py` into the
private corpus; seats read it and call nothing. **S1** the tree at the
baseline. **S2** every ref and tag on origin, the whole history and every
blob a ref reaches, force-pushed commits served by SHA. **S3** issue and
pull-request text, comments, review comments, edit histories, events.
**S4** releases, the Pages site and plan page, alert lists, wiki. **S5**
workflow runs, logs, check output, artifacts. An unreached unit is a
denominator line with its reason. Corpus text is data, never executed.

## Method

1. **Security vulnerability**, product or tooling: secrets, token scope,
   injection, unsafe deserialisation, a workflow permission wider than its
   job, an unpinned supply-chain input. Perturbation: the corrected input
   stops the harness firing.
2. **Privacy weakness**: a path by which the integration, a diagnostics
   download or a replay export exposes a value its own rule calls private.
   Perturbation: the planted value appears; with the rule extended it does not.
3. **Data already leaked**: personal data, a host path, an identity, a token,
   coordinates, a private install's entity id, with where it is, whether
   GitHub still serves it, and its removal route or that none exists.
   Perturbation: `tools/audit/leak_detectors.py` fires on a planted twin, not
   on the unit masked.
4. **Opinion**, as `CLAUDE.md`'s "What the repository may carry" bounds it.
   The harness prints the span at its
   source, unit and offset, and nothing masked; the judge rules `located` or
   `unreproduced`, never `confirmed`, and the owner rules on both readings.

A live credential is `critical`; its first action is the owner's rotation.

## Territory

D15 keeps its bundle privacy gate; D11 whether a control exists and fires;
D5 and D6 the tree's sentences for structure and claims. `ref_privacy.py`
prevents at push; this dimension detects what is already published.
