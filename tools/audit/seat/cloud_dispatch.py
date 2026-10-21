#!/usr/bin/env python3
"""Render the cloud-runner trigger payload for one seat.

    python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer|fixer|probe \
        --head <40-hex> [--pr N] [--topic T] [--nonce N] [--brief FILE] \
        [--env-id ID] [--model M] [--repo OWNER/NAME] [--overlay FILE] [--out FILE]
    python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer|fixer|probe --group G --model M \
        [--roster-ref REF] [--head <40-hex>] [--pr N] [--nonce N] [--overlay FILE]
    python3 -I tools/audit/seat/cloud_dispatch.py --self-test

THE GROUP PATH (`--group`, or `dispatch_group()` for a caller that hosts it) takes
a role, a roster group and a model. The roster at REF (default origin/main) gives
the brief, the topic (the group's branch) and the repository; the head is that
ref's tip; the environment id comes from the overlay / $HPO_CLOUD_ENV_ID. The
payload is rendered by the same `render` as the flag path, so it is the flag
path's byte for byte, and is published, with its prompt, on origin as
`dispatch/<role>-<topic>` (PAYLOAD.json, PROMPT.md); the one line printed is that
ref name. A standing trigger whose prompt fetches the ref it is fired with
needs nothing else. A render refusal (below) pushes nothing.

WHAT IT RENDERS. The whole `job_config.ccr` object a cloud runner's trigger
update takes: `environment_id`, `session_context` (`allowed_tools`, `model`,
`sources`) and `events` (one user message, the seat's prompt). Every trigger
update resends the full ccr and then `run`s it, so a payload is always whole;
this prints exactly that and never a patch. INSTRUMENTS.md has the measured
shape of a cloud seat.

WHERE THE ENVIRONMENT COMES FROM. Never from this file. The environment id,
the model and the repository are a flag, else the overlay file (`--overlay`, or
$HPO_CLOUD_OVERLAY, a JSON object with `environment_id`, `model`, `repo`), else
$HPO_CLOUD_ENV_ID / $HPO_CLOUD_MODEL / $HPO_CLOUD_REPO. One of the three is
required: a missing value is a refusal, not a default that goes stale.

THE BRIEF is read and INLINED at render time, because the runner snapshots the
message at `run`: a brief edited afterwards reaches no running seat.

WHAT IT REFUSES (exit 2, nothing printed on stdout):
  * a head that is not exactly 40 lowercase hex digits;
  * a reviewer with an empty bus nonce (the relay matches the verdict to its
    dispatch by it), or a reviewer with no --pr;
  * a fixer or probe with no --topic (the return refs are named by it);
  * a missing environment id, model or repository;
  * any home-directory path in the rendered text (ref_privacy.HOME_DIR, the
    host-path grammar): the payload is published to the runner, and a seat's
    prompt may not name the machine it was written on;
  * an unreadable brief;
  * with --group: a group the roster does not name, a roster that cannot be read,
    and a ref name that would publish the host (ref_privacy.refusal).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _sibling(name: str):
    """Load a sibling module by path (`python3 -I` puts no script dir on sys.path)."""
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # @dataclass reads sys.modules[cls.__module__]
    spec.loader.exec_module(mod)
    return mod


ref_privacy = _sibling("ref_privacy")
roster_lib = _sibling("roster_lib")
HOME = re.compile(ref_privacy.HOME_DIR)
LOWER_HEX = frozenset("0123456789abcdef")


def is_head(head: str) -> bool:
    """Exactly 40 lowercase hex digits (not a regex: the grammar is policy_lint's to own)."""
    return len(head) == 40 and set(head) <= LOWER_HEX

ROLES = ("reviewer", "fixer", "probe")
#: The tools a cloud seat is allowed; the same for every role (measured shape).
ALLOWED_TOOLS = ["preset:default", "Bash", "Glob", "Grep", "Read", "Write",
                 "BashOutput", "KillBash", "Monitor"]


class Refusal(Exception):
    pass


def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, brief: str) -> str:
    who = {"reviewer": "CLOUD REVIEWER", "fixer": "CLOUD FIXER", "probe": "CLOUD PROBE"}[role]
    subject = f"PR #{pr} of {repo}, at head {head}" if pr else f"{repo}, topic {topic}, at head {head}"
    first = f"{who} seat for {subject}."
    if nonce:
        first += f" Bus nonce: {nonce}."
    first += " Never send push notifications."
    setup = ("Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) "
             "is on PATH from the environment. Run anything heavy in the background with Monitor "
             "and no timeout.")
    if role == "reviewer":
        body = (
            "Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them "
            f"exactly. Fetch the PR head with `git fetch origin {head}`; the PR body is in the PR. "
            "Verify each claim adversarially: mutate the fix and check the tests fail, and check "
            "every figure in the body at this head. Check that it merges with origin/main "
            "(`git merge-tree --write-tree`) and read CI on this head from the check-runs API.\n"
            f"Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is "
            f"exactly `Fix review: merge {head}` or `Fix review: blocked {head} <class>: <reason>` (no brackets; "
            f"the class is lower-case letters and dashes), in the format the role file gives, "
            f"then a blank line, then `bus-nonce: {nonce}`; put the evidence in `ev/` beside it, and make at least one file under `ev/` contain the full 40-hex head "
            f"`{head}` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): "
            f"bus.sh refuses a verdict whose `ev/` names no head. Do NOT run "
            f"bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict "
            f"there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one "
            f"parentless commit with a private index and touches no branch of your checkout: "
            f"`R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && "
            f"cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr "
            f"sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=seat "
            f"-c user.email=seat@users.noreply.github.com commit-tree $T -m \"verdict {pr} {head}\") && "
            f"git -C $R push -q origin $C:refs/heads/probe/rev-{pr}-{nonce.strip()[:8]}`. "
            "That ref is the return signal. Do not post comments, approve or merge.")
    elif role == "fixer":
        body = (
            "Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, "
            f"in a worktree of your own cut from origin/main. Fetch {head} for the base you were given.\n"
            f"Output: push the code to refs/heads/handoff/{topic}, then write the PR body and run "
            f"`bash tools/audit/seat/body_push.sh {topic} <body.md>`, which pushes "
            f"refs/heads/handoff-body/{topic}; that second push is the return signal. Push nothing "
            "else, open no pull request and write no delivery row. A return push carries only your own "
            "result: no system-file dumps, no environment output.")
    else:
        body = (
            "Role: a read-only probe. Measure what the brief below asks against the tree at "
            f"{head} (`git fetch origin {head}`); change no tracked file and send no code to any ref.\n"
            f"Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh "
            f"{topic} <result.md>`, which pushes refs/heads/handoff-body/{topic}; that push is the "
            "return signal. A return push carries only your own result tokens.")
    tail = ("Never write to any branch except your return refs. Never work around a hook or a refusal; "
            "report it in your result instead.")
    text = "\n".join([first, setup, body, tail]) + "\n"
    if brief:
        text += "\nBrief (snapshotted when this payload was rendered):\n" + brief.rstrip("\n") + "\n"
    return text


def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str = "",
           topic: str = "", nonce: str = "", brief: str = "") -> dict:
    if role not in ROLES:
        raise Refusal(f"role must be one of {', '.join(ROLES)}")
    if not is_head(head or ""):
        raise Refusal("head must be exactly 40 lowercase hex digits")
    if role == "reviewer":
        if not nonce.strip():
            raise Refusal("a reviewer needs a non-empty bus nonce")
        if not pr.isdigit():
            raise Refusal("a reviewer needs --pr <number>")
    elif not topic.strip() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", topic):
        raise Refusal("a fixer or probe needs --topic (letters, digits, . _ -)")
    for name, val in (("environment id", env_id), ("model", model), ("repo", repo)):
        if not (val or "").strip():
            raise Refusal(f"no {name}: pass a flag, an overlay entry or its HPO_CLOUD_* variable")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise Refusal("repo must be OWNER/NAME")
    text = _prompt(role, repo, pr, head, topic, nonce, brief)
    payload = {"job_config": {"ccr": {
        "environment_id": env_id,
        "session_context": {
            "allowed_tools": list(ALLOWED_TOOLS),
            "model": model,
            "sources": [{"git_repository": {"url": f"https://github.com/{repo}"}}]},
        "events": [{"data": {"type": "user", "message": {"role": "user", "content": text}}}]}}}
    m = HOME.search(json.dumps(payload))
    if m:
        raise Refusal(f"the rendered payload names a home directory ({m.group(0)!r}); "
                      "write the brief with repo-relative paths")
    return payload


# ------------------------------------------------------------ the group path
#
# `dispatch_group` is the whole call for one seat: role, group, model. It is a
# function, not a CLI step, so the beat (R10-ORCH-MACHINERY) can host it as it
# is. It renders through `render`, the same code the flag path runs, so the
# payload is the flag path's byte for byte; what it adds is where the inputs
# come from and where the output goes.

#: The ref namespace a seat fetches its dispatch from: `dispatch/<role>-<topic>`.
DISPATCH_NS = "dispatch"
#: Identity of the commit that carries a dispatch (a constant, never the host's).
_SEAT = ("-c", "user.name=seat", "-c", "user.email=seat@users.noreply.github.com")


def _git(repo_dir: str, *argv: str, stdin: str | None = None) -> str:
    r = subprocess.run(["git", "-C", repo_dir, *argv], input=stdin, capture_output=True, text=True)
    if r.returncode:
        raise Refusal(f"git {argv[0]} failed: {(r.stderr or r.stdout).strip()[:200]}")
    return r.stdout


def _topic_of(group: dict) -> str:
    """The topic a group's seat returns under: its branch, less the `handoff/` prefix."""
    return roster_lib.branch_of(group).removeprefix("handoff/")


def _publish(repo_dir: str, ref: str, files: dict[str, str]) -> None:
    """Append one commit holding `files` to `refs/heads/<ref>` on origin.

    The first commit has no parent; later ones fast-forward, so a re-dispatch
    needs no force-push. An identical tree adds no commit. A fetch that fails
    for any reason but a missing ref refuses: a parentless commit would only be
    refused by the push as a non-fast-forward, never rewritten."""
    why = ref_privacy.refusal(ref, (("the dispatch message", f"dispatch: {ref}"),))
    if why:
        raise Refusal(f"the dispatch ref would publish the host: {why}")
    tip = _git(repo_dir, "ls-remote", "origin", f"refs/heads/{ref}").split()[:1]
    if tip:
        _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")
    entries = "".join(f"100644 blob {_git(repo_dir, 'hash-object', '-w', '--stdin', stdin=text).strip()}\t{name}\n"
                      for name, text in sorted(files.items()))
    tree = _git(repo_dir, "mktree", stdin=entries).strip()
    if tip and _git(repo_dir, "rev-parse", f"{tip[0]}^{{tree}}").strip() == tree:
        return
    commit = _git(repo_dir, *_SEAT, "commit-tree", tree, *(["-p", tip[0]] if tip else []),
                  "-m", f"dispatch: {ref}").strip()
    _git(repo_dir, "push", "-q", "origin", f"{commit}:refs/heads/{ref}")


def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
                   roster_ref: str = roster_lib.MAIN_REF, head: str = "", pr: str = "", nonce: str = "",
                   overlay: str | None = None, environ=None) -> str:
    """Render the seat for `group_id` from the roster, publish it, return its ref name.

    The roster at `roster_ref` of `repo_dir` gives the brief, the topic (the
    group's branch) and the repository; the head is that ref's tip unless one is
    passed (a reviewer's is the PR head); the environment id comes from the
    known seat environment (`--overlay` / $HPO_CLOUD_ENV_ID). Nothing is pushed
    unless the payload rendered, so every `render` refusal holds here too."""
    try:
        roster = roster_lib.show_roster(repo_dir, roster_ref)
    except roster_lib.RosterNotFound as e:
        raise Refusal(str(e))
    group = roster_lib.groups_of(roster).get(group_id)
    if group is None:
        raise Refusal(f"{group_id} is not a group of the roster at {roster_ref}")
    environ = os.environ if environ is None else environ
    known = _config(argparse.Namespace(overlay=overlay, env_id=None, model=model, repo=None), environ)
    topic = _topic_of(group)
    payload = render(role, head or _git(repo_dir, "rev-parse", f"{roster_ref}^{{commit}}").strip(),
                     env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
                     pr=pr, topic=topic, nonce=nonce, brief=group.get("brief") or "")
    ref = f"{DISPATCH_NS}/{role}-{topic}"
    _publish(repo_dir, ref, {
        "PAYLOAD.json": json.dumps(payload),
        "PROMPT.md": payload["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]})
    return ref


def _config(args: argparse.Namespace, environ=None) -> dict:
    environ = os.environ if environ is None else environ
    ov: dict = {}
    path = args.overlay or environ.get("HPO_CLOUD_OVERLAY")
    if path:
        try:
            ov = json.loads(Path(path).read_text())
        except (OSError, ValueError) as e:
            raise Refusal(f"unreadable overlay: {e.__class__.__name__}")
        if not isinstance(ov, dict):
            raise Refusal("overlay must be a JSON object")

    def pick(flag, key, var):
        return flag or ov.get(key) or environ.get(var) or ""
    return {"env_id": pick(args.env_id, "environment_id", "HPO_CLOUD_ENV_ID"),
            "model": pick(args.model, "model", "HPO_CLOUD_MODEL"),
            "repo": pick(args.repo, "repo", "HPO_CLOUD_REPO")}


def _group_checks(check) -> None:
    """The group path (`dispatch`): offline, against a throwaway origin and checkout."""
    import contextlib
    import io
    import subprocess
    import tempfile
    sys.path.insert(0, str(HERE.parents[2] / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init

    def git(cwd, *a):
        return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout

    env = {"HPO_CLOUD_ENV_ID": "env_x", "HPO_CLOUD_MODEL": "ignored"}
    users = "/" + "Users/"
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        origin, work = Path(td) / "origin.git", Path(td) / "work"
        throwaway_git_init(origin, "-q", "--bare")
        throwaway_git_init(work, "-q", "-b", "main")
        roster = work / roster_lib.ROSTERS_DIR / "wave-r10-groups.json"
        roster.parent.mkdir(parents=True)

        def land(groups):
            roster.write_text(json.dumps({"repo": "owner/name", "groups": groups}))
            git(work, "add", "-A")
            git(work, "commit", "-q", "-m", "roster")
            git(work, "push", "-q", "-f", str(origin), "main")
            git(work, "fetch", "-q", str(origin), "+main:refs/remotes/origin/main")
        grp = {"group": "R10-X", "brief": "Fix the thing in tools/x.py.\n", "resume": {"branch": "handoff/r10-x"}}
        bad = {"group": "R10-BAD", "brief": "cd " + users + "someone/work"}
        land([grp, bad])
        git(work, "remote", "add", "origin", str(origin))
        tip = git(work, "rev-parse", "origin/main").strip()

        def dispatch(group="R10-X", role="fixer", **kw):
            return dispatch_group(role, group, "m-1", repo_dir=str(work), **{"environ": env, **kw})

        def refused(*a, **kw):
            try:
                dispatch(*a, **kw)
            except Refusal:
                return True
            return False

        def fetched(line, name):
            git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
            return git(work, "show", "FETCH_HEAD:" + name)

        line = dispatch()
        check("a group dispatch prints one short line, the ref name",
              line == "dispatch/fixer-r10-x" and "\n" not in line and " " not in line)
        brief = work / "brief.txt"
        brief.write_text(grp["brief"])
        old = io.StringIO()
        with contextlib.redirect_stdout(old):
            rc = main(["--role", "fixer", "--head", tip, "--topic", "r10-x", "--brief", str(brief),
                       "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"])
        check("the printed line round-trips to a payload byte-identical to today's flag path",
              rc == 0 and fetched(line, "PAYLOAD.json") == old.getvalue().rstrip("\n"))
        msg = json.loads(fetched(line, "PAYLOAD.json"))["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
        check("the ref carries the prompt the payload carries", fetched(line, "PROMPT.md") == msg)
        check("the roster brief is inlined and the roster tip is the head",
              "Fix the thing in tools/x.py." in msg and tip in msg)
        check("a re-dispatch of the same brief moves no ref", dispatch() == line
              and git(work, "ls-remote", str(origin), "refs/heads/" + line).split()[0]
              == git(work, "rev-parse", "FETCH_HEAD").strip())
        first = git(work, "rev-parse", "FETCH_HEAD").strip()
        land([{**grp, "brief": "Changed.\n"}, bad])
        dispatch()
        git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
        check("a changed brief fast-forwards the ref",
              git(work, "rev-parse", "FETCH_HEAD^").strip() == first and "Changed." in fetched(line, "PROMPT.md"))
        check("the dispatch ref is on origin only once the render passed (null control for the refusals)",
              git(work, "ls-remote", str(origin), "refs/heads/dispatch/*").count("\n") == 1)
        check("a host path in a roster brief refuses and pushes nothing",
              refused("R10-BAD") and "r10-bad" not in git(work, "ls-remote", str(origin)))
        check("a group the roster does not name refuses", refused("R10-NOPE"))
        check("an unknown environment refuses", refused(environ={}))
        check("a reviewer needs its pr and nonce, as on the flag path", refused(role="reviewer"))
        check("a reviewer dispatch with pr and nonce renders", dispatch(role="reviewer", pr="7", nonce="abc123")
              == "dispatch/reviewer-r10-x")




def self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + bool(cond), failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    base = dict(env_id="env_x", model="m-1", repo="owner/name")
    head = "0123456789abcdef" * 2 + "01234567"

    def refused(role="reviewer", h=head, **kw) -> bool:
        a = {**base, "pr": "7", "topic": "t-1", "nonce": "abc123", **kw}
        try:
            render(role, h, **a)
        except Refusal:
            return True
        return False

    ok = render("reviewer", head, **base, pr="7", nonce="abc123")
    ccr = ok["job_config"]["ccr"]
    check("a reviewer renders (null control for every refusal)", not refused())
    check("the ccr carries environment_id, session_context and one user event",
          set(ccr) == {"environment_id", "session_context", "events"} and len(ccr["events"]) == 1
          and set(ccr["session_context"]) == {"allowed_tools", "model", "sources"})
    msg = ccr["events"][0]["data"]["message"]["content"]
    check("the prompt names the head, the nonce and the probe return ref",
          head in msg and "abc123" in msg and "probe/rev-7-abc123" in msg and "bus-nonce: abc123" in msg)
    check("the reviewer is told a file under ev/ must contain the full head (bus.sh push-verdict requires it)",
          "file under `ev/` contain the full 40-hex head `" + head + "`" in msg and "ev/HEAD.txt" in msg)
    check("the reviewer is given the unbracketed first-line grammar",
          "blocked " + head + " <class>: <reason>" in msg and "[class: reason]" not in msg)
    check("the prompt builds no repository (throwaway_git.py --check refuses a raw init)",
          re.search(r"git\s+ini[t]", msg) is None and "commit-tree" in msg)
    check("the reviewer is told not to run bus.sh and the prompt runs no bus.sh push-verdict",
          "Do NOT run bus.sh" in msg and "push-verdict" not in msg and "refs/heads/review" not in msg)
    check("the source is the repo", ccr["session_context"]["sources"][0]["git_repository"]["url"]
          == "https://github.com/owner/name")
    check("a fixer renders and names both return refs",
          not refused("fixer", nonce="") and
          all(r in render("fixer", head, **base, topic="t-1")["job_config"]["ccr"]["events"][0]
              ["data"]["message"]["content"] for r in ("handoff/t-1", "handoff-body/t-1")))
    check("a probe renders without a nonce", not refused("probe", nonce=""))
    check("a 39-hex head is refused", refused(h=head[:-1]))
    check("a 41-hex head is refused", refused(h=head + "0"))
    check("an upper-case head is refused", refused(h=head.upper()))
    check("a non-hex head is refused", refused(h="g" * 40))
    check("an empty reviewer nonce is refused", refused(nonce=""))
    check("a blank reviewer nonce is refused", refused(nonce="  "))
    check("a reviewer without --pr is refused", refused(pr=""))
    check("a fixer without --topic is refused", refused("fixer", topic=""))
    check("a topic with a slash is refused", refused("probe", topic="a/b"))
    check("a missing environment id is refused", refused(env_id=""))
    check("a missing model is refused", refused(model=""))
    check("a repo that is not OWNER/NAME is refused", refused(repo="name"))
    check("an unknown role is refused", refused("author"))
    # Built from parts: a literal home path would be refused in this very file.
    users, home_ = "/" + "Users/", "/" + "home/"
    for label, home in (("a macOS home", users + "someone/work"), ("a linux home", home_ + "someone/work"),
                        ("a public account's home", home_ + "user/heatpump_optimizer")):
        check(f"{label} in the brief is refused", refused(brief=f"cd {home}"))
    check("a home path in the nonce is refused", refused(nonce="/" + "Users/x/y"))
    check("a repo-relative brief passes (null control)", not refused(brief="read tools/audit/seat/bus.sh"))
    check("the brief is inlined",
          "FIND-ME" in render("fixer", head, **base, topic="t", brief="FIND-ME")["job_config"]["ccr"]
          ["events"][0]["data"]["message"]["content"])
    check("the rendered text carries no home directory", HOME.search(json.dumps(ok)) is None)
    _group_checks(check)
    print(f"cloud_dispatch self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="cloud_dispatch.py", description=__doc__.split("\n")[0])
    ap.add_argument("--role", required=True, choices=ROLES)
    ap.add_argument("--head")
    ap.add_argument("--group", help="a roster group: publish its seat to a dispatch ref, print the ref name")
    ap.add_argument("--roster-ref", default=roster_lib.MAIN_REF)
    ap.add_argument("--pr", default="")
    ap.add_argument("--topic", default="")
    ap.add_argument("--nonce", default="")
    ap.add_argument("--brief")
    ap.add_argument("--env-id")
    ap.add_argument("--model")
    ap.add_argument("--repo")
    ap.add_argument("--overlay")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    try:
        if args.group:
            if not args.model:
                raise Refusal("--group needs --model")
            print(dispatch_group(args.role, args.group, args.model, roster_ref=args.roster_ref,
                                 head=args.head or "", pr=args.pr, nonce=args.nonce, overlay=args.overlay))
            return 0
        if not args.head:
            raise Refusal("--head is required without --group")
        brief = ""
        if args.brief:
            try:
                brief = Path(args.brief).read_text()
            except OSError as e:
                raise Refusal(f"unreadable brief: {e.__class__.__name__}")
        payload = render(args.role, args.head, pr=args.pr, topic=args.topic, nonce=args.nonce,
                         brief=brief, **_config(args))
    except Refusal as e:
        print(f"cloud_dispatch: refused: {e}", file=sys.stderr)
        return 2
    out = json.dumps(payload)
    if args.out:
        Path(args.out).write_text(out)
        print(args.out)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
