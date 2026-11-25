# Deviations from the plan, 2026-11-25

Recorded under `orchestrator.md` section 2b. No file in this directory records
deviations (`CHANGES-R3.md` and `CHANGES-R4.md` record plan revisions), so this
file is new and follows the table shape of `CHANGES-R4.md`. Revision 4 and its
rows stand for everything not named here.

| deviation | before | after | reason |
|---|---|---|---|
| (a) new CI groups for #3885 | no CI group on the plan | a second critical path: dynamic fast-lane sharding (2 to 4 shards) and the CI queue design (`design/r11-ci-3885-queue`) | tvofi's ruling of 2026-11-25 |
| (b) CI-5 dropped | CI-5, the CI-main concurrency group in `ci.yml`, planned | dropped; handoff branch `handoff/r11-ci-3885-ci5-drop` | tvofi, 2026-11-25: the superseded-main cancel makes it obsolete |
| (c) hold on all groups except critical path, CI and outside | all ready groups dispatch | held: R11 `late-p1-options`, `late-p2-replay-finite`, `seam-tests` and `seam-wallclock-dst`; critical path, CI and outside groups continue | tvofi's ruling of 2026-11-25 |
| (d) `R11-OUTSIDE-SELF-SETTING-PUMP` routed to a designer first | straight to a fixer | designer first, then design review, then the fixer | decision 0014 requires design before build for an outside feature |
