#!/bin/bash
# plant.sh <wt> <scratch>: copy the package per plant, apply junk to silent_mode.py, measure layering.
set -u
WT=$1; S=$2; P=custom_components/heatpump_optimizer
OLD='from .optimizer import _utc_step_starts'
mk() { rm -rf $S/plants/$1; mkdir -p $S/plants/$1/custom_components; cp -R $WT/$P $S/plants/$1/$P; echo $S/plants/$1/$P/silent_mode.py; }
sub() { python3 - "$1" "$2" "$3" <<'PY'
import sys; p, old, new = sys.argv[1:]; s = open(p).read(); assert old in s, old; open(p, "w").write(s.replace(old, new, 1))
PY
}
f=$(mk p0_none); python3 $S/lay2.py $WT $S/plants/p0_none p0_none
f=$(mk p1_tc_else); sub $f "$OLD" $'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    pass\nelse:\n    from .optimizer import _utc_step_starts'; python3 $S/lay2.py $WT $S/plants/p1_tc_else p1_tc_else
f=$(mk p2_not_tc); sub $f "$OLD" $'from typing import TYPE_CHECKING\nif not TYPE_CHECKING:\n    from .optimizer import _utc_step_starts'; python3 $S/lay2.py $WT $S/plants/p2_not_tc p2_not_tc
f=$(mk p3_import_module_const); sub $f "$OLD" $'import importlib\n_utc_step_starts = importlib.import_module(".optimizer", __package__)._utc_step_starts'; python3 $S/lay2.py $WT $S/plants/p3_import_module_const p3_import_module_const
f=$(mk p4_absolute); sub $f "$OLD" 'from custom_components.heatpump_optimizer.optimizer import _utc_step_starts'; python3 $S/lay2.py $WT $S/plants/p4_absolute p4_absolute
f=$(mk p5_junk_read_scipy); sub $f "$OLD" $'from .optimizer import _utc_step_starts\nimport scipy\nassert scipy'; python3 $S/lay2.py $WT $S/plants/p5_junk_read_scipy p5_junk_read_scipy
f=$(mk p5b_unread_scipy); sub $f "$OLD" $'from .optimizer import _utc_step_starts\nimport scipy'; python3 $S/lay2.py $WT $S/plants/p5b_unread_scipy p5b_unread_scipy
f=$(mk p6_getattr_concat); sub $f "$OLD" $'from . import optimizer as _o\n_utc_step_starts = getattr(_o, "_utc" + "_step_starts")'; python3 $S/lay2.py $WT $S/plants/p6_getattr_concat p6_getattr_concat
f=$(mk p7_vars); sub $f "$OLD" $'from . import optimizer as _o\n_utc_step_starts = vars(_o)["_utc_step_starts"]'; python3 $S/lay2.py $WT $S/plants/p7_vars p7_vars
f=$(mk p8_rebind); sub $f "$OLD" $'from . import optimizer as _o\n_m = _o\n_utc_step_starts = _m._utc_step_starts'; python3 $S/lay2.py $WT $S/plants/p8_rebind p8_rebind
f=$(mk p9_lazy); sub $f "$OLD" ''; sub $f 'def ' $'def _lazy_probe():\n    from .optimizer import _utc_step_starts\n    return _utc_step_starts\n\n\ndef '; python3 $S/lay2.py $WT $S/plants/p9_lazy p9_lazy_control
f=$(mk p10_tc_only); sub $f "$OLD" $'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from .optimizer import _utc_step_starts'; python3 $S/lay2.py $WT $S/plants/p10_tc_only p10_tc_only_control
