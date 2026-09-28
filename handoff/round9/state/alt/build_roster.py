"""Build ALT-ROSTER.json: the live round-9 roster with merged groups truthed from origin/main,
three endgame carries folded into their stage briefs, and the EG lane appended."""
import json, subprocess, collections, sys
LIVE, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(LIVE), object_pairs_hook=collections.OrderedDict)
G = collections.OrderedDict((g["group"], g) for g in d["groups"])
P = "custom_components/heatpump_optimizer/"
EV = "handoff/round9/state/alt/evidence"
EVSHA = "a163db90"
PLAN = "handoff/audit-r9-alt: handoff/round9/state/ALT-ENDGAME-PLAN.md, handoff/round9/state/ALT-ROSTER.json, handoff/round9/state/alt/EG-B5-DESIGN.md"

# --- 1. truth resume for merged groups (merge commits on origin/main, first parent) ---
MERGED = {
 "R9-F1.1": (1722, "2d71759e"), "R9-F1.2": (1724, "12b0df68"), "R9-F1.3": (1731, "3bae92d9"),
 "R9-F2.1": (1694, "058e89f1"), "R9-F2.2": (1713, "9c6b923f"), "R9-F2.3": (1723, "2eef524d"), "R9-F2.5": (1734, "31394964"),
 "R9-F3.1": (1691, "917f16c2"), "R9-F3.2": (1707, "ba60afab"), "R9-F3.3": (1717, "49fc8bbe"),
 "R9-F4.1": (1704, "0c9c4000"), "R9-F4.2": (1718, "fab17619"),
 "R9-F5.1": (1698, "5abd5f9d"), "R9-F5.2": (1732, "8ff6827a"),
 "R9-F6.1": (1699, "7428d87a"), "R9-F6.2": (1709, "92bce7c4"),
 "R9-F7.1": (1690, "cbb8a271"),
 "R9-F8.1": (1696, "62933b18"), "R9-F8.2": (1703, "a67f4d40"), "R9-F8.3": (1733, "cdbca706"),
 "R9-F9.1": (1702, "48b696c1"), "R9-F9.2": (1714, "624db889"),
 "R9-F10.1": (1693, "1ef6a805"),
 "R9-F11.1": (1697, "b5501cca"), "R9-F11.2": (1701, "399ef171"), "R9-F11.3": (1715, "87d780c7"), "R9-F11.6": (1720, "2d012406"),
}
def full(sha):
    return subprocess.check_output(["git", "rev-parse", sha], text=True).strip()
for gid, (pr, sha) in MERGED.items():
    r = G[gid]["resume"]
    r["stage"] = "done"; r["commit"] = full(sha)
    r["last_step"] = f"merged as #{pr} (merge commit {sha} on main)"
    r["next_step"] = "none: merged"
MERGED["R9-F1.4"] = (1735, "686239d2")
r = G["R9-F1.4"]["resume"]
r["stage"] = "done"; r["commit"] = full("686239d2")
r["last_step"] = "merged as #1735 (merge commit 686239d2 on main)"; r["next_step"] = "none: merged"

# --- 2. carries folded into the stage briefs (finding-propagation.md) ---
CARRY = {
 "R9-F10.4": (1738,
  f" Carry (endgame review, #1738, verified before filing): the ratchet misprices decomposition three ways, each measured with its control at {EVSHA} ({EV}). "
  "(a) duplication_blocks compares functions within one module only: a copy placed in another module moves nothing, the same copy in its own module moves it (m5_dup_control.sh). "
  f"(b) private coordinator members read from another module move no metric, while the same reads inside a coordinator method move cut_dhw (m3_ratchet_control.sh); the reach spans {P}pump_arbiter.py, {P}boost.py, {P}away.py, {P}wood_fuel.py and the surfaces, beyond the coordinator.py and wood_fuel.py sweep behind D7-s1-01 (m3_reach.py). "
  "(c) classes_over_300 scores the extraction of a sound class from the coordinator as the one regression (#750, W5-G9). "
  "Price (a) and (b) in tests/structure.py beside D7-s1-01; for (c) propose a definition under which an extraction that shrinks the god class is not a regression (for example lines above the threshold summed over classes) and ask tvofi before the push, because it changes a budget key. "
  "Demonstrate each arm failing on its probe at the base and passing on the fixed instrument. All three land before any R9-EG move (R9-EG-B5, R9-EG-B7)."),
 "R9-F10.3": (1748,
  " Carry (endgame review, #1748, verified before filing): the per-site ratchet this PR lands identifies a site by file, kind and stripped text (added_unpinned in tests/mutation_table.py at 8eda51a2), and its base enumerates only files that exist at the base, so a site moved unchanged into another module counts as newly added and unpinned; the docstring's promise that a moved site is the base's holds within one file only. "
  "Measured by a skeptic seat on the DHW planner move (#1743) with its ledger correctly re-keyed: the prototype reports the whole moved cluster as added (every unpinned site in the new module plus one helper's). "
  "Count a site as moved, not added, when its kind and stripped text leave one file and reappear unchanged in another in the same diff; restrict the match to files the diff removes lines from and adds lines to, and to the same trailing scope name, so a generic line such as a bare return cannot launder a new guard. "
  "Demonstrate it on the #1743 move simulation (refused at the base, passing on the fixed ratchet) and on a genuinely new unpinned guard inside a moved file (still refused). R9-EG-B5 does not start until this lands."),
 "R9-F1.10": (1741,
  f" Carry (endgame review, #1741, verified before filing): unify the two step-start clocks, coordinator._utc_step_starts and optimizer._utc_step_starts, into one function taking a timedelta step and an offset ({P}silent_mode.py, tests/dst_checks.py and tests/features.py import them; the coordinator bridge is _horizon_step_starts); and give the tank-room ambient, held as a literal in {P}thermal_model.py (_simulate_step_two_zone and simulate_trajectory_batch), {P}sysid.py and {P}optimizer.py, one name. "
  f"Measured at {EVSHA} ({EV}/m6a_step_starts.py): the clocks agree on every reachable grid because dt_hours is time_step_minutes over 60; a step that is not a whole number of minutes disagrees (the control), so the agreement is held by the config surface, not by one definition. "
  "Pure: goldens byte-identical; extend the agreement pin in tests/dst_checks.py to the autumn transition."),
 "R9-F10.1b": (1740,
  f" Carry (endgame review, #1740, verified before filing): this PR closes P11 (#1649), and Store version semantics are a P11 instance the barrier landed in R9-F10.1 does not cover. The stub Store in tests/hastub/homeassistant/helpers/storage.py accepts version and discards it, where Home Assistant re-raises NotImplementedError on a major-version mismatch with no migration override (a copy of its storage helper is {EV}/ha_storage_dev.py.txt at {EVSHA}). "
  f"Measured with {EV}/m4_store_version.py: saved at one version and loaded at the next, the stub returns the data; at equal versions both return it (the control). "
  "Make the stub honour version the way Home Assistant does, so a bump without a migration fails in the gate; R9-EG-B4 then lands the production seam."),
}
for gid, (issue, text) in CARRY.items():
    g = G[gid]
    g["brief"] = g["brief"].rstrip() + text
    if issue not in g["issues"]:
        g["issues"] = sorted(g["issues"] + [issue])

# --- 3. the EG lane ---
def resume(slug, pid, seat=False):
    b = f"handoff/r9-eg-{slug}"
    return collections.OrderedDict([
        ("stage", "not-started"), ("branch", b), ("commit", None), ("last_step", None),
        ("next_step", "root-cause.md section 1 at a fresh merge base" if seat else "fixer.md step 1 at a fresh merge base: re-measure the issue's enumerator, then write the failing check"),
        ("note_file", f"handoff/round9/fix/resume/{pid}.md on {b}"),
        ("review_branch", None if seat else b + "-review"),
        ("review_note_file", None if seat else f"handoff/round9/fix/resume/{pid}-review.md on {b}-review"),
        ("plan", PLAN),
        ("log", "handoff/audit-r9-plan:handoff/round9/RESUME.md (append-only mirror)"),
        ("note", "Added by the round-9 endgame review (2026-09-28). The seat's resume note on its branch outranks this entry for in-flight state; the record seat updates stage, commit, last_step and next_step at each hand-off and merge."),
    ])
def group(pid, slug, issues, fixes, after, why, gate, brief, seat=False, effort="high"):
    g = collections.OrderedDict()
    g["group"] = f"R9-{pid}"; g["lane"] = "EG"; g["issues"] = issues; g["fixes"] = fixes
    g["findings"] = []; g["covers"] = []; g["cap_exception"] = None; g["sweep_instances"] = []
    g["class"] = "architecture"; g["wave"] = None
    g["fixerModel"] = "opus"; g["reviewerModel"] = "opus"
    g["model"] = collections.OrderedDict([("fixer", "opus"), ("fixer_why", why), ("reviewer", None if seat else "opus"),
                                          ("rca", "opus" if seat else None), ("runner", "haiku"), ("record", "sonnet")])
    g["effort"] = effort; g["fixture"] = False; g["owner_gate"] = gate; g["rca"] = seat
    g["barrier"] = []; g["barrier_prototype"] = []; g["blocked_on"] = None
    g["after"] = after; g["resume"] = resume(slug, pid, seat); g["brief"] = brief
    return g
HDR = lambda pid, what: (f"Round-9 endgame {'seat' if pid == 'EG-B0' else 'PR'} {pid} (lane EG, architecture: {what}). "
                         "Added by the endgame review (the ALT endgame plan on the handoff/audit-r9-alt branch); the lane owns no file until its after-edges merge, then borrows what its scope names. ")
EG = [
 group("EG-B0", "solve-inputs-rca", [1736], [], [], "root-cause seat for a five-instance recurring class", None,
  HDR("EG-B0", "root cause of the solve-scoped hub writes") +
  "Not a pull request: a root-cause seat under tools/audit/briefs/root-cause.md, beside R9-EG-B1 and never inside it. "
  f"Issue #1736: each solve writes its inputs into the live hub objects the coordinator shares ({P}coordinator.py async_run_optimization and _prepare_dhw_inputs; only the setback fields are unwound by away.restore_setback), and four closed issues fixed one reader each (#240, #1517, #1529, #1683). "
  "Owed: the named cause; the process state (a-d) with its evidence, testing (c) against (b) explicitly because each per-site fix was correct; the cost test in wall-clock per occurrence over a release cycle; and the countermeasure, which tvofi has scheduled as R9-EG-B1. "
  "Also measure the two measure-first leads in #1736 with their null controls: async_simulate against the live solve on identical inputs, with and without a setback active (control: setback inactive, identical plans); and the published comfort floor against the one the plan was solved with while a setback is active. "
  "Report each as established or refuted; an established parity gap goes to tvofi as a product decision, never into R9-EG-B1. "
  f"Enumerator: {EV}/m1_hub_writes.py at {EVSHA}. Write the Root cause section on #1736 and read it back byte-for-byte.", seat=True),
 group("EG-B2", "surface-identity", [1739, 1742], [1742], ["R9-F1.11"], "registry-compatibility-sensitive identity pinning across every platform", None,
  HDR("EG-B2", "surface identity and public accessors") +
  f"Issues #1742 (Fixes) and #1739 (Part of: the surface half). Scope: {P}entity.py, {P}sensor.py, {P}binary_sensor.py, {P}button.py, {P}switch.py, {P}climate.py, {P}datetime.py, {P}diagnostics.py. "
  "(1) Pin unique_id, translation key and entity_id once in the entity.py base beside ConfiguredInputMixin and DHWEntityMixin; entity.py keeps importing nothing from the package, so the core never imports the surface layer. "
  "(2) climate.py and binary_sensor.py read coordinator.effective_config instead of their own merged copy of the entry's data and options. "
  "(3) Surface reads of coordinator private members move to the existing public accessors (effective_config, mode, optimization_running), or to a new read-only property where none exists; entity.py's two getattr reaches are in scope. "
  "(4) The payload accessor moves onto the base. "
  "Null control, in the body: a before/after snapshot of every (platform, unique_id, entity_id, translation_key) with en and sv loaded, byte-identical; tests/entities.py passes unchanged. "
  "Out of scope: config_flow.py and services.py (the doc_claims arms read them). After R9-F1.11, the last round-9 PR that borrows sensor.py and the F1-owned button.py."),
 group("EG-B3", "typed-payload", [1737], [1737], ["R9-F10.4", "R9-EG-B2"], "a typed contract over the coordinator's whole published payload", None,
  HDR("EG-B3", "typed payload contract") +
  "Issue #1737 (Fixes). A total=False TypedDict describing the published payload (the producer set R9-F1.11's P6 barrier registers; the coordinator's _build_data_dict and its views), with the coordinator's DataUpdateCoordinator type parameter set to it, and the hand-written payload shape in tests/entities.py derived from it. "
  "Measure the typing-census delta first with HPO_TYPING_PYTHON (gate-scoping.md); a read with no producer then becomes a census error, which is the point. "
  "No runtime change; goldens identical. If the type lands in a new module, classify it (the tests/entities.py orphan check) and record its closure with --single. After R9-F10.4 and R9-EG-B2."),
 group("EG-B4", "store-version", [1740], [1740], ["R9-F10.1b", "R9-F10.4", "R9-EG-B3"], "a persistence-boundary change touching every store", None,
  HDR("EG-B4", "store version seam") +
  f"Issue #1740 (Fixes). (1) One version constant per store: DHW_PROFILE_STORE_VERSION serves the profile, draws and legionella stores today, and the snapshot and ledger stores use a literal. "
  f"(2) QuarantiningStore in {P}store.py gains Home Assistant's migration hook with a default that surfaces a failed migration (WARNING plus a repair issue through setpoint_check.create_issue), where the loaders now log at DEBUG and reset ({P}legionella.py re-stamps its last cycle on any load failure). "
  "(3) Demonstrate against R9-F10.1b's version-honouring stub: bump one store's version on a scratch branch; the gate fails at the base and passes at the head. After R9-F10.1b, R9-F10.4 and R9-EG-B3."),
 group("EG-B1", "solve-inputs", [1736], [1736], ["R9-F10.4", "R9-F2.4", "R9-F10.6", "R9-F11.5", "R9-EG-B0", "R9-EG-B4", "R9-EG-B5"], "a coordinator and optimizer refactor across the solve boundary", "any structure-budget raise needs tvofi's confirmation before the push (CLAUDE.md rule 2)",
  HDR("EG-B1", "per-solve immutable inputs") +
  f"Issue #1736 (Fixes). The configured hub objects (the coordinator's _opt_config, _thermal_params and _current_state) stop being written per solve. Each solve builds one per-solve input record consumed by the live solve, the fuse advisor, the price tiles and async_simulate; HeatPumpOptimizer.optimize takes it keyword-only instead of its positional arrays (its own comment in {P}optimizer.py concedes a transposition would be silent). "
  "The setback becomes a value in the record, so away.apply_setback, away.restore_setback and the compare-and-restore envelope are deleted, not extended. "
  f"Pure refactor: goldens byte-identical at the merge base, claim files untouched. Null control: {EV}/m1_hub_writes.py at {EVSHA} reports no hub writes on the solve path at the head and the base count at the base. "
  "Keep the record under the attrbag_classes_over_30 threshold by grouping, not flattening. Expect coordinator_loc to fall; re-record with the reason in the commit message. "
  "R9-EG-B0 reports first; its parity findings are tvofi's product decisions, not riders. Structure-budget writer: never in flight with R9-EG-B5 or R9-EG-B7 (plan principle 2); it lands after R9-EG-B5, whose planner takes its inputs at construction, so B1 changes at most that construction site. "
  "Lands after the round's fix stamp (after R9-F10.6 and R9-F11.5) so a refactor cannot hold the fixes' release; the fixer may prepare the branch earlier and merge origin/main before hand-off."),
 group("EG-B6", "collaborator-interfaces", [1739], [1739], ["R9-EG-B1"], "every collaborator module's access to coordinator state", None,
  HDR("EG-B6", "collaborator interfaces") +
  f"Issue #1739 (Fixes, with R9-EG-B2's surface half). {P}pump_arbiter.py, {P}boost.py, {P}away.py, {P}wood_fuel.py, {P}diagnostics.py, {P}setpoint_check.py, {P}services.py and {P}__init__.py stop reaching coordinator private members: each receives explicit inputs (the per-solve record from R9-EG-B1, or a narrow read-only view the coordinator publishes). "
  "The three writes (boost.apply setting the running action; the reload-handover and skip-once flags set from __init__.py) become coordinator methods. One module per commit; goldens byte-identical. "
  f"Enumerator: {EV}/m3_reach.py at {EVSHA} reports none at the head (control: the base count at the base). If R9-F10.4 priced out-of-class reach per #1738 arm (b), the re-record shows the drop; say which drops are real. After R9-EG-B1."),
 group("EG-B8", "dhw-block-replan", [1747], [1747], ["R9-F2.4"], "a behaviour fix in the solver's DHW replan, with a root-cause section owed (trigger 1)", None,
  HDR("EG-B8", "the DHW block ignored by the co-optimisation replan") +
  f"Issue #1747 (Fixes). _co_optimize in {P}optimizer.py rebuilds the DHW requirements without the block that _optimize_with_dhw's own _build_dhw_requirements call receives (blocked from the horizon's dhw_blocked), so with DHW mode-blocked and mostly negative prices the replan is adopted and ships DHW heat, masking the tank-floor breach the plan exists to report. "
  f"Probe at 22921612e10b: {EV}/b8_replan_blocked.py runs the tests/golden.py wood_coil scenario blocked with prices shifted; as-is ships DHW at the deepest shifts, the control arm (the replan given the block) ships none at every shift and reports the breach. "
  "Fix: pass the block into the replan, or skip the replan while DHW is blocked. fixer.md: failing test first (the probe's shifted arm), mutation proof, and the Root cause section on #1747 (defect-root-cause.md trigger 1: it reached released versions). "
  "Claims stay empty unless drift is measured: no golden scenario is blocked. Lands before R9-EG-B5, which rewrites this call site (plan principle 3)."),
 group("EG-B5a", "dhw-closure-dedupe", [1743], [], ["R9-F2.4", "R9-F10.4"], "a pure refactor of the two solve paths' duplicated closures", "a structure-budget re-record (downward) with the reason in the commit message",
  HDR("EG-B5a", "one builder for the duplicated solve closures") +
  f"Issue #1743 (Part of). The nested _space_traj, objective and objective_batch closures are duplicated between _optimize_space_only and _optimize_with_dhw in {P}optimizer.py: _space_traj is identical after dedent, and the other two differ only by an optional DHW power term added to the space power. "
  "Replace them with one optimizer method that builds all three from the horizon and an optional DHW plan power; with none, the arithmetic is the space-only path's. "
  "Pure refactor: tests/env_drift.py --all at the merge base must be byte-identical, and the claim files stay untouched. Expect duplication_blocks and max_method_loc to fall (measured by simulation in the EG-B5 design spec on the handoff/audit-r9-alt branch); re-record with the reason. "
  "After R9-F2.4, which edits _optimize_space_only's seeds, and R9-F10.4, the instrument. Structure-budget writer: never in flight with R9-EG-B5, R9-EG-B1 or R9-EG-B7."),
 group("EG-B5", "dhw-planner", [1743, 1748], [1743], ["R9-EG-B5a", "R9-EG-B8", "R9-F1.10", "R9-F10.4"], "extraction of the optimizer's DHW planner core into its own class", "tvofi opted in (2026-09-28); a classes_over_300 increase, unless R9-F10.4 re-defined it per #1738 arm (c), needs tvofi's confirmation before the push",
  HDR("EG-B5", "DHW planner extraction, opted in") +
  f"Issue #1743 (Fixes). The design spec is the EG-B5 design spec on the handoff/audit-r9-alt branch; this brief is its summary and the spec wins where they differ. "
  f"Move the nineteen DHW planner core methods of HeatPumpOptimizer in {P}optimizer.py (from _dhw_planning_prices and _baseline_dhw_economics through _build_dhw_requirements, _plan_dhw_min_cost, _repair_dhw_floor, _clamp_dhw_to_capacity, _apply_dhw_min_run and _plan_dhw_cheapest_first) into one planner class in a new module, built once per solve in optimize from explicit inputs (the model, the PV export price, the per-solve surplus and price-known mask) and passed down; it writes no attribute. "
  "_optimize_with_dhw, _solve_space and _co_optimize stay on the optimizer as orchestration: moving them would need a back-reference, the shape docs/HANDOVER.md refuses. "
  "_build_dhw_requirements returns the plan and the requirement; the optimizer keeps _dhw_requirement, assigned where the stash was written (last-writer-wins preserved), and _dhw_legionella_step is deleted (tests read it through a spy on the last build). DhwPlan keeps exactly its published fields: tests/features.py pins them. "
  f"Shared helpers move without a cycle: _step_humidity and _mean_humidity to {P}thermal_model.py, _pin_is_free to {P}manual_plan.py; the horizon parameter is typed by a Protocol in the new module, never by a TYPE_CHECKING import, which would add an equivalent guard today's count ratchet refuses. "
  "Tests: retarget the direct calls, class-level monkeypatches and captures in tests/features.py and the call in tests/guard_pins.py, with no delegating shims; add the new module to _P3_FILES in tests/features.py or the humidity rule silently stops covering the moved code. "
  "Ledger: re-key the moved rows (the planner's, the module constant's and the two humidity helpers') by path, scope and directory with their digests unchanged; tests/mutation_table.py --normalize does not do it; carry the survivor-triage row as it is. "
  "Closures: the new module makes the gate FULL; wait for the closures-autofix commit. Null controls: tests/env_drift.py --all byte-identical at the merge base, a whole-file provenance comparison under a stated substitution table, an AST check that the planner writes no attribute, and a three-dot diff at every merge from main (plan principle 3). "
  "Preconditions: R9-F10.3 carries #1748 (moved, not added), R9-EG-B8 has fixed #1747, and R9-EG-B5a has landed. Structure-budget writer: never in flight with R9-EG-B5a, R9-EG-B1 or R9-EG-B7."),
 group("EG-B7", "coordinator-seams", [1744], [1744], ["R9-EG-B1", "R9-EG-B6"], "a measured go/no-go on the coordinator's cheapest seams", "a classes_over_300 increase, unless R9-F10.4 re-defined it, needs tvofi's confirmation before the push",
  HDR("EG-B7", "coordinator seams, conditional") +
  "Issue #1744. After R9-EG-B1 and R9-EG-B6, re-measure cut_dhw, cut_views, cross_seam_edges and the hub-read counts at the merge base (tests/structure.py over tests/seam_map.json). "
  "Where a seam's cut falls, extract it as a class that owns its attributes, one seam per pull request, on the W5-G9 precedent (#750): goldens byte-identical, the seam map re-keyed in the same commit, the ledger re-keyed with --normalize, any raise asked before the push. "
  "Where it does not fall, record the halt on #1744 with the numbers and set this group done. Structure-budget writer: never in flight with R9-EG-B1 or R9-EG-B5."),
]
for g in EG:
    G[g["group"]] = g

# --- 4. waves over the open DAG ---
open_ids = [k for k, g in G.items() if g["resume"]["stage"] != "done"]
depth = {}
def dep(k, seen=()):
    if k in depth: return depth[k]
    if k in seen: raise SystemExit(f"cycle at {k}")
    ups = [a for a in G[k]["after"] if G[a]["resume"]["stage"] != "done"]
    depth[k] = 1 + max((dep(a, seen + (k,)) for a in ups), default=0)
    return depth[k]
for k in open_ids:
    G[k]["wave"] = dep(k)
for k, g in G.items():
    for a in g["after"]:
        assert a in G, f"{k}: after {a} not in file"
d["groups"] = list(G.values())
d["_comment"] = [
 "ALT roster (2026-09-28): the live round-9 roster from handoff/audit-r9-fixplan with (1) every merged group's resume truthed from origin/main's merge commits (31394964; F1.4 merged as #1735 at 686239d2); (2) four verified endgame carries folded into R9-F1.10 (#1741), R9-F10.1b (#1740), R9-F10.3 (#1748) and R9-F10.4 (#1738); (3) lane EG appended: R9-EG-B0 (root-cause seat), R9-EG-B1..B8 and R9-EG-B5a. `wave` is recomputed over open groups only (1 = startable now). Plan: handoff/round9/state/ALT-ENDGAME-PLAN.md on handoff/audit-r9-alt; EG-B5 design: handoff/round9/state/alt/EG-B5-DESIGN.md there (tvofi opted in to B5, 2026-09-28).",
] + list(d["_comment"])
json.dump(d, open(OUT, "w"), indent=2, ensure_ascii=False)
open(OUT, "a").write("\n")
crit = max(open_ids + [g["group"] for g in EG], key=lambda k: G[k]["wave"])
print("open groups:", len([k for k in G if G[k]["resume"]["stage"] != "done"]), "| max wave:", G[crit]["wave"], crit)
for w in sorted({G[k]["wave"] for k in G if G[k]["resume"]["stage"] != "done"}):
    print(f"wave {w}:", [k.replace("R9-", "") for k in G if G[k]["resume"]["stage"] != "done" and G[k]["wave"] == w])
