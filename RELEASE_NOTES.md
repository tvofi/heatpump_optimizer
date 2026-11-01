## v7.1.1

**Patch stamp: 100 merges since v7.1.0.** Users were waiting on a set of fixes: a factory reset, the ceiling probe, and a run of away-mode and learner corrections. The rest of the window is the round-10 engineering and audit machinery.

User-visible changes:

- Factory reset: the integration can be reset to a clean state (#3047).
- Ceiling probe: the heat-pump ceiling is probed instead of assumed (#3050).
- Away presence: the plan is recomputed when presence or the holiday calendar changes (#3052).
- Away setback: weekend and holiday comfort no longer override the away setback (#3013), and the away override survives an entry reload and the restore (#3015).
- Learner inputs: a sensor swap voids the heat-loss learners, and a reset action is added (#3022).
- Vent freeze skips only the learners room air cannot reach (#3009).
- Step-boundary actuation: the pump switch is written at the step boundary (#2968).
- COP: compressor part-load inverse conversions and residual carries (#3006, #3005), COP gate part 6 (#3038).
- Wood: the blueprint notifies when wood beats the heat pump, with a recommended lighting window (#3016).
- Health tab residual carries (#2997).
- README figures render on the Marketplace page, light and dark (#3014); final user docs (#3048).

Engineering and audit programme (round 10):

- Audited fix groups and instruments (39): #2925, #2962, #2989, #2992, #2994, #2995, #3000, #3001, #3002, #3004, #3010, #3011, #3012, #3024, #3037, #3041, #3042, #3045, #3049, #3051, #3056, #3058, #3059, #3060, #3061, #3063, #3064, #3066, #3070, #3072, #3073, #3075, #3076, #3086, #3092, #3097, #3118.
- Triage rulings (33): #2987, #3003, #3007, #3017, #3018, #3019, #3020, #3023, #3025, #3026, #3027, #3029, #3030, #3031, #3033, #3034, #3035, #3036, #3039, #3043, #3046, #3053, #3067, #3068, #3069, #3079, #3080, #3082, #3084, #3095, #3096, #3141, #3142.
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

