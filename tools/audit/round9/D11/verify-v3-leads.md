# D11 — verify-v3-leads (V3: reach and class)

## D11-s1-71 — rules_sync vs policy_lint frontmatter parsers disagree on 2 of 6 shapes

**Executed numbers.** Re-ran `tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs`: baseline `divergent_cells=2 of 6` (`trailing_comment`, `list_under_other_key`); `--perturb eol`: `1 of 6`. Exact match. load1 2.38-2.43, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D11/verify-v3-leads/v3_frontmatter_seam_recheck.mjs`. A first pass, grepping for the literal text `paths:`, was wrong in both directions: it missed `rules_sync.mjs` entirely (its `parse()` never spells the word `paths:` — it grabs every `- "..."` line in the frontmatter by position, confirmed by reading line 40: `[...fm.matchAll(/^\s*-\s*"([^"]+)"\s*$/gm)]`, exactly matching the finding's stated mechanism), and it false-hit `check-wave-script.mjs` (whose only "paths:"-shaped text is the unrelated object key `harness_paths: []`). Corrected method: narrowed `.claude/workflows/*.mjs` to the 4 files that reference `.claude/rules` at all, then read each by hand — `brief_lint.mjs` discusses citation "paths" only in prose (per `.claude/rules/brief-citations.md`, it explicitly does not read `tools/audit/briefs/`), `friction_issues.mjs` only quotes rule filenames as strings. Result: exactly 2 real readers, `policy_lint.mjs` and `rules_sync.mjs` — matching the finding precisely.

**Attacks.** Not a Home Assistant runtime path — this is repository tooling (governance/CI), so the "real HA" half of the V3 lens does not apply directly; it is, however, confirmed reachable in the sense that matters for this dimension: both `rules_sync.mjs --check` and `policy_lint.mjs` run for real against the actual `.claude/rules/*.md` files in CI. Severity: `live_rules_divergent=0 of 10` — none of the 10 live rules trip it today, so this is a capability, not an incident; low/hygiene-adjacent bug is earned, not inflated.

**Class.** `I4` (two independent parsers or definitions of one concept disagree) — exact match.

**Metric definition.** Probe rule frontmatters on which `rules_sync` `parse().paths` and `policy_lint` `rulePaths()` return different lists (JSON-compared).

**Vote: verify.** Severity low, class I4, seam_rule_enumerates true (the finding's own literal seam_rule text is imprecise as a reproducible grep, but the reader set it names is independently confirmed exhaustive by hand).

## D11-s1-72 — entities.py GOV pin reads governance.yml only

**Executed numbers.** Re-ran `tools/audit/round9/D11/leads/l3_gov_pin.py`: baseline `escaping_cells=3 of 3`, `positive_control_pin_fails=1 of 1`, `live_gov_missing=1` (rerun-stale-verdict); `--perturb all-files`: `0 of 3`. Exact match. load1 2.37, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D11/verify-v3-leads/v3_gov_pin_source_recheck.py`: read `tests/entities.py`'s pin source directly (`_DS_GOV = Path(".github/workflows/governance.yml").read_text()` — confirms the pin's second arm reads exactly 1 file), read `governance_cost.py`'s own derivation comment directly (names 4 files: `governance.yml`, `tests.yml` for `briefs`, `pr-contract.yml`, `budget-raise-gate.yml`), and confirmed `budget-raise-gate-rerun.yml` contains a real `rerun-stale-verdict:` job (`rerun_job_exists=1`) that is absent from `GOV` (`rerun_job_in_gov=0`).

**Attacks.** This is not a hypothetical escaping cell: `budget-raise-gate-rerun.yml`'s `rerun-stale-verdict` job already exists today, is already absent from `GOV`, and isn't even named by `governance_cost.py`'s own derivation comment — so the pin is already blind to a live governance job at baseline, with no perturbation required (`live_gov_missing=1` fires unperturbed). Consequence is bounded to `D13`'s cost-accounting split (a governance job's seconds counted as non-governance overhead) — not a security or merge-gate bypass — so low stands rather than escalating; flagged here for the judge's attention as an already-realized gap rather than a pure capability, since that distinction matters for how urgently it should be fixed.

**Class.** `I4` (two independent definitions of one concept disagree: the derivation comment's stated rule vs. the pin's actually-enforced, narrower rule) — confirmed, in preference to `I3` (this is not a skipped/stale-ref/bypassable check, it is a narrowly-scoped one).

**Metric definition.** Probe cells (one new job appended to a workflow file GOV's rule or D13's re-derivation counts as governance) in which entities.py's GOV pin still passes.

**Vote: verify.** Severity low, class I4, seam_rule_enumerates true.
