#!/usr/bin/env python3
"""D6-s3 links: HEAD every link a D6 text unit of the seat's cells names.

Metric (one line): per distinct link found in the text_ledger.py D6 units of
translations/en.json and custom_components/heatpump_optimizer/*.py (a URL, or
a bare host the text tells the reader to visit), the HTTP status of a HEAD
request (GET when HEAD is refused), following redirects.

Writes links.json beside itself (ledger.py's link rows).
Run (from the export root; needs outbound HTTPS):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s3/links.py
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B3): RESULT links=1,
RESULT links_dead=0; the status itself is external and can change.
Instrumented symbol: the units text_ledger.py:units_of yields for the cells
(config_flow.py's token help string and en.json's invalid_tibber_token error).
"""
import json
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "tools/audit"))
import text_ledger as TL  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
FILES = [PKG + "translations/en.json"] + sorted(
    PKG + p.name for p in (ROOT / PKG).glob("*.py") if not p.name.startswith("._"))
LINK = re.compile(r"https?://[^\s\"'<>)]+|\b(?:[a-z0-9-]+\.)+(?:com|org|net|io|se|de)\b", re.I)


def status(url):
    ctx = ssl.create_default_context()
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": "link-check"})
        try:
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return e.code
        except Exception as e:  # a link that cannot be reached is reported, not hidden
            return f"error:{type(e).__name__}"
    return "error"


def main():
    links = {}
    for uid, _line, _kind, text in TL.enumerate_units(ROOT, FILES, "D6"):
        for m in LINK.findall(text):
            url = m.rstrip(".,;") if m.startswith("http") else "https://" + m.rstrip(".,;")
            links.setdefault(url, []).append(uid)
    dead, rows = 0, {}
    for url, uids in sorted(links.items()):
        st = status(url)
        ok = isinstance(st, int) and st < 400
        dead += not ok
        print(f"LINK {st} {url} <- {', '.join(uids)}")
        for u in uids:
            rows[u] = {"url": url, "status": st, "verdict": "true" if ok else "false"}
    # ledger.py rows these units as link claims from this file.
    (pathlib.Path(__file__).resolve().parent / "links.json").write_text(json.dumps(rows, indent=1))
    print(f"RESULT links={len(links)} count")
    print(f"RESULT links_dead={dead} count")


if __name__ == "__main__":
    main()
