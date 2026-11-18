"""Recording stand-in for ``homeassistant.helpers.issue_registry``.

Destination: tests/hastub/homeassistant/helpers/issue_registry.py (T4a).

The v4.0.0 detectors raise repair issues (accuracy drift, compressor
degradation). What the tests need to pin is the wiring — that a trip
raises exactly one issue with the right translation key, and that
recovery or rollback deletes it — so issues land on ``hass.issues`` as
``(domain, issue_id, kwargs)`` tuples with working deletion, mirroring
how ``event.py`` records state listeners.
"""
from __future__ import annotations


class IssueSeverity:
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def async_create_issue(hass, domain, issue_id, **kwargs) -> None:
    issues = getattr(hass, "issues", None)
    if issues is None:
        issues = []
        hass.issues = issues
    # Re-creating an existing issue updates it in real HA; the stub
    # mirrors that so a chatty detector shows as ONE issue, not a pile.
    issues[:] = [i for i in issues if i[:2] != (domain, issue_id)]
    issues.append((domain, issue_id, kwargs))


def async_delete_issue(hass, domain, issue_id) -> None:
    issues = getattr(hass, "issues", None)
    if issues:
        issues[:] = [i for i in issues if i[:2] != (domain, issue_id)]
