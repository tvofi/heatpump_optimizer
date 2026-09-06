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
  so ``_apply_action`` and its followers are reached but write nowhere. This
  lane observes that a plan exists, not that it was carried out.
* **The config flow.** The entry is seeded into ``.storage/core.config_entries``
  from the defaults recorded in ``tests/golden/config_flow.json``, so the nine
  setup steps are not driven here. ``tests/entities.py`` and the golden lane own
  the flow itself.

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
    "entities:none_unavailable",
    "plan:optimization_result",
    "plan:last_optimization_published",
    "plan:current_action_published",
    "plan:setpoints_non_empty",
    "plan:no_solve_failure_issue",
)

# Judged by the outer half, over the container's combined output and the log
# file the run left in the bind mount. The worker child inherits the parent's
# stderr (``coordinator._ensure_worker`` passes ``stderr=None``), so its
# traceback lands on the container's stderr and never in home-assistant.log --
# which is why both streams are scanned rather than the log alone.
OUTSIDE_CHECKS = (
    "run:driver_reported",
    "run:exit_status",
    "log:no_module_not_found",
    "log:no_worker_exit",
    "log:no_integration_traceback",
)

FORBIDDEN = {
    "log:no_module_not_found": "ModuleNotFoundError",
    "log:no_worker_exit": "process worker exited rc=",
}

TRACEBACK_HEAD = "Traceback (most recent call last):"


# --- shared reporting -------------------------------------------------------


class Checks:
    """A pass/fail record that survives the container boundary as JSON."""

    def __init__(self) -> None:
        self.results: dict[str, list] = {}

    def check(self, name: str, cond: object, detail: str = "") -> bool:
        ok = bool(cond)
        self.results[name] = [ok, detail if not ok else ""]
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f"  [{detail}]" if detail and not ok else ""))
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
        f"entry state is {state} (reason: {getattr(entry, 'reason', None)})",
    )
    return entry


def _check_entities(checks: Checks, hass, entry) -> None:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    registered = er.async_entries_for_config_entry(registry, entry.entry_id)
    domains = {e.entity_id.split(".")[0] for e in registered}
    checks.check(
        "entities:registered",
        len(registered) > 0 and {"sensor", "binary_sensor", "climate"} <= domains,
        f"{len(registered)} entities across {sorted(domains)}",
    )
    unavailable = [
        e.entity_id
        for e in registered
        if (s := hass.states.get(e.entity_id)) is None or s.state == "unavailable"
    ]
    checks.check(
        "entities:none_unavailable",
        not unavailable,
        f"{len(unavailable)} unavailable: {sorted(unavailable)[:10]}",
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
    issues = ir.async_get(hass).issues
    raised = [key for (domain, key) in issues if domain == PACKAGE_NAME]
    checks.check(
        "plan:no_solve_failure_issue",
        "solve_failures" not in raised,
        f"repairs raised by the integration: {raised}",
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
    data = _fixture_defaults(initial_pages)
    data.update(
        {
            "name": "CI",
            "tibber_token": "nightly-ha-local",
            "weather_entity": "weather.ci_weather",
            "indoor_temp_entity": "sensor.ci_indoor_temperature",
            "outdoor_temp_entity": "sensor.ci_outdoor_temperature",
            "dhw_temp_entity": "sensor.ci_dhw_temperature",
            "heat_pump_power_entity": "sensor.ci_heat_pump_power",
        }
    )
    return {
        # A well-formed ULID: Home Assistant generates entry ids with one and
        # a stray I, L, O or U here is a shape no installation has.
        "entry_id": "01JHPA9NGHTHACNTNR00000001",
        "title": "Heat Pump Optimizer",
        "version": int(version.group(1)),
        "data": data,
        "options": _fixture_defaults(options_pages),
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
  - weather:
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
        checks.check(name, not hits, f"{len(hits)} line(s), first: {hits[0][:200]}" if hits else "")
    blocks = text.split(TRACEBACK_HEAD)[1:]
    ours = [b for b in blocks if PACKAGE_NAME in "\n".join(b.splitlines()[:40])]
    checks.check(
        "log:no_integration_traceback",
        not ours,
        f"{len(ours)} traceback(s) naming {PACKAGE_NAME}; first:\n"
        + (TRACEBACK_HEAD + ours[0][:600] if ours else ""),
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
    with tempfile.TemporaryDirectory() as tmp:
        config, driver = _stage(Path(tmp))
        try:
            completed = _docker(args.image, config, driver, args.plan_budget, args.timeout)
        except subprocess.TimeoutExpired:
            checks.check("run:driver_reported", False, f"no result after {args.timeout}s")
            return 1
        return _report(checks, completed, config)


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
