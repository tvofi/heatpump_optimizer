"""Reviewer's own harness: exec tests/entities.py's arch-instrument pin (lines 34323-34342 at
29b08d042) against a tests.yml text, original or mutated, and print its verdict."""
import sys
import yaml as _yaml

WT = "/Users/timmalmstrom/hpo-seats/r10s5/rev-2665/wt"
src = open(f"{WT}/tests/entities.py").read().splitlines()[34322:34342]
head = open(f"{WT}/.github/workflows/tests.yml").read()
main = open(sys.argv[1]).read() if len(sys.argv) > 1 else None


class R:
    @staticmethod
    def check(name, ok, detail=""):
        print(("ok  " if ok else "FAIL"), detail)
        R.last = ok


def pin(text, label):
    print(f"[{label}] ", end="")
    exec("\n".join(src), {"_yaml": _yaml, "_tests_workflow": text, "R": R})
    return R.last


def mutate(old, new, count=1):
    assert head.count(old) >= 1, old
    return head.replace(old, new, count)


results = {}
results["head"] = pin(head, "head")
if main:
    results["main"] = pin(main, "origin/main tests.yml")
# arch-instrument's copy of the scope step: full on push -> auto (the body's mutant). The second
# occurrence of the scope `else` branch is arch-instrument's.
i = head.index("- name: Run the architecture-score pair")
j = head.rindex('echo "GATE_SCOPE=full" >> "$GITHUB_ENV"', 0, i)
results["scope-full->auto"] = pin(head[:j] + 'echo "GATE_SCOPE=auto" >> "$GITHUB_ENV"' + head[j + len('echo "GATE_SCOPE=full" >> "$GITHUB_ENV"'):], "arch copy: full->auto")
results["fast RUN_PART dropped"] = pin(mutate("          RUN_PART: fast\n", ""), "fast RUN_PART dropped")
results["arch RUN_PART=all"] = pin(mutate("          RUN_PART: arch\n", "          RUN_PART: all\n"), "arch RUN_PART=all")
k = head.index("  arch-instrument:\n")
results["arch needs fast too"] = pin(head[:k] + head[k:].replace("needs: [closure-scope]", "needs: [closure-scope, fast]", 1), "arch needs fast")
# arch-instrument's copy of the comparison-ref step: push ref HEAD^1 -> HEAD
m = head.rindex("REF=$(git rev-parse --verify --quiet 'HEAD^1^{commit}') || REF=\"\"\n          fi", 0, i)
results["ref push HEAD^1->HEAD"] = pin(head[:m] + head[m:].replace("'HEAD^1^{commit}'", "'HEAD^{commit}'", 1), "arch copy: push ref HEAD^1->HEAD")
print("RESULT", {k: ("pass" if v else "fail") for k, v in results.items()})
