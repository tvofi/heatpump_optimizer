#!/usr/bin/env python3
"""Candidate detectors for data already published: where a span is, by class, for an owner-only seat to judge.

    python3 -I leak_detectors.py scan --out FILE <file>...      (FILE under $HPO_PRIVATE_ROOT)
    python3 -I leak_detectors.py locate --file F --offset N --length L [--masked]
    python3 -I leak_detectors.py --self-test [--no-mutants]

The detective pass over what is already published; tools/audit/seat/ref_privacy.py
stays the preventive owner of what an outgoing push may say, and its host
classes are IMPORTED here, never copied. A detector returns CANDIDATES: a
class and a span. Whether a candidate is a leak is the seat's finding, with
its own harness; a detector that is quiet proves nothing about a unit.

The classes:
  host-path, scratch-root   ref_privacy's own, judged against no host (any
                            machine's home or session temp root);
  token                     a GitHub token, a PEM private key header, a JSON
                            web token (Home Assistant's long-lived tokens are
                            one), a cloud access key id, a Slack token;
  email                     an address outside GitHub's noreply grammar and
                            the reserved example domains;
  coordinates               a latitude and longitude pair with four or more
                            decimals, or a `latitude`/`longitude` key with a
                            numeric value;
  address                   a private-range or link-local IPv4 address, or a
                            MAC address;
  person-entity             a `person.`, `device_tracker.` or `zone.` entity
                            id other than the documented placeholders.
NOT DETECTED, each a cell a seat reads by hand: a name, a street address or a
phone number in prose; an entity id of any other domain (the tree's own
examples use them throughout); a value split across lines, encoded, or inside
a compressed blob; an opinion (a reading, never a pattern).

`scan` writes one JSON row per candidate -- file, class, offset, length -- to
--out, and refuses an --out outside $HPO_PRIVATE_ROOT: its output names where
published data sits, so it stays where the findings stay. It prints only that
it wrote. `locate` is the location harness an M3 or M4 finding cites: it
prints the span at an offset, and with --masked (the span replaced before the
read) prints nothing, so the harness moves under its own perturbation.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "seat"))
import ref_privacy  # noqa: E402 -- the host-path grammar has one owner

#: Judged against no host: only the classes that need no identity can fire.
NO_HOST = ref_privacy.Identity.made((), (), None)
HOST_CLASSES = {"host-path": ref_privacy._HOST_PATH, "scratch-root": ref_privacy._SCRATCH_ROOT}  # noqa: SLF001

_B64 = r"[A-Za-z0-9_-]"
TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}"
    r"|eyJ" + _B64 + r"{8,}\.eyJ" + _B64 + r"{8,}\." + _B64 + r"{8,}"
    r"|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})"
    r"|-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")
EMAIL = re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)(?![A-Za-z0-9-])")
PUBLIC_EMAIL_DOMAINS = re.compile(r"(?:users\.noreply\.)?github\.com|(?:.+\.)?example\.(?:com|org|net)|.+\.(?:invalid|test|example)", re.I)
COORDINATES = re.compile(
    r"(?<![0-9.])-?[0-9]{1,2}\.[0-9]{4,}\s*,\s*-?[0-9]{1,3}\.[0-9]{4,}(?![0-9])"
    r"|\b(?:lat(?:itude)?|lon(?:gitude)?|lng)[\"']?\s*[:=]\s*[\"']?-?[0-9]{1,3}\.[0-9]{3,}", re.I)
_OCTET = r"(?:25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])"
ADDRESS = re.compile(
    r"(?<![0-9.])(?:10\." + _OCTET + r"|192\.168|172\.(?:1[6-9]|2[0-9]|3[01])|169\.254)\." + _OCTET + r"\." + _OCTET + r"(?![0-9.])"
    r"|(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f:])")
PERSON_ENTITY = re.compile(r"(?<![A-Za-z0-9_.])(?:person|device_tracker|zone)\.([a-z0-9_]+)(?![A-Za-z0-9_])")
PLACEHOLDER_ENTITIES = frozenset({"home", "example", "me", "user", "name", "your_name", "phone", "my_phone", "xxx"})

CLASSES = ("host-path", "scratch-root", "token", "email", "coordinates", "address", "person-entity")


def scan(text: str) -> list[tuple[str, int, int]]:
    """Every candidate span of `text` as (class, start, end), in order of start."""
    out = [(cls, m.start(), m.end()) for cls, rx in HOST_CLASSES.items() for m in rx.finditer(text)]
    out += [("token", m.start(), m.end()) for m in TOKEN.finditer(text)]
    out += [("email", m.start(), m.end()) for m in EMAIL.finditer(text) if not PUBLIC_EMAIL_DOMAINS.fullmatch(m.group(1))]
    out += [("coordinates", m.start(), m.end()) for m in COORDINATES.finditer(text)]
    out += [("address", m.start(), m.end()) for m in ADDRESS.finditer(text)]
    out += [("person-entity", m.start(), m.end()) for m in PERSON_ENTITY.finditer(text) if m.group(1) not in PLACEHOLDER_ENTITIES]
    return sorted(out, key=lambda c: (c[1], c[2], c[0]))


def mask(text: str, start: int, end: int) -> str:
    """`text` with the span replaced by as many `x`: the perturbation a location harness runs."""
    return text[:start] + "x" * (end - start) + text[end:]


def locate(text: str, offset: int, length: int, masked: bool = False) -> str:
    """The span at an offset; "" when it is out of range, or masked."""
    if offset < 0 or length <= 0 or offset + length > len(text):
        return ""
    return "" if masked else text[offset:offset + length]


def private(path: str, root: str | None) -> bool:
    """Whether `path` is under the private root: the only place a scan may write."""
    if not root or not os.path.isabs(root):
        return False
    real, base = os.path.realpath(path), os.path.realpath(root)
    return real.startswith(base + os.sep)


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test(Path(__file__), mutants="--no-mutants" not in argv)
    if argv[:1] == ["scan"] and argv[1:2] == ["--out"] and len(argv) >= 4:
        out = argv[2]
        if not private(out, os.environ.get("HPO_PRIVATE_ROOT")):
            print("leak_detectors: REFUSED --out is not under $HPO_PRIVATE_ROOT: a scan's rows stay where the findings stay")
            return 2
        rows = [{"file": f, "class": c, "offset": s, "length": e - s} for f in argv[3:] for c, s, e in scan(read(f))]
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(rows, fh, indent=1)
        print("leak_detectors: wrote the candidates under the private root")
        return 0
    if argv[:1] == ["locate"]:
        try:
            a = dict(zip(argv[1::2], argv[2::2])) if "--masked" not in argv else dict(zip([x for x in argv[1:] if x != "--masked"][0::2],
                                                                                           [x for x in argv[1:] if x != "--masked"][1::2]))
            offset, length, text = int(a["--offset"]), int(a["--length"]), read(a["--file"])
        except (KeyError, ValueError, OSError):
            print(__doc__.split("\n\n")[0], file=sys.stderr)
            return 2
        span = locate(mask(text, offset, offset + length) if "--masked" in argv else text, offset, length, "--masked" in argv)
        if span:
            print(span)
        return 0 if span else 1
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


SELF_TEST_MARK = "# ---" + "--- self-test: mutants edit only the code above this line"
# ------ self-test: mutants edit only the code above this line


def cases(m) -> dict[str, bool]:
    import contextlib
    import io
    import secrets
    import tempfile
    r: dict[str, bool] = {}
    rnd = secrets.token_hex(20)
    # Every planted value is built here, never spelled: a spelled one is what the tree's own checks, and this file, refuse.
    twins = {
        "host-path": "/" + "/".join(("Users", "someone", "proj")),
        "scratch-root": "tmp" + "/claude-" + "501",
        "token": "gh" + "p_" + rnd[:36],
        "email": "first.last" + "@" + "mailhost.org",
        "coordinates": "59." + "3293" + ", " + "18." + "0686",
        "address": "192." + "168.1.20",
        "person-entity": "person" + "." + "alex_smith",
    }
    more = {
        "token": ["github_" + "pat_" + rnd + rnd[:10], "eyJ" + rnd[:12] + ".eyJ" + rnd[:12] + "." + rnd[:12],
                  "AKIA" + "ABCDEFGHIJKLMNOP", "xox" + "b-" + rnd[:14], "-----BEGIN " + "RSA PRIVATE KEY-----", "-----BEGIN " + "PRIVATE KEY-----"],
        "coordinates": ['"latitude"' + ": 59.329", "lon" + "=18.068"],
        "address": ["10." + "0.0.5", "172." + "16.4.1", "169." + "254.1.1", "aa:bb:" + "cc:dd:ee:ff"],
        "person-entity": ["device_tracker" + "." + "alex_phone", "zone" + "." + "summer_house"],
    }
    def first(v):
        """The one candidate of a planted value, or a span that matches nothing."""
        got = m.scan(f"see {v} here")
        return got[0] if len(got) == 1 else ("", -1, -1)
    r["scan: a planted twin of every class fires as exactly that class, starting at its own offset"] = all(
        first(v)[:2] == (c, 4) and 4 < first(v)[2] <= 4 + len(v) for c, v in twins.items()) and sorted(twins) == sorted(m.CLASSES)
    r["scan: the other spellings of a class fire too"] = all(
        [x[0] for x in m.scan(f"a {v} b")] == [c] for c, vs in more.items() for v in vs)
    r["mask: with the detector's own span masked it is quiet (the perturbation of a leaked-data finding)"] = all(
        first(v)[1] == 4 and m.scan(m.mask(f"see {v} here", *first(v)[1:])) == [] for v in twins.values())
    quiet = ["a12345@" + "users.noreply.github.com", "noreply@" + "github.com", "x@" + "example.com", "dev@" + "sub.example.org", "a@" + "host.invalid",
             "version 1.2.3.4", "8.8." + "8.8", "10.1", "192.168.1", "1.5, 2.5", "59.33, 18.07", "sensor.outdoor_temperature",
             "person" + ".home", "zone" + ".home", "device_tracker" + ".example", "gh" + "p_short", "eyJ.eyJ.x", "/usr/local/bin",
             "/home/" + "user/heatpump_optimizer", "12:34:56", "BEGIN PUBLIC KEY", "latitude: number", "at 10.0.0", "0a:1b:2c"]
    r["scan null: noreply and example addresses, public or partial numbers, placeholder entities and the cloud image's root are quiet"] = \
        [q for q in quiet if m.scan(f"a {q} b")] == []
    r["scan: the host-path grammar is ref_privacy's own object, not a copy"] = \
        m.HOST_CLASSES["host-path"] is m.ref_privacy._HOST_PATH and m.HOST_CLASSES["scratch-root"] is m.ref_privacy._SCRATCH_ROOT  # noqa: SLF001
    text = "before " + twins["email"] + " after"
    (cls, s, e), = m.scan(text)
    r["locate: the span at an offset is printed, and masked it is not (a location harness moves)"] = \
        m.locate(text, s, e - s) == twins["email"] and m.locate(text, s, e - s, masked=True) == "" \
        and m.locate(text, len(text), 5) == "" and m.locate(text, -1, 5) == "" and m.locate(text, 0, 0) == "" \
        and m.locate(text, len(text) - 2, 5) == ""
    with tempfile.TemporaryDirectory() as td:
        root, src = Path(td) / "private", Path(td) / "unit.txt"
        root.mkdir()
        src.write_text(text)
        old = os.environ.get("HPO_PRIVATE_ROOT")

        def cli(argv, env_root):
            buf = io.StringIO()
            os.environ.pop("HPO_PRIVATE_ROOT", None)
            if env_root is not None:
                os.environ["HPO_PRIVATE_ROOT"] = env_root
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    rc = m.main(argv)
            finally:
                os.environ.pop("HPO_PRIVATE_ROOT", None)
                if old is not None:
                    os.environ["HPO_PRIVATE_ROOT"] = old
            return rc, buf.getvalue()

        rc, out = cli(["scan", "--out", str(root / "c.json"), str(src)], str(root))
        rows = json.loads((root / "c.json").read_text()) if (root / "c.json").exists() else None
        r["cli scan: the rows go under the private root, owner-only, and the output names no file, class or value"] = \
            rc == 0 and rows == [{"file": str(src), "class": "email", "offset": s, "length": e - s}] \
            and (os.stat(root / "c.json").st_mode & 0o777) == 0o600 and twins["email"] not in out and "email" not in out and str(src) not in out
        refused = [cli(["scan", "--out", o, str(src)], er) for o, er in (
            (str(Path(td) / "outside.json"), str(root)), (str(root / "x.json"), None), (str(root / "x.json"), "relative"),
            (str(root / ".." / "escape.json"), str(root)))]
        r["cli scan: an --out outside the private root, or with no root set, is refused and nothing is written"] = \
            all(rc_ == 2 and "REFUSED" in o_ for rc_, o_ in refused) and not (Path(td) / "outside.json").exists() \
            and not (root / "x.json").exists() and not (Path(td) / "escape.json").exists()
        rc1, out1 = cli(["locate", "--file", str(src), "--offset", str(s), "--length", str(e - s)], None)
        rc2, out2 = cli(["locate", "--file", str(src), "--offset", str(s), "--length", str(e - s), "--masked"], None)
        r["cli locate: prints the span and exits 0; masked, prints nothing and exits 1"] = \
            (rc1, out1) == (0, twins["email"] + "\n") and (rc2, out2) == (1, "")
    return r


#: (needle, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "host classes": ('out = [(cls, m.start(), m.end()) for cls, rx in HOST_CLASSES.items() for m in rx.finditer(text)]', "out = []", "planted twin of every class"),
    "token": ('out += [("token", m.start(), m.end()) for m in TOKEN.finditer(text)]', "pass", "planted twin of every class"),
    "pem": (r'    r"|-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")', r'    r"|-----BEGIN RSA PRIVATE KEY-----")', "other spellings"),
    "public email": ("if not PUBLIC_EMAIL_DOMAINS.fullmatch(m.group(1))]", "]", "noreply and example addresses"),
    "coordinates": ('out += [("coordinates", m.start(), m.end()) for m in COORDINATES.finditer(text)]', "pass", "planted twin of every class"),
    "four decimals": (r'r"(?<![0-9.])-?[0-9]{1,2}\.[0-9]{4,}\s*,\s*-?[0-9]{1,3}\.[0-9]{4,}(?![0-9])"', r'r"(?<![0-9.])-?[0-9]{1,2}\.[0-9]+\s*,\s*-?[0-9]{1,3}\.[0-9]+(?![0-9])"', "public or partial numbers"),
    "private ranges": (r'(?:10\." + _OCTET + r"|192\.168|172\.(?:1[6-9]|2[0-9]|3[01])|169\.254)', r'(?:" + _OCTET + r"\." + _OCTET + r")', "public or partial numbers"),
    "mac": (r'    r"|(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f:])")', '    r"|(?!x)x")', "other spellings"),
    "placeholders": ("if m.group(1) not in PLACEHOLDER_ENTITIES]", "]", "placeholder entities"),
    "mask": ('return text[:start] + "x" * (end - start) + text[end:]', "return text", "own span masked"),
    "locate masked": ('    return "" if masked else text[offset:offset + length]', "    return text[offset:offset + length]", "masked it is not"),
    "locate range": ("    if offset < 0 or length <= 0 or offset + length > len(text):\n", "    if False:\n", "masked it is not"),
    "out is private": ('        if not private(out, os.environ.get("HPO_PRIVATE_ROOT")):\n', "        if False:\n", "outside the private root"),
    "real path": ("    real, base = os.path.realpath(path), os.path.realpath(root)\n", "    real, base = path, root\n", "outside the private root"),
    "mode": ("os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)", "os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)", "owner-only"),
}


def self_test(path: Path, mutants: bool = True) -> int:
    import importlib.util
    import shutil
    import subprocess
    import tempfile
    bad = []
    spec = importlib.util.spec_from_file_location("leak_detectors_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name, ok in cases(mod).items():
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            bad.append(name)
    if mutants:
        code, sep, tail = path.read_text().partition(SELF_TEST_MARK)
        for name, (old, new, case) in MUTANTS.items():
            if code.count(old) != 1:
                print(f"FAIL mutant {name}: needle found {code.count(old)} times in the code")
                bad.append("mutant " + name)
                continue
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / "seat").mkdir()
                shutil.copy(path.parent / "seat" / "ref_privacy.py", Path(td) / "seat" / "ref_privacy.py")
                mp = Path(td) / path.name
                mp.write_text(code.replace(old, new) + sep + tail)
                p = subprocess.run([sys.executable, "-I", str(mp), "--self-test", "--no-mutants"], capture_output=True, text=True, timeout=120)
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("leak_detectors self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
