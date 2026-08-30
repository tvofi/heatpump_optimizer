"""Checks for Lovelace resource registration.

Getting the card onto the page is as much a part of it working as the card's
own code. These paths had no coverage, and a bug in them is unusually hard to
diagnose from the outside: the files on disk are correct, the integration logs
nothing unusual, and the browser simply keeps running an old card, so upgrades
look like they silently do nothing.

``frontend.py`` is loaded on its own here. Importing the package would pull in
the solver and its dependencies, none of which have anything to do with
serving a file.
"""
from __future__ import annotations

import asyncio
import importlib.util
import logging
import pathlib
import sys
import types

CARD_URL_BASE = "/heatpump_optimizer_static/heatpump-optimizer-card.js"
URL = f"{CARD_URL_BASE}?v=9.9.9"

FAILS = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILS
    print(("  ok  " if cond else "  FAIL") + "  " + name)
    if not cond:
        if detail:
            print("        " + detail)
        FAILS += 1


def _load_frontend():
    # The module type-annotates against homeassistant.core; tests/hastub
    # supplies it, exactly as for the other suites.
    stub = str(pathlib.Path(__file__).resolve().parent / "hastub")
    if stub not in sys.path:
        sys.path.insert(0, stub)
    # Importing the real package would pull in the solver and its
    # dependencies (see the module docstring), so the parent package is a
    # namespace shell whose path is the component directory. frontend loads
    # as a genuine submodule -- its ``from .const import`` resolves against
    # the real const.py -- without executing the package __init__.
    component = pathlib.Path("custom_components/heatpump_optimizer").resolve()
    if "heatpump_optimizer" in sys.modules:
        raise SystemExit("heatpump_optimizer already imported; cannot load standalone")
    pkg = types.ModuleType("heatpump_optimizer")
    pkg.__path__ = [str(component)]
    sys.modules["heatpump_optimizer"] = pkg
    spec = importlib.util.spec_from_file_location(
        "heatpump_optimizer.frontend", component / "frontend.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["heatpump_optimizer.frontend"] = module
    spec.loader.exec_module(module)
    return module


class Resources:
    """Stand-in for Lovelace's resource collection."""

    loaded = True

    def __init__(self, items):
        self._items = items
        self.updated = []
        self.created = []

    def async_items(self):
        return self._items

    async def async_update_item(self, item_id, data):
        self.updated.append((item_id, data))

    async def async_create_item(self, data):
        self.created.append(data)


def _hass(resources, mode="storage"):
    return types.SimpleNamespace(
        data={
            "lovelace": types.SimpleNamespace(mode=mode, resources=resources)
        }
    )


async def main() -> None:
    frontend = _load_frontend()
    register = frontend._register_lovelace_resource

    # A fresh install has nothing registered yet.
    res = Resources([])
    await register(_hass(res), URL)
    check(
        "a missing resource is created",
        [d.get("url") for d in res.created] == [URL],
        f"created {res.created}",
    )

    # After an upgrade the cache-busting query is stale. Leaving it means
    # browsers keep serving the card they already have.
    res = Resources([{"id": "b", "url": f"{CARD_URL_BASE}?v=2.8.0"}])
    await register(_hass(res), URL)
    check(
        "a stale cache-busting query is updated in place",
        res.updated and res.updated[0][1]["url"] == URL,
        f"updated {res.updated}",
    )
    check(
        "and no duplicate is created alongside it",
        not res.created,
        f"created {res.created}",
    )

    # Already correct: touching it would churn the user's config for nothing.
    res = Resources([{"id": "c", "url": URL}])
    await register(_hass(res), URL)
    check(
        "an up-to-date resource is left alone",
        not res.created and not res.updated,
    )

    # The failure that made upgrades appear to do nothing: a second copy of
    # the card, usually a manual install left behind under /local/. It claims
    # the custom element first, so ours loads and is ignored.
    res = Resources([{"id": "d", "url": "/local/heatpump-optimizer-card.js"}])
    await register(_hass(res), URL)
    check(
        "a shadowing copy does not stop the bundled card registering",
        [d.get("url") for d in res.created] == [URL],
        f"created {res.created}",
    )

    # YAML mode owns its own resource list, so we must not write to it.
    res = Resources([])
    await register(_hass(res, mode="yaml"), URL)
    check(
        "YAML mode is left to manage its own resources",
        not res.created and not res.updated,
    )

    # Lovelace internals are not a public API, so a surprise must never
    # escape into config-entry setup.
    broken = types.SimpleNamespace(
        data={"lovelace": types.SimpleNamespace(mode="storage", resources=object())}
    )
    # It logs the failure with a traceback, which is the point; keep that out
    # of the test output.
    logging.disable(logging.CRITICAL)
    try:
        await register(broken, URL)
        raised = False
    except Exception:  # noqa: BLE001
        raised = True
    finally:
        logging.disable(logging.NOTSET)
    check("an unusable resource collection does not raise", not raised)

    # The card is served without long-lived cache headers. The ?v= query only
    # helps where we own the resource entry, which is not the case in YAML
    # mode or for a hand-added resource.
    src = pathlib.Path(
        "custom_components/heatpump_optimizer/frontend.py"
    ).read_text()
    check(
        "the card is served without long-lived cache headers",
        "StaticPathConfig(URL_BASE, www_dir, False)" in src,
        "a cached copy would survive an upgrade",
    )

    print()
    if FAILS:
        print(f"{FAILS} FRONTEND CHECK(S) FAILED")
        sys.exit(1)
    print("ALL FRONTEND CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
