// Reviewer's own differential: load each card in a vm with DOM stubs, compare outputs of the touched functions.
import fs from 'fs'; import vm from 'vm';
const [,, baseF, headF, perturb] = process.argv;
function load(f, pert) {
  let src = fs.readFileSync(f, 'utf8');
  if (pert) { const a = 'return `${p.x.toFixed(2)} ${p.y.toFixed(2)}`;'; if (!src.includes(a)) throw 'no perturb anchor'; src = src.replace(a, 'return `${p.x.toFixed(3)} ${p.y.toFixed(2)}`;'); }
  const noop = () => {}; const P = new Proxy(function(){}, { get: (t,k)=> k===Symbol.toPrimitive? ()=>'' : P, apply: ()=>P, construct: ()=>P });
  const ctx = { console, HTMLElement: class {}, customElements: { define: noop, get: noop, whenDefined: () => Promise.resolve() }, window: { customCards: [] , addEventListener: noop, matchMedia: () => ({ matches: false, addEventListener: noop })}, document: P, localStorage: { getItem: () => null, setItem: noop }, navigator: { language: 'en' }, setTimeout, clearTimeout, requestAnimationFrame: noop, ResizeObserver: class { observe(){} }, Intl, Date, Math, JSON };
  vm.createContext(ctx);
  vm.runInContext(src + `\n;globalThis.__x = { formatWindows, quietOverlapProblem, steppedLine, smoothLine, Legend, WhatIfPanel, setupSvgHtml, CARD_TAG };`, ctx);
  return ctx.__x;
}
const B = load(baseF), H = load(headF, perturb === 'perturb');
const out = []; const cmp = (name, f) => { let b, h; try { b = f(B); } catch (e) { b = 'ERR ' + e.message; } try { h = f(H); } catch (e) { h = 'ERR ' + e.message; } out.push([name, JSON.stringify(b) === JSON.stringify(h), b]); };
const specs = ['', '22:00-06:00', '07:00-09:00', 'mon-fri 12:00-13:30', 'sat,sun 05:00-08:00, 23:00-23:30', 'daily 06:00-07:00'];
for (const ws of [[], [{start:'07:00',end:'09:00'}], [{days:'mon-fri',start:'22:00',end:'06:00'},{days:'daily',start:'12:00',end:'13:00'}]]) cmp('formatWindows '+JSON.stringify(ws), X => X.formatWindows(ws));
let clashes = 0;
for (const s of specs) for (const o of specs) for (const d of specs) { cmp(`qop ${s}|${o}|${d}`, X => X.quietOverlapProblem(s, o, d)); if (out.at(-1)[2]) clashes++; }
for (const n of [1,2,3,4,7,20]) { const pts = Array.from({length:n}, (_, i) => ({ x: i*13.337, y: Math.sin(i)*40.1234+50 })); cmp('stepped'+n, X => X.steppedLine(pts)); cmp('smooth'+n, X => X.smoothLine(pts)); }
const cfgs = [{space_entity:'sensor.a',dhw_entity:'sensor.b',hours:24},{space_entity:'sensor.a',dhw_entity:'sensor.b',title:'T',hours:48}];
for (const c of cfgs) { cmp('storageKey', X => X.Legend.prototype.storageKey.call(X.Legend.prototype, c)); }
const differ = out.filter(r => !r[1]);
console.log(`RESULT ${out.length} cases, ${differ.length} differ, ${clashes} clash messages${perturb?' (perturbed)':''}`);
const errs=out.filter(r=>String(r[2]).startsWith("ERR")).length; console.log("RESULT errors", errs, "sample:", out.find(r=>r[0].startsWith("qop")&&r[2])?.[2], "|", out.filter(r=>r[0]==="storageKey").map(r=>r[2]).join(" ; "));
for (const d of differ.slice(0,3)) console.log('  differ:', d[0]);
