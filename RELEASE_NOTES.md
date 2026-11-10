## v7.1.9

**Patch stamp: 38 merges since v7.1.8, stamped early so outside users can try the water set-point fix.** The user-visible changes are the water set-point lift and ceiling options, the part-load and savings-meter fixes, and the COP gate. The rest of the window is round-10 tooling and audit machinery.

### #3372 Water set-point lift and ceiling (R10-WATER-SETPOINT-LIFT)

Adopts outside pull request #3356 by Bankaifan, with thanks. When Pump duty control is set to Control and the space set-point is a water temperature, the Sensors and entities page now offers two options: the modulation floor's lift over the measured inlet, and the full-power flow ceiling. The space set-point unit can now also be `return`, for a controller that takes the number as its return-water target. A stored ceiling at or below 25 °C, which only a hand-edited entry can produce, now reads as 55 °C instead of switching heating off.

### Product fixes

- #3291 Part-load residue (R10-PARTLOAD-RESIDUE).
- #3360 Savings-meter floor (R10-SAV-METER-FLOOR).
- #3347 Savings comfort, part 4 (R10-SAV-COMFORT).
- #3371 COP gate, part E (R10-COP-GATE-E).
- #3346 "Why now" widget, part 2 (R10-WHY-NOW-WIDGET).

### Developer tooling, CI and audit machinery only

#3349, #3348, #3367, #3337, #3339, #3315, #3305, #3343, #3327, #3326, #3330, #3310, #3338, #3363 (closes #3283), #3325, #3342, #3344, #3336, #3317, #3340, #3333, #3318: round-10 hotfixes and tooling, which include one BLAS controller per process, the gate-busy deferral, per-leg CodeQL timeouts, roster read and write sweeps, the relay sweep and the body contract. #3353, #3354, #3352, #3334, #3362, #3316: root-cause records. #3319: the round playbook (R10-ROUND-PLAYBOOK). #3373, #3370, #3357: delivery-status rows (record only).

## v7.1.8

**Patch stamp: 6 merges since v7.1.7.** The user-visible change is that the heat-pump plan now respects the "Heat pump min power" setting. The rest of the window is round-10 tooling and audit machinery.

### #3308 The plan respects "Heat pump min power" (R10-MIN-POWER-FLOOR)

The heat-pump plan now respects the "Heat pump min power" setting. A pump that cannot modulate is no longer planned at steps below its minimum, and a pump that also heats hot water no longer has space heating and hot water planned together above its maximum power. A new "compressor modulation" option (auto, on/off, modulating) on the thermal model page lets you declare how your pump behaves. Closes #3289.

### #3294 Standing contracts for the orchestrator's sessions, part 2 (R10-FLY-STANDING-CONTRACTS)

The hooks that the orchestrator's sessions depend on are now tracked, described and installable, including a guard on the orchestrator's shell commands. Developer tooling only.

### #3320 Suite host determinism, part 2 (R10-SUITE-HOST-DETERMINISM)

The entity test script gives the same answer on any host. Test tooling only.

### #3335 Root-cause record for the stamp flush cost (R10-RCA-STAMP-FLUSH-COST)

Records that the existing root-cause note on stamps dispatching a whole Nightly run already covers the owner's ruling. No code changed.

### #3324 Closeout instruments (R10-CLOSEOUT-INSTRUMENTS)

The instruments for closing out an audit round: worktree collection, closeout exemptions and tag pruning. Developer tooling only.

### #3328 Delivery rows recorded (autofix)

Delivery-status rows for #3262, #3288, #3301, #3311 and #3312. Record only.

## v7.1.7

**Patch stamp: 5 merges since v7.1.6.** The user-visible change is that the round's plan page is now public: the developer documentation links it, and outside contributors have a stated intake route. The rest of the window is round-10 engineering and audit machinery.

### #3262 The round's plan page is public (R10-OUTSIDE-INTAKE)

The plan page for an ongoing audit round is now published from the developer documentation (owner ruling, 2026-11-06). The same change states how issues, pull requests and posts from outside users are taken in and answered during a round.

### #3301 CI's prediction covers every restoring job (R10-FLY-CIPREDICT-RESTORING)

`tools/pr/ci_predict.py` now predicts every CI job that restores a grader from the base, not only governance's three. A prediction no longer misses a red those jobs would raise. Closes #2952.

### #3288 The merge train retries its carry-path fetch (R10-TRAIN-MERGE-LOOP part 2)

The merge loop's second part: the approval carry path retries a failed `git fetch` instead of refusing on the first transient error.

### #3312 The figure block is registered with the field-coverage grader (R10-BODY-CONTRACT part 3 bootstrap)

`tools/pr/figure_block.py` is registered as pending in main's field-coverage registry, so the body-contract work that builds on it can pass the grader CI restores from the base.

### #3311 The "other" friction family is disposed (R10-FRICTION-OTHER-FAMILY)

The record of the friction family that matched no class: mostly spelling dispersion, and one taught obligation that three pull requests had missed. It lands as `dev/audit/rca/R10-RCA-OTHER-UNTAUGHT.md`.

## v7.1.6

**Patch stamp: 27 merges since v7.1.5.** The user-visible changes are a live "Why now" explanation on the card, a saving that says when it includes wood heat, a buffer tank that no longer starts every solve from a fixed 40 °C, and inputs that come back as soon as their entity reports again. The rest of the window is round-10 engineering and audit machinery.

### #3274 Why now widget (R10-WHY-NOW-WIDGET)

The solver now publishes five signed drivers for each step: price rank, comfort floor, mold guard, away and forecast. Each is a percent of that step's push. The space-plan sensor publishes the current step's drivers as `why_now`, and the card shows them after the headline, in English and Swedish. They are computed in a new pure module, `slot_drivers.py`.

### #3244 The monthly saving says it includes wood heat (R10-HOTFIX-SAV-ESTIMATE part 2)

Wherever wood is configured, the saving now states that it includes wood's heat and excludes the cost of firewood (owner ruling, 2026-11-04). The receipt event, the `MonthlySavingsSensor` attribute `saving_includes_wood`, the card's receipt and savings table, and the notification blueprint all read one definition. The CodeQL autoescape alert on its render harness is fixed at the root.

### #3268 Buffer tank seeded without a probe (R10-COMBI-TANK PR 0)

Without a buffer probe, the buffer temperature never advanced. Every solve started from the 40 °C default or a stale value. It is now seeded from the previous plan's trajectory, the way the DHW tank already was. The rise inputs used for external-heat detection read only measured values, so a planned rise is no longer counted as evidence of external heat.

### #3300 A missing input is re-read when its entity returns (R10-INPUT-REAPPEAR)

This adopts the outside pull request #3292 from @Bankaifan. When the cycle finds a configured input missing or unavailable, it is now re-read as soon as its entity reports a value, instead of one optimisation interval later.

### #3273 One owner for each clone-class fact (R10-CLONE-2238)

The remaining #2238 clone-class instances (one fact decided twice) now each have a single owner in the module that held both copies, and every other copy calls it. Examples are the planned space/DHW split, the fabric-loss residual refusal and the indoor-sensor trajectory.

### #3307 Session-start hook self-test pins its clock (R10-HOTFIX-MAIN-IST-RED)

Main's `instrument-self-tests` job went red when git's relative clock ticked between two reports that the self-test compares byte for byte. The self-test now pins `GIT_TEST_DATE_NOW`. The hook's normal output is unchanged.

### #3295 Root-cause record for the ci-red friction key (R10-FRICTION-CI-RED)

The record behind the recurring-friction key `ci-red` (#3156). It names each of the 18 entries' PR and red check, and finds that one verdict word covers four mechanisms. It also re-files #3219 from group A to group D.

### #3264 Plan-model correctness and the Gantt-drift instrument (R10-FLOW-TOOLKIT-MODEL)

`tools/plan/replan.py` now prices only pending carries as open work. The Gantt-drift instrument is now tracked in the tree.

### #3296 The stamp's record flush dispatches only the beat (R10-FLY-STAMP-FLUSH-COST)

`nightly.yml` gains a `lanes` input (all or beat), and the stamp's record flush posts `lanes=beat`, so it no longer runs every nightly lane. Rules 4 and 5 now read one window.

### #3302 Each PR's own delivery row no longer counts as non-product (R10-CI-OWN-DELIVERY-ROW)

CI-throughput lever 2. A pull request's own delivery row no longer stops the machinery lanes from standing down on an all-product change. A strace recording measures which lanes actually read a row.

### #3290 The merge train waits for a deferring gate (R10-HOTFIX-TRAIN-DEFER-WAIT)

CI-throughput lever 1. The train no longer treats an edit run's deferring red gate as final while the head's code run is still running.

### #3287 A deferring gate publishes at once and the sweep settles it (R10-HOTFIX-GATE-BUSY-DEFER, part 3)

A deferring gate no longer holds a runner. `gate-sweep.yml` re-runs it once the deciding run completes. A new `settle` branch covers gates that deferred to each other and deciders that ended red or cancelled.

### #3278 Root cause of the busy gate deferral (R10-RCA-GATE-BUSY-DEFER-2)

The root-cause record beside the gate-deferral fix. Re-runs replayed a pre-fix `gate.py` restored from the payload's base SHA. The record also reclassifies #3263's edit/code-run red as a defect, the one #3276 fixed.

### #3277 Whole-run cancels at live heads (R10-RCA-LIVEHEAD-CANCEL)

The root-cause record, detector and bug class for whole-run cancels at live heads. They were operator cancels under the owner credential, not CI machinery.

### #3285 Root cause of the record flush dispatching all of Nightly (R10-RCA-FLUSH-DISPATCH)

The record, harness and class `N-dispatch-overreach`. The flush treated a job as the unit of dispatch, but the API dispatches a whole workflow.

### #3280 The record flush honours a train hold (R10-FLY-STAMP-FLUSH-HOLD)

`stamp.py` no longer spends its flush dispatches under a live `train-hold`. `merge_train.py` keeps the hold DELETE from being skipped by a second signal during the unwind.

### #3275 Instrument self-tests run detached (R10-HOTFIX-SELFTEST-TIMEOUT)

The five slow self-tests in `instrument-self-tests` now start detached at the beginning of the job, so the job takes as long as the longer of the two parts instead of their sum. The 30-minute timeout is not raised.

### #3269 Nightly pins per night (R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT)

Mutation-ledger runs are now seeded by run id, so two runs on one date no longer draw the same slice. Two more changes, each tied to a measured line of the 06 Nov breakdown, raise the number of pins per night.

### #3265 Plan page lanes (R10-HOTFIX-PLAN-LANES)

`roster_lane` now places a group by the files it owns, so instrument, CI and record groups are no longer drawn in the core-model lane.

### #3267 Sweep template sync (R10-SWEEP-TEMPLATE-SYNC)

The 11-06 sweep changes made outside the tree are folded into the tracked sweep instruments, and the template declares the overlay keys its rows read.

### #3252 Relay residue (R10-RELAY-SWEEP)

The residue in `cloud_relay.sh` is fixed on one owning seam (carries 0-9).

### #3293 Handoff path, part 2 (R10-HANDOFF-PATH)

`pr_args.sh` resolves its own directory once, when it is sourced. `open_driver.py` gains a stem escape, a guarded log read and a STUCK line after three tries.

### #3272 Triage batch 128

P399, cloud fires without sources, is accepted, narrowed to R10-POLICY-ROLE-PACK.

### #3286, #3298, #3306, #3309 Delivery rows (autofix)

Record-class merges that write the delivery rows: #3286 for #3244 and #3277; #3298 for #3252, #3265, #3272, #3273, #3278, #3280, #3285 and #3287; #3306 for #3267, #3268, #3269, #3275 and #3293; #3309 for #3264, #3274, #3290, #3295, #3296, #3300, #3302 and #3307.


## v7.1.5

**Patch stamp: 23 merges since v7.1.4.** One user-visible fix: the optimiser no longer hangs when its worker process goes silent.

Stamped with --allow-red before main's gate completed, on the owner's standing order to stamp without waiting for main CI.

User-visible:

- #3232 (outside contribution from @Bankaifan, adopted from #3226): the coordinator's process worker reply wait is now bounded, and the stop path no longer holds the worker lock indefinitely, so a silent worker cannot hang optimisation or Home Assistant shutdown.

Engineering and audit programme (round 10):

- Audited fix groups and instruments (15): #3250 (roster-reader predicates, carries 1-4), #3251 (ref privacy for cloud seats), #3259 (gate stale-jobs carries, part 2), #3260 (body-contract carries, part 2), #3249 (dispatch at handoff), #3241 (carry residue), #3276 (an edit gate no longer defers to a code run it cannot see conclude), #3263 (nightly-status hotfix), #3234 (replay cost budget, round 2), #3242 (train merge loop), #3246 (one concurrent gate run decides at a head), #3248 (obligations ledger residue), #3253 (roster write path residue), #3255 (friction records), #3256 (policy role pack).
- Brief carries (2): #3247 (D0 brief: stop-tolerance refusal and DHW cert-cell gap), #3261 (D1 brief: the process-worker hang root cause).
- Roster and record merges (5): #3258 (round-10 roster and triage rulings), #3270 (delivery rows, autofix), #3271 (triage batch 127, P393 to P398), #3279 (delivery rows for #3232, #3246, #3255, #3263, autofix), #3281 (delivery rows for #3241, #3249, #3250, #3251, #3259, #3261, #3271, #3276, autofix).

- Delivery record: the rows the stamp flushed before tagging (#3282).

## v7.1.4

**Patch stamp: 10 merges since v7.1.3.** No user-visible change. The window is release and audit machinery.

Stamped with --allow-red before main's gate completed, on the owner's standing order to stamp without waiting for main CI.

Engineering and audit programme (round 10):

- Audited fix groups and instruments (3): #3236 (the stamp bumps from the highest release tag), #3243 (gate lease TOCTOU), #3240 (planted-defect audit).
- Triage rulings (3): #3212, #3237, #3238.
- Roster and record merges (4): #3239 (round-10 roster and triage rulings), #3235, #3254 and #3257 (delivery rows, autofix).

- Delivery record: the rows the stamp flushed before tagging (#3254).

- Delivery record: the rows the stamp flushed before tagging (#3257).

## v7.1.3

**Patch stamp: 84 merges since v7.1.1.** v7.1.2 was never stamped, so this window opens at v7.1.1 and carries v7.1.2's contents. The user-visible part is the savings estimate and a handful of pricing and learner fixes, plus a contributed DHW set-point input. The rest of the window is the round-10 engineering and audit machinery.

User-visible changes:

- Savings: the month row settles stored heat (#3195), and settles against the meter (#3220).
- DHW set-point: a water_heater entity is accepted as the set-point input (#3231, outside contribution).
- Compressor part-load pricing (#3182), COP gate part D (#3193).
- Overbook residual (#3183), two-zone heat-loss (#3196), learned-store load (#3185).

Engineering and audit programme (round 10):

- Audited fix groups and instruments (52): #3054, #3055, #3065, #3077, #3078, #3085, #3089, #3090, #3147, #3149, #3150, #3151, #3153, #3160, #3163, #3164, #3165, #3167, #3168, #3169, #3170, #3173, #3174, #3175, #3179, #3180, #3181, #3184, #3186, #3189, #3191, #3192, #3194, #3197, #3198, #3199, #3200, #3201, #3205, #3206, #3208, #3216, #3217, #3218, #3219, #3221, #3222, #3223, #3227, #3228, #3229, #3230.
- Triage rulings (16): #3154, #3157, #3158, #3159, #3161, #3171, #3172, #3177, #3202, #3203, #3204, #3209, #3210, #3211, #3213, #3214.
- Record and bot merges (8): #3091, #3155, #3162, #3176, #3178, #3207, #3215, #3233.

## v7.1.2

**Unstamped release.** v7.1.2 was a hand tag of b8e82369, published 2026-11-02, never stamped: its manifest and VERSION read 7.1.1. Its contents are included in v7.1.3.

## v7.1.1

**Patch stamp: 107 merges since v7.1.0.** Users were waiting on a set of fixes: a factory reset, the ceiling probe, and a run of away-mode and learner corrections. The rest of the window is the round-10 engineering and audit machinery.

User-visible changes:

- SAV comfort: the duty ledger's run fold settles one tick into each step (#3145).
- Factory reset: the integration can be reset to a clean state (#3047).
- Ceiling probe: the heat-pump ceiling is probed instead of assumed (#3050).
- Away presence: the plan is recomputed when presence or the holiday calendar changes (#3052).
- Away setback: weekend and holiday comfort no longer override the away setback (#3013), and the away override survives an entry reload and the restore (#3015).
- Learner inputs: a sensor swap voids the heat-loss learners, and a reset action is added (#3022).
- Vent freeze skips only the learners room air cannot reach (#3009).
- Step-boundary actuation: the pump switch is written at the step boundary (#2968).
- COP: compressor part-load inverse conversions and residual carries (#3006, #3005), COP gate part 6 (#3038).
- Wood: the blueprint notifies when wood beats the heat pump, with a recommended lighting window (#3016).
- Health tab: no-meter heat-loss bar and history-free strings (#3062), residual carries (#2997).
- README figures render on the Marketplace page, light and dark (#3014); final user docs (#3048).

Engineering and audit programme (round 10):

- Audited fix groups and instruments (40): #2925, #2962, #2989, #2992, #2994, #2995, #3000, #3001, #3002, #3004, #3010, #3011, #3012, #3024, #3037, #3041, #3042, #3045, #3049, #3051, #3056, #3058, #3059, #3060, #3061, #3063, #3064, #3066, #3070, #3072, #3073, #3075, #3076, #3086, #3092, #3097, #3118, #3143.
- Triage rulings (36): #2987, #3003, #3007, #3017, #3018, #3019, #3020, #3023, #3025, #3026, #3027, #3029, #3030, #3031, #3033, #3034, #3035, #3036, #3039, #3043, #3046, #3053, #3067, #3068, #3069, #3079, #3080, #3082, #3084, #3095, #3096, #3141, #3142, #3144, #3146, #3152.
- Record and bot merges (14): #3008, #3021, #3028, #3032, #3040, #3044, #3057, #3071, #3074, #3081, #3093, #3094, #3098, #3148.

## v7.1.0

**Round-10 merge-train stamp: 98 merges since v7.0.5.** The window is the merge seat's train clearing the programme's remaining audited fix groups: the claim-carry barrier, the train's single admission rule, the COP gate and compressor part-load pricing, the Health tab and the Home Assistant Marketplace integration.

User-visible changes:

- Marketplace: the integration ships through the Home Assistant Marketplace (#2973, #2967).
- Health tab: reworked from the owner's report of 2026-10-14 (#2976).
- COP: the compressor's power is priced in COP, off by default (#2872); the COP gate's pending-prediction readers (#2917, #2975).
- Advisor what-if and the config flow pages (#2963, #2946, #2915).

Engineering and audit programme (round 10):

- Audited fix groups (50): #2973, #2975, #2978, #2872, #2976, #2977, #2955, #2917, #2969, #2961, #2964, #2971, #2967, #2954, #2959, #2953, #2963, #2960, #2956, #2957, #2939, #2949, #2948, #2946, #2933, #2947, #2896, #2935, #2936, #2915, #2887, #2919, #2916, #2937, #2913, #2938, #2912, #2930, #2920, #2923, #2918, #2910, #2873, #2909, #2905, #2883, #2894, #2876, #2853, #2897.
- Roster batches (4): #2988, #2914, #2903, #2899.
- Triage rulings (31): #2993, #2991, #2986, #2985, #2980, #2983, #2981, #2982, #2970, #2974, #2972, #2958, #2945, #2906, #2934, #2932, #2931, #2922, #2929, #2927, #2928, #2926, #2924, #2921, #2908, #2902, #2900, #2891, #2892, #2890, #2898.
- Record and bot merges (13): #2996, #2990, #2984, #2979, #2966, #2951, #2944, #2943, #2941, #2940, #2911, #2904, #2901.

- Delivery record: the rows the stamp flushed before tagging (#2996).

