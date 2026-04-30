"""
Event Bus

This module provides the EventBus class for publishing and subscribing to
application events, and the HookEvent class containing event type constants.

Example:
    >>> from sillys.md.core import EventBus, HookEvent
    >>> bus = EventBus()
    >>> bus.subscribe(HookEvent.USER_CREATED, on_user_created)
    >>> bus.publish(HookEvent.USER_CREATED, {"user_id": 123, "email": "user@example.com"})
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass(frozen=True)
class HookEvent:
    """
    Constants for standard application events.

    These constants define the event types that can be published and
    subscribed to throughout the application.

    Attributes:
        USER_CREATED: Fired when a new user is created.
        USER_LOGGED_IN: Fired when a user successfully logs in.
        SKILL_PUBLISHED: Fired when a skill is published.
        PAYMENT_COMPLETED: Fired when a payment is successfully processed.
        MODULE_INSTALLED: Fired when a module is installed.
        MODULE_ENABLED: Fired when a module is enabled.
        MODULE_DISABLED: Fired when a module is disabled.
        MODULE_ERROR: Fired when a module encounters an error.
        SYSTEM_STARTUP: Fired when the system starts up.
        SYSTEM_SHUTDOWN: Fired when the system shuts down.
    """

    USER_CREATED = "user.created"
    USER_LOGGED_IN = "user.logged_in"
    SKILL_PUBLISHED = "skill.published"
    PAYMENT_COMPLETED = "payment.completed"
    MODULE_INSTALLED = "module.installed"
    MODULE_ENABLED = "module.enabled"
    MODULE_DISABLED = "module.disabled"
    MODULE_ERROR = "module.error"
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"

    @classmethod
    def get_all_events(cls) -> Set[str]:
        """
        Get all defined event names.

        Returns:
            Set of all event name strings.
        """
        return {
            value
            for key, value in cls.__dataclass_fields__.items()
            if isinstance(value, str)
        }

    @classmethod
    def is_valid_event(cls, event: str) -> bool:
        """
        Check if an event name is a valid HookEvent constant.

        Args:
            event: The event name to check.

        Returns:
            True if the event is a valid HookEvent, False otherwise.
        """
        return event in cls.get_all_events()


Handler = Callable[[Any], Any]


class EventBus:
    """
    Central event bus for application-wide event publishing and subscribing.

    The EventBus follows the observer pattern, allowing components to
    subscribe to specific events and be notified when those events occur.

    Attributes:
        _handlers: Dictionary mapping event names to lists of handler functions.

    Example:
        >>> bus = EventBus()
        >>>
        >>> def on_user_created(data):
        ...     print(f"New user: {data['email']}")
        >>>
        >>> bus.subscribe(HookEvent.USER_CREATED, on_user_created)
        >>> bus.publish(HookEvent.USER_CREATED, {"user_id": 1, "email": "test@example.com"})
    """

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._handlers: Dict[str, List[Handler]] = {}
        self._global_handlers: List[Handler] = []
        self._event_history: List[Dict[str, Any]] = []
        self._max_history: int = 1000
        self._paused_events: Set[str] = set()

    def subscribe(self, event: str, handler: Handler) -> None:
        """
        Subscribe a handler to a specific event.

        Args:
            event: The event name to subscribe to.
            handler: Callback function to invoke when the event is published.

        Example:
            >>> def handle_user_created(data):
            ...     print(f"User created: {data}")
            >>> bus.subscribe(HookEvent.USER_CREATED, handle_user_created)
        """
        if event not in self._handlers:
            self._handlers[event] = []
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Handler) -> bool:
        """
        Unsubscribe a handler from a specific event.

        Args:
            event: The event name to unsubscribe from.
            handler: The handler function to remove.

        Returns:
            True if the handler was found and removed, False otherwise.
        """
        if event in self._handlers and handler in self._handlers[event]:
            self._handlers[event].remove(handler)
            if not self._handlers[event]:
                del self._handlers[event]
            return True
        return False

    def subscribe_global(self, handler: Handler) -> None:
        """
        Subscribe a handler to all events.

        Global handlers are called for every event published.

        Args:
            handler: Callback function to invoke for all events.

        Example:
            >>> def log_all_events(event, data):
            ...     print(f"Event: {event}, Data: {data}")
            >>> bus.subscribe_global(log_all_events)
        """
        if handler not in self._global_handlers:
            self._global_handlers.append(handler)

    def unsubscribe_global(self, handler: Handler) -> bool:
        """
        Unsubscribe a global handler.

        Args:
            handler: The handler function to remove.

        Returns:
            True if the handler was found and removed, False otherwise.
        """
        if handler in self._global_handlers:
            self._global_handlers.remove(handler)
            return True
        return False

    def publish(self, event: str, data: Any = None) -> List[Any]:
        """
        Publish an event to all subscribed handlers.

        All handlers are called in the order they were subscribed.
        Exceptions in handlers are caught and included in the results.

        Args:
            event: The event name to publish.
            data: Optional data to pass to the handlers.

        Returns:
            List of return values from each handler (or exceptions).

        Example:
            >>> results = bus.publish(
            ...     HookEvent.USER_CREATED,
            ...     {"user_id": 1, "email": "user@example.com"}
            ... )
        """
        if event in self._paused_events:
            return []

        results: List[Any] = []

        for handler in self._global_handlers:
            try:
                result = handler(event, data)
                results.append(result)
            except Exception as e:
                results.append(e)

        handlers = self._handlers.get(event, [])
        for handler in handlers:
            try:
                result = handler(data)
                results.append(result)
            except Exception as e:
                results.append(e)

        self._record_event(event, data, results)

        return results

    def _record_event(self, event: str, data: Any, results: List[Any]) -> None:
        """
        Record an event in history.

        Args:
            event: The event name.
            data: Event data.
            results: Handler results.
        """
        record = {
            "event": event,
            "data": data,
            "results": [str(r) if isinstance(r, Exception) else r for r in results],
        }
        self._event_history.append(record)

        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

    def get_event_history(
        self,
        event: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the event history.

        Args:
            event: Optional event name to filter by.
            limit: Maximum number of records to return.

        Returns:
            List of event records in chronological order (newest last).
        """
        history = self._event_history

        if event is not None:
            history = [r for r in history if r["event"] == event]

        if limit is not None:
            history = history[-limit:]

        return history

    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()

    def pause_event(self, event: str) -> None:
        """
        Pause publishing for a specific event.

        Events published while paused are silently ignored.

        Args:
            event: The event name to pause.
        """
        self._paused_events.add(event)

    def resume_event(self, event: str) -> None:
        """
        Resume publishing for a specific event.

        Args:
            event: The event name to resume.
        """
        self._paused_events.discard(event)

    def is_paused(self, event: str) -> bool:
        """
        Check if an event is paused.

        Args:
            event: The event name to check.

        Returns:
            True if the event is paused, False otherwise.
        """
        return event in self._paused_events

    def list_subscriptions(self, event: Optional[str] = None) -> Dict[str, int]:
        """
        List all subscriptions.

        Args:
            event: Optional event name to filter by.

        Returns:
            Dictionary mapping event names to handler counts.
        """
        if event is not None:
            return {event: len(self._handlers.get(event, []))}

        return {e: len(h) for e, h in self._handlers.items()}

    def get_handlers(self, event: str) -> List[Handler]:
        """
        Get all handlers for a specific event.

        Args:
            event: The event name.

        Returns:
            List of handler functions.
        """
        return self._handlers.get(event, []).copy()

    def clear_handlers(self, event: Optional[str] = None) -> None:
        """
        Clear handlers for an event or all events.

        Args:
            event: Optional event name. If None, clears all handlers.
        """
        if event is not None:
            if event in self._handlers:
                del self._handlers[event]
        else:
            self._handlers.clear()
            self._global_handlers.clear()

    def __len__(self) -> int:
        """Return the total number of subscribed handlers."""
        return sum(len(handlers) for handlers in self._handlers.values())

    def has_subscribers(self, event: str) -> bool:
        """
        Check if an event has any subscribers.

        Args:
            event: The event name to check.

        Returns:
            True if the event has handlers, False otherwise.
        """
        return event in self._handlers and len(self._handlers[event]) > 0
