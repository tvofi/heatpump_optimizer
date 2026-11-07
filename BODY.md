# R10-GENERIC-HEAT-CURVE-PERSISTENT: default research for O5a / O5b / O5c

Probe seat, topic r10-ghc-research, tree a37c58e5f32123b4028e90983799dc2aa81816f8 (read-only; no tracked file used or changed).
Tags: **[D]** documented (manufacturer or datasheet, or a project's own docs), **[F]** forum or community claim,
**[E]** my estimate (no source). **[S]** means I only saw the claim in a search-result snippet: three hosts
did not resolve from this cloud session (energiesparhaus.at, forum.iobroker.net, community.home-assistant.io),
so I could not open them.

## Recommended defaults (summary)

| knob | default | user range | binding reason |
|---|---|---|---|
| O5a band | **3 K** | 0.5 to 5 K | Luxtronik's own user correction is ±5 K; SG-Ready style boosts are +1 to +2 offset steps (NIBE) |
| O5b writes/day | **12** (6 displace+restore episodes) | 0 (off) to 48 | below the only manufacturer write quota found (Daikin 7000/yr = 19/day); 15 y on a 100k-cycle cell |
| O5c dwell | **60 min** | 15 min to 6 h | 3 radiator response times; the SG-Ready 10 min minimum is the floor |

## 1. Non-volatile write endurance

Sources:
- python-luxtronik README, https://github.com/Bouni/python-luxtronik [D, project docs]: "The heat pump controller uses
  a NAND memory chip as persistent storage for the permanent configuration (CFI)"; it "has only a limited number of
  erase cycles"; "every change of a parameter will eventually induce some file changes on the controller, hence
  frequent parameter changes may limit the lifetime of your heat pump". The same README calls the SHI registers
  "Additional (volatile) control and status registers". So on Luxtronik every parameter-interface write does write
  through to NAND; the SHI offset does not.
- ioBroker Luxtronik2 adapter thread, https://forum.iobroker.net/topic/84954/test-luxtronik2-controller/83 [F][S]:
  v0.6.4 adds read-before-write (skips a write equal to the current value) and daily/total write counters; claims
  4 to 14 physical writes per circulation-pump activation. Unverified; host unreachable.
- Daikin: Arnold-n in https://github.com/Arnold-n/P1P2Serial/pull/87 [F, quoting D]: quotes the Daikin Modbus
  Interface DIII design guide for EKMBDXA7V1: "The number of control commands per indoor unit is limited to 7000
  per year"; says F-series parameter storage "may have been implemented in flash memory without any wear
  leveling"; the limit "protects the flash memory in the Daikin unit". The search summary of that thread adds
  that Daikin's Altherma LAN-adapter documents state no write-frequency limit [S]. Gateway
  https://github.com/budulinek/Daikin-P1P2---UDP-Gateway [D, project docs]: "max 7000 writes per year (19
  writes/day on average)"; it enforces a configurable "Daily EEPROM Write Quota" and drops commands over it.
  P1P2Serial itself rate-limited writes to 1/hour, a PR proposed 60/hour.
- NIBE: energiesparhaus.at thread
  https://www.energiesparhaus.at/forum-nibe-wp-wie-oft-kann-man-parameter-veraendern-flash-lebensdauer/55835_1
  [F][S]: quotes NIBE as 1 million writes per position; the posters work out 182/day/setting for 15 years.
  The NIBE quote itself is unverified.
- Vaillant aroTHERM (ebusd), Stiebel Eltron ISG/WPM, Mitsubishi Ecodan (CN105), Panasonic Aquarea (HeishaMon):
  **no source found** on write endurance, write-through, or rate limits. Stiebel's ISG Modbus guide
  (https://manuals.plus/stiebel-eltron/modbus-tcpip-software-extension-for-internet-service-gateway-manual)
  documents only FC06/FC16 writes and per-register min/max. Aquarea lists fault "E18 EEPROM Parameter Error" [S],
  which does not bound endurance.
- Generic parts [D, datasheets via mirrors]: Microchip 24LC256 serial EEPROM ">1,000,000 erase/write cycles"
  (older revision: "100,000 guaranteed")
  (https://ece-classes.usc.edu/ee459/library/datasheets/24LC256.pdf); STM32F412 internal flash 10 kcycles per sector,
  20-year retention at 10 kcycles / 55 °C (alldatasheet mirror of the ST datasheet); Micron SLC NAND
  (MT29F4G08ABADAH4, https://www.lcsc.com/product-detail/C5813068.html) 100,000 PROGRAM/ERASE cycles with ECC.
  NOR flash typically 10k to 100k: only a secondary blog
  (https://applied-ee.github.io/embedded/docs/foundations/memory-and-linker/flash-wear-and-persistent-storage/).

Write-through: confirmed only for Luxtronik (README) and Daikin (gateway docs, "new settings are stored in the
main Daikin controller, wearing its EEPROM"). For every other brand it is unknown; the safe assumption is yes.
Rate limits other integrations enforce: Daikin gateway 19/day quota [D]; P1P2Serial 1/h then 60/h [F];
ioBroker Luxtronik read-before-write plus a counter [F][S]. python-luxtronik and the HA Luxtronik integrations
(BenPru/Firetribe) warn but enforce no rate, only `safe` mode for unknown parameters [D].

## 2. O5b daily write budget

Life L = 15 y = 5,475 d. A per-day budget B is sustainable for a cell rated N cycles at margin m when
B <= N / (L * m). Each write is assumed to cost one erase/write of the same cell (no wear levelling) [E].

| storage (rating, tag) | N/L (m=1) | m=2 |
|---|---|---|
| serial EEPROM 1M [D] / NIBE claim 1M [F] | 182.6/day | 91/day |
| SLC NAND 100k [D] (Luxtronik class) | 18.3/day | 9.1/day |
| Daikin quota 7000/yr [D, F-series] | 19.2/day | (already a quota) |
| MCU internal flash 10k [D] | 1.83/day | 0.9/day |

Default 12/day: 12 * 5,475 = 65,700 writes, 66 % of a 100k cell (margin 1.5) and 6.6 % of a 1M cell, and
37 % below Daikin's 19/day. Persistent mode spends 2 writes per episode (baseline+displace, then restore), so
12/day = 6 episodes. The 100k row at m=2 gives 9/day; I picked 12 over 9 because NAND under a flash filesystem
very likely spreads erases over many blocks [E]. **That is an estimate; nothing I found confirms it for Luxtronik.**
Range: 0 (persistent writes off) to 48 (one per 30 min; still m=3.8 on a 1M cell, but above the only
documented manufacturer quota, so the UI should say so). A 10k-flash controller with no wear levelling
cannot be served by any useful budget (≤1.8/day); there is no default for that case, it is a per-brand fact.
Sources disagree by 100x (10k vs 1M), and no brand publishes its parameter-store technology. Mitigations every
source agrees on: read-before-write (skip an equal value) and a persistent counter.

## 3. O5a band (comfort and efficiency range of a parallel shift)

- Luxtronik user correction: Homey Luxtronik app (https://homey.app/de-at/app/com.luxtronik.heatpump/)
  "Heizungs-Temperaturkorrektur" −5 to +5 K [D, third-party app docs]; KNX forum list "E11: Sollwertverschiebung
  Heizung (°C) -5.0/5.0", "E16: Heizkurve Parallelverschiebung (°C) 5.0/35.0", "E15: Endpunkt 20.0/70.0"
  (https://knx-user-forum.de/forum/projektforen/edomi/1016455-interesse-an-lbs-für-luxtronik-2-steuerung) [F].
  So E16 is an absolute foot point (5..35 °C), not a delta: the band has to be applied around the baseline.
- SHI heating_offset −20..20 K (from the brief; not re-sourced here).
- NIBE SG Ready (manuals via manualslib, e.g. https://www.manualslib.com/manual/3348937/Nibe-S1256pc.html?page=44)
  [D]: overcapacity raises "the parallel offset for the indoor temperature" by "+2" (or room setpoint +2 °C);
  low-price mode by "+1"; cooling overcapacity "-1". NIBE offset steps are curve steps, not K [E: the step-to-K
  ratio depends on the curve slope and is not given].
- evcc Luxtronik template `heatoffset` [K], default 0.0 (https://docs.evcc.io/en/heating/alpha-innotec) [D].
- One SG-Ready description raises flow 55 → 65 °C (10 K) [F][S]; I found no standard SG-Ready Kelvin value:
  the boost is set in each controller.
The brief's "+2..+5 K" is consistent with these, except the 10 K outlier.

Derivation: band is the worst a crash can leave. The ±5 K Luxtronik user range is the largest
manufacturer-facing shift found, so 5 K is the max. Default 3 K: the midpoint of NIBE's +1/+2 steps (≈1 to 3 K
[E]) and Luxtronik's 5 K. Effect of a stuck +3 K: ≈ +1 K room for radiators, using a flow-to-room
sensitivity of 3 to 4 K flow per K room [E, rule of thumb, unsourced], and ≈ 6 to 9 % worse COP at
2 to 3 %/K flow [E, rule of thumb, unsourced]. Range 0.5 K (below a typical 1.5 to 2 K return hysteresis,
so nothing happens) to 5 K.

## 4. O5c dwell and thermal response

- Luxtronik controls on return temperature with a hysteresis, settable 0.5 to 10 K (Homey Luxtronik app [D, third
  party]), 1.5 K reported as the factory value and 2 K "as recommended" in forums [F]. A shift smaller than the
  hysteresis may cause no compressor action until the return drifts across it.
- SG-Ready signal: "active for at least 10 minutes and can only be reactivated 10 minutes after it was last
  active", "no more than 3 times a day" for blocking (https://gridx.ai/knowledge/sg-ready) [D, secondary; not
  found in a BWP original].
- Radiators: warm in "10–20 Minuten" (https://www.enpal.de/waermepumpe/thermostat-fussbodenheizung) [F, consumer
  guide]. No engineering time constant in minutes found; an ITU thesis ranks aluminium < panel < steel radiators
  (https://polen.itu.edu.tr/items/e6e4949f-a55f-4f69-8537-ec1b2365e912) [D, qualitative].
- Floor heating: 1 to 3 h (same consumer guide), 2 to 3 h (GWF Stuttgart sheet
  https://www.gwf-stuttgart.de/wp-content/uploads/Informationsblatt-Fussbodenheizung.pdf) [F]; up to 24 h
  (Dawonia tenant guide) [F]; literature 0.5 to 2 h for light floors (Weitzman 2004, cited by Ning et al.,
  https://escholarship.org/uc/item/1sx88662) and ~10 h light / ~30 h massive (Kull et al., graphical method,
  spread up to 100x) [D, literature]; review: minutes (ceiling panels) to tens of hours (TABS)
  (https://doi.org/10.1016/j.jobe.2020.102133) [D].
- Flow temperature itself follows the heat pump within minutes once the compressor responds [E]; return lags by
  loop transit plus emitter mass, the numbers above. Sources disagree by more than 10x for floor heating.

Derivation: a second write is only useful once the first has been seen. With τ ≈ 20 min for radiators [F],
3τ = 60 min reaches ~95 % (1 − e⁻³). For light floor heating τ ≈ 1 h, 60 min shows ~63 %; floor heating users
should set 2 to 3 h. Floor 15 min: above the SG-Ready 10 min minimum and less than one radiator τ. Max 6 h:
covers a 2 h τ floor at 3τ. Check against O5b: at the 60 min dwell, 24 writes/day are possible, so the
12/day budget binds first; the dwell bounds cycling within a day, the budget bounds wear.

## 5. Brands needing a different default

- **Luxtronik 2.1 with SHI (v3.90.3+, per evcc docs)**: prefer kind `offset` (volatile; no NAND wear) over
  `persistent`; use `persistent` only on 2.0/SHI-less units, and then keep 12/day or lower (NAND, unknown
  levelling, 4 to 14 physical writes per logical change claimed [F][S]).
- **Daikin (DIII/F-series via EKMBDXA)**: the 7000/yr quota counts *all* control commands; the integration's
  budget has to share it with any other writer. Altherma: no documented limit found.
- **NIBE**: offsets are curve steps, not K: O5a needs a step unit or a per-model conversion. Claimed 1M/position
  [F] would allow far more than 12/day, but it is unverified.
- **Any controller storing parameters in MCU internal flash without levelling**: ≤1.8/day at 10k cycles; no
  generic default fits. No brand found that is known to do this.
- Vaillant, Stiebel Eltron, Mitsubishi Ecodan, Panasonic Aquarea: no data; generic default applies, unvalidated.

## Gaps

No manufacturer publishes parameter-store endurance; the 12/day default rests on one documented quota (Daikin,
older systems) and datasheet classes. A measured answer needs a write counter in the field or vendor confirmation.
