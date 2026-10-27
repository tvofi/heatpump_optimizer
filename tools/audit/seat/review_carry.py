#!/usr/bin/env python3
"""review_carry.py -- does a new head carry branch-authored change since the
head a review measured?

THE RULING (tvofi, 2026-10-27, verbatim): "if there are no code changes, the
previous review can be carried". This makes it mechanical, because a seat that
has to decide by eye whether a move carried code will eventually decide wrong
in the direction that merges unreviewed code (R10-REVIEW-CARRY).

THE TEST IS A COMMIT RANGE, NOT AN OPINION:

    git rev-list --count <reviewed-head>..<new-head> --not origin/main

Zero, or a count whose commits are all merges, means no branch-authored
change and the prior verdict carries: this prints CARRY. A merge authors no
code of its own -- what it joins is main's history (`--not` drops it) or
branch commits, which are in the range as non-merge commits and counted -- so
a merge of the branch's own previous head, the shape update_pr.sh re-cuts one
into, is not a change either. Any non-merge commit in that range means the
head carries code and takes a fresh review: this prints FRESH-REVIEW. A body
rewrite never by itself voids a verdict, because it is not a commit in the
range. A claim-file resolution, or a `ci:`/`claims:` bot commit, inside the
range IS a change when it lands as a commit: it is a non-merge commit, and no
subject is exempt -- the range is read before the merge is trusted. A claim
file resolved INSIDE a merge is not read here; `tools/pr/app_approve.sh
--carry` reads it, and a pure union of both parents is the only resolution it
accepts. (This answers the reviewer's verdict carrying. `merge_train.py`'s
owner-approval carry answers a different question -- the owner's approval, not
the reviewer's verdict -- and is not this instrument.)

THE MEASURED INSTANCES, the null control: one command, opposite answers.

    #2876  253dc4867 -> e0237e6d0  branch-only 1, the merge itself -> CARRY
    #2876  253dc4867 -> d08647f05  branch-only 3, all merges       -> CARRY
    #2854  fccb88371 -> 9f424cf74  branch-only 41 (incl. ce277f1d6) -> FRESH-REVIEW

DEGENERATE CASES, each explicit rather than a guess:
  - an unknown sha cannot be decided: CANNOT DECIDE, exit 2, no verdict line;
  - the reviewed head is the new head (head did not move): CARRY;
  - the reviewed head is an ancestor of the new head: the range is read;
  - the new head is not a descendant of the reviewed head (force-push): the
    branch-only range is still counted and printed, and the answer is
    FRESH-REVIEW, because a rewritten head is not the head the review measured.

Usage:
    review_carry.py <reviewed-head> <new-head> [--main <ref>] [--verdict-only]
                    [--repo <dir>]
    review_carry.py --self-test

Exit: 0 CARRY, 1 FRESH-REVIEW, 2 cannot decide.

The verdict is also the last line, `review_carry: CARRY|FRESH-REVIEW`, so a
seat can paste the whole output into a brief or a verdict.
"""
import os
import subprocess
import sys
import tempfile

CARRY = "CARRY"
FRESH = "FRESH-REVIEW"


class Undecidable(Exception):
    pass


def git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout, proc.stderr


def must(repo, *args):
    code, out, err = git(repo, *args)
    if code != 0:
        raise Undecidable("git %s failed: %s" % (" ".join(args), err.strip()[:200]))
    return out


def resolve_commit(repo, rev):
    code, out, _ = git(repo, "rev-parse", "--verify", "--quiet", rev + "^{commit}")
    sha = out.strip()
    if code != 0 or len(sha) != 40:
        raise Undecidable("unknown sha %r: no commit of that name in %s" % (rev, repo))
    return sha


def is_ancestor(repo, a, b):
    code, _, _ = git(repo, "merge-base", "--is-ancestor", a, b)
    return code == 0


def parents_of(repo, commit):
    fields = must(repo, "rev-list", "--parents", "-n", "1", commit).split()
    return fields[1:]


def branch_only(repo, reviewed, new, main):
    """The range the rule names: reviewed..new, excluding main's history."""
    count = int(must(repo, "rev-list", "--count", "%s..%s" % (reviewed, new),
                     "--not", main).strip() or "0")
    commits = []
    if count:
        for line in must(repo, "log", "--reverse", "--format=%H%x09%s",
                         "%s..%s" % (reviewed, new), "--not", main).splitlines():
            if line.strip():
                sha, _, subject = line.partition("\t")
                commits.append((sha, subject))
    return count, commits


def classify(repo, reviewed, new, main):
    """-> (verdict, reason, count, commits). Raises Undecidable when it cannot
    judge. `main` is a resolved commit id."""
    if reviewed == new:
        return CARRY, "head did not move", 0, []
    descendant = is_ancestor(repo, reviewed, new)
    count, commits = branch_only(repo, reviewed, new, main)
    carrying = []
    for sha, subject in commits:
        # A merge joins history; it does not author a commit. What it joins is
        # either main's (excluded by --not) or branch commits, which the range
        # returns as non-merge commits of their own. So it counts as carrying
        # only if it is not a merge at all.
        if len(parents_of(repo, sha)) < 2:
            carrying.append((sha, subject))
    if not descendant:
        reason = ("force-push: %s is not a descendant of %s"
                  % (new[:9], reviewed[:9]))
        if carrying:
            reason += "; %d of %d branch-only commit(s) carry code" % (
                len(carrying), count)
        return FRESH, reason, count, commits
    if count == 0:
        return CARRY, "no branch-only commit", 0, []
    if carrying:
        return (FRESH,
                "%d of %d branch-only commit(s) carry code"
                % (len(carrying), count),
                count, commits)
    return (CARRY,
            "all %d branch-only commit(s) are merges" % count,
            count, commits)


def render(reviewed, new, main_name, verdict, reason, count, commits):
    lines = ["review_carry: %s -> %s  main=%s" % (reviewed[:9], new[:9], main_name),
             "  branch-only commits: %d" % count,
             "  why: %s" % reason]
    for sha, subject in commits:
        lines.append("  %s  %s" % (sha[:9], subject))
    lines.append("review_carry: %s" % verdict)
    return "\n".join(lines)


def run(argv):
    args = list(argv)
    main_name = "origin/main"
    verdict_only = False
    repo = None
    positional = []
    while args:
        a = args.pop(0)
        if a in ("-h", "--help"):
            sys.stdout.write(__doc__)
            return 0
        if a == "--verdict-only":
            verdict_only = True
        elif a == "--main":
            if not args:
                raise Undecidable("--main needs a ref")
            main_name = args.pop(0)
        elif a == "--repo":
            if not args:
                raise Undecidable("--repo needs a directory")
            repo = args.pop(0)
        elif a.startswith("--"):
            raise Undecidable("unknown argument %r" % a)
        else:
            positional.append(a)
    if len(positional) != 2:
        raise Undecidable("usage: review_carry.py <reviewed-head> <new-head> "
                          "[--main <ref>] [--verdict-only] [--repo <dir>]")
    repo = repo or os.getcwd()
    if not os.path.isdir(repo):
        raise Undecidable("not a directory: %s" % repo)
    reviewed = resolve_commit(repo, positional[0])
    new = resolve_commit(repo, positional[1])
    main = resolve_commit(repo, main_name)
    verdict, reason, count, commits = classify(repo, reviewed, new, main)
    if verdict_only:
        print(verdict)
    else:
        print(render(reviewed, new, main_name, verdict, reason, count, commits))
    return 0 if verdict == CARRY else 1


# ---- self-test -------------------------------------------------------------
def _t(repo, *args):
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, env=_GIT_ENV)
    if proc.returncode != 0:
        raise SystemExit("self-test: git %s failed: %s"
                         % (" ".join(args), proc.stderr.strip()))
    return proc.stdout


def _commit(repo, message):
    _t(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
       "--allow-empty", "-m", message)
    return _t(repo, "rev-parse", "HEAD").strip()


_GIT_ENV = {}


def self_test():
    global _GIT_ENV
    failures = 0
    checks = 0

    def check(name, got, want):
        nonlocal failures, checks
        checks += 1
        if got != want:
            failures += 1
            print("  FAIL %s: got %r, want %r" % (name, got, want))
        else:
            print("  ok   %s" % name)

    root = tempfile.mkdtemp(prefix="review_carry_selftest.")
    _GIT_ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
                    GIT_CONFIG_SYSTEM=os.devnull, GIT_AUTHOR_NAME="t",
                    GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                    GIT_COMMITTER_EMAIL="t@t")
    origin = os.path.join(root, "origin.git")
    seat = os.path.join(root, "seat")
    _t(root, "init", "-q", "--bare", origin)
    _t(root, "init", "-q", seat)
    _t(seat, "remote", "add", "origin", origin)
    _t(seat, "checkout", "-q", "-b", "main")
    _t(seat, "commit", "-q", "--allow-empty", "-m", "base")
    base = _t(seat, "rev-parse", "HEAD").strip()
    _t(seat, "push", "-q", "origin", "HEAD:refs/heads/main")
    # main advances on its own line, so a branch can merge it in.
    _t(seat, "checkout", "-q", "-b", "main2", "main")
    _t(seat, "commit", "-q", "--allow-empty", "-m", "main moves on")
    main1 = _t(seat, "rev-parse", "HEAD").strip()
    _t(seat, "push", "-q", "origin", "HEAD:refs/heads/main")
    _t(seat, "checkout", "-q", "main")
    _t(seat, "reset", "-q", "--hard", main1)
    # the reviewed head: reviewed work on a branch
    _t(seat, "checkout", "-q", "-b", "fix/x", base)
    with open(os.path.join(seat, "code.txt"), "w") as fh:
        fh.write("reviewed\n")
    _t(seat, "add", "code.txt")
    reviewed = _commit(seat, "reviewed: the code")
    # a merge-only move: merge main1 in
    _t(seat, "merge", "-q", "--no-ff", "-m",
       "Merge remote-tracking branch 'origin/main' into fix/x", main1)
    merged = _t(seat, "rev-parse", "HEAD").strip()
    # update_pr.sh's re-cut: a merge whose second parent is the branch's own
    # previous head, so neither parent is main and the range is merges only.
    recut = _t(seat, "commit-tree",
               _t(seat, "rev-parse", merged + "^{tree}").strip(),
               "-p", reviewed, "-p", merged, "-m",
               "Merge commit 'x' into fix/x").strip()
    # a code move: a non-merge commit on top
    with open(os.path.join(seat, "code.txt"), "w") as fh:
        fh.write("changed\n")
    _t(seat, "add", "code.txt")
    coded = _commit(seat, "fix: change the code")
    # a bot-subject commit is still a non-merge commit: no exemption
    bot = _commit(seat, "ci: pin killed mutants")
    # a merge of a NON-main branch is a branch-authored change
    _t(seat, "checkout", "-q", "-b", "feat/y", merged)
    _commit(seat, "feat: unreviewed work")
    _t(seat, "checkout", "-q", "fix/x")
    _t(seat, "merge", "-q", "--no-ff", "-m", "Merge branch 'feat/y' into fix/x",
       "feat/y")
    feat_merge = _t(seat, "rev-parse", "HEAD").strip()

    def answer(rev, new, main="origin/main"):
        return classify(seat, resolve_commit(seat, rev), resolve_commit(seat, new),
                        resolve_commit(seat, main))

    v, why, n, cs = answer(reviewed, merged)
    check("a merge-only move answers CARRY", v, CARRY)
    check("the merge-only move's branch-only count is 1", n, 1)
    check("the merge it counted is the merge itself", cs[0][0], merged)

    v, _, n, _ = answer(reviewed, coded)
    check("a code move answers FRESH-REVIEW", v, FRESH)
    check("the code move's branch-only count is 2", n, 2)

    v, why, n, _ = answer(reviewed, recut)
    check("a re-cut merge of the branch's own previous head answers CARRY",
          v, CARRY)
    check("its branch-only count is 2, both merges", n, 2)

    v, _, _, _ = answer(reviewed, reviewed)
    check("head did not move answers CARRY", v, CARRY)

    v, _, _, _ = answer(reviewed, bot)
    check("a bot-subject commit is a code move", v, FRESH)

    v, _, _, _ = answer(reviewed, feat_merge)
    check("a merge of a non-main branch answers FRESH-REVIEW", v, FRESH)

    v, why, _, _ = answer(reviewed, merged, main="main")
    check("a newer main ref does not change the answer", v, CARRY)

    # force-push: a head that does not descend from the reviewed head
    _t(seat, "checkout", "-q", "-b", "fix/force", reviewed)
    _t(seat, "reset", "-q", "--hard", base)
    with open(os.path.join(seat, "code.txt"), "w") as fh:
        fh.write("rewritten\n")
    _t(seat, "add", "code.txt")
    forced = _commit(seat, "fix: rewritten history")
    v, why, _, _ = answer(reviewed, forced)
    check("a force-push answers FRESH-REVIEW", v, FRESH)
    check("the force-push names itself", why.startswith("force-push:"), True)

    try:
        answer("0" * 40, merged)
        check("an unknown sha cannot decide", "no error", "Undecidable")
    except Undecidable:
        check("an unknown sha cannot decide", "Undecidable", "Undecidable")

    print("review_carry self-test: %d checks, %d failed" % (checks, failures))
    return 0 if failures == 0 else 1


def main(argv):
    if not argv:
        sys.stderr.write("review_carry: CANNOT DECIDE: no arguments\n")
        return 2
    if argv[0] == "--self-test":
        return self_test()
    try:
        return run(argv)
    except Undecidable as exc:
        sys.stderr.write("review_carry: CANNOT DECIDE: %s\n" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
