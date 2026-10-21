"""The re-chain as the R10-FLOW-RECHAIN decision seat ruled it (2026-10-21, at roster 2c76c3128,
main 5d433771a): 15 coordinator.py edges examined, 8 dropped, 7 kept, 3 required and 4 recommended
edges added. Shared by simulate.py and gen_plan.py. K7's first proposal (10 drops) was wrong on 4."""
HOT_ONLY = {  # dropped: (later, earlier)
    ('R10-RATIO-ANCHOR', 'R10-NIGHT-FOLDS'), ('R10-INPUT-STALENESS', 'R10-RATIO-ANCHOR'),
    ('R10-CURRENCY', 'R10-INPUT-STALENESS'), ('R10-LOOP-CPU', 'R10-FREQ-DEFROST'),
    ('R10-CONFIG-NOTICES', 'R10-LIVESTATE'), ('R10-PARAMS-OWNER', 'R10-CONFIG-NOTICES'),
    ('R10-ARCH-SHAPES', 'R10-PARAMS-OWNER'), ('R10-LEARNER-ETA', 'R10-ARCH-SHAPES'),
}
REQUIRED = {  # later: [earlier, ...] -- must land in the same burst as the drops
    'R10-PARAMS-OWNER': ['R10-LIVESTATE'], 'R10-ARCH-SHAPES': ['R10-LIVESTATE'],
    'R10-HEAT-METER': ['R10-PARAMS-OWNER', 'R10-ARCH-SHAPES'],
}
RECOMMENDED = {  # 0 depth each: overlapping pairs already unordered today
    'R10-LIVESTATE': ['R10-LOOP-CPU'], 'R10-LOOP-CPU': ['R10-NIGHT-FOLDS'],
    'R10-PARAMS-OWNER': ['R10-NIGHT-FOLDS', 'R10-RATIO-ANCHOR'], 'R10-ARCH-SHAPES': ['R10-INPUT-STALENESS'],
}
STUDY_ADD = {  # this study's addition, outside the seat's mandate: 0 depth (HEAT-METER waits on depth 4)
    'R10-HEAT-METER': ['R10-THERMAL-POWER-OPTION'],
}
def added(n, recommended=True, study=True):
    out = list(REQUIRED.get(n, []))
    if recommended: out += RECOMMENDED.get(n, [])
    if study: out += STUDY_ADD.get(n, [])
    return out
