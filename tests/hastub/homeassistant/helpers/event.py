def async_track_time_interval(*a, **k): return lambda: None


def async_track_state_change_event(hass, entity_ids, action):
    """Record the subscription so tests can fire synthetic state events.

    The v4.0.0 live peak guard (#7) is the first event-driven code path in
    the integration; its decision logic is a pure function precisely so the
    tests never need a real event bus. What DOES need pinning is the wiring:
    that the listener is registered only when the feature is on, against the
    right entity, and that unsubscribing works. Registrations land on
    ``hass.state_listeners`` as ``(entity_ids, action)`` pairs; a test fires
    one by calling the action with an object shaped like an HA Event
    (``event.data["new_state"]`` etc.).
    """
    listeners = getattr(hass, "state_listeners", None)
    if listeners is None:
        listeners = []
        hass.state_listeners = listeners
    entry = (list(entity_ids), action)
    listeners.append(entry)

    def _unsub():
        if entry in listeners:
            listeners.remove(entry)

    return _unsub
