# R10-ARCH-DOCS-FIRST: design note (architect note, extended)

Base `8a4c438e7d9a6e2c492a1733d658d96b7b1eedcf` (origin/main; no predecessor handoff: `after` is empty).
Roster `handoff/audit-r10-roster` `b93ece169acfa8c97b469bbb18df06267aa14f6f`. Contract `dev/governance/roles/designer.md`.
Finding #2395 has no finder harness: owner report (tvofi, 2026-10-17 and 2026-10-22). O9 (the harnesses README) resolves to no file in
the tree: `72826387f^:tools/audit/harnesses/README.md` was deleted by 72826387f, and `dev/audit/harnesses/` has no index.

## Revision 2

This revision answers design review `revise 16954f0c8 architecture-unsound` (ref `handoff-body/design-verdict-r10-arch-docs-first`). Main is `0b162da1a`; #2600 landed this group's roster entry there. The base above is unchanged, because the note is prose and a rebase would add nothing.

| verdict item | change |
|---|---|
| R1: predicate (c) refuses on a roster sync | (c) is now report-only: it prints `note:` lines and returns no finding (§6). "No target marker names a done group" moves to R10-ARCH-DOCS's end-of-round predicate (§3, item R1). |
| R2: (a) fails once a `retired-by` path is deleted | (a) exempts `retired-by` paths as well as `target` paths. The state-tolerance invariant now sits beside the grammar (§3), and §6 states each predicate against it. |
| R3: work order contradicts R10-FLOW-DESIGN-POLICY | The work order is now audit → [design → design review, L/XL] → fix → fix review → train → merge → record → stamp (§1). §4's handoff path adds the design-verdict read-back for L/XL. I1 is replaced by the C7 mapping. |
| C1 | `mermaid.parse` runs locally before handoff, and the result goes in the PR body (§6, item T1a). |
| C2 | Red fixtures added for the unknown-diagram-type arm of (d) and the `%%{init` arm of (e). The fixtures' roster is an inline stub (§6, item T2). |
| C3 | "Declared" is defined, and the planted typo'd node case is specified (§6 (d), item T3). |
| C4 | D2 is rerouted to R10-PLAN-ARTIFACT, the owner by §2.3. R10-ORCH-MACHINERY keeps the confirmation of the builder (Notes, item D2). |
| C5 | D5 is corrected: R10-REPLAY-LANE edits `tests/replay.py` and `.github/workflows/nightly.yml`. It is a `decision: orchestrator`, carried to R10-FLOW-BOARD and R10-REPLAY-SCOPED (Notes, item D5). |
| C6 | §5 states the actual closure growth: the roster, `dev/README.md` and the workflows read. (b) accepts only groups in main's roster (item B1). |
| C7 | §4 lists the ORCHESTRATOR-PROMPT rules that are shape: each is a marker or node, and the prose cites the rule (item O2). |
| C8 | Sibling sites lists the two extra mermaid hits, and (e) is scoped (item S1). |
| C9 | §4 states that `dev/README.md` figures get GitHub's themes only; R10-ARCH-DOCS confirms both renderers (item V2). |
| C10 | Hot files lists the extra files the fixer's PR body names (item F2). |
| C11 | I1 is replaced by C7 (Notes, item I1). |

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
| `dev/README.md` (new) | The developer onboarding, holding everything the owner asked to sit "beside the CI shape". **Layout of `dev/`**, **governing documents**, **the work in order** (audit → [design → design review, L/XL] → fix → fix review → train → merge → record → stamp, per R10-FLOW-DESIGN-POLICY in `dev/governance/roles/orchestrator.md` and `designer.md`/`design-review.md`, and ORCHESTRATOR-PROMPT line 51, R16–R19; the seed's order put design after fix and is superseded), **requirements before a push**: all from seed 0edd7fa66, with literal counts removed ("ADRs 0001-0013", "D0..D15"). **CI shape**: the job graph, plus the seed's `0edd7fa66:dev/CI-GATE.md` folded in as the refusal order (selection → ratchet → claims → required check → train). **Orchestration machinery**: components (carry (a)). **One handoff's path**: carry (b), with each ledger kind it opens or closes. **Who decides**: carry (c). **Harnesses**: a generated-by-command index of `dev/audit/harnesses/` (the O9 fold); a re-created README would be a second index. |
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
- **State tolerance (invariant).** Every predicate a gate runs over a marked document holds both before and after each named group lands, and at every roster state between. A marker is legal while its group is not started, in progress or done. A `target` path may be absent or present, and so may a `retired-by` path. Nothing in this group's checker may turn red because another group merged or a roster sync marked a group done. Resolution is a single act, R10-ARCH-DOCS's end-of-round predicate, and it is the only check that reads a marker against a group's `done` state.
- **Marked text states no numeral.** `tests/doc_claims.py` and `tests/entities.py` read numerals against the tree, so a planned count would go red today.

Examples:
- Prose: `- the supervised beat (beatd), one job table for every detached job [target: R10-ORCH-MACHINERY]`.
- Mermaid: `R[("ruleset requires only gate<br/>[target: R10-CI-LAYOUT-P2; owner step]")]` and `T -.->|"[target: R10-CI-LAYOUT-P2]"| G`.

The regex `\[(target|retired-by): (R10-[A-Z0-9-]+(, R10-[A-Z0-9-]+)*)(; owner step)?\]` finds every marker in prose and mermaid alike. Resolution is not this group's check; by the invariant above it runs once, at R10-ARCH-DOCS's end of round ("No unresolved target marker may survive on main"):
- `target`: the group is `done` and the element is present, so the marker becomes plain text;
- `retired-by`: the group is `done` and the element is absent, so the line is deleted;
- a marker naming a done group that survives on main goes red there, and only there.

Carry: R10-ARCH-DOCS (item R1). Own the end-of-round predicate "no target or retired-by marker names a done group". It moves from this group's (c), which is now report-only.

## 4. Diagrams, format, visual language

The diagrams:
- **Architecture** (`docs/architecture.md`): a flowchart, with dashed edges for planned flow.
- **CI job graph** (`dev/README.md`): P2's umbrella, `.github/workflows/ci.yml` → prelude → units → pr-contract → `gate` → ruleset. The units already on main are drawn from `.github/workflows/`.
- **Refusal order** (`dev/README.md`): from the seed.
- **Orchestration machinery components** (`dev/README.md`): beat jobs, ledger and kinds, bus refs, the relay's arms, train and pitch, dispatch records, heartbeat and watcher, hold list, roster branch, plan page, flow toolkit.
- **One handoff's path** (`dev/README.md`): a `sequenceDiagram`, with a note per step naming the ledger kind opened or closed. For an L or XL group it opens with designer → design review, and the `Design review: approve <sha>` read-back is the step that dispatches the fixer. Then fix → fix review → train → merge → record → stamp, the same order as §1.

Shape from ORCHESTRATOR-PROMPT (`origin/claude/dazzling-gauss-7l3u2b:dev/programme/flow-study/ORCHESTRATOR-PROMPT.md`). Each is a node or a marker in the machinery figures, and the prose cites the rule rather than restating it:
- the P2 ruleset cut-over, drawn as an owner/admin rhombus with a read-back and a rollback edge, `[target: R10-CI-LAYOUT-P2; owner step]`;
- "moved means the head SHA": the reviewable head is a SHA node, and a head moved under review is drawn as the blocked-verdict edge;
- the pitch gap rule on the train, as a label on the train → merge edge;
- 0 open PRs and no owed handoff, as the end-state node at programme end.

Carry: R10-ARCH-DOCS-FIRST (item O2)

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
- `dev/README.md` is not a site page, so the token map below never reaches its figures; they get GitHub's themes only. The shape encoding keeps them correct without it. Carry: R10-ARCH-DOCS (item V2): confirm light and dark on both renderers.
- The one tree read is a token map: `tools/site/build_docs.mjs` parses `docs/site/docs.css`'s `:root` block and its dark block (`--surface-2`, `--accent`, `--ink`, `--ink-2`, `--line`, `--f-body`) into mermaid `themeVariables` per theme. That is a small edit to a file outside this group's `files` (decision: orchestrator). Without it, the site keeps mermaid's neutral and dark themes, and the docs are still correct. Carry: R10-ARCH-DOCS (item V1)

## 5. Budgets (measured at base)

- `node tools/policy/policy_lint.mjs --budgets`: no file this group writes matches `POLICY_GLOBS`. It already matches `dev/audit/README.md` and `CLAUDE.md`, and this group edits neither. Always-loaded and corpus stay flat. **No CLAUDE.md row is added**: `--budgets` already reports always-loaded above its cap and inside its band, so a row there is the one place this group could cost a raise. **No budget raise.**
- `tests/structure_budgets.json`: every metric is a code metric, so the docs touch none of them. The doc_claims function is test code and outside the measured package.
- `tests/closures.json`: `tests/doc_claims.py`'s closure grows by `dev/README.md`, by `dev/programme/rosters/wave-r10-groups.json` (read by (b) and (c)), and by each `.github/workflows/*.yml` whose job ids (a) or the CI figure reads. The fixer states the measured growth in the PR body. (b) accepts only groups present in **main's** roster, which lags the roster ref. A group the roster ref has and main lacks must not be named until a roster sync lands that group on main. Carry: R10-ARCH-DOCS-FIRST (item B1). Re-record it with `tests/derive_closures.sh --single tests/doc_claims.py` on Linux, or let the UNDER-SCOPED autofix in `dev/governance/rules/ci-autofix.md` do it; never hand-edit the recording.

## 6. Test and control plan (the fixer's)

One new findings function (doc wiring: paths, tree, roster), in `tests/doc_claims.py`, run over `docs/architecture.md`, `README.md` and `dev/README.md`. It checks:
- (a) every backticked repo path resolves in `git ls-files`, or carries a `target` **or `retired-by`** marker. Either state of a marked path passes, by the invariant in §3;
- (b) every marker is well formed and names a group in main's roster (B1). It reads a key and never a state, so it holds at every stage of the named group;
- (c) **report-only**: a marker naming a done group prints a `note:` line and is never a finding. The function returns nothing for it, at any state. Refusing is R10-ARCH-DOCS's (R1);
- (d) every block opens with a known diagram type (`flowchart`, `graph`, `sequenceDiagram`). In a flowchart a node id is **declared** when it appears with a shape (`id[...]`, `id(...)`, `id{...}`, `id([...])`, `id[(...)]`) at least once in the block. A bare id that appears exactly once, and never with a shape, is a finding: that catches a typo'd endpoint. Ids used bare two or more times pass, since mermaid declares them implicitly. `sequenceDiagram` arms check only `participant`/`actor` declarations against message endpoints. The real-tree arm must pass on `docs/architecture.md`'s existing block; if it cannot, the fixer drops this arm in favour of T1a and says so in the body. Carry: R10-ARCH-DOCS-FIRST (item T3);
- (e) no hex colour or `%%{init` appears in a mermaid block, scoped to the files listed in Sibling sites.

Each of (a), (b), (d) and (e) holds before and after any named group lands: none reads a group's state, and (a) accepts either presence of a marked path.

Fixtures and controls:
- **Red fixture**: inline strings, in the style of the existing `mermaid_pin_findings` controls. A renamed path, `[target: R10-NOPE]`, a bare node id used once (`A --> Bx` where `B[...]` is declared), a block opening `pie` (unknown diagram type), a hex fill, and a `%%{init: ...}%%` line. Each yields its finding. The roster these fixtures read is an **inline stub** passed to the function, never the live file: R10-CI-LAYOUT-P1 is `done` on the roster ref and `not-started` on main. Carry: R10-ARCH-DOCS-FIRST (item T2)
- **State-tolerance control**: a marker naming a stub-`done` group, and a `retired-by` path absent from the stub tree, yield **no** finding, only a `note:` line. This pins R1 and R2.
- **Null control**: the same strings, corrected, yield none.
- **Real-tree arm**: the check runs on the committed docs and passes.
- **Mutation proof**: target the path-resolution predicate, the marker exemption in (a), and the declared-node rule in (d). A mutant that makes (c) refuse must be killed by the state-tolerance control.
- **Local `mermaid.parse`** before the handoff: run `npm ci` in `tools/site` (the pinned mermaid) and parse every block in `docs/architecture.md`, `dev/README.md` and `README.md`. Record the command and its result in the PR body. Wiring it into a gate stays T1. Carry: R10-ARCH-DOCS-FIRST (item T1a)

A real `mermaid.parse` belongs to R10-ARCH-DOCS's wiring test, wherever mermaid is installed. Carry: R10-ARCH-DOCS (item T1)

## Alternatives

- **Generated SVG pairs with `<picture>`**: lost, because mermaid exists only in the Pages job (see 4) and a figure would need its own parity check.
- **Onboarding in `README.md`**: lost, because the docs build renders README as the product page and `tests/doc_claims.py` grades it as a user doc.
- **Two files, the seed's `dev/README.md` plus `0edd7fa66:dev/CI-GATE.md`**: lost, because the owner asked for the machinery beside the CI shape, and a second file is a second classification and a second wiring target.
- **Planned modules written inside the module map**: lost, because `tests/entities.py` refuses a name not on disk.

## Sibling sites

`git grep -n '```mermaid' -- '*.md'` lists the blocks: `README.md`, `docs/architecture.md`, `docs/how-it-works.md`, `docs/configuration.md`, `docs/setup.md`, `dev/archive/handoff/round9/plan-table-live.md` and `dev/programme/round9/state/PLAN-TABLE.md`. Check (e) covers the first five plus `dev/README.md`. The two `dev/` state files are clean of hex and `%%{init` today, and they stay outside (e)'s scope because they are records rather than reader docs. Carry: R10-ARCH-DOCS (item S1): widen (e) tree-wide if it chooses. Checks (a) to (d) run only on this group's three files; R10-ARCH-DOCS may widen them.

## Hot files and serial position

- Wave 1. `docs/architecture.md` is touched by no other non-done group.
- `README.md` is shared with R10-ARCH-DOCS only.
- `tests/doc_claims.py`, `tests/layout.json` and `tests/closure.py` are shared with R10-MERGE-SUBJECT-HARDEN (`tests/closure.py`). That collision is a merge-order one, not a seam one.
- Beyond the roster's `files` (`docs/architecture.md`, `README.md`, plus `tools/site/build_docs.mjs` per O-1), the fixer writes `dev/README.md`, `tests/doc_claims.py`, `tests/layout.json`, `tests/closure.py`, `tests/closures.json` and `tools/site/build_docs.mjs`. By the orchestrator's decision, the fixer lists these in the PR body for train hot-file accounting, and the roster is not edited. Carry: dismissed: orchestrator owns roster files (item F2)

## Notes for the fixer

- Carry: R10-ARCH-DOCS (item D1). The FIRST carry says the machinery is drawn "as built at this stage's merge base". The newer brief (owner, 2026-10-22) says the final shape. Draw the final shape with markers; ARCH-DOCS checks it against the R10-ORCH-MACHINERY tables at its own merge base.
- Carry: R10-PLAN-ARTIFACT (item D2). Four groups each claim the plan page or model. R10-PLAN-ARTIFACT extends `tools/audit/seat/plan_table.py --html`, ORCH-MACHINERY part (3) builds a shared model builder, R10-FLOW-TOOLKIT-MODEL extends that model, and R10-FLOW-BOARD writes to `tools/audit/seat/state_docs.py`. Meanwhile `tools/audit/seat/plan_page.py` is already on main. Draw one page, `tools/audit/seat/plan_page.py`, and one plan model. By §2.3 the plan model's owner is R10-PLAN-ARTIFACT, whose `files` hold `tools/audit/seat/plan_table.py` and `tools/plan/replan.py`; R10-FLOW-BOARD's carry already says "one plan model". Mark the model `[target: R10-PLAN-ARTIFACT]`. R10-PLAN-ARTIFACT confirms it, and R10-ORCH-MACHINERY confirms that its part (3) builder extends that model and is not a second one.
- Carry: R10-ROUND-PLAYBOOK (item D3). Its path-resolving control is this function. Extend that function to `dev/audit/README.md`; do not build a second checker.
- Carry: R10-CI-LAYOUT-P2 (item D4). Today the docs name `main-protect-checks` and its contexts; P2 replaces the required contexts with the single `gate` as an owner step. Draw the ruleset node `[target: R10-CI-LAYOUT-P2; owner step]` and `.github/workflows/pr-contract-rerun.yml` `[retired-by: R10-CI-LAYOUT-P2]`.
- decision: orchestrator. Carry: R10-FLOW-BOARD (item D5); the same notice goes to R10-REPLAY-SCOPED. R10-REPLAY-SCOPED edits `.github/workflows/tests.yml`, and R10-FLOW-BOARD edits `.github/workflows/governance.yml`. Neither has an `after` edge to R10-CI-LAYOUT-P2, which makes both files `workflow_call`-only units. R10-REPLAY-LANE edits `tests/replay.py` and `.github/workflows/nightly.yml`, so it does not collide. The doc draws the two units' jobs as `tests / <job>` and `governance / <job>` either way; the merge order is the orchestrator's.
- Carry: dismissed: superseded by O-2 decision (item I1). ORCHESTRATOR-PROMPT is `origin/claude/dazzling-gauss-7l3u2b:dev/programme/flow-study/ORCHESTRATOR-PROMPT.md` (30c57744a), and the rules in it that are shape are mapped in §4 (item O2).
- Carry: R10-ARCH-DOCS (item F1). Fold P40 there: the committed `docs/img/card/*.png` figures are compared to the card. This group commits no figure.
