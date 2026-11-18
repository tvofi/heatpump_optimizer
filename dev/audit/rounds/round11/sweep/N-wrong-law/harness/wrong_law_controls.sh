#!/usr/bin/env bash
# Controls for wrong_law.py. positive: the D2-s2-02 planted sign (`1.0 + duty`)
# in a copy of defrost.py is listed PINNED. null: a clean fixture of correctly
# signed clamped laws -> pinned 0. perturbation: one sign flipped at
# dhw_planner.py:105 (_tank_decay) in a copy -> pinned +1.
set -u
D=$(dirname "$0"); EN="python3 $D/wrong_law.py"; P=custom_components/heatpump_optimizer
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
echo "tree: $($EN | tail -1)"
cp -r $P "$T/plant"; sed -i 's/1.0 - duty \* DEFROST_LOSS_MULTIPLIER/1.0 + duty * DEFROST_LOSS_MULTIPLIER/' "$T/plant/defrost.py"
echo "positive (planted D2-s2-02): $($EN "$T/plant" | grep -c '^PINNED .*defrost.py:205') pinned at defrost.py:205; $($EN "$T/plant" | tail -1)"
mkdir -p "$T/clean"; printf 'K = 1.5\nLO = 0.5\nHI = 1.0\ndef f(d):\n    return min(HI, max(LO, 1.0 - d * K))\ndef g(x):\n    return max(0.0, 1.0 - x / 3.0)\n' > "$T/clean/a.py"
echo "null: $($EN "$T/clean" | tail -1)"
cp -r $P "$T/pert"; sed -i 's|np.clip(1.0 - ua \* dt / c_dhw, 0.0, 1.0)|np.clip(1.0 + ua * dt / c_dhw, 0.0, 1.0)|' "$T/pert/dhw_planner.py"
echo "perturb (dhw_planner.py:105 sign flipped): $($EN | tail -1) -> $($EN "$T/pert" | tail -1)"
