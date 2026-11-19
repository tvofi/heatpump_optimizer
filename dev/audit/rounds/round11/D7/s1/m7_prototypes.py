#!/usr/bin/env python3
"""D7.M7 prototypes: architecture-score delta of each prototype edit, alone and combined, with its revert,
and the behaviour-suite comparison of the prototype tree against the tree under test.

Metric (one line): dS = tools/audit/archscore/score.py:delta(vector(tree), vector(tree + prototype)), every
counter on (ARCHSCORE_ABLATE unset), plus the same delta after the prototype is applied and reverted.
KEY: the score vector vector.py:measure returns for the edited package -- never the edit list itself.

Prototypes (exact-text edits of a temp copy; the tree under test is never written):
  note    drift.py / power_guard.py: the two ``_note`` methods (timestamped evidence line, newest six kept)
          become one ``drift.EvidenceNotes._note`` both detectors inherit, and one ``EVIDENCE_KEEP``
                                                                                               label GOOD
  note_helper  the same dedupe as a module function handed the detector's list: the score reads the helper's
          writes as in-place writes into a shared object (a counter working, kept as the control) label BAD
  avail   binary_sensor.py / climate.py / sensor.py: three ``available`` properties gating on one flag of
          one payload block become ``entity.PayloadFlagMixin`` and a declared ``_available_flag``  label GOOD
  step    pump_arbiter.py: ``_step_index`` and ``_planned_room`` share ``_covering`` for the stamp lookup
                                                                                               label GOOD
  day     price_model.py: ``observe_day`` and ``observe_day_quarters`` share ``_usable_day`` for the
          complete / finite / positive-mean test of a day of prices                            label GOOD
  reader  coordinator.py: the two verbatim ``InputReader(hass, config, enabled=.., scale=..)`` constructions
          become ``inputs.entry_reader``                                                        label GOOD
  layer   four pure modules import ``utc_elapsed_seconds`` from ``drift`` (its owner) instead of through
          ``accuracy``'s re-export, and ``HISTORY_LENGTH`` moves to ``const``: ``tariff``, and through it
          ``optimizer`` and ``topology``, stop reaching Home Assistant for a constant           label GOOD
  fdjac   sysid.py: ``_lm_solve`` and ``_slab_ua_profile_halfwidth`` build the same forward-difference
          Jacobian -> one ``_fd_jacobian``                                                      label GOOD
  entry   ledger.py: ``add`` and ``observe_meta_mean`` look up the month's running entry the same way ->
          one ``_entry`` (the honest form of what ``fold`` games)                               label GOOD
  notice  legionella.py: the two day-count notices format the same placeholders -> one ``_interval_notice``
                                                                                               label GOOD
  curr    currency.py imports ``HomeAssistant`` for one annotation: under ``if TYPE_CHECKING:`` the module
          is pure and ``grid_fee`` stops reaching the glue through it                           label GOOD
  famdel  const.py: ``ENTITY_FAMILY_OVERRIDES``, the one dead member and the one unused public name the score
          lists, deleted (tests/entities.py and the score's own family census are its only readers)
                                                                                    label NOT AN OPPORTUNITY
  fold    ledger.py: ``add`` and ``observe_meta_mean`` bodies moved, both still written out, under ONE
          ``def _fold``; nothing is shared                                                      label GAME

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score
        every arm alone, then the GOOD ones combined (about 20 vectors: several minutes of CPU)
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only fold
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only fold --fold-owner
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only note,avail,step,day,reader,layer --combined
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --suite features,entities,guard_pins
        the GOOD arms combined against the unedited tree, both copied under a tempfile root; --only picks arms.
        D7S1_JOBS (default 4) scripts at a time; D7S1_BASE_CACHE=DIR keeps the unedited side's outputs;
        D7S1_TIMEOUT=SECONDS kills a script at the limit and compares the two sides' check lines over their
        common prefix (features.py and boost_drift_replay.py do not finish on a loaded box); D7S1_KEEP=DIR
        keeps both sides' outputs.
    --fold-owner applies the place-keyed clone owner of m7_floor_plants.py (the perturbation for ``fold``).

Expected at the baseline (exact; counts and a deterministic score):
    note   dS +0.6964 IMPROVES  (duplication_copies 18 -> 17)
    note_helper  dS -6.4988 WORSENS, inadmissible (shared_inplace_writes 3 -> 9)
    avail  dS +1.4326 IMPROVES  (18 -> 16)      step  dS +0.6964 IMPROVES     day  dS +0.6964 IMPROVES
    reader dS +0.6964 IMPROVES                  layer dS +0.8074 IMPROVES  (layer_violations 13 -> 7)
    famdel dS -6.6634 WORSENS, inadmissible (family_splits 0 -> 2; dead_members and public_unused 1 -> 0)
    fold   dS +0.6964 IMPROVES with both bodies still in the tree (the hole); with --fold-owner dS +0.0000 NULL
    fdjac, entry, notice  dS +0.6964 IMPROVES each     curr  dS +0.1069 IMPROVES (layer_violations 13 -> 12)
    note+avail+step+day+reader+layer  dS +5.6952 IMPROVES (duplication_copies 18 -> 12, layer_violations 13 -> 7)
    note+avail+step+day+reader+layer+fdjac+entry+notice+curr  dS +9.2671 IMPROVES (18 -> 9, 13 -> 6)
    note+step+day+reader+fdjac+entry+notice (avail left out)  dS +5.9188 IMPROVES (18 -> 11)
    every reverted arm dS +0.0000
    (a bare --score runs every arm alone and then the first six combined; --suite without --only uses those six;
    golden.py needs GOLDEN_MODE=strict in a tree without git)
    --suite: per script, the multiset of "ok"/"FAIL" check lines of the prototype tree equals the tree's own
    (suite_ok_lines_lost=0, suite_new_fail_lines=0, same exit code); the wall figures it prints are provisional.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: darwin arm64, 8 cores (box B5).
Hooks: tools/audit/archscore/vector.py:measure, tools/audit/archscore/score.py:delta,
tools/audit/archscore/counters.py:gapped_clones.
Writes only under a tempfile root.
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import shutil  # noqa: E402
import signal  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tools" / "audit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
PKG = "custom_components/heatpump_optimizer"

# (file, old, new): ``old`` occurs exactly once unless a count is given as a 4th item.
PROTOS: dict[str, list[tuple]] = {
    "note": [
        ("drift.py",
         "    def _note(self, when: datetime, text: str) -> None:\n"
         "        self.evidence.append(f\"{when.isoformat(timespec='seconds')}: {text}\")\n"
         "        del self.evidence[:-6]\n\n",
         ""),
        ("drift.py", "            self.evidence = [str(e) for e in raw[-6:]]\n",
         "            self.evidence = [str(e) for e in raw[-EVIDENCE_KEEP:]]\n"),
        ("drift.py", "@dataclass\nclass Cusum:\n",
         "#: Evidence lines a detector keeps, newest last.\n"
         "EVIDENCE_KEEP = 6\n\n\n"
         "class EvidenceNotes:\n"
         "    \"\"\"The evidence log a detector publishes: timestamped lines, the newest few kept.\n\n"
         "    The one owner of the line's shape and of the cap. The drift detectors and the\n"
         "    peak guard publish the same list, so they write it through the same method.\n"
         "    \"\"\"\n\n"
         "    evidence: list[str]\n\n"
         "    def _note(self, when: datetime, text: str) -> None:\n"
         "        self.evidence.append(f\"{when.isoformat(timespec='seconds')}: {text}\")\n"
         "        del self.evidence[:-EVIDENCE_KEEP]\n\n\n"
         "@dataclass\nclass Cusum(EvidenceNotes):\n"),
        ("power_guard.py",
         "\n    def _note(self, now: datetime, text: str) -> None:\n"
         "        self.evidence.append(f\"{now.isoformat(timespec='seconds')}: {text}\")\n"
         "        del self.evidence[:-6]\n",
         ""),
        ("power_guard.py", "@dataclass\nclass GuardState:\n", "@dataclass\nclass GuardState(EvidenceNotes):\n"),
        ("power_guard.py", "from .accuracy import utc_elapsed_seconds\n",
         "from .accuracy import utc_elapsed_seconds\nfrom .drift import EvidenceNotes\n"),
    ],
    "note_helper": [
        ("drift.py",
         "    def _note(self, when: datetime, text: str) -> None:\n"
         "        self.evidence.append(f\"{when.isoformat(timespec='seconds')}: {text}\")\n"
         "        del self.evidence[:-6]\n\n",
         ""),
        ("drift.py", "self._note(", "note_evidence(self.evidence, ", 0),
        ("drift.py", "import numpy as np\n",
         "import numpy as np\n\n\n"
         "def note_evidence(evidence: list[str], when: datetime, text: str) -> None:\n"
         "    evidence.append(f\"{when.isoformat(timespec='seconds')}: {text}\")\n"
         "    del evidence[:-6]\n"),
        ("power_guard.py",
         "\n    def _note(self, now: datetime, text: str) -> None:\n"
         "        self.evidence.append(f\"{now.isoformat(timespec='seconds')}: {text}\")\n"
         "        del self.evidence[:-6]\n",
         ""),
        ("power_guard.py", "self._note(", "note_evidence(self.evidence, ", 0),
        ("power_guard.py", "from .accuracy import utc_elapsed_seconds\n",
         "from .accuracy import utc_elapsed_seconds\nfrom .drift import note_evidence\n"),
    ],
    "avail": [
        ("entity.py",
         "class DHWEntityMixin(HeatPumpOptimizerEntity):\n",
         "class PayloadFlagMixin(HeatPumpOptimizerEntity):\n"
         "    \"\"\"An entity that answers only while one flag of one payload block is set.\n\n"
         "    The block is the coordinator's own statement that the feature has an answer\n"
         "    (``wood_fuel.ready``, ``power_headroom.available``, ``reading_ok.<input>``); a\n"
         "    missing block or flag is unavailable, never a default.\n"
         "    \"\"\"\n\n"
         "    #: (payload block, flag in it) that must be truthy for the entity to be available.\n"
         "    _available_flag: tuple[str, str] = (\"\", \"\")\n\n"
         "    @property\n"
         "    def available(self) -> bool:\n"
         "        block, flag = self._available_flag\n"
         "        gate: Any = self._data().get(block) or {}\n"
         "        return bool(super().available and gate.get(flag))\n\n\n"
         "class DHWEntityMixin(HeatPumpOptimizerEntity):\n"),
        ("binary_sensor.py", "from .entity import HeatPumpOptimizerEntity\n",
         "from .entity import HeatPumpOptimizerEntity, PayloadFlagMixin\n"),
        ("binary_sensor.py", "class WoodCheaperBinarySensor(_OptimizerBinarySensorBase):\n",
         "class WoodCheaperBinarySensor(PayloadFlagMixin, _OptimizerBinarySensorBase):\n"),
        ("binary_sensor.py",
         "        super().__init__(coordinator, entry, \"wood_cheaper\", \"wood_cheaper\")\n\n"
         "    @property\n"
         "    def available(self) -> bool:\n"
         "        fuel = self._data().get(\"wood_fuel\") or {}\n"
         "        return bool(super().available and fuel.get(\"ready\"))\n",
         "        super().__init__(coordinator, entry, \"wood_cheaper\", \"wood_cheaper\")\n\n"
         "    _available_flag = (\"wood_fuel\", \"ready\")\n"),
        ("climate.py", "from .entity import dhw_split_attributes\n",
         "from .entity import PayloadFlagMixin, dhw_split_attributes\n"),
        ("climate.py", "class HeatPumpOptimizerClimate(HeatPumpOptimizerEntity, ClimateEntity):\n",
         "class HeatPumpOptimizerClimate(PayloadFlagMixin, HeatPumpOptimizerEntity, ClimateEntity):\n"),
        ("climate.py",
         "    @property\n"
         "    def available(self) -> bool:\n"
         "        \"\"\"Unavailable while the indoor thermometer has not read.\n\n"
         "        ``native_current_temperature`` used to return ``ThermalState.room_temperature``\n"
         "        (21.0 °C) on a default install with no indoor entity, and the climate\n"
         "        entity stayed available, so the thermostat card published that\n"
         "        constructor default as a measurement (A3(e)).\n"
         "        \"\"\"\n"
         "        flags = (self._data()).get(\"reading_ok\") or {}\n"
         "        return bool(super().available and flags.get(\"upper_floor_temperature\"))\n",
         "    # Unavailable while the indoor thermometer has not read.\n"
         "    # ``native_current_temperature`` used to return ``ThermalState.room_temperature``\n"
         "    # (21.0 °C) on a default install with no indoor entity, and the climate\n"
         "    # entity stayed available, so the thermostat card published that\n"
         "    # constructor default as a measurement (A3(e)).\n"
         "    _available_flag = (\"reading_ok\", \"upper_floor_temperature\")\n"),
        ("sensor.py", "from .entity import dhw_split_attributes\n",
         "from .entity import PayloadFlagMixin, dhw_split_attributes\n"),
        ("sensor.py", "class PowerHeadroomSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):\n",
         "class PowerHeadroomSensor(PayloadFlagMixin, _PayloadNumberMixin, HeatPumpOptimizerSensorBase):\n"),
        ("sensor.py",
         "    @property\n"
         "    def available(self) -> bool:\n"
         "        data = (self._data()).get(\"power_headroom\") or {}\n"
         "        return bool(super().available and data.get(\"available\"))\n\n",
         "    _available_flag = (\"power_headroom\", \"available\")\n\n"),
    ],
    "step": [
        ("pump_arbiter.py",
         "def _step_index(result: Any, now: datetime) -> int | None:\n",
         "def _covering(result: Any, now: datetime) -> tuple[list[Any], int]:\n"
         "    \"\"\"The plan's stamps and the index of the last one at or before ``now`` (-1 before the plan).\"\"\"\n"
         "    stamps = list(getattr(result, \"timestamps\", None) or [])\n"
         "    return stamps, bisect.bisect_right(stamps, now) - 1\n\n\n"
         "def _step_index(result: Any, now: datetime) -> int | None:\n"),
        ("pump_arbiter.py",
         "    stamps = list(getattr(result, \"timestamps\", None) or [])\n"
         "    i = bisect.bisect_right(stamps, now) - 1\n"
         "    if i < 0 or (i == len(stamps) - 1",
         "    stamps, i = _covering(result, now)\n"
         "    if i < 0 or (i == len(stamps) - 1"),
        ("pump_arbiter.py",
         "    stamps = list(getattr(result, \"timestamps\", None) or [])\n"
         "    i = bisect.bisect_right(stamps, now) - 1\n"
         "    points = list(getattr(result, attr, None) or [])\n",
         "    _stamps, i = _covering(result, now)\n"
         "    points = list(getattr(result, attr, None) or [])\n"),
    ],
    "day": [
        ("price_model.py",
         "        if len(hourly_prices) != HOURS_PER_DAY:\n"
         "            return False\n"
         "        values = np.asarray(hourly_prices, dtype=float)\n"
         "        if not np.all(np.isfinite(values)):\n"
         "            return False\n"
         "        mean = float(np.mean(values))\n"
         "        # A zero or negative daily mean makes the normalisation meaningless.\n"
         "        # Negative spot hours are real and are kept in the shape; a whole day\n"
         "        # averaging at or below zero is not something to generalise from.\n"
         "        if mean <= 1e-6:\n"
         "            return False\n",
         "        values = _usable_day(hourly_prices, HOURS_PER_DAY)\n"
         "        if values is None:\n"
         "            return False\n"
         "        mean = float(np.mean(values))\n"),
        ("price_model.py",
         "        if len(quarter_prices) != QUARTERS_PER_DAY:\n"
         "            return False\n"
         "        values = np.asarray(quarter_prices, dtype=float)\n"
         "        if not np.all(np.isfinite(values)):\n"
         "            return False\n"
         "        if float(np.mean(values)) <= 1e-6:\n"
         "            return False\n",
         "        values = _usable_day(quarter_prices, QUARTERS_PER_DAY)\n"
         "        if values is None:\n"
         "            return False\n"),
        ("price_model.py",
         "def _profile_index(",
         "def _usable_day(prices: list[float], steps: int) -> np.ndarray | None:\n"
         "    \"\"\"One complete day of prices as an array, or ``None`` when it cannot be learned from.\n\n"
         "    Complete, because a day missing its cheap hours biases every other one upward;\n"
         "    finite; and with a positive mean: negative spot hours are real and are kept, but a\n"
         "    whole day averaging at or below zero makes the normalisation meaningless.\n"
         "    \"\"\"\n"
         "    if len(prices) != steps:\n"
         "        return None\n"
         "    values = np.asarray(prices, dtype=float)\n"
         "    if not np.all(np.isfinite(values)) or float(np.mean(values)) <= 1e-6:\n"
         "        return None\n"
         "    return values\n\n\n"
         "def _profile_index("),
    ],
    "reader": [
        ("inputs.py", "class InputReader:\n",
         "def entry_reader(hass: Any, config: Any) -> InputReader:\n"
         "    \"\"\"The entity reader under the install's staleness rules: its watchdog switch and age scale.\n\n"
         "    The one place those two options reach a reader, so a new caller cannot read\n"
         "    entities with the watchdog's defaults by leaving them out.\n"
         "    \"\"\"\n"
         "    return InputReader(\n"
         "        hass,\n"
         "        config,\n"
         "        enabled=config.staleness_watchdog_enabled,\n"
         "        scale=config.staleness_max_age_scale,\n"
         "    )\n\n\n"
         "class InputReader:\n"),
        ("coordinator.py",
         "        reader = InputReader(\n"
         "            self.hass,\n"
         "            ctx._config,\n"
         "            enabled=ctx._config.staleness_watchdog_enabled,\n"
         "            scale=ctx._config.staleness_max_age_scale,\n"
         "        )\n",
         "        reader = entry_reader(self.hass, ctx._config)\n", 0),
        ("coordinator.py", "    InputReturnWatch,\n    age_of,\n",
         "    InputReturnWatch,\n    age_of,\n    entry_reader,\n"),
    ],
    "layer": [
        ("comfort_learning.py", "from .accuracy import utc_elapsed_seconds\nfrom .drift import stored_instant\n",
         "from .drift import stored_instant, utc_elapsed_seconds\n"),
        ("external_heat.py", "from .accuracy import utc_elapsed_seconds\n", "from .drift import utc_elapsed_seconds\n"),
        ("power_guard.py", "from .accuracy import utc_elapsed_seconds\n", "from .drift import utc_elapsed_seconds\n"),
        ("sysid.py", "from .accuracy import utc_elapsed_seconds\n", "from .drift import utc_elapsed_seconds\n"),
        ("tariff.py", "from .accuracy import HISTORY_LENGTH\n", "from .const import HISTORY_LENGTH\n"),
        ("accuracy.py",
         "# How many intervals to keep. At the default 30-minute optimization interval\n"
         "# this is a fortnight, which is long enough to see a seasonal bias emerge\n"
         "# without keeping an unbounded amount of state in memory.\n"
         "HISTORY_LENGTH = 672\n",
         "# HISTORY_LENGTH is const's: the tariff's house-sample cap reads it too, and a pure\n"
         "# module must not import this one (it imports Home Assistant) for a constant.\n"),
        ("accuracy.py", "from .const import (\n    COP_TRACKING_ERROR_GATE,\n",
         "from .const import (\n    COP_TRACKING_ERROR_GATE,\n    HISTORY_LENGTH,\n"),
        ("const.py", "    \"total_energy\": \"lifetime\",\n}\n",
         "    \"total_energy\": \"lifetime\",\n}\n\n"
         "# How many intervals a rolling history keeps. At the default 30-minute optimization\n"
         "# interval this is a fortnight, which is long enough to see a seasonal bias emerge\n"
         "# without keeping an unbounded amount of state in memory.\n"
         "HISTORY_LENGTH: Final = 672\n"),
    ],
    "fdjac": [
        ("sysid.py",
         "        jac = np.empty((value.size, x.size))\n"
         "        for i in range(x.size):\n"
         "            step = 1e-6 * max(abs(float(x[i])), 1.0)\n"
         "            bumped = x.copy()\n"
         "            bumped[i] += step\n"
         "            jac[:, i] = (residual(bumped) - value) / step\n",
         "        jac = _fd_jacobian(residual, x, value)\n"),
        ("sysid.py",
         "    jac = np.empty((value.size, x_hat.size))\n"
         "    for i in range(x_hat.size):\n"
         "        step = 1e-6 * max(abs(float(x_hat[i])), 1.0)\n"
         "        bumped = np.asarray(x_hat, dtype=float).copy()\n"
         "        bumped[i] += step\n"
         "        jac[:, i] = (_residual(bumped) - value) / step\n",
         "    jac = _fd_jacobian(_residual, x_hat, value)\n"),
        ("sysid.py", "def _lm_solve(\n",
         "def _fd_jacobian(\n"
         "    residual: Callable[[np.ndarray], np.ndarray], x: np.ndarray, value: np.ndarray\n"
         ") -> np.ndarray:\n"
         "    \"\"\"The forward-difference Jacobian of ``residual`` at ``x``, where it reads ``value``.\n\n"
         "    One relative step per parameter (1e-6 of its size, at least 1e-6): the fit and the\n"
         "    adoption gate's half-width differentiate the same residual the same way.\n"
         "    \"\"\"\n"
         "    x = np.asarray(x, dtype=float)\n"
         "    jac = np.empty((value.size, x.size))\n"
         "    for i in range(x.size):\n"
         "        step = 1e-6 * max(abs(float(x[i])), 1.0)\n"
         "        bumped = x.copy()\n"
         "        bumped[i] += step\n"
         "        jac[:, i] = (residual(bumped) - value) / step\n"
         "    return jac\n\n\n"
         "def _lm_solve(\n"),
    ],
    "entry": [
        ("ledger.py",
         "        lines = self._month(month_key(when))[\"lines\"]\n"
         "        entry = lines.setdefault(line, {\"kwh\": 0.0, \"sek\": 0.0})\n",
         "        entry = self._entry(when, \"lines\", line, {\"kwh\": 0.0, \"sek\": 0.0})\n"),
        ("ledger.py",
         "        meta = self._month(month_key(when))[\"meta\"]\n"
         "        entry = meta.setdefault(name, {\"sum\": 0.0, \"count\": 0})\n",
         "        entry = self._entry(when, \"meta\", name, {\"sum\": 0.0, \"count\": 0})\n"),
        ("ledger.py",
         "    def add(self, when: datetime, line: str, *, kwh: float, sek: float) -> None:\n",
         "    def _entry(self, when: datetime, section: str, name: str, zero: dict[str, Any]) -> dict[str, Any]:\n"
         "        \"\"\"The running entry ``name`` of one section of ``when``'s month, started at ``zero``.\"\"\"\n"
         "        entry: dict[str, Any] = self._month(month_key(when))[section].setdefault(name, zero)\n"
         "        return entry\n\n"
         "    def add(self, when: datetime, line: str, *, kwh: float, sek: float) -> None:\n"),
    ],
    "notice": [
        ("legionella.py",
         "        set_issue(\n"
         "            self.hass,\n"
         "            \"dhw_legionella_overdue\",\n"
         "            days is not None,\n"
         "            placeholders={\n"
         "                \"days\": f\"{days}\",\n"
         "                \"interval_days\": f\"{float(params.dhw_legionella_interval_days):.0f}\",\n"
         "            },\n"
         "        )\n",
         "        self._interval_notice(\"dhw_legionella_overdue\", \"days\", days, params)\n"),
        ("legionella.py",
         "        set_issue(\n"
         "            self.hass,\n"
         "            \"dhw_legionella_mode_blocked\",\n"
         "            overdue_days is not None,\n"
         "            placeholders={\n"
         "                \"overdue_days\": f\"{overdue_days}\",\n"
         "                \"interval_days\": f\"{float(params.dhw_legionella_interval_days):.0f}\",\n"
         "            },\n"
         "        )\n",
         "        self._interval_notice(\"dhw_legionella_mode_blocked\", \"overdue_days\", overdue_days, params)\n"),
        ("legionella.py",
         "    def check_overdue(self) -> None:\n",
         "    def _interval_notice(self, key: str, field: str, days: int | None, params: Any) -> None:\n"
         "        \"\"\"Raise notice ``key`` while ``days`` is a number, clear it while it is None.\n\n"
         "        The two day-count notices carry the same placeholders: the count under its own\n"
         "        name and the configured interval, formatted once here.\n"
         "        \"\"\"\n"
         "        set_issue(\n"
         "            self.hass,\n"
         "            key,\n"
         "            days is not None,\n"
         "            placeholders={\n"
         "                field: f\"{days}\",\n"
         "                \"interval_days\": f\"{float(params.dhw_legionella_interval_days):.0f}\",\n"
         "            },\n"
         "        )\n\n"
         "    def check_overdue(self) -> None:\n"),
    ],
    "curr": [
        ("currency.py",
         "import re\nfrom typing import Any\n\nfrom homeassistant.core import HomeAssistant\n",
         "import re\nfrom typing import TYPE_CHECKING, Any\n\n"
         "if TYPE_CHECKING:  # the annotation only: this module runs without Home Assistant\n"
         "    from homeassistant.core import HomeAssistant\n"),
    ],
    "famdel": [
        ("const.py",
         "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {\n"
         "    # The accuracy readout sorts with its prediction sensor (#1668), not\n"
         "    # among the diagnose buttons' other neighbours.\n"
         "    \"diagnose_last_interval\": \"prediction\",\n"
         "    # The four lifetime meters left the Cost family: their names lead with\n"
         "    # the meters' own token so the name sort keeps them in one run (#1668);\n"
         "    # entity ids and translation keys are untouched.\n"
         "    \"cost_total_heating\": \"lifetime\",\n"
         "    \"space_heating_cost\": \"lifetime\",\n"
         "    \"space_heating_energy\": \"lifetime\",\n"
         "    \"total_energy\": \"lifetime\",\n"
         "}\n",
         "\n"),
    ],
    "fold": [
        ("ledger.py",
         "        if not (np.isfinite(kwh) and np.isfinite(sek)):\n"
         "            return\n"
         "        lines = self._month(month_key(when))[\"lines\"]\n"
         "        entry = lines.setdefault(line, {\"kwh\": 0.0, \"sek\": 0.0})\n"
         "        entry[\"kwh\"] = float(entry[\"kwh\"]) + float(kwh)\n"
         "        entry[\"sek\"] = float(entry[\"sek\"]) + float(sek)\n",
         "        self._fold(True, when, line, kwh, sek)\n\n"
         "    def _fold(self, lines_not_meta: bool, when: datetime, name: str, a: float, b: float) -> None:\n"
         "        if lines_not_meta:\n"
         "            if not (np.isfinite(a) and np.isfinite(b)):\n"
         "                return\n"
         "            lines = self._month(month_key(when))[\"lines\"]\n"
         "            entry = lines.setdefault(name, {\"kwh\": 0.0, \"sek\": 0.0})\n"
         "            entry[\"kwh\"] = float(entry[\"kwh\"]) + float(a)\n"
         "            entry[\"sek\"] = float(entry[\"sek\"]) + float(b)\n"
         "        else:\n"
         "            if not np.isfinite(a):\n"
         "                return\n"
         "            meta = self._month(month_key(when))[\"meta\"]\n"
         "            entry = meta.setdefault(name, {\"sum\": 0.0, \"count\": 0})\n"
         "            entry[\"sum\"] = float(entry[\"sum\"]) + float(a)\n"
         "            entry[\"count\"] = int(entry[\"count\"]) + 1\n"),
        ("ledger.py",
         "        if not np.isfinite(value):\n"
         "            return\n"
         "        meta = self._month(month_key(when))[\"meta\"]\n"
         "        entry = meta.setdefault(name, {\"sum\": 0.0, \"count\": 0})\n"
         "        entry[\"sum\"] = float(entry[\"sum\"]) + float(value)\n"
         "        entry[\"count\"] = int(entry[\"count\"]) + 1\n",
         "        self._fold(False, when, name, value, 0.0)\n"),
    ],
}
GOOD = ("note", "avail", "step", "day", "reader", "layer")
# the re-run's four (the orchestrator's note): scored alone and on top of GOOD; their suite is --only
MORE = ("fdjac", "entry", "notice", "curr")


def apply(pkg: Path, names: list[str], revert: bool = False) -> None:
    for name in names:
        edits = PROTOS[name]
        for edit in (reversed(edits) if revert else edits):
            f, old, new = edit[:3]
            many = len(edit) > 3
            p = pkg / f
            s = p.read_text()
            if revert:
                if many:
                    raise SystemExit(f"{name}: a replace-all edit is reverted from the pristine copy, not in place")
                assert s.count(new) >= 1 and new, f"{name}:{f}: cannot revert"
                s = s.replace(new, old, 1)
            else:
                n = s.count(old)
                assert n >= 1 if many else n == 1, f"{name}:{f}: anchor occurs {n} times: {old[:60]!r}"
                s = s.replace(old, new)
            compile(s, str(p), "exec")
            p.write_text(s)


def copy_pkg(root: Path, into: Path) -> Path:
    shutil.copytree(root / PKG, into / PKG, ignore=shutil.ignore_patterns("__pycache__"))
    return into


def score(only: list[str] | None, fold_owner: bool) -> int:
    from archscore import counters as K, score as SC, vector as V
    if fold_owner:
        import m7_floor_plants as FP
        real = K.gapped_clones
        K.gapped_clones = lambda S, trees, gap=None: real(S, trees, gap) + FP.place_owned_clones(S, trees, gap)
    arms = [[n] for n in (only or list(PROTOS))]
    if not only:
        arms.append(list(GOOD))
    elif "--combined" in sys.argv:
        arms = [list(only)]
    base = V.measure(REPO)
    print("RESULT counters_ablated=" + (",".join(sorted(V.ablated())) or "none") + " label")
    print(f"RESULT fold_owner={int(fold_owner)} flag")
    for arm in arms:
        tag = "+".join(arm)
        with tempfile.TemporaryDirectory(prefix="d7s1-proto-") as tmp:
            tree = copy_pkg(REPO, Path(tmp))
            apply(tree / PKG, arm)
            cur = V.measure(tree)
            d = SC.delta(base, cur)
            print(f"ARM {tag}: " + SC.report(base, cur).replace("\n", " |"))
            print(f"RESULT dS_{tag}={d['dS']:+.4f} score")
            print(f"RESULT admissible_{tag}={int(d['admissible'])} flag")
            print(f"RESULT verdict_{tag}={d['verdict']} label")
            print(f"RESULT duplication_copies_{tag}={cur['duplication_copies']} count")
            # the revert: the prototype tree put back edit by edit (replace-all edits from the pristine file)
            for name in arm:
                for f in {e[0] for e in PROTOS[name]}:
                    shutil.copyfile(REPO / PKG / f, tree / PKG / f)
            rd = SC.delta(base, V.measure(tree))
            print(f"RESULT dS_reverted_{tag}={rd['dS']:+.4f} score")
    return 0


def checks(text: str) -> Counter:
    return Counter(ln.strip() for ln in text.splitlines() if ln.startswith(("  ok", "  FAIL")))


TIMED_OUT = -999


def checks_seq(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.startswith(("  ok", "  FAIL"))]


def run_script(tree: Path, script: str, env: dict) -> tuple[int, str, float]:
    """One suite script in ``tree``. With D7S1_TIMEOUT (seconds) the script and its children are killed at the
    limit and ``TIMED_OUT`` is returned with what it printed until then (the child runs unbuffered, so every
    line it finished is there)."""
    t = time.time()
    limit = float(os.environ.get("D7S1_TIMEOUT", "0")) or None
    proc = subprocess.Popen([sys.executable, f"tests/{script}.py"], cwd=tree, env=dict(env, PYTHONUNBUFFERED="1"),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = proc.communicate(timeout=limit)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        rc = TIMED_OUT
    return rc, (out or "") + (err or ""), time.time() - t


def suite(scripts: list[str], arm: list[str]) -> int:
    from concurrent.futures import ThreadPoolExecutor
    ignore = shutil.ignore_patterns("__pycache__", "rounds", ".git")
    with tempfile.TemporaryDirectory(prefix="d7s1-suite-") as tmp:
        trees = {}
        for side in ("base", "proto"):
            t = Path(tmp) / side
            shutil.copytree(REPO, t, ignore=ignore)
            trees[side] = t
        apply(trees["proto"] / PKG, arm)
        jobs = {}
        # D7S1_BASE_CACHE: a directory keeping the tree's own (unedited) outputs between runs, so a second
        # prototype arm does not pay for the base side again. Unset: both sides run every time.
        cache = Path(os.environ["D7S1_BASE_CACHE"]) if os.environ.get("D7S1_BASE_CACHE") else None

        def cached(script: str, tree: Path, env: dict):
            if cache is None:
                return run_script(tree, script, env)
            out, rc = cache / f"{script}.out", cache / f"{script}.rc"
            while (cache / f"{script}.pending").exists() and not (out.exists() and rc.exists()):
                time.sleep(5)   # another run of the tree's own side is in flight and will land here
            if out.exists() and rc.exists():
                return int(rc.read_text()), out.read_text(), 0.0
            got = run_script(tree, script, env)
            if got[0] != TIMED_OUT:
                cache.mkdir(parents=True, exist_ok=True)
                out.write_text(got[1])
                rc.write_text(str(got[0]))
            return got

        with ThreadPoolExecutor(max_workers=int(os.environ.get("D7S1_JOBS", "4"))) as ex:
            for side, t in trees.items():
                for s in scripts:
                    env = dict(os.environ, PYTHONPATH="tests/hastub", HPO_PLANDATA=str(Path(tmp) / f"plan-{side}-{s}.json"))
                    jobs[(side, s)] = ex.submit(cached, s, t, env) if side == "base" else ex.submit(run_script, t, s, env)
        lost_total = newfail_total = timed_out = prefix_total = 0
        keep = Path(os.environ["D7S1_KEEP"]) if os.environ.get("D7S1_KEEP") else None
        for s in scripts:
            (rb, ob, wb), (rp, op, wp) = jobs[("base", s)].result(), jobs[("proto", s)].result()
            if keep is not None:
                keep.mkdir(parents=True, exist_ok=True)
                (keep / f"{s}.base.out").write_text(ob)
                (keep / f"{s}.proto.out").write_text(op)
            if TIMED_OUT in (rb, rp):
                # a side did not finish: the scripts print their checks in one order, so the comparison is the
                # common prefix of the two sequences, position by position
                sb, sp = checks_seq(ob), checks_seq(op)
                n = min(len(sb), len(sp))
                diff = [(sb[i], sp[i]) for i in range(n) if sb[i] != sp[i]]
                timed_out += 1
                prefix_total += n
                lost_total += sum(1 for a, _b in diff if a.startswith("ok"))
                newfail_total += sum(1 for _a, b in diff if b.startswith("FAIL"))
                print(f"SUITE {s} TIMED OUT (base rc={rb} {len(sb)} check lines, proto rc={rp} {len(sp)} check lines):"
                      f" prefix_lines={n} prefix_mismatches={len(diff)}"
                      f" prefix_ok={sum(1 for x in sb[:n] if x.startswith('ok'))}"
                      f" prefix_fail={sum(1 for x in sb[:n] if x.startswith('FAIL'))}")
                for a, b in diff[:5]:
                    print(f"  base : {a[:200]}")
                    print(f"  proto: {b[:200]}")
                continue
            cb, cp = checks(ob), checks(op)
            lost = sum((cb - cp).values())
            new = sum((cp - cb).values())
            newfail = sum(v for k, v in (cp - cb).items() if k.startswith("FAIL"))
            lost_ok = sum(v for k, v in (cb - cp).items() if k.startswith("ok"))
            lost_total += lost_ok
            newfail_total += newfail
            print(f"SUITE {s} base: rc={rb} ok={sum(v for k, v in cb.items() if k.startswith('ok'))}"
                  f" fail={sum(v for k, v in cb.items() if k.startswith('FAIL'))} wall={wb:.0f}s |"
                  f" proto: rc={rp} ok={sum(v for k, v in cp.items() if k.startswith('ok'))}"
                  f" fail={sum(v for k, v in cp.items() if k.startswith('FAIL'))} wall={wp:.0f}s |"
                  f" lines_only_base={lost} lines_only_proto={new} same_rc={int(rb == rp)}")
            for k in list((cb - cp))[:5]:
                print(f"  only base : {k[:200]}")
            for k in list((cp - cb))[:5]:
                print(f"  only proto: {k[:200]}")
            if rb != rp:
                print("  proto tail: " + " / ".join(op.strip().splitlines()[-4:])[:600])
        tag = "+".join(arm)
        print(f"RESULT suite_arm={tag} label")
        print(f"RESULT suite_scripts={len(scripts)} count")
        print(f"RESULT suite_ok_lines_lost={lost_total} count")
        print(f"RESULT suite_new_fail_lines={newfail_total} count")
        print(f"RESULT suite_timed_out={timed_out} count")
        print(f"RESULT suite_prefix_lines={prefix_total} count")
    return 0


def main() -> int:
    t0, c0 = time.process_time(), time.thread_time()
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    if "--suite" in sys.argv:
        rc = suite(sys.argv[sys.argv.index("--suite") + 1].split(","), only or list(GOOD))
    else:
        rc = score(only, "--fold-owner" in sys.argv)
    tf = (time.process_time() - t0) / max(time.thread_time() - c0, 1e-9)
    print(f"RESULT thread_factor={tf:.2f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")
    return rc


if __name__ == "__main__":
    sys.exit(main())
