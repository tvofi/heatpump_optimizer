
window.__applyProposal = (dark) => {
  const card = window.__card, root = card.shadowRoot;
  const T = dark
    ? { accent: '#4fb3f0', heat: '#d2601f', surface2: '#242a30', ok: '#1fad6b', okbg: 'rgba(31,173,107,.14)', chipbg: 'rgba(255,255,255,.04)' }
    : { accent: '#026aa8', heat: '#d2601f', surface2: '#f7f9fb', ok: '#1c7350', okbg: 'rgba(28,115,80,.10)', chipbg: 'rgba(15,34,51,.02)' };
  const css = `
  :host { --hpo-accent: var(--hpo-accent-theme, ${T.accent}); --hpo-heat: ${T.heat};
          --hpo-surface-2: ${T.surface2}; --hpo-text: var(--primary-text-color, ${dark ? '#e1e1e1' : '#212121'});
          --hpo-space-1: 4px; --hpo-space-2: 8px; --hpo-space-3: 12px; --hpo-space-4: 16px; --hpo-space-5: 24px;
          --hpo-radius-s: 6px; --hpo-radius-m: 12px; --hpo-radius-pill: 999px;
          --hpo-text-xs: 12px; --hpo-text-sm: 13px; --hpo-text-md: 15px; --hpo-text-lg: 18px; }
  .header { display:flex; align-items:center; gap: var(--hpo-space-3); padding: var(--hpo-space-3) var(--hpo-space-4) var(--hpo-space-3) !important; margin:0 !important }
  .header .title { color: var(--hpo-text); }
  .header .title { font-size: var(--hpo-text-lg); font-weight: 600; letter-spacing: .1px; flex: 0 1 auto; }
  .hpo-mark { width: 28px; height: 28px; flex: none; }
  .hpo-pill { display:inline-flex; align-items:center; gap:6px; font-size: var(--hpo-text-xs); font-weight:500;
              padding: 3px 10px 3px 8px; border-radius: var(--hpo-radius-pill); color: ${T.ok}; background: ${T.okbg}; margin-right:auto; white-space:nowrap }
  .hpo-pill::before { content:''; width:7px; height:7px; border-radius:50%; background:${T.ok}; }
  .hpo-stats { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: var(--hpo-space-2); padding: 0 var(--hpo-space-4) var(--hpo-space-3); }
  .hpo-stat { background: var(--hpo-surface-2); border-radius: var(--hpo-radius-m); padding: var(--hpo-space-2) var(--hpo-space-3); min-width:0 }
  .hpo-stat .k { font-size: var(--hpo-text-xs); color: var(--secondary-text-color, #727272); white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
  .hpo-stat .v { color: var(--hpo-text); font-size: var(--hpo-text-lg); font-weight:600; font-variant-numeric: tabular-nums; margin-top:2px; white-space:nowrap }
  .hpo-stat .v small { font-size: var(--hpo-text-xs); font-weight:500; color: var(--secondary-text-color, #727272); margin-left:3px }
  .hpo-stat.accent .v { color: var(--hpo-accent); }
  .legend { gap: 6px !important; padding: 0 var(--hpo-space-4) !important; flex-wrap: wrap; }
  .legend .chip { font-size: var(--hpo-text-sm) !important; min-height: 28px !important; padding: 2px 10px 2px 8px !important;
                  border-radius: var(--hpo-radius-pill) !important; background: ${T.chipbg}; line-height: 1.2; flex: none; white-space: nowrap }
  .legend .chip .dot { width: 8px !important; height: 8px !important; margin-right: 6px !important }
  .legend .legend-note { order: 99; flex-basis:100%; font-size: var(--hpo-text-xs) !important; color: var(--secondary-text-color,#727272) !important; margin: 2px 0 0 !important }
  .legend .legend-note::before { content:''; display:inline-block; width:18px; margin-right:6px; vertical-align:middle; border-top: 1.5px dashed currentColor; }
  path.series[data-key="price"][stroke="none"] { fill-opacity: .16; }
  path.series[data-key="solar"][stroke="none"] { fill-opacity: .10; }
  @media (max-width: 600px) {
    .legend { flex-wrap: nowrap !important; overflow-x: auto; scrollbar-width: none;
              -webkit-mask-image: linear-gradient(90deg, #000 88%, transparent); mask-image: linear-gradient(90deg, #000 88%, transparent) }
    .legend .legend-note { display:none }
    .hpo-stats { grid-template-columns: repeat(2, minmax(0,1fr)) }
    .hpo-stat .v { font-size: var(--hpo-text-md) }
  }`;
  const st = document.createElement('style'); st.textContent = css; root.appendChild(st);
  const header = root.querySelector('.header'), title = root.querySelector('.title');
  const m = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  m.setAttribute('viewBox', '0 0 48 48'); m.setAttribute('class', 'hpo-mark'); m.setAttribute('aria-hidden', 'true');
  m.innerHTML = `<path d="M20 22 V26 H27 V35 H36 V22 Z" fill="${T.heat}"/><path d="M6 12 H13 V19 H20 V26 H27 V35 H36 V13 H42" fill="none" stroke="${T.accent}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>`;
  header.insertBefore(m, title);
  const pill = document.createElement('span'); pill.className = 'hpo-pill'; pill.textContent = 'Heating now';
  title.after(pill);
  const d = window.__stats;
  const stats = document.createElement('div'); stats.className = 'hpo-stats';
  stats.innerHTML = `<div class="hpo-stat accent"><div class="k">Price now</div><div class="v">${d.price}<small>SEK/kWh</small></div></div>
    <div class="hpo-stat"><div class="k">Planned heat</div><div class="v">${d.kwh}<small>kWh</small></div></div>
    <div class="hpo-stat"><div class="k">Plan cost</div><div class="v">${d.cost}<small>SEK</small></div></div>
    <div class="hpo-stat"><div class="k">Indoor</div><div class="v">${d.indoor}<small>°C</small></div></div>`;
  header.after(stats);
};
