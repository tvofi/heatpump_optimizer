"""Generate the docs/ figures that are pictures OF THE SHIPPED MODEL.

Every curve here is produced by calling production code -- ``ThermalModel``,
``dhw_schedule.parse_windows``, and the plan payload ``tests/plan_view.py``
writes -- so a figure cannot go on illustrating a claim the model has stopped
making. Nothing is drawn from the prose it accompanies.

Lives beside its output because ``docs/`` is INERT in ``tests/closure.py``:
nothing under ``tests/`` reads it, so it needs no closure entry and editing it
selects no gate script. (A generator under ``tools/`` would be an orphan until
``closure.py`` named it, and ``closure.py`` is a GATE_FILE.)

    python3 tests/plan_view.py                       # writes the plan payload
    PYTHONPATH=tests/hastub:tests:custom_components \
      python3 docs/img/make_model_figures.py

Run from the repository root.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "img"
for extra in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(ROOT / extra))

from profiles import house  # noqa: E402  (after sys.path)
from heatpump_optimizer.dhw_schedule import (  # noqa: E402
    hour_in_windows,
    parse_windows,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
)

# The payload path tests/plan_view.py, tests/card.mjs and the card figure
# generator all derive the same way, so a figure cannot be built from another
# checkout's stale plan.
_default_plan = "/tmp/plandata-%s.json" % hashlib.sha256(
    str(ROOT / "tests").encode()
).hexdigest()[:12]
PLAN_PATH = os.environ.get("HPO_PLANDATA", _default_plan)


def params():
    """The shipped model under the shared test profile's configuration."""
    cfg = house(two_zone=False, dhw=True)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = True
    return cfg, p


# --------------------------------------------------------------------------
# A very small SVG plotter. Hand-rolled rather than matplotlib: the gate
# installs no plotting library, and an SVG built here stays diffable.
# --------------------------------------------------------------------------

FONT = '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
INK = "#1c1c1c"
MUTED = "#5a5a5a"
GRID = "#e4e4e4"


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Panel:
    """One set of axes at a fixed place on the canvas."""

    def __init__(self, x, y, w, h, xlim, ylim):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xlim, self.ylim = xlim, ylim
        self.parts: list[str] = []

    def sx(self, v):
        lo, hi = self.xlim
        return self.x + (v - lo) / (hi - lo) * self.w

    def sy(self, v):
        lo, hi = self.ylim
        return self.y + self.h - (v - lo) / (hi - lo) * self.h

    def frame(self, xticks, yticks, xfmt=str, yfmt=str, xlabel="", ylabel=""):
        p = [
            f'<rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" '
            f'fill="#ffffff" stroke="#cfcfcf"/>'
        ]
        for t in xticks:
            gx = self.sx(t)
            p.append(
                f'<line x1="{gx:.1f}" y1="{self.y}" x2="{gx:.1f}" '
                f'y2="{self.y + self.h}" stroke="{GRID}"/>'
            )
            p.append(
                f'<text x="{gx:.1f}" y="{self.y + self.h + 15}" font-size="10.5" '
                f'text-anchor="middle" fill="{MUTED}">{esc(xfmt(t))}</text>'
            )
        for t in yticks:
            gy = self.sy(t)
            p.append(
                f'<line x1="{self.x}" y1="{gy:.1f}" x2="{self.x + self.w}" '
                f'y2="{gy:.1f}" stroke="{GRID}"/>'
            )
            p.append(
                f'<text x="{self.x - 7}" y="{gy + 3.5:.1f}" font-size="10.5" '
                f'text-anchor="end" fill="{MUTED}">{esc(yfmt(t))}</text>'
            )
        if xlabel:
            p.append(
                f'<text x="{self.x + self.w / 2:.1f}" y="{self.y + self.h + 32}" '
                f'font-size="11.5" text-anchor="middle" fill="{INK}">{esc(xlabel)}</text>'
            )
        if ylabel:
            p.append(
                f'<text x="{self.x - 44}" y="{self.y + self.h / 2:.1f}" font-size="11.5" '
                f'text-anchor="middle" fill="{INK}" '
                f'transform="rotate(-90 {self.x - 44} {self.y + self.h / 2:.1f})">'
                f"{esc(ylabel)}</text>"
            )
        self.parts = p + self.parts
        return self

    def line(self, xs, ys, color, width=2.0, dash=None, opacity=1.0):
        d = " ".join(
            ("M" if i == 0 else "L") + f" {self.sx(x):.2f} {self.sy(y):.2f}"
            for i, (x, y) in enumerate(zip(xs, ys))
        )
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
            f'{da} stroke-opacity="{opacity}"/>'
        )
        return self

    def step_fill(self, xs, ys, color, opacity=0.35):
        """A stepped filled area from the baseline, for a power schedule."""
        base = self.sy(self.ylim[0])
        pts = [f"M {self.sx(xs[0]):.2f} {base:.2f}"]
        for i, x in enumerate(xs):
            nxt = xs[i + 1] if i + 1 < len(xs) else self.xlim[1]
            pts.append(f"L {self.sx(x):.2f} {self.sy(ys[i]):.2f}")
            pts.append(f"L {self.sx(nxt):.2f} {self.sy(ys[i]):.2f}")
        pts.append(f"L {self.sx(self.xlim[1]):.2f} {base:.2f} Z")
        self.parts.append(
            f'<path d="{" ".join(pts)}" fill="{color}" fill-opacity="{opacity}" stroke="none"/>'
        )
        return self

    def band(self, x0, x1, color, opacity=0.14):
        self.parts.append(
            f'<rect x="{self.sx(x0):.1f}" y="{self.y}" '
            f'width="{self.sx(x1) - self.sx(x0):.1f}" height="{self.h}" '
            f'fill="{color}" fill-opacity="{opacity}"/>'
        )
        return self

    def hline(self, v, color, dash="5 4", width=1.4):
        gy = self.sy(v)
        self.parts.append(
            f'<line x1="{self.x}" y1="{gy:.1f}" x2="{self.x + self.w}" y2="{gy:.1f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'
        )
        return self

    def note(self, x, v, text, anchor="middle", dy=-8, size=11, color=None):
        self.parts.append(
            f'<text x="{self.sx(x):.1f}" y="{self.sy(v) + dy:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{color or INK}">{esc(text)}</text>'
        )
        return self

    def svg(self):
        return "\n".join(self.parts)


def document(w, h, title, subtitle, body, aria):
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img"\n'
        f'     aria-label="{esc(aria)}">\n'
        f"<style>text {{ font-family: {FONT}; }}</style>\n"
        f'<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>\n'
        f'<text x="22" y="28" font-size="16" font-weight="700" fill="{INK}">{esc(title)}</text>\n'
        f'<text x="22" y="46" font-size="12" fill="{MUTED}">{esc(subtitle)}</text>\n'
        f"{body}\n</svg>\n"
    )


def swatch(x, y, label, color, dash=None, width=2.0):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x}" y1="{y}" x2="{x + 22}" y2="{y}" stroke="{color}" '
        f'stroke-width="{width}"{da}/>'
        f'<text x="{x + 29}" y="{y + 4}" font-size="11.5" fill="{INK}">{esc(label)}</text>'
    )


def hhmm(h):
    return "%02d:%02d" % (int(h) % 24, round((h - int(h)) * 60))


# --------------------------------------------------------------------------
# B8 -- the hot-water demand-window timeline
# --------------------------------------------------------------------------

WINDOW_SPEC = "06:00-08:30, 17:00-22:00"
WRAP_SPEC = "22:00-02:00"


def demand_windows():
    cfg, p = params()
    if cfg["dhw_windows"] != WINDOW_SPEC:
        raise SystemExit(
            f"the shared profile's window spec is {cfg['dhw_windows']!r}, "
            f"not {WINDOW_SPEC!r}; the figure would caption the wrong frames"
        )
    windows = parse_windows(WINDOW_SPEC)
    wrapped = parse_windows(WRAP_SPEC)

    plan = json.loads(pathlib.Path(PLAN_PATH).read_text())
    fc = plan["dhw_plan"]["forecast"]
    t0 = fc[0]["t"][:10]
    hours = [
        (int(q["t"][11:13]) + int(q["t"][14:16]) / 60.0) + (0 if q["t"][:10] == t0 else 24)
        for q in fc
    ]
    temps = [q["dhw_temp"] for q in fc]
    powers = [q.get("dhw_power") or 0.0 for q in fc]

    W, H = 980, 496
    top = Panel(74, 84, W - 74 - 150, 236, (0, 24), (38, 60))
    bot = Panel(74, 352, W - 74 - 150, 54, (0, 24), (0, max(max(powers), 1.0) * 1.15))

    for a, b in windows:
        top.band(a, b, "#2f6f4f", 0.16)
        bot.band(a, b, "#2f6f4f", 0.16)
    top.frame(
        range(0, 25, 2), range(40, 61, 5),
        xfmt=lambda v: "%02d" % v, yfmt=lambda v: "%d" % v,
        ylabel="Tank temperature (°C)",
    )
    bot.frame(
        range(0, 25, 2), [0, round(max(max(powers), 1.0), 1)],
        xfmt=lambda v: "%02d" % v, yfmt=lambda v: "%.1f" % v,
        xlabel="Hour of the day", ylabel="kW",
    )
    # The curve meets the minimum line close enough to the morning frame's edge
    # that the eye cannot tell which side of it the crossing is on. State the
    # measurement instead of leaving the reader to judge by pixel.
    inside = [v for h, v in zip(hours, temps) if h < 24 and hour_in_windows(h, windows)]
    outside = [v for h, v in zip(hours, temps) if h < 24 and not hour_in_windows(h, windows)]
    if min(inside) < p.dhw_min_temp:
        raise SystemExit(
            f"the plan dips to {min(inside):.2f} °C inside a frame, below the "
            f"{p.dhw_min_temp:.1f} °C the caption promises"
        )
    top.hline(p.dhw_setpoint, "#9a7700")
    top.hline(p.dhw_min_temp, "#c0392b")
    top.line(hours, temps, "#c264d0", 2.2)
    bot.step_fill(hours, powers, "#e0544e", 0.5)
    bot.line(hours, powers, "#e0544e", 1.2)

    top.parts.append(
        f'<text x="{top.sx(0.2):.1f}" y="{top.sy(p.dhw_setpoint) - 6:.1f}" font-size="10.5" '
        f'fill="#7a5f00">setpoint {p.dhw_setpoint:.0f} °C</text>'
    )
    top.parts.append(
        f'<text x="{top.sx(0.2):.1f}" y="{top.sy(p.dhw_min_temp) - 6:.1f}" font-size="10.5" '
        f'fill="#a5322a">minimum {p.dhw_min_temp:.0f} °C — guaranteed inside a frame</text>'
    )
    top.parts.append(
        f'<text x="{top.sx(23.8):.1f}" y="{top.y + 14}" font-size="11" text-anchor="end" '
        f'fill="{MUTED}">lowest inside a frame {min(inside):.1f} °C · outside '
        f'{min(outside):.1f} °C</text>'
    )
    for a, b in windows:
        top.parts.append(
            f'<text x="{top.sx((a + b) / 2):.1f}" y="{top.y + 14}" font-size="11" '
            f'font-weight="700" text-anchor="middle" fill="#2f6f4f">'
            f"{esc(hhmm(a))}–{esc(hhmm(b))}</text>"
        )

    # The wrapping-frame strip: `22:00-02:00` is one frame the user writes and
    # two the model plans against, and only the parser can say where it splits.
    strip_y = 424
    strip = Panel(74, strip_y, W - 74 - 150, 18, (0, 24), (0, 1))
    strip.frame([], [])
    for a, b in wrapped:
        strip.band(a, b, "#2f6f4f", 0.3)

    legend_x = W - 138
    legend = "\n".join(
        [
            f'<text x="{legend_x}" y="100" font-size="11.5" font-weight="700" fill="{INK}">Read as</text>',
            swatch(legend_x, 120, "tank °C", "#c264d0", width=2.2),
            swatch(legend_x, 140, "setpoint", "#9a7700", dash="5 4", width=1.4),
            swatch(legend_x, 160, "minimum", "#c0392b", dash="5 4", width=1.4),
            f'<rect x="{legend_x}" y="173" width="22" height="11" fill="#2f6f4f" fill-opacity="0.16"/>'
            f'<text x="{legend_x + 29}" y="182" font-size="11.5" fill="{INK}">demand frame</text>',
            swatch(legend_x, 202, "hot-water kW", "#e0544e", width=2.0),
            f'<text x="{legend_x}" y="232" font-size="11" fill="{MUTED}">Outside a frame</text>',
            f'<text x="{legend_x}" y="247" font-size="11" fill="{MUTED}">there is no</text>',
            f'<text x="{legend_x}" y="262" font-size="11" fill="{MUTED}">availability</text>',
            f'<text x="{legend_x}" y="277" font-size="11" fill="{MUTED}">requirement at all,</text>',
            f'<text x="{legend_x}" y="292" font-size="11" fill="{MUTED}">so the tank drifts.</text>',
        ]
    )

    body = "\n".join(
        [
            top.svg(),
            bot.svg(),
            strip.svg(),
            f'<text x="22" y="{strip_y + 13}" font-size="11.5" fill="{INK}">'
            f"{esc(WRAP_SPEC)}</text>",
            f'<text x="22" y="{strip_y + 38}" font-size="11.5" fill="{MUTED}">'
            + esc(
                f"A frame may wrap past midnight. parse_windows splits the one you write into "
                f"the {len(wrapped)} the plan is solved against, shaded above."
            )
            + "</text>",
            legend,
        ]
    )
    return document(
        W, H,
        "Hot water only has to be there when you say so",
        f"The plan the optimizer actually produced for {esc(WINDOW_SPEC)}: pre-heated as each frame opens, "
        "held above the minimum inside it, left to drift outside.",
        body,
        "A 24-hour timeline of the hot-water tank temperature under the shipped optimizer's own plan. "
        "Two shaded demand frames, 06:00 to 08:30 and 17:00 to 22:00. The tank is heated before each frame "
        "opens and stays above the 45 degree minimum inside it, and drifts below between frames where there "
        "is no availability requirement. Underneath, the planned hot-water power, and a strip showing that "
        "the single frame 22:00-02:00 is parsed into two.",
    )


# --------------------------------------------------------------------------
# B11 -- the curve claims in docs/how-it-works.md
# --------------------------------------------------------------------------

STORE_COLORS = {"room": "#1a7a52", "buffer": "#4a90e2", "dhw": "#c264d0"}


def marginal_cop():
    """"Each store converts at its own marginal COP" -- drawn by asking it."""
    _, p = params()
    outdoor = np.linspace(-20.0, 15.0, 71)
    tank = float(p.dhw_setpoint)

    def curves(carnot: bool):
        p.cop_flow_carnot = carnot
        m = ThermalModel(p)
        return {
            "room": [m.marginal_cop(t, "room") for t in outdoor],
            "buffer": [m.marginal_cop(t, "buffer", tank) for t in outdoor],
            "dhw": [m.marginal_cop(t, "dhw", tank) for t in outdoor],
        }

    was = p.cop_flow_carnot
    off = curves(False)
    on = curves(True)
    p.cop_flow_carnot = was

    identical = max(abs(a - b) for a, b in zip(off["room"], off["buffer"]))

    W, H = 980, 480
    ymax = max(max(v) for v in list(off.values()) + list(on.values())) * 1.08
    panels = []
    for i, (title, data) in enumerate(
        ((f"No throttling valve — cop_flow_carnot off", off),
         (f"Throttling valve — cop_flow_carnot on, tank at {tank:.0f} °C", on))
    ):
        ax = Panel(70 + i * 470, 108, 380, 244, (-20, 15), (0, ymax))
        ax.frame(
            range(-20, 16, 5), [0, 1, 2, 3, 4, 5],
            xfmt=lambda v: "%d" % v, yfmt=lambda v: "%d" % v,
            xlabel="Outdoor temperature (°C)",
            ylabel="Marginal COP" if i == 0 else "",
        )
        for key in ("room", "buffer", "dhw"):
            ax.line(
                outdoor, data[key], STORE_COLORS[key],
                width=3.4 if key == "buffer" else 2.0,
                opacity=0.5 if key == "buffer" else 1.0,
            )
        panels.append(
            f'<text x="{70 + i * 470}" y="98" font-size="12.5" font-weight="700" '
            f'fill="{INK}">{esc(title)}</text>\n' + ax.svg()
        )

    legend_y = 410
    legend = "\n".join(
        [
            swatch(70, legend_y, "building mass (room, slab, upper, lower) — the plain space curve", "#1a7a52"),
            swatch(70, legend_y + 20,
                   "buffer tank — flow-derated at its own temperature, drawn thick so the plain "
                   "curve shows through it", "#4a90e2", width=3.4),
            swatch(70, legend_y + 40, "DHW tank — compute_cop_dhw at the tank temperature", "#c264d0"),
        ]
    )

    return document(
        W, H,
        "One kWh costs a different amount depending on where it goes",
        f"ThermalModel.marginal_cop, asked directly. Gate off, the buffer curve is not close to the plain "
        f"space curve — it is the same number at every point (largest difference {identical:g}).",
        "\n".join(panels) + "\n" + legend,
        "Two plots of marginal COP against outdoor temperature from minus 20 to plus 15 degrees. "
        "Left, with the throttling-valve gate off: the buffer-tank curve lies exactly on the building-mass "
        "curve, and only the hot-water tank sits lower. Right, with the gate on: the buffer tank is derated "
        "below the building-mass curve because it charges at its own temperature.",
    ), identical


def store_decay():
    """Measured, not re-derived: perturb the shipped tank simulation.

    ``docs/how-it-works.md`` states the linear program's store as ``a kWh
    delivered k steps ago still contributes (1 - UA*dt/C)^k / C degrees
    today``. Rather than plotting that expression -- which would make the
    figure agree with the prose whatever the code does -- this runs
    ``ThermalModel.simulate_dhw_step`` forward twice, once with a single small
    heat injection, and plots the difference. The formula is what the curve
    should look like; the curve is what the model does.

    The heat is injected as ``dhw_power_thermal`` because the claim is about a
    kWh *delivered into the tank*. ``simulate_dhw_only`` would be the shorter
    call and the wrong one: ``extend_dhw_temps`` multiplies its schedule by
    ``compute_cop_dhw`` first, so its input is electricity and the curve would
    carry the COP at whatever outdoor temperature was chosen -- 2.16x here, an
    entirely invented feature of the plot.
    """
    _, p = params()
    m = ThermalModel(p)
    dt = 0.25
    n = 96
    draw = 0.0                   # nobody drawing: standby loss alone
    kwh = 0.05                   # small enough that no clamp or ceiling engages
    start = 50.0

    def run(inject: float) -> list[float]:
        temp = start
        out = [temp]
        for i in range(n):
            temp = m.simulate_dhw_step(
                dhw_temp=temp,
                dhw_power_thermal=(inject / dt) if i == 0 else 0.0,
                hour_of_day=0.0,
                dt_hours=dt,
                draw_power=draw,
            )
            out.append(temp)
        return out

    base = np.asarray(run(0.0))
    hot = np.asarray(run(kwh))
    # Step 0 is the state before the injection, identical in both runs; the
    # kWh is in the tank from step 1 on, so that is lag zero.
    influence = (hot - base)[1:] / kwh      # deg C still present per thermal kWh
    lag_hours = np.arange(len(influence)) * dt

    ceiling = float(influence[0])
    if not np.all(np.diff(influence) <= 1e-9):
        raise SystemExit("the measured influence is not monotonically decaying")
    retained = float(influence[-1] / ceiling)

    W, H = 760, 418
    ax = Panel(84, 92, W - 84 - 40, 214, (0, 24), (0, ceiling * 1.1))
    ax.frame(
        range(0, 25, 4), [0, ceiling / 2, ceiling],
        xfmt=lambda v: "%d h" % v, yfmt=lambda v: "%.2f" % v,
        xlabel="How long ago the kWh was delivered",
        ylabel="°C of it still in the tank, per kWh",
    )
    ax.line(lag_hours, influence, "#c264d0", 2.4)
    end = float(lag_hours[-1])
    ax.parts.append(
        f'<line x1="{ax.sx(end):.1f}" y1="{ax.sy(influence[-1]):.1f}" '
        f'x2="{ax.sx(end):.1f}" y2="{ax.sy(0):.1f}" stroke="{MUTED}" stroke-width="1" '
        f'stroke-dasharray="3 3"/>'
    )
    ax.note(
        end - 0.5, influence[-1],
        f"{retained * 100:.0f}% of it is still there a day later",
        anchor="end", dy=-10,
    )

    return document(
        W, H,
        "Heat bought early is still there later, minus what leaked",
        "Measured by perturbing ThermalModel.simulate_dhw_step, not by plotting the formula.",
        ax.svg()
        + f'\n<text x="84" y="{H - 42}" font-size="11.5" fill="{MUTED}">'
        + esc(
            f"One extra thermal kWh at hour 0, nobody drawing. Tank {p.dhw_tank_volume:.0f} L: "
            f"C = {p.dhw_tank_thermal_mass:.3f} kWh/°C, UA = "
            f"{p.dhw_tank_heat_loss_coefficient * 1000:.1f} W/°C."
        )
        + "</text>"
        + f'\n<text x="84" y="{H - 24}" font-size="11.5" fill="{MUTED}">'
        + esc(
            "It is why buying early already costs more than buying late, with no pre-heat cap."
        )
        + "</text>",
        "A decay curve: the degrees per kWh still present in the hot-water tank against how long ago the "
        "kWh was delivered, measured from the shipped tank simulation over 24 hours.",
    ), ceiling, retained


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    written = []

    svg = demand_windows()
    (OUT / "dhw-demand-windows.svg").write_text(svg)
    written.append(("dhw-demand-windows.svg", len(svg)))

    svg, identical = marginal_cop()
    (OUT / "marginal-cop.svg").write_text(svg)
    written.append(("marginal-cop.svg", len(svg)))
    print(f"marginal_cop: max |buffer - room| with the gate off = {identical:.3e}")

    svg, ceiling, retained = store_decay()
    (OUT / "dhw-store-decay.svg").write_text(svg)
    written.append(("dhw-store-decay.svg", len(svg)))
    print(
        f"store decay: peak {ceiling:.4f} degC per thermal kWh (1/C), "
        f"{retained * 100:.1f}% still present after 24 h"
    )

    for name, size in written:
        print(f"{name}: {size} bytes")
    print("MODEL FIGURES WRITTEN")
