# R9-I4 root cause: governance tooling has no one-definition rule, so a concept's second reader is written beside the first and never compared

Seat: round-9 RCA, class I4 (N=5), beside F11.1; barrier for F11.4. Baseline `1936d5ca`; prototype on
`handoff/r9-rca-i4`, cut from `origin/main` `db878b29`. `.claude/` and `tools/` are byte-identical between
the two (`git diff --stat 1936d5ca db878b29 -- .claude/ tools/` prints nothing). Evidence:
`tools/audit/round9/rca/i4/` on the branch.

## Root cause

### Cause

A governance concept gets a second reader, written independently of the first and usually across a
file or language boundary. Nothing compares the two. When one reader is fixed, its sibling keeps the
old definition. Which side moved, from `git log` at the baseline:

- **D11-s1-71.** Both `paths:` parsers were born in one commit, `e4a388af` (#615): `rulePaths` in
  `policy_lint.mjs` and `parse` in `rules_sync.mjs`. That PR ran five review rounds (decision 0003,
  "One"). Neither parser moved later. They disagree on 2 of 7 shapes (below).
- **D7-s3-02.** `dead_methods` was added by #1395 as "the same screen as `dead_top_level_symbols`, one
  level in". Then #1538 (`16adac15`) moved `dead_top_level_symbols` and `dynamic_reference_audit` off
  `referenced_names` onto `bound_references`, and left `dead_methods` on bare names. Its docstring line
  sat in that commit's own diff context. The fixed reader moved; its declared twin did not.
- **D14-s2-03.** The class-id set has three definitions:
  - `bugclasses.json` keys, the ledger;
  - `finding.schema.json`'s enum, a copy kept equal by a `check-wave-script.mjs` test;
  - `audit-find.js`'s `CLASS_GUESS = /^([PI][0-9]+|new)$/`, a grammar standing in for the list, which
    nothing compares.
- **D13-s1-01.** "The pull request a first-parent commit carries" has four readers: `stamp.py
  pr_from_subject` and `delivery_status.py subject_number` (both shapes), `policy_lint.mjs`
  `MERGE_SUBJECT_RE` (squash shape only), and its API mode. The API mode drops a commit whose `pulls`
  answers `[]` as "a stamp". Because the subject arm cannot read a merge-commit subject, nothing marks
  the 52 dropped (cited, REPORT.md, not re-run: the `--stats` window needs a live `origin/main` at the
  baseline). The same skip is D11-s1-02's (class I3).
- **D11-s1-72** (cited, `l3_gov_pin.py`, reproduced at baseline, `escaping_cells=3 of 3`). `entities.py`
  pins `_GOV_WF = ".github/workflows/governance.yml"`, while `governance_cost.py` derives the governance
  workflow set.

The repository already has the remedy, applied once per instance and never as a rule:

- `counts.mjs` exists so that "One enumeration, two callers" share a module (#581).
- `policy_lint.mjs` reads `web-fix-wave.js`'s `VERDICT_RE` out of its source text.
- `tests/README.md` "A test must never re-implement what it is testing" is enforced by `closure.py
  no-copies`, but for tests against production only. No rule or check covers one governance tool
  re-implementing another.

**Class search beyond the sweep** (`node .claude/workflows/agreement.mjs` at `db878b29`, `ag-main.out`,
exit 1):

- `merge-subject-pr`: **304 of 323** live and boundary subjects divergent. `policy_lint.mjs` subject
  mode reads `null` on every `Merge pull request #N from …` subject, where `stamp.py` and
  `delivery_status.py` read N.
- `finding-class-id`: `P99`, `I99` and `P0` are admitted by the intake regex and refused by both the
  ledger and the schema.
- `rule-frontmatter-paths`: `trailing_comment` and `list_under_other_key` diverge. The other 5 shapes
  and 10 live rules agree. `single_quoted`, `unquoted` and `flow_style` read `[]` in **both** parsers,
  a shared misreading that agreement cannot see.
- Discovery: **23** regex sources are shared by two or more of 87 governance code files. Three are the
  round-9 instances. Of the other 20, these repeat a concept's grammar across files; they are
  candidates and **not measured divergent**:
  - figure path and assignment grammars (`figure_census.mjs`/`figure_lint.mjs`);
  - the delivery-row anchor (`policy_lint.mjs`/`counts.mjs`; `policy_lint.mjs`/`record-predicate/sweep.mjs`);
  - the roster glob `wave-.*-groups\.json` (3 files);
  - the `VERDICT_CLASSES`/`VERDICT_RE` source extractors (3 files);
  - the README claim grammars (`doc_claims.py`/`entities.py`);
  - the mutation-ledger line grammar (`mutation_table.py`/`ledger_merge.py`).

**Historic concentration.** 12 of the 22 recorded I4 instances name `policy_lint.mjs`: 9 of the 14
in round 8's `findings.tsv` (R4–R7), round 8's #1549, and 2 of round 9's. That file's `--stats`,
`--record` and `--sunset` re-derive facts that other tools, or GitHub, define.

### Process state: (a)

No process requires a governance concept to have one definition, or requires its readers to be
compared:

- The one-definition rule that exists (`tests/README.md` plus `closure.py no-copies`) is scoped to
  tests against production.
- `bugclasses.json` records I4 as `"detector": null`, `"status": "open"`. Its `detector_idea`, "Per
  reader pair, generated boundary cases asserting both readers give the same verdict", was never built.
- `fixer.md` step 8 asks a fixer for "a rule that enumerates the class's seams". Whether #1605's fixer
  ran one for "readers of liveness" cannot be read from the tree: PR bodies are not in it, and this
  seat runs no `gh`. So this is not recorded as (b).

### Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, wall-clock per audit round.

- **P(recurrence) is measured.** `bugclasses.json` I4 lists 14 instances over rounds 4 to 7. Round 8
  has 3 (#1538, #1539, #1549). Round 9 has 5. That is 22 in 6 rounds, and 6 of 6 rounds hold at least
  one, so the mean is 3.67 per round.
- **Defect cost is measured on the fix side only; audit discovery is excluded.** #1566 (#1549) took
  136 min from its first commit to the merge. #1605 (R8-I4, 2 issues) took 1197 min from its own first
  commit `16adac15`, of which the wait for the groups it was ordered after is a part. That gives 136 to
  599 min per instance.
- **Reach is 2 of 5 round-9 instances demonstrated** (D11-s1-71, D14-s2-03), plus D13-s1-01's subject
  arm, which is not counted. The prevented cost per round is 3.67 × 2/5 × 136..599 = **200..879 min**.
- **Standing cost is measured**: 0.9 to 1.3 s wall and 0.39 s CPU per run. Runs happen on merges
  touching governance code, which is 259 of 300 merges in `v6.5.0..1936d5ca`, about 130 per round. The
  cost is 130 × k × 1.3 s ≈ **2.8 min × k**, where k is CI runs per merge, which was not measured.
- **Verdict: it passes for k < 71 at the lower bound.** The one-off cost is classifying the 20 shared
  grammars, done once by F11.4's fixer.

### Barrier: an agreement lane, and grammar discovery

`.claude/workflows/agreement.mjs` (235 lines, sha1 `8191123c601a908ec90b649264cd73cb81c16fee`) has two
arms.

1. **Pairs.** Each registered concept names its readers and a corpus. The corpus is the live tree's
   instances plus the boundary cases a finding showed. Every reader answers every item, and any
   disagreement is refused. A reader that throws, or an empty corpus, is REFUSED, never a pass. The
   readers are the real ones: imported, or read from their source text the way `policy_lint.mjs` reads
   `VERDICT_RE`. None is a copy.
2. **Discovery**, decision 0003's bounded direction. A regex source in two or more governance code
   files must be named in `SHARED_GRAMMARS` with a disposition: `pair:`, `module:` or `not-a-concept:`.
   An entry that no longer spans two files is DEAD. A second reader written tomorrow with a copied
   grammar is found without anyone listing it.

| run | tree | result |
|---|---|---|
| fail | `db878b29` (`ag-main.out`) | exit 1: frontmatter 2 of 17 divergent, class-id 3 of 25, merge-subject 304 of 323; 20 grammars unregistered |
| pass | fixed tree, pairs arm | exit 0, 0 divergent in all three pairs |
| pass, D11-s1-71 grammar | fixed tree, discovery (`ag-fixed-disc.out`, then `ag-fixed-disc2.out`) | first the entry `-"([^"]+)"` is DEAD (the grammar now lives in one module); once it is removed, the unregistered set is byte-identical to `db878b29`'s 20, so the instance's grammar alone resolved |
| mutant | fixed tree, the judge adds `I6` to `bugclasses.json` and nothing else | exit 1, DIVERGENT `I6`: ledger true, schema false, intake false |
| null: skip | a reader that cannot be read (`parse` renamed) | REFUSED `no top-level function parseGone`, exit 1 |

"Fixed tree" is `fixed-demo.patch` on `db878b29`:

- A new `rule_frontmatter.mjs` (11 lines) that `policy_lint.mjs` `rulePaths` and `rules_sync.mjs`
  `parse` both import. `rules_sync.mjs` exports `parse` and guards its main. `rules_sync.mjs --check`
  still prints `RULES-SYNC ok`.
- `MERGE_SUBJECT_RE` reads both shapes, as `stamp.py` does.
- `audit-find.js` `CLASS_GUESS` names the ledger ids. The pair lane is what keeps that copy honest.

The full discovery PASS needs F11.4 to classify the 20 grammars. It is not claimed here.

`python3 tests/structure.py` on the branch prints `STRUCTURE RATCHET PASSED`. The ratchet measures
`custom_components/` only.

**Residual, for tvofi.** A second reader with a **different** grammar for a concept nobody has
registered is not found mechanically. No signature identifies a concept, and none of the three forms
the sweep proposed (a shared module per instance) prevents the next one. The closing step is
procedural, and it is policy, so it is a proposal only. It addresses (a):
- `fixer.md` step 8 would gain "a fix that changes one reader of a governance concept registers the
  concept in `agreement.mjs` with every reader the enumeration returns".
- `tests/README.md`'s no-copies section would gain "and one governance tool re-implementing another".

## Plan fold

- **Landing PR: F11.4, as planned.** It follows F10.4 (D7-s3-02) and F11.1 (D11-s1-71, D11-s1-72,
  D13-s1-01).
- **Carry into F11.1's brief** (the orchestrator writes it). F11.1's fixes should leave the readers
  importable, so F11.4 needs no source-text reads or temp modules:
  - export `rulePaths` and `mergedPRs` from `policy_lint.mjs`, or the shared frontmatter module;
  - `rules_sync.mjs`: `export function parse` and a main guard (it writes `.cursor/rules/` on import
    today);
  - D13-s1-01's fix decides whether subject mode reads both shapes. If it deliberately does not, F11.4
    registers that difference instead of the pair.
- **Carry into F10.4 and F11.1**: register their pairs in F11.4, namely `dead_methods` against
  `bound_references` over methods (D7-s3-02), and `entities.py`'s GOV set against
  `governance_cost.py`'s derivation (D11-s1-72). Neither is prototyped here.
- **Files:**
  - `.claude/workflows/agreement.mjs` (new). It evaluates tracked source through `new Function`, so it
    joins `codeowners_gap.py`'s F surface: `rules_sync.mjs` must be pinned and `audit-find.js`
    **code-owned**.
  - `audit-find.js` (**code-owned**, already F11.4's).
  - A run step in a required job: `governance.yml` is **code-owned**, or the step goes into
    `check-wave-script.mjs`'s `wave-script` job.
  - `tests/entities.py` must classify the new file.
  - No policy file.
- **Estimated lines** (prototype, `wc`/numstat): barrier 235 plus about 20 registry lines for the
  classification; instance fixes +24/−20 including the new 11-line module. Discovery run 0.1 to 0.2 s,
  pairs 0.8 to 1.1 s.
- **No change to the PR set or `after` edges.**

## Figures

| figure | enumerator |
|---|---|
| 2/17, 3/25, 304/323 divergent; 23 shared grammars, 20 unregistered | `node .claude/workflows/agreement.mjs` at `db878b29` |
| 0 divergent | same, with `fixed-demo.patch` |
| divergent_cells=2 of 6, escaping_cells=3 of 3, i4_reader_sites=31 | `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I4/enumerate.py` at `1936d5ca` (sweep export `b2e3560671`) |
| 22 instances / 6 rounds | `bugclasses.json` `I4.instances` (14) + R8-I4 `issues` (2) + #1549 + `CLASSES-DRAFT.json` I4 `n` (5) |
| 12 of 22 in policy_lint.mjs | `git show 12743bf7:handoff/round8/findings.tsv`, class I4 rows naming `policy_lint.mjs` (9), + #1549, + D11-s1-71 and D13-s1-01 |
| 136 / 1197 min | `git log` first own commit to merge, #1566 `ca8204f4`, #1605 `23eaf856` (own first commit `16adac15`) |
| 259 of 300 merges | `git rev-list --first-parent --merges v6.5.0..1936d5ca`, diff names under `.claude/workflows/`, `tools/`, `tests/*.py`, `tests/*.mjs` |
