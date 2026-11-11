"""R10-HOTFIX-CARD-HEALTH-TEXT: which of the card's class and id names a
content blocker's generic element-hiding rules target, per filter list.

    python3 -I dev/audit/harnesses/r10_card_blocker_names.py [<git ref>]

Fetches the lists at run time (nothing is vendored: EasyList is GPLv3 /
CC BY-SA), keeps each generic `##<selector>` rule (no domain), and reports
every card name a rule targets by a plain `.name` / `#name` token or a
`[class|id <op>= "v"]` attribute test (=, ~=, ^=, $=, *=, |=). The card's
names are read as tests/card.mjs's barrier reads them: class and id
attribute values (a templated value up to its first `${`), className
assignments and classList arguments -- the names that reach its DOM, not
the stylesheet's selectors. A rule's plain tokens are read outside its
brackets and parentheses; a compound rule with further conditions is
reported whole, for the reader to judge. Exit 0 always; the lane barrier is tests/card.mjs, not this. The
null control is the base ref: at v7.1.11 it reads `adv-text` and
`adv-label` from EasyList and AdGuard Base.
"""

import re
import subprocess
import sys
import urllib.request

CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
LISTS = {
    "EasyList general hide": "https://raw.githubusercontent.com/easylist/easylist/master/easylist/easylist_general_hide.txt",
    "AdGuard Base (chromium)": "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/platforms/extension/chromium/filters/2.txt",
    "AdGuard Base (uBlock flavour)": "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/platforms/extension/ublock/filters/2.txt",
    "uBlock filters": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt",
}
ATTR = re.compile(r"""\[\s*(class|id)\s*([~^$*|]?)=\s*["']?([^"'\]\s]+)["']?\s*(?:i\s*)?\]""")


def card_names(src):
    """(kind, name) for every class and id the card writes into its DOM."""
    names = set()

    def add(kind, value):
        for tok in value.split():
            lit = tok.split("${")[0]
            if lit:
                names.add((kind, lit))

    for m in re.finditer(r"""\b(class|id)\s*=\s*(["'])(.*?)\2""", src, re.S):
        add(m.group(1), m.group(3))
    for m in re.finditer(r"""\bclassName\s*=\s*(["'`])(.*?)\1""", src, re.S):
        add("class", m.group(2))
    for m in re.finditer(r"\bclassList\.(?:add|remove|toggle|contains|replace)\(([^)]*)\)", src):
        for q in re.finditer(r"""(["'`])([^"'`]*)\1""", m.group(1)):
            add("class", q.group(2))
    return names


def index(rules):
    """Plain `.name` / `#name` tokens, and the class / id attribute tests."""
    plain, attrs = {}, []
    for r in rules:
        bare = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", r)
        for sig, tok in re.findall(r"([.#])(-?[A-Za-z_][\w-]*)", bare):
            plain.setdefault(("class" if sig == "." else "id", tok), []).append(r)
        attrs.extend((kind, op, v, r) for kind, op, v in ATTR.findall(r))
    return plain, attrs


def targeted(kind, name, plain, attrs):
    hit = list(plain.get((kind, name), []))
    for k, op, v, r in attrs:
        if k != kind:
            continue
        if (op in ("", "~") and name == v) or (op == "^" and name.startswith(v)) or \
           (op == "$" and name.endswith(v)) or (op == "*" and v in name) or \
           (op == "|" and (name == v or name.startswith(v + "-"))):
            hit.append(r)
    return hit


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    src = subprocess.run(["git", "show", f"{ref}:{CARD}"], check=True,
                         capture_output=True, text=True).stdout
    names = sorted(card_names(src))
    print(f"card at {ref}: {len(names)} names")
    for label, url in LISTS.items():
        text = urllib.request.urlopen(url, timeout=120).read().decode("utf-8", "replace")
        stamp = next((ln for ln in text.splitlines()[:40]
                      if re.match(r"! (TimeUpdated|Last modified|Version):", ln)), "! (no stamp)")
        rules = [ln[2:] for ln in text.splitlines() if ln.startswith("##")]
        plain, attrs = index(rules)
        hits = {f"{k} {n}": h for k, n in names if (h := targeted(k, n, plain, attrs))}
        print(f"{label}: {len(rules)} generic rules; {stamp[2:]}; {url}")
        for n, r in sorted(hits.items()):
            print(f"  {n}: {', '.join(r[:4])}{' ...' if len(r) > 4 else ''}")
        alone = sorted(k for k, h in hits.items()
                       if any(r.strip() == ("." if k.startswith("class") else "#") + k.split(" ", 1)[1] for r in h))
        print(f"  targeted by a rule naming it alone ({len(alone)}): {', '.join(alone) or 'none'}")


if __name__ == "__main__":
    main()
