#!/usr/bin/env python3
"""Roster rev 2: the live roster (handoff/audit-r9-fixplan .claude/workflows/wave-r9-groups.json at 27049219)
plus the deltas of the RCA-1736 shape screen, register v2 and the bulk RCAs (2026-09-28).

  python3 build_roster_rev2.py LIVE.json ALT-ROSTER.json OUT.json

Deltas:
  1. resume truthing: every group the live file shows not-started but main merged takes ALT's truthed resume
     (18 groups regressed by a regeneration); EG-B0's rca-done moves off EG-B1 onto EG-B0 (27049219 put it on B1)
  2. carries appended to the briefs of R9-EG-B1, R9-F1.7, R9-F1.8, R9-F2.4, R9-F10.3, R9-F10.4, R9-F11.4
  3. new groups: R9-EG-B9, R9-EG-B10, R9-EG-R0, R9-EG-R1, R9-F10.1c, R9-F10.7, R9-F11.7 (+ N-name-sort if NAMESORT)
  4. edges: R9-F1.6 after R9-EG-B9 (sev:high behaviour fix in the F1 serial slot); R9-EG-B1 after R9-EG-B9, R9-EG-B10
"""
import copy, json, sys

live, alt, out = sys.argv[1:4]
L = json.load(open(live))
A = {g['group']: g for g in json.load(open(alt))['groups']}
G = {g['group']: g for g in L['groups']}
EV = '8061ec9b'   # handoff/audit-r9-alt: the shape screen's probes (handoff/round9/state/alt/evidence/screen)
RG = 'c5c32f2b'   # handoff/audit-r9-alt: register v2 and RCA-BULK-1..3 (handoff/round9/state/alt/register, rca)
RG2 = 'fbce8345'   # handoff/audit-r9-alt: RCA-BULK-4
RG3 = '53a9bbab'   # handoff/audit-r9-alt: register v2 reconciled (the version EG-R0 lands)

# ---- 1. resume truthing
fixed = []
for gid, g in G.items():
    a = A.get(gid)
    if a and a['resume'].get('stage') == 'done' and g['resume'].get('stage') != 'done':
        g['resume'] = copy.deepcopy(a['resume'])
        fixed.append(gid)
G['R9-EG-B1']['resume']['stage'] = 'not-started'
G['R9-EG-B0']['resume'].update({
    'stage': 'rca-done', 'last_step': 'RCA-1736 posted on #1736 (comment 5877263448, 2026-09-28T19:47Z); document on handoff/r9-eg-b0 at 08304c9a',
    'next_step': 'none: its obligations are in R9-EG-B1\'s brief; the class is N-shared-config in register v2 (R9-EG-R0)'})

# live status at 2026-09-29T00:05Z (origin/main 5a2a62ff; #201 comment 5879584794; the seats' resume branches)
G['R9-F1.5']['resume'].update({'stage': 'in-review', 'commit': 'e3ad93d02bd8f5a7f632746d25003e3829761606',
    'last_step': 'PR #1751 open (hpo-author) at e3ad93d0, merge base 686239d2; first full CI 30 check-runs, zero red; branch frozen for review',
    'next_step': 'fix-review.md from a detached worktree at e3ad93d0 (review branch handoff/r9-f1-coordinator-5-review), then merge; R9-EG-B9 is next in the F1 slot'})
G['R9-F7.2']['resume'].update({'stage': 'fixing', 'commit': '028630ac',
    'last_step': 'failing test pushed at 84d99a9b; fix commit 028630ac (the valve gate typed as a sensor-base subclass) on handoff/r9-f7-entities-2',
    'next_step': 'fixer.md steps 4-8 at the head, then the hand-off; R9-F7.4 follows its merge'})

# ---- 2. carries
def carry(gid, text):
    G[gid]['brief'] = G[gid]['brief'].rstrip() + ' ' + text
    return gid

carried = [
    carry('R9-EG-B1', f'Carry (shape screen, #1736 comment 5879641429, verified before filing): the per-solve record must also take over four readers the RCA did not list, each confirmed with a probe and a null arm at {EV} (handoff/round9/state/alt/evidence/screen). H1: a scheduled cycle inside a button- or service-started away solve publishes the setback through _thermal_view and _dhw_view, the keys the card\'s schedule editor pre-fills from (H1.py); those views read configured values, never the record. H3: dhw_hourly_draw_pattern is written by the DHW learner and per solve; the blend moves into the record, and normalize_profile\'s fallback and the published DHW advisor read the pooled profile (H3.py). H4: the DHW learner\'s freeze reads _current_state.external_heat_active, a copy made only inside the solve, so in comfort, boost or off it never updates; read the live flag (H4.py). H2 (mechanism only, no effect reproduced): _record_quiet_comfort_period judges quiet periods against the effective band; decide configured or effective in the PR body. And the executor hand-off barrier in tests/entities.py checks only the callable; once the solve hands over a frozen record, refuse a live hub object as an argument. The class also has members outside the hubs that land before this PR: R9-EG-B9 (#1752, #1753) and R9-EG-B10 (#1754).'),
    carry('R9-F1.7', f'Carry (register v2 class RCA for P10, RCA-BULK-1 at {RG}, handoff/round9/state/alt/rca/RCA-BULK-1.md section 2): N-loop-cpu is P10 in register v2, and this PR is where its class barrier lands. Build the check that model-kernel calls made outside process_worker.run_worker on a replayed day are zero (handoff/round9/state/alt/rca/bulk1/p10_loop_kernels.py: base arm on the loop from topology.py _advisor_replay, advisor-removed arm zero, worker-failing arm on an executor thread), extend its kernel list to the sysid fit, and make it the barrier the register\'s P10 detector names. The demonstration: red at the merge base, green at the head, and the fallback arm still counted as executor work.'),
    carry('R9-F1.8', f'Carry (register v2 class RCA for P8, RCA-BULK-1 at {RG}, section 3): resolve_currency in custom_components/heatpump_optimizer/currency.py is already the one shared resolver, and it returns the instance\'s configured currency, not the price feed\'s currency, so forcing every surface through it (the metric #1657 proposes) would lock the defect in; do not build that metric. Carry the feed\'s currency from price ingest and check it with the EUR-feed replay (handoff/round9/state/alt/rca/bulk1/p8_denomination.py: published money units in the instance currency under a EUR feed, none under a SEK feed). Whether the displayed currency follows the feed is a product rule: ask tvofi before the push.'),
    carry('R9-F2.4', f'Carry (register v2 class RCA for P4, RCA-BULK-1 at {RG}, section 4): the class-eliminating barrier is refused on numbers (tvofi\'s refusals on #1293 and #1294); the solve certificate in tests/optimality.py is the class detector. #1664 is fixed or claimed here as its own finding, and nothing in this PR widens the seed set or tightens the tolerance as a class measure.'),
    carry('R9-F10.3', f'Carry (register v2 class RCA for I2, RCA-BULK-2 at {RG}, handoff/round9/state/alt/rca/RCA-BULK-2.md section 1): closure.py check compares the committed closure only with a new recording by the same recorder, so the recorder\'s blind spots never show. Add a nightly second oracle, strace -f of the gate against the committed closures, reporting files the recorder missed; refuse any over-scope barrier. Register v2 moves three rows out of I2, so the class count this PR cites is the register\'s, not the round-9 judge\'s.'),
    carry('R9-F10.4', f'Carry (register v2 class RCA for N-structure-blind, RCA-BULK-2 at {RG}, section 2): judge liveness by reachability from production roots, tests not counting as roots, with a self-check that plants one example of every past shape and a printed count of the shapes the metric cannot measure; register v2 folds N-dead-member into N-structure-blind. Carry (RCA-BULK-3 section 2, #1545): the typing check #1590 landed fails at the claim\'s commit and passes at main, but qs_py_typed_files has no check; give it one here, beside the ratchet truth this PR owns.'),
    carry('R9-F11.4', f'Carry (RCA-BULK-3 at {RG}, handoff/round9/state/alt/rca/RCA-BULK-3.md section 5, #1041): the silent-zero refusal is overturned on its re-run cost test. Land merge_shape_guard as a check in agreement.mjs that refuses an item every reader answers null (the prototype is handoff/round9/state/alt/rca/bulk3/merge_shape_guard_lite.py). The class barrier for N-silent-zero, registering count-printing instruments in field_coverage.mjs\'s perturb-to-red registry, is tvofi\'s decision: ask before building it.'),
]

# ---- 3. new groups
TEMPLATE = copy.deepcopy(G['R9-EG-B8'])

def group(gid, lane, issues, fixes, after, wave, why, branch, brief, owner_gate=None, cls='architecture', effort='high',
          fixer='opus'):
    g = copy.deepcopy(TEMPLATE)
    short = gid.replace('R9-', '')
    g.update({'group': gid, 'lane': lane, 'issues': issues, 'fixes': fixes, 'after': after, 'wave': wave,
              'class': cls, 'effort': effort, 'owner_gate': owner_gate, 'brief': brief,
              'fixerModel': fixer})
    g['model'] = dict(g['model'], fixer=fixer, fixer_why=why)
    g['resume'] = dict(g['resume'], branch=branch, note_file=f'handoff/round9/fix/resume/{short}.md on {branch}',
                       review_branch=f'{branch}-review',
                       review_note_file=f'handoff/round9/fix/resume/{short}-review.md on {branch}-review',
                       plan='handoff/audit-r9-alt: handoff/round9/state/ALT-ENDGAME-PLAN.md (rev 2), handoff/round9/state/ALT-ROSTER.json, handoff/round9/state/alt/SCREEN-1736-SHAPES.md, handoff/round9/state/alt/register/REGISTER-V2.md',
                       note='Added by roster rev 2 (the RCA-1736 shape screen and register v2, 2026-09-28). The seat\'s resume note on its branch outranks this entry for in-flight state.')
    G[gid] = g
    return gid

new = [
    group('R9-EG-B9', 'EG', [1752, 1753], [1752, 1753], ['R9-F1.5'], 2,
          'a behaviour fix that stops unrequested maximum actuation, with a root-cause section owed (trigger 1)',
          'handoff/r9-eg-action-copy',
          f'Round-9 endgame PR EG-B9 (lane EG, behaviour fix in the F1 serial slot: class N-shared-config outside the three hubs). Issues #1752 (Fixes) and #1753 (Fixes). #1752: boost.overlay in custom_components/heatpump_optimizer/boost.py writes the boost into coordinator._current_action in place and nothing removes it; the action is replaced only on a successful solve, so after a cancel or expiry a no_prices or solve_failed cycle keeps actuating maximum power and displace until the plan-stale gate, and data current_action is the same object. Probe at {EV}: handoff/round9/state/alt/evidence/screen/S1.py (probe arms no_prices and solve_failed against the solve-succeeds and never-boosted nulls). Fix: keep the last solve\'s action as its own base and build the published and actuated action each cycle as the overlay of a copy, as _run_system_identification already does. #1753: _maybe_run_fuse_advisor and _maybe_refresh_price_tile save the what-if limiter and cache, await async_simulate and restore both unconditionally (the #1517 shape); S2.py shows a spurious rate limit and a lost user answer. Fix: give them a shadow-solve entry that neither reads nor writes the user limiter and cache, and delete the borrow. fixer.md: failing tests first (the probes\' arms), mutation proof, the Root cause section on #1752 (defect-root-cause.md trigger 1; the class cause and process state are RCA-1736\'s). No golden boosts, so claims stay empty. Lands before R9-EG-B1 (plan principle 3) and before R9-F1.6, which waits on it: the defect actuates the pump.'),
    group('R9-EG-B10', 'EG', [1754, 1755], [1754, 1755], ['R9-EG-B9', 'R9-F1.6'], 3,
          'solve-lifecycle concurrency: a dropped re-solve, an override identity, and per-entry fallback state',
          'handoff/r9-eg-solve-lifecycle',
          f'Round-9 endgame PR EG-B10 (lane EG, behaviour fix: the solve lifecycle). Issues #1754 (Fixes) and #1755 (Fixes). #1754: async_run_optimization in custom_components/heatpump_optimizer/coordinator.py returns early while a solve is in flight and records nothing, so the re-solve an input change asked for (async_apply_manual_plan, async_clear_manual_plan and every refresh-now caller) is dropped until the next scheduled cycle; and _record_manual_release writes the finished solve\'s releases into whichever override is current after the await. Probe at {EV}: handoff/round9/state/alt/evidence/screen/C2.py (swap arm against the no-swap and new-override-alone nulls). Fix: the guard records a pending re-run that the in-flight solve\'s finally honours, coalesced to one, and releases go to the override the solve pinned against. #1755: the worker-fallback streak and cause are per hass, so one entry\'s success resets another\'s cap (C1.py); key them by entry. fixer.md: failing tests first, mutation proof. Lands before R9-EG-B1 (plan principle 3).'),
    group('R9-EG-R0', 'EG', [1759], [], [], 0,
          'a data PR: the register rebuilt for rounds 1-9, its enum, and the RCA documents moved in-tree',
          'handoff/r9-eg-register-v2',
          f'Round-9 endgame PR EG-R0 (lane EG, register data). Issue #1759 (Part of). Replace tools/audit/bugclasses.json with handoff/round9/state/alt/register/bugclasses.v2.json at {RG3}, move the class_guess enum of tools/audit/finding.schema.json in the same PR (handoff/round9/state/alt/register/finding.schema.class_guess.json; check-wave-script.mjs holds the two equal), and add the RCA documents under tools/audit/rca/: the fourteen round-9 class RCAs from 763b0ba4 (handoff/round9/state/rca), RCA-1736 from handoff/r9-eg-b0 at 08304c9a, and RCA-BULK-1 to RCA-BULK-4 from handoff/audit-r9-alt. tools/audit is INERT, so the gate scope is unchanged. Verify with python3 handoff/round9/state/alt/register/build_v2.py --check on the branch that carries it before copying. tvofi reviews the move list in rows_v2.tsv (the move column) and the open questions in handoff/round9/state/alt/register/REGISTER-V2.md before merge. No policy, no budget.',
          owner_gate='tvofi reviews the register v2 move list and REGISTER-V2.md\'s open questions before merge', cls='register', effort='medium', fixer='sonnet'),
    group('R9-EG-R1', 'EG', [1759], [1759], ['R9-F11.4', 'R9-EG-R0'], 12,
          'the round\'s deterministic register fold and its check, plus owner-gated policy clauses',
          'handoff/r9-eg-register-fold',
          f'Round-9 endgame PR EG-R1 (lane EG, the permanent register fold). Issue #1759 (Fixes). Specified in handoff/round9/state/alt/rca/RCA-BULK-2.md section 3.4 at {RG}. Build a new deterministic fold-ledger script under tools/audit, which .claude/workflows/audit-verify.js runs after the class sweep: it appends each survivor and each seam marked beyond_finding to its class, refuses a survivor whose class is absent and a new id without nearest and differs, and opens the round-record PR. Give it a check mode run in an existing lane: every in-tree judge survivor in exactly one class, every class that met an adopted trigger carrying a barrier or an rca, every rca resolving under tools/audit/rca. The demonstration is handoff/round9/state/alt/rca/bulk2/register_check.py: red on the register at 3490cb16, green on register v2 with its RCAs cited, and red at the round-8 register. Policy, each asked of tvofi before the push: reuse before minting in tools/audit/briefs/judge.md, the cross-round trigger in .claude/rules/defect-root-cause.md, where an RCA is recorded, and the declared-families line in tools/audit/briefs/D8.md step 3 (#1760). audit-verify.js and the briefs are code-owned.',
          owner_gate='policy (judge.md, defect-root-cause.md) and code-owned audit-verify.js: tvofi\'s confirmation before the push and approving review at the head', cls='register'),
    group('R9-F10.1c', 'F10', [1756], [1756], ['R9-F10.1b'], 9,
          'two replay arms for the DST tracer, each demonstrated against a historical mutant',
          'handoff/r9-f10-gate-infra-1c',
          f'Round-9 fix PR F10.1c (gate infrastructure, class P7 barrier completion). Issue #1756 (Fixes). The class RCA (handoff/round9/state/alt/rca/RCA-BULK-1.md section 1 at {RG}) re-introduced each historical P7 member into main: the tracer in tests/dst_checks.py fails the grid member and passes the tariff and plan-age members. Add a config arm (capacity tariff and off-peak mask at 15 and 60 minutes, a manual plan applied before the fold) and a straddle arm (the solve failing across the transition, so stamps written before the fold are read after it). Demonstration: the mutants in handoff/round9/state/alt/rca/bulk1/p7_mutants.py for the tariff and plan-age members turn red, main and the plain-day null stay green. The arms are expected to fire on the manual-override length in custom_components/heatpump_optimizer/services.py and custom_components/heatpump_optimizer/manual_plan.py: a fix or a named exemption, asked of tvofi, since the override length is behaviour. Update the P7 barrier text in tools/audit/bugclasses.json to name what the tracer does not reach.',
          cls='P7', effort='high'),
    group('R9-F10.7', 'F10', [1758], [], ['R9-F10.6'], 13,
          'a nightly loop-stall instrument inside real Home Assistant, to diagnose an unexplained freeze',
          'handoff/r9-f10-loop-heartbeat',
          f'Round-9 fix PR F10.7 (gate infrastructure, diagnostic). Issue #1758 (Part of). The owed trigger-1 RCA for the v6.6.0 options-flow freeze (handoff/round9/state/alt/rca/RCA-BULK-3.md section 4 at {RG}) could not establish the cause. Add a loop-heartbeat arm to the nightly-ha options round-trips in tests/nightly_ha.py: a one-millisecond call_later probe recording the maximum gap, across an untouched exit, a changed save and several changed saves in a row in menu mode, with a py-spy dump on a stall. Nightly only. The barrier decision waits for what it finds; tvofi runs the Profiler on the host in parallel.',
          cls='P10', effort='medium'),
    group('R9-F11.7', 'F11', [1757], [1757], ['R9-F11.5'], 13,
          'a governance arm in graders-head-copy that runs the PR\'s own governance graders under the Actions token',
          'handoff/r9-f11-governance-7',
          f'Round-9 fix PR F11.7 (governance, the #1721 RCA countermeasure). Issue #1757 (Fixes). The RCA (handoff/round9/state/alt/rca/RCA-BULK-3.md section 1 at {RG}): a changed ruleset comparator first ran under the Actions GITHUB_TOKEN on main, because governance.yml restores the pinned graders from the base and graders-head-copy in .github/workflows/tests.yml runs only coverage_ratchet and delivery_status. Add a governance step there: when the three-dot diff touches .claude/workflows, run the PR\'s own policy_lint.mjs and field_coverage.mjs under the read-only token, non-required like the existing job. Demonstration: red on a branch whose counts.mjs is reverted to 87d780c7, green at main (handoff/round9/state/alt/rca/bulk3/demo_1721.txt). tests.yml is code-owned.',
          owner_gate='tests.yml is code-owned: merges on tvofi\'s approving review', cls='P11', effort='medium'),
]

new.append(group('R9-F7.4', 'F7', [1760], [1760], ['R9-F7.2'], 3,
          'a production family declaration and one generic contiguity check replacing six per-finder pins',
          'handoff/r9-f7-entities-4',
          f'Round-9 fix PR F7.4 (entities, class N-name-sort barrier). Issue #1760 (Fixes). The class RCA (handoff/round9/state/alt/rca/RCA-BULK-4.md at {RG2}): entity family membership is declared nowhere in production, so each round\'s finder invented a family list and each fix pinned exactly that list; tests/entities.py holds six such blocks and none measures another\'s families. Declare families in custom_components/heatpump_optimizer/const.py as the translation key\'s lead token plus an explicit override table, and replace the contiguity parts of the six blocks with one check: every declared family of two or more members forms one contiguous run in the English and Swedish name sorts under one collation, with anchors so an empty roster fails. Demonstration: handoff/round9/state/alt/rca/bulk4/family_check.py and demo.out (the #1334 and #1668 fix commits flip it from red to green; the #1733 cost split turns it red). Ask tvofi before the push whether the away and Swedish compressor splits are renamed or allowed.',
          cls='N-name-sort', effort='medium', fixer='sonnet'))

# waves: one past the latest after-edge's wave
for gid, w in {'R9-EG-B9': 8, 'R9-EG-B10': 9, 'R9-EG-R0': 0, 'R9-EG-R1': 17, 'R9-F10.1c': 12, 'R9-F10.7': 18, 'R9-F11.7': 18, 'R9-F7.4': 2}.items():
    G[gid]['wave'] = w

# ---- 4. edges
G['R9-F1.6']['after'] = G['R9-F1.6']['after'] + ['R9-EG-B9']
G['R9-EG-B1']['after'] = G['R9-EG-B1']['after'] + ['R9-EG-B9', 'R9-EG-B10']

order = [g['group'] for g in L['groups']] + [n for n in new if n not in [g['group'] for g in L['groups']]]
L['groups'] = [G[k] for k in order]
L['_comment'] = list(L.get('_comment') or []) + ['rev 2 (2026-09-28, handoff/audit-r9-alt): resume truthing, carries from the RCA-1736 shape screen and register v2 bulk RCAs, groups EG-B9, EG-B10, EG-R0, EG-R1, F10.1c, F10.7, F11.7.']
json.dump(L, open(out, 'w'), indent=2, ensure_ascii=False)
open(out, 'a').write('\n')

# DAG check
ids = {g['group'] for g in L['groups']}
bad = [(g['group'], a) for g in L['groups'] for a in g['after'] if a not in ids]
seen, stack = {}, []
def visit(n):
    if seen.get(n) == 1: raise SystemExit(f'cycle at {n}')
    if seen.get(n) == 2: return
    seen[n] = 1
    for a in next(g for g in L['groups'] if g['group'] == n)['after']: visit(a)
    seen[n] = 2
for n in ids: visit(n)
print(f'resume truthed: {len(fixed)} {fixed}\ncarries: {carried}\nnew: {new}\ndangling edges: {bad}\nacyclic: yes, {len(ids)} groups')
