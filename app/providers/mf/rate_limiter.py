"""Rate limiter for MF API."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class MfRateLimiter:
    """Rate limiter for MF API with simple time-based limiting."""

    def __init__(self, requests_per_second: float = 1.0):
        self.rate_limit_window = timedelta(seconds=1.0 / requests_per_second)
        self.last_request_time: Optional[datetime] = None

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if not self.last_request_time:
            return False
        return datetime.now(timezone.utc) - self.last_request_time < self.rate_limit_window

    def get_next_available_time(self) -> Optional[datetime]:
        """Get next available time for requests."""
        if not self.is_rate_limited():
            return None
        return self.last_request_time + self.rate_limit_window if self.last_request_time else None

    def record_request(self):
        """Record a request for rate limiting purposes."""
        self.last_request_time = datetime.now(timezone.utc)

    def get_wait_time(self) -> float:
        """Get the time to wait before the next request (in seconds)."""
        if not self.is_rate_limited():
            return 0.0

        if self.last_request_time:
            elapsed = (datetime.now(timezone.utc) - self.last_request_time).total_seconds()
            return max(0.0, self.rate_limit_window.total_seconds() - elapsed)

        return 0.0
