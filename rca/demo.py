"""Prototype of the proposed predicate (not repository code)."""
import re, sys
sys.path.insert(0, sys.argv[1]); import closure  # main's closure.py, unchanged
def proposed(status, closures_log):
    printed = bool(re.search(r"^(\S+Z )?UNDER-SCOPED: ", closures_log, re.M))
    if status == "skip-not-under-scoped" and printed:
        return "skip-classifier-disagrees"
    return status
for label, log, status in [
    ("e42b1cd defect", sys.argv[2], "skip-not-under-scoped"),
    ("a46a91c null (INERT READS only)", sys.argv[3], "skip-not-under-scoped"),
]:
    text = open(log).read()
    cur_rc, _ = closure.autofix_report("closures-autofix", status)
    new = proposed(status, text)
    new_rc = 1 if closure.autofix_repair_failed("closures-autofix", new) else 0
    print(f"{label}: today status={status} job_rc={cur_rc} | proposed status={new} job_rc={new_rc}")
