import subprocess, sys, pathlib
C="custom_components/heatpump_optimizer/"
M={
"M1_real_hours_utc_removed":(C+"ledger.py","        start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)\n","        pass\n"),
"M2_settled_floor_removed":(C+"ledger.py","return None if settled < MIN_COVERAGE_HOURS else max(1.0, month_hours(now) / settled)","return max(1.0, month_hours(now) / settled)"),
"M3_fallback_floor_removed":(C+"ledger.py","    if _real_hours(_month_start(now), now) < MIN_COVERAGE_HOURS:\n        return None\n",""),
"M4_savings_none_as_one":(C+"ledger.py","            if factor is None:  # the open month under MIN_COVERAGE_HOURS: no estimate yet\n                continue\n","            if factor is None:\n                factor = 1.0\n"),
"M5_waiting_for_none":(C+"sensor.py",'        return "open_month_coverage"','        return None'),
"M6_figure_currency_reversed":(C+"currency.py","return feed_currency(hass, feed) or adopted or resolve_currency(hass)","return adopted or resolve_currency(hass) or feed_currency(hass, feed)"),
"M7_price_feed_no_source_test":(C+"price_model.py","return (cfg.price_entity or None) if entity_priced(cfg) else None","return cfg.price_entity or None"),
"M8_money_resolve":(C+"config_flow.py","    currency = figure_currency(hass, price_feed(current))\n    return _number","    from .currency import resolve_currency\n    currency = resolve_currency(hass)\n    return _number"),
"M9_grid_fee_errors_resolve":(C+"config_flow.py","figure_currency(self.hass, price_feed(_current))","__import__('heatpump_optimizer.currency',fromlist=['x']).resolve_currency(self.hass)"),
"M10_usable_day_lt":(C+"price_model.py","float(np.mean(values)) <= 1e-6","float(np.mean(values)) < 1e-6"),
"M11_min_coverage_quarter":(C+"ledger.py","MIN_COVERAGE_HOURS = 24.0","MIN_COVERAGE_HOURS = 0.25"),
"M12_fee_placeholders_resolve":(C+"config_flow.py","    currency = figure_currency(hass, price_feed(current))\n    return {","    from .currency import resolve_currency\n    currency = resolve_currency(hass)\n    return {"),
"M13_waiting_for_estimated_any_dropped":(C+"sensor.py",'        if any(isinstance(row, dict) and row.get("estimated") for row in rows):\n            return None\n',''),
}
names=sys.argv[1:] or list(M)
for n in names:
    f,old,new=M[n]; p=pathlib.Path(f); s=p.read_text()
    assert s.count(old)==1,(n,s.count(old)); p.write_text(s.replace(old,new))
    r=subprocess.run(["python3","tests/_r11block.py"],env={**__import__('os').environ,"PYTHONPATH":"tests/hastub:tests"},capture_output=True,text=True,timeout=200)
    subprocess.run(["git","checkout","-q","--",f])
    fails=[l.strip() for l in (r.stdout+r.stderr).splitlines() if l.strip().startswith("FAIL") or "Error" in l]
    print(f"{n}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}")
    for l in fails[:6]: print("   ",l[:160])
