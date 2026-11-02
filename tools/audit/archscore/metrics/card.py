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

GATE ONLY (weight 0), counter C24, as ``shape_copies`` is for Python:

  card_rule_copies        sites spelling a one-statement rule another site spells too: a RULE is a run of
                    two or more operands of one ``&&``/``||`` chain (at one bracket depth, cut at
                    ``;`` ``,`` ``?`` ``:`` ``=`` ``=>`` a block and a statement keyword) in which some
                    value is read by two operands -- a test of one value, ``s.state === "unavailable"
                    || s.state === "unknown"`` -- and which carries RULE_TOKENS tokens or more and
                    some content (a string, a number, a member name). Its values (a name with its
                    member path, ``opts.probe``; not a keyword or a ``KEEP`` global) are numbered by
                    first use within the run and its strings keep their text, so ``x === null ||
                    x === undefined || x === ""`` in one function and the same over ``opts.v`` in
                    another are one rule, and a test of two different strings is not. A site is one chain;
                    it counts once when any of its runs is spelled at another site, in any function
                    or the same one. The 20-token window cannot see such a rule: the #2401 review
                    spelled three of ARCH2-s5's card_shapes rules once more and card_clone_copies read
                    108 -> 108. Not weighted, by the reason ``shapes.py`` gives: one operand
                    re-spelled leaves the class while the rule is still written again, so a fall
                    credits nothing; a rise is a new spelling of a rule, and refuses.
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
#: Counter C24: the one-statement rule census (``card_rule_copies``). ``vector.py`` switches it off.
RULES = True
#: Normalized tokens a rule's run needs, its values one token each and its operands joined by one: the
#: live-state guard ``v0 === "unavailable" || v0 === "unknown"`` carries 7, the smallest of ARCH2-s5's rules.
RULE_TOKENS = 7
#: Globals and keywords a rule's run keeps as spelled (every other name not after ``.`` is numbered).
KEEP = frozenset("typeof instanceof in void new delete null undefined true false this super NaN Infinity "
                 "Number Math Array Object String Boolean Date JSON isFinite isNaN parseFloat parseInt".split())
#: Tokens that end a rule's run at its own depth (a block's braces and its own brackets end it too).
_RULE_CUT = frozenset(";  , ? : = => += -= *= /= %= **= <<= >>= >>>= &= |= ^= &&= ||= ??= return throw case "
                      "default if else for while do switch try catch finally const let var yield await".split())
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


def tokenize(src: str, strings: bool = False) -> list[str]:
    """``src`` as tokens (the module docstring's rules). ``strings``: a quoted string is its text, double-quoted,
    rather than ``S`` -- one token either way, so the two streams index alike (the rule census reads it)."""
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
                out.extend(tokenize(src[inner_start:j - 1], strings))
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
            j = _skip_string(src, i)
            out.append('"' + src[i + 1:j - 1] + '"' if strings else "S")
            i = j
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


def _chains(body: list[str]) -> list[list[list[str]]]:
    """Every ``&&``/``||`` chain of two or more operands in ``body``, as its operands, at each bracket depth
    (the module docstring's cuts)."""
    out: list[list[list[str]]] = []

    def level(seq: list[str]) -> None:
        pieces, cur, i = [], [], 0
        while i < len(seq):
            t = seq[i]
            if t in ("(", "[", "{"):
                j, depth = i, 0
                while j < len(seq):
                    depth += seq[j] in ("(", "[", "{")
                    depth -= seq[j] in (")", "]", "}")
                    if depth == 0:
                        break
                    j += 1
                level(seq[i + 1:j])
                if t == "{":
                    pieces.append(cur)
                    cur = []
                else:
                    cur += seq[i:j + 1]
                i = j + 1
                continue
            if t in _RULE_CUT or t in (")", "]", "}"):
                pieces.append(cur)
                cur = []
            else:
                cur.append(t)
            i += 1
        pieces.append(cur)
        for piece in pieces:
            operands, part, depth = [], [], 0
            for t in piece:
                depth += t in ("(", "[", "{")
                depth -= t in (")", "]", "}")
                if depth == 0 and t in ("&&", "||"):
                    operands.append(part)
                    part = []
                else:
                    part.append(t)
            operands.append(part)
            if len(operands) >= 2 and all(operands):
                out.append(operands)

    level(body)
    return out


def _rule_key(operands: list[list[str]]) -> tuple | None:
    """A run of operands as a rule: each value it reads numbered by first use, or None when no value is read by
    two of its operands, it carries fewer than RULE_TOKENS tokens, or it carries no CONTENT -- a string, a
    number, a ``KEEP`` word or a member or callee name -- so ``a === b || a === c`` is a shape, not a rule. A value is a name with its member path
    (``probe``, ``opts.probe``, ``this._hass.states[id].state`` are each one value); a call keeps its callee's
    members as spelled (``v0.trim()``), and a path rooted at a ``KEEP`` global stays as spelled
    (``Number.isFinite``)."""
    num: dict[str, str] = {}
    readers: dict[str, set] = defaultdict(set)
    key: list[str] = []
    content = False
    for k, part in enumerate(operands):
        if k:
            key.append("&|")
        m, n = 0, len(part)
        while m < n:
            t = part[m]
            if not (_IDENT.fullmatch(t) and (t == "this" or t not in KEEP) and t not in _HEADS
                    and t not in ("S", "R", "F") and (m == 0 or part[m - 1] not in (".", "?."))):
                content = content or t[:1] == '"' or bool(_NUM.fullmatch(t)) \
                    or (_IDENT.fullmatch(t) is not None and t not in ("S", "R", "F", "this"))
                key.append(t)
                m += 1
                continue
            e = m + 1  # the path's extent: ``.name``, ``?.name`` and ``[..]`` steps
            while e < n:
                if part[e] in (".", "?.") and e + 1 < n and _IDENT.fullmatch(part[e + 1]):
                    e += 2
                elif part[e] == "[":
                    e = m + _matching(part[m:], e - m) + 1
                else:
                    break
            if e < n and part[e] == "(":  # a call: the root is the value, its members stay
                e = m + 1
            v = num.setdefault(" ".join(part[m:e]), f"v{len(num)}")
            readers[v].add(k)
            key.append(v)
            m = e
    if len(key) < RULE_TOKENS or not content or not any(len(r) >= 2 for r in readers.values()):
        return None
    return tuple(key)


def rule_copies(toks: list[str]) -> list[list[str]]:
    """Classes of sites spelling one rule (``card_rule_copies``): ``toks`` keeps string text (``tokenize(..,
    strings=True)``); each member is ``function@index:chain``."""
    fns = functions(toks)
    owners: dict[tuple, set] = defaultdict(set)
    for k, fn in enumerate(fns):
        _n, start, _b0, end = fn
        nested = [(s0, e0) for (_m, s0, _c, e0) in fns if start < s0 and e0 <= end and (s0, e0) != (start, end)]
        outer = [(a, b) for a, b in nested if not any(a2 < a and b <= b2 for a2, b2 in nested if (a2, b2) != (a, b))]
        for c, operands in enumerate(_chains(_own_tokens(toks, fn, outer))):
            site = f"{fn[0]}@{k}:{c}"
            for a in range(len(operands)):
                for b in range(a + 2, len(operands) + 1):
                    key = _rule_key(operands[a:b])
                    if key is not None:
                        owners[key].add(site)
    parent: dict = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for sites in owners.values():
        if len(sites) > 1:
            first, *rest = sorted(sites)
            for o in rest:
                parent[find(o)] = find(first)
    groups: dict = defaultdict(list)
    for m in parent:
        groups[find(m)].append(m)
    return sorted(sorted(g) for g in groups.values() if len(g) > 1)


def card_tokens(root: Path, strings: bool = False) -> list[str]:
    toks: list[str] = []
    for p in sorted((Path(root) / C.PKG_REL / "www").glob("*.js")):
        toks += tokenize(p.read_text(), strings)
    return toks


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    texts = card_tokens(root, strings=True)
    toks = ["S" if t[:1] == '"' else t for t in texts]
    dead = dead_definitions(toks)
    clones = clone_copies(toks)
    rules = rule_copies(texts) if RULES else []
    return {
        "metric": "card",
        "card_dead_definitions": len(dead),
        "card_clone_copies": sum(len(g) for g in clones),
        "card_rule_copies": sum(len(g) for g in rules),
        "details": {"tokens": len(toks), "functions": len(functions(toks)), "dead": dead,
                    "clone_classes": [g[:6] for g in clones], "rule_classes": [g[:6] for g in rules]},
        "runtime_s": round(time.perf_counter() - t0, 3),
    }
