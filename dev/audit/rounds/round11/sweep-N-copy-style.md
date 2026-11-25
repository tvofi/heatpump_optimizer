# Class sweep N-copy-style (round 11, PLAN phase D)

Class: user-facing copy breaks the style rule its sibling strings keep (title case, quote style,
degree sign). Not in `dev/audit/config/bugclasses.json` at this register head (no entry: status
open by default; the fold adds it). Findings: D4-s3-06, D4-s3-07.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep_n_copy_style.py [ROOT]` -- seams are
(surface x language x rule): translations/{en,de,sv}.json, card `STRINGS` {en,de,sv}, services.yaml,
blueprints/**, user-visible Python literals (exception/notification text); rules quote_style,
degree_sign, title_case_titles (en/sv only). 20 seams at register head 28b864af6d.

- Positive control: re-finds both findings exactly -- en titles 6, sv titles 3 (D4-s3-06); de
  straight spans 25 + card 2 = 27, blueprint degree-without-sign 2 (D4-s3-07).
- Null control: `--fixture=clean` -> `instance_seams=0`.
- Perturbation: `--perturb=reintro` (one line: de fixture string `Setze "Komfort" auf 21 C.`) ->
  `instance_seams=2` (de quote_style 1, de degree_sign 1).

## Dispositions

| seam | disposition |
|---|---|
| translations/en.json title_case_titles (6) | instance -- finding D4-s3-06 |
| translations/sv.json title_case_titles (3) | instance -- finding D4-s3-06 |
| translations/de.json quote_style (25) | instance -- finding D4-s3-07 |
| card STRINGS.de quote_style (2) | instance -- finding D4-s3-07 |
| blueprints/** degree_sign (2) | instance -- finding D4-s3-07 |
| translations/en.json quote_style (61 straight vs 3 typographic) | instance, beyond finding |
| translations/sv.json quote_style (62 straight vs 1 typographic) | instance, beyond finding |
| card STRINGS.en quote_style (2 vs 3) | instance, beyond finding |
| card STRINGS.sv quote_style (2 vs 3) | instance, beyond finding |
| translations/de.json title_case_titles | not applicable -- German capitalises nouns |
| degree_sign in translations en/de/sv, card en/de/sv, services.yaml, *.py | not applicable -- zero at head; no guard exists (clean, unguarded) |
| quote_style in services.yaml, *.py, blueprints (1 straight, 0 typographic: no sibling rule to break) | not applicable -- clean at head, unguarded |

Each instance probe is the enumerator's SEAM line for that cell; it fails while its count is above 0.
For en and sv the house quote style is undecided (straight dominates); the fix picks one per
language and converges the minority, so the beyond-finding seams count whichever side loses.

## Barrier

None exists (`barriered: false`). Proposed: lift the enumerator into a `tests/` text-style check
over the same surfaces, failing on any non-zero seam (under 1 s, one node call); cost-test per
`root-cause.md` belongs to the class's fix group.
