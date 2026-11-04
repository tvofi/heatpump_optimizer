# Reviewer's own harness: C24 template arm, independent of the fixer's test.
import sys; tree=sys.argv[1]; card_src=sys.argv[2] if len(sys.argv)>2 else tree
sys.path.insert(0, tree+'/tools/audit')
from pathlib import Path
from archscore.metrics import card as K
def rules(js): return sum(len(g) for g in K.rule_copies(K.tokenize(js, strings=True)))
BASE = """
function a(p) { const k = `${p.id}:${p.id}`; return k; }
function b(e, q) {
  const z = q.size;
  return z;
}
"""
anchor="  return z;\n"
pl=lambda l: BASE.replace(anchor, l+anchor)
b=rules(BASE)
cases={
 "respelled_key(own)": pl("  if (q.k === `${e[0]}~${e[1]}`) return 1;\n") ,
 "respelled_label": pl("  const t = `${e.start}..${e.end} @`;\n  const u = `${q.start}..${q.end} @`;\n"),
 "null_unrelated": pl("  const t = `${e.a}/${q.b}`;\n"),
 "null_markup_twice": pl("  const t = `<g x=\"${e.x}\" y=\"${e.y}\"/>`;\n  const u = `<g x=\"${q.x}\" y=\"${q.y}\"/>`;\n"),
}
print("RESULT base", b)
for k,v in cases.items(): print("RESULT", k, rules(v))
m=K.measure(Path(card_src)); print("RESULT real", m['card_dead_definitions'], m['card_clone_copies'], m['card_rule_copies'])
