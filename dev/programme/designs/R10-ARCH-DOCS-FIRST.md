# R10-ARCH-DOCS-FIRST: design note (architect note, extended)

Base `8a4c438e7d9a6e2c492a1733d658d96b7b1eedcf` (origin/main; no predecessor handoff: `after` is empty).
Roster `handoff/audit-r10-roster` `b93ece169acfa8c97b469bbb18df06267aa14f6f`. Contract `dev/governance/roles/designer.md`.
Finding #2395 has no finder harness: owner report (tvofi, 2026-10-17 and 2026-10-22). O9 (the harnesses README) resolves to no file in
the tree: `72826387f^:tools/audit/harnesses/README.md` was deleted by 72826387f, and `dev/audit/harnesses/` has no index.

## Seam

Prose and diagrams only; no production module changes. Each claim check has one owner:
- `tests/entities.py` already owns the counted claims in `docs/architecture.md` (opening counts, module map, HA boundary, option pages, services, sensors).
- `tests/doc_claims.py` owns the counts across reader docs (its `DOCS` set is `docs/*.md`; it reads `README.md` separately) and the mermaid pin.
- This group's new checks go into `tests/doc_claims.py` as one function. No new gate script.
- The checker R10-ROUND-PLAYBOOK asks for is that same function, not a second instrument (see 6).

## 1. Document map

| file | sections, and what each states |
|---|---|
| `docs/architecture.md` | Keep every `##` section on main: the counted ones stay tree-exact. **How the pieces fit**: the seed's four-region diagram (outside / HA boundary / pure core / learners) and its region legend, re-derived at base, because the seed is 2437 commits behind and states 77 modules where the tree has 81. **Module map**: the tree only, since `tests/entities.py` refuses a name not on disk; modules the plan adds go in a *Planned modules* list **below** the code block, each with a marker. **Where the architecture is measured**: from the seed, updated to name `tools/audit/archscore/` and the wiring check. New section **The shape at programme end**: per-module deltas from the code groups (R10-ARCH-SHAPES, R10-PARAMS-OWNER, R10-LIVESTATE, R10-SENSOR-PAYLOAD, R10-HEAT-METER, ...), each a marked line. |
| `dev/README.md` (new) | The developer onboarding, holding everything the owner asked to sit "beside the CI shape". **Layout of `dev/`**, **governing documents**, **the work in order** (audit → fix → design → review → train → record → stamp), **requirements before a push**: all from seed 0edd7fa66, with literal counts removed ("ADRs 0001-0013", "D0..D15"). **CI shape**: the job graph, plus the seed's `0edd7fa66:dev/CI-GATE.md` folded in as the refusal order (selection → ratchet → claims → required check → train). **Orchestration machinery**: components (carry (a)). **One handoff's path**: carry (b), with each ledger kind it opens or closes. **Who decides**: carry (c). **Harnesses**: a generated-by-command index of `dev/audit/harnesses/` (the O9 fold); a re-created README would be a second index. |
| `README.md` | One line in a developer paragraph pointing to `dev/README.md`. No row in `## Documentation`: `tools/site/build_docs.mjs` builds every row of that table as a user page. |
| `tests/layout.json`, `tests/closure.py` | Add a `dev` category naming `dev/README.md` exactly (seed 0edd7fa66). The file enters `tests/doc_claims.py`'s measured closure rather than `INERT`, because the check reads it. |

What survives from the seeds:
- From 4305cd109: the diagram regions, the legend prose and "Where the architecture is measured". Every count in it is re-derived.
- From 0edd7fa66: the layout tree, the governing-documents table and the work order, with counts and file lists replaced by commands. Its `0edd7fa66:dev/CI-GATE.md` survives as the refusal-order subsection. Its `main-protect-checks` contexts are redrawn to R10-CI-LAYOUT-P2's single `gate`.

Carry: R10-ARCH-DOCS (item M1)

## 2. Deriving the protected final shape

Inputs, all read at the fixer's merge base and never from this note:
- (i) every roster group not done, enumerated by `jq -r '.groups[]|select(.resume.stage!="done")|.group' dev/programme/rosters/wave-r10-groups.json` on the roster ref, with each group's `brief`, `after`, `carry` and `architect_note`;
- (ii) the design refs those name: `handoff/orch-machinery` 09174d94e (§6.2 job table, §6.3 ledger kinds) with `review/orch-machinery-design` 0bd5d12f0, R10-CI-LAYOUT-P2's `1371a0a6:DESIGN-P2.md` (§0 and §2.1) with review afc00bfe, every open `design/*` ref, and every approved architect note;
- (iii) the plan page: `tools/plan/replan.py` (its `--out` file) drawn by `tools/audit/seat/plan_page.py`, plus the plan of record `dev/programme/plan-2026-09-open-issues.md`.

Procedure:
1. Write each element from the tree when it exists at base (`git ls-files` or a grep of a workflow's job ids).
2. Otherwise write it from the brief of the group whose `files`, or whose design, lands it, and mark it (see 3).
3. An element that two non-done groups' briefs state differently is not merged silently. Draw the shape the owning group's brief states. The owner is the group whose `files` holds the path; if that is ambiguous, the group whose design ref is approved. Write one `Carry:` to the other group in the body, by `dev/governance/rules/finding-propagation.md`.

The disagreements this note found are routed in Notes for the fixer (items D1–D5).

## 3. Target-marker grammar

```
marker  := "[target: " group ( ", " group )* [ "; owner step" ] "]"
         | "[retired-by: " group "]"
group   := "R10-" [A-Z0-9-]+          ; must be a key in wave-r10-groups.json
```

- A marker qualifies the smallest enclosing unit: a list item, a table row, a heading (which covers its section), or a mermaid node or edge label.
- `target`: the element exists only once the named group merges.
- `retired-by`: the element exists on main and is absent from the final shape. Use it for things a reader still meets today, such as `.github/workflows/pr-contract-rerun.yml`.
- `; owner step`: the element lands only on the owner's own action, such as the ruleset cut-over.
- **Marked text states no numeral.** `tests/doc_claims.py` and `tests/entities.py` read numerals against the tree, so a planned count would go red today.

Examples:
- Prose: `- the supervised beat (beatd), one job table for every detached job [target: R10-ORCH-MACHINERY]`.
- Mermaid: `R[("ruleset requires only gate<br/>[target: R10-CI-LAYOUT-P2; owner step]")]` and `T -.->|"[target: R10-CI-LAYOUT-P2]"| G`.

The regex `\[(target|retired-by): (R10-[A-Z0-9-]+(, R10-[A-Z0-9-]+)*)(; owner step)?\]` finds every marker in prose and mermaid alike. At R10-ARCH-DOCS it resolves each one:
- `target`: the group is `done` and the element is present, so the marker becomes plain text;
- `retired-by`: the group is `done` and the element is absent, so the line is deleted;
- any other state goes red.

## 4. Diagrams, format, visual language

The diagrams:
- **Architecture** (`docs/architecture.md`): a flowchart, with dashed edges for planned flow.
- **CI job graph** (`dev/README.md`): P2's umbrella, `.github/workflows/ci.yml` → prelude → units → pr-contract → `gate` → ruleset. The units already on main are drawn from `.github/workflows/`.
- **Refusal order** (`dev/README.md`): from the seed.
- **Orchestration machinery components** (`dev/README.md`): beat jobs, ledger and kinds, bus refs, the relay's arms, train and pitch, dispatch records, heartbeat and watcher, hold list, roster branch, plan page, flow toolkit.
- **One handoff's path** (`dev/README.md`): a `sequenceDiagram`, with a note per step naming the ledger kind opened or closed.

Format: GitHub mermaid. Committed SVGs would need a renderer in the gate: mermaid is installed only by the Pages workflow (`tools/site/package.json`), so an SVG would add a second figure-versus-source drift surface, the class P40 names.

Visual language without hand-copying:
- No mermaid block carries a hex value or an `%%{init}`.
- Meaning lives in **shape**, so it survives both themes:
  - a seat or agent is a stadium `([ ])`;
  - a script, or a job run detached by `tools/audit/seat/daemonize.py`, is a rectangle;
  - a person's or an agent's decision is a rhombus `{ }`;
  - a ref or store is a cylinder `[( )]`;
  - a planned edge is dashed `-.->`.
- Colour comes from the renderer. GitHub follows the reader's light or dark mode. On the site, `tools/site/build_docs.mjs` already redraws neutral and dark on toggle.
- The one tree read is a token map: `tools/site/build_docs.mjs` parses `docs/site/docs.css`'s `:root` block and its dark block (`--surface-2`, `--accent`, `--ink`, `--ink-2`, `--line`, `--f-body`) into mermaid `themeVariables` per theme. That is a small edit to a file outside this group's `files` (decision: orchestrator). Without it, the site keeps mermaid's neutral and dark themes, and the docs are still correct. Carry: R10-ARCH-DOCS (item V1)

## 5. Budgets (measured at base)

- `node tools/policy/policy_lint.mjs --budgets`: no file this group writes matches `POLICY_GLOBS`. It already matches `dev/audit/README.md` and `CLAUDE.md`, and this group edits neither. Always-loaded and corpus stay flat. **No CLAUDE.md row is added**: `--budgets` already reports always-loaded above its cap and inside its band, so a row there is the one place this group could cost a raise. **No budget raise.**
- `tests/structure_budgets.json`: every metric is a code metric, so the docs touch none of them. The doc_claims function is test code and outside the measured package.
- `tests/closures.json`: `tests/doc_claims.py`'s closure grows by `dev/README.md`. Re-record it with `tests/derive_closures.sh --single tests/doc_claims.py` on Linux, or let the UNDER-SCOPED autofix in `dev/governance/rules/ci-autofix.md` do it; never hand-edit the recording.

## 6. Test and control plan (the fixer's)

One new findings function (doc wiring: paths, tree, roster), in `tests/doc_claims.py`, run over `docs/architecture.md`, `README.md` and `dev/README.md`. It checks:
- (a) every backticked repo path resolves in `git ls-files`, or carries a `target` marker;
- (b) every marker is well formed and names a roster group;
- (c) a `target` marker names a group that is **not** done, since a done group's marker is stale;
- (d) every mermaid edge refers to a node the block declares, and every block opens with a known diagram type (a structural lint, because the gate has no mermaid);
- (e) no hex colour or `%%{init` appears in a mermaid block.

Fixtures and controls:
- **Red fixture**: inline strings, in the style of the existing `mermaid_pin_findings` controls. A renamed path, `[target: R10-NOPE]`, a marker naming a done group (`R10-CI-LAYOUT-P1`), an edge to an undeclared node, and a hex fill. Each yields its finding.
- **Null control**: the same strings, corrected, yield none.
- **Real-tree arm**: the check runs on the committed docs and passes.
- **Mutation proof**: target the path-resolution and done-group predicates.

A real `mermaid.parse` belongs to R10-ARCH-DOCS's wiring test, wherever mermaid is installed. Carry: R10-ARCH-DOCS (item T1)

## Alternatives

- **Generated SVG pairs with `<picture>`**: lost, because mermaid exists only in the Pages job (see 4) and a figure would need its own parity check.
- **Onboarding in `README.md`**: lost, because the docs build renders README as the product page and `tests/doc_claims.py` grades it as a user doc.
- **Two files, the seed's `dev/README.md` plus `0edd7fa66:dev/CI-GATE.md`**: lost, because the owner asked for the machinery beside the CI shape, and a second file is a second classification and a second wiring target.
- **Planned modules written inside the module map**: lost, because `tests/entities.py` refuses a name not on disk.

## Sibling sites

`git grep -n '```mermaid' -- '*.md'` lists the blocks: `README.md`, `docs/architecture.md`, `docs/how-it-works.md`, `docs/configuration.md` and `docs/setup.md`. Check (e) covers them. Checks (a) to (d) run only on this group's three files; R10-ARCH-DOCS may widen them.

## Hot files and serial position

- Wave 1. `docs/architecture.md` is touched by no other non-done group.
- `README.md` is shared with R10-ARCH-DOCS only.
- `tests/doc_claims.py`, `tests/layout.json` and `tests/closure.py` are shared with R10-MERGE-SUBJECT-HARDEN (`tests/closure.py`). That collision is a merge-order one, not a seam one.

## Notes for the fixer

- Carry: R10-ARCH-DOCS (item D1). The FIRST carry says the machinery is drawn "as built at this stage's merge base". The newer brief (owner, 2026-10-22) says the final shape. Draw the final shape with markers; ARCH-DOCS checks it against the R10-ORCH-MACHINERY tables at its own merge base.
- Carry: R10-ORCH-MACHINERY (item D2). Four groups each claim the plan page or model. R10-PLAN-ARTIFACT extends `tools/audit/seat/plan_table.py --html`, ORCH-MACHINERY part (3) builds a shared model builder, R10-FLOW-TOOLKIT-MODEL extends that model, and R10-FLOW-BOARD writes to `tools/audit/seat/state_docs.py`. Meanwhile `tools/audit/seat/plan_page.py` is already on main. Draw one page, `tools/audit/seat/plan_page.py`, with the model builder marked `[target: R10-ORCH-MACHINERY]`. ORCH-MACHINERY confirms it owns the builder.
- Carry: R10-ROUND-PLAYBOOK (item D3). Its path-resolving control is this function. Extend that function to `dev/audit/README.md`; do not build a second checker.
- Carry: R10-CI-LAYOUT-P2 (item D4). Today the docs name `main-protect-checks` and its contexts; P2 replaces the required contexts with the single `gate` as an owner step. Draw the ruleset node `[target: R10-CI-LAYOUT-P2; owner step]` and `.github/workflows/pr-contract-rerun.yml` `[retired-by: R10-CI-LAYOUT-P2]`.
- Carry: R10-REPLAY-SCOPED (item D5). R10-REPLAY-SCOPED and R10-REPLAY-LANE edit `.github/workflows/tests.yml`, and R10-FLOW-BOARD edits `.github/workflows/governance.yml`. None has an `after` edge to R10-CI-LAYOUT-P2, which makes both files `workflow_call`-only units. The doc draws their jobs as `tests / <job>` and `governance / <job>` units either way; the order is the orchestrator's decision.
- Carry: dismissed: the Lean flow study's ORCHESTRATOR-PROMPT is on no ref this seat can read, so the orchestrator supplies it in the dispatch (item I1).
- Carry: R10-ARCH-DOCS (item F1). Fold P40 there: the committed `docs/img/card/*.png` figures are compared to the card. This group commits no figure.
