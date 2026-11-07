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

