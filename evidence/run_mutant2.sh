#!/usr/bin/env bash
# rev3805-delta: commit-stage check, head control and ship-first mutant.
set -u
W=/Users/timmalmstrom/hpo-seats/r11/rev3805-delta
EV=/Users/timmalmstrom/hpo-seats/r11/rev3805-delta-ev
cd "$W"
DRV=tests/_rev3805_dsp_driver.py
{ sed -n '1,107p' tests/features.py; sed -n '92524,94276p' tests/features.py; echo 'sys.exit(R.close("REV3805 DSP"))'; } > "$DRV"
python3 tests/gate_lock.py slot-take --label rev3805-delta --owner-pid $$ || exit 70
trap 'python3 tests/gate_lock.py slot-release --label rev3805-delta; git -C "$W" checkout -- custom_components/heatpump_optimizer/optimizer.py; rm -f "$W/$DRV"' EXIT
python3 - <<'EOF'
import re
p = "custom_components/heatpump_optimizer/optimizer.py"
s = open(p).read()
old = "        ), key=lambda c: c[0])[1:]\n    except Exception as err:  # noqa: BLE001 - the stage is optional: the projection ships"
assert s.count(old) == 1, "anchor"
s = s.replace("        return min((\n            _best_runs(", "        return [\n            _best_runs(", 1)
s = s.replace(old, "        ][0][1:]\n    except Exception as err:  # noqa: BLE001 - the stage is optional: the projection ships", 1)
open(p, "w").write(s)
EOF
git diff --stat; git diff custom_components/heatpump_optimizer/optimizer.py > "$EV/mutant2.diff"
echo "== mutant (commit every descent, ship the first)"
PYTHONPATH=tests/hastub python3 "$DRV" > "$EV/mutant2.log" 2>&1; echo "mutant rc=$?"
