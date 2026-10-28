"""Reviewer-built model of P228's gate-qualification rule (not the finder's; none committed)."""
import re, sys
TS = re.compile(r"^\d{4}-\d\d-\d\dT[\d:.]+Z ")
STR = ("API rate limit exceeded for installation", "RATE-LIMITED reset_epoch=", "the GitHub API is unreachable")
REASON = re.compile(r"^(.+): failure \(this run\)$")
def reasons(lines, fail_only=False):
    ls = [TS.sub("", l.rstrip("\n")) for l in lines]
    for i, l in enumerate(ls):
        if l.startswith("FAIL "):
            out = [l[5:]]
            if not fail_only:
                for m in ls[i+1:]:
                    if m.startswith("##[error]"): break
                    out.append(m)
            return set(out)
        if l.startswith("RATE-LIMITED reset_epoch="):
            return "RL"
    return None
def qualifies(gate_lines, failed, fail_only=False):  # failed: {job: log_text}
    matching = {j for j, t in failed.items() if any(s in t for s in STR)}
    r = reasons(gate_lines, fail_only)
    if r == "RL": return True
    if not r: return False
    for x in r:
        m = REASON.match(x)
        if not m or m.group(1) not in matching: return False
    return True
def rerun(gate_lines, failed, attempt=1, fail_only=False, any_match=False):
    if attempt != 1: return False
    others = {j: t for j, t in failed.items() if j != "gate"}
    test = any if any_match else all
    if not test(any(s in t for s in STR) for t in others.values()): return False
    return qualifies(gate_lines, failed, fail_only)
if __name__ == "__main__":
    real = open(sys.argv[1]).readlines()
    hacs = "GitHubRatelimitException: API rate limit exceeded for installation"
    envm = "FAIL pr / nothing skipped -- skip required-contexts the GitHub API is unreachable"
    F = {"validate / validate-hacs": hacs, "governance / env-matrix": envm, "gate": "".join(real)}
    g = lambda *ls: [f"2026-10-27T23:10:18.0Z {l}\n" for l in ls] + ["2026-10-27T23:10:18.1Z ##[error]Process completed with exit code 1.\n"]
    A = "FAIL governance / env-matrix: failure (this run)"; B = "validate / validate-hacs: failure (this run)"
    rows = [
     ("instance log (real), re-run", rerun(real, F), True),
     ("instance log, FAIL-only reader still re-runs here (env-matrix also matches)", rerun(real, F, fail_only=True), True),
     ("fixture order A,B re-run", rerun(g(A, B), F), True),
     ("fixture order B,A re-run", rerun(g("FAIL " + B, A[5:]), F), True),
     ("null: second reason SKIPPED not re-run", rerun(g(A, "tests / browser: SKIPPED (this run)"), F), False),
     ("null: second reason (run <id>) not re-run", rerun(g(A, "validate / validate-hacs: failure (run 9)"), F), False),
     ("mutant FAIL-only on SKIPPED-second -> re-runs (caught)", rerun(g(A, "tests / browser: SKIPPED (this run)"), F, fail_only=True), True),
     ("null: first reason names non-infra job", rerun(g("FAIL tests / fast (3.14): failure (this run)", B), dict(F, **{"tests / fast (3.14)": "AssertionError"})), False),
     ("null: attempt 2", rerun(real, F, attempt=2), False),
     ("null: mixed (one non-infra failed job)", rerun(real, dict(F, **{"tests / fast (3.14)": "AssertionError"})), False),
     ("mutant any-match on mixed -> re-runs (caught)", rerun(real, dict(F, **{"tests / fast (3.14)": "AssertionError"}), any_match=True), None),
     ("RATE-LIMITED gate is matching", rerun(["2026-10-27T23:10:18.0Z RATE-LIMITED reset_epoch=1792991224 repos/x\n", "2026-10-27T23:10:18.0Z ##[error]reset_epoch=1792991224\n"], F), True),
    ]
    for name, got, want in rows:
        print(f"RESULT {name}: {got}" + ("" if want is None or got == want else f"  !! want {want}"))
