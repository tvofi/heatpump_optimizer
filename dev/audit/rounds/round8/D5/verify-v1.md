# D5 verification — round 8, single-verifier panel

Verifier tree: `/home/claude/audit-r8/seats/D5-v1`
Baseline SHA: `cdf82daabcfe3777d98b31489f36df5555ec9d82`
Finder evidence copied in from `D5-s1` and `D5-s2` unmodified.
Own harnesses added: `v1_stepnum_position.py`, `v1_stepnum_overlap.py`,
`v1_comment_idents_pyscan.py`. Production files touched during the s2
perturbation (`const.py`, `optimizer.py`) were restored and verified
byte-identical to `/home/claude/audit-r8/export` (`diff -q`, both `OK`)
before this report was written.

This round runs one verifier instead of three, so both halves of
`verifier.md` are carried here: the finder's harness is re-run, and a
second, independently written harness with its own metric definition is
run per finding.

---

## D5-s1-01 — Quick-start diagram/prose step numbers disagree

**Re-run of the finder's harness** (`s1_stepnum.py`, unmodified, copied
from `D5-s1`):

```
RESULT mismatched_labels=3 count
RESULT thread_factor=1.00 ratio
RESULT load1=16.34 load
```
matching mismatches: Temperatures (diagram 3 / prose 4), Hot water
(diagram 5 / prose 6), Weather sensitivity (diagram 6 / prose 7).

Perturbation (`--fix`, temp copy only, README.md never touched):
```
RESULT mismatched_labels=0 count
```
Direction matches `expected_direction: to_zero`. Confirmed.

**My own measurement**, two takes, both written from scratch with their own
metric definitions (not reusing `s1_stepnum.py`'s matching logic):

1. `v1_stepnum_position.py` — pair diagram node *i* with prose heading *i*
   by pure sequence order. This is unsound here (prose has 7 numbered
   headings, the diagram only 6 — the "finish menu" is numbered in prose but
   not in the diagram — so index-aligned pairing drifts after that point and
   under- or over-counts by accident). I report it mainly as a documented
   negative result: `positional_mismatches=0` on the unperturbed text,
   which is wrong (a coincidence of prose[2]="finish menu"/step3 landing on
   the same number as diagram[2]="Temperatures"/step3, masking the true
   mismatch rather than revealing it). This take is **discarded** as a
   metric — logged for transparency, not used for the vote.

2. `v1_stepnum_overlap.py` — pair each diagram node with the prose heading
   of highest Jaccard word-overlap (stopword-filtered, threshold 0.34,
   greedy best-first), instead of `s1_stepnum.py`'s exact first-three-word
   prefix match. Result on the unperturbed text:
   ```
   RESULT overlap_mismatches=3 count
   RESULT unmatched_prose=2 count
   ```
   Same 3 pairs as the finder's harness, **plus** it independently confirms
   the "finish menu" prose heading has no diagram counterpart (as claimed).
   It does *not* surface a 4th mismatch either, but for a data reason, not
   a matching-algorithm reason (see attack below) — so this take corroborates
   `mismatched_labels=3` under a genuinely different implementation.

**Attack on the method — and a real defect in both harnesses, mine included:**

The diagram node for the building-description branch is
`D{"4 · How do you want to<br/>describe your building?"}`. Both
`s1_stepnum.py`'s `DIAGRAM_NODE_RE` and my own capture the label text only
up to the first `<br/>`, i.e. `"How do you want to"` — the actual content
word ("building") is on the far side of the line break and is never
captured. Since `s1_stepnum.py` normalizes to the first three words, it
gets `"how do you"`, which cannot match anything in the prose ("How to
describe your building" → `"how to describe"`), so the pair is silently
dropped from `diagram`/`prose` matching entirely — not filtered out as "no
mismatch", just invisible to the comparison. My word-overlap version has
the same truncation, so its diagram-side word set is empty after
stopword-filtering `{how, do, you, want, to}`, and it can't be matched to
anything either, for the same underlying reason (upstream extraction, not
downstream matching).

I checked the ground truth by hand against `README.md`'s "## Quick start"
section directly (not through either regex): the diagram node is numbered
**4**, the corresponding prose heading is `**5 · How to describe your
building.**`. That is a fourth disagreeing pair (4 vs 5), consistent with
the *prose* of the finding's own claim text ("diagram... numbers 3, 4, 5,
6... prose... numbers 4, 5, 6, 7") and with `s1_stepnum.py`'s own docstring,
which states an *expected* value of 4 at this baseline SHA — but the
harness as coded, and as actually run by me and by the finder, prints 3.

So: the finding's evidence.value (3) is an accurate report of what the
supplied harness computes, but the harness undercounts the true phenomenon
by one, due to a `<br/>`-truncation bug in its own diagram-node regex
compounding its label-matching rule. This is an instrument defect
(`tools/audit/README.md`, "A defect in an instrument is a finding"), not a
refutation — if anything the true number of disagreeing pairs is 4, not 3,
which if anything strengthens the finding rather than weakening it. I am
not filing it separately: per `CLAUDE.md`'s fix-first order this is exactly
the kind of one-line instrument fix a fixer should make in place, and it
does not change this finding's severity (the mechanism, direction, and
even the "from step 3 on" framing are all still correct at either count).

**Null control / contention:** this is a static count over `README.md`
text, not a timing number — `load1` (16.3) is irrelevant to it, and both
re-runs (finder's and mine) are exact and reproducible regardless of box
load.

**Severity:** `low` is earned — it's a documentation-consistency nit a
careful reader can self-correct by matching content rather than numbers,
with no functional consequence.

**Vote: verify.** Value 3 (as the harness computes it) reproduces exactly;
my independent overlap-based harness reproduces the same 3; the
perturbation drives it to 0 in the expected direction; and my own
hand-check of the source text shows the true count is if anything 4, so
there is no risk this is an artefact inflating the finder's number — if
anything the harness underreports it slightly. Severity `low` stands.

---

## D5-s2-01 — Two comment blocks name a real symbol as a bare shorthand

**Re-run of the finder's harness** (`s2_comment_idents.py`, unmodified):

```
RESULT raw_missing=19 count
RESULT shorthand_missing=2 count
RESULT checked_idents=640 count
RESULT wall_s=9.037 s
RESULT load1=15.90 n/a
RESULT thread_factor=1.00 ratio
```
The two `SHORTHAND` lines match the claim exactly:
```
SHORTHAND custom_components/heatpump_optimizer/const.py:78-85 MIN_POWER -> real sibling CONF_HEAT_PUMP_MIN_POWER
SHORTHAND custom_components/heatpump_optimizer/optimizer.py:6515-6520 min_power -> real sibling min_electrical_power
```
Value, unit and tolerance all reproduce exactly (count metric, contention-immune, `load1` is quoted per house rules but does not bear on a count).

**Perturbation**, applied to production files under a `finally`-equivalent
(explicit backup/restore, verified with `diff -q` against the baseline
export afterward — see header of this report):
```
const.py:80   ``MIN_POWER``            -> ``CONF_HEAT_PUMP_MIN_POWER``
optimizer.py:6519  min_power * 24 h... -> min_electrical_power * 24 h...
```
Re-run:
```
RESULT shorthand_missing=0 count
```
Direction matches `expected_direction: to_zero`. Confirmed, and files
restored byte-identical to baseline.

**My own measurement**, written from scratch (`v1_comment_idents_pyscan.py`):
no `grep` subprocess, no whole-file word-subset trawl over every comment
block in every file — instead it targets exactly the two claimed
(bare, real) pairs and asks the narrower question directly: does the bare
token occur anywhere in non-comment code (via a Python `re` scan, not
`grep -w`), does the real full name occur in code, and — this is where I
added a stricter bar than the finder's own metric — does the real full name
also occur **in the same cited comment block**, not just somewhere in the
file.

```
-- MIN_POWER (claimed real sibling CONF_HEAT_PUMP_MIN_POWER) at const.py:80
   code occurrences of bare MIN_POWER: []
   real full name CONF_HEAT_PUMP_MIN_POWER in code: 30 occurrences (file-wide)
   bare token present in the cited block: True
   real full name present in the SAME block: False
   CONFIRMED (block-local bar): False
-- min_power (claimed real sibling min_electrical_power) at optimizer.py:6519
   code occurrences of bare min_power: []
   real full name min_electrical_power in code: 16 occurrences
   bare token present in the cited block: True
   real full name present in the SAME block: True
   CONFIRMED (block-local bar): True
RESULT confirmed_shorthand=1 count
```

This is a genuinely different number (1, not 2) from a genuinely different,
and stricter, metric definition: mine requires the real full name to be
named *in the same comment block* as the bare shorthand it claims to
abbreviate; `s2_comment_idents.py`'s (and the finding's own
`metric_definition`) only requires a proper-word-subset real identifier to
exist somewhere in the *same file*.

**Attack on the method:** the finding's `claim` field says the bare form
sits "inside the same comment block that names or uses the symbol's real
form," which reads as a block-local co-location claim. For
`optimizer.py:6519` that is literally true — `min_electrical_power` is
backticked two sentences earlier in the identical comment block. For
`const.py:80` it is not: the block names `CONF_HEAT_PUMP_MAX_POWER` (a
*different*, sibling constant), not `CONF_HEAT_PUMP_MIN_POWER`, whose only
occurrences are at `const.py:656` (a real, non-comment definition, 587
lines away) and 29 other file-wide sites. The finding's own docstring is
in fact honest about this ("real sibling: CONF_HEAT_PUMP_MIN_POWER,
const.py:656, **never itself named in the block**") — so the underlying
fact is not misrepresented in the harness's design or in the finder's own
prose caveat, only the shorter `claim`/`title` phrasing overstates it by
implying block-local co-location for both instances uniformly.

This does not change what the pattern actually is for `const.py:80`: a
comment block that pairs a real symbol (`CONF_HEAT_PUMP_MAX_POWER`) with
what reads like its natural counterpart (`MIN_POWER`) but is in fact dead
shorthand with zero code occurrences anywhere in the tree — a reader
skimming that block has no way to know `MIN_POWER` isn't real, and the
harness's file-wide "does a real word-superset identifier exist" check is
a reasonable proxy for "this reads like an abbreviation of something real."
It is a precision issue in the one-sentence claim text, not a defect in the
metric or the count.

**Severity:** `low` is earned for both instances — dead comment tokens with
no behavioural reach, caught by grep/read, zero runtime consequence.

**Vote: verify.** `shorthand_missing=2` reproduces exactly under the
finder's harness and the perturbation drives it to 0 as expected with
production restored byte-identical. My independently-written, stricter
harness confirms 1 of the 2 instances under a tighter co-location bar and
explains, via the finder's own honest docstring caveat, why the second
instance doesn't clear that tighter bar without that meaning the claim is
wrong — merely that "beside the real full name" is precise for
`optimizer.py:6519` and imprecise (though not false: the real full name of
the *abbreviated symbol* does exist and is checkable file-wide) for
`const.py:80`. Severity `low` stands for both.

---

## Cross-finding note

D5-s1-01 (docs numbering) and D5-s2-01 (code comments) are not the same
mechanism — one is diagram/prose drift in `README.md`, the other is dead
shorthand tokens in two unrelated `.py` comment blocks — no shared harness,
no shared instrumented symbol, nothing to flag as one mechanism appearing
twice.

## Summary

| id | finder value | my value | perturbation | vote | severity |
|---|---|---|---|---|---|
| D5-s1-01 | 3 (mismatched_labels) | 3 (overlap_mismatches, independent match rule); true count likely 4 by hand-check, harness undercounts by 1 via a `<br/>`-truncation bug | to 0, confirmed | verify | low |
| D5-s2-01 | 2 (shorthand_missing) | 1 under a stricter same-block-only bar; 2 under the finder's own file-wide metric, reproduced exactly | to 0, confirmed, production restored | verify | low |
