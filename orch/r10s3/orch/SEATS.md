# Session-3 seat ledger (orchestrator scratch; volatile)
tick        haiku   a6578fe0b8ea67c95  loop, returns on new -> lines / heartbeat
survey      sonnet  ac56abebde81f5f14  read-only reconciliation REPORT.md
replan      Plan    a3fee6edb0929e8f3  edge classification
judge-d2    opus    a5a5ef7c07df66064  PUMP-MODEL D2-s2-01 ruling
vent        opus    a57cb0b03f8a63d10  R10-VENT-DETECTOR fixer, topic r10-vent-detector
i5docs      sonnet  ada2b83df515efc15  R10-I5-DOCS fixer, topic r10-i5-docs
archp4      opus    a4e2e94ad0107f3f2  ARCHSCORE p4/p5, topics r10-archscore-coverage-p4/-p5
refpriv     opus    a6f68486bbe7471cb  REF-PRIVACY remainder, topic r10-ref-privacy-2
census      opus    a6d4d05787e445d28  #2345 resume, topic r10-deeplink-census
nlog        opus    a9c312bf3c84b975a  #2351 resume, topic r10-n-log-flood
pump        opus    aaf06e1088d561678  PUMP-MODEL merge main, topic r10-pump-model
PRs: #2356 roster (fix/audit-r10-roster) -> approve tvofi + merge when green
Daemons: beat pid 25448, wtsync pid 25458 (logs in r10s3/)
leaf        opus    aff577d3188e4e69e  R10-LEAF-IMPORTS, topic r10-leaf-imports (merge first)
savbase     opus    aa6cf87afcc5fca0b  R10-SAV-BASELINE, topic r10-sav-baseline
ratioanch   opus    a7ed6c18cec858fff  R10-RATIO-ANCHOR, topic r10-ratio-anchor
store       opus    aa71913905ac0d052  R10-STORE, topic r10-store
sensorpay   opus    ad4e12bd7dc46a399  R10-SENSOR-PAYLOAD, topic r10-sensor-payload
tickorch    sonnet  ad5a9e123f6983dc8  R10-TICK-ORCH a,c, topic r10-tick-orch-2
d15         opus    a44a014a8c5e34c1e  R10-D15-GRADER, topic r10-d15-grader
trainhold   sonnet  a417c18750693d835  R10-TRAIN-HOLD resume (/private/tmp/r10-train-hold/wt), topic r10-train-hold
rosterafter sonnet  add15e8237dff175f  roster_edit set-after op, topic r10-roster-set-after
rcafric     opus    a8209d4ea54f9b5c3  RCA #2331/#2353, topic r10-rca-harness-friction
stranded    opus    a41a26114dfe37374  coverage-cache, rca-prepr-bounce, earlycutoff, arch-doc, dev-onboard
DONE: survey (REPORT.md), replan (REPLAN-EDGES.json), judge-d2 (ruling #201 6240984157)
Closed: #2270 #2254 #2304 #2307 #2350. Owed: #2337 roster group append; #2356 merge when CodeQL done.
OWED roster group R10-ARCH-DOCS (owner ruling 2026-10-17): LAST stage, after every other group. Two deliverables:
  (1) docs/architecture.md — the architecture, clearly, graphically (diagrams) and in words; seed: fix/r10-arch-doc 4305cd109 (/private/tmp/r10-arch-doc)
  (2) dev README/onboarding — graphically and in words: the agentic coding process and its requirements, the CI shape and its requirements; seed: fix/r10-dev-onboard 0edd7fa66 (/private/tmp/r10-dev-onboard)
  Append via roster_edit append-group with after = all other open groups once set-after lands; brief: every claim checked against the tree at its merge base (D5/D6 standard); diagrams render on GitHub (mermaid).
  R10-ARCH-DOCS diagram identity (owner, 2026-10-17): diagrams in the integration's design identity = the card's tokens, typography, chips and table styles (as Plan/Savings/Advisor/Health/Setup; source: the card's CSS custom properties in the card JS). Read the token values from the tree at merge base, never hand-copied. Preferred: mermaid with an init/themeVariables block mapped from those tokens (renders on GitHub), or committed SVGs generated from the tokens by a script in-tree (so they regenerate when tokens change); check both light and dark rendering. Brief to cite the token source path.
  CORRECTION (owner 2026-10-17): the visual language is what the live repo defines on origin/main at the stage's merge base — not a copy: docs/img/brand/*.svg (mark, tile, lockups, light+dark), docs/site/docs.css and docs/index.html (the published site), brand/ icons, and the card's CSS tokens. The seat derives palette/typography from those files and cites them; diagrams match the published site in light and dark.
