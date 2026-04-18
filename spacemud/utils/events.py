# utils/events.py
_handlers = {}


def on(event_name, handler):
    """Register a handler for an event."""
    _handlers.setdefault(event_name, []).append(handler)


def fire_event(event_name, **kwargs):
    """Fire all handlers registered for event_name."""
    for handler in _handlers.get(event_name, []):
        handler(**kwargs)
