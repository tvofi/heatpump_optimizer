#!/usr/bin/env python3
"""Home Assistant itself, in the container an installation actually runs (#521).

``tests/deployment_shape.py`` (#513) builds the deployment *shape* -- the
production module name and the ``custom_components`` filesystem layout, with no
``tests/`` sibling -- and drives the process worker through it in about a
second. It says in its own docstring what it cannot do: ``homeassistant`` comes
from ``tests/hastub`` there, as it does in every other lane, so no script in
this directory has ever observed real Home Assistant import or setup semantics.
That is the third divergence of #513 and it is what let #511 -- every solve
failing, on every install, permanently -- ship green in v6.3.15.

This lane closes it by running the integration inside the official
``homeassistant/home-assistant`` image: real Home Assistant, real interpreter,
real ``/config/custom_components/heatpump_optimizer`` path, real
``custom_components.*`` qualified name, real config-entry setup. It is nightly
only, because it costs minutes, needs Docker, and is the first lane here that
can go red for a reason outside this repository.

THE ASSERTION THAT MATTERS IS THAT A PLAN CAME OUT. Setup succeeded throughout
#511; it was the solve that failed. A lane asserting only "the integration
loaded" would have been green for the whole of that release, so the checks are
ordered outward from ``plan:*`` rather than inward from "it booted".

Deliberately NOT pytest-homeassistant-custom-component. Its layout puts the
repository root on ``sys.path`` and keeps a ``tests/`` sibling, which is the
branch of ``coordinator._worker_env`` no installation takes -- so #511 may not
reproduce under it at all. It would buy real Home Assistant import semantics
while staying blind to the defect that motivated the work.

WHAT THIS LANE DOES NOT COVER, stated the way ``deployment_shape.py`` states
its own limit:

* **Tibber.** Prices are the one input whose absence stops a solve outright
  (``_fetch_tibber_prices`` raises ``UpdateFailed``), and the real endpoint
  needs a live account. ``api.tibber.com`` is redirected to a local TLS server
  in the container by ``--add-host``, whose certificate is added to the trust
  store the shared aiohttp session uses. Production code is not patched: the
  real URL, the real session and real TLS are exercised; only the counterparty
  is ours. The Tibber *account* path -- reauth, a refused token -- is not
  covered.
* **Actuation.** No heat-pump switch, valve or frequency entity is configured,
  and the two ECL110 MQTT topics are blanked because the container has no
  broker, so ``_apply_action`` and its followers are reached but write
  nowhere. This lane observes that a plan exists, not that it was carried out.
* **Home Assistant's own complaints.** Its loop protection fired twice on this
  integration on this lane's first green run (#525); #540 moved both off the
  loop, so ``KNOWN_BLOCKING`` is empty and ANY report against this package now
  fails ``log:no_new_blocking_call``. What the pin cannot see is an upstream
  reword of the report itself: ``log:blocking_report_parsed`` catches a reword
  of the half naming the source line, and nothing here catches a reword of
  ``Detected blocking call to``. Only a deliberate blocking call, provoked
  inside the container, would (#588).
* **The config flow.** The entry is seeded into ``.storage/core.config_entries``
  from the defaults recorded in ``tests/golden/config_flow.json``, so the nine
  setup steps are not driven here. ``tests/entities.py`` and the golden lane own
  the flow itself.

AND MOST OF WHAT A CONTAINER COULD ASSERT, WHICH THE FOUR LIMITS ABOVE DO NOT
SAY (#533). The programme's production-escape analysis derives fourteen
assertions for this lane; the four above are not any of the ten missing ones,
so a reader had to re-derive the gap to find it. Written down instead:

===  ====================================================  ==========  =======
A    what it asserts                                       escapes     state
===  ====================================================  ==========  =======
A1   the entry reaches ``loaded``, both image tags         6           done
A2   a plan was actually produced                          4           done
A3   the published-state sweep, judged by HA's machinery   15          #584
A4   availability conjoins the coordinator (fault-inject)  6           none
A5   the entry round-trips through its own 23 forms        9           #587
A6   corrupt-store resilience                              4           none
A7   the log carries none of this integration's failures   5           partial
A8   services register once, deregister on unload          3           #587
A9   reload without growth                                 3           #587
A10  diagnostics leak no credential and no location        2           #585
A11  a failing service raises, it does not no-op           3           none
A12  an older schema version migrates                      1           none
A13  the currency follows the instance                     1           none
A14  setup does not block the event loop                   1           partial
===  ====================================================  ==========  =======

Roughly 15 of the ~58 escapes a container could reach. **A3 is worth more than
the four implemented assertions combined** and is the one to build next. The
counts are bullet-level, stable in ranking and about +/-15 in absolute terms;
the two largest classes in the record -- solver numbers and card geometry, 68
escapes between them -- are out of this lane's reach by construction, so this
is the deployment-shape and HA-citizenship lane and not a general safety net.
A4, A6, A11, A12 and A13 have no issue: they are recorded here and unscheduled,
which is a different thing from unnoticed.

    python tests/nightly_ha.py --image homeassistant/home-assistant:2025.2.0

The same file is the driver that runs inside the container (``--inside``); the
container half never sees this repository, only ``/config`` and its own two
mounted files.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Home Assistant loads an integration from ``<config>/custom_components/<domain>``.
CONFIG_DIR_NAME = "custom_components"
PACKAGE_NAME = "heatpump_optimizer"
PACKAGE_REL = f"{CONFIG_DIR_NAME}/{PACKAGE_NAME}"

# Inside the container. ``/opt/hpo`` holds exactly this file and the seed, so
# nothing on the driver's own ``sys.path`` can make the package under test
# resolvable by accident -- the trap `deployment_shape.py` calls out.
IN_CONFIG = "/config"
IN_DRIVER_DIR = "/opt/hpo"
IN_SEED = f"{IN_DRIVER_DIR}/seed.json"
LOG_NAME = "home-assistant.log"

TIBBER_HOST = "api.tibber.com"

MARKER = "<<<nightly-ha-json>>>"

# What the container half must report. The outer half requires this set
# exactly: a driver that dies after two checks, or one whose checks were
# quietly renamed away, fails here instead of looking like a pass. A no-op is
# indistinguishable from a pass unless something demands the checks by name.
INSIDE_CHECKS = (
    "shape:package_at_config_path",
    "shape:no_tests_sibling",
    "shape:inherited_pythonpath_cannot_mask",
    "ha:home_assistant_is_real",
    "ha:core_running",
    "entry:loaded",
    "entities:registered",
    "entities:coordinator_healthy",
    "entities:none_unavailable_by_coordinator",
    "plan:optimization_result",
    "plan:last_optimization_published",
    "plan:current_action_published",
    "plan:setpoints_non_empty",
    "plan:no_solve_repair",
)

# Judged by the outer half, over the container's combined output and the log
# file the run left in the bind mount. The worker child inherits the parent's
# stderr (``coordinator._ensure_worker`` passes ``stderr=None``), so its
# traceback lands on the container's stderr and never in home-assistant.log --
# which is why both streams are scanned rather than the log alone.
#
# Demanded by name, exactly as ``INSIDE_CHECKS`` is, and for the same reason
# its comment gives. Until #533 nothing referenced this tuple at all: it was a
# roster the run never consulted, so a check deleted or renamed out here left
# a shorter green run and no other trace. ``run:all_checks_ran`` is the demand
# and names itself in its own roster.
OUTSIDE_CHECKS = (
    "run:driver_reported",
    "run:exit_status",
    "run:all_checks_ran",
    "log:no_module_not_found",
    "log:no_worker_exit",
    "log:no_integration_traceback",
    "log:blocking_report_parsed",
    "log:no_new_blocking_call",
    "log:blocking_pin_not_stale",
)

FORBIDDEN = {
    "log:no_module_not_found": "ModuleNotFoundError",
    "log:no_worker_exit": "process worker exited rc=",
}

TRACEBACK_HEAD = "Traceback (most recent call last):"

# The repairs that mean the solve route itself is in trouble. Named rather than
# "the integration raised nothing", because a defaults-only entry with no
# lower-floor sensor and no legionella schedule legitimately raises others, and
# a check that failed on those would become pressure to weaken it later.
# solve_worker_fallback is #515's: with an in-process fallback in place a
# worker that can unpickle nothing still produces a plan, so without this the
# plan checks alone would call a degraded install healthy.
SOLVE_REPAIRS = frozenset({"solve_failures", "solve_worker_fallback"})

# Home Assistant's own loop protection, which no lane using tests/hastub can
# see -- `homeassistant.util.loop` does not exist there. Its report carries a
# stack, so it is picked out by its own rule instead of being counted as an
# exception traceback.
#
# `BLOCKING_CALL` is built FROM `BLOCKING_AT_OURS` rather than beside it, so
# the loose anchor and the strict pin cannot drift apart. The loose one asks
# only whether Home Assistant blamed this package; the strict one also reads
# the source line, which is the half an upstream reword would take away. A
# report the loose regex claims and the strict one cannot parse is that
# reword, and `log:blocking_report_parsed` is where it lands -- because
# without it the pin degrades to always-pass and says nothing (#533).
_BLOCKING_AT = (
    r"Detected blocking call to (\S+) .* at "
    rf"({re.escape(PACKAGE_REL)}/[\w./]+)"
)
BLOCKING_AT_OURS = re.compile(_BLOCKING_AT)
BLOCKING_CALL = re.compile(_BLOCKING_AT + r", line \d+: (.*?) \(offender:")

# A RATCHET, IN BOTH DIRECTIONS, AND BOTH DIRECTIONS FAIL.
#
# `log:no_new_blocking_call` refuses growth: an offender not listed here is a
# new defect. `log:blocking_pin_not_stale` refuses decay: an offender listed
# here that the run did not produce has been FIXED, and a pin outliving its
# defect would pass while pinning nothing. #525's two entries stood here after
# #540 removed both, and the run went green either way -- one check with a
# subset test and a detail line cannot report the second direction, because a
# shrunken pin is a pass and `Checks.check` blanked the detail on a pass.
#
# The two directions are separate checks rather than an equality test for the
# reason the old comment measured: an offender on a conditional path (#525's
# `worker.wait`, reached only while the worker is alive) is legitimately
# absent from some runs. Equality would fail such a run for a second, unrelated
# reason. Two checks name which direction moved, and a pinned entry whose path
# is that conditional does not belong here in the first place.
#
# Empty since #540 (#533): the import went to `async_add_import_executor_job`
# and the reap to `async_add_executor_job`, so ANY report against this package
# now fails the lane -- the strongest form, and the one an empty pin cannot go
# stale in. If #540's fix is incomplete, this lane says so by name.
KNOWN_BLOCKING: frozenset[tuple[str, str, str]] = frozenset()
BLOCKING_REPORT = "Detected blocking call to"


# --- shared reporting -------------------------------------------------------


class Checks:
    """A pass/fail record that survives the container boundary as JSON."""

    def __init__(self) -> None:
        self.results: dict[str, list] = {}

    def check(self, name: str, cond: object, detail: str = "") -> bool:
        """Record a check. The detail is kept whether it passed or failed.

        Blanking it on pass is how the stale ``KNOWN_BLOCKING`` pin stayed
        invisible (#533): its detail names the offenders pinned but not seen,
        and a pin that has gone stale *passes*, so the one line that would
        have reported it was exactly the line thrown away. A detail is a
        measurement, not an excuse for a failure -- write it to read in both
        states, because it is only ever printed in one of them by accident.
        """
        ok = bool(cond)
        self.results[name] = [ok, detail]
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f"  [{detail}]" if detail else ""))
        return ok

    def failures(self) -> list[str]:
        return [n for n, (ok, _) in self.results.items() if not ok]


# ===========================================================================
# The container half
# ===========================================================================


# Cheap at night, dear morning and evening: a curve with something to optimise
# against, and no randomness anywhere, so two runs of this lane differ only by
# the hour they started at.
DIURNAL_PRICE = (
    0.55, 0.50, 0.48, 0.47, 0.50, 0.70, 1.20, 1.60, 1.45, 1.10, 0.90, 0.80,
    0.75, 0.72, 0.78, 0.95, 1.35, 1.70, 1.50, 1.15, 0.95, 0.80, 0.68, 0.60,
)


def _hourly_prices(now: datetime) -> tuple[list[dict], list[dict]]:
    """A deterministic three-day price curve in the Tibber wire shape.

    Starts two hours behind ``now`` so the horizon the optimizer builds is
    fully inside published data rather than inside the learned extrapolation.
    """
    start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=2)
    entries = [
        {
            "total": DIURNAL_PRICE[(start + timedelta(hours=i)).hour],
            "startsAt": (start + timedelta(hours=i)).isoformat(),
            "level": "NORMAL",
        }
        for i in range(72)
    ]
    return entries[:24], entries[24:]


def _tibber_body(now: datetime) -> bytes:
    today, tomorrow = _hourly_prices(now)
    return json.dumps(
        {
            "data": {
                "viewer": {
                    "homes": [
                        {
                            "currentSubscription": {
                                "priceInfo": {
                                    "current": today[2],
                                    "today": today,
                                    "tomorrow": tomorrow,
                                }
                            }
                        }
                    ]
                }
            }
        }
    ).encode()


def _self_signed(host: str, workdir: Path) -> tuple[Path, Path]:
    """A certificate for ``host``, trusted by appending it to the CA bundle."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, host)])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(host)]), False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), True)
        .sign(key, hashes.SHA256())
    )
    cert_path, key_path = workdir / "price.crt", workdir / "price.key"
    pem = cert.public_bytes(serialization.Encoding.PEM)
    cert_path.write_bytes(pem)
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    import certifi

    with open(certifi.where(), "ab") as bundle:
        bundle.write(b"\n" + pem)
    return cert_path, key_path


def _serve_prices(workdir: Path) -> None:
    """Answer the real Tibber URL from loopback, over real TLS.

    ``--add-host`` points the hostname here; the certificate above is in the
    bundle ``homeassistant.util.ssl`` hands to the shared aiohttp session. So
    ``TIBBER_API_URL``, the session and the TLS handshake are all the
    production ones, and no module constant is monkeypatched.
    """
    import ssl
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    cert, key = _self_signed(TIBBER_HOST, workdir)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's name
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            body = _tibber_body(datetime.now().astimezone())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: object) -> None:
            return

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # PROTOCOL_TLS_SERVER still permits TLS 1.0/1.1, which CodeQL flags high
    # (py/insecure-protocol) and which nothing here needs.
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(cert, key)
    server = ThreadingHTTPServer(("127.0.0.1", 443), Handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()


def _write_config_entries(seed: dict) -> None:
    """Seed ``.storage/core.config_entries`` in Home Assistant's own format.

    The storage version is read from the installed ``config_entries`` module
    rather than written down, so this lane neither triggers a migration it did
    not mean to nor claims a version newer than the image's.
    """
    from homeassistant import config_entries as ce

    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "created_at": now,
        "data": seed["data"],
        "disabled_by": None,
        "discovery_keys": {},
        "domain": PACKAGE_NAME,
        "entry_id": seed["entry_id"],
        "minor_version": 1,
        "modified_at": now,
        "options": seed["options"],
        "pref_disable_new_entities": False,
        "pref_disable_polling": False,
        "source": "user",
        "subentries": [],
        "title": seed["title"],
        "unique_id": None,
        "version": seed["version"],
    }
    store = Path(IN_CONFIG) / ".storage"
    store.mkdir(parents=True, exist_ok=True)
    (store / "core.config_entries").write_text(
        json.dumps(
            {
                "version": ce.STORAGE_VERSION,
                "minor_version": ce.STORAGE_VERSION_MINOR,
                "key": "core.config_entries",
                "data": {"entries": [entry]},
            },
            indent=1,
        )
    )


def _check_shape(checks: Checks) -> None:
    """The deployment shape, asserted rather than assumed.

    Every check below turns green if the package happens to be importable from
    somewhere else, so the shape is proved before anything is measured -- and
    in particular the inherited ``PYTHONPATH`` is proved unable to resolve
    ``custom_components`` on its own, because that is precisely what #511's
    ``_worker_env`` has to supply and an image that supplied it for free would
    make this lane pass while proving nothing.
    """
    pkg = Path(IN_CONFIG) / PACKAGE_REL
    checks.check(
        "shape:package_at_config_path",
        (pkg / "__init__.py").is_file() and (pkg / "manifest.json").is_file(),
        f"{pkg} is not an integration",
    )
    checks.check(
        "shape:no_tests_sibling",
        not (Path(IN_CONFIG) / "tests").exists()
        and not (pkg.parent / "tests").exists(),
        "a tests/ sibling puts _worker_env on the branch no install takes",
    )
    inherited = [p for p in (os.environ.get("PYTHONPATH") or "").split(os.pathsep) if p]
    masks = [p for p in inherited if (Path(p) / CONFIG_DIR_NAME).is_dir()]
    checks.check(
        "shape:inherited_pythonpath_cannot_mask",
        not masks,
        f"inherited PYTHONPATH already resolves {CONFIG_DIR_NAME}: {masks}",
    )


async def _boot(seed: dict):
    """Boot Home Assistant the way its own entry point does."""
    import dataclasses

    from homeassistant import bootstrap, runner

    wanted = {
        "config_dir": IN_CONFIG,
        "verbose": False,
        "log_rotate_days": None,
        "log_file": str(Path(IN_CONFIG) / LOG_NAME),
        "log_no_color": True,
        "skip_pip": False,
        "recovery_mode": False,
        "debug": False,
        "open_ui": False,
    }
    names = {f.name for f in dataclasses.fields(runner.RuntimeConfig)}
    config = runner.RuntimeConfig(**{k: v for k, v in wanted.items() if k in names})
    _write_config_entries(seed)
    hass = await bootstrap.async_setup_hass(config)
    if hass is not None:
        await hass.async_start()
        await hass.async_block_till_done()
    return hass


async def _await_plan(coordinator, deadline: float) -> None:
    """Wait for the background first solve ``async_setup_entry`` scheduled.

    ``async_config_entry_first_refresh`` deliberately skips the solve, so a
    plan exists only after the deferred refresh has run. Waited for rather
    than forced, because the scheduling is part of what this lane observes;
    one explicit refresh follows if the deadline passes, so a slow runner
    reports a solve failure rather than a timeout.
    """
    import asyncio
    import time

    while time.monotonic() < deadline:
        if getattr(coordinator, "_optimization_result", None) is not None:
            return
        await asyncio.sleep(1.0)
    await coordinator.async_refresh()


def _check_entry(checks: Checks, hass, seed: dict):
    from homeassistant.config_entries import ConfigEntryState

    entry = hass.config_entries.async_get_entry(seed["entry_id"])
    state = getattr(entry, "state", None)
    checks.check(
        "entry:loaded",
        state is ConfigEntryState.LOADED,
        f"no entry {seed['entry_id']}: the seed did not reach the manager"
        if entry is None
        else f"entry state is {state} (reason: {getattr(entry, 'reason', None)})",
    )
    return entry


def _self_gated(hass, entity_id: str) -> bool:
    """Whether the entity narrows its own availability past the coordinator's.

    Derived from the class, never listed. Roughly a third of this roster
    overrides ``available`` to mean "the install has no lower floor / no
    battery / no hot water", and on a defaults-only entry those are
    unavailable because they are supposed to be; pinning today's set of them
    would rot on the next entity added. What must never happen is an entity
    going unavailable because the COORDINATOR failed, and that is exactly the
    set this leaves behind. An entity whose object cannot be found counts as
    NOT self-gated, so an unresolvable one fails rather than disappears.
    """
    from homeassistant.helpers.entity import Entity
    from homeassistant.helpers.entity_component import DATA_INSTANCES
    from homeassistant.helpers.update_coordinator import CoordinatorEntity

    component = hass.data.get(DATA_INSTANCES, {}).get(entity_id.split(".")[0])
    entity = component.get_entity(entity_id) if component is not None else None
    if entity is None:
        return False
    return type(entity).available not in (CoordinatorEntity.available, Entity.available)


def _check_entities(checks: Checks, hass, entry) -> None:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    registered = er.async_entries_for_config_entry(registry, entry.entry_id)
    # Six sensors set _attr_entity_registry_enabled_default = False. A disabled
    # registry entry has no state object at all, which is the same shape as an
    # entity that failed to add -- so they are excluded here rather than
    # tolerated below, and an ENABLED entity with no state still fails.
    enabled = [e for e in registered if e.disabled_by is None]
    domains = {e.entity_id.split(".")[0] for e in enabled}
    checks.check(
        "entities:registered",
        len(enabled) > 0 and {"sensor", "binary_sensor", "climate"} <= domains,
        f"{len(enabled)} enabled entities across {sorted(domains)}",
    )
    checks.check(
        "entities:coordinator_healthy",
        bool(entry.runtime_data.last_update_success),
        "last_update_success is False: every entity is unavailable at once",
    )
    unavailable = [
        e.entity_id
        for e in enabled
        if (s := hass.states.get(e.entity_id)) is None or s.state == "unavailable"
    ]
    exposed = [e for e in unavailable if not _self_gated(hass, e)]
    print(
        f"  ..   {len(registered)} registered, {len(registered) - len(enabled)} "
        f"disabled by default, {len(unavailable)} unavailable, "
        f"{len(unavailable) - len(exposed)} of those self-gated"
    )
    for item in sorted(registered, key=lambda e: e.entity_id):
        state = hass.states.get(item.entity_id)
        print(f"       {item.entity_id} = {state.state if state else '<no state>'}")
    checks.check(
        "entities:none_unavailable_by_coordinator",
        not exposed,
        f"{len(exposed)} unavailable without gating themselves: {sorted(exposed)[:10]}",
    )


def _check_plan(checks: Checks, hass, entry) -> None:
    """The point of the lane: a plan came out.

    Read from the payload the entities read (``_build_data_dict``) as well as
    from the result object, because #511 left both empty while setup and every
    entity stayed perfectly healthy.
    """
    from homeassistant.helpers import issue_registry as ir

    coordinator = entry.runtime_data
    data = coordinator.data or {}
    result = getattr(coordinator, "_optimization_result", None)
    checks.check(
        "plan:optimization_result",
        result is not None,
        f"no solve completed; solve_failures={getattr(coordinator, '_solve_failures', '?')}",
    )
    checks.check(
        "plan:last_optimization_published",
        data.get("last_optimization") is not None,
        "the payload's last_optimization is the repair notice's em-dash",
    )
    action = data.get("current_action")
    checks.check(
        "plan:current_action_published",
        isinstance(action, dict) and "mode" in action,
        f"current_action={action!r}",
    )
    setpoints = list(getattr(result, "optimal_setpoints", []) or [])
    checks.check(
        "plan:setpoints_non_empty",
        len(setpoints) > 0,
        f"{len(setpoints)} setpoints in the plan",
    )
    raised = {
        key for (domain, key) in ir.async_get(hass).issues if domain == PACKAGE_NAME
    }
    checks.check(
        "plan:no_solve_repair",
        not (raised & SOLVE_REPAIRS),
        f"solve-route repairs raised: {sorted(raised & SOLVE_REPAIRS)}; "
        f"everything raised: {sorted(raised)}",
    )


async def _inside(seed: dict, budget: float) -> int:
    import time

    checks = Checks()
    _check_shape(checks)
    hass = await _boot(seed)
    checks.check("ha:home_assistant_is_real", hass is not None, "bootstrap returned None")
    if hass is None:
        return _emit(checks)
    import homeassistant.core as ha_core

    checks.check(
        "ha:core_running",
        hass.state is ha_core.CoreState.running,
        f"core state is {hass.state}",
    )
    entry = _check_entry(checks, hass, seed)
    if getattr(entry, "runtime_data", None) is not None:
        await _await_plan(entry.runtime_data, time.monotonic() + budget)
        await hass.async_block_till_done()
        _check_entities(checks, hass, entry)
        _check_plan(checks, hass, entry)
    await hass.async_stop()
    return _emit(checks)


def _emit(checks: Checks) -> int:
    print(MARKER + json.dumps(checks.results), flush=True)
    return 1 if checks.failures() else 0


def _run_inside(args: argparse.Namespace) -> int:
    import asyncio

    seed = json.loads(Path(IN_SEED).read_text())
    _serve_prices(Path(tempfile.mkdtemp()))
    return asyncio.run(_inside(seed, args.plan_budget))


# ===========================================================================
# The runner half
# ===========================================================================


def _fixture_defaults(pages: dict) -> dict:
    """Every field's recorded default, as a value.

    ``tests/golden/config_flow.json`` stores each default as ``repr``; a field
    whose default is ``null`` (the entity selectors, mostly) is left out
    entirely so the integration's own fallback applies rather than a literal
    ``None`` the config flow would never have written.
    """
    out: dict = {}
    for page in pages.values():
        for name, spec in page.items():
            if not isinstance(spec, dict) or "selector" not in spec:
                continue
            if spec.get("default") is None:
                continue
            try:
                out[name] = ast.literal_eval(spec["default"])
            except (ValueError, SyntaxError):
                continue
    return out


def _seed_payload() -> dict:
    """The config entry, from the flow's own recorded defaults.

    Driving the nine setup steps is the expensive part of a real-Home-Assistant
    test and it is already paid for: the golden fixture records every page's
    schema, so "the user accepted every default" is a dictionary comprehension
    rather than a UI script. The entity keys the integration reads are then
    pointed at the template entities ``configuration.yaml`` defines, and the
    Tibber token at the local server -- the two things a defaults-only entry
    cannot supply.
    """
    fixture = json.loads((ROOT / "tests" / "golden" / "config_flow.json").read_text())
    options_pages = {k: v for k, v in fixture.items() if not k.startswith("_")}
    initial_pages = {
        k: v for k, v in fixture["_initial"].items() if "menu" not in v
    }
    const = (ROOT / "custom_components" / PACKAGE_NAME / "const.py").read_text()
    version = re.search(r"CONFIG_ENTRY_VERSION:\s*Final\s*=\s*(\d+)", const)
    if version is None:
        raise SystemExit("const.py no longer declares CONFIG_ENTRY_VERSION")
    # The effective configuration is ``{**entry.data, **entry.options}``
    # (``HeatPumpOptimizerOptionsFlow._current``), so OPTIONS WIN. The first
    # run of this lane put these in ``data`` alone and the fixture's own
    # option default -- ``weather.home``, from the FakeEntry golden.py records
    # against -- silently replaced the weather entity the container defines.
    wiring = {
        "tibber_token": "nightly-ha-local",
        "weather_entity": "weather.ci_weather",
        "indoor_temp_entity": "sensor.ci_indoor_temperature",
        "outdoor_temp_entity": "sensor.ci_outdoor_temperature",
        "dhw_temp_entity": "sensor.ci_dhw_temperature",
        "heat_pump_power_entity": "sensor.ci_heat_pump_power",
        # No broker here, and the topic defaults are non-empty, so a
        # defaults-only entry publishes on every cycle and logs the failure at
        # ERROR. Blanked rather than tolerated: `_publish_ecl110` returns early
        # on two empty topics, which is the install-without-MQTT case.
        "ecl110_command_topic": "",
        "ecl110_displace_set_topic": "",
    }
    data = _fixture_defaults(initial_pages)
    data.update({"name": "CI"})
    data.update(wiring)
    return {
        # A well-formed ULID: Home Assistant generates entry ids with one and
        # a stray I, L, O or U here is a shape no installation has.
        "entry_id": "01JHPA9NGHTHACNTNR00000001",
        "title": "Heat Pump Optimizer",
        "version": int(version.group(1)),
        "data": data,
        "options": {**_fixture_defaults(options_pages), **wiring},
    }


def _forecast_literal(now: datetime) -> str:
    """A 48-hour hourly forecast, written into the template weather entity."""
    start = now.replace(minute=0, second=0, microsecond=0)
    rows = []
    for i in range(48):
        at = start + timedelta(hours=i)
        temp = -1.0 if 0 <= at.hour < 8 else 3.0
        rows.append(
            "{'datetime': '%s', 'condition': 'cloudy', 'temperature': %s, "
            "'wind_speed': 3.0, 'precipitation': 0.0}" % (at.isoformat(), temp)
        )
    return "[" + ", ".join(rows) + "]"


CONFIGURATION_YAML = """\
# Minimal, offline, and deliberately not `default_config`: every component
# here is one the integration reaches. The template entities stand in for the
# house sensors a real entry points at.
homeassistant:
  name: Nightly HA
  latitude: 59.33
  longitude: 18.07
  elevation: 20
  unit_system: metric
  time_zone: Europe/Stockholm
  currency: SEK

http:

logger:
  default: warning
  logs:
    custom_components.heatpump_optimizer: debug

template:
  - sensor:
      - name: "CI indoor temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        state: "21.2"
      - name: "CI outdoor temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        state: "1.5"
      - name: "CI DHW temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
        state: "48.0"
      - name: "CI heat pump power"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: "1200"
  # Trigger-based on purpose: a plain template weather entity renders
  # condition and temperature but leaves forecast_hourly_template empty, and
  # `weather.get_forecasts` then returns [] with nothing logged. The start
  # trigger fires inside hass.async_start(), before the solve this lane waits
  # for.
  - trigger:
      - platform: homeassistant
        event: start
      - platform: time_pattern
        minutes: "/5"
    weather:
      - name: "CI weather"
        condition_template: "cloudy"
        temperature_template: "{{ 1.5 }}"
        temperature_unit: "°C"
        humidity_template: "{{ 75 }}"
        forecast_hourly_template: "{{ FORECAST }}"
"""


def _stage(workdir: Path) -> tuple[Path, Path]:
    """Build the two mounts: a config directory, and the driver's own dir.

    The package is copied from the tracked tree file by file -- never the
    working directory -- so an untracked stray cannot make the container pass,
    and nothing but the package lands under ``custom_components``.
    """
    config = workdir / "config"
    driver = workdir / "opt"
    (config / CONFIG_DIR_NAME).mkdir(parents=True)
    driver.mkdir()
    listed = subprocess.run(
        ["git", "ls-files", f"{PACKAGE_REL}/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    if not listed:
        raise SystemExit(f"no tracked files under {PACKAGE_REL}/")
    for rel in listed:
        dest = config / CONFIG_DIR_NAME / Path(rel).relative_to(CONFIG_DIR_NAME)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    yaml = CONFIGURATION_YAML.replace(
        "FORECAST", _forecast_literal(datetime.now(timezone.utc))
    )
    (config / "configuration.yaml").write_text(yaml)
    shutil.copy2(Path(__file__).resolve(), driver / "nightly_ha.py")
    (driver / "seed.json").write_text(json.dumps(_seed_payload(), indent=1))
    return config, driver


def _docker(image: str, config: Path, driver: Path, budget: float, timeout: float):
    command = [
        "docker", "run", "--rm",
        "--add-host", f"{TIBBER_HOST}:127.0.0.1",
        "-e", "TZ=Europe/Stockholm",
        "-v", f"{config}:{IN_CONFIG}",
        "-v", f"{driver}:{IN_DRIVER_DIR}:ro",
        "--entrypoint", "python3",
        image,
        f"{IN_DRIVER_DIR}/nightly_ha.py", "--inside",
        "--plan-budget", str(budget),
    ]
    print("$ " + " ".join(command), flush=True)
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def _scan(checks: Checks, text: str) -> None:
    for name, needle in FORBIDDEN.items():
        hits = [line for line in text.splitlines() if needle in line]
        checks.check(
            name,
            not hits,
            f"{len(hits)} line(s)" + (f", first: {hits[0][:200]}" if hits else ""),
        )
    # A blocking-call report is a WARNING that carries a stack, not an
    # exception, so the stack after one belongs to the pin below rather than
    # to this check -- otherwise #525 would read as an integration crash.
    parts = text.split(TRACEBACK_HEAD)
    ours = [
        block
        for before, block in zip(parts, parts[1:])
        if PACKAGE_NAME in "\n".join(block.splitlines()[:40])
        and BLOCKING_REPORT not in before[-2000:]
    ]
    checks.check(
        "log:no_integration_traceback",
        not ours,
        f"{len(ours)} traceback(s) naming {PACKAGE_NAME}"
        + (f"; first:\n{TRACEBACK_HEAD}{ours[0][:600]}" if ours else ""),
    )
    # The loose anchor's matches are the population the pin is computed over,
    # so a line it claims and `BLOCKING_CALL` cannot parse silently shrinks
    # that population to nothing -- which reads as "no offenders" (#533).
    blamed = {line for line in text.splitlines() if BLOCKING_AT_OURS.search(line)}
    unparsed = sorted(line for line in blamed if not BLOCKING_CALL.search(line))
    checks.check(
        "log:blocking_report_parsed",
        not unparsed,
        f"{len(blamed)} report(s) blame this package, {len(unparsed)} unparsed"
        + (f"; first: {unparsed[0][:300]}" if unparsed else ""),
    )
    found = set(BLOCKING_CALL.findall(text))
    checks.check(
        "log:no_new_blocking_call",
        found <= KNOWN_BLOCKING,
        f"{len(found)} offender(s) seen; "
        f"new: {sorted(found - KNOWN_BLOCKING)}",
    )
    checks.check(
        "log:blocking_pin_not_stale",
        KNOWN_BLOCKING <= found,
        f"{len(KNOWN_BLOCKING)} pinned; "
        f"fixed but still pinned: {sorted(KNOWN_BLOCKING - found)}",
    )


def _report(checks: Checks, completed, config: Path) -> int:
    reported = [
        line[len(MARKER):]
        for line in completed.stdout.splitlines()
        if line.startswith(MARKER)
    ]
    checks.check(
        "run:driver_reported",
        len(reported) == 1,
        f"{len(reported)} result markers in the container's output",
    )
    # The container's own check lines, always. Without this a green run says
    # only "ALL 20 checks PASSED" and a reader cannot see WHICH twenty ran --
    # which is the shape of a lane nobody trusts and nobody reads.
    print("--- inside the container ---")
    for line in completed.stdout.splitlines():
        if line[:6] in ("  ok  ", "  FAIL", "  ..  "):
            print(line)
    inside = json.loads(reported[0]) if len(reported) == 1 else {}
    if set(inside) != set(INSIDE_CHECKS):
        missing = sorted(set(INSIDE_CHECKS) - set(inside))
        checks.check("run:exit_status", False, f"checks never ran: {missing}")
    else:
        checks.results.update(inside)
        checks.check(
            "run:exit_status",
            completed.returncode == 0,
            f"the container exited {completed.returncode}",
        )
    log = config / LOG_NAME
    _scan(checks, completed.stdout + completed.stderr + (log.read_text(errors="replace") if log.is_file() else ""))
    # Both rosters, by name. A driver that died after two checks already fails
    # above; this is the other half -- a check that stopped being reached, or
    # was renamed, on either side of the container boundary (#533).
    ran = set(checks.results) | {"run:all_checks_ran"}
    want = set(INSIDE_CHECKS) | set(OUTSIDE_CHECKS)
    checks.check(
        "run:all_checks_ran",
        ran == want,
        f"{len(ran)} of {len(want)} ran; missing: {sorted(want - ran)}; "
        f"undeclared: {sorted(ran - want)}",
    )
    failed = checks.failures()
    if failed:
        print("\n--- container output ---")
        print(completed.stdout[-20000:])
        print(completed.stderr[-20000:])
        print(f"\nFAILED: {len(failed)} of {len(checks.results)} checks: {failed}")
        return 1
    print(f"\nALL {len(checks.results)} checks PASSED")
    return 0


def _run_outside(args: argparse.Namespace) -> int:
    checks = Checks()
    # mkdtemp and rmtree(ignore_errors), not TemporaryDirectory: Home Assistant
    # runs as root in the container and leaves root-owned files (blueprints,
    # .storage) in the bind mount that the runner's user cannot remove.
    # `ignore_cleanup_errors=True` does not cover that -- its handler calls
    # _resetperms, whose chmod raises PermissionError outside the ignore path,
    # and the lane reported ALL 20 checks PASSED and then exited 1 (measured,
    # job 101525... of run 34047698688). Cleanup is not a verdict.
    tmp = Path(tempfile.mkdtemp(prefix="nightly-ha-"))
    try:
        config, driver = _stage(tmp)
        try:
            completed = _docker(args.image, config, driver, args.plan_budget, args.timeout)
        except subprocess.TimeoutExpired:
            checks.check("run:driver_reported", False, f"no result after {args.timeout}s")
            return 1
        return _report(checks, completed, config)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="homeassistant/home-assistant:stable")
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--plan-budget", type=float, default=240.0)
    parser.add_argument("--timeout", type=float, default=1500.0)
    args = parser.parse_args(argv)
    return _run_inside(args) if args.inside else _run_outside(args)


if __name__ == "__main__":
    sys.exit(main())
