# Reviewer's fast harness: execs tests/entities.py lines 21856-21878 verbatim (the pin) against a given codeql.yml.
import sys, yaml as _yaml
src = open("/tmp/wt/tests/entities.py").read().splitlines()[21855:21878]
class R:
    @staticmethod
    def check(name, ok, detail=""): print(("ok  " if ok else "FAIL"), name[:60], "|", detail[:110]); sys.exit(0 if ok else 1)
_CODEQL_YML = open(sys.argv[1]).read()
exec("\n".join(src), {"_yaml": _yaml, "R": R, "_CODEQL_YML": _CODEQL_YML})
