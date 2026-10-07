# D6 verify report (v1) — round 8

Single verifier on the D6 panel (owner's call: one verifier per dimension this
round, not three). I carry both halves of `verifier.md`: re-ran the finder's
harness and perturbation, and wrote an independent harness under my own
metric definition.

Tree: `/home/claude/audit-r8/seats/D6-v1`. Finder evidence copied in from
`D6-s1` and `D6-s2` (`cp -rn ... tools/audit/round8/D6/.`). D6-s2 filed zero
findings (11 non-findings, all confirmed inline by the reporter's own greps —
no overlap with D6-s1-01, nothing further for me to verify there).

## D6-s1-01 — README Requirements section omits threadpoolctl

**Claim:** README.md's `## Requirements` section lists Python deps as
"`numpy` and `scipy`, installed automatically from the integration manifest",
but `manifest.json`'s `requirements` also pins `threadpoolctl>=3.5.0`, which
is a real runtime dependency (resolved dynamically by name in
`optimizer.py`), and README never names it in that section.

### 1. Re-ran the finder's harness exactly

```
$ python3 tools/audit/round8/D6/s1_requirements_claim.py
RESULT manifest_requirements_count=3 packages ['numpy', 'scipy', 'threadpoolctl']
RESULT undocumented_count=1 packages ['threadpoolctl']
RESULT undocumented_and_used_count=1 packages ['threadpoolctl']
RESULT load1=18.09 load
RESULT thread_factor=1.0 ratio
```

Matches the finder's reported value=1 exactly. Box was under heavy
contention (load1≈18-20 across all runs, shared 4-vCPU box per BASELINE.md)
but this harness is a pure text/AST scan with no timing component, so
contention does not affect the number — flagging it per instruction 3 anyway,
as required.

**Perturbation, re-run myself:** added `"pyyaml>=6.0"` to a scratch copy of
`manifest.json`'s `requirements` (not added to README), re-ran:
`undocumented_count` went 1→2, naming `pyyaml` as the new entry, exactly as
the finder's harness docstring predicts (`expected_direction: to_zero` is
about *removing* threadpoolctl, which I also re-checked: doing that dropped
`undocumented_count` back to 0). Restored `manifest.json` from the saved
original; `diff` against `/home/claude/audit-r8/export` confirms byte-identical.

### 2. My own harness, independent method

Wrote `tools/audit/round8/D6/v1_requirements_gap.py`. Two deliberate
differences from the finder's method, to attack it from a different angle:

- **Documentation check is whole-README, not section-scoped.** The finder's
  harness only looks inside the text between `## Requirements` and the next
  `## `. I searched the entire `README.md` for the string `threadpoolctl`
  (case-insensitive) — it does not appear anywhere in the file, confirmed
  separately with a plain `grep -n -i threadpoolctl README.md` (no output).
  This rules out the possible attack "maybe it's just outside that one
  section, documented elsewhere in the README" — it is not documented at all.
- **"Actually used" check is AST-based, not substring-based.** The finder's
  `really_used` check is `p in src_text`, a literal substring test that would
  also fire on the word appearing only in a comment. I parsed every
  production `.py` file's AST and required either a real `import`/`from
  import` statement naming the package, or an `importlib.import_module("...")`
  call node with that literal string argument — the stricter test actually
  matches how `threadpoolctl` is resolved in this codebase per the
  `optimizer.py:265` comment ("Resolved by name, not imported").

```
$ python3 tools/audit/round8/D6/v1_requirements_gap.py
RESULT manifest_requirements_count=3 packages ['numpy', 'scipy', 'threadpoolctl']
RESULT anywhere_undocumented_count=1 packages ['threadpoolctl']
RESULT ast_import_used_count=3 packages ['numpy', 'scipy', 'threadpoolctl']
RESULT anywhere_undocumented_and_used_count=1 packages ['threadpoolctl']
```

Metric definition (mine): count of manifest.json requirement package names
absent from README.md in its entirety (case-insensitive substring) AND
reached by a real `import`/`from-import` AST node or an
`importlib.import_module("<name>")` call node in production
`custom_components/heatpump_optimizer/*.py`.

Same result: 1 (`threadpoolctl`). Re-ran the perturbation on my own harness
too (added `pyyaml` to requirements): `anywhere_undocumented_count` went
1→2, `ast_import_used_count` unchanged at 3 (pyyaml correctly excluded, since
it is not actually imported by anything — the AST check is not fooled by the
literal string I chose not to reference in code). Restored and re-diffed
against the export; byte-identical.

### 3. Attacking the method (verifier.md order)

- **Contention:** no timing measured; the harness is deterministic text/AST
  parsing. Not applicable.
- **Wrong gate mode:** not a suite-gap or gate-mode claim; this is a static
  docs/manifest cross-check, no gate involved.
- **Grid artefact:** single scalar count over the whole repo, not an
  aggregate over cells. Not applicable.
- **Null control:** the perturbation *is* the null/positive control pair —
  adding an undocumented, unused package (pyyaml) correctly moves
  `undocumented_count` but *not* `undocumented_and_used_count` (both harnesses
  agree on this), and removing threadpoolctl correctly zeroes the count. Both
  directions behave as the finder predicted; the control is not missing.
- **FakeHass vs real HA reachability:** irrelevant — this is a build-time/doc
  claim about manifest contents and README prose, not a runtime code path
  gated by the test stub.
- **Severity earned by consequence:** `threadpoolctl` is looked up inside a
  `try/except (ImportError, AttributeError)` and the code tolerates its
  absence (falls back to `_threadpool_limits = None`), so the practical
  consequence of the doc gap is small — a reader who skips it does not break
  the integration, only loses BLAS thread pinning silently. This supports
  "low" severity as filed, not higher. I considered whether this weakens the
  finding to a non-finding (i.e., "not really a dependency since it's
  optional"), but manifest.json still pins and auto-installs it unconditionally
  regardless of whether the code tolerates its absence, and the README claim
  ("`numpy` and `scipy`... installed automatically from the integration
  manifest") is still an incomplete list of what actually gets installed —
  the claim is about documentation completeness, not about runtime necessity.
  So the gap is real; severity "low" is right, not higher.

### 4. Test-gap claim requirement

Not applicable — this is a documentation-accuracy finding (D6), not a
test-suite-gap claim, so no production mutation/kill-test is owed.

### Vote

**verify**, severity **low** (as filed). My number: `undocumented_count=1`
(finder's harness) and independently `anywhere_undocumented_count=1` (my own
AST-based harness) — both agree, both survive the perturbation and its
inverse, both survive a whole-file (not section-scoped) documentation search,
and the underlying facts (manifest pins threadpoolctl, README's Requirements
section and the entire README never mention it, the package is genuinely
resolved at runtime via `importlib.import_module`) are directly confirmed by
reading the files. No mechanism overlap with D6-s2 (which filed zero
findings).
