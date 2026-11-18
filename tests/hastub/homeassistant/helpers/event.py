import inspect


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
    # Upstream runs a plain function that is not ``@callback`` in an executor
    # thread, where the ``hass.async_*`` calls every listener here makes are
    # refused (v6.6.12: the pump arbiter's ``_changed`` raised on every pump
    # state event). The stub refuses the registration instead, so a lane sees
    # it: stricter than upstream, which accepts it and fails at dispatch.
    if not (
        getattr(action, "_hass_callback", False)
        or inspect.iscoroutinefunction(action)
    ):
        raise TypeError(f"{action!r} is neither @callback nor a coroutine function")
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


def async_call_later(hass, delay, action):
    """Record a one-shot timer on ``hass.timers`` as ``[delay, action]``.

    No lane runs a loop to fire it: a test fires a timer by calling its
    action with a time, as upstream's does at expiry. The returned cancel
    removes the entry, so an armed timer is visible and a cancelled one is
    gone; twice is harmless, as upstream's. A plain function that is neither
    ``@callback`` nor a coroutine is refused, as the state tracker refuses it.
    """
    if not (getattr(action, "_hass_callback", False) or inspect.iscoroutinefunction(action)):
        raise TypeError(f"{action!r} is neither @callback nor a coroutine function")
    timers = getattr(hass, "timers", None)
    if timers is None:
        timers = []
        hass.timers = timers
    entry = [delay, action]
    timers.append(entry)

    def _cancel():
        if entry in timers:
            timers.remove(entry)

    return _cancel
