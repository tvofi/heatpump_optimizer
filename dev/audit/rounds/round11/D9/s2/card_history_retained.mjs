// D9-s2 retained bytes, the card: rows the plan card's HistorySource holds per day of one card element's life.
//
// METRIC: after each simulated day of a long-lived card element (a wall dashboard; one
// dialog session per day in which the user pans the plan chart 10 h into the past and the
// dialog stays open for one hour of live-edge refetches), the rows retained by the
// production collaborator `HistorySource` (custom_components/heatpump_optimizer/www/
// heatpump-optimizer-card.js): the per-field sample logs (`log`), the action log
// (`actionLog`), the dedup keys (`seen`), the covered chunks (`covered`) and the memoized
// overlay points (`memo`, what `overlays()` returns). Slope = retained rows per day between
// day --warm and the last day; HistorySource's own reach is HISTORY_SPAN_MS = 48 h, so a
// bounded holder plateaus after day 2. Count key: rows the production object holds, read
// off the object (never re-derived from the fixture). The JS heap after a forced GC is
// printed beside it, provisional.
//
// RUN:   node --expose-gc dev/audit/rounds/round11/D9/s2/card_history_retained.mjs [--days 30] [--arm ARM]
//   ARM = baseline (default) | trim   (perturbation: an in-memory one-line edit of the
//         card source; `absorb`'s add() drops samples older than Date.now() - HISTORY_SPAN_MS
//         -> the log-row slope goes to ~0)
//       | nopan  (null control: the same days, the dialog never panned -> 0 rows)
// EXPECTED (baseline, 30 days, warm 3): retained_rows_slope ~ 1,9xx rows/day (exact for this
//   fixture; +-1 % across fixture edits), trim arm: log rows flat; nopan: 0.
// BASELINE: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. MACHINE: printed. Writes nothing.
// thread_factor: Node is single-threaded here; printed as process cpu / (user+system of
// the main thread) = 1.000 by construction, beside the heap number.
import fs from "fs";
import os from "os";
import vm from "vm";
import { makeCardContext, loadCard, historyApi, realisticHistory, withActuals,
         flushHistory, CARD_PATH, DEFAULT_SPACE, DEFAULT_DHW, HOUR } from "../../../../../../tests/card_rig.mjs";

const arg = (name, dflt) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : dflt;
};
const DAYS = Number(arg("days", 30));
const WARM = Number(arg("warm", 3));
const ARM = arg("arm", "baseline");
const DAY = 24 * HOUR;

let src = fs.readFileSync(CARD_PATH, "utf8");
if (ARM === "trim") {
  const anchor = "      log.sort((a, b) => a.t - b.t);\n";
  if (!src.includes(anchor)) throw new Error("trim anchor not found: the perturbation no longer applies");
  src = src.replace(anchor, anchor +
    "      { const floor = Date.now() - HISTORY_SPAN_MS; let k = 0; while (k < log.length && log[k].t < floor) k++; if (k) log.splice(0, k); }\n");
}

const { ctx } = makeCardContext();
const T0 = Date.parse("2026-01-10T00:00:00Z");
let NOW = T0;
const RealDate = Date;
ctx.Date = class ClockDate extends RealDate {
  constructor(...a) { super(...(a.length ? a : [NOW])); }
  static now() { return NOW; }
};
loadCard(ctx, src);
const HistorySource = vm.runInContext("HistorySource", ctx);

const entries = realisticHistory(T0 + (DAYS + 1) * DAY, { spanMs: (DAYS + 3) * DAY });
const api = historyApi(entries);
const states = withActuals({
  [DEFAULT_SPACE]: { state: "0", attributes: { plan_kind: "space", forecast: [] } },
  [DEFAULT_DHW]: { state: "0", attributes: { plan_kind: "dhw", forecast: [] } },
});
const host = {
  hass: { states, callApi: api.callApi },
  plan: { resolveEntity: (k) => (k === "space" ? DEFAULT_SPACE : k === "dhw" ? DEFAULT_DHW : null) },
  renderForced() {},
};
const hs = new HistorySource(host);

const count = () => {
  const logRows = Object.values(hs.log).reduce((n, a) => n + a.length, 0);
  const memo = hs.memo && hs.memo.value
    ? Object.values(hs.memo.value).reduce((n, a) => n + a.length, 0) : 0;
  return { logRows, actionRows: hs.actionLog.length, seen: hs.seen.size,
           covered: hs.covered.size, memoPoints: memo,
           total: logRows + hs.actionLog.length + hs.seen.size + memo };
};
const heap = () => { if (global.gc) { global.gc(); global.gc(); } return process.memoryUsage().heapUsed; };

const series = [];
const cpu0 = process.cpuUsage();
for (let d = 1; d <= DAYS; d++) {
  NOW = T0 + d * DAY + 18 * HOUR; // the evening session
  // One dialog session: the pan into the past, then an hour open, a render each plan step.
  for (let step = 0; step <= 4; step++) {
    const live = NOW;
    const viewStart = ARM === "nopan" ? live : live - 10 * HOUR;
    hs.ensure(viewStart, live);
    await flushHistory();
    await new Promise((r) => setImmediate(r));
    hs.overlays();
    NOW += 15 * 60000;
  }
  const c = count();
  series.push({ day: d, ...c, heap: heap() });
}

const at = (d) => series.find((r) => r.day === d);
const first = at(WARM), last = series[series.length - 1];
const n = last.day - first.day;
const slope = (k) => (last[k] - first[k]) / n;
const cpu = process.cpuUsage(cpu0);
console.log(`# machine ${os.platform()} ${os.arch()} ${os.cpus()[0].model} node ${process.version}`);
console.log(`# arm=${ARM} days=${DAYS} warm=${WARM} api_calls=${api.calls.length} unavailable=${hs.unavailable}`);
for (const r of series.filter((r) => r.day === 1 || r.day % 5 === 0 || r.day === DAYS)) {
  console.log(`# day=${r.day} log=${r.logRows} action=${r.actionRows} seen=${r.seen} covered=${r.covered} memo=${r.memoPoints} total=${r.total} heap=${r.heap}`);
}
console.log(`RESULT retained_rows_slope=${slope("total").toFixed(1)} rows/day`);
console.log(`RESULT log_rows_slope=${slope("logRows").toFixed(1)} rows/day`);
console.log(`RESULT action_rows_slope=${slope("actionRows").toFixed(1)} rows/day`);
console.log(`RESULT seen_keys_slope=${slope("seen").toFixed(1)} keys/day`);
console.log(`RESULT memo_points_slope=${slope("memoPoints").toFixed(1)} points/day`);
console.log(`RESULT covered_chunks=${last.covered} chunks (48 h span = 4-5)`);
console.log(`RESULT retained_rows_day${DAYS}=${last.total} rows`);
console.log(`RESULT heap_slope=${global.gc ? slope("heap").toFixed(0) : "n/a (run with --expose-gc)"} B/day (provisional)`);
console.log(`RESULT thread_factor=1.000`);
console.log(`RESULT cpu_s=${((cpu.user + cpu.system) / 1e6).toFixed(2)} s (provisional)`);
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`);
let swp = 0;
try { swp = Number((fs.readFileSync("/proc/vmstat", "utf8").match(/^pswpin (\d+)/m) || [0, 0])[1]); } catch { /* none */ }
console.log(`RESULT swapins=${swp}`);
