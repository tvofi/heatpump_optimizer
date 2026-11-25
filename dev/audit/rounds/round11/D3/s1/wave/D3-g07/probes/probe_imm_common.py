"""Shared driver of box D3-g07's two _immersion_dhw_margin probes: no measurement of its own."""
import _probe_lib as L


def margin(fn, events, now):
    """_immersion_dhw_margin(now) in K on a live coordinator with immersion feedback on."""
    c = L.coord(immersion_feedback_enabled=True)
    c._immersion_events = list(events)
    return float(fn(c, now))
