#!/usr/bin/env python3
"""R10-HOTFIX-SAV-ESTIMATE: the notifications blueprint's monthly receipt, rendered.

WHY IT EXISTS. The receipt event (``notifier.EVENT_MONTHLY_RECEIPT``) carries
``saving_includes_wood``, and the blueprint's "Monthly receipt" message states
the event's ``saving_sek`` to the user. Where wood is configured that saving
includes wood's heat and not firewood's cost, so the message must say so (Carry
A, tvofi 2026-11-04). ``tests/entities.py`` pins the template's source, because
CI's interpreter has no jinja2; this harness renders it, under an interpreter
that has one (``/opt/hpo/venv-ha/bin/python``, whose Home Assistant brings
jinja2), so a reader sees the message a user receives.

Asserted arms (rc 1 on DEFECT):

  wood      a saving on a wood house: the card's ``savings.wood_note`` appears
            exactly once in the rendered message.
  no-wood   the null leg: the same saving, ``saving_includes_wood`` false, and
            the note is absent.
  no-saving the event's ``saving_sek`` is null on a wood house: the message
            states no saving, so it carries no note.

Usage: python3 dev/audit/harnesses/r10_sav_receipt_render.py [blueprint.yaml]
The default blueprint is the tree's; pass another file (a ``git show`` of an
older head) to measure that one.
"""
from __future__ import annotations

import pathlib
import re
import sys

import jinja2
import yaml


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
DEFAULT_BP = ROOT / "blueprints/automation/notifications.yaml"
CARD = ROOT / "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor("!input", lambda loader, node: loader.construct_scalar(node))


def receipt_message(path: pathlib.Path) -> str:
    bp = yaml.load(path.read_text(), Loader=_Loader)
    return next(
        option["sequence"][0]["data"]["message"]
        for step in bp["action"] if "choose" in step
        for option in step["choose"] if option.get("alias") == "Monthly receipt"
    )


def main() -> int:
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BP
    note = re.search(r'"savings\.wood_note": "([^"]+)"', CARD.read_text()).group(1)
    template = jinja2.Environment().from_string(receipt_message(path))
    base = {"total_sek": 812.4, "currency": "SEK", "saving_sek": 203.6, "saving_pct": 20.1}
    arms = [
        ("wood", {"saving_includes_wood": True}, 1),
        ("no-wood", {"saving_includes_wood": False}, 0),
        ("no-saving", {"saving_sek": None, "saving_includes_wood": True}, 0),
    ]
    defect = False
    for name, extra, want in arms:
        text = template.render(data={**base, **extra})
        got = text.count(note)
        ok = got == want
        defect |= not ok
        print(f"RESULT {name} notes={got} want={want} {'ok' if ok else 'DEFECT'} message={text!r}")
    return 1 if defect else 0


if __name__ == "__main__":
    sys.exit(main())
