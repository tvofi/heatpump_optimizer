# BLOCKED: r11-seam-inputs-guards (fixer seat, base bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f)

Question: The brief says "Do your work inline, with no subagents" and also "never set FRUGAL_ALLOW_INLINE"; the frugal plugin's PreToolUse hook (frugal@synced, guard on inline search ops) refused the sixth inline read of this prompt ("inline search op 6 this prompt exceeds budget of 5 ... Delegate the remaining discovery to frugal:scout or frugal:extractor"). The brief forbids both remedies the hook offers, and a scheduled seat gets no second prompt to reset the budget. May this seat delegate discovery reads to frugal:scout / frugal:extractor, or will the dispatch set FRUGAL_ALLOW_INLINE=1 for the seat?

State reached before the refusal (no code written, nothing pushed but this file):

- Setup: `tools/audit/seat/cloud-setup.sh --check` OK; origin/main == bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f.
- D2-s3-02: at bc658f9ded, `inputs.normalize_price_per_kwh` already returns `value * per_kwh / 100.0` on the PRICE_MINOR_UNITS branch (read, not yet re-run through `D2/s3/m4_tariff.py`); owner precedent (1) would make it "not reproduced at main, pinned" once the harness reads 0.
- D7-s3-01: at bc658f9ded, `inputs.temperature_from_c` already returns `value_c / factor - offset` (read, not yet re-run through `D7/s3/m8_agree.py --only temperature_roundtrip`); same precedent.
- D1-s3-01, D1-s3-03, D1-s2-05, D1-s2-51: not yet read; harnesses are in the plan/r11 export (819aa2e354b4e5baaf824b8568fd72bea8168a75, dev/audit/rounds/round11/D1/).
