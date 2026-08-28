"""The drift gate for golden fixtures whose floats do not travel.

`valve_storage_smart_write`, `wood_two_tank`, `wood_two_tank_smart_write`,
`wood_coil` and `valve_upper_direct_slab` do not reproduce across
scipy/numpy builds — and not at the last decimal: these are the non-convex
valve/wood solves, and a different BLAS lands them in a different local
optimum (plan-shape flips, different compressor-start counts). On such a
machine `tests/golden.py` reports them as DIFF on a clean checkout of main,
which makes "fails, as expected" worthless as a review signal: a real
regression in exactly these scenarios would hide behind the label.

This script restores the signal. It captures scenarios twice in the SAME
environment — once from this working tree, once from a pristine worktree
of a reference commit (default `origin/main`) — and requires the two
computed payload sets to be byte-identical. Solver noise cancels because
both runs share the solver; anything left is this branch's doing.

    PYTHONPATH=tests/hastub python3 tests/env_drift.py [ref]          # 5 sensitive fixtures
    PYTHONPATH=tests/hastub python3 tests/env_drift.py --all [ref]    # every fixture (CI)

`--all` is what CI runs: committed fixtures were recorded on one machine
and CI runs on another, so exact comparison against the files would cry
wolf; comparing two captures made by the same runner is environment-proof
by construction.

A branch is allowed to move fixtures — behaviour changes are sometimes
the point — but it must say so: `tests/golden/claimed_drift.txt` lists
one scenario name per line (with a reason after `#`). Listed scenarios
still print their diffs, but do not fail the gate. A claim that matched
nothing is stale and fails too, but it is counted and reported apart
from drift: nothing regressed, the list is simply out of date.

A claim describes exactly ONE diff, and two rules keep it that way:

  * The file carries a machine-read declaration line — `# claims-for:
    <version>` — which must equal the repo-root VERSION file. That is
    checked first, before any capture, in both modes, and it fails the
    run on its own.
  * In `--all` mode the claim list must also differ from the baseline's.
    The stamp only expires claims when the version *changes*, and this
    history is full of consecutive commits that share one: 7b512bc,
    401db6e and 2248f64 all carry 4.0.0, and the ten v4.0.0 T* tranche
    merges all carry 3.16.0 (the release they were building towards is
    in their titles, not in VERSION). Across any of those an inherited
    file carries a matching stamp and sails through. So if this tree
    claims exactly what the baseline
    claims — same names, same reasons — the list was written for the
    baseline's diff rather than this one, and the run fails. An empty
    list is always fine; it is a statement, not an inheritance.

Staleness is only ever judged against scenarios this run actually
captured. The five-fixture mode captures SENSITIVE and nothing else, so
a claim naming any other scenario is reported as not evaluated there
rather than called stale — judging it is `--all`'s job, which is what
CI runs.

The file is committed, so without those rules it outlives the PR that
wrote it: v4.0.7, v4.2.0 and v4.3.0 each moved no goldens, inherited the
previous release's claims, and failed CI on main with N stale claims for
code that was never wrong (a push to main is compared against HEAD^1 —
the merged PR's own diff). A release that moves nothing still rewrites
the file: bump `claims-for:`, delete every claim, and the empty list is
then a statement about THIS diff instead of an inherited lie.

Scenarios that exist only on this branch (a PR adding coverage) have no
baseline to compare against; they are reported and pass — the golden
invariant layer inside `golden.py` still vets them. Scenarios that exist
only on the baseline (a PR deleting coverage) fail unless claimed.

The comparison ref must not resolve to HEAD. A tree compared against
itself is byte-identical by construction — no drift whatever the branch
did, and every claim stale — so a gate in that state proves nothing and
says so instead of passing.

Exit 0: no unclaimed drift. Exit 1: this branch moved a fixture the
reference does not move in this environment — either a regression, or a
behaviour change the PR must claim; or a claim matched nothing; or the
claim file is stamped for a different release than VERSION, or is the
baseline's list carried forward; or the ref is HEAD itself. Never
re-record the five sensitive fixtures on a machine where golden.py
already reports them as DIFF.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

SENSITIVE = (
    "valve_storage_smart_write",
    "wood_two_tank",
    "wood_two_tank_smart_write",
    "wood_coil",
    "valve_upper_direct_slab",
)

CLAIM_FILE = os.path.join("tests", "golden", "claimed_drift.txt")
CLAIM_VERSION_MARKER = "claims-for:"
#: Declares a SENSITIVE fixture whose drift is judged per machine rather than
#: per release. See `_may_drift` for why an ordinary claim cannot do this job.
MAY_DRIFT_MARKER = "may-drift:"
VERSION_FILE = "VERSION"


def capture_tree(root: str, out_path: str, everything: bool) -> None:
    """Worker mode: capture scenarios from one repo root."""
    os.chdir(root)  # golden.py resolves its fixtures relative to cwd
    sys.path.insert(0, os.path.join(root, "tests"))
    sys.path.insert(0, os.path.join(root, "custom_components"))
    import golden

    if everything:
        payloads = {n: golden.capture(n, s) for n, s in golden.SCENARIOS.items()}
        for name, config in golden.coordinator_scenarios().items():
            payloads[name] = golden.capture_coordinator(config)
        payloads["config_flow"] = golden.capture_config_flow()
    else:
        payloads = {n: golden.capture(n, golden.SCENARIOS[n]) for n in SENSITIVE}
    with open(out_path, "w") as f:
        json.dump(payloads, f, indent=1, sort_keys=True)


def _diff_leaves(a, b, path, out) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k}: present on one side only")
            else:
                _diff_leaves(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _diff_leaves(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")


def _repo_version(repo: str) -> str:
    """The release this tree is, per the repo-root VERSION file."""
    path = os.path.join(repo, VERSION_FILE)
    if not os.path.exists(path):
        return ""
    return open(path).read().strip()


def _looks_like_version(text: str) -> bool:
    parts = text.split(".")
    return len(parts) == 3 and all(p.isdigit() for p in parts)


def _rev(repo: str, rev: str) -> str | None:
    """The commit `rev` names in `repo`, or None when it does not resolve."""
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=repo, capture_output=True, text=True,
    )
    return proc.stdout.strip() or None


def _claimed(repo: str) -> tuple[str | None, dict[str, str]]:
    """The release a claim file is stamped for, and the scenarios it claims.

    The stamp is a comment line that BEGINS with the marker and nothing
    else (`# claims-for: 5.0.0`), first one wins. Merely mentioning
    `claims-for:` does not declare anything — the file's own header prose
    talks about the rule, and an earlier draft of this parser read that
    sentence as the declaration. A claim line never declares either: it has
    a body, so its trailing reason is only a reason.
    """
    path = os.path.join(repo, CLAIM_FILE)
    declared: str | None = None
    claims: dict[str, str] = {}
    if not os.path.exists(path):
        return declared, claims
    for line in open(path):
        body, _, comment = line.partition("#")
        name = body.strip()
        if name:
            claims[name] = comment.strip() or "no reason given"
            continue
        note = comment.strip()
        if declared is None and note.startswith(CLAIM_VERSION_MARKER):
            rest = note[len(CLAIM_VERSION_MARKER):].split()
            declared = rest[0] if rest else ""
    return declared, claims


def _may_drift(repo: str) -> dict[str, str]:
    """SENSITIVE fixtures this branch may or may not move, and why.

    An ordinary claim asserts "this scenario moved". For the five fixtures in
    ``SENSITIVE`` that assertion is not a property of the branch at all: they
    do not reproduce across BLAS builds, so each machine solves them to a
    different local optimum, and whether a given change touches one is a fact
    about the runner rather than about the diff.

    v5.1.7 is the case that forced this. Its change relabels the
    ``classify_space_steps`` fall-through, which a plan reaches only when a
    step has no ``heat_loss_factors > 1.1``. All five sensitive fixtures run a
    profile whose factor is a constant 1.06, so every ``preheat_weather`` they
    carry is a fall-through -- and *which* steps fall through depends on the
    local optimum. On this machine only ``valve_upper_direct_slab`` has one;
    the committed fixtures, recorded elsewhere, show them in
    ``valve_storage_smart_write`` and ``wood_two_tank_smart_write`` instead.
    So a claim naming this machine's fixture is unclaimed drift on the
    recording machine, and a claim naming the recording machine's fixtures is
    a stale claim here. Both spellings fail, on different machines, for a
    change that is correct on both.

    A may-drift entry says the honest thing: this scenario is one the gate
    itself declares non-reproducible, this change plausibly touches it, and
    the diff is printed for a human rather than judged by the runner. It is
    deliberately weaker than a claim, and confined so it cannot be used as
    one: `may_drift_error` rejects any name outside ``SENSITIVE``, so the
    exemption can never reach a fixture whose floats do travel.

    Written as comment lines (``# may-drift: <name> -- <reason>``) so that
    `_claimed`, which reads any non-comment line as a claim, is untouched --
    and so that the entries stay out of the inherited-claims comparison,
    which is right: this is a standing statement about five fixtures, not a
    claim about one release's diff, and it does not expire with VERSION.
    """
    path = os.path.join(repo, CLAIM_FILE)
    out: dict[str, str] = {}
    if not os.path.exists(path):
        return out
    for line in open(path):
        body, _, comment = line.partition("#")
        if body.strip():
            # A claim line. Its trailing text is a reason, never a marker.
            continue
        note = comment.strip()
        if not note.startswith(MAY_DRIFT_MARKER):
            continue
        rest = note[len(MAY_DRIFT_MARKER):].strip()
        name, _, reason = rest.partition("--")
        if name.strip():
            out[name.strip()] = reason.strip() or "no reason given"
    return out


def may_drift_error(
    may_drift: dict[str, str], claims: dict[str, str]
) -> str | None:
    """Why the may-drift list is not usable - None when it is.

    Two rules, and both exist to stop the category becoming a way to launder
    a real regression:

    * it may only name fixtures in ``SENSITIVE``, the ones this script
      already declares non-reproducible. Anywhere else, a moved fixture is
      the branch's doing and has to be claimed;
    * a name cannot be both claimed and may-drift, because the two say
      different things about the same scenario and only one can be checked.
    """
    stray = sorted(set(may_drift) - set(SENSITIVE))
    if stray:
        return (
            "MAY-DRIFT OUT OF SCOPE: {file} marks\n"
            "{stray} as may-drift, but that category exists only for the\n"
            "fixtures this gate declares non-reproducible across BLAS\n"
            "builds: {sensitive}.\n"
            "Everywhere else a moved fixture is this branch's doing and is\n"
            "judged per release -- claim it with a reason, or find out why\n"
            "it moved. Widening this category would let a real regression\n"
            "through under a permanent exemption."
        ).format(
            file=CLAIM_FILE,
            stray=", ".join(stray),
            sensitive=", ".join(SENSITIVE),
        )
    both = sorted(set(may_drift) & set(claims))
    if both:
        return (
            "CLAIMED AND MAY-DRIFT: {file} lists\n"
            "{both} as both. A claim asserts the scenario moved and goes\n"
            "stale when it does not; may-drift asserts nothing either way.\n"
            "Pick one -- may-drift for the sensitive fixtures, a claim for\n"
            "everything else."
        ).format(file=CLAIM_FILE, both=", ".join(both))
    return None


def claim_version_error(repo: str) -> str | None:
    """Why the claim file is not stamped for this tree — None when it is.

    Public on purpose: tests/entities.py calls it too, so the rule holds in
    every GOLDEN_MODE, including the strict runs where run.sh skips this
    script entirely because the comparison ref is unreachable.
    """
    version = _repo_version(repo)
    declared, _ = _claimed(repo)
    if not version:
        return (
            f"NO VERSION FILE: {VERSION_FILE} is missing or empty, so the\n"
            f"claim file in {CLAIM_FILE} cannot be checked against the\n"
            "release it belongs to. Restore VERSION."
        )
    # Equality alone is not enough: `claims-for: next` in a tree whose
    # VERSION also reads `next` would match itself and pass, and a stamp
    # that is not a release number expires on nothing.
    if not _looks_like_version(version):
        return (
            f"MALFORMED VERSION: {VERSION_FILE} reads '{version}', which is\n"
            f"not an X.Y.Z release number, so the '{CLAIM_VERSION_MARKER}'\n"
            f"stamp in {CLAIM_FILE} cannot be tied to a release. Fix\n"
            f"{VERSION_FILE} first."
        )
    if declared == version:
        return None
    if declared is None:
        head = (
            f"UNSTAMPED CLAIM FILE: {CLAIM_FILE} declares no release,\n"
            f"and this tree is v{version}. Every claim file must carry a\n"
            f"'# {CLAIM_VERSION_MARKER} {version}' line of its own."
        )
    elif not _looks_like_version(declared):
        head = (
            f"MALFORMED CLAIM FILE: {CLAIM_FILE} declares\n"
            f"'{CLAIM_VERSION_MARKER} {declared}', which is not a version, and\n"
            f"this tree is v{version}."
        )
    else:
        head = (
            f"STALE CLAIM FILE: {CLAIM_FILE} declares claims for\n"
            f"v{declared} but this tree is v{version}."
        )
    return (
        f"{head} A claim describes one release's diff\n"
        "and does not carry forward. Rewrite the file for this release --\n"
        f"bump the '{CLAIM_VERSION_MARKER}' line and delete claims this release\n"
        "does not move (an empty list is the right answer for a release\n"
        "that moves no goldens)."
    )


def inherited_claims_error(
    claims: dict[str, str], baseline_claims: dict[str, str], ref: str
) -> str | None:
    """Why this tree's claim list is the baseline's — None when it is not.

    The `claims-for:` stamp expires a claim per VERSION *value*, which is
    weaker than the rule it stands for: consecutive commits routinely
    share a version (7b512bc/401db6e/2248f64 at 4.0.0, the ten v4.0.0
    T* merges at 3.16.0), and across those an inherited file carries
    a matching stamp. This is the invariant itself: a claim list that is
    exactly the baseline's — same names, same reasons — was written for
    the baseline's diff, not for this one. Comparing the PARSED claims
    rather than the file's bytes means a comment or whitespace edit
    cannot launder an inherited list. An empty list claims nothing and is
    always fine.
    """
    if not claims or claims != baseline_claims:
        return None
    names = ", ".join(sorted(claims))
    return (
        f"INHERITED CLAIMS: {CLAIM_FILE} claims exactly\n"
        f"what {ref} already claims -- the same {len(claims)} scenario(s),\n"
        "with the same reasons:\n"
        f"  {names}\n"
        "So this list was written for the baseline's diff and carried\n"
        "forward, not written for this one; whatever it excuses here, it\n"
        "excuses by accident. (The 'claims-for:' stamp cannot catch this:\n"
        "it only expires claims when VERSION changes, and a merge at an\n"
        "unchanged version inherits a matching stamp too.) Rewrite the\n"
        "list for THIS diff -- delete what this change does not move, and\n"
        "give what it does move a reason that describes this change. An\n"
        "empty list is the right answer for a change that moves nothing."
    )


def self_comparison_error(ref: str, head: str) -> str:
    """The message for a run whose comparison ref resolves to HEAD."""
    return (
        f"SELF-COMPARISON: '{ref}' resolves to {head[:12]}, which is HEAD.\n"
        "Comparing this tree against itself proves nothing: the two\n"
        "captures are identical by construction, so no drift can ever be\n"
        f"reported and every claim in {CLAIM_FILE} is\n"
        "stale by definition -- a gate that cannot fail is not a gate.\n"
        "Point the comparison ref at the commit this tree should be\n"
        "measured against -- the merge-base with the target branch for a\n"
        "PR, HEAD^1 for a push to main -- and fail the run if that commit\n"
        "cannot be resolved instead of falling back to HEAD."
    )


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--capture":
        everything = "--all" in sys.argv[4:]
        capture_tree(sys.argv[2], sys.argv[3], everything)
        return 0

    args = [a for a in sys.argv[1:] if a != "--all"]
    everything = "--all" in sys.argv[1:]
    ref = args[0] if args and args[0] else "origin/main"
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Before anything else, in both modes: a claim file stamped for another
    # release is wrong whatever the capture would say, and this has to fire
    # even when `ref` cannot be resolved and no baseline can be built.
    stamp_problem = claim_version_error(repo)
    if stamp_problem:
        print(stamp_problem)
        return 1
    _declared, claims = _claimed(repo)
    may_drift = _may_drift(repo)
    scope_problem = may_drift_error(may_drift, claims)
    if scope_problem:
        print(scope_problem)
        return 1

    # A ref that resolves to HEAD makes the whole gate vacuous, so say so
    # rather than reporting the "no drift" it would trivially find. (A ref
    # that resolves to nothing is left to the worktree call below, which
    # reports git's own reason for it.)
    head_sha = _rev(repo, "HEAD")
    ref_sha = _rev(repo, ref)
    if head_sha is not None and ref_sha == head_sha:
        print(self_comparison_error(ref, head_sha))
        return 1

    tmp = tempfile.mkdtemp(prefix="env_drift_")
    worktree = os.path.join(tmp, "baseline")
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree, ref],
        cwd=repo, check=True, capture_output=True,
    )
    try:
        # Cheapest check that needs the baseline, so it runs before the two
        # capture subprocesses rather than after half an hour of solving.
        if everything:
            _, baseline_claims = _claimed(worktree)
            inherited = inherited_claims_error(claims, baseline_claims, ref)
            if inherited:
                print(inherited)
                return 1

        outputs = {}
        for label, root in (("branch", repo), ("baseline", worktree)):
            out_path = os.path.join(tmp, f"{label}.json")
            env = dict(os.environ)
            env["PYTHONPATH"] = os.path.join(root, "tests", "hastub")
            cmd = [sys.executable, os.path.abspath(__file__),
                   "--capture", root, out_path]
            if everything:
                cmd.append("--all")
            subprocess.run(cmd, check=True, env=env)
            outputs[label] = json.load(open(out_path))
            print(f"  captured {len(outputs[label])} scenarios from {label}")

        branch, baseline = outputs["branch"], outputs["baseline"]
        drifted = 0
        claimed_hits = []
        may_drift_hits: list[str] = []
        for name in sorted(set(branch) | set(baseline)):
            if name not in baseline:
                # Added by this branch, so there is nothing to compare --
                # but a PR that adds a scenario may still have claimed it,
                # and a claim that goes unrecorded here reads as stale.
                if name in claims:
                    claimed_hits.append(name)
                    print(f"  CLAIMED {name}: added by this branch, no baseline "
                          f"on {ref} ({claims[name]})")
                else:
                    print(f"  new   {name}: no baseline on {ref} (added by this branch)")
                continue
            if name not in branch:
                if name in claims:
                    claimed_hits.append(name)
                    print(f"  CLAIMED {name}: removed ({claims[name]})")
                else:
                    drifted += 1
                    print(f"  DRIFT {name}: scenario removed by this branch")
                continue
            diffs: list[str] = []
            _diff_leaves(baseline[name], branch[name], name, diffs)
            if not diffs and name in may_drift:
                # Not "ok": nothing was proved. This machine's solve of a
                # non-reproducible fixture simply did not land on the part
                # the change touches, and another machine's may.
                print(f"  may-drift {name}: did not move here ({may_drift[name]})")
            elif not diffs:
                print(f"  ok    {name} is byte-identical to {ref} here")
            elif name in may_drift:
                may_drift_hits.append(name)
                print(f"  MAY-DRIFT {name}: {len(diffs)} leaves moved "
                      f"({may_drift[name]})")
                # Printed in full rather than truncated at three: nobody can
                # judge these from a runner's verdict, so the log is the only
                # place the evidence exists.
                for line in diffs[:10]:
                    print(f"         {line}")
            elif name in claims:
                claimed_hits.append(name)
                print(f"  CLAIMED {name}: {len(diffs)} leaves moved ({claims[name]})")
                for line in diffs[:3]:
                    print(f"         {line}")
            else:
                drifted += 1
                print(f"  DRIFT {name}: {len(diffs)} leaves moved vs {ref}")
                for line in diffs[:5]:
                    print(f"         {line}")

        # Staleness is only meaningful for scenarios this run captured. The
        # five-fixture mode captures SENSITIVE and nothing else, so a claim
        # for config_flow or a coord_* capture could never land in
        # `claimed_hits` there -- it is unjudged, not stale, and calling it
        # stale failed local strict runs on a perfectly good claim file.
        judged = set(claims) if everything else set(claims) & set(SENSITIVE)
        unjudged = sorted(set(claims) - judged)
        stale = sorted(judged - set(claimed_hits))
        for name in stale:
            print(f"  STALE claim for {name}: nothing drifted, remove it")
        for name in unjudged:
            print(f"  unjudged claim for {name}: not captured in this mode")

        if may_drift_hits:
            print(f"\n{len(may_drift_hits)} MAY-DRIFT SCENARIO(S) MOVED, unjudged")
            print("These are the fixtures this gate declares non-reproducible")
            print("across BLAS builds, so a diff in them is not evidence about")
            print("this branch either way and is printed rather than judged:")
            for name in may_drift_hits:
                print(f"  {name}: {may_drift[name]}")
            print("Read the leaf diffs above. Never re-record them on a")
            print("machine where golden.py already reports them as DIFF.")

        if unjudged:
            print(f"\nNOT EVALUATED: {len(unjudged)} claim(s) name scenarios that")
            print("this mode does not capture, so they were neither honoured")
            print(f"nor called stale here: {', '.join(unjudged)}")
            print("Only the five sensitive fixtures are captured without")
            print("--all; run with --all (as CI does) to judge the rest.")

        if drifted:
            print(f"\n{drifted} UNCLAIMED DRIFT(S) vs {ref}")
            print("This branch moved scenarios the baseline does not move in")
            print("this environment: a regression, or a change that must be")
            print("claimed in tests/golden/claimed_drift.txt and justified in")
            print("the PR. Never re-record the five sensitive fixtures on a")
            print("machine where golden.py already reports them as DIFF.")
        if stale:
            # A stale claim is not drift and must not be counted as one: the
            # three historical CI failures on main printed "N UNCLAIMED
            # DRIFT(S)" and a paragraph about regressions when nothing had
            # moved at all, which is what made them so hard to read.
            print(f"\n{len(stale)} STALE CLAIM(S) vs {ref}")
            print("Nothing drifted for these -- they are entries in")
            print("tests/golden/claimed_drift.txt that matched no scenario:")
            for name in stale:
                print(f"  {name}: {claims[name]}")
            print("A claim nothing uses would silently excuse the next")
            print("accidental drift, so it fails. Delete these lines; the")
            print("behaviour they describe is already gone or never came.")
        if drifted or stale:
            return 1
        n = len(set(branch) | set(baseline))
        print(f"\nNO UNCLAIMED DRIFT: {n} scenario(s) checked against {ref}")
        return 0
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree],
            cwd=repo, capture_output=True,
        )
        # The worktree call above unregisters the checkout but leaves the
        # mkdtemp that held it, so every run used to leave a directory
        # behind in /tmp. A gate that litters the disk it runs on is its
        # own slow failure.
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
