"""Spell a one-template card rule once more inline: the Setup diagram keys a drawn edge as ``${e[0]}>${e[1]}``
and binds it to ``edge``, and the attempt tests the rejected set with the key written out again instead of
reading the binding. The rule is spelled at one more site and behaves the same; a template's text read ``S``
and no ``&&``/``||`` chain in it, so neither the 20-token window nor the chain census read it. Counter C24
(``card_rule_copies``, gate-only), its template arm."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "www" / "heatpump-optimizer-card.js"
src = p.read_text()
bound = "rejected.has(edge) ? \" invalid\" : matched"
spelled = "rejected.has(`${e[0]}>${e[1]}`) ? \" invalid\" : matched"
assert src.count(bound) == 1, src.count(bound)
p.write_text(src.replace(bound, spelled))
print("respelled 1")
