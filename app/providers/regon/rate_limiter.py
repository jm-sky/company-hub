"""Rate limiter for REGON API."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RegonRateLimiter:
    """Rate limiter for REGON API with time-based limits."""

    # Rate limiting configuration based on REGON API limits
    RATE_LIMITS = {
        "peak": {"per_second": 3, "per_minute": 120, "per_hour": 6000},  # 8:00-16:59
        "off_peak_1": {  # 6:00-7:59, 17:00-21:59
            "per_second": 3,
            "per_minute": 150,
            "per_hour": 8000,
        },
        "off_peak_2": {  # 22:00-5:59
            "per_second": 4,
            "per_minute": 200,
            "per_hour": 10000,
        },
    }

    def __init__(self):
        self.last_request_time: Optional[datetime] = None
        self.request_count = 0

    def get_current_rate_limits(self) -> Dict[str, int]:
        """Get current rate limits based on time of day."""
        now = datetime.now()
        hour = now.hour

        if 8 <= hour <= 16:
            return self.RATE_LIMITS["peak"]
        elif (6 <= hour <= 7) or (17 <= hour <= 21):
            return self.RATE_LIMITS["off_peak_1"]
        else:
            return self.RATE_LIMITS["off_peak_2"]

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        if not self.last_request_time:
            return False

        now = datetime.now()
        time_since_last = now - self.last_request_time

        # Get current rate limits based on time of day
        current_limits = self.get_current_rate_limits()

        # Check if we need to wait (simplified check for per-second limit)
        min_interval = 1 / current_limits["per_second"]
        return time_since_last.total_seconds() < min_interval

    def get_next_available_time(self) -> Optional[datetime]:
        """Get next available time for requests."""
        if not self.is_rate_limited():
            return None

        current_limits = self.get_current_rate_limits()
        wait_time = 1 / current_limits["per_second"]

        if self.last_request_time:
            return self.last_request_time + timedelta(seconds=wait_time)

        return None

    def record_request(self):
        """Record a request for rate limiting purposes."""
        self.last_request_time = datetime.now()
        self.request_count += 1

    def get_wait_time(self) -> float:
        """Get the time to wait before the next request (in seconds)."""
        if not self.is_rate_limited():
            return 0.0

        current_limits = self.get_current_rate_limits()
        min_interval = 1 / current_limits["per_second"]

        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            return max(0.0, min_interval - elapsed)

        return 0.0
