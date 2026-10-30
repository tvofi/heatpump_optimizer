# Design note: R10-AUDIT-COVERAGE-ENDGAME (pre-study r10-audit-coverage)

Base: `437f1ba9b521199b360d84effe6a621573d34663` (origin/main at dispatch; no predecessor handoff head). Roster read at `origin/handoff/audit-r10-roster`. v10.0.0 = this base plus every roster group whose `resume.stage` is not `done` (55 such groups besides R10-CATALOG-PR and R10-CLOSEOUT-CLEANUP; count: `[g for g in roster['groups'] if g['resume'].get('stage')!='done']` over the roster JSON). Seat: designer, read-only; no production code.

## 1. Finding and evidence (summary matrix)

Coverage means a dimension brief that would read the path **and** a finder scope that hands it to a seat. COMMON.md (finder contract) says a finder measures only its named cells, and anything else is a lead, so a path in no scope universe is never measured, whatever a brief says. Enumerator: Appendix A (`cov.py <ref>`), using `tools/audit/check_scopes.py`'s own glob semantics, over `git ls-tree -r <ref>`.

| body | tracked paths | in ≥1 universe | brief names it | verdict |
|---|---|---|---|---|
| (a) production `custom_components/heatpump_optimizer/**` | 102 | 102 | yes (D0–D12, D15) | covered |
| (a) `blueprints/**` | 4 | 0 | no brief | **uncovered (G2)** |
| (b) instruments `tools/**` | 487 | 487 (486 via D11 only) | D11 names `tools/policy/policy_lint.mjs`, `tools/policy/brief_lint.mjs`, `tools/release/stamp.py`, `tools/pr/prepr.sh`; nothing under `tools/audit/seat/`, `tools/plan/`, nor the merge train | **partial (G3)** |
| (c) `.github/**`, `.claude/**`, `.cursor/**` | 60 | 60 (D11 only) | workflows only as "the workflow job"; hooks only via `.claude/settings.json`; CODEOWNERS not named (ruleset is) | **partial (G3)** |
| (c) `tests/**` scripts and gate machinery | 3069 (58 scripts; 2895 under `tests/mutation_ledger/`) | **0** | D3 names `tests/closure.py`, `tests/closures.json`, `tests/env_drift.py`; D11 names `tests/structure.py` | **uncovered by scope (G1)** |

Sampling (the "would actually read" test): D11's universe is 3133 files, of which 2147 are evidence records under `dev/audit/rounds/` (`git ls-files dev/audit/rounds | wc -l`). All three D11 seats own `**`, split only by step. So a D11 seat gets the instruments in a list that is about 69% records (G3). D4 does not name the card file literally, but "the card in a real browser" reads it, so the card counts as covered. In-flight paths that do not exist at base land in these cells: the two new `tools/` instruments (R10-POLICY-ROLE-PACK, R10-FLY-GH-CALL-LOG) fall into D11's glob, so they are partial like G3. R10-README-GRAPHICS adds a renderer script and figures under `docs/img/readme/`, which is in no universe (G1-class, see section 4).

Bug classes: `python3 tools/audit/fold_ledger.py check --ledger dev/audit/config/bugclasses.json` exits 0 with 0 violations (47 classes). Eleven classes carry neither a barrier nor an RCA (for example N-approval-rebuy, N-registry-leak, N-restore-race). Each has one instance and met no trigger, so none is owed (`fold_ledger.py` OWED rule), and none is a gap. A real gap: classes P1, P5 and P9 name barrier paths that are absent from the tree (a round-9 sweep under the old `tools/audit/` round-9 path, and two retired `.claude/workflows/` carry files). The check never resolves a barrier path (**G5**).

Harnesses: 484 scripts (192 under `dev/audit/harnesses/`, 292 under `dev/audit/rounds/round9/`). A static path scan finds that 283 reference at least one path missing at base, 333 refs in all. Most are self-references to the pre-move round-9 location. Some are hard stale reads: `dev/audit/harnesses/follower_debounce.py` fails with FileNotFoundError on a retired workflow, `dev/audit/harnesses/dual_path.py` fails in a `git mv` of a rule already moved under `dev/governance/rules/`, and `dev/audit/harnesses/boost_replay_fork_parity.py` fails on a missing module. A 1-in-12 sample re-run at base (41 harnesses, Appendix C): 17 green, 6 exit on missing argv, 2 on a stale path or module, 5 time out at 60 s, 11 exit non-zero for other reasons. Harnesses carry no machine-readable run line, so whether they "re-run green at main" cannot be measured in bulk: a missing argv (IndexError) looks the same as a real break (**G6**). 38 of 84 production modules are referenced by no harness (**G7**).

**Null control.** The enumerator reports `custom_components/heatpump_optimizer/optimizer.py` covered (D0,D1,D2,D3,D5,D7,D9,D10,D12) and `tools/site/build_docs.mjs` covered (D6,D11). It reports `tests/closure.py` and `blueprints/automation/notifications.yaml` uncovered. Running `check_scopes.py --repo . --ref HEAD` gives every dimension `ok`, so the existing checker cannot see G1/G2. That is the checker's own blind spot (G4). brief_lint negative control: appending a nonexistent path to the entry turns brief_lint red (1 error, rc=1).

## 2. Owning seam and shape

Owner: `tools/audit/check_scopes.py` with its data `dev/audit/config/scopes.json`. Its one caller is `.claude/workflows/audit-find.js` (Prepare step, which refuses the round on rc≠0). Second, independent owner: `tools/audit/fold_ledger.py` (G5). These two do not share a concern, so the group does not need two owners for one change.

Shape:
- (G4) `check_scopes.py` gains a coverage mode. It takes the tracked tree at `--ref`, subtracts the union of every dimension's universe, then subtracts a reasoned exclusion map in `scopes.json` (path glob → reason, for example binaries, recorded data, licences). It refuses every remaining path. `--self-test` gains a perturbation that drops one universe and must be refused. Invariant kept: per-dimension disjoint/complete is unchanged, and the `--seat` output is unchanged for every seat whose blocks the group does not edit.
- (G1) D3 universe += the suite scripts under `tests/`. D11 universe += the gate machinery (closure, entities, structure, env_drift, gate_lock, budget JSONs, `tests/hastub`). Both exclude recorded data (`tests/mutation_ledger/`, `tests/golden/`), and the exclusion map names the reason.
- (G2) `blueprints/**` goes into D4's and D6's universes. D4.md names blueprints as a surface.
- (G3) `dev/audit/rounds/**` comes out of D11's universe and into the exclusion map. D11.md names `tools/audit/seat/`, `tools/pr/`, `tools/plan/`, the merge train (`tools/audit/seat/merge_train.py`), `.github/workflows/`, `.claude/hooks/` and `.github/CODEOWNERS` as code a seat reads. The seats keep their step split.
- (G5) `fold_ledger.py check` resolves each path-shaped barrier token at the head and refuses a missing one. P1, P5 and P9 are repointed.
- (G6) Stale harnesses still cited by an open finding or a bug-class detector are repaired with `tools/audit/seat/moved_paths.py`. The rest are listed as retired in `dev/audit/README.md`.

| fix | kind |
|---|---|
| G1, G2, G3 scope edits; G4 coverage mode; G5 ledger check and repoint; G6 harness repair | tree work |
| D3.md, D4.md, D11.md wording (G1–G3) | policy edit (dimension briefs; orchestrator approves under its mandate before merge) |

## 3. Alternatives (each lost on code grounds)

1. A standalone `tools/audit/` coverage script. It duplicates `expand_braces`/`glob_re`/`match`, so two glob dialects could drift. It also adds a tracked file that `tests/closure.py` must classify.
2. A coverage assertion in `tests/entities.py`. Several open groups touch that hot file, and the scopes are consumed in audit-find's Prepare step, not in CI. A red there would block unrelated code PRs over audit configuration.
3. Putting `tests/**` wholesale into D11. That hands 2895 mutation-ledger records to a finder, which is the same dilution as G3.

## 4. Sibling sites (by command)

`python3 cov.py <base> --table | awk '$3=="-"'` lists every uncovered path. At base, outside `tests/`, `blueprints/` and binaries, it gives `docs/design/**` (6 md) and the root files (LICENSE, NOTICE, SECURITY.md, VERSION, RELEASE_NOTES.md, .gitignore, .gitattributes). Each goes into the exclusion map with a reason, or into D5/D6. The fixer decides per path and records the reason. In-flight siblings are the R10-README-GRAPHICS renderer and figures under `docs/img/readme/` (D6 universe or exclusion) and the two new `tools/` instruments (D11 by glob, and named by G3's brief edit). The fixer re-runs the command at its merge base, because later merges add paths.

## 5. Evidence plan, by file

- Failing test first: `tools/audit/check_scopes.py --self-test` adds an arm. Coverage mode run against the base-shaped `scopes.json` must refuse `tests/closure.py` and `blueprints/automation/notifications.yaml`. It is red before the fix and green after the scope edit. Null control: `custom_components/heatpump_optimizer/optimizer.py` stays covered in both runs. Perturbation: drop D10's universe, and the arm must refuse.
- Mutation proof targets: the line computing tree minus the union of universes, and the exclusion-map subtraction in `check_scopes.py`. In `fold_ledger.py`, the barrier-path existence test (its self-test gains an arm: a barrier citing a missing path is refused, and one citing a present path passes).
- Finder's harness at both ends: Appendix A's enumerator (pre-fix, it shows tests/blueprints uncovered; post-fix, none unclassified). Goldens: none move, so no claim file is touched.

## 6. Too large for one group (split out, recommendation)

- **Harness census (G6 in full)**: 283/484 harnesses with stale refs and no run line. Recommendation: a round-11 instrument group that gives every harness a one-line, machine-readable invocation and a CI-free census runner that classifies each harness as green, stale or args-missing. The endgame repairs only harnesses that are still cited.
- **Production seams with no harness (G7)**: 38 modules. Harnesses are per finding (COMMON.md), so this is a D3 seed for round 11 and not a fix group.

## Roster entry

The R10-AUDIT-COVERAGE-ENDGAME object, appended to `groups`: brief_lint at base on the roster plus this entry gives `TOTAL: 0 error(s)` (2 warnings, both in other groups), rc=0. `after` lists every group not `done` except R10-CATALOG-PR and R10-CLOSEOUT-CLEANUP (55).

```json
{
 "group": "R10-AUDIT-COVERAGE-ENDGAME",
 "lane": "IN",
 "kind": "instrument",
 "class": "instrument",
 "severity": "medium",
 "size": "L",
 "issues": [],
 "fixes": [],
 "findings": [],
 "wave": 1,
 "files": [
  "dev/audit/config/scopes.json",
  "tools/audit/check_scopes.py",
  "tools/audit/fold_ledger.py",
  "dev/audit/config/bugclasses.json",
  "dev/governance/dimensions/D3.md",
  "dev/governance/dimensions/D4.md",
  "dev/governance/dimensions/D11.md",
  ".claude/workflows/audit-find.js",
  "dev/audit/harnesses/",
  "dev/audit/rounds/round9/",
  "dev/audit/README.md"
 ],
 "hot_files": [
  "dev/audit/config/scopes.json",
  "dev/audit/README.md"
 ],
 "fixture": false,
 "owner_gate": null,
 "rca": [],
 "architect_note": "",
 "effort": "medium",
 "model": {
  "fixer": "opus",
  "reviewer": "opus",
  "rca": null,
  "runner": "haiku",
  "record": "sonnet"
 },
 "fixerModel": "opus",
 "reviewerModel": "opus",
 "after": [
  "R10-COP-GATE",
  "R10-UX-HEALTH",
  "R10-PREPR-CAP",
  "R10-ARCH-DOCS",
  "R10-CEILING-PROBE",
  "R10-COP-PARTLOAD",
  "R10-FLOW-BOARD",
  "R10-FLOW-DESIGN-STAGES",
  "R10-FLOW-WIP",
  "R10-FLOW-BODY-ONLY",
  "R10-FLY-OPENPR-ATOMIC",
  "R10-FLY-ROW-HEAD-CARRY",
  "R10-FLY-RELAY-REVIEW-FF",
  "R10-FLY-CARRY-DOC-CONTEXT",
  "R10-FLOW-TOOLKIT-MODEL",
  "R10-ROUND-PLAYBOOK",
  "R10-FLY-STAMP-CHECK-NOTES",
  "R10-FLY-MANDATE-REVOKE-GUARD",
  "R10-TRAIN-OVERLAP-GRADE",
  "R10-NIGHTLY-HB-RESPAWN",
  "R10-ORCH-LEDGER",
  "R10-ORCH-PLANPAGE",
  "R10-ORCH-ROSTER-SCHEMA",
  "R10-FLY-DAEMONIZE-ARGV",
  "R10-FLY-SUITE-ENV-FLAKES",
  "R10-FLY-NO-FOOTERS",
  "R10-ORCH-REVIEW-PACKET",
  "R10-POLICY-ROLE-PACK",
  "R10-BRIEFS-FOLD-D0",
  "R10-REPLAY-REAL-DAY",
  "R10-ARCHSCORE-SPELLINGS",
  "R10-SAV-ACTUATION",
  "R10-FLY-LEDGER-SAMPLE",
  "R10-MERGE-SUBJECT-CASEARM",
  "R10-996-RUNNER-CLAIMS",
  "R10-ARCH-SHAPES-CLASSIFIER",
  "R10-FRICTION-REGRESSION",
  "R10-FLY-MUTANT-RESTORE",
  "R10-FLY-TRAIN-DEFAULTS",
  "R10-FLY-RELAY-TOOLS-LEVEL",
  "R10-FLY-GH-CALL-LOG",
  "R10-FLY-CIPREDICT-RESTORING",
  "R10-FLY-RECORD-RED-NAMES",
  "R10-FLY-CANCEL-SWEEP",
  "R10-FLY-TICK-APPROVAL-OWED",
  "R10-FLY-SEAT-ALIVE-ID",
  "R10-FLY-BUS-BASH32",
  "R10-ARCH-DOCS-WIRING",
  "R10-HOTFIX-AWAY-SETBACK",
  "R10-HOTFIX-AWAY-LIVE",
  "R10-README-GRAPHICS",
  "R10-HOTFIX-LEARNER-INPUTS",
  "R10-FACTORY-RESET",
  "R10-WOOD-NOTIFY",
  "R10-USER-DOCS-FINAL"
 ],
 "carry": [],
 "resume": {
  "stage": "not-started",
  "branch": null,
  "commit": null
 },
 "brief": "Pre-study: the design note on the design/r10-audit-coverage ref. Owner request (tvofi, 2026-10-30): the audit dimensions, finder scopes, bug classes and harnesses must cover production, instruments and repo machinery as they stand at v10.0.0. This group runs after every group that adds code and before R10-CLOSEOUT-CLEANUP's apply run, R10-CATALOG-PR and the closeout stamp. Re-measure every gap at your own merge base before fixing it: groups that land after the pre-study change the tree, so carry no count from the note; derive each with the command the note gives and print it in the body. Gaps to re-measure and close: (G1) no universe in dev/audit/config/scopes.json matches any path under tests/, although D3.md and D11.md name tests/closure.py, tests/closures.json, tests/env_drift.py and tests/structure.py as things a finder measures; add the suite scripts to D3's universe and the gate machinery (closure, entities, structure, env_drift, gate_lock, the budget files, tests/hastub) to D11's, excluding recorded data such as tests/mutation_ledger/ and tests/golden/. (G2) blueprints/ is in no universe and no brief; add it to D4's and D6's universes and name it in D4.md. (G3) D11's universe is dominated by evidence records under dev/audit/rounds/, and D11.md never names tools/audit/seat/, tools/pr/, tools/plan/, the merge train or .github/workflows/ as code to read; name them in D11.md and exclude dev/audit/rounds/ from D11's universe, each seat keeping its steps. (G4) tools/audit/check_scopes.py proves disjoint and complete within a dimension but not that the union of universes covers the tree: add a coverage mode to it that refuses any tracked path in no universe and not on an explicit, reasoned exclusion list kept in scopes.json, with a self-test perturbation that drops one universe and must be refused, and run it where .claude/workflows/audit-find.js runs the scope check. (G5) three bug-class barriers in dev/audit/config/bugclasses.json (P1, P5, P9) cite paths absent from the tree; repoint each at its live path, and make tools/audit/fold_ledger.py check refuse a path-shaped barrier token that does not resolve at the head. (G6) harnesses under dev/audit/harnesses/ and dev/audit/rounds/round9/ that read moved paths (the round-9 tree moved under dev/audit/rounds/, a workflow and a rule file that moved or were retired): repair those still cited by an open finding or a bug-class detector, using tools/audit/seat/moved_paths.py, and list the rest as retired in dev/audit/README.md; the full census is split out in the note. Dimension briefs are policy (D3.md, D4.md, D11.md): the orchestrator approves them under its mandate before the merge. Null control: the coverage mode reports custom_components/heatpump_optimizer/optimizer.py covered before and after."
}
```

## Notes for the fixer

- Carry: R10-CATALOG-PR (item E1). That group gains `after: R10-AUDIT-COVERAGE-ENDGAME` by `roster_edit.py`, so the catalog PR follows the coverage measurement.
- Carry: R10-CLOSEOUT-CLEANUP (item E2). That group gains the same edge. Its `--apply` run deletes `design/*` and `handoff/*` refs, so it must follow this group's merge. Its own new instrument then lands after this measurement. G4's coverage mode classifies it by D11's glob, and a re-run of the coverage mode at its head is enough.
- Carry: R10-ROUND-PLAYBOOK (item E3). Both groups touch `dev/audit/README.md`. The edge already orders this group after it.
- `check_scopes.py`'s LOC column reads 0 for non-package files. Do not read it as empty.

## Appendix A: enumerator (`cov.py`)

```python
#!/usr/bin/env python3
"""Coverage enumerator: tracked path x dimension universe (scopes.json), per body.
usage: cov.py <ref> [--table]"""
import json, subprocess, sys
import re
def expand_braces(p):
    m = re.search(r"\{([^{}]*)\}", p)
    if not m:
        return [p]
    return [q for alt in m.group(1).split(",") for q in expand_braces(p[:m.start()] + alt + p[m.end():])]

def glob_re(p):
    out, i = "", 0
    while i < len(p):
        if p.startswith("**", i):
            out += ".*"; i += 2
        elif p[i] == "*":
            out += "[^/]*"; i += 1
        else:
            out += re.escape(p[i]); i += 1
    return re.compile(out + r"\Z")

def match(files, globs):
    rx = [glob_re(q) for g in globs for q in expand_braces(g)]
    return {f for f in files if any(r.match(f) for r in rx)}

ref = sys.argv[1]
tree = subprocess.run(["git","ls-tree","-r","--name-only",ref],capture_output=True,text=True,check=True).stdout.split()
sc = json.loads(subprocess.run(["git","show",f"{ref}:dev/audit/config/scopes.json"],capture_output=True,text=True,check=True).stdout)
dims = [k for k in sc if not k.startswith("_")]
uni = {d: (match(tree, sc[d]["universe"]) if sc[d]["universe"] else set()) for d in dims}
def body(p):
    if p.startswith("custom_components/heatpump_optimizer/"): return "a-production"
    if p.startswith("tools/"): return "b-instruments"
    if p.startswith("blueprints/"): return "a-production"
    if p.startswith((".github/",".claude/",".cursor/","tests/")): return "c-machinery"
    if p.startswith("dev/"): return None
    return "d-docs-root"
rows = {}
for p in tree:
    b = body(p)
    if not b: continue
    ds = [d for d in dims if p in uni[d]]
    rows[p] = (b, ds)
from collections import Counter, defaultdict
c = defaultdict(Counter)
for p,(b,ds) in rows.items():
    c[b]["total"] += 1
    c[b]["no-dimension" if not ds else ("D11-only" if ds==["D11"] else "dim")] += 1
for b in sorted(c): print(b, dict(c[b]))
if "--table" in sys.argv:
    for p,(b,ds) in sorted(rows.items()): print(b, p, ",".join(ds) or "-")
```

## Appendix C: harness sample re-run at base (1 in 12, `PYTHONPATH=tests/hastub:tests:custom_components`, 60 s cap)

```
1	dev/audit/harnesses/archscore_layering_seam_census.py	IndexError: list index out of range
0	dev/audit/harnesses/draw_range_evidence.py	mild-indep  cfg=(1.0, 6.0) engaged 20/20 seeds; last seed observed=(1.113, 1.898) switch+setpoint: (1.0, 
0	dev/audit/harnesses/j5_gil.py	RESULT dhw_cap_zero_range.ticks_per_second=834.419 1/s
0	dev/audit/harnesses/r10_buffer_store.py	flat: buffer plan identical to no-buffer False
1	dev/audit/harnesses/r10_ci_layout_p1/critpath.py	IndexError: list index out of range
0	dev/audit/harnesses/r10_ci_layout_u5/script_runs.py	script_runs_per_push=54 budget=54
0	dev/audit/harnesses/r10_dead_rate_limit.py	RESULT digest=3187402b35f5e993a2e0b090b885338973619521
124	dev/audit/harnesses/r10_flow_dispatch_mutants.py	    FAIL a nonce the relay minted is re-recorded by the seat fired with it, with its model, minti
0	dev/audit/harnesses/r10_i1_sweep_guards.py	RESULT sites=17 killed=17 null=False
0	dev/audit/harnesses/r10_merge_subject_census.mjs	SPLIT 3 of 3 pr word(s) with merge on a later line of the statement uncovered, over 378 file(s)
124	dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py	M1-one-try KILLED by: hb:positive_control survives one hung py-spy sample: a fresh spin ans
1	dev/audit/harnesses/r10_review_gather_share.py	IndexError: list index out of range
124	dev/audit/harnesses/r10_setpoint_power.py	
1	dev/audit/harnesses/r10_thermal_power_option.py	AttributeError: 'Gate' object has no attribute '_fold_cop_evidence'
1	dev/audit/harnesses/r10_u9a_ratchet_nulls.py	ci-ratchet: Tests push run 39864627483 carries no jobs list; --gather-runs embeds them (fail closed)
2	dev/audit/harnesses/record_batch_measure.py	merges, so a count above zero comes from the range, not the rule.
1	dev/audit/rounds/round9/D0/s1/coord.py	IndexError: tuple index out of range
0	dev/audit/rounds/round9/D1/leads/_rig.py	
1	dev/audit/rounds/round9/D1/leads/stub_store_codec.py	ModuleNotFoundError: No module named 'orjson'
0	dev/audit/rounds/round9/D1/s2/leads/lc_flow_bias_containment.py	RESULT swapins=0
0	dev/audit/rounds/round9/D1/s3/parsers.py	RESULT swapins=0
0	dev/audit/rounds/round9/D1/s5/parsers_sweep.py	RESULT swapins=0
1	dev/audit/rounds/round9/D11/leads/l3_gov_pin.py	ValueError: substring not found
1	dev/audit/rounds/round9/D12/leads/l2_wood_currency.py	TypeError: build_wood_fuel_view() got an unexpected keyword argument 'space_kw'
124	dev/audit/rounds/round9/D12/s3/usable.py	CELL 70 {"layout": "single", "dhw": "none", "wood": "wood", "pv": "pv_meter", "buffer": "buffer", "surfac
1	dev/audit/rounds/round9/D14/s2/p8_card.mjs	Node.js v22.22.0
0	dev/audit/rounds/round9/D14/s5/doc_refs.py	RESULT swapins=n/a
0	dev/audit/rounds/round9/D2/s2/flow_bias_clamp.py	RESULT swapins=0
0	dev/audit/rounds/round9/D2/s4/newton_bias.py	RESULT swapins=0
1	dev/audit/rounds/round9/D3/s2/storeguards.py	KeyError: 'CMP_BOUND'
1	dev/audit/rounds/round9/D4/s1/layout_kbd.mjs	Node.js v22.22.0
0	dev/audit/rounds/round9/D4/s2/unit_typography.py	RESULT swapins=0
0	dev/audit/rounds/round9/D5/s1/quick_setup_promise.py	RESULT swapins=0
1	dev/audit/rounds/round9/D6/s2/card_config.mjs	Node.js v22.22.0
124	dev/audit/rounds/round9/D7/s1/train_mutations.py	  null tests/doc_claims.py: rc=1 failed=19 survived 5s 
1	dev/audit/rounds/round9/D8/s1/matrix.py	ModuleNotFoundError: No module named 'orjson'
0	dev/audit/rounds/round9/D9/leads/l3_valve_solve.py	RESULT swapins=0
1	dev/audit/rounds/round9/D9/s1/worker_rss.py	TypeError: optimize_in_process() takes 2 positional arguments but 4 were given
1	dev/audit/rounds/round9/EG-B5/ledger_check.py	IndexError: list index out of range
1	dev/audit/rounds/round9/F10/f10_6/inventory_identity.py	IndexError: list index out of range
1	dev/audit/rounds/round9/rca/1747/rca_census_reach.py	AttributeError: type object 'HeatPumpOptimizer' has no attribute '_build_dhw_requirements'
```
