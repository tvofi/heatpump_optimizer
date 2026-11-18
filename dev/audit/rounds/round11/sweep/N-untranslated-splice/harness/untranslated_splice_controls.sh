#!/usr/bin/env bash
# Controls for untranslated_splice.py: positive (re-finds the D4-s3-01 seam
# rule's sites), null (zero on a clean fixture), perturbation (+1 under a
# one-line re-introduction in a copy of the package).
set -u
D=$(dirname "$0"); EN="python3 $D/untranslated_splice.py"; P=custom_components/heatpump_optimizer
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
rule=$(grep -cE "err(\.message| && err\.message)" $P/www/heatpump-optimizer-card.js)
found=$($EN --json | python3 -c 'import json,sys;print(sum(1 for s in json.load(sys.stdin) if s["file"].endswith(".js")))')
echo "positive: seam_rule sites=$rule enumerator js seams=$found"
mkdir -p "$T/cc/clean/www"
cat > "$T/cc/clean/a.py" <<'P'
def f(entry, x):
    raise ValueError("x", translation_placeholders={"entry_id": entry.entry_id, "n": f"{x:.1f}"})
P
echo 'L("errors.could_not_apply", { name: entity.name });' > "$T/cc/clean/www/c.js"
echo "null: $($EN "$T/cc/clean" | tail -1)"
cp -r $P "$T/cc/pkg"; base=$($EN "$T/cc/pkg" | tail -1)
sed -i 's/translation_placeholders={"entry_id": entry.entry_id},/translation_placeholders={"entry_id": entry.entry_id, "error": str(err)},/' "$T/cc/pkg/debugger.py"
echo "perturb (debugger.py one line splices str(err)): $base -> $($EN "$T/cc/pkg" | tail -1)"
