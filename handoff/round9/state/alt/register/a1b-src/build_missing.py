import csv
R='5a2a62ff:docs/audit-2026-09.md'
R3F='5a2a62ff:tools/audit/round3/ledger/filed.tsv'
R3V='5a2a62ff:tools/audit/round3/ledger/verdicts.tsv'
R4J='5a2a62ff:tools/audit/round4/judge-verdicts.md'
rows=[]
def add(rnd,fid,iss,cls,conf,src,note,kind='judged',alias=''):
    rows.append([rnd,fid,iss,cls,alias,kind,conf,src,note])
# ---- R1 (register L49-215; verdicts L256-298) ----
V1a='verdict L260 "all ten D4 UI/UX findings" verified'
add('R1','D4-05','#169','P1','med',R+':83','high; grid_fee_rules accepts any sign/magnitude, sign-flip typo becomes permanent fee subsidy (input with no plausibility bound, R9 N-plausibility->P1 precedent); '+V1a)
add('R1','D4-07','#170','P2','med',R+':85','medium; day_start/day_end slider ranges disjoint, forbid valid schedules and shield the real validator (two definitions of a valid schedule disagree); '+V1a)
add('R1','D4-08','#171','P1','low',R+':86','medium; dhw_windows accepts a meaningless 1-minute window (input with no plausibility bound); '+V1a)
add('R1','D4-09','#198','_unclassified','med',R+':87','medium; options page densest, ~18 fields zero grouping; reason: form density/grouping is UX information architecture, no mechanism class fits; '+V1a)
add('R1','D4-10','#179','_unclassified','med',R+':88','medium; 55 sensors in one flat device, 10 diagnostic, 6 disabled-by-default; reason: entity organisation/categorisation, no mechanism class fits (sibling-inconsistency parts are D8-04/D8-06); '+V1a)
add('R1','D5-05','','I5','high',R+':97','low-med; tests/README.md omits manual_plan.py and setup_qa_render.mjs; fixed PR #127 v6.2.7; verdict L265 "all D5" verified')
add('R1','D7-06','#178','N-structure-blind','med',R+':119','low; 5 verified dead symbols (+4 CONF keys REFUTED, L251-256: "The 5 dead symbols stand"); register net 59 counts D7-06 among the 3 killed but #178 filed on the surviving half; class per R2 D7-06 precedent (dead production members)')
add('R1','D8-03','#174','N-name-sort','high',R+':154','medium; DHW domain across 3 entity_id prefixes breaks alphabetical clustering; verdict L266 verified; the root-cause seat\'s known miss')
add('R1','D8-04','#175','P2','med',R+':155','medium; stat_kind headline family split 2-vs-2 across entity_category (one family, divergent category decision); no explicit verdict line in L256-298 (neither verified nor weakened list names it) but filed #175 and delivered in B4 (L358) -> survivor, verdict implicit')
add('R1','D8-05','#176','P2','high',R+':156','low; PredictionAccuracySensor missing its siblings\' evidence-wait pattern (guard at siblings, missing here); verdict L289 weakened/minor')
add('R1','D8-06','#177','P2','med',R+':157','low; ECL110 sensors lack entity_category=DIAGNOSTIC unlike other disabled-by-default sensors; verdict L289 survives 2-1')
add('R1','D9-03','#166','I1','high',R+':171','high; stress gate: one 1400x per-scenario ratio spans 1913x cost spread, cheapest can regress 2626x and pass (R9 N-cpu-gate-blind->I1 precedent); verdict L259 strengthened')
add('R1','D9-04','#167','I1','high',R+':172','medium->low-med; zero memory instrumentation in the gate (R4 D9-06 memory-gate precedent I1); verdict L298 weakened')
add('R1','D10-04','#194','I1','med',R+':130','high; config-flow tests never exercise a full flow, error paths or dup prevention (test gap); verdict L265 D10-01..05 verified')
add('R1','D10-05','#183','I5','low',R+':131','medium; no uninstall/removal instructions in docs (docs missing vs shipped stores; A1 might flag as QS conformance -> _unclassified); verdict L265 verified')
add('R1','D10-09','','I3','low',R+':135','medium; Tibber outage logs ERROR every poll, not once; fixed PR #144 v6.2.12; class follows R2 D10-03 (its regression) = I3, fit is weak (alt _unclassified: log-once conformance); verdict L264 verified')
add('R1','D10-10','#184','_unclassified','med',R+':136','medium; no platform declares PARALLEL_UPDATES; reason: HA quality-scale code conformance (A1 precedent for R1 D10-01/02/12); verdict L266 verified')
add('R1','D10-11','#195','I1','low',R+':137','low; sampled statement coverage far below 95% bar; fixed PR #889 v6.4.3; coverage deficit as test gap (alt _unclassified); verdict L266 verified')
add('R1','D10-14','#196','_unclassified','med',R+':140','low; no reconfigure flow; reason: HA quality-scale conformance (A1 precedent); verdict L266 verified')
add('R1','D10-15','#197','_unclassified','med',R+':141','low; mypy 160 errors, majority stub artefacts; reason: typing conformance count, no mechanism class; verdict L266 verified')
# ---- R2 ----
add('R2','D4-09','','_unclassified','med',R+':572','low; corroborates #198 (R1 D4-09): five form pages >15 fields; reason: form density/grouping, UX IA; D4 panel "still to run" at register (L896), nothing marks it refuted; corroboration rows kept per rows_v2 precedent (R2 D2-04/D7-01/D7-03/D7-05/D9-05)')
add('R2','D4-10','#264','P2','high',R+':573','low; DHW setup defaults log a WARNING the coordinator deliberately exempts for that pair (one fact decided twice); filed #264 after D4 panel')
add('R2','D4-11','#265','I4','med',R+':574','low; CARD_VERSION 5.4.17 in a 6.2.14 release (two definitions of the release version); #265 title: duplicate-copy guard half refuted, version half survives')
add('R2','D4-12','#266','_unclassified','low',R+':575','low; "the same than the saved plan": English template composition ungrammatical; reason: i18n string-composition defect, no mechanism class (alt I5); filed #266')
add('R2','D10-06','#296','_unclassified','low',R+':658','low; services in async_setup_entry not async_setup: re-report of R1 D10-01, fixed since baseline by #207; panel L939 3-0 verify; include only under rows_v2 precedent that keeps R2 D10-01 (also fixed-since-baseline); class per A1 flag on R1 D10-01')
add('R2','D10-07','#297','_unclassified','low',R+':659','low; no PARALLEL_UPDATES: re-report of R1 D10-10, fixed since baseline by #207; panel L940 3-0 verify; HA QS conformance')
add('R2','D10-08','#298','_unclassified','med',R+':660','low; hass.data[DOMAIN] / entity base classes outside entity.py: fixed since baseline by #207 (partial, common-modules residual); panel L941 3-0 verify; A1 precedent R1 D10-02')
add('R2','D10-10','#300','I5','med',R+':662','low; 64 _attr_icon, no icons.json: corroborates #189 (R1 D10-13, I5); panel L943 3-0 verify')
add('R2','D10-11','#301','_unclassified','low',R+':663','low; no diagnostics platform: re-report of R1 D10-12, fixed since baseline by #209; panel L944 3-0 verify; A1 precedent R1 D10-12')
add('R2','D10-12','#302','I5','med',R+':664','low; docs gaps: removal (fixed #207), known limitations, blueprints, supported devices; panel L945 2-0 weakened; canonical for zcode D10-18 (#218, blueprint half)')
add('R2','D10-13','#303','_unclassified','med',R+':665','low; mypy --strict 722 errors (427 production-only under pinned ruler): corroborates #197 (R1 D10-15); panel L946 1-0 weakened; typing conformance count')
add('R2','D10-14','#304','I1','med',R+':666','low; statement coverage 88.4 %, config_flow.py below 100 % rule: corroborates #195/#194; panel L947 2-0 weakened, config-flow half verified with a killing mutation')
add('R2','D9-06','#291','I1','med','gh:#291','medium; default two-zone DHW solve 2.33x slower c398fc8->main and the stress gate cannot see it (R9 N-cpu-gate-blind->I1); judge-found during D9-05 re-measure; labels judge:verified, round-2; absent from the register table')
add('R2','D2-07','#310','P5','high','gh:#310','high; regression of #212: drifting sensor adopted at confidence 1.000 with -14.2 % UA bias; judge-found re-checking D2-04; labels judge:verified, regression, round-2; fixed PR #322')
add('R2','D2-08','#325','P5','high','gh:#325','medium; drifting+noisy sensor unidentifiable (median UA error -0.184, discrimination at null); rescoped by judge 2026-09-03; labels judge:verified, round-2')
# ---- R3 ----
add('R3','D4-01','#822','P9','high',R3F+':28','medium; no-data legend chips 1.90:1 light/2.36:1 dark, tabbable, click persists a hidden-series pref; votes.tsv v1+v2 verify (not in verdicts.tsv); filed')
add('R3','D4-02','#823','P9','high',R3F+':29','medium; away strip outside coarse-pointer rule set: 13 px checkbox, 11/25 finger points miss; votes.tsv v1+v2 verify; filed')
add('R3','D4-03','#824','_unclassified','low',R3F+':30','low; config flow declares 0 section() groupings where options declares 34; votes v1+v2 weaken(low); reason: form grouping UX IA (alt P2: grouping applied on one flow, missing at its sibling)')
add('R3','D6-03','FIXED-in-PR-833','I5','high',R3F+':43','low; configuration.md under-declares service fields (16/4/5 vs 11/3/3); verdicts.tsv:35 weakened low')
add('R3','D7-02','#780','I1','high',R3F+':8','low; rolling.py:577 regression guard asserts over an empty set, cannot catch its named defect (+ dead attr last_dhw_refused); verdicts.tsv:9 weakened low; ruling-tranche-1 L47/L70')
add('R3','D10-01','#827','I5','high',R3F+':32','low; quality_scale.yaml marks 3 satisfied rules todo, totals line wrong (R4 D10-01 precedent I5); verdicts.tsv:39 weakened low')
add('R3','D10-03','#829','_unclassified','med',R3F+':34','low; strict-typing unmet at 187 errors under the repo ruler, py.typed not owed; verdicts.tsv:41 weakened low; reason: typing conformance count (R7 D10-01, its re-open, is I5 as claim drift)')
add('R3','D10-04','#830','P11','high',R3F+':35','low; coordinator built without config_entry, hastub (*args,**kwargs) signature makes it undetectable by the whole gate: the test double is the only oracle; verdicts.tsv:42 weakened low (stated mechanism refuted, one-keyword fix stands)')
add('R3','R3-INSTRUMENT','#817','I5','med',R3F+':27','medium; 14 audit-instrument defects bundled on owner instruction (5 harness headers disagree with their harness, stale brief literals; also item 8 verdicts.py tail miscounts kills = I1, item 6 unqualified id namespace); panel/judge by-products, fixed PR #893; kept per R5-INST-01/R7-INSTR-01 precedent')
# ---- R4 ----
add('R4','D1-INST','#924','P11','high',R4J+':328','low hygiene; stub refresh entry points are counters, the gate never runs a cycle through the coordinator base class (UpdateFailed->unavailable chain unexercised); judge weakened(low) 1v/2w')
add('R4','D3-INST','#934','I2','low',R4J+':338','low hygiene; closure/cost accounting records 0.4 s vs real 160.9 s, README double-charges; judge verified(low) 3v; class: recorded closure diverges from the measured one (alt _unclassified accounting)')
add('R4','D3-S4','#933','I1','med',R4J+':337','hygiene/low; CLAMP_DROP survivor judged equivalent (numpy slices clamp); judge verified 3v "judged equivalent as filed"; excluded by round-8 classes.md as equivalent, but filed and judged like D3-S3 (in rows_v2 as I1)')
add('R4','D4-03','#936','P9','high',R4J+':341','low; 24 px target floor emitted only under pointer:coarse, zoom pair 20.22 px under a mouse; judge verified(low) 3v')
add('R4','D8-INST','#947','I1','med',R4J+':352','low hygiene; six vacuous instrument checks; judge verified(low) 3v panel-sustained')
add('R4','D9-INST','#950','_unclassified','low',R4J+':355','low hygiene; 4+1 harnesses print no thread_factor the finder contract requires; judge verified(low) 3v; reason: harness contract telemetry gap, no mechanism class (alt I5)')
add('R4','R4-OWNER-01','#908','P6','low','gh:#908','medium; operation score EMA frozen stale over free days with no staleness signal; envelope grade computed from config with no evidence (silent fallback presented as measured, R1 D1-04 precedent P6; alt _unclassified); owner-verified by executed production code, not panel; filed under [R4-..] beside the 42, fixed PR #1004')
# ---- R5 run A, baseline eaa2a06 (#1207-#1241) ----
A='Round-5 run at baseline eaa2a06 (finder->panel->judge), filed 2026-09-19; '
r5=[
('D0-01','#1207','P4','high','medium; verified; polish <2 % discarded by _LBFGSB_RESTART_KEEP_REL (stop/keep rule does not bracket the optimum)'),
('D0-02','#1208','P4','high','low; verified; polish runs on one candidate only'),
('D1-01','#1209','P1','high','high; verified; NaN learned scalars from the thermal_learning store install on the live model'),
('D2-01','#1210','P3','high','low; verified; soft top-k under-charges the capacity peak (R4 D2-01 smooth_topk precedent P3)'),
('D3-01','#1211','I1','high','medium; verified; mutation instrument driver set is not the gate\'s'),
('D3-02','#1212','I1','high','medium; verified; out-of-range defrost duty guard untested'),
('D3-03','#1213','I1','high','medium; verified; flow_setpoint emitter-UA floor untested'),
('D3-04','#1214','I1','high','medium; verified; cheaper_hour_count non-positive-COP guard untested'),
('D3-05','#1215','I1','high','low; verified; StartCounter already-running early return untested'),
('D3-06','#1216','I1','high','medium; verified; SystemIdentification plausible-bounds refusal untested'),
('D3-07','#1217','I1','high','low; verified; 2 of 7 mutation survivors are equivalent mutants, not separated'),
('D3-08','#1218','I2','high','low; verified; deployment_shape closure 74/74, 53 script pairs share >=0.80'),
('D4-01','#1219','P9','high','medium; verified; setup click-to-assign rows 11.7-14.6 px under the 24 px floor'),
('D4-02','#1220','P9','high','low; weakened; picker .sp-filter 23.19 px, absent from htmlTargetFloor'),
('D4-03','#1221','I5','high','low; verified; card sv missing stats.delta_detail_same (R8 D4-s2-01 untranslated-sv precedent I5)'),
('D5-01','#1222','I5','high','low; verified; platform docstrings undercount entity rosters by 7'),
('D5-02','#1223','I5','high','low; verified; __init__ "40 modules" note stale (45)'),
('D5-03','#1224','I5','high','low; weakened; README/architecture.md mermaid diagrams drifted by one node + edge'),
('D7-01','#1225','I1','high','low; verified; mutation gate default driver list omits the module\'s own test (false survivor)'),
('D8-01','#1226','P6','high','medium; verified; Sensor-Gap Advisor _gaps() gets only peak inputs, two slots pinned 0.00 (R7 D8-01 precedent P6)'),
('D8-02','#1227','N-name-sort','high','low; verified; entity-id sort splits Cost/Plan/Learning/Optimization into 13 runs; the root-cause seat\'s known miss; R5 run-B D8-01 (#1333) re-measures its rename'),
('D8-03','#1228','P8','med','low; verified; "Euro" advisor names hardcode Euro while the unit is coordinator.currency'),
('D9-01','#1229','I1','high','low; weakened; stress gate work meter misses single-scenario cost-only regressions (N-cpu-gate-blind->I1)'),
('D9-02','#1230','N-solve-recompute','high','low; weakened; _apply_dhw_min_run re-simulates the whole horizon per weak slot, O(n^2)'),
('D11-01','#1231','I3','high','critical; verified; hpo-stamp deploy key bypass "always" skips all 4 main-protect rules'),
('D11-02','#1232','I3','med','high; verified; ruleset reader returns byte-identical output with/without rule+bypass changes (governance detector blind)'),
('D11-03','#1233','I3','high','high; verified; reviewer != author not enforced'),
('D11-04','#1234','I3','high','high; verified; record refusal carries continue-on-error, undispositioned merges stay green'),
('D11-05','#1235','I3','med','medium; verified; PR template violates the body contract but the arm pushes to found[] not rc, stays green'),
('D11-06','#1236','I3','med','medium; verified; dismiss_stale_reviews_on_push=false contradicts decision 0008 (R4 D11-04 live-vs-tree precedent I3; alt I5)'),
('D12-01','#1237','P2','high','low; verified; no-DHW plant still publishes dhw_windows/dhw_min_temperature (is-configured gate missing at a sibling, R5 D12-01 precedent)'),
('D13-01','#1238','I4','med','medium; verified; friction histogram top row is PR trailers, not friction'),
('D13-02','#1239','I4','high','medium; verified; 16 of 30 blocked verdicts outside the wave grammar'),
('D13-03','#1240','I4','high','medium; verified; verdict histogram emits one key, its note says otherwise'),
('D13-04','#1241','I4','med','low; verified; carried GOV set understates governance cost by 7 %'),
]
for fid,iss,cls,conf,n in r5:
    add('R5',fid+'@eaa2a06',iss,cls,conf,'gh:'+iss,n+'; '+A+'issue body states judge verdict')
# ---- R6 ----
add('R6','D0-01','#1377','P4','high',R+':1251','medium->low; space solve refines only its four pre-scored candidates; bang-bang seeds lower objective median 0.0615 % (objective-only; the deferred R5 #1294 change); judge table L1359 v/w/w weakened low')
# ---- R7 ----
add('R7','D2-03','#1487','P3','med','gh:#1487','low; _dhw_coil_wood_forecast still floors wood capacity with max(...,0.01): sibling seam of R7 D2-01 (#1450, P3); found_by=fixer (round-7 thermal_model fixer step-8 enumeration), not panel-judged; labels round-7, fixed PR #1556',kind='sweep')
hdr=['round','finding_id','issue','class_id','r9_alias','kind','confidence','source','note']
with open('/tmp/claude-0/-home-user-heatpump-optimizer/1b5fa08f-9bd8-59e8-b197-ffb291fc579e/scratchpad/phaseA/a1b/missing_rows.tsv','w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n'); w.writerow(hdr); w.writerows(rows)
from collections import Counter
print(len(rows)); print(Counter(r[0] for r in rows)); print(sorted(Counter(r[3] for r in rows).items(),key=lambda x:-x[1])); print(Counter(r[6] for r in rows))
