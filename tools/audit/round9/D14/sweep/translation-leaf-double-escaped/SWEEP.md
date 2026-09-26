# Class sweep — "translation leaf double-escaped"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D4-s2-03** (verified, medium — the `dhw_min_too_close` error text (both the
config-flow `dhw` step and the options-flow `hot_water` step, both languages) carries a literal
`\uXXXX` escape sequence baked into the JSON string value itself. HA's frontend formats error
text with ICU MessageFormat, where a backslash is not an escape character, so after `json.loads`
the sequence prints verbatim instead of the intended character — `garbled_chars_en=1`,
`garbled_chars_sv=9` per text, `escaped_error_texts_reached=4` of the 4 (flow × language) cells).

## Enumerator

`tools/audit/round9/D14/sweep/translation-leaf-double-escaped/enumerate.sh` reuses the finder's
own harness verbatim (`tools/audit/round9/D4/s2/escaped_text.py`), which already scans every
error text both flows can RETURN, looked up in `strings.json` and both `translations/*.json`
files exactly where the frontend looks — it IS the class enumerator.

Positive control: re-running reproduces `escaped_error_texts_reached=4`, `garbled_chars_en=1`,
`garbled_chars_sv=9`, and `escaped_texts_all_files=6` at exactly the finding's baseline counts.
Null control: `escaped_other_error_texts=0` — every other error text of both flows, in both
languages, carries no literal escape.
Perturbation: `--perturb` (decode the literal escapes in the loaded translation texts in memory)
drops both counts to 0 — documented in the harness header, the judge's own perturbation.

## Disposition

| seam | disposition | note |
|---|---|---|
| `strings.json`, `en.json`, `sv.json` × `config.error.dhw_min_too_close` / `options.error.dhw_min_too_close` (6 seams) | **instance** | D4-s2-03 itself — all 6 files carry the same double-escaped leaf (the `strings.json` source and its two compiled translations, for both flows that share the key). |
| Every other error text of the config and options flows, both languages | **guarded** | `escaped_other_error_texts=0` — the enumerator's own null control confirms no other leaf is affected. |

## Count

N = 1 verified finding (D4-s2-03, covering all 6 file/flow/language seams as one mechanism — one
mistyped leaf, propagated through the source strings file and both compiled translations) + 0
additional sweep-confirmed instances beyond it. **rca = false** (N=1 < 3, not a ledger class, not
barriered).

## Barrier proposal

A cheap CI check: after `json.loads`, no translation leaf's string value should match
`\\u[0-9a-fA-F]{4}` (a literal backslash-u, as opposed to a JSON-level `\uXXXX` that `json.loads`
already decodes) — catches exactly this double-escaping mistake at typo time. Estimated gate
cost: under 1s (regex scan of `strings.json` + `translations/*.json` after parsing).
