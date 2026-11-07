# BLOCKED: #3271 red is a real regression from this diff

Run 128272747268 (tests / fast (3.14), 2026-11-07 02:44Z), script `python3 tests/harness_headers.py`, 213 s:

    FAIL every inlined walk matches the canonical helper and no depth root remains  [FAIL depth seams: dev/audit/harnesses/r10_triage_p393.py:35: ROOT = Path(__file__).resolve().parents[3]
    1 of 112 HARNESS HEADER CHECKS FAILED

It is not host timing. The only failing check, deterministic, names a file this PR adds
(`dev/audit/harnesses/r10_triage_p393.py` line 35 inlines a depth-root walk instead of the canonical repo_root helper).
The code head 2e84abd9 and PR head 3ab5c18b differ only by delivery rows, so the line is present at both.
Every other check in that run passed except as listed; no other failing script.

Brief step 2 says a failure this diff can cause means stop: no body written, nothing pushed to handoff or handoff-body.
Not measured: main / other PR heads (this one-check failure names a file only in this diff, so main cannot show it); local rerun
(this container's HA venv lacks the CI deps and fails 57 unrelated checks in 12 s, so it is not comparable); failure_logs.sh (gh auth fails here, logs read via the API).

Needs a code fix, which a body-only seat must not make: replace the inlined ROOT walk at line 35 with the canonical helper
that harness_headers.py names, then rerun tests/harness_headers.py. That edits a record file's harness, so it belongs to the PR author.
