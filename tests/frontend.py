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

    def __init__(self, items, loaded=True):
        self._items = items
        self.updated = []
        self.created = []
        self.loaded = loaded
        self.load_calls = 0

    def async_items(self):
        return self._items

    async def async_load(self):
        self.load_calls += 1
        self.loaded = True

    async def async_update_item(self, item_id, data):
        self.updated.append((item_id, data))

    async def async_create_item(self, data):
        self.created.append(data)


class DataOnlyResources:
    """A resources collection exposing `.data` instead of `.async_items()`.

    A second Home Assistant shape the real Lovelace store has used.
    """

    loaded = True

    def __init__(self, items):
        self.data = items
        self.created = []
        self.updated = []

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

    # Older Home Assistant exposes `lovelace` as a plain dict rather than an
    # object with `.mode`/`.resources` attributes; both shapes must be read
    # the same way.
    res_dict_style = Resources([])
    hass_dict_lovelace = types.SimpleNamespace(
        data={"lovelace": {"mode": "storage", "resources": res_dict_style}}
    )
    await register(hass_dict_lovelace, URL)
    check(
        "dict-style lovelace data is read the same as object-style",
        [d.get("url") for d in res_dict_style.created] == [URL],
        f"created {res_dict_style.created}",
    )

    # Neither shape carries anything reachable as `resources` at all: must be
    # a clean no-op, not a crash reaching into config-entry setup.
    hass_no_resources = types.SimpleNamespace(
        data={"lovelace": types.SimpleNamespace(mode="storage")}
    )
    try:
        await register(hass_no_resources, URL)
        no_resources_raised = False
    except Exception:  # noqa: BLE001
        no_resources_raised = True
    check(
        "lovelace with no resources collection at all is a clean no-op",
        not no_resources_raised,
    )

    # A resources collection that has not loaded its items yet must be loaded
    # before being read, or every item lookup below sees an empty list.
    res_unloaded = Resources([], loaded=False)
    await register(_hass(res_unloaded), URL)
    check(
        "an unloaded resource collection is loaded before being read",
        res_unloaded.load_calls == 1 and res_unloaded.loaded,
        f"load_calls={res_unloaded.load_calls} loaded={res_unloaded.loaded}",
    )

    # A resources object exposing `.data` instead of `async_items()` (the
    # other shape seen in the wild). Also covers an existing entry with no
    # `url` at all, which must be skipped rather than crash the shadow-copy
    # scan.
    #
    # The fixture carries a STALE entry for our own base URL, so reading
    # `.data` and not reading it produce different outcomes: read, the stale
    # entry is found and updated in place and nothing is created; not read,
    # `existing` is empty, nothing matches and the card is CREATED. Asserting
    # only that the resource was created -- as this check first did -- is an
    # outcome that happens on both paths, so it pinned nothing.
    warnings_seen: list[str] = []

    class _Collect(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.WARNING:
                warnings_seen.append(record.getMessage())

    res_data_only = DataOnlyResources(
        [
            {"id": "y"},
            {"id": "d", "url": "/local/heatpump-optimizer-card.js"},
            {"id": "s", "url": f"{CARD_URL_BASE}?v=2.8.0"},
        ]
    )
    collector = _Collect()
    frontend._LOGGER.addHandler(collector)
    try:
        await register(_hass(res_data_only), URL)
    finally:
        frontend._LOGGER.removeHandler(collector)
    check(
        "a resources object without async_items() falls back to .data",
        [(i, d.get("url")) for i, d in res_data_only.updated] == [("s", URL)]
        and not res_data_only.created,
        f"updated={res_data_only.updated} created={res_data_only.created}",
    )
    check(
        "the shadowing copy found via .data is named in a warning",
        any("/local/heatpump-optimizer-card.js" in m for m in warnings_seen),
        f"warnings {warnings_seen}",
    )

    # A stale entry with no `id` cannot be updated in place (there is nothing
    # to address the update to) and must be left alone rather than duplicated.
    res_stale_no_id = Resources([{"url": f"{CARD_URL_BASE}?v=2.8.0"}])
    await register(_hass(res_stale_no_id), URL)
    check(
        "a stale resource with no id is left alone, not duplicated",
        not res_stale_no_id.updated and not res_stale_no_id.created,
        f"updated={res_stale_no_id.updated} created={res_stale_no_id.created}",
    )

    # --- _register_static_path: serving the card's JS itself -------------
    static = frontend._register_static_path

    class _ModernHttp:
        def __init__(self, raise_exc=None):
            self.calls = []
            self._raise = raise_exc

        async def async_register_static_paths(self, configs):
            self.calls.append(configs)
            if self._raise:
                raise self._raise

    class _FakeStaticPathConfig:
        def __init__(self, url_path, path, cache_headers):
            self.url_path = url_path
            self.path = path
            self.cache_headers = cache_headers

    fake_http_component = types.ModuleType("homeassistant.components.http")
    fake_http_component.StaticPathConfig = _FakeStaticPathConfig
    # tests/hastub has no homeassistant.components.http at all, which is what
    # makes every OTHER Home Assistant release in this suite take the
    # deprecated branch below -- injected here to reach the modern one too.
    sys.modules["homeassistant.components.http"] = fake_http_component

    modern_http = _ModernHttp()
    await static(types.SimpleNamespace(http=modern_http), "/www/dir")
    check(
        "the modern async static-path API is used when it is available",
        len(modern_http.calls) == 1
        and modern_http.calls[0][0].url_path == frontend.URL_BASE
        and modern_http.calls[0][0].path == "/www/dir"
        and modern_http.calls[0][0].cache_headers is False,
        str([vars(c[0]) for c in modern_http.calls]),
    )

    logging.disable(logging.CRITICAL)
    try:
        await static(
            types.SimpleNamespace(http=_ModernHttp(raise_exc=RuntimeError("boom"))),
            "/www/dir",
        )
        modern_broken_raised = False
    except Exception:  # noqa: BLE001
        modern_broken_raised = True
    finally:
        logging.disable(logging.NOTSET)
    check(
        "an unexpected error from the modern API is caught, not propagated",
        not modern_broken_raised,
    )

    del sys.modules["homeassistant.components.http"]

    class _LegacyHttp:
        def __init__(self, raise_exc=None):
            self.calls = []
            self._raise = raise_exc

        def register_static_path(self, url, path, cache_headers):
            self.calls.append((url, path, cache_headers))
            if self._raise:
                raise self._raise

    legacy_http = _LegacyHttp()
    await static(types.SimpleNamespace(http=legacy_http), "/www/dir")
    check(
        "the deprecated sync call is used when the modern API is unavailable",
        legacy_http.calls == [(frontend.URL_BASE, "/www/dir", False)],
        str(legacy_http.calls),
    )

    logging.disable(logging.CRITICAL)
    try:
        await static(
            types.SimpleNamespace(http=_LegacyHttp(raise_exc=OSError("disk full"))),
            "/www/dir",
        )
        legacy_broken_raised = False
    except Exception:  # noqa: BLE001
        legacy_broken_raised = True
    finally:
        logging.disable(logging.NOTSET)
    check(
        "a failure in the deprecated sync call is caught, not propagated",
        not legacy_broken_raised,
    )

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
