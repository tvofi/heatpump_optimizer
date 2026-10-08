# Reviewer's own harness (not the fixer's): drives the #2028 pin's predicate,
# extracted verbatim from tests/entities.py at the head, over planted variants.
import re, sys
src = open(sys.argv[1]).read(); wf0 = open(sys.argv[2]).read()
def grab(name):
    i = src.index(f"def {name}("); j = src.index("\n\n\n", i); return src[i:j]
ns = {"re": re}
exec(grab("_workflow_job"), ns); exec(grab("_red_history_credentialed"), ns)
def verdict(wf):
    body = "\n".join(l for l in ns["_workflow_job"](wf, "pr-contract").split("\n") if not l.lstrip().startswith("#"))
    step = next((b for b in body.split("\n      - name: ") if b.startswith("Check the body against the contract")), "")
    pos = ns["_red_history_credentialed"](step)
    null = bool(step) and not ns["_red_history_credentialed"](re.sub(r".*secrets\.GITHUB_TOKEN.*\n", "", step))
    return pos, null
L = "          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n        run: |\n          set -euo pipefail\n          # One --red"
R = "        run: |\n          set -euo pipefail\n          # One --red"
assert wf0.count(L) == 1
FIG = "      - name: Every figure's command resolves at this head\n        if: always()\n"
muts = {
 "head": wf0,
 "M0 delete line": wf0.replace(L, R),
 "M1 comment out": wf0.replace(L, "          # GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n" + R),
 "M2 moved to next step": wf0.replace(L, R).replace(FIG, FIG + "        env:\n          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n"),
 "M3 empty value": wf0.replace(L, L.replace("${{ secrets.GITHUB_TOKEN }}", '""')),
 "M4 GITHUB_TOKEN name (equivalent)": wf0.replace(L, L.replace("GH_TOKEN:", "GITHUB_TOKEN:")),
 "M5 github.token (equivalent)": wf0.replace(L, L.replace("secrets.GITHUB_TOKEN", "github.token")),
 "M6 in run block only": wf0.replace(L, R.replace("set -euo pipefail", "set -euo pipefail\n          # GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n          echo GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}")),
 "M7 wrong secret": wf0.replace(L, L.replace("secrets.GITHUB_TOKEN", "secrets.OTHER")),
}
for k, wf in muts.items():
    pos, null = verdict(wf)
    print(f"RESULT {k:36s} pin={'ok' if pos else 'FAIL'} null={'ok' if null else 'FAIL'}")
