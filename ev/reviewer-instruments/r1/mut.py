import sys
MUT = {
 "M1": ("        elif main == was:\n            lines = our_blocks.get(name)", "        elif main == was:\n            lines = their_blocks.get(name)"),
 "M2": ("            refused.append(name)\n            continue", "            lines = our_blocks.get(name)"),
 "M3": ("        if mine == main or mine == was:\n            lines = their_blocks.get(name)", "        if mine == main or mine == was:\n            lines = our_blocks.get(name) or their_blocks.get(name)"),
 "M4": ("    if both_changed and not (", "    if False and not ("),
 "M5": ("        if _is_may_drift(line) and not (line in was and (line not in mine or line not in main)):", "        if _is_may_drift(line):"),
 "M6": ("            return f\"the claims for '{name}' are neither side's own\"", "            pass"),
 "R-keep-deleted": ("        if lines:\n            decided[name] = lines", "        lines = lines or _claim_blocks(base).get(name)\n        if lines:\n            decided[name] = lines"),
 "R-mine-eq-main-only": ("        if mine == main or mine == was:", "        if mine == was:"),
}
name, path = sys.argv[1], sys.argv[2]
a, b = MUT[name]; s = open(path).read(); assert s.count(a) == 1, name; open(path, "w").write(s.replace(a, b))
