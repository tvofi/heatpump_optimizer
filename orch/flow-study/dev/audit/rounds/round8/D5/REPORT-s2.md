# D5 seat s2 — code comments (round 8, baseline cdf82daabcfe3777d98b31489f36df5555ec9d82)

## Scope

Method step 4 only: module docstrings and every `#` comment block longer than
3 consecutive lines under `custom_components/heatpump_optimizer/*.py` (81
files). Executable checks: do the identifiers a comment names exist, and do
the numbers a comment cites match the constant beside them. Structure,
reader-path walkthroughs and `docs/*.md` content are seat s1's focus and were
not duplicated here.

## Method actually run

1. `tools/audit/round8/D5/s2_comment_idents.py` extracts every module
   docstring and every >3-line `#` block from all 81 files (640 candidate
   underscore-identifiers), checks each against a non-comment-line grep over
   `custom_components/` + `tests/` (`*.py`, `*.mjs`), and then narrows the
   raw misses to ones whose word-set is a proper subset of a real identifier
   also present in the same file -- the shape of an abbreviation, not of
   incidental prose. Raw misses: 20 (of which 18 are false positives of the
   checker itself -- see below); shorthand misses: 2, both confirmed by hand.
2. `tools/audit/round8/D5/s2_backtick_check.py` runs the same existence
   check restricted to backtick/double-backtick-quoted names only (the
   stronger claim: the author explicitly marked this as a code reference).
   7 of 407 came back missing; all 7 triaged by hand (see non-findings).
3. Spot-checked cited numbers against the `const.py` constants they
   describe for the buffer-tank thermal-mass family (the block deriving
   9.7 W/K and "168% of the charge"): recomputed from the named constants,
   matched to rounding.
4. Manually read the highest cross-file comment-similarity pair found
   (difflib ratio 0.87, `binary_sensor.py` / `sensor.py` "wood twin" gate
   comments) as a possible stale-copy defect; it is not one.
5. Swept every `vN.N.N` citation in a code comment against
   `manifest.json`'s shipped version; none is post-current.

## Why raw_missing=20 is not the claim

18 of the 20 raw misses are false positives of a purely lexical checker
against a codebase that: (a) uses short math notation in prose (`T_prev`,
`q_eff`, `q_nominal`, `T_use`, `house_temp`, `TW_in`) that was never meant to
name a Python symbol; (b) deliberately documents removed code by the name it
used to have (`PLACE_LABELS`, `_MULTI_START_SOLVES`, `DEFAULT_KEY`) -- the
comment says so explicitly in the same sentence; (c) cites another project's
own identifiers by repo+SHA (`device_name_slug`, `fault_description`,
`device_config` -- tvofi/tuya_heat_pump and make-all/tuya-local, named in the
same paragraph); (d) got split across a line wrap by my own block-length
regex (`_current_spot_` / `price`, which is `_current_spot_price` and real).
None of these is a defect; they are listed so a verifier does not have to
re-derive them. Only the shorthand-filtered 2 are reported as a finding, and
the finding's own metric name (`shorthand_missing`) is the number the claim
rests on.

## Findings

**D5-s2-01** (low, hygiene) -- const.py:80 and optimizer.py:6519 each drop a
real, correctly-named production symbol to a bare abbreviation
(`MIN_POWER`, `min_power`) that has zero code occurrence, in the same
comment block that also correctly names the real symbol
(`CONF_HEAT_PUMP_MIN_POWER`, `min_electrical_power`). Perturbation executed:
rewriting the two comment lines drives `shorthand_missing` 2 -> 0; reverted,
tree confirmed byte-identical to the baseline export with `diff -rq`.

I looked for, and did not find, a second phenomenon that would clear the
bar: no wrong number, no comment describing removed/renamed behaviour as
current, no genuinely misleading docstring, in the >3-line-comment
population sampled. That absence is itself the round's headline result for
this seat -- see non-findings.

## Non-findings

See `report-s2.json`'s `non_findings` array (4 entries): the backtick-name
existence sweep (0 genuine misses among the 7 raw), the buffer-tank UA
re-derivation, the wood-twin cross-reference check, and the version-citation
sweep. Each carries its own command and value.

## What I could not finish

Did not attempt: a full leave-one-out over per-file comment density
(D5-s2-01 is not a grid aggregate, so it does not apply); a systematic
redundant-comment sweep for "explains what the next line obviously does" --
every >3-line block sampled was substantive (issue numbers, measured deltas,
physical justification), so this codebase's comments do not appear to have
that failure mode at the >3-line population level; a 1-line-comment sweep
was out of this seat's stated scope (method step 4 samples docstrings and
>3-line comments).

## Exposure

`D5.md`'s method step 4 required no `docs/` reading -- this seat's own scope
is code comments, and none of the >3-line comment blocks or module
docstrings sampled quoted or leaned on `docs/*.md` content, an earlier audit
round, or GitHub. In-code comments across the module routinely cite issue
numbers and prior-round finding ids (`R1-D0-02`, `R5-D1-06`, `R6-D0-02`,
etc.) as historical narrative inside their own explanation of a design
decision -- read as context while sampling, never used to select or motivate
either finding above. Schema/task-brief mismatch on finding-id format noted
in `report-s2.json`'s `exposure_note_schema`.

## Tree hygiene

`diff -rq custom_components/heatpump_optimizer /home/claude/audit-r8/export/custom_components/heatpump_optimizer`
is empty after the perturbation was reverted. No other production file was
touched. Only `tools/audit/round8/D5/` was written to (this file,
`report-s2.json`, and the two harnesses).
