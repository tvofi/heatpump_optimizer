#!/usr/bin/env python3
"""Run one `gh` READ under gh_read.py's rule, for a step that has no Python of its own.

    python3 -I tools/audit/seat/gh_read_run.py gh api repos/o/r/pulls/1 --jq .body
    python3 -I tools/audit/seat/gh_read_run.py --self-test

For pr-contract.yml's reads (R10-FLY-GH-READ-RETRY carry 0; the job's wiring
is a follow-up, because the job grades with the base's copy): one unretried
`gh api` read failed #2579's contract on a non-JSON answer that a sibling read
a second earlier did not get. The rule is gh_read's, not restated here: 4
reads settling 5/15/45 s, retrying only what `gh_read.gh_wait` calls
transient. The answering read's stdout is written once, so a retried
`--paginate` never prints a page twice; each settle goes to stderr. A refusal
exits with the last read's code and writes its stderr, with what stopped the
loop on the last line. An argv `gh_read.is_read` does not call a read is never
run (exit 2): a write is never retried.

Its own file, beside gh_read.py rather than in it, because a workflow runs the
base's copy of what it pins: a mode added to gh_read.py would be missing from
the copy that grades the pull request adding it.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gh_read  # noqa: E402  the one read rule


def read(argv, run=subprocess.run, sleep=time.sleep, out=None, err=None) -> int:
    out, err = out or sys.stdout, err or sys.stderr
    if not gh_read.is_read(argv):
        print(f"gh_read_run: not a read, so not run: {' '.join(argv)}", file=err)
        return 2
    codes = []

    def attempt():  # a failure is gh's stderr, which gh_wait classifies
        done = run(argv, text=True, capture_output=True)
        codes.append(done.returncode)
        return (done.stdout, None) if done.returncode == 0 else (None, (done.stderr or "").rstrip())
    answer, failure, _, why = gh_read.retry(attempt, gh_read.gh_wait, sleep,
                                            lambda line: print(f"gh_read_run: {line}", file=err))
    if failure is None:
        out.write(answer)
        return 0
    print(" ".join((failure, why)).strip(), file=err)
    return codes[-1] or 1


def self_test() -> int:
    import io
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"FAIL {name}")

    def drive(queue, argv=("gh", "api", "repos/o/r/pulls/1", "--jq", ".body")):
        """`read` over a queue of (rc, stderr) failures, answered by '{"ok"}' once spent."""
        calls, sleeps, out, err = [], [], io.StringIO(), io.StringIO()

        def run(a, **kw):
            calls.append(list(a))
            if not (kw.get("text") is True and kw.get("capture_output") is True):
                raise AssertionError(f"a read is run as text, its output captured: {kw}")
            rc, text = queue.pop(0) if queue else (0, "")
            return subprocess.CompletedProcess(a, rc, '{"ok"}\n' if rc == 0 else "partial\n", text)
        rc = read(list(argv), run=run, sleep=sleeps.append, out=out, err=err)
        return rc, len(calls), sleeps, out.getvalue(), err.getvalue()

    EOF = 'Get "https://api.github.com/repos/o/r/pulls/1": EOF\n'
    NON_JSON = "invalid character 'S' looking for beginning of value\n"
    rc, n, sleeps, out, _ = drive([(1, EOF)])
    check("one transport failure, then an answer: answered after exactly 2 calls",
          rc == 0 and n == 2 and sleeps == [5] and out == '{"ok"}\n')
    rc, n, sleeps, out, _ = drive([(1, NON_JSON)])
    check("#2579's non-JSON answer once, then JSON: answered after exactly 2 calls",
          rc == 0 and n == 2 and sleeps == [5] and out == '{"ok"}\n')
    rc, n, sleeps, out, err = drive([(1, "gh: Not Found (HTTP 404)\n")])
    check("a 404 refuses after exactly 1 call, with gh's code, its line and no output",
          rc == 1 and n == 1 and sleeps == [] and out == "" and err == "gh: Not Found (HTTP 404)\n")
    rc, n, sleeps, out, err = drive([(1, "gh: Validation Failed (HTTP 422)\n")])
    check("a 422 refuses after exactly 1 call", rc == 1 and n == 1 and sleeps == [])
    queue = [(1, EOF), (1, NON_JSON), (1, "gh: HTTP 502\n"), (1, "gh: Service Unavailable (HTTP 503)\n"),
             (1, "gh: Bad Gateway (HTTP 502)\n")]
    check("(every failure queued for the budget is transient, so only the budget stops it)",
          all(gh_read.gh_transient(t) for _, t in queue))
    rc, n, sleeps, out, err = drive(queue)
    check("five transient failures, one past the budget: refused after exactly 4 calls, 5/15/45 s",
          rc == 1 and n == 4 and sleeps == [5, 15, 45] and out == "")
    check("naming the last error read and the attempt count on its last line",
          err.splitlines()[-1] == "gh: Service Unavailable (HTTP 503) (after 4 attempts)")
    rc, n, *_ = drive([(4, EOF)] * 5)
    check("a refusal keeps the last read's own exit code", rc == 4 and n == 4)
    rc, n, sleeps, out, err = drive([(1, EOF)], ("gh", "api", "--paginate", "repos/o/r/pulls/1/commits"))
    check("a retried --paginate writes the answering read's output once",
          rc == 0 and n == 2 and out == '{"ok"}\n')
    rc, n, sleeps, out, err = drive([], ("gh", "api", "-X", "POST", "repos/o/r/issues/1/comments"))
    check("a write is never run: exit 2 after 0 calls", rc == 2 and n == 0 and "not a read" in err)
    rc, n, *_ = drive([], ("gh", "api", "repos/o/r/issues/1/comments", "-f", "body=x"))
    check("a field-carrying gh api is a write: exit 2 after 0 calls", rc == 2 and n == 0)
    rc, n, *_ = drive([], ("git", "fetch", "origin"))
    check("a command that is not gh is not run: exit 2 after 0 calls", rc == 2 and n == 0)
    err = io.StringIO()
    saved, sys.stderr = sys.stderr, err
    try:
        rc = main(["gh", "api", "-X", "POST", "repos/o/r/issues/1/comments"])
    finally:
        sys.stderr = saved
    check("main hands any other argv to read: a write exits 2, never run", rc == 2 and "not a read" in err.getvalue())
    print(f"gh_read_run self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    return read(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
