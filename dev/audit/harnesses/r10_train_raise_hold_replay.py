#!/usr/bin/env python3
"""R10-TRAIN-RAISE-HOLD (#2401): replay the train's raise reading on live pull requests.

    python3 dev/audit/harnesses/r10_train_raise_hold_replay.py PR[:BASE] [PR[:BASE] ...]
    python3 dev/audit/harnesses/r10_train_raise_hold_replay.py --self-test

For each pull request, at its live head and three-dot from origin/main (or
from BASE, for one main already holds: #2401 merged at 07a09406a, its base
was 176851e950), prints two readings of "is this a budget raise":

  path     the defect's rule, as merge_train.py's approve and
           queue_pre_flight.py applied it before the fix: any changed path
           ending `_budgets.json` is a raise;
  gate     `Train.raise_hold`, the fix: budget_raise_gate's own
           `raises_between` from the merge base, then -- on a raise only --
           the owner's approval at the head with the body's justification and
           the mandate judged now, exactly as approve and pre-flight read it.

Read-only: it fetches the head and calls `gh` read APIs; it never pushes,
approves, comments or merges. A read that fails prints the train's own Stop
and the exit status is 1: every read here (`gh pr view`, `git fetch`, `git
merge-base`, `git diff`) is checked on its return code, and the head and the
base must each be a 40-hex object name before anything is read from them. The
reading used to take `t.out`'s text for the value, so an unauthenticated gh
(HTTP 403) became the "head", the diff became error words, `raise_hold` took
its cheap no-budget-file exit and a real raise (#2368) printed
"0 raise(s), HOLDS" -- the fail-open shape this PR closes in the train.
`--self-test` plants each failing read and a healthy control.
"""
import sys
import tempfile
from pathlib import Path



def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools/audit/seat"))
import merge_train as mt  # noqa: E402


class ReadFailed(Exception):
    """A read the replay depends on failed: the value is unknown, never a hold."""


def read(t, what: str, *argv: str) -> str:
    """The stdout of <argv>, or ReadFailed: a non-zero rc is a failed read."""
    rc, text = t.run(list(argv))
    if rc != 0:
        raise ReadFailed(f"{what} failed (rc={rc}): {text.strip()[:120]}")
    return text.strip()


def sha(t, what: str, *argv: str) -> str:
    v = read(t, what, *argv)
    if not mt.is_sha(v):
        raise ReadFailed(f"{what} is not a 40-hex object name: {v[:60]!r}")
    return v


def replay(t, pr: int, at: str) -> int:
    """Print the two readings for <pr>; 0, or 1 when a read failed."""
    try:
        h = sha(t, "gh pr view headRefOid", "gh", "pr", "view", str(pr), "--repo", t.repo,
                "--json", "headRefOid", "--jq", ".headRefOid")
        read(t, "git fetch", "git", "fetch", "-q", "origin", "main", h)
        base = sha(t, "git merge-base", "git", "merge-base", at or "origin/main", h)
        files = read(t, "git diff", "git", "diff", "--no-renames", "--name-only", base, h).split()
    except ReadFailed as e:
        print(f"#{pr}")
        print(f"  gate : STOP read: {e}")
        return 1
    path = [f for f in files if f.endswith("_budgets.json")]
    print(f"#{pr} head {h[:12]} base {base[:12]}")
    print(f"  path : {'RAISE' if path else 'none'} ({', '.join(path) or 'no budget path'})")
    if at:  # raise_hold reads the merge base with origin/main; answer it with BASE's
        real = t.run

        def run(argv, cwd=mt.ROOT, stdin=None, real=real, base=base):
            if argv[:3] == ["git", "merge-base", "origin/main"]:
                return 0, base + "\n"
            return real(argv, cwd=cwd, stdin=stdin)
        t.run = run
    try:
        raises, held, why = t.raise_hold(pr, h, files)
        print(f"  gate : {len(raises)} raise(s), {'HOLDS' if held else 'STOPS'}: {why}")
    except mt.Stop as s:
        print(f"  gate : STOP {s.step}: {s.why}")
    return 0


def main(argv: "list[str]") -> int:
    if argv == ["--self-test"]:
        return self_test()
    if not argv or not all(a.split(":")[0].isdigit() for a in argv):
        print(__doc__)
        return 2
    rc = 0
    with tempfile.TemporaryDirectory() as d:
        t = mt.Train("tvofi/heatpump_optimizer", Path(d), None, "", (), 1)
        for arg in argv:
            pr, _, at = arg.partition(":")
            t.run = t._run  # a BASE answers its own entry only
            rc |= replay(t, int(pr), at)
    return rc


def self_test() -> int:
    """Plant each failing read; a healthy control must still print the hold."""
    import contextlib
    import io
    H, B = "a" * 40, "b" * 40
    ok = {"gh": (0, H + "\n"), "fetch": (0, ""), "merge-base": (0, B + "\n"),
          "diff": (0, "tests/stress_budgets.json\n")}

    def drive(fail: "dict[str, tuple[int, str]]"):
        answers = {**ok, **fail}

        class T:
            repo = "o/r"

            def run(self, argv, cwd=None, stdin=None):
                key = argv[0] if argv[0] == "gh" else argv[1]
                return answers[key]

            def raise_hold(self, pr, h, files):
                return [], True, "no budget raise (planted)"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = replay(T(), 2368, "")
        return rc, buf.getvalue()

    bad = 0

    def check(name: str, cond: bool) -> None:
        nonlocal bad
        print(("  ok   " if cond else "  FAIL ") + name)
        bad += 0 if cond else 1
    rc, out = drive({})
    check("null control: every read healthy prints the train's reading and exits 0",
          rc == 0 and "HOLDS" in out and "path : RAISE" in out)
    for name, key, bodyv in (
            ("gh unauthenticated (HTTP 403)", "gh", (1, "HTTP 403: Forbidden")),
            ("git fetch failing", "fetch", (128, "fatal: unable to access")),
            ("git merge-base failing", "merge-base", (1, "fatal: Not a valid object")),
            ("git diff failing", "diff", (128, "fatal: bad object"))):
        rc, out = drive({key: bodyv})
        check(f"{name} prints a Stop and exits non-zero, never a hold",
              rc == 1 and "STOP read" in out and "HOLDS" not in out and "path :" not in out)
    rc, out = drive({"gh": (0, "HTTP 403: Gi\n")})
    check("a head that is not 40-hex is a Stop even when gh exits 0",
          rc == 1 and "STOP read" in out and "HOLDS" not in out)
    rc, out = drive({"merge-base": (0, "fatal: Not a\n")})
    check("a base that is not 40-hex is a Stop even when git exits 0",
          rc == 1 and "STOP read" in out and "HOLDS" not in out)
    print(f"replay self-test: {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
