"""Edges the re-chain proposal drops (shared by simulate.py and gen_plan.py)."""
HOT_ONLY = {('R10-RATIO-ANCHOR', 'R10-NIGHT-FOLDS'), ('R10-INPUT-STALENESS', 'R10-RATIO-ANCHOR'),
            ('R10-CURRENCY', 'R10-INPUT-STALENESS'), ('R10-LOOP-CPU', 'R10-FREQ-DEFROST'),
            ('R10-SCORES', 'R10-ADVISOR'), ('R10-CONFIG-NOTICES', 'R10-LIVESTATE'),
            ('R10-LEARNER-ETA', 'R10-ARCH-SHAPES'), ('R10-HEAT-METER', 'R10-LEARNER-ETA'),
            ('R10-HEAT-METER', 'R10-RATIO-ANCHOR'), ('R10-ARCH-SHAPES', 'R10-FREQ-DEFROST')}
