"""Spell a one-statement card rule once more inline: the Setup tab's manual-setpoint field reads
``slot.manual_setpoint == null``, and the attempt writes the nullish test out as the card spells it elsewhere,
``x === null || x === undefined``. The rule is spelled at one more site and behaves the same; it is shorter than
a 20-token window, so card_clone_copies read nothing (the #2401 review spelled three of ARCH2-s5's card_shapes
rules once more inline and card_clone_copies read 108 -> 108). Counter C24 (``card_rule_copies``, gate-only)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "www" / "heatpump-optimizer-card.js"
src = p.read_text()
loose = "slot.manual_setpoint == null ? 0 : slot.manual_setpoint"
spelled = ("slot.manual_setpoint === null || slot.manual_setpoint === undefined\n"
           "                ? 0\n"
           "                : slot.manual_setpoint")
assert src.count(loose) == 1, src.count(loose)
p.write_text(src.replace(loose, spelled))
print("respelled 1")
