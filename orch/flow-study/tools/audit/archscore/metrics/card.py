"""card: the Lovelace card's dead definitions and copied code (R10-ARCHSCORE-COVERAGE item 2; ARCH2-s5 and
D7-s3-02, round 10).

The card (``www/*.js``) is the package's largest surface and every other metric reads Python only, so a
card change read delta-S 0 whatever it did. Stdlib only: a JavaScript TOKENIZER here, never a parser, so
each rule is stated on tokens.

Tokens. Comments are dropped. A string is one ``S`` token; a template literal is ``S`` tokens for its
text and the tokens of each ``${..}`` expression, recursively; a number is its value; a regular
expression literal is one ``R`` token; identifiers and punctuators are themselves. ``/`` starts a
regular expression where an operand is expected.

  card_dead_definitions   top-level ``function``/``class`` declarations, top-level ``const``/``let``
                    bindings, and class members (``name(..) {``, getters and setters), whose name
                    appears as no other identifier token anywhere in the card files, a ``.name``
                    access included, less ``HOOKS``: the names the browser, lit or Home Assistant
                    calls by convention. D7-s3-02's ``textWidth`` was one.
  card_clone_copies       functions sharing a window of WINDOW consecutive tokens, after a function's
                    own identifiers (its parameters and ``const``/``let``/``var`` names) are numbered
                    by first use and its no-op statements dropped (counter C22) and strings read ``S``: the copies (members of a clone class), as
                    ``duplication_copies`` counts Python's. A window crosses statement boundaries,
                    so a rule spelled inline in several functions (the live-state guard, the
                    finite-number test) joins its spellers.
"""
from __future__ import annotations

import re
import time
from collections import defaultdict
from pathlib import Path

from . import common as C

#: Tokens per window. 20, calibrated on ARCH2-s5's four card patches (round 10): at 16 the finite-number
#: owner (C4), a dedupe, read one copy more; at 20 no patch rises and their union reads 108 -> 101.
WINDOW = 20
#: Counter C22: a function's own names are numbered and its no-op statements dropped, so renaming its names or
#: interleaving ``void 1;`` hides no copy. ``vector.py`` switches it off.
OWN_NAMES = True
#: Tokens a statement with no effect may hold: literals, identifiers read, and pure operators. A call (an
#: identifier or ``)`` followed by ``(``), an assignment, a member access, ``new``/``await``/``delete`` or a
#: keyword at its head gives it an effect, and it is kept.
_PURE_OPS = frozenset("void typeof + - * / % ! ~ , ( ) && || ?? == === != !== < > <= >= & | ^ << >> >>> ** ? :".split())
_HEADS = frozenset("if for while do switch try catch finally return throw break continue case default else const "
                   "let var function class import export yield await new delete with debugger".split())
#: Members the browser (custom elements), lit or Home Assistant's frontend call by name.
HOOKS = frozenset({
    "constructor", "connectedCallback", "disconnectedCallback", "attributeChangedCallback",
    "adoptedCallback", "observedAttributes", "render", "updated", "firstUpdated", "shouldUpdate",
    "willUpdate", "properties", "styles", "setConfig", "getCardSize", "getStubConfig",
    "getConfigElement", "getLayoutOptions", "getGridOptions", "hass", "config",
})
_IDENT = re.compile(r"[A-Za-z_$][\w$]*")
_NUM = re.compile(r"(?:0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|(?:\d[\d_]*\.?[\d_]*|\.\d[\d_]*)(?:[eE][+-]?\d+)?)n?")
_PUNCT = sorted(""">>>= ... === !== **= <<= >>= >>> &&= ||= ??= => == != <= >= && || ?? ?. ++ -- += -= *= /= %=
&= |= ^= ** << >> { } ( ) [ ] ; , < > + - * / % & | ^ ! ~ ? : = . @ #""".split(), key=len, reverse=True)
#: After these, ``/`` begins a regular expression rather than a division.
_OPERAND_EXPECTED = set("( , = : [ ! & | ? { } ; + - * % < > ~ ^".split()) | {
    "=>", "==", "===", "!=", "!==", "&&", "||", "??", "return", "typeof", "case", "do", "else", "in",
    "of", "new", "delete", "void", "throw", "yield", "await", "<=", ">=", "+=", "-=", "*=", "/=", "%=",
    "**", "**=", "...",
}


def tokenize(src: str) -> list[str]:
    """``src`` as tokens (the module docstring's rules)."""
    out: list[str] = []
    i, n = 0, len(src)

    def template(i: int) -> int:
        """Tokens of a template literal starting after its opening backtick; returns the index after it."""
        out.append("S")
        while i < n:
            ch = src[i]
            if ch == "\\":
                i += 2
            elif ch == "`":
                return i + 1
            elif ch == "$" and src.startswith("${", i):
                depth, j = 1, i + 2
                inner_start = j
                while j < n and depth:  # the expression's extent: braces, comments and nested literals respected
                    c = src[j]
                    if src.startswith("/*", j):
                        k = src.find("*/", j + 2)
                        j = n if k < 0 else k + 2
                        continue
                    if src.startswith("//", j):
                        k = src.find("\n", j)
                        j = n if k < 0 else k
                        continue
                    if c in "\"'":
                        j = _skip_string(src, j)
                        continue
                    if c == "`":
                        j = _skip_template(src, j + 1)
                        continue
                    depth += c == "{"
                    depth -= c == "}"
                    j += 1
                out.extend(tokenize(src[inner_start:j - 1]))
                out.append("S")
                i = j
            else:
                i += 1
        return i

    while i < n:
        ch = src[i]
        if ch.isspace():
            i += 1
        elif src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif ch in "\"'":
            i = _skip_string(src, i)
            out.append("S")
        elif ch == "`":
            i = template(i + 1)
        elif ch == "/" and (not out or out[-1] in _OPERAND_EXPECTED):
            j, in_class = i + 1, False
            while j < n and src[j] != "\n":
                c = src[j]
                if c == "\\":
                    j += 2
                    continue
                if c == "[":
                    in_class = True
                elif c == "]":
                    in_class = False
                elif c == "/" and not in_class:
                    break
                j += 1
            j += 1
            while j < n and (src[j].isalnum()):
                j += 1
            out.append("R")
            i = j
        elif (m := _IDENT.match(src, i)) is not None:
            out.append(m.group())
            i = m.end()
        elif (ch.isdigit() or (ch == "." and i + 1 < n and src[i + 1].isdigit())) \
                and (m := _NUM.match(src, i)) is not None and m.end() > i:
            out.append(m.group())
            i = m.end()
        else:
            for p in _PUNCT:
                if src.startswith(p, i):
                    out.append(p)
                    i += len(p)
                    break
            else:
                out.append(ch)
                i += 1
    return out


def _skip_string(src: str, i: int) -> int:
    q, j = src[i], i + 1
    while j < len(src) and src[j] != q:
        j += 2 if src[j] == "\\" else 1
    return j + 1


def _skip_template(src: str, i: int) -> int:
    j = i
    while j < len(src) and src[j] != "`":
        if src[j] == "\\":
            j += 2
            continue
        if src.startswith("${", j):
            depth, j = 1, j + 2
            while j < len(src) and depth:
                depth += src[j] == "{"
                depth -= src[j] == "}"
                j += 1
            continue
        j += 1
    return j + 1


def _matching(toks: list[str], i: int) -> int:
    """Index of the bracket closing the one at ``i``."""
    pair = {"{": "}", "(": ")", "[": "]"}[toks[i]]
    depth = 0
    for j in range(i, len(toks)):
        if toks[j] == toks[i]:
            depth += 1
        elif toks[j] == pair:
            depth -= 1
            if depth == 0:
                return j
    return len(toks) - 1


def functions(toks: list[str]) -> list[tuple[str, int, int, int]]:
    """``(name, params start, body start, body end)`` for each function: ``function f(..) {``, a class
    member ``name(..) {`` (``get``/``set``/``static``/``async`` before it), and an arrow ``(..) => {``
    bound to a name. Nested functions are their own entries."""
    out = []
    for i, t in enumerate(toks):
        if t != "(" or i == 0:
            continue
        close = _matching(toks, i)
        after = close + 1
        if after < len(toks) and toks[after] == "=>":
            after += 1
        if after >= len(toks) or toks[after] != "{":
            continue
        name = toks[i - 1]
        if name == "function" or not _IDENT.fullmatch(name) or name in (
                "if", "for", "while", "switch", "catch", "with", "return", "typeof"):
            if toks[after - 1] != "=>":
                continue
            name = toks[i - 3] if i >= 3 and toks[i - 2] == "=" else "<arrow>"
        out.append((name, i, after, _matching(toks, after)))
    return out


def definitions(toks: list[str]) -> list[str]:
    """Names the card defines at top level or as class members."""
    names, depth, cls_depth = [], 0, []
    for i, t in enumerate(toks):
        if t == "{":
            if i >= 2 and (toks[i - 2] == "class" or (i >= 4 and toks[i - 4] == "class" and toks[i - 2] == "extends")):
                cls_depth.append(depth + 1)
            depth += 1
            continue
        if t == "}":
            if cls_depth and cls_depth[-1] == depth:
                cls_depth.pop()
            depth -= 1
            continue
        nxt = toks[i + 1] if i + 1 < len(toks) else ""
        if depth == 0 and t in ("function", "class") and _IDENT.fullmatch(nxt):
            names.append(nxt)
        elif depth == 0 and t in ("const", "let", "var") and _IDENT.fullmatch(nxt):
            names.append(nxt)
        elif cls_depth and depth == cls_depth[-1] and _IDENT.fullmatch(t) and nxt == "(" \
                and toks[i - 1] in (";", "}", "{", "static", "get", "set", "async", "*"):
            if toks[_matching(toks, i + 1) + 1:_matching(toks, i + 1) + 2] == ["{"]:
                names.append(t)
    return names


def dead_definitions(toks: list[str]) -> list[str]:
    seen: dict[str, int] = defaultdict(int)
    for t in toks:
        seen[t] += 1
    return sorted({d for d in definitions(toks) if d not in HOOKS and seen[d] <= 1})


def drop_noops(body: list[str]) -> list[str]:
    """``body`` without its no-op statements: a run that starts a statement (after ``;``, ``{`` or ``}``, outside
    any parenthesis, so a ``for (..;..;..)`` header is kept), ends at ``;``, and holds only ``_PURE_OPS``,
    literals and identifiers with no call -- ``void 1;``, ``"x";``, ``a + 1;`` -- or nothing at all, the
    empty statement ``;`` after a ``;`` or a ``{``. A ``;`` after ``}`` is kept: tokens cannot tell a block's
    ``}`` (where it is an empty statement) from an object literal's or a function expression's (``x = {};``,
    where it ends the statement). A ``;`` that is a statement's body (``if (x) ;``, ``else ;``) does not start
    one and is kept."""
    out, i, depth, n = [], 0, 0, len(body)
    while i < n:
        t = body[i]
        if depth == 0 and (not out or out[-1] in (";", "{", "}")) and t not in _HEADS:
            j = i
            while j < n and body[j] != ";" and body[j] not in ("{", "}"):
                j += 1
            run = body[i:j]
            if j < n and body[j] == ";" and (run or out[-1:] != ["}"]) and all(
                    (x in _PURE_OPS or x in ("S", "R") or _NUM.fullmatch(x) or _IDENT.fullmatch(x))
                    and x not in _HEADS for x in run) \
                    and not any(run[k + 1] == "(" and (_IDENT.fullmatch(run[k]) or run[k] == ")")
                                and run[k] not in _PURE_OPS for k in range(len(run) - 1)):
                i = j + 1
                continue
        depth += t == "("
        depth -= t == ")"
        out.append(t)
        i += 1
    return out


def _own_tokens(toks: list[str], fn: tuple[str, int, int, int], nested: list[tuple[int, int]]) -> list[str]:
    """A function's tokens from its parameters to its closing brace, each nested function's span one ``F``
    token (it is its own entry), and the function's own names numbered by first use."""
    _name, start, _b0, end = fn
    body, j = [], start
    for a, b in sorted(nested):
        if a > j:
            body += toks[j:a]
        if b >= j:
            body.append("F")
            j = b + 1
    body += toks[j:end + 1]
    if OWN_NAMES:
        body = drop_noops(body)
    own: set[str] = set()
    params_end = _matching(toks, start) - start if OWN_NAMES else -1
    for k, t in enumerate(body):
        if k <= params_end and _IDENT.fullmatch(t) and (k == 0 or body[k - 1] != "."):
            own.add(t)
        elif OWN_NAMES and t in ("const", "let", "var") and k + 1 < len(body) and _IDENT.fullmatch(body[k + 1]):
            own.add(body[k + 1])
    out, num = [], {}
    for k, t in enumerate(body):
        if t in own and (k == 0 or body[k - 1] != "."):
            out.append(f"v{num.setdefault(t, len(num))}")
        else:
            out.append(t)
    return out


def clone_copies(toks: list[str], window: int = WINDOW) -> list[list[str]]:
    """Clone classes of functions sharing a normalized window of ``window`` tokens of their own."""
    fns = functions(toks)
    windows: dict[tuple, set] = defaultdict(set)
    for k, fn in enumerate(fns):
        _n, start, _b0, end = fn
        nested = [(s0, e0) for (_m, s0, _c, e0) in fns if start < s0 and e0 <= end and (s0, e0) != (start, end)]
        outer = [(a, b) for a, b in nested if not any(a2 < a and b <= b2 for a2, b2 in nested if (a2, b2) != (a, b))]
        norm = _own_tokens(toks, fn, outer)
        for j in range(len(norm) - window + 1):
            windows[tuple(norm[j:j + window])].add(f"{fn[0]}@{k}")
    parent: dict = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for owners in windows.values():
        if len(owners) > 1:
            first, *rest = sorted(owners)
            for o in rest:
                parent[find(o)] = find(first)
    groups: dict = defaultdict(list)
    for m in parent:
        groups[find(m)].append(m)
    return sorted(sorted(g) for g in groups.values() if len(g) > 1)


def card_tokens(root: Path) -> list[str]:
    toks: list[str] = []
    for p in sorted((Path(root) / C.PKG_REL / "www").glob("*.js")):
        toks += tokenize(p.read_text())
    return toks


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    toks = card_tokens(root)
    dead = dead_definitions(toks)
    clones = clone_copies(toks)
    return {
        "metric": "card",
        "card_dead_definitions": len(dead),
        "card_clone_copies": sum(len(g) for g in clones),
        "details": {"tokens": len(toks), "functions": len(functions(toks)), "dead": dead,
                    "clone_classes": [g[:6] for g in clones]},
        "runtime_s": round(time.perf_counter() - t0, 3),
    }
