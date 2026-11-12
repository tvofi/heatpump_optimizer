#!/usr/bin/env python3
"""Render the cloud-runner trigger payload for one seat.

    python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer|fixer|probe \
        --head <40-hex> [--pr N] [--topic T] [--nonce N] [--brief FILE] \
        [--env-id ID] [--model M] [--repo OWNER/NAME] [--overlay FILE] [--out FILE] [--publish]
    python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer|fixer|probe --group G --model M \
        [--roster-ref REF] [--head <40-hex>] [--pr N] [--nonce N] [--overlay FILE]
    python3 -I tools/audit/seat/cloud_dispatch.py --self-test

THE GROUP PATH (`--group`, or `dispatch_group()` for a caller that hosts it) takes
a role, a roster group and a model. The roster at REF (default: the round's
roster branch, roster_lib.default_roster_ref) gives the brief (`group_brief`: its
brief, `After:` and carries), the topic (the group's branch) and the repository; the head is --head, else origin/main's tip,
never the roster ref's (a seat forks from main, not from the roster branch); a
reviewer needs --head (the PR head) and takes its nonce from `bus.sh dispatch`, which
mints one or re-records --nonce; the environment id comes from the overlay /
$HPO_CLOUD_ENV_ID. The
payload is rendered by the same `publish_seat` as the flag path's --publish, so it
is that path's byte for byte, and is published, with its prompt, on origin as
`dispatch/<role>-<topic>` (PAYLOAD.json, PROMPT.md); the one line printed is that
ref name. A published payload's event is a stub, never the prompt itself (the
runner echoes the event; R10-FLY-CACHE-PROMPTS): the seat line, the footer ban,
and the commit holding PROMPT.md, pinned by SHA, never by the moving ref. The
prompt is committed first, alone, and PAYLOAD.json on top of it, since a commit
cannot name its own SHA. --publish
does the same on the flag path, to `dispatch/<role>-<topic>`, else
`dispatch/<role>-rev-<PR>`, and prints the payload as without it. A standing trigger whose prompt fetches the ref it is fired with
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

THE BRIEF is read and INLINED at render time, into the event or, published, into
PROMPT.md at the pinned commit: either way a brief edited afterwards reaches no
running seat, since a re-dispatch only moves the ref past that commit.

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
  * with --group: a model outside the family the roster rules for the role
    (`model_refusal`), a group the roster does not name, a roster that cannot be read,
    a reviewer without --head, a ref name that would publish the host
    (ref_privacy.refusal), and any flag the group path does not consume
    (--topic, --brief, --repo, --env-id, --out; GROUP_FLAGS gives each its reason).
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
proof_watch = _sibling("proof_watch")  # the bus-nonce line's one Python reader
HOME = re.compile(ref_privacy.HOME_DIR)
LOWER_HEX = frozenset("0123456789abcdef")


def is_head(head: str) -> bool:
    """Exactly 40 lowercase hex digits (not a regex: the grammar is policy_lint's to own)."""
    return len(head) == 40 and set(head) <= LOWER_HEX

ROLES = ("reviewer", "fixer", "probe", "designer", "design-reviewer")
#: The design steps' roles (decision 0014): topic is the roster group id, and each
#: writes one ref family through `bus.sh`.
DESIGN_ROLES = ("designer", "design-reviewer")
#: The tools a cloud seat is allowed; the same for every role (measured shape).
ALLOWED_TOOLS = ["preset:default", "Bash", "Glob", "Grep", "Read", "Write",
                 "BashOutput", "KillBash", "Monitor"]


#: The owner's ban on a tool's attribution (tvofi, 2026-10-22: "make this ban
#: persistent"), stated to every role in one line. .claude/settings.json's
#: `attribution` hides the harness's own lines; ref_privacy.py refuses the rest.
FOOTER_BAN = ("Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai "
              "session link in any commit, pull-request body or comment you produce; check your commits "
              "with `git log --format=%B` before pushing.")


#: The identity a dispatch commit and a writing seat's own commits carry: a noreply
#: address, which ref_privacy's host-email class passes, never the host's default.
#: It is the one `dev/programme/HANDOVER.md`'s Identity bullet names (hpo-fixer).
SEAT_NAME, SEAT_EMAIL = "hpo-fixer", "70032254+tvofi@users.noreply.github.com"
#: The roles that commit in their own checkout, and so pin that identity first.
COMMITTING_ROLES = ("fixer", "probe")
#: Where a cloud fixer pushes each verified step (`<WIP_NS>/<topic>`), so an idle
#: container holds no unpushed work. Neither cloud_relay.sh's handoff arm nor
#: `bus.sh orphans` lists the prefix, so a step push moves no pull request.
WIP_NS = "handoff-wip"


#: The toolchain check a seat runs before any work (#2709): REFUSE stops the seat.
SETUP_CHECK = "bash tools/audit/seat/cloud-setup.sh --check"


#: A seat's prompt cache lives 5 min: a wait past it rewrites the whole context on
#: the next turn (R10-FLY-CACHE-PROMPTS). 240 s stays under it; GitHub's 60 s poll
#: floor stays the lower bound.
WAIT_LINE = "Never wait in one tool call longer than 240 s; poll again instead."


#: The owner's frugal-routing directive (tvofi 2026-11-06, triage s6-batch127 P398), stated
#: to every role in one line, verbatim; a guard refusal is answered by a cheaper sub-seat,
#: never an inline allowance or a bypass (tvofi 2026-11-09, R10-FLY-CLOUD-FRUGAL-OFF dropped).
FRUGAL_LINE = ("Discovery reads (search, list, read across files) go through Agent subagents, as the "
               "frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet "
               "Agent subagent to do it rather than bypassing the guard; never set "
               "FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.")

#: Who owes a red an answer (owner rulings tvofi 2026-11-07, 2026-11-09: no merge is
#: blocked on a non-required red), stated to the two seats that meet check runs, in one
#: line naming the instrument that prints the set; the rule itself is defect-root-cause.md's.
OWED_REDS_ROLES = ("reviewer", "fixer")
OWED_REDS_LINE = ("A red is owed a `## Red checks` answer, and may block, only when its name is in the set "
                  "`python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any "
                  "other red is neither answered nor a block.")

#: The policy pack (tools/policy/role_pack.py) a role reads once in place of its
#: contract and INSTRUMENTS.md. The payload schema has no per-seat environment, so
#: the seat renders it itself, with the same renderer the SessionStart hook runs;
#: the probe has no contract and so no pack.
PACK_ROLE = {"reviewer": "fix-review", "fixer": "fixer", "designer": "designer",
             "design-reviewer": "design-review"}


class Refusal(Exception):
    pass


#: The roster key a role's model is ruled under: the group's `model` table, else its
#: `<key>Model` field (roster_lib's shape). The values are the roster's, routed by
#: judgement per group (tvofi 2026-10-24 card 9); this table only names the key. A
#: role with no key (the probe, the design steps) has no ruling to enforce.
MODEL_KEY = {"fixer": "fixer", "reviewer": "reviewer"}


def _family(model: str) -> str:
    """`claude-sonnet-5-5` and `sonnet` are one model family; an unknown name is itself."""
    m = re.search(r"haiku|sonnet|opus|fable", model.lower())
    return m.group(0) if m else model.lower()


def model_refusal(role: str, group: dict, model: str) -> str | None:
    """Why `model` may not run `role` for `group`, in one line, or None when the roster
    rules no model for it or the model is of the family it rules."""
    key = MODEL_KEY.get(role)
    table = group.get("model") if isinstance(group.get("model"), dict) else {}
    ruled = key and (table.get(key) or group.get(f"{key}Model"))
    if not ruled or _family(model) == _family(ruled):
        return None
    return f"{group.get('group')} rules {ruled} for its {role} (roster model.{key}); --model {model} is not {ruled}"


#: The family a carry-only (review_carry CARRY) or record-PR review runs on, whatever the
#: roster rules for a full review (tvofi 2026-11-01, card 9: a delta re-read needs no opus).
LIGHT_REVIEW_MODEL = "sonnet"


def resolve_model(role: str, group: dict, *, carry_only: bool = False, record_pr: bool = False) -> tuple[str, str]:
    """The model a dispatch with no --model runs on, and the roster field it was read from
    (`model.fixer`, `fixerModel`, or the light-review rule), never an opus default. A role
    the roster rules no model for refuses: a guess goes stale (the overlay's `model` is the
    flag path's, not a group's)."""
    if role == "reviewer" and (carry_only or record_pr):
        return LIGHT_REVIEW_MODEL, "carry-only review" if carry_only else "record-PR review"
    key = MODEL_KEY.get(role)
    table = group.get("model") if isinstance(group.get("model"), dict) else {}
    for field, val in ((f"model.{key}", table.get(key)), (f"{key}Model", group.get(f"{key}Model"))):
        if key and val:
            return val, f"roster {field}"
    raise Refusal(f"{group.get('group')} rules no model for its {role} (roster model.{key}): pass --model")


def _seat_line(role: str, repo: str, pr: str, head: str, topic: str, nonce: str) -> str:
    who = {"reviewer": "CLOUD REVIEWER", "fixer": "CLOUD FIXER", "probe": "CLOUD PROBE",
           "designer": "CLOUD DESIGNER", "design-reviewer": "CLOUD DESIGN REVIEWER"}[role]
    subject = f"PR #{pr} of {repo}, at head {head}" if pr else f"{repo}, topic {topic}, at head {head}"
    first = f"{who} seat for {subject}."
    if nonce:
        first += f" Bus nonce: {nonce}."
    return first + " Never send push notifications."


def _pointer(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, ref: str, pin: str) -> str:
    """The event a published seat is fired with: who it is, the footer ban, and the
    commit its prompt is at. The runner echoes the event into every view of the
    trigger, so the whole prompt there was paid for several times over; PROMPT.md is
    paid once. `pin` is a SHA, never `ref`: a re-dispatch moves the ref, and a
    running seat's brief may not move with it."""
    return (_seat_line(role, repo, pr, head, topic, nonce) + " " + FOOTER_BAN + "\n"
            f"Your full brief is PROMPT.md at commit {pin} of {ref} (`git fetch origin {pin} && "
            f"git show {pin}:PROMPT.md`); read it first and follow it exactly.\n")


def _prompt(role: str, repo: str, pr: str, head: str, topic: str, nonce: str, brief: str,
            design: str = "", reviewed_head: str = "", verdict: tuple = ()) -> str:
    first = _seat_line(role, repo, pr, head, topic, nonce) + " " + FOOTER_BAN
    pin = (f"Before any commit, pin the seat identity: `git config user.name {SEAT_NAME} && git config "
           f"user.email {SEAT_EMAIL}`. ") if role in COMMITTING_ROLES else ""
    setup = ("Setup: `git fetch --unshallow --tags origin`. " + pin + "The session-start `toolchain:` line "
             "says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with "
             "`eval \"$(bash .claude/hooks/session-start.sh --env-lines)\"`. Then run "
             f"`{SETUP_CHECK}`, and on REFUSE stop: report its line as your result and start no work. "
             "Run anything heavy in "
             "the background with Monitor and no timeout. " + WAIT_LINE)
    if role in PACK_ROLE:
        setup += (f" Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render "
                  f"{PACK_ROLE[role]} --out $HOME/role-pack.md`, then that file in place of your role "
                  "contract and INSTRUMENTS.md; on REFUSE read those files as before.")
    if role == "reviewer":
        # DISPATCH AT THE HANDOFF (Carry 0): no pull request exists yet, so the reviewer reads the
        # body at handoff-body/<topic>, renders no packet and waits on no CI, and returns its
        # verdict on probe/revt-<topic>-<nonce8> as `verdict <topic> <head>`; the relay holds it
        # until open_pr.sh re-keys the dispatch to the PR (bus.sh rekey) and the carry check passes.
        at_handoff = not pr
        subj_key = topic if at_handoff else pr
        ref_key = f"revt-{topic}" if at_handoff else f"rev-{pr}"
        where = (f"the body is BODY.md at refs/heads/handoff-body/{topic} (`git fetch origin handoff-body/{topic}`), "
                 "and no pull request exists yet. There is no review packet and no CI to wait on before the PR "
                 "opens: say so in the verdict's evidence. " if at_handoff else
                 "the PR body is in the PR. Start from the review packet, which you render here rather than read from the "
                 "dispatcher, whose copy is a path on its own machine: "
                 f"`python3 -I tools/audit/seat/review_packet.py render --pr {pr} --head {head} "
                 + (f"--reviewed-head {reviewed_head} " if reviewed_head else "") +
                 "--out $HOME/review-packet.md`. A refusal names its signal and the packet is still "
                 "written unless the signal is `host-path`; re-read the live checks either way. ")
        wait_ci = ("\n" if at_handoff else
                   "Wait for CI on this head only by re-running "
                   f"`python3 tools/audit/seat/merge_train.py classify {head} --pr {pr}` in the background, at least "
                   "60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) "
                   "or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; "
                   "judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches "
                   "the waiter's own command line, nor on a context the ruleset does not require, such as "
                   "`prelude`. A review_packet `required-red` signal does not stop you while classify prints "
                   "WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after "
                   "about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it "
                   "printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay "
                   "posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. "
                   f"If the review is not complete then, push `Fix review: blocked {head} ci-wait: <the last "
                   "classify line>` as below.\n")
        body = (
            "Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them "
            f"exactly. Fetch the {'handoff' if at_handoff else 'PR'} head with `git fetch origin {head}`; " + where +
            (f"This is a later round over the reviewed head {reviewed_head}: its scope is the packet's "
             "`## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, "
             "widened only to the exact already-reviewed code a production (custom_components/) delta puts "
             "at non-obvious risk that CI would not detect, the verdict naming path and risk; an "
             "instrument, test, policy or body delta never widens it (fix-review.md step 12). " if reviewed_head else "") +
            "Verify each claim adversarially: mutate the fix and check the tests fail, and check "
            "every figure in the body at this head. Check that it merges with origin/main "
            "(`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a "
            "conflict, never on a head that is behind main but merges cleanly (the train re-proves it on "
            "the current main). " + wait_ci +
            f"Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is "
            f"exactly `Fix review: merge {head}` or `Fix review: blocked {head} <class>: <reason>` (no brackets; "
            f"the class is lower-case letters and dashes), in the format the role file gives, "
            f"then a blank line, then `bus-nonce: {nonce}`, then the body in sections. A blocked verdict's "
            f"block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving "
            f"mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under "
            f"`## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` "
            f"(finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you "
            f"could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, "
            f"and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a "
            f"note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens "
            f"with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect "
            f"you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no "
            f"valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log "
            f"by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head "
            f"`{head}` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): "
            f"bus.sh refuses a verdict whose `ev/` names no head. Do NOT run "
            f"bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict "
            f"there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one "
            f"parentless commit with a private index and touches no branch of your checkout: "
            f"`R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && "
            f"cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr "
            f"sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name={SEAT_NAME} "
            f"-c user.email={SEAT_EMAIL} commit-tree $T -m \"verdict {subj_key} {head}\") && "
            f"git -C $R push -q origin $C:refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`. "
            "That ref is the return signal. Do not post comments, approve or merge.\n"
            # CARRY 8 (P437 C2): 13 of 160 reviewer dispatches ended with no probe ref (11-07, 11-08).
            "Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you "
            f"pushes `Fix review: blocked {head} seat-refused: <the refusing line>`; never end your turn while "
            "a background poll runs. After the push, read the ref back with "
            f"`git ls-remote origin refs/heads/probe/{ref_key}-{nonce.strip()[:8]}`, and push again if it does "
            "not print your commit.")
    elif role == "fixer":
        body = (
            "Role: read dev/governance/roles/fixer.md from main, and follow it exactly, "
            f"in a worktree of your own cut from origin/main. Fetch {head} for the base you were given.\n"
            f"Output: push each verified step, fast-forward only, to refs/heads/{WIP_NS}/{topic} before "
            f"any wait on a background run, so an idle container loses nothing; never step-push to "
            f"handoff/{topic}, whose move updates the pull request. Hand off at your first clean "
            "`tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved "
            "since that run needs no re-merge and no second run, because the train re-proves the head on the "
            "current main. Merge origin/main and rerun prepr.sh only when "
            "`git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, "
            f"first push `BLOCKED.md` with a `Question:` line to refs/heads/{WIP_NS}/{topic}, even with no code. Then push the code to "
            f"refs/heads/handoff/{topic}, then write the PR body and run "
            f"`bash tools/audit/seat/body_push.sh {topic} <body.md>`, which pushes "
            f"refs/heads/handoff-body/{topic}; that second push is the return signal. Once it succeeds, "
            f"delete the step ref: `git push origin :refs/heads/{WIP_NS}/{topic}`. When body_push.sh "
            f"exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster "
            f"you may not write: push a BLOCKED.md holding that output to refs/heads/{WIP_NS}/{topic} and stop; "
            "the relay folds the carries and re-runs body_push.sh. Push nothing "
            "else, open no pull request and write no delivery row. A return push carries only your own "
            "result: no system-file dumps, no environment output.")
    elif role == "designer":
        body = (
            "Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base "
            f"is {head} (`git fetch origin {head}`); name it in the note. Write no production code.\n"
            f"Output: write the note as design.md in a directory of your own and run `bash "
            f"tools/audit/seat/bus.sh push-design {topic} <design.md>`, which pushes "
            f"refs/heads/design/{topic}; that push is the return signal, and the design/{topic} tip "
            "is the SHA you hand off. You may push only to that ref. Open no pull request, push no "
            "handoff ref and write no delivery row."
            + (f" The design reviewer's verdict is at design-verdict/{topic}, commit {verdict[0]}, "
               f"first line `{verdict[1]}`: read it first, answer every point in a new design.md pushed "
               f"on top of design/{topic}, and do not restart." if verdict else ""))
    elif role == "design-reviewer":
        body = (
            "Role: read dev/governance/roles/design-review.md from main, and follow it exactly. "
            f"Review the design at refs/heads/design/{topic}, SHA {design}: "
            f"`git fetch origin {design}` and open a detached worktree there. The base the note names "
            f"is judged against {head}. Rerun nothing; there is no code.\n"
            f"Output: write verdict.md, whose first line is exactly `Design review: approve {design}` or "
            f"`Design review: revise {design} <class>` (the class is lower-case letters and dashes), "
            f"and run `bash tools/audit/seat/bus.sh push-design-verdict {topic} <verdict.md>`, which "
            f"pushes refs/heads/design-verdict/{topic} and refuses a design that has moved; that push "
            "is the return signal. You may push only to that ref. Write no design, open no pull "
            "request and push no code.")
    else:
        body = (
            "Role: a read-only probe. Measure what the brief below asks against the tree at "
            f"{head} (`git fetch origin {head}`); change no tracked file and send no code to any ref.\n"
            f"Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh "
            f"{topic} <result.md>`, which pushes refs/heads/handoff-body/{topic}; that push is the "
            "return signal. A return push carries only your own result tokens.")
    if role in OWED_REDS_ROLES:
        body += "\n" + OWED_REDS_LINE
    refs = f"your return refs and refs/heads/{WIP_NS}/{topic} and refs/heads/{WIP_NS}/{topic}-body" if role == "fixer" else "your return refs"
    tail = (f"Never write to any branch except {refs}. Never work around a hook or a refusal; "
            "report it in your result instead.")
    text = "\n".join([first, setup, body, tail, FRUGAL_LINE]) + "\n"
    if brief:
        text += "\nBrief (snapshotted when this payload was rendered):\n" + brief.rstrip("\n") + "\n"
    return text


def render(role: str, head: str, *, env_id: str, model: str, repo: str, pr: str = "",
           topic: str = "", nonce: str = "", brief: str = "", publish_ref: str = "",
           design: str = "", pin: str = "", reviewed_head: str = "", verdict: tuple = ()) -> dict:
    """The payload; with `publish_ref`, its event is the stub naming PROMPT.md at commit
    `pin` of that ref (`publish_seat`)."""
    if role not in ROLES:
        raise Refusal(f"role must be one of {', '.join(ROLES)}")
    if not is_head(head or ""):
        raise Refusal("head must be exactly 40 lowercase hex digits")
    if role == "reviewer":
        if not nonce.strip():
            raise Refusal("a reviewer needs a non-empty bus nonce")
        if not pr and topic.strip() and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", topic):
            pass  # a reviewer at the handoff: the topic keys the dispatch until the PR opens
        elif not pr.isdigit():
            raise Refusal("a reviewer needs --pr <number> (or --topic <t>, a reviewer at the handoff before the PR opens)")
    elif not topic.strip() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", topic):
        raise Refusal("a fixer, probe or design seat needs --topic (letters, digits, . _ -)")
    if reviewed_head and (role != "reviewer" or not is_head(reviewed_head)):
        raise Refusal("--reviewed-head is a reviewer's: the 40-hex head a previous verdict names")
    if role == "design-reviewer" and not is_head(design or ""):
        raise Refusal("a design reviewer needs --design <the 40-hex design/<topic> tip it reviews>")
    for name, val in (("environment id", env_id), ("model", model), ("repo", repo)):
        if not (val or "").strip():
            raise Refusal(f"no {name}: pass a flag, an overlay entry or its HPO_CLOUD_* variable")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise Refusal("repo must be OWNER/NAME")
    if publish_ref and not is_head(pin):
        raise Refusal("a published seat's stub needs the 40-hex commit holding its PROMPT.md")
    text = (_pointer(role, repo, pr, head, topic, nonce, publish_ref, pin) if publish_ref
            else _prompt(role, repo, pr, head, topic, nonce, brief, design, reviewed_head, verdict))
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
#: Where a seat's head comes from when none is passed: main, never the roster
#: ref, whose tip is the roster branch a fixer must not fork from.
HEAD_REF = roster_lib.MAIN_REF
#: Identity of the commit that carries a dispatch (a constant, never the host's).
_SEAT = ("-c", f"user.name={SEAT_NAME}", "-c", f"user.email={SEAT_EMAIL}")


def _git(repo_dir: str, *argv: str, stdin: str | None = None) -> str:
    r = subprocess.run(["git", "-C", repo_dir, *argv], input=stdin, capture_output=True, text=True)
    if r.returncode:
        raise Refusal(f"git {argv[0]} failed: {(r.stderr or r.stdout).strip()[:200]}")
    return r.stdout


def _topic_of(group: dict) -> str:
    """The topic a group's seat returns under: its branch, less the `handoff/` prefix."""
    return roster_lib.branch_of(group).removeprefix("handoff/")


def _tip(repo_dir: str, ref: str) -> str:
    """The tip of `refs/heads/<ref>` on origin, fetched, or "" when there is none.
    A ref that would publish the host refuses before anything is read or pushed."""
    why = ref_privacy.refusal(ref, (("the dispatch message", f"dispatch: {ref}"),))
    if why:
        raise Refusal(f"the dispatch ref would publish the host: {why}")
    tip = _git(repo_dir, "ls-remote", "origin", f"refs/heads/{ref}").split()[:1]
    if tip:
        _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")
    return tip[0] if tip else ""


def _tree(repo_dir: str, files: dict[str, str]) -> str:
    entries = "".join(f"100644 blob {_git(repo_dir, 'hash-object', '-w', '--stdin', stdin=text).strip()}\t{name}\n"
                      for name, text in sorted(files.items()))
    return _git(repo_dir, "mktree", stdin=entries).strip()


def _publish(repo_dir: str, ref: str, files: dict[str, str]) -> str:
    """Append one commit holding `files` to `refs/heads/<ref>` on origin; return the tip.

    The first commit has no parent; later ones fast-forward, so a re-dispatch
    needs no force-push. An identical tree adds no commit. A fetch that fails
    for any reason but a missing ref refuses: a parentless commit would only be
    refused by the push as a non-fast-forward, never rewritten."""
    tip = _tip(repo_dir, ref)
    tree = _tree(repo_dir, files)
    if tip and _git(repo_dir, "rev-parse", f"{tip}^{{tree}}").strip() == tree:
        return tip
    commit = _git(repo_dir, *_SEAT, "commit-tree", tree, *(["-p", tip] if tip else []),
                  "-m", f"dispatch: {ref}").strip()
    _git(repo_dir, "push", "-q", "origin", f"{commit}:refs/heads/{ref}")
    return commit


def _snapshot(repo_dir: str, ref: str, prompt: str) -> str:
    """The commit of `ref` holding PROMPT.md alone, which a stub pins: the tip's parent
    when the tip already publishes this prompt over it (a re-dispatch moves nothing),
    else a new commit appended to the ref."""
    tip = _tip(repo_dir, ref)
    if tip:
        parent = _git(repo_dir, "log", "-1", "--format=%P", tip).split()[:1]
        if parent and _git(repo_dir, "rev-parse", f"{parent[0]}^{{tree}}").strip() == _tree(
                repo_dir, {"PROMPT.md": prompt}) and _git(repo_dir, "rev-parse", f"{tip}:PROMPT.md") \
                == _git(repo_dir, "rev-parse", f"{parent[0]}:PROMPT.md"):
            return parent[0]
    return _publish(repo_dir, ref, {"PROMPT.md": prompt})


def group_brief(group: dict, roster: dict | None = None, *, fixer: bool = False) -> str:
    """What a group's seat is briefed with: the roster brief, then `After:` the groups it
    follows, then each carry as `Carry <i>:`, verbatim, `<i>` its 0-based index in the
    roster's list (the index a brief or a verdict cites a carry by)."""
    parts = [(group.get("brief") or "").rstrip("\n"), "After: " + (", ".join(group.get("after") or []) or "none")]
    parts += [f"Carry {i}: {c}" for i, c in enumerate(group.get("carry") or [])]
    if fixer and roster is not None:  # the generated lines, after everything the roster wrote
        parts += roster_lib.brief_lines(roster, group.get("group") or "")
    return "\n\n".join(p for p in parts if p) + "\n"


#: fixer.md's "at most five findings", applied to a group's pending carries (triage P551).
PART_CARRIES = 5
#: The remainder a split folds into its last part rather than dispatching alone (P551: "one or two").
PART_FOLD = 2


def part_split(pending: list[int]) -> str:
    """The serial parts of `pending` (roster carry indices, in order): fives, a remainder of
    PART_FOLD or fewer folded into the last; each part's indices as runs (`0-4`, `0-1+3`),
    parts comma-separated."""
    parts = [pending[i:i + PART_CARRIES] for i in range(0, len(pending), PART_CARRIES)]
    if len(parts) > 1 and len(parts[-1]) <= PART_FOLD:
        parts[-2:] = [parts[-2] + parts[-1]]
    def runs(idx):
        out, start = [], 0
        for j in range(1, len(idx) + 1):
            if j == len(idx) or idx[j] != idx[j - 1] + 1:
                out.append(str(idx[start]) if start == j - 1 else f"{idx[start]}-{idx[j - 1]}")
                start = j
        return "+".join(out)
    return ", ".join(runs(p) for p in parts)


def part_line(group_id: str, pending: list[int], part: int) -> str:
    """The generated brief line for `--part <part>`, or "" for a group of five or fewer pending
    carries dispatched with none. Over five with no part refuses with the split: a silent part 1
    would re-dispatch part 1's carries at its own handoff, since they stay pending until its merge."""
    split = part_split(pending)
    if not part:
        if len(pending) <= PART_CARRIES:
            return ""
        raise Refusal(f"{group_id} holds {len(pending)} pending carries, over the fixer's five (fixer.md): "
                      f"dispatch serial parts, each at the previous part's handoff, with --part <k>: {split}")
    if len(pending) <= PART_CARRIES:
        raise Refusal(f"--part {part}: {group_id} holds five or fewer pending carries ({len(pending)}), no split")
    parts = split.split(", ")
    if not 1 <= part <= len(parts):
        raise Refusal(f"--part {part}: {group_id} splits into {len(parts)} parts: {split}")
    return (f"Part {part} of {len(parts)}: build carries {parts[part - 1]}; the others are later parts "
            "dispatched at this part's handoff; answer none of them")


def dispatch_ref(role: str, topic: str, pr: str) -> str:
    """`dispatch/<role>-<topic>`, or `dispatch/<role>-rev-<PR>` for a seat with no topic."""
    key = topic or (f"rev-{pr}" if pr.isdigit() else "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", key):
        raise Refusal("a published seat needs a topic (letters, digits, . _ -) or a --pr")
    return f"{DISPATCH_NS}/{role}-{key}"


def publish_seat(repo_dir: str, ref: str, role: str, head: str, **args) -> dict:
    """Publish the seat's whole prompt as PROMPT.md on `ref`, then the payload firing it
    on top; return that payload, whose event is the stub pinning the prompt's commit.
    The prompt renders first, so every `render` refusal, the host-path one on the
    published PROMPT.md included, pushes nothing; the stub adds only a ref, which
    `_tip` judges before its first read."""
    prompt = render(role, head, **args)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
    payload = render(role, head, **args, publish_ref=ref, pin=_snapshot(repo_dir, ref, prompt))
    _publish(repo_dir, ref, {"PAYLOAD.json": json.dumps(payload), "PROMPT.md": prompt})
    return payload


def design_tip(repo_dir: str, group_id: str) -> str:
    """The 40-hex tip of `design/<group>` on origin, or "" when the designer has pushed none."""
    out = _git(repo_dir, "ls-remote", "origin", f"refs/heads/design/{group_id}").split()[:1]
    return out[0] if out else ""


def design_approved(repo_dir: str, group_id: str) -> bool:
    """Whether `design-verdict/<group>` reads `Design review: approve <sha>` at the tip
    `design/<group>` holds now: an approval of a design that has since moved is not one."""
    tip = design_tip(repo_dir, group_id)
    if not tip:
        return False
    vref = f"refs/heads/design-verdict/{group_id}"
    if not _git(repo_dir, "ls-remote", "origin", vref).split():
        return False
    _git(repo_dir, "fetch", "-q", "origin", vref)
    first = _git(repo_dir, "show", "FETCH_HEAD:verdict.md").split("\n", 1)[0]
    return first == f"Design review: approve {tip}"


def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
                   roster_ref: str | None = None, head: str = "", pr: str = "", nonce: str = "",
                   overlay: str | None = None, environ=None, design_exempt: str = "",
                   carry_only: bool = False, record_pr: bool = False, reviewed_head: str = "",
                   part: int = 0) -> str:
    """Render the seat for `group_id` from the roster, publish it, return its ref name.

    The roster at `roster_ref` of `repo_dir` (default: the round's roster
    branch, `roster_lib.reader_ref`) gives the brief, the topic (the group's
    branch) and the repository. The head is a separate source: the one passed,
    else HEAD_REF's tip; a reviewer must pass its PR head. The environment id comes from the
    known seat environment (`--overlay` / $HPO_CLOUD_ENV_ID). Nothing is pushed
    unless the payload rendered, so every `render` refusal holds here too. A
    reviewer's nonce is `bus.sh dispatch`'s (`_bus_dispatch`), so the seat is in the
    worker registry and its `reviewer-fire` closed; an unpublished ref reopens it."""
    if role == "reviewer" and not head:
        raise Refusal("a reviewer is dispatched at its PR head: pass --head")
    roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)
    try:
        roster = roster_lib.show_roster(repo_dir, roster_ref)
    except roster_lib.RosterNotFound as e:
        raise Refusal(str(e))
    group = roster_lib.groups_of(roster).get(group_id)
    if group is None:
        raise Refusal(f"{group_id} is not a group of the roster at {roster_ref}")
    if model:
        why = model_refusal(role, group, model)
        if why:
            raise Refusal(why)
    else:
        model, source = resolve_model(role, group, carry_only=carry_only, record_pr=record_pr)
        print(f"cloud_dispatch: model {model} for the {role} of {group_id}, read from {source}", file=sys.stderr)
    environ = os.environ if environ is None else environ
    known = _config(argparse.Namespace(overlay=overlay, env_id=None, model=model, repo=None), environ)
    topic = group_id if role in DESIGN_ROLES else _topic_of(group)
    pline = ""
    if part and role != "fixer":
        raise Refusal(f"--part is the fixer's: a {role} seat is not split")
    if role == "fixer" and (part or len(group.get("carry") or []) > PART_CARRIES):
        try:
            legacy = roster_lib.read_legacy(repo_dir, roster_lib.roster_path(repo_dir, roster_ref, None))
        except roster_lib.RosterNotFound as e:
            raise Refusal(str(e))
        pline = part_line(group_id, roster_lib.pending_carries(group, legacy), part)
        if part > 1:
            topic = f"{topic}-p{part}"
            for other in roster.get("groups", []):  # a part's topic is a roster group's own: one seat ref, one wrong credit
                if other is not group and topic in (_topic_of(other), roster_lib.norm_group(str(other.get("group")))):
                    raise Refusal(f"--part {part}: {topic} is the topic of {other.get('group')}")
    design = ""
    if role == "fixer" and roster_lib.needs_design(group) and not design_exempt.strip():
        if not design_approved(repo_dir, group_id):
            raise Refusal(f"{group_id} is size {group.get('size')}: no approved `Design review: approve "
                          f"<sha>` at design-verdict/{group_id} names the current design/{group_id} tip "
                          "(decision 0014). Run the designer and design reviewer, or pass "
                          "--design-exempt <reason> where an approved design, pre-study or prototype "
                          "is already on record")
    if role in DESIGN_ROLES and not roster_lib.needs_design(group):
        raise Refusal(f"{group_id} is size {group.get('size')}: only L and XL groups take a design (decision 0014)")
    if role == "design-reviewer":
        design = design_tip(repo_dir, group_id)
        if not design:
            raise Refusal(f"no design/{group_id} on origin to review")
    verdict = ()
    if role == "designer":  # a revise routes the round-2 designer to the verdict commit, pinned by SHA
        vref = f"refs/heads/design-verdict/{group_id}"
        vtip = _git(repo_dir, "ls-remote", "origin", vref).split()[:1]
        if vtip:
            _git(repo_dir, "fetch", "-q", "origin", vtip[0])
            verdict = (vtip[0], _git(repo_dir, "show", f"{vtip[0]}:verdict.md").split("\n", 1)[0])
    args = dict(design=design, verdict=verdict, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
                pr=pr, topic=topic,
                brief=group_brief(group, roster, fixer=role == "fixer") + (f"\n{pline}\n" if pline else ""),
                reviewed_head=reviewed_head)
    head = head or _git(repo_dir, "rev-parse", f"{HEAD_REF}^{{commit}}").strip()
    if role == "reviewer":
        render(role, head, **args, nonce=BUS_PROBE_NONCE)  # every other refusal, before the bus records
        nonce = _bus_dispatch(repo_dir, pr, head, model, nonce, environ, reviewed_head)
    ref = dispatch_ref(role, topic, "")
    try:
        publish_seat(repo_dir, ref, role, head, **args, nonce=nonce)
    except Refusal:
        if role == "reviewer":  # the bus closed reviewer-fire for a seat that was never fired
            subprocess.run([sys.executable, "-I", str(HERE / "ledger.py"), *_ledger_log(environ), "open",
                            "reviewer-fire", pr, head, f"nonce={nonce} the dispatch ref was not published"],
                           env={**os.environ, **environ}, capture_output=True)
        raise
    return ref


#: A well-formed nonce for the reviewer's pre-render: the bus mints or checks the real one.
BUS_PROBE_NONCE = "0" * 32


def _ledger_log(environ) -> list[str]:
    return ["--log", environ["HPO_BUS_LEDGER"]] if environ.get("HPO_BUS_LEDGER") else []


def _bus_dispatch(repo_dir: str, pr: str, head: str, model: str, nonce: str, environ,
                  reviewed_head: str = "") -> str:
    """The reviewer's nonce through `bus.sh dispatch`, the worker registry: minted, or a nonce
    minted earlier at this pr and head (the relay's) re-recorded with this seat and model. Either
    closes `reviewer-fire <pr> <head>` in the ledger."""
    r = subprocess.run(["bash", str(HERE / "bus.sh"), "dispatch", pr, head, "cloud", "--model", model,
                        *(["--nonce", nonce] if nonce else []),
                        *(["--reviewed-head", reviewed_head] if reviewed_head else [])],
                       cwd=repo_dir, env={**os.environ, **environ}, capture_output=True, text=True)
    n = proof_watch.verdict_nonce(r.stdout)
    if r.returncode or not n:
        raise Refusal(f"bus.sh dispatch refused: {(r.stderr or r.stdout).strip()[-300:]}")
    return n


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
    from throwaway_git import throwaway_git_clone, throwaway_git_environ, throwaway_git_init

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
        big = {"group": "R10-BIG", "size": "L", "brief": "Redesign tools/y.py.\n"}
        two = {"group": "R10-TWO", "brief": "Two things.\n", "after": ["R10-X", "R10-BIG"],
               "carry": ["First, verbatim.", "Second; tools/z.py."]}
        cbad = {"group": "R10-CBAD", "brief": "Clean.\n", "carry": ["fine", "cd " + users + "someone/work"]}
        ruled = {"group": "R10-M", "brief": "Model.\n", "model": {"fixer": "sonnet", "reviewer": "opus"}}
        legacy = {"group": "R10-L", "brief": "Legacy.\n", "fixerModel": "opus"}
        prod = {"group": "R10-PROD", "brief": "Produce.\n", "files": ["tools/a.py"], "resume": {"stage": "in-progress"},
                "enumeration": "git grep -n seam -- tools"}
        cons = {"group": "R10-CONS", "brief": "Consume.\n", "after": ["R10-PROD"], "resume": {"stage": "queued"}}
        share = {"group": "R10-SHARE", "brief": "Share.\n", "files": ["tools/a.py", "tools/b.py"], "resume": {"stage": "queued"}}
        donec = {"group": "R10-DONEC", "brief": "Done.\n", "after": ["R10-PROD"], "resume": {"stage": "done"}}
        # CARRY 13 (P551): 21 pending carries and a marked one past them; five pending and a moved one.
        many = {"group": "R10-SPLIT", "brief": "Many.\n", "resume": {"branch": "handoff/r10-split"},
                "carry": [f"Carry text {i}." for i in range(21)] + ["Built. [implemented: abc1234]"]}
        five = {"group": "R10-FIVE", "brief": "Five.\n", "carry": [f"Five {i}." for i in range(5)] + ["Gone. [moved: R10-X]"]}
        # Part 2's topic is R10-CLASH-P2's id, part 3's R10-ALIAS's branch; R10-SELF-P2's part 2 is its own id.
        clash = {"group": "R10-CLASH", "brief": "Clash.\n", "carry": [f"Clash {i}." for i in range(13)]}
        clash2 = {"group": "R10-CLASH-P2", "brief": "Own.\n", "resume": {"branch": "handoff/other-topic"}}
        alias = {"group": "R10-ALIAS", "brief": "Alias.\n", "resume": {"branch": "handoff/r10-clash-p3"}}
        selfp = {"group": "R10-SELF-P2", "brief": "Self.\n", "resume": {"branch": "handoff/r10-self"},
                 "carry": [f"Self {i}." for i in range(8)]}
        land([grp, bad, big, two, cbad, ruled, legacy, prod, cons, share, donec, many, five, clash, clash2, alias, selfp])
        git(work, "remote", "add", "origin", str(origin))
        tip = git(work, "rev-parse", "origin/main").strip()

        def dispatch(group="R10-X", role="fixer", model="m-1", **kw):
            with contextlib.redirect_stderr(io.StringIO()):  # roster_lib's absent-branch note
                return dispatch_group(role, group, model, repo_dir=str(work), **{"environ": env, **kw})

        def refused(*a, **kw):
            return bool(reason(*a, **kw))

        def reason(*a, **kw) -> str:  # the refusal's text, "" when the dispatch passed
            try:
                dispatch(*a, **kw)
            except Refusal as e:
                return str(e) or "refused"
            return ""

        @contextlib.contextmanager
        def _env(extra):  # main() reads os.environ, as the orchestrator's shell gives it
            saved = dict(os.environ)
            os.environ.update(extra)
            try:
                yield
            finally:
                os.environ.clear()
                os.environ.update(saved)

        def fetched(line, name):
            git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
            return git(work, "show", "FETCH_HEAD:" + name)

        line = dispatch()
        check("a group dispatch prints one short line, the ref name",
              line == "dispatch/fixer-r10-x" and "\n" not in line and " " not in line)
        # The design steps (decision 0014).
        check("a fixer for an L group with no design ref is refused",
              refused("R10-BIG") and not git(work, "ls-remote", "origin", "refs/heads/dispatch/fixer-r10-big").strip())
        check("a fixer for an L group is dispatched with --design-exempt (the reason is the orchestrator's)",
              dispatch("R10-BIG", design_exempt="approved prototype on record") == "dispatch/fixer-r10-big")
        check("a designer for an S group is refused (only L and XL take a design)",
              refused("R10-X", "designer") and refused("R10-X", "design-reviewer"))
        check("a design reviewer with no design/<group> to review is refused, for that reason",
              reason("R10-BIG", "design-reviewer") == "no design/R10-BIG on origin to review")
        ref = dispatch("R10-BIG", "designer")
        dtext = fetched(ref, "PROMPT.md")
        check("a designer's ref is dispatch/designer-<group>, pins the base SHA and names its contract",
              ref == "dispatch/designer-R10-BIG" and tip in dtext
              and "dev/governance/roles/designer.md" in dtext)
        check("the designer's text allows design/<group> alone and no pull request, in its own words",
              "bus.sh push-design R10-BIG" in dtext and "refs/heads/design/R10-BIG" in dtext
              and "only to that ref" in dtext and "Open no pull request" in dtext
              and "send no code to any ref" not in dtext)
        check("a designer's text names no design-verdict ref while none exists (null control)",
              "design-verdict/" not in dtext)
        git(work, "push", "-q", "origin", f"{tip}:refs/heads/design/R10-BIG")
        rref = dispatch("R10-BIG", "design-reviewer")
        rtext = fetched(rref, "PROMPT.md")
        check("a design reviewer pins the design tip and the base, names its contract and its one ref",
              rref == "dispatch/design-reviewer-R10-BIG" and f"Design review: approve {tip}" in rtext
              and tip in rtext and "dev/governance/roles/design-review.md" in rtext
              and "push-design-verdict R10-BIG" in rtext and "only to that ref" in rtext)
        check("a fixer is still refused with a design and no verdict", refused("R10-BIG", design_exempt=""))
        _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: revise {tip} class-open\n"})
        check("a fixer is refused on a `revise` verdict", refused("R10-BIG"))
        vtip = git(work, "ls-remote", "origin", "refs/heads/design-verdict/R10-BIG").split()[0]
        dref = dispatch("R10-BIG", "designer")  # over the existing dispatch/designer-R10-BIG ref
        dtext2 = fetched(dref, "PROMPT.md")
        check("a designer's text pins the revise verdict's own commit and first line",
              dref == ref and vtip != tip and vtip in dtext2 and f"Design review: revise {tip} class-open" in dtext2)
        _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {'a' * 40}\n"})
        check("a fixer is refused on an approval of a design that has since moved", refused("R10-BIG"))
        _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {tip}\n"})
        check("a fixer is dispatched once the verdict approves the current design tip (null control)",
              dispatch("R10-BIG") == "dispatch/fixer-r10-big")
        brief = work / "brief.txt"
        brief.write_text(group_brief(grp))  # what the group path briefs, so the two payloads can agree
        flags = ["--role", "fixer", "--head", tip, "--topic", "r10-x", "--brief", str(brief),
                 "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"]
        plain, old = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(plain):
            rc0 = main(flags)
        with contextlib.chdir(work), contextlib.redirect_stdout(old):
            rc = main([*flags, "--publish"])
        check("the printed line round-trips to a payload byte-identical to the flag path's --publish",
              rc == 0 and fetched(line, "PAYLOAD.json") == old.getvalue().rstrip("\n"))
        content = lambda text: json.loads(text)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
        msg = fetched(line, "PROMPT.md")
        ptr = content(fetched(line, "PAYLOAD.json"))
        _pin = re.search(r"at commit ([0-9a-f]{40}) of ", ptr)
        pin = _pin.group(1) if _pin else ""
        check("the published event is a stub pinning the commit holding PROMPT.md by SHA, never the ref's tip",
              pin and f"of {line} (`git fetch origin {pin} && git show {pin}:PROMPT.md`)" in ptr
              and "FETCH_HEAD" not in ptr and git(work, "show", f"{pin}:PROMPT.md") == msg
              and git(work, "rev-parse", "FETCH_HEAD^").strip() == pin)
        check("the stub keeps the seat line and the footer ban inline; PROMPT.md is the whole prompt",
              ptr.startswith("CLOUD FIXER seat for owner/name, topic r10-x, at head " + tip + ".")
              and FOOTER_BAN in ptr and msg.startswith("CLOUD FIXER") and msg not in ptr)
        check("the stub payload is far smaller than the prompt: under 1 KB whole, the brief absent, the SHA present",
              len(fetched(line, "PAYLOAD.json")) < 1024 < len(msg) and "Fix the thing" not in ptr and pin in ptr)
        check("without --publish the flag path is unchanged: the whole prompt in its event, nothing published",
              rc0 == 0 and content(plain.getvalue()) == msg)
        check("the roster brief is inlined and the roster tip is the head",
              "Fix the thing in tools/x.py." in msg and tip in msg)
        check("a group with no carry, consumer or enumeration renders its brief and `After:` alone (the null control)",
              fetched(dispatch("R10-L", model="opus"), "PROMPT.md").endswith("\nBrief (snapshotted when this payload was rendered):\n"
                                                              "Legacy.\n\nAfter: none\n"))
        # CARRY 4 (tvofi 2026-11-01 card 2): the live consumers and the class enumeration, generated.
        ptext = fetched(dispatch("R10-PROD"), "PROMPT.md")
        check("a fixer's brief lists the live consumers (after-edged and file-sharing) as the only valid Carry targets, not the done one",
              "Valid `Carry:` targets (live consumers of R10-PROD: groups after it or sharing its files): R10-CONS, R10-SHARE\n" in ptext
              and "R10-DONEC" not in ptext.split("Valid `Carry:` targets")[1])
        check("and the group's class-enumeration command",
              "disposition every seam it returns): git grep -n seam -- tools\n" in ptext)
        # CARRY 13 (P551): over five pending carries refuses with the split; --part k renders one part.
        saved_cut = dict(roster_lib.CARRY_CUTOVER)
        roster_lib.CARRY_CUTOVER.clear()  # the fixture's roster has no cut-over commit to read legacy at

        def why_any(*a, **kw) -> str:  # reason(), but any exception reads as a named failure, not a crash
            try:
                return reason(*a, **kw)
            except Exception as e:  # noqa: BLE001 -- a mutant's IndexError must fail a check, not the run
                return f"{e.__class__.__name__}: {e}"

        def split_any(n: int) -> str:  # part_split of 0..n-1; an exception reads as a named failure, as why_any
            try:
                return part_split(list(range(n)))
            except Exception as e:  # noqa: BLE001
                return f"{e.__class__.__name__}: {e}"
        try:
            mwhy = reason("R10-SPLIT")
            check("a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split",
                  "21 pending carries" in mwhy and "--part <k>: 0-4, 5-9, 10-14, 15-20" in mwhy and "\n" not in mwhy
                  and not git(work, "ls-remote", "origin", "refs/heads/dispatch/fixer-r10-split*").strip())
            p2 = dispatch("R10-SPLIT", part=2)
            p2text = fetched(p2, "PROMPT.md")
            pline = ("Part 2 of 4: build carries 5-9; the others are later parts dispatched at this part's handoff; "
                     "answer none of them")
            check("--part 2 renders the topic <topic>-p2 and one generated line naming carries 5-9",
                  p2 == "dispatch/fixer-r10-split-p2" and "topic r10-split-p2, at head" in p2text
                  and sum(ln == pline for ln in p2text.splitlines()) == 1 and p2text.endswith(pline + "\n"))
            cwhy = why_any("R10-CLASH", part=2)
            awhy = why_any("R10-CLASH", part=3)
            check("a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; "
                  "part 1, a free part and a part that is its own group's id (R10-SELF-P2) publish",
                  "R10-CLASH-P2" in cwhy and "\n" not in cwhy and "R10-ALIAS" in awhy and "\n" not in awhy
                  and not git(work, "ls-remote", "origin", "refs/heads/dispatch/fixer-r10-clash-p*").strip()
                  and not why_any("R10-CLASH", part=1) and p2 == "dispatch/fixer-r10-split-p2"
                  and not why_any("R10-SELF-P2", part=2))
            p1text = fetched(dispatch("R10-SPLIT", part=1), "PROMPT.md")
            check("--part 1 keeps the group's own topic and names carries 0-4",
                  "topic r10-split, at head" in p1text and "\nPart 1 of 4: build carries 0-4; the others" in p1text)
            check("a part past the split, a part of a group of five or fewer, and a part for another role refuse",
                  "splits into 4 parts" in why_any("R10-SPLIT", part=5) and "five or fewer" in why_any("R10-FIVE", part=1)
                  and "fixer's" in why_any("R10-SPLIT", "probe", part=2))
            fwhy = why_any("R10-FIVE")
            ftext = "" if fwhy else fetched("dispatch/fixer-" + _topic_of(five), "PROMPT.md")
            check("five pending carries (a moved sixth not counted) dispatch unrefused, the brief byte-identical (null control)",
                  not fwhy and ftext.endswith("Brief (snapshotted when this payload was rendered):\n"
                                 + group_brief(five, {"groups": [five]}, fixer=True)) and "\nPart " not in ftext)
            check("the split folds a remainder of one or two into the last part, and only that",
                  [split_any(n) for n in (1, 2, 5, 6, 7, 8, 21, 22, 23)]
                  == ["0", "0-1", "0-4", "0-5", "0-6", "0-4, 5-7", "0-4, 5-9, 10-14, 15-20", "0-4, 5-9, 10-14, 15-21",
                      "0-4, 5-9, 10-14, 15-19, 20-22"]
                  and part_split([0, 1, 3, 4, 5, 6, 9]) == "0-1+3-6+9" and part_split([0, 2, 3]) == "0+2-3")
            out = io.StringIO()
            with contextlib.chdir(work), _env(env), contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(io.StringIO()):
                crc = main(["--role", "fixer", "--group", "R10-SPLIT", "--part", "3", "--model", "m-1"])
            err = io.StringIO()
            with contextlib.chdir(work), _env(env), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                nrc = main(["--role", "fixer", "--part", "2", "--head", tip, "--model", "m-1"])
            check("the CLI forwards --part to the group path, and refuses it without --group",
                  crc == 0 and out.getvalue().strip() == "dispatch/fixer-r10-split-p3"
                  and nrc == 2 and "--part applies only with --group" in err.getvalue())
        finally:
            roster_lib.CARRY_CUTOVER.update(saved_cut)
        check("a reviewer's brief carries neither generated line",
              "Valid `Carry:`" not in group_brief(prod, {"groups": [prod, cons]}, fixer=False))
        try:
            dispatch("R10-M", model="claude-opus-5-5")
            why = ""
        except Refusal as e:
            why = str(e)
        check("a fixer on a model the roster does not rule for the group refuses, in one line naming both",
              "R10-M rules sonnet for its fixer" in why and "claude-opus-5-5" in why and "\n" not in why
              and "r10-m" not in git(work, "ls-remote", str(origin)))
        check("a fixer on the ruled family passes, by full id or alias (null control)",
              dispatch("R10-M", model="claude-sonnet-5-5") == dispatch("R10-M", model="sonnet") == "dispatch/fixer-r10-m")
        check("the legacy <role>Model field rules where the model table is absent",
              refused("R10-L", model="claude-sonnet-5-5") and dispatch("R10-L", model="claude-opus-5-5"))
        # CARRY 8 (tvofi 2026-11-01 card 9): a dispatch with no --model reads the roster's field.
        errbuf = io.StringIO()
        with contextlib.redirect_stderr(errbuf):
            routed = dispatch_group("fixer", "R10-M", "", repo_dir=str(work), environ=env)
        check("a fixer dispatched with no model runs on the roster's fixer model and prints the model and the field it read",
              routed == "dispatch/fixer-r10-m" and "model sonnet for the fixer of R10-M, read from roster model.fixer" in errbuf.getvalue())
        check("the legacy <role>Model field is read where the table is absent, and the field named",
              resolve_model("fixer", legacy) == ("opus", "roster fixerModel"))
        check("a roster ruling opus for the reviewer still resolves opus for a first-round review (null control)",
              resolve_model("reviewer", ruled) == ("opus", "roster model.reviewer"))
        check("a carry-only review and a record-PR review resolve sonnet whatever the roster rules",
              resolve_model("reviewer", ruled, carry_only=True)[0] == resolve_model("reviewer", ruled, record_pr=True)[0] == "sonnet"
              and resolve_model("fixer", ruled, carry_only=True)[0] == "sonnet")
        check("a role with no ruled model and no --model refuses rather than guessing",
              refused("R10-X", model="") and "rules no model" in reason("R10-X", model=""))
        check("a role the roster rules no model for is not checked (a probe on R10-M runs on any model)",
              dispatch("R10-M", "probe", model="claude-haiku-5-5") == "dispatch/probe-r10-m")
        twotext = fetched(dispatch("R10-TWO"), "PROMPT.md")
        check("a group's two carries render numbered by roster index and verbatim, after its brief and `After:`",
              twotext.endswith("Two things.\n\nAfter: R10-X, R10-BIG\n\nCarry 0: First, verbatim.\n\n"
                               "Carry 1: Second; tools/z.py.\n"))
        check("a host path inside a carry refuses as one in the brief does, and pushes nothing",
              refused("R10-CBAD") and "r10-cbad" not in git(work, "ls-remote", str(origin)))
        dispatch()  # settle: the ref holds this roster's brief for R10-X
        tip_of = lambda: git(work, "ls-remote", str(origin), "refs/heads/" + line).split()[0]
        settled = tip_of()
        check("a re-dispatch of the same brief moves no ref", dispatch() == line and tip_of() == settled)
        git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
        first = git(work, "rev-parse", "FETCH_HEAD").strip()
        land([{**grp, "brief": "Changed.\n"}, bad])
        dispatch()
        git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
        check("a changed brief fast-forwards the ref",
              git(work, "merge-base", "--is-ancestor", first, "FETCH_HEAD") == ""
              and git(work, "rev-parse", "FETCH_HEAD").strip() != first and "Changed." in fetched(line, "PROMPT.md"))
        stale = git(work, "show", f"{pin}:PROMPT.md")
        check("a seat fired with the first stub still reads the first brief at its pinned commit after the re-dispatch",
              "Fix the thing in tools/x.py." in stale and "Changed." not in stale
              and pin not in content(fetched(line, "PAYLOAD.json")))
        check("the dispatch ref is on origin only once the render passed (null control for the refusals)",
              git(work, "ls-remote", str(origin), "refs/heads/dispatch/*").lower().count("r10-big") == 3
              and git(work, "ls-remote", str(origin), "refs/heads/dispatch/*").count("r10-x") == 1)
        check("a host path in a roster brief refuses and pushes nothing",
              refused("R10-BAD") and "r10-bad" not in git(work, "ls-remote", str(origin)))
        check("a group the roster does not name refuses", refused("R10-NOPE"))
        check("an unknown environment refuses", refused(environ={}))
        # A reviewer goes through bus.sh dispatch, the worker registry: a PR head carrying its
        # delivery rows, the bus state and the ledger in the scratch directory.
        bus_state, ledger_log = Path(td) / "bus", Path(td) / "ledger" / "cloud-relay.log"
        env.update(HPO_BUS_STATE=str(bus_state), HPO_BUS_LEDGER=str(ledger_log))
        # The packet renderer is stubbed for the same reason `bus.sh --self-test`
        # stubs it: the real one reads a pull request's body and check runs over
        # `gh`, and this arm measures the dispatch path, not the renderer. The
        # renderer's own seam is driven by its --self-test and by bus.sh's.
        packer = Path(td) / "packer"
        packer.write_text(
            "#!/bin/sh\n"
            '[ -z "${BUS_PACK_REFUSE:-}" ] || { echo "review_packet: REFUSE head-note: planted" >&2; exit 1; }\n'
            'while [ $# -gt 0 ]; do case $1 in --head) h=$2; shift 2 ;; --out) o=$2; shift 2 ;; *) shift ;; esac; done\n'
            'mkdir -p "$(dirname "$o")" && printf "# Review packet\\nhead: %s\\n" "$h" > "$o"\n')
        packer.chmod(0o755)
        env["HPO_BUS_PACKER"] = f"sh {packer}"
        # The head classifier likewise (merge_train.py classify reads check runs over `gh`):
        # GREEN here; bus.sh's self-test drives its RED, WAIT and unreadable arms.
        classifier = Path(td) / "classifier"
        classifier.write_text('#!/bin/sh\necho "GREEN $2 pending: none red: none"\n')
        env["HPO_BUS_CLASSIFY"] = f"sh {classifier}"
        (work / "dev/programme/delivery").mkdir(parents=True)
        for n in (7, 81):
            (work / f"dev/programme/delivery/{n}.md").write_text(f"- [#{n}](x) **open**\n")
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", "rows")
        rhead = git(work, "rev-parse", "HEAD").strip()
        git(work, "push", "-q", str(origin), "HEAD:refs/heads/pr-head")
        git(work, "reset", "-q", "--hard", "origin/main")
        ledger = _sibling("ledger")
        ledger.record(ledger_log.parent, str(ledger_log), "open", "reviewer-fire", "7", rhead, "nonce=relay")
        registry = lambda: (bus_state / "dispatched").read_text().splitlines() if (bus_state / "dispatched").exists() else []
        check("a reviewer needs its pr, as on the flag path, and records nothing",
              refused(role="reviewer", head=tip) and registry() == [])
        check("a reviewer needs its PR head, and is refused for that reason",
              "pass --head" in reason(role="reviewer", pr="7") and registry() == [])
        check("a reviewer dispatch with no nonce mints one through bus.sh dispatch and renders",
              dispatch(role="reviewer", head=rhead, pr="7") == "dispatch/reviewer-r10-x")
        rec = (registry() or [""])[-1].split()
        check("the worker registry records the reviewer: pr, head, seat, nonce, time and the model",
              len(rec) == 6 and rec[:3] == ["7", rhead, "cloud"] and rec[5] == "m-1"
              and f"Bus nonce: {rec[3]}." in fetched("dispatch/reviewer-r10-x", "PROMPT.md"))
        open_, _ = ledger.fold(ledger.events(ledger_log.parent, str(ledger_log)))
        check("a dispatch through dispatch_group closes reviewer-fire at its pr and head in the ledger",
              not [o for o in open_ if o[:2] == ("reviewer-fire", "7")]
              and any(r[0] == "close" and r[2:5] == ["reviewer-fire", "7", rhead]
                      for r in ledger.events(ledger_log.parent, str(ledger_log))))
        check("a reviewer is dispatched at the PR head passed, not at a ref's tip",
              rhead in fetched("dispatch/reviewer-r10-x", "PROMPT.md")
              and git(work, "rev-parse", "origin/main").strip() not in fetched("dispatch/reviewer-r10-x", "PROMPT.md"))
        check("the reviewer's brief carries the packet render at the dispatched head for the seat's own machine",
              f"review_packet.py render --pr 7 --head {rhead} " in fetched("dispatch/reviewer-r10-x", "PROMPT.md"))
        rh2 = "c" * 40
        p_later = _prompt("reviewer", "o/r", "7", rhead, "", "1" * 32, "", "", rh2)
        p_first = _prompt("reviewer", "o/r", "7", rhead, "", "1" * 32, "")
        check("a later round's reviewer renders its packet with --reviewed-head and is told its scope is the delta "
              "(fix-review.md 12); null: a first round's render names no reviewed head",
              f"render --pr 7 --head {rhead} --reviewed-head {rh2} --out " in p_later
              and f"later round over the reviewed head {rh2}" in p_later
              and f"render --pr 7 --head {rhead} --out " in p_first and "--reviewed-head" not in p_first)
        check("the later-round reviewer prompt carries the exception's three qualifiers and no wider trigger",
              "custom_components/" in p_later and "non-obvious" in p_later and "CI would not" in p_later
              and "reaches code that review relied on" not in p_later and "in full" not in p_later)
        try:
            render("fixer", rhead, env_id="e", model="m", repo="o/r", topic="t", reviewed_head=rh2)
            ok = False
        except Refusal:
            ok = True
        check("--reviewed-head is a reviewer's: a fixer given one is refused", ok)
        check("a nonce no dispatch minted is refused by the bus, and records nothing",
              refused(role="reviewer", head=rhead, pr="7", nonce="0" * 32) and len(registry()) == 1)
        check("a packet the renderer refuses holds the reviewer dispatch, and records nothing",
              refused(role="reviewer", head=rhead, pr="7", environ={**env, "BUS_PACK_REFUSE": "1"})
              and len(registry()) == 1)
        # A SEAT THAT CANNOT RENDER ONE STILL DISPATCHES (#2870). The REAL renderer,
        # not the stub, in the throwaway clone this dispatch runs in; its `gh` is
        # made to fail, so it exits 3 (UNAVAILABLE) and bus.sh names no packet and
        # proceeds. The alternative -- a render failure refusing the dispatch, which
        # #2870's first head did -- breaks every caller whose clone has no token.
        before = len(registry())
        try:
            rendered = dispatch(role="reviewer", head=rhead, pr="7",
                                environ={**env, "HPO_BUS_PACKER": "", "HPO_BUS_GH": "false"})
        except Refusal:  # a refusal, not a crash, is the regression: report it as one
            rendered = ""
        check("a packet the seat cannot render dispatches anyway, records, and says why (the #2870 regression)",
              rendered == "dispatch/reviewer-r10-x" and len(registry()) == before + 1)
        real_publish = globals()["_publish"]
        globals()["_publish"] = lambda *a, **k: (_ for _ in ()).throw(Refusal("the push was refused"))
        try:
            unpublished = refused(role="reviewer", head=rhead, pr="7")
        finally:
            globals()["_publish"] = real_publish
        open_, _ = ledger.fold(ledger.events(ledger_log.parent, str(ledger_log)))
        check("a dispatch ref that was not published reopens reviewer-fire: the seat was never fired",
              unpublished and [o[:3] for o in open_ if o[0] == "reviewer-fire"] == [("reviewer-fire", "7", rhead)])
        leak = DISPATCH_NS + "/fixer-" + users + "someone"
        try:
            _publish(str(work), leak, {"PROMPT.md": "x"})
            published = True
        except Refusal:
            published = False
        check("_publish itself refuses a ref that would publish the host, and pushes nothing",
              not published and "someone" not in git(work, "ls-remote", str(origin)))
        # A step push matches no glob the handoff machinery lists, read from its own source.
        # (carry_fold_arm lists handoff-wip/* on purpose, to read a BLOCKED.md; it moves no PR, so it is not a handoff glob)
        # (the same glob listed by two arms is one glob: the pin is the set the handoff machinery lists, not how often)
        globs = list(dict.fromkeys([g for g in re.findall(r"'(refs/heads/handoff[^'*]*\*)'", (HERE / "cloud_relay.sh").read_text())
                  if not g.startswith(f"refs/heads/{WIP_NS}/")]
                 + re.findall(r'"\+(refs/heads/handoff[^:"*]*\*):', (HERE / "bus.sh").read_text())))
        git(work, "push", "-q", str(origin), f"{tip}:refs/heads/{WIP_NS}/r10-x", f"{tip}:refs/heads/handoff/r10-x")
        listed = git(work, "ls-remote", str(origin), *globs)
        check("a handoff-wip push is invisible to cloud_relay.sh's handoff arm and bus.sh orphans; handoff/ is not (null)",
              len(globs) == 2 and f"refs/heads/{WIP_NS}/" not in listed and "refs/heads/handoff/r10-x" in listed)
        git(work, "push", "-q", str(origin), f":refs/heads/{WIP_NS}/r10-x", ":refs/heads/handoff/r10-x")
        # The pinned identity passes ref_privacy --commits; a machine's domain does not (null control).
        bare_env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}

        def judged(email):
            repo = Path(td) / f"ident-{len(email)}"
            throwaway_git_init(repo, "-q")
            subprocess.run(["git", "-C", str(repo), "-c", f"user.name={SEAT_NAME}", "-c", f"user.email={email}",
                            "commit", "-q", "--allow-empty", "-m", "a step"], env=bare_env, check=True)
            r = subprocess.run([sys.executable, "-I", str(HERE / "ref_privacy.py"), "guard", "--ref",
                                f"{WIP_NS}/r10-x", "--commits", "HEAD", "-C", str(repo)],
                               capture_output=True, text=True, env=bare_env)
            return r.returncode, git(repo, "log", "-1", "--format=%ae")
        check("ref_privacy guards a handoff-wip push like any: the pinned identity passes, a .local one refuses (null)",
              judged(SEAT_EMAIL) == (0, SEAT_EMAIL + "\n") and judged("seat@build.local")[0] == 3)
        out = io.StringIO()
        with contextlib.chdir(work), contextlib.redirect_stdout(out):
            rc = main(["--role", "reviewer", "--head", rhead, "--pr", "7", "--nonce", "abc123", "--publish",
                       "--env-id", "env_x", "--model", "m-1", "--repo", "owner/name"])
        try:
            msg = fetched("dispatch/reviewer-rev-7", "PROMPT.md")
        except subprocess.CalledProcessError:
            msg = ""
        check("a reviewer's flag-path --publish publishes to dispatch/reviewer-rev-<PR> and points there",
              rc == 0 and " of dispatch/reviewer-rev-7 (`git fetch origin " in content(out.getvalue())
              and msg.startswith("CLOUD REVIEWER") and "Bus nonce: abc123." in msg)
        # Two sources, never one: the roster from the round's roster branch
        # (O17), the head from main. The branch is one commit ahead of main
        # with its own brief, so either swap shows.
        main_tip = git(work, "rev-parse", "origin/main").strip()
        roster.write_text(json.dumps({"repo": "owner/name", "groups": [{**grp, "brief": "On the branch.\n"}]}))
        git(work, "commit", "-q", "-am", "roster edit")
        git(work, "push", "-q", str(origin), "HEAD:refs/heads/handoff/audit-r10-roster")
        git(work, "fetch", "-q", str(origin), "+handoff/audit-r10-roster:refs/remotes/origin/handoff/audit-r10-roster")
        branch_tip = git(work, "rev-parse", "origin/handoff/audit-r10-roster").strip()
        dispatch()
        msg = fetched(line, "PROMPT.md")
        check("by default the brief is the round's roster branch's and the head is main's tip, not that branch's",
              "On the branch." in msg and main_tip in msg and branch_tip not in msg)
        # An explicit source wins over the default: main's brief differs from the branch's.
        dispatch(roster_ref="origin/main")
        msg = fetched(line, "PROMPT.md")
        check("an explicit roster ref is read, not the round's roster branch",
              "Changed." in msg and "On the branch." not in msg)
        overlay = Path(td) / "overlay.json"
        overlay.write_text(json.dumps({"environment_id": "env_x"}))
        out = io.StringIO()
        with contextlib.chdir(work), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = main(["--role", "fixer", "--group", "R10-X", "--model", "m-1", "--head", first,
                       "--roster-ref", "origin/main", "--overlay", str(overlay)])
        msg = fetched(line, "PROMPT.md")
        check("the --group CLI passes --head and --roster-ref through",
              rc == 0 and out.getvalue() == line + "\n" and first in msg and main_tip not in msg
              and "Changed." in msg and "On the branch." not in msg)
        # Every other input distinct from any call above (a second group, a model, a pr and a nonce
        # nothing published), so each value on the ref is this call's.
        roster.write_text(json.dumps({"repo": "owner/name", "groups": [
            {**grp, "brief": "On the branch.\n"}, {**grp, "group": "R10-Y", "resume": {"branch": "handoff/r10-y"}}]}))
        git(work, "commit", "-q", "-am", "second group")
        git(work, "push", "-q", str(origin), "HEAD:refs/heads/handoff/audit-r10-roster")
        git(work, "fetch", "-q", str(origin), "+handoff/audit-r10-roster:refs/remotes/origin/handoff/audit-r10-roster")
        relay = subprocess.run(["bash", str(HERE / "bus.sh"), "dispatch", "81", rhead, "cloud"], cwd=work,
                               env={**os.environ, **env}, capture_output=True, text=True).stdout
        # Search, never strip a prefix: `dispatch` prints its `review-packet:` line
        # above the nonce, and `_bus_dispatch` reads it the same way.
        nonce81 = proof_watch.verdict_nonce(relay) or ""
        check("a relay dispatch at a second pull request mints its nonce", len(nonce81) == 32)
        out = io.StringIO()
        with contextlib.chdir(work), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()), \
                _env(env):
            rc = main(["--role", "reviewer", "--group", "R10-Y", "--model", "m-9", "--head", rhead,
                       "--pr", "81", "--nonce", nonce81, "--overlay", str(overlay)])
        try:  # a wrong role or group publishes no reviewer-r10-y ref: the check, not a crash, says so
            msg = fetched("dispatch/reviewer-r10-y", "PROMPT.md")
            model = json.loads(fetched("dispatch/reviewer-r10-y", "PAYLOAD.json"))["job_config"]["ccr"][
                "session_context"]["model"]
        except subprocess.CalledProcessError:
            msg = model = ""
        check("the --group CLI passes --role, --group, --model, --pr and --nonce through",
              rc == 0 and out.getvalue() == "dispatch/reviewer-r10-y\n" and msg.startswith("CLOUD REVIEWER")
              and "PR #81 " in msg and f"Bus nonce: {nonce81}." in msg and model == "m-9")
        check("a nonce the relay minted is re-recorded by the seat fired with it, with its model, minting none",
              [l.split()[3:4] + l.split()[5:] for l in registry() if l.startswith("81 ")]
              == [[nonce81, "-"], [nonce81, "m-9"]])
        # A clone of main alone (--no-local: a local clone copies every object) holds none of the
        # dispatch ref's objects, so it must fetch the tip it extends.
        tip_before = git(work, "ls-remote", str(origin), "refs/heads/" + line).split()[0]
        other = Path(td) / "other"
        throwaway_git_clone(origin, other, "-q", "--no-local", "--single-branch", "--branch", "main")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                again = dispatch_group("fixer", "R10-X", "m-1", repo_dir=str(other), roster_ref="origin/main",
                                       environ=env)
        except Refusal:
            again = None
        git(work, "fetch", "-q", str(origin), "refs/heads/" + line)
        check("a re-dispatch from a second clone fast-forwards the existing ref",
              again == line and git(work, "rev-parse", "FETCH_HEAD").strip() != tip_before
              and git(work, "merge-base", "--is-ancestor", tip_before, "FETCH_HEAD") == "")




def _flag_checks(check) -> None:
    """Every flag the parser accepts is either forwarded or refused on the --group path.

    Table-driven from the parser itself, so a flag added without a GROUP_FLAGS
    entry fails here. `dispatch_group` is stubbed to record its call: a
    forwarded flag's distinct value must reach it, a refused flag must exit 2
    without calling it."""
    import contextlib
    import io
    dests = {a.dest for a in _parser()._actions if a.dest != "help"}
    switches = {a.dest for a in _parser()._actions if a.nargs == 0 and a.dest != "help"}
    ints = {a.dest for a in _parser()._actions if a.type is int}  # `--part`: a number, forwarded as one
    check("every flag the parser accepts has a --group disposition in GROUP_FLAGS, and no other",
          dests == set(GROUP_FLAGS))
    calls: list = []
    real = globals()["dispatch_group"]
    globals()["dispatch_group"] = lambda *a, **kw: calls.append((a, kw)) or "dispatch/stub"
    try:
        for dest in sorted(dests):
            base = {"role": "fixer", "group": "G-BASE", "model": "m-base"}
            value = "probe" if dest == "role" else (True if dest in switches else "7" if dest in ints else f"value-of-{dest}")
            argv = [x for k, v in {**base, dest: value}.items() for x in ("--" + k.replace("_", "-"), v)]
            if dest in switches:  # a switch takes no value
                argv = argv[:-1]
            calls.clear()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = main(argv)
            if GROUP_FLAGS.get(dest):
                check(f"--group refuses --{dest.replace('_', '-')} (exit 2, nothing dispatched)",
                      rc == 2 and not calls)
            else:
                sent = [*calls[0][0], *calls[0][1].values()] if len(calls) == 1 else []
                check(f"--group forwards --{dest.replace('_', '-')} to dispatch_group",
                      rc == 0 and (int(value) if dest in ints else value) in sent)
    finally:
        globals()["dispatch_group"] = real


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
    check("the reviewer is told to separate findings, each with its own Carry:, from evidence",
          "`## Findings` ending in its own `Carry: " in msg and "goes under `## Evidence`" in msg
          and "`## Block`" in msg)
    check("the reviewer is told carry_audit reads Evidence and a merge verdict's other sections by shape (P308, P314)",
          "by its shape alone: a finding only when it opens with a lead word" in msg
          and "a defect you hand on goes under `## Findings`" in msg)
    check("the reviewer is told to keep ev/ under 25 MB in all (#2563's HTTP 400)", "under 25 MB in all" in msg)
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
    prompts = {r: render(r, head, **base, pr="7", topic="t-1", nonce="abc123", design=head)["job_config"]["ccr"]["events"][0]
               ["data"]["message"]["content"] for r in ROLES}
    check("every role's prompt states the footer ban in one line (R10-FLY-NO-FOOTERS)",
          all(sum(FOOTER_BAN in line for line in t.splitlines()) == 1 for t in prompts.values()))
    check("and no rendered prompt carries the attribution it bans (ref_privacy's classes: the null control)",
          all(ref_privacy.attribution(t) == [] for t in prompts.values()))
    check("every role's prompt caps one tool call's wait under the 5-minute prompt-cache TTL (R10-FLY-CACHE-PROMPTS)",
          all(WAIT_LINE in t and "240 s" in WAIT_LINE for t in prompts.values()))
    check("every role's prompt carries the frugal-routing line once, verbatim (P398)",
          all(sum(line == FRUGAL_LINE for line in t.splitlines()) == 1 for t in prompts.values())
          and FRUGAL_LINE == ("Discovery reads (search, list, read across files) go through Agent subagents, as the "
                              "frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet "
                              "Agent subagent to do it rather than bypassing the guard; never set "
                              "FRUGAL_ALLOW_INLINE and never edit .claude/settings.json."))
    check("and no prompt grants an inline allowance the guard does not (tvofi 2026-11-09, Carry 9)",
          not any("inline search operations" in t for t in prompts.values()))
    owed_roles = ("reviewer", "fixer")  # literal: a mutant of OWED_REDS_ROLES must not move the test too
    check("the reviewer and the fixer are told, in one line citing its rule, that only a red "
          "`merge_train.py owed-reds` prints is owed an answer or blocks (tvofi 2026-11-07, 2026-11-09)",
          all(sum("`python3 tools/audit/seat/merge_train.py owed-reds`" in line and "defect-root-cause.md" in line
                  for line in prompts[r].splitlines()) == 1 for r in owed_roles))
    check("and no other role is (null control: a seat that never meets a check run)",
          not any("owed-reds" in prompts[r] for r in ROLES if r not in owed_roles))
    check("every role with a contract is told to render its pack, the probe is not",
          all(f"role_pack.py render {PACK_ROLE[r]} " in prompts[r] for r in PACK_ROLE)
          and "role_pack.py" not in prompts["probe"])
    check("the fixer reads its role file, not CLAUDE.md, which the harness already loaded",
          "dev/governance/roles/fixer.md" in prompts["fixer"] and "CLAUDE.md" not in prompts["fixer"])
    check("every role's setup line runs the toolchain check and stops on its REFUSE (#2709)",
          all(f"`{SETUP_CHECK}`, and on REFUSE stop" in t.splitlines()[1] for t in prompts.values()))
    rv = prompts["reviewer"]
    check("the reviewer waits for CI only by re-running merge_train.py classify --pr, 60 s apart, until 0, 1, 2 "
          "or 4 (APPROVAL-OWED, P345)",
          f"`python3 tools/audit/seat/merge_train.py classify {head} --pr 7` in the background, at least" in rv
          and "or 4 (APPROVAL-OWED: " in rv
          and "exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict)" in rv and "3 is WAIT" in rv)
    check("the reviewer is forbidden a pgrep or pkill waiter and a context the ruleset does not require",
          "Never wait with `pgrep` or `pkill`" in rv and "such as\n`prelude`" not in rv and "such as `prelude`" in rv)
    # CARRY 8 (P437 C2): every reviewer stop path ends in a verdict pushed to its probe ref, read back.
    hv = render("reviewer", head, **base, topic="t-1", nonce="abc123")["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
    check("the reviewer's setup or hook refusal pushes `seat-refused`, and it reads its ref back, at the PR and at the handoff",
          all(f"`Fix review: blocked {head} seat-refused: <the refusing line>`" in t
              and "never end your turn while a background poll runs" in t for t in (rv, hv))
          and "`git ls-remote origin refs/heads/probe/rev-7-abc123`" in rv
          and "`git ls-remote origin refs/heads/probe/revt-t-1-abc123`" in hv)
    check("a required-red packet does not stop the reviewer while classify reads WAIT: classify decides",
          "A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides" in rv)
    check("WAIT is bounded: past about 30 minutes an incomplete review pushes `ci-wait` with the classify line",
          re.search(r"still prints WAIT after about 30 minutes of polling, stop waiting: .*?If the review is not "
                    rf"complete then, push `Fix review: blocked {head} ci-wait: <the last classify line>`", rv, re.S)
          is not None and "ci-wait" not in hv)
    check("no other role is told any reviewer stop push (null control: the fixer prompt carries none)",
          all("seat-refused" not in t and "ci-wait" not in t and "refs/heads/probe/" not in t
              for r, t in prompts.items() if r != "reviewer"))
    check("no other role is told to wait on merge_train.py classify (null control)",
          all("merge_train.py classify" not in t and "pgrep" not in t for r, t in prompts.items() if r != "reviewer"))
    wip, fx = f"refs/heads/{WIP_NS}/t-1", prompts["fixer"]
    check("the fixer step-pushes fast-forward to handoff-wip/<topic>, never to handoff/, and the tail allows it",
          f"push each verified step, fast-forward only, to {wip} before any wait" in fx
          and "never step-push to\nhandoff/t-1" not in fx and "never step-push to handoff/t-1" in fx
          and f"except your return refs and {wip} and {wip}-body." in fx)
    check("the fixer deletes the step ref only after body_push.sh succeeds",
          0 <= fx.find("body_push.sh t-1") < fx.find(f"`git push origin :{wip}`"))
    check("the fixer hands off at its first clean prepr.sh head and re-merges main only on a merge-tree conflict",
          "Hand off at your first clean `tools/pr/prepr.sh` head" in fx
          and "needs no re-merge and no second run" in fx
          and 0 <= fx.find("Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict")
          < fx.find("push the code to refs/heads/handoff/t-1")
          and "`git merge origin/main`, rerun" not in fx)
    check("the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main",
          "`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict" in rv
          and "never on a head that is behind main but merges cleanly" in rv)
    check("the fixer is told to push BLOCKED.md with a Question line before stopping on a question",
          f"first push `BLOCKED.md` with a `Question:` line to refs/heads/{WIP_NS}/t-1" in fx
          and all("BLOCKED.md" not in t for r, t in prompts.items() if r != "fixer"))
    check("no other role is told the merge-tree block rule (null control)",
          all("behind main but merges cleanly" not in t for r, t in prompts.items() if r != "reviewer"))
    check("no other role is licensed a step ref (null control)",
          all(WIP_NS not in t for r, t in prompts.items() if r != "fixer"))
    ident = f"`git config user.name {SEAT_NAME} && git config user.email {SEAT_EMAIL}`"
    check("the fixer and the probe pin the seat's noreply identity in the setup line, no other role does (null)",
          all((ident in t.splitlines()[1]) == (r in COMMITTING_ROLES) for r, t in prompts.items())
          and set(COMMITTING_ROLES) == {"fixer", "probe"})
    sh = (Path(__file__).with_name("cloud-setup.sh")).read_text()
    shid = [(m.group(1), m.group(2)) for m in [re.search(r"^SEAT_NAME=(\S+)\nSEAT_EMAIL=(\S+)$", sh, re.M)] if m]
    check("cloud-setup.sh exports the same SEAT_NAME/SEAT_EMAIL as this module",
          shid == [(SEAT_NAME, SEAT_EMAIL)])
    # A design choice, pinned by value: the arms above compare against the
    # constant and pass for any identity, so the old `seat` read green.
    check("the seat identity is hpo-fixer at the owner's noreply address",
          (SEAT_NAME, SEAT_EMAIL) == ("hpo-fixer", "70032254+tvofi@users.noreply.github.com"))
    for role, ref in (("fixer", "dispatch/fixer-t-1"), ("reviewer", "dispatch/reviewer-rev-7")):
        a = dict(pr="7" if role == "reviewer" else "", topic="" if role == "reviewer" else "t-1",
                 nonce="abc123" if role == "reviewer" else "")
        check(f"the {role}'s publish ref is {ref}", dispatch_ref(role, a["topic"], a["pr"]) == ref)
        pin = "fedcba9876543210" * 2 + "fedcba98"
        ptr = render(role, head, **base, **a, publish_ref=ref, pin=pin)["job_config"]["ccr"]["events"][0][
            "data"]["message"]["content"]
        check(f"a published {role}'s event is a stub: the seat line, the footer ban and PROMPT.md at the pinned SHA",
              ptr.startswith(_seat_line(role, "owner/name", a["pr"], head, a["topic"], a["nonce"]))
              and f"git fetch origin {pin} && git show {pin}:PROMPT.md" in ptr and f"of {ref} " in ptr
              and sum(FOOTER_BAN in x for x in ptr.splitlines()) == 1 and len(ptr) < len(prompts[role]))
        check(f"a published {role} with no 40-hex pin is refused", refused(role, publish_ref=ref, pin="")
              and refused(role, publish_ref=ref, pin=ref) and not refused(role, publish_ref=ref, pin=pin))
    check("a reviewer's stub carries its nonce", "abc123" in render(
        "reviewer", head, **base, pr="7", nonce="abc123", publish_ref="dispatch/reviewer-rev-7", pin=head)[
        "job_config"]["ccr"]["events"][0]["data"]["message"]["content"])
    check("a 39-hex head is refused", refused(h=head[:-1]))
    check("a 41-hex head is refused", refused(h=head + "0"))
    check("an upper-case head is refused", refused(h=head.upper()))
    check("a non-hex head is refused", refused(h="g" * 40))
    check("an empty reviewer nonce is refused", refused(nonce=""))
    check("a blank reviewer nonce is refused", refused(nonce="  "))
    check("a reviewer with neither --pr nor --topic is refused", refused(pr="", topic=""))
    check("a reviewer's --pr must be a number when it is given", refused(pr="x7"))
    # CARRY 0: a reviewer at the handoff, before the pull request exists, keyed by the topic.
    def reviewer_text(**kw):
        a = {**base, "nonce": "abcd1234" * 4, **kw}
        return render("reviewer", head, **a)["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]
    hand, pull = reviewer_text(pr="", topic="t-1"), reviewer_text(pr="7", topic="t-1")
    check("a reviewer at the handoff returns on probe/revt-<topic>-<nonce8> with the subject `verdict <topic> <head>`",
          "refs/heads/probe/revt-t-1-abcd1234" in hand and f'-m \"verdict t-1 {head}\"' in hand)
    check("and reads the body at handoff-body/<topic>, renders no packet and waits on no CI",
          "handoff-body/t-1" in hand and "review_packet.py render" not in hand and "merge_train.py classify" not in hand)
    check("a reviewer with a PR is told to return a `pending-ci:` draft rather than wait without bound; a handoff reviewer, which waits on no CI, is not",
          "pending-ci: <the context names" in pull and "pending-ci" not in hand)
    check("null control: a reviewer with a PR number is unchanged (probe/rev-<pr>, the packet, the CI wait)",
          "refs/heads/probe/rev-7-abcd1234" in pull and f'-m \"verdict 7 {head}\"' in pull
          and "review_packet.py render --pr 7" in pull and "merge_train.py classify" in pull and "revt-" not in pull)
    check("a fixer without --topic is refused", refused("fixer", topic=""))
    check("a design reviewer without the 40-hex design tip is refused on the flag path",
          refused("design-reviewer", design="") and not refused("design-reviewer", design=head))
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
    _flag_checks(check)
    _group_checks(check)
    print(f"cloud_dispatch self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


#: Every flag `_parser()` accepts, and what the --group path does with it: None
#: when main() forwards it to `dispatch_group`, else the refusal's reason. The
#: self-test drives each entry through main() and refuses a flag missing here.
GROUP_FLAGS = {
    "role": None, "group": None, "model": None, "head": None, "roster_ref": None,
    "pr": None, "nonce": None, "overlay": None, "design_exempt": None, "reviewed_head": None,
    "carry_only": None, "record_pr": None, "part": None,
    "design": "dispatch_group reads the tip of design/<group> on origin",
    "topic": "the roster gives the topic (the group's branch)",
    "brief": "the roster gives the brief",
    "repo": "the roster gives the repository",
    "env_id": "the environment id comes from the overlay or $HPO_CLOUD_ENV_ID",
    "out": "--group publishes the payload to its ref and prints the ref name",
    "publish": "--group always publishes",
}


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="cloud_dispatch.py", description=__doc__.split("\n")[0])
    ap.add_argument("--role", required=True, choices=ROLES)
    ap.add_argument("--head")
    ap.add_argument("--group", help="a roster group: publish its seat to a dispatch ref, print the ref name")
    ap.add_argument("--roster-ref", help="default: the round roster branch, else origin/main "
                    "(roster_lib.default_roster_ref)")
    ap.add_argument("--pr", default="")
    ap.add_argument("--topic", default="")
    ap.add_argument("--nonce", default="")
    ap.add_argument("--design", default="", help="a design reviewer's reviewed design/<topic> tip (flag path)")
    ap.add_argument("--reviewed-head", default="", help="a later round's reviewer: the head the previous verdict "
                    "names, so the packet renders its delta (fix-review.md step 12)")
    ap.add_argument("--design-exempt", default="", help="a fixer dispatch for an L/XL group whose approved "
                    "design, pre-study or prototype is already on record: the reason")
    ap.add_argument("--brief")
    ap.add_argument("--env-id")
    ap.add_argument("--model", help="with --group, omitted: read from the roster (model.<role>, <role>Model), "
                    "and the field is printed")
    ap.add_argument("--carry-only", action="store_true", help="--group reviewer: a review_carry CARRY or delta re-review (sonnet)")
    ap.add_argument("--record-pr", action="store_true", help="--group reviewer: a record-PR review (sonnet)")
    ap.add_argument("--part", type=int, default=0, help="--group fixer over five pending carries: the serial "
                    "part k to dispatch (the refusal without it prints the split)")
    ap.add_argument("--repo")
    ap.add_argument("--overlay")
    ap.add_argument("--out")
    ap.add_argument("--publish", action="store_true", help="publish PROMPT.md to dispatch/<role>-<topic or "
                    "rev-PR> and fire the seat with a pointer to it")
    return ap


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    ap = _parser()
    args = ap.parse_args(argv)
    try:
        if args.group:
            for dest, why in GROUP_FLAGS.items():
                if why and getattr(args, dest) != ap.get_default(dest):
                    raise Refusal(f"--{dest.replace('_', '-')} does not apply with --group: {why}")
            print(dispatch_group(args.role, args.group, args.model or "", roster_ref=args.roster_ref,
                                 head=args.head or "", pr=args.pr, design_exempt=args.design_exempt,
                                 nonce=args.nonce, overlay=args.overlay, reviewed_head=args.reviewed_head,
                                 carry_only=args.carry_only, record_pr=args.record_pr, part=args.part))
            return 0
        if args.part:
            raise Refusal("--part applies only with --group: the roster gives the carries it splits")
        if not args.head:
            raise Refusal("--head is required without --group")
        brief = ""
        if args.brief:
            try:
                brief = Path(args.brief).read_text()
            except OSError as e:
                raise Refusal(f"unreadable brief: {e.__class__.__name__}")
        known = dict(pr=args.pr, topic=args.topic, nonce=args.nonce, brief=brief, design=args.design,
                     reviewed_head=args.reviewed_head, **_config(args))
        if args.publish:
            payload = publish_seat(".", dispatch_ref(args.role, args.topic, args.pr), args.role, args.head,
                                   **known)
        else:
            payload = render(args.role, args.head, **known)
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
