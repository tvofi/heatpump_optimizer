#!/usr/bin/env python3
"""owner_only_channel.py -- every public path of the audit pipeline, closed for an owner-only dimension.

    python3 -I dev/audit/harnesses/owner_only_channel.py [--only P4,P5,...]

A dimension whose dev/audit/config/scopes.json entry carries `owner_only: true`
publishes nothing (R11-PRE-SECURITY-PRIVACY). This harness plants a CANARY --
a hex nonce and a dimension number drawn per run, never written to the tree --
as a finding of such a dimension, and drives each public path of the pipeline
with it. An arm passes when the canary reached nothing public: no ref of a
scratch origin, no stub `gh` or `curl`, no printed line. Each arm carries its
NULL CONTROL: the same canary under a public dimension, or with the closure's
switch off, reaches the place the arm watches, so the arm is shown able to
see a leak.

  P1-P3  the two workflow drivers: the arms are tools/policy/check-wave-script.mjs's
         'the owner-only dimensions' block, which drives both scripts over a
         fixture dimension. Named here by line; a missing or failing one fails.
  P4     tools/audit/fold_ledger.py check and fold, over a scratch tree.
  P5     tools/audit/seat/shims/seat-gh in owner-only mode: every write refused
         before the real gh; null: mode unset, the stub gh receives it.
  P5b    the writers that hold their own credential, run in the launcher's
         environment: each stops on its own fail-closed line before any call.
         The list is compared with `git grep -l -E 'mint_token|openssl dgst
         -sha256 -sign|GIT_SSH_COMMAND' -- tools`: a file that command newly
         returns owes an arm.
  P7     tools/audit/seat/ref_privacy.py guard, in a scratch checkout whose
         scopes declare the dimension: the id in a ref name, a message and a
         body; and one push through the guard to a scratch bare origin.
  P10    tools/audit/seat/finder_overlap.py's own owner-only arms, by line.
  SCOPES tools/audit/check_scopes.py over the planned shape (cells, an empty
         file universe, an axis of five sources): it passes whole, and a
         planted overlap and a planted orphan on the axis are each refused.
  SET    the four readers of the declaration agree on one fixture table.

INSTRUCTION-ONLY, no arm, said so that no reader takes a green run for more
than it is: a roster line written by hand (P6), another dimension's report
meeting such a matter (P8), and this dimension's own pull requests (P9) are
closed by rule and by P7's tripwire on the finding id; a weakness described
in prose without its id is caught by none of them.

Prints one line per arm, then `OWNER-ONLY CHANNEL HELD` or `BROKEN` naming
each arm that read otherwise; exit 0 or 1.
"""
from __future__ import annotations

import importlib.util
import json
import os
import secrets
import shutil
import stat
import subprocess
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
sys.path.insert(0, str(ROOT / "tests"))
from throwaway_git import throwaway_git_init  # noqa: E402

NONCE = secrets.token_hex(16)
DIM = f"D{200 + secrets.randbelow(700)}"          # the owner-only dimension of this run
SEAT, FID = f"{DIM}-s1", f"{DIM}-s1-{secrets.randbelow(100):02d}"
PUBLIC_FID = f"D15-s1-{secrets.randbelow(100):02d}"
PY = [sys.executable, "-I"]
RESULTS: list[tuple[str, bool, str]] = []

#: The writers that mint or sign with a credential of their own (design row P5b), and the two
#: files the sibling command also returns that are no writer.
CREDENTIALED = ("tools/pr/app_push.sh", "tools/pr/app_comment.sh", "tools/pr/app_approve.sh", "tools/audit/seat/body_patch.sh",
                "tools/audit/seat/remerge_main.sh", "tools/audit/seat/bus.sh", "tools/release/stamp.py")
NOT_WRITERS = {"tools/pr/app_mint.sh": "sourced by its callers, each an arm of its own",
               "tools/audit/seat/remerge_main_selftest.py": "a test of remerge_main.sh"}
SIBLING = ["git", "grep", "-l", "-E", "mint_token|openssl dgst -sha256 -sign|GIT_SSH_COMMAND", "--", "tools"]


def arm(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(("ok   " if ok else "FAIL ") + name + ("" if ok or not detail else " -- " + detail.replace(NONCE, "<nonce>")[:300]))


def run(argv, cwd=None, env=None, stdin=None, timeout=300):
    more = {"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}  # a stub that reads stdin must meet its end
    p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, **more)
    return p.returncode, p.stdout + p.stderr


def load(rel: str):
    spec = importlib.util.spec_from_file_location("under_test_" + Path(rel).stem, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str((ROOT / rel).parent))
    sys.modules[spec.name] = mod  # a dataclass resolves its module by name
    spec.loader.exec_module(mod)
    return mod


def named_lines(out: str, wanted: list[str], what: str) -> None:
    """Each wanted line is present and `ok`, and the run holds no FAIL of its own."""
    lines = [ln.strip() for ln in out.splitlines()]
    for w in wanted:
        hit = [ln for ln in lines if w in ln]
        arm(f"{what}: {w}", len(hit) >= 1 and all(ln.startswith("ok") for ln in hit), "missing" if not hit else hit[0][:120])


def p1_p3() -> None:
    rc, out = run(["node", str(ROOT / "tools/policy/check-wave-script.mjs")])
    start = out.find("-- The owner-only dimensions")
    block = out[start:out.find("\n-- ", start + 5)] if start >= 0 else ""
    arm("P1-P3: the grader's owner-only block ran and holds no FAIL", bool(block) and "FAIL" not in block, "block missing or red")
    named_lines(block, [
        "a public round dispatches no seat of an owner-only dimension",
        "nor does a box run",
        "a box row naming an owner-only seat stops the round before Prepare",
        "a run handed a private root dispatches the owner-only seats and nothing else",
        "nothing a seat replied is in the return value or a log line",
        "a seat that throws, then returns nothing, is retried once",
        "a red probe stops the run before any seat",
        "null control: the same dimension with the flag removed is dispatched",
        "null control: the same canary under a D15 seat",
        "the public verification pass refuses a register holding an owner-only finding",
        "a private root with args.file, inside the checkout, or with no owner-only dimension is refused",
        "a run handed a private root verifies and judges the owner-only dimensions and nothing else",
        "a verifier or judge that throws leaves a fixed sentence and no reply text",
        "null control: with the dimension out of the set the same finding reaches the judge",
    ], "P1-P3")


def scratch_tree(td: Path, flag=True) -> Path:
    """A tree holding the instruments under test and a scopes.json declaring DIM by `flag`."""
    t = td / "tree"
    for rel in ("tools/audit/fold_ledger.py", "tools/audit/seat/ref_privacy.py", "tools/audit/seat/finder_overlap.py",
                "tools/audit/seat/plant_recall.py"):
        (t / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, t / rel)
    (t / "dev/audit/config").mkdir(parents=True, exist_ok=True)
    entry = {"mode": "cells", "universe": [], "steps": ["M1"], "seats": {"s1": [{"files": ["**"], "steps": ["M1"]}]}}
    if flag is not None:
        entry["owner_only"] = flag
    (t / "dev/audit/config/scopes.json").write_text(json.dumps({"D15": {"seats": {"s1": []}}, DIM: entry}))
    return t


def p4(td: Path) -> None:
    fl = load("tools/audit/fold_ledger.py")

    def tree(fid: str, name: str) -> Path:
        t = scratch_tree(td / name)
        judge = {"round": 2, "verdicts": [{"id": fid, "verdict": "verified", "class": "P1", "title": NONCE, "note": NONCE}]}
        fl._plant(str(t), fl._settle({"P1": fl._entry([]), "_rca": {}, "_unclassified": [], "_excluded": []}), judge)  # noqa: SLF001
        return t

    t = tree(FID, "p4")
    before = (t / fl.LEDGER).read_text()
    rc, out = run(PY + [str(t / "tools/audit/fold_ledger.py"), "check", "--root", str(t)])
    arm("P4: check refuses a JUDGE.json holding the canary under an owner-only id, without the id or the nonce",
        rc == 1 and "OWNER-ONLY: dev/audit/rounds/round2/JUDGE.json" in out and FID not in out and NONCE not in out, out[-200:])
    rc, out = run(PY + [str(t / "tools/audit/fold_ledger.py"), "fold", "--round", "2", "--root", str(t)])
    arm("P4: fold refuses the round and leaves the ledger byte-identical",
        rc != 0 and "OWNER-ONLY" in out and (t / fl.LEDGER).read_text() == before and NONCE not in out and FID not in out, out[-200:])
    t = tree(PUBLIC_FID, "p4null")
    rc, out = run(PY + [str(t / "tools/audit/fold_ledger.py"), "fold", "--round", "2", "--root", str(t)])
    rc2, out2 = run(PY + [str(t / "tools/audit/fold_ledger.py"), "check", "--root", str(t)])
    arm("P4 null: the same canary under a D15 id is folded into the ledger, and check passes",
        rc == 0 and f"R2 {PUBLIC_FID}" in (t / fl.LEDGER).read_text() and rc2 == 0 and "OWNER-ONLY" not in out + out2, (out + out2)[-200:])


def stub_bin(td: Path, names=("gh", "curl")) -> tuple[Path, Path]:
    """A directory of stubs that record their argv and stdin to one log and exit 0."""
    b, log = td / "stubs", td / "stub.log"
    b.mkdir(parents=True, exist_ok=True)
    log.write_text("")
    for n in names:
        (b / n).write_text(f'#!/bin/bash\n{{ printf "%s" "{n}"; printf " %q" "$@"; printf "\\n"; [ -t 0 ] || cat; }} >> "{log}" 2>/dev/null\nexit 0\n')
        (b / n).chmod(0o755)
    return b, log


def p5(td: Path) -> None:
    stubs, log = stub_bin(td / "p5", ("gh",))
    shim = str(ROOT / "tools/audit/seat/shims/seat-gh")
    base = {"PATH": f"{stubs}:/usr/bin:/bin", "HOME": str(td / "p5"), "HPO_STATE_DIR": str(td / "p5" / "state")}
    writes = [["issue", "create", "-t", NONCE, "-b", NONCE], ["issue", "comment", "7", "-b", NONCE], ["pr", "comment", "7", "-b", NONCE],
              ["pr", "create", "-t", NONCE, "-b", NONCE], ["pr", "review", "7", "--approve", "-b", NONCE], ["pr", "merge", "7"],
              ["release", "create", "v0", "-n", NONCE], ["gist", "create", "-d", NONCE], ["api", "repos/o/r/issues", "-f", f"title={NONCE}"],
              ["api", "-X", "POST", "repos/o/r/issues/7/comments", "-f", f"body={NONCE}"], ["api", "--method=PATCH", "repos/o/r/issues/7"],
              ["api", "repos/o/r/git/refs", "--input", "x.json"], ["api", "graphql", "-f", "query=mutation{addComment(input:{})}"],
              ["api", "-XDELETE", "repos/o/r/git/refs/heads/x"], ["repo", "edit", "-d", NONCE], ["label", "create", NONCE],
              ["workflow", "run", "x.yml"], ["secret", "set", "X", "-b", NONCE], ["auth", "token"], ["frobnicate", NONCE]]
    refused = [run(["bash", shim] + w, env={**base, "HPO_OWNER_ONLY": "1"}) for w in writes]
    arm(f"P5: in owner-only mode the shim refuses each of {len(writes)} write spellings itself, and the real gh is never started",
        all(rc == 1 and "owner-only mode" in out for rc, out in refused) and log.read_text() == "",
        f"{sum(1 for rc, _ in refused if rc != 1)} passed; log {log.read_text()[:80]!r}")
    reads = [["api", "repos/o/r/issues?per_page=100&page=1"], ["pr", "view", "7"], ["--version"]]
    got = [run(["bash", shim] + r_, env={**base, "HPO_OWNER_ONLY": "1"}) for r_ in reads]
    arm("P5: a read still passes in that mode (the mode is no blanket refusal)",
        all(rc == 0 for rc, _ in got) and len(log.read_text().splitlines()) == len(reads), log.read_text()[:120])
    log.write_text("")
    rc, out = run(["bash", shim] + writes[0], env=base)
    arm("P5 null: with the mode unset the same write reaches the stub gh, the canary with it",
        rc == 0 and NONCE in log.read_text(), log.read_text()[:120])


def p7(td: Path) -> None:
    t = scratch_tree(td / "p7")
    (t / "tests").mkdir(exist_ok=True)
    guard = PY + [str(t / "tools/audit/seat/ref_privacy.py"), "guard"]
    cases = {"a ref name": ["--ref", f"handoff/fix-{FID}"], "a message": ["--ref", "handoff/x", "--message", f"closes {FID}: {NONCE}"]}
    for where, args in cases.items():
        rc, out = run(guard + args)
        arm(f"P7: the guard refuses an owner-only finding id in {where}, quoting neither the id nor the nonce",
            rc == 3 and "owner-only-id" in out and FID not in out and NONCE not in out, out[-200:])
    body = td / "p7" / "body.md"
    body.write_text(f"## Figures\n\n- {FID}: {NONCE}\n")
    rc, out = run(PY + [str(t / "tools/audit/seat/ref_privacy.py"), "body-lines", str(body)])
    arm("P7: a comment or pull-request body holding the id is refused by its line", rc == 1 and "line 3: owner-only-id" in out and NONCE not in out, out)
    rc, out = run(guard + ["--ref", f"handoff/fix-{PUBLIC_FID}", "--message", f"closes {PUBLIC_FID}: {NONCE}"])
    rc2, out2 = run(guard + ["--ref", f"handoff/{SEAT}", "--message", f"{DIM} seats and steps, {SEAT}, {DIM}.M2"])
    arm("P7 null: the same canary under a D15 id passes the guard, and so do the owner-only dimension's name and seat id",
        rc == 0 and rc2 == 0, out + out2)
    # One push through the guard, to a scratch bare origin: the commits a push publishes are judged by --commits.
    origin, work = td / "p7" / "origin.git", td / "p7" / "work"
    work.mkdir()
    env = throwaway_git_init(str(work), "-q", "-b", "main")
    env = {**env, "GIT_AUTHOR_EMAIL": "70032254+tvofi@users.noreply.github.com", "GIT_COMMITTER_EMAIL": "70032254+tvofi@users.noreply.github.com"}
    origin.mkdir()
    throwaway_git_init(str(origin), "-q", "--bare")

    def guarded_push(branch: str, message: str) -> tuple[bool, str]:
        (work / "f.txt").write_text(branch)
        subprocess.run(["git", "add", "-A"], cwd=work, env=env, check=True)
        subprocess.run(["git", "commit", "-q", "-m", message], cwd=work, env=env, check=True)
        rc, out = run(guard + ["--ref", branch, "--commits", "HEAD", "-C", str(work)], env=env)
        if rc == 0:
            subprocess.run(["git", "push", "-q", str(origin), f"HEAD:refs/heads/{branch}"], cwd=work, env=env, check=True)
        refs = subprocess.run(["git", "for-each-ref", "--format=%(refname)"], cwd=origin, env=env, capture_output=True, text=True).stdout
        log = subprocess.run(["git", "log", "--all", "--format=%B"], cwd=origin, env=env, capture_output=True, text=True).stdout
        return rc == 0, refs + log

    pushed, seen = guarded_push("handoff/null", f"record {PUBLIC_FID}: {NONCE}")
    arm("P7 null: a guarded push whose commit message carries the canary under a D15 id lands on the scratch origin",
        pushed and NONCE in seen and "refs/heads/handoff/null" in seen, seen[-160:])
    pushed, seen = guarded_push("handoff/canary", f"record {FID}: {NONCE}-second")
    arm("P7: the same push with the owner-only id is refused by the guard, and no ref of the scratch origin holds it",
        not pushed and "handoff/canary" not in seen and f"{NONCE}-second" not in seen and FID not in seen, seen[-160:])


def p10() -> None:
    rc, out = run(PY + [str(ROOT / "tools/audit/seat/finder_overlap.py"), "--self-test", "--no-mutants"])
    named_lines(out, [
        "owner-only seat: the canary seat is refused, no pair written, no twin path printed",
        "owner-only estimate: a pair naming the canary seat is refused before any report is read",
        "owner-only null: the same seat with the flag removed is admitted and its twin path printed",
        "owner-only null: a D15 seat of the committed scopes is admitted beside an owner-only dimension",
    ], "P10")


def scopes_shape() -> None:
    table = json.loads((ROOT / "dev/audit/config/scopes.json").read_text())
    steps, src = ["M1", "M2", "M3", "M4"], ["S1", "S2", "S3", "S4", "S5"]
    good = {"s1": [{"files": ["**"], "steps": ["M1", "M2"], "axis": ["S1"]}], "s2": [{"files": ["**"], "steps": ["M3", "M4"], "axis": ["S1"]}],
            "s3": [{"files": ["**"], "steps": steps, "axis": ["S2"]}], "s4": [{"files": ["**"], "steps": steps, "axis": ["S3"]}],
            "s5": [{"files": ["**"], "steps": steps, "axis": ["S4", "S5"]}]}
    overlap, orphan = json.loads(json.dumps(good)), json.loads(json.dumps(good))
    overlap["s4"][0]["axis"] = ["S3", "S2"]
    orphan["s5"][0]["axis"] = ["S4"]

    def check(seats):
        with tempfile.NamedTemporaryFile("w", suffix=".json") as fh:
            json.dump({**table, DIM: {"mode": "cells", "universe": [], "axis": {"source": src}, "steps": steps, "seats": seats, "owner_only": True}}, fh)
            fh.flush()
            return run(PY + [str(ROOT / "tools/audit/check_scopes.py"), "--repo", str(ROOT), "--ref", "HEAD", "--scopes", fh.name])
    rc, out = check(good)
    arm("SCOPES null: the planned shape (five seats over four steps and five sources, an empty file universe, owner_only) passes check_scopes",
        rc == 0 and f"ok {DIM} mode=cells seats=5" in out, out[-300:])
    rc, out = check(overlap)
    arm("SCOPES: a planted overlap on the source axis is refused by the cell it names", rc == 1 and "owned twice" in out and "'S2')" in out, out[-300:])
    rc, out = check(orphan)
    arm("SCOPES: a planted orphan on the source axis is refused by the cell it names", rc == 1 and "unowned" in out and "'S5')" in out, out[-300:])


def one_set(td: Path) -> None:
    """The declaration has one owner and four readers; over one tricky table they return one set."""
    table = {"_note": ["x"], "D3": {"owner_only": True, "seats": {}}, "D4": {"owner_only": "true"}, "D5": {"owner_only": 1}, "D6": {"owner_only": False},
             "D7": None, "D8": {}, "D12": {"owner_only": True}}
    want = ["D12", "D3"]
    t = td / "set"
    (t / "dev/audit/config").mkdir(parents=True)
    (t / "dev/audit/config/scopes.json").write_text(json.dumps(table))
    got = {
        "ref_privacy.py": sorted(load("tools/audit/seat/ref_privacy.py").owner_only_dims(t)),
        "finder_overlap.py": sorted(load("tools/audit/seat/finder_overlap.py").owner_only(table)),
        "fold_ledger.py": sorted(load("tools/audit/fold_ledger.py").owner_only(str(t))),
    }
    src = (ROOT / ".claude/workflows/audit-find.js").read_text()
    block = src[src.index("// DISPATCH:BEGIN"):src.index("// DISPATCH:END")]
    rc, out = run(["node", "-e", f"{block}\nprocess.stdout.write(JSON.stringify(ownerOnlyOf({json.dumps(table)})))"])
    got["audit-find.js"] = sorted(json.loads(out)) if rc == 0 else [f"node exited {rc}"]
    arm("SET: the four readers of scopes.json's owner_only return one set over one table (true alone declares)",
        all(v == want for v in got.values()), json.dumps(got))


def launcher_env(td: Path, stubs: Path) -> dict:
    """The environment tools/audit/seat/owner_only.py builds, with the stubs ahead of the system tools."""
    oo = load("tools/audit/seat/owner_only.py")
    root = td / "private"
    root.mkdir(mode=0o700)
    oo.prepare(str(root), [str(td / "owner-identity")], [])
    env = oo.session_env(str(root), "MODEL_KEY", {"MODEL_KEY": "k"})
    env["PATH"] = f"{stubs}:{os.environ.get('PATH', oo.SYSTEM_PATH)}"
    return env


def p5b(td: Path) -> None:
    rc, out = run(SIBLING, cwd=ROOT)
    found = sorted(out.split())
    owed = sorted(set(found) - set(CREDENTIALED) - set(NOT_WRITERS))
    gone = sorted((set(CREDENTIALED) | set(NOT_WRITERS)) - set(found))
    arm("P5b: every file the sibling command returns is an arm here or named as no writer, and every arm is still returned",
        rc == 0 and not owed and not gone, f"owes an arm: {owed}; no longer returned: {gone}")
    for rel in CREDENTIALED:
        try:
            WRITER_ARMS[rel](td / ("w-" + Path(rel).stem), rel)
        except Exception as e:  # noqa: BLE001 -- a writer arm that crashes is a failed arm, and the next still runs
            arm(f"P5b: {rel}: the arm ran to its end", False, f"{type(e).__name__}: {str(e)[:160]}")


def writer(td: Path, rel: str, argv, refusal: str, files: dict, cwd=None, rc_want=1, extra=None) -> None:
    """One credentialed writer in the launcher's environment: it stops on `refusal` and the stubs see nothing.
    Null: the same command with a throwaway identity directory holding `files` no longer stops there."""
    td.mkdir(parents=True, exist_ok=True)
    stubs, log = stub_bin(td, ("gh", "curl", "ssh", "sleep"))
    env = {**launcher_env(td, stubs), **(extra or {})}
    rc, out = run(argv, cwd=cwd, env=env, timeout=120)
    arm(f"P5b: {rel} stops on its own fail-closed line before any call, in the launcher's environment",
        rc == rc_want and refusal in out and not [ln for ln in log.read_text().splitlines() if ln.startswith(("curl", "ssh"))] and NONCE not in log.read_text(),
        f"rc {rc}: {out[-200:]!r} log {log.read_text()[:100]!r}")
    ident = td / "throwaway-identity"
    ident.mkdir()
    for name, content in files.items():
        if content == "KEY":
            subprocess.run(["openssl", "genrsa", "-out", str(ident / name), "2048"], capture_output=True, check=True)
        else:
            (ident / name).write_text(content)
        (ident / name).chmod(0o600)
    rc, out = run(argv, cwd=cwd, env={**env, "HPO_IDENTITY_DIR": str(ident)}, timeout=120)
    arm(f"P5b null: {rel} with a throwaway identity directory no longer stops on that line (the refusal is the absent key's)",
        refusal not in out, f"rc {rc}: {out[-200:]!r}")


def w_app_push(td, rel):
    wt = td / "wt"
    wt.mkdir(parents=True)
    writer(td, rel, ["bash", str(ROOT / rel), "--branch-only", "o/r", str(wt), "batch/" + NONCE[:8]],
           "hpo-author.appid.txt (fail closed)", {"hpo-author.appid.txt": "424242\n", "hpo-author.pem": "KEY"})


def w_app_comment(td, rel):
    td.mkdir(parents=True)
    body = td / "verdict.md"
    body.write_text(f"Fix review: merge {'a' * 40}\n\n{NONCE}\n")
    writer(td, rel, ["bash", str(ROOT / rel), "o/r", "1", str(body)], "identity-approver.appid (fail closed)",
           {"identity-approver.appid": "424242\n", "identity-approver.pem": "KEY"})


def w_app_approve(td, rel):
    writer(td, rel, ["bash", str(ROOT / rel), "o/r", "1", "a" * 40], "identity-approver.appid (fail closed)",
           {"identity-approver.appid": "424242\n", "identity-approver.pem": "KEY"})


def w_body_patch(td, rel):
    td.mkdir(parents=True)
    body = td / "body.md"
    body.write_text(f"{NONCE}\n")
    writer(td, rel, ["bash", str(ROOT / rel), "--repo", "o/r", "1", "a" * 40, str(body)], "hpo-author.appid.txt (fail closed)",
           {"hpo-author.appid.txt": "424242\n", "hpo-author.pem": "KEY"})


def w_bus(td, rel):
    td.mkdir(parents=True)
    origin = td / "origin.git"   # the bus's remote for this arm: with a key it fetches, and never from the real origin
    origin.mkdir()
    throwaway_git_init(str(origin), "-q", "--bare")
    writer(td, rel, ["bash", str(ROOT / rel), "confirm", "1", "a" * 40], "no hpo-approver key on this machine",
           {"identity-approver.pem": "KEY"}, cwd=ROOT, extra={"HPO_BUS_REMOTE": str(origin), "HPO_BUS_STATE": str(td / "bus-state")})


def w_remerge(td, rel):
    """Its non-fork path reads no key itself: it runs app_push.sh, whose fail-closed line it reports. So it has no null of
    its own: app_push.sh's is its null."""
    td.mkdir(parents=True)
    stubs, log = stub_bin(td, ("gh", "curl", "ssh", "sleep"))
    env = launcher_env(td, stubs)
    wt, body = td / "wt", td / "body.md"
    wt.mkdir()
    body.write_text(f"{NONCE}\n")
    rc, out = run(["bash", str(ROOT / rel), "1", str(wt), "fix/x", str(body)], cwd=ROOT, env=env, timeout=120)
    arm(f"P5b: {rel} fails at its push with no key, and no curl or ssh is started (its key read is app_push.sh's, the null above)",
        rc != 0 and "REMERGE FAILED" in out and not [ln for ln in log.read_text().splitlines() if ln.startswith(("curl", "ssh"))]
        and NONCE not in log.read_text(), f"rc {rc}: {out[-200:]!r} log {log.read_text()[:100]!r}")


def w_stamp(td, rel):
    """Run to its refusal only; the null reads the same rule's own function, since past it the stamp would run for real."""
    td.mkdir(parents=True)
    stubs, log = stub_bin(td, ("gh", "curl", "ssh"))
    env = launcher_env(td, stubs)
    missing = td / "no-such-key"
    rc, out = run([sys.executable, str(ROOT / rel), "--bump", "patch", "--title", "x", "--push", "--push-key", str(missing)], cwd=ROOT, env=env)
    arm(f"P5b: {rel} refuses a deploy key it cannot read, before any git or ssh call",
        rc == 2 and "rule push-key" in out and "nothing was written" in out and log.read_text() == "", f"rc {rc}: {out[-200:]!r}")
    stamp = load(rel)
    key, hosts = td / "key", td / "hosts"
    key.write_text("k")
    hosts.write_text("h")
    key.chmod(0o600)
    hosts.chmod(0o600)
    arm(f"P5b null: {rel}'s push-key rule passes a throwaway mode-600 key (the refusal is the absent key's)",
        stamp.push_key_problem(str(key), str(hosts)) is None and stamp.push_key_problem(str(missing), str(hosts)) is not None)


WRITER_ARMS: dict = {"tools/pr/app_push.sh": w_app_push, "tools/pr/app_comment.sh": w_app_comment, "tools/pr/app_approve.sh": w_app_approve,
                     "tools/audit/seat/body_patch.sh": w_body_patch, "tools/audit/seat/remerge_main.sh": w_remerge,
                     "tools/audit/seat/bus.sh": w_bus, "tools/release/stamp.py": w_stamp}


def main(argv: list[str]) -> int:
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    arms = {"P1-P3": lambda td: p1_p3(), "P4": p4, "P5": p5, "P5b": p5b, "P7": p7, "P10": lambda td: p10(),
            "SCOPES": lambda td: scopes_shape(), "SET": one_set}
    with tempfile.TemporaryDirectory() as td:
        for name, fn in arms.items():
            if only is None or name in only:
                d = Path(td) / name
                d.mkdir()
                try:
                    fn(d)
                except Exception as e:  # noqa: BLE001 -- an arm that crashes is a failed arm, never a skipped one
                    arm(f"{name}: the arm ran to its end", False, f"{type(e).__name__}: {e}")
    bad = [n for n, ok, _ in RESULTS if not ok]
    print(f"RESULT arms={len(RESULTS)} failed={len(bad)}")
    print("OWNER-ONLY CHANNEL HELD" if not bad else "OWNER-ONLY CHANNEL BROKEN: " + "; ".join(bad))
    return 1 if bad or not RESULTS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
