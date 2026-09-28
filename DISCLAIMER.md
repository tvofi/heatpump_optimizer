# Disclaimer

The full disclaimer for the Heat Pump Optimizer integration. The
[README](README.md) carries a condensed summary of it; this is the full text.

**Read this before installing.** This software controls real heating equipment
and makes claims about money. Both deserve care.

**No warranty.** This project is provided "as is" and "as available" under the
MIT licence, with no warranty or condition of any kind, express or implied,
including but not limited to warranties of merchantability, fitness for a
particular purpose, title, accuracy, and non-infringement. There is no
guarantee that it works at all, that it works as described, that it will
continue to work, or that any defect will ever be corrected. See
[LICENSE](LICENSE) for the full text.

**Any use of this software is entirely at your own risk.** You accept that risk
in full, and in its entirety, the moment you install or run it.

**No responsibility, no liability.** The authors and contributors accept **no
responsibility whatsoever** for anything arising out of, or in any way
connected with, this software — its use, its misuse, its inability to be used,
its effects, its behaviour, its functions or its failure to function.

This exclusion is intended to be as broad as the law allows. It covers every
kind of loss or damage, whether direct, indirect, incidental, special,
exemplary, punitive or consequential, and regardless of the legal theory
advanced — contract, tort, negligence, strict liability, statute or otherwise —
and applies even if the possibility of such damage was known or foreseeable. It
includes, without limitation: damage to your heat pump, boiler, tanks, pipes,
controller, sensors, wiring or any other equipment; damage to your building or
its contents, including from freezing, overheating, condensation, water or
fire; loss of heating or hot water, and any discomfort, disruption or
displacement resulting from it; injury or illness, including any arising from
water temperature or hygiene; excessive electricity consumption, unexpected
bills, missed savings, tariff penalties or peak charges; wear, shortened
service life, or voided warranties on your equipment; corrupted or lost
configuration, history or data; time and cost spent installing, diagnosing,
repairing or removing it; and any decision you make in reliance on anything
this software calculates, predicts, reports or displays.

**It is your decision and your risk.** Any use of this software, and anything
you do with it or because of it, is entirely and exclusively at your own risk.
You alone are responsible for deciding whether to install it, for how you
configure it, for what you allow it to control, for supervising what it does,
and for making sure independent protections remain in place. Nobody is obliged
to provide support, fixes, updates or maintenance of any kind. If any part of
this exclusion is held unenforceable, the remainder continues to apply and
liability is limited to the smallest amount permitted by law.

**It is not a safety device.** Do not rely on it for frost protection, for
keeping pipes from freezing, for legionella control, or for anything else where
failure has consequences. It can stop working for many ordinary reasons — a
lost network connection, an expired API token, a Home Assistant upgrade, a
crashed process, a dead sensor — and when it does, your heat pump is left
wherever it was last told to be. Keep your heat pump's own thermostats,
limits and safety controls active and correctly configured. They, not this
integration, are what protect your home.

**Anti-legionella is a convenience, not a compliance feature.** The cycle
scheduled here is a best effort based on a modelled tank temperature at one
sensor. It is not a substitute for following your local regulations and your
tank manufacturer's guidance on hot water hygiene, and it cannot detect
stratification, dead legs or a mis-sited sensor. If in doubt, keep an
independent legionella cycle configured on the tank itself.

**Savings figures are estimates.** Every cost, saving and percentage this
integration reports is the output of a model, computed against forecast prices
and forecast weather. Real savings depend on your building, your tariff, your
heat pump, your habits and the weather actually occurring. Nothing here is a
guarantee or a financial projection, and the baseline it compares against is a
simulated conventional thermostat following the same comfort schedule —
only the hot-water half of the baseline is always-on — rather than a
measurement of what you would otherwise have spent. Treat the numbers as a
guide to relative decisions, not as an accounting record.

**The model learns, and can be wrong.** Several parameters are estimated from
your own house over time. A faulty or mis-configured sensor can push those
estimates somewhere unhelpful, and the optimizer will then plan confidently
against a wrong model. The input watchdog and the guard thresholds exist to
limit that, but they cannot eliminate it. Check the diagnostic sensors
occasionally, especially in the first weeks.

**Your equipment, your responsibility.** Driving a heat pump or an external
controller over MQTT may affect its warranty, may interact badly with its own
internal logic, and may be subject to local regulation. Confirm that what you
are doing is permitted and sensible for your specific hardware before enabling
control features. Cycling a compressor more than its manufacturer intends can
shorten its life.

**No affiliation.** This project is not affiliated with, endorsed by, or
supported by Home Assistant, Nabu Casa, Tibber, Nord Pool, Danfoss, Open-Meteo,
or any heat pump manufacturer. Product and company names are used only to
describe what the integration interoperates with. Use of third-party APIs is
subject to those providers' own terms, and their availability, accuracy and
pricing are outside this project's control.

