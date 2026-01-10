from datetime import datetime, timedelta
from typing import Any
import calendar


class DateTimeTool:
    """Date and time utility tool for current time, timezone info, and date calculations."""

    name = "datetime"
    description = "Get current date/time, perform date calculations, find days between dates, calculate days until events, and get day of week information."

    # Common timezone offsets (simplified - no DST handling)
    TIMEZONES = {
        "UTC": 0,
        "GMT": 0,
        "EST": -5,
        "EDT": -4,
        "CST": -6,
        "CDT": -5,
        "MST": -7,
        "MDT": -6,
        "PST": -8,
        "PDT": -7,
        "CET": 1,
        "CEST": 2,
        "IST": 5.5,  # India
        "JST": 9,  # Japan
        "AEST": 10,  # Australia Eastern
        "AEDT": 11,
        "NZST": 12,
        "NZDT": 13,
    }

    def get_schema(self) -> dict:
        """Return OpenAI-compatible function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": [
                                "current_time",
                                "days_between",
                                "days_until",
                                "add_days",
                                "day_of_week",
                                "is_leap_year",
                                "days_in_month",
                            ],
                            "description": "The operation to perform",
                        },
                        "date1": {
                            "type": "string",
                            "description": "First date in YYYY-MM-DD format or relative (e.g., 'today', 'tomorrow')",
                        },
                        "date2": {
                            "type": "string",
                            "description": "Second date in YYYY-MM-DD format (for days_between)",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to add (for add_days operation)",
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (e.g., 'UTC', 'EST', 'PST', 'IST', 'JST')",
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year for leap year check",
                        },
                        "month": {
                            "type": "integer",
                            "description": "Month number (1-12) for days_in_month",
                        },
                    },
                    "required": ["operation"],
                },
            },
        }

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse a date string into a datetime object."""
        if not date_str:
            return None

        date_str = date_str.lower().strip()
        today = datetime.utcnow().date()

        # Handle relative dates
        if date_str == "today":
            return datetime.combine(today, datetime.min.time())
        elif date_str == "tomorrow":
            return datetime.combine(today + timedelta(days=1), datetime.min.time())
        elif date_str == "yesterday":
            return datetime.combine(today - timedelta(days=1), datetime.min.time())

        # Handle specific holidays/events (use next occurrence)
        year = today.year
        holidays = {
            "christmas": (12, 25),
            "halloween": (10, 31),
            "valentines": (2, 14),
            "valentine's": (2, 14),
            "independence day": (7, 4),
            "july 4th": (7, 4),
            "new year": (1, 1),
            "new years": (1, 1),
            "new year's": (1, 1),
        }

        for event, (month, day) in holidays.items():
            if event in date_str:
                # Check if this year's date has passed
                event_date = datetime(year, month, day).date()
                if event_date < today:
                    # Use next year
                    event_date = datetime(year + 1, month, day).date()
                date_str = event_date.strftime("%Y-%m-%d")
                break

        # Try parsing as YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            pass

        # Try other common formats
        formats = [
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def execute(
        self,
        operation: str,
        date1: str | None = None,
        date2: str | None = None,
        days: int | None = None,
        timezone: str | None = None,
        year: int | None = None,
        month: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute date/time operations.

        Args:
            operation: The operation to perform
            date1: First date (for most operations)
            date2: Second date (for days_between)
            days: Number of days (for add_days)
            timezone: Timezone string
            year: Year for leap year check
            month: Month for days_in_month

        Returns:
            Dictionary containing the result
        """
        try:
            if operation == "current_time":
                now_utc = datetime.utcnow()
                tz = timezone.upper() if timezone else "UTC"
                offset = self.TIMEZONES.get(tz, 0)

                # Apply offset
                local_time = now_utc + timedelta(hours=offset)

                return {
                    "success": True,
                    "operation": operation,
                    "timezone": tz,
                    "datetime": local_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": local_time.strftime("%Y-%m-%d"),
                    "time": local_time.strftime("%H:%M:%S"),
                    "day_of_week": local_time.strftime("%A"),
                    "utc_offset": f"UTC{'+' if offset >= 0 else ''}{offset}",
                }

            elif operation == "days_between":
                if not date1 or not date2:
                    return {
                        "success": False,
                        "error": "Both date1 and date2 are required for days_between",
                    }

                d1 = self._parse_date(date1)
                d2 = self._parse_date(date2)

                if not d1 or not d2:
                    return {
                        "success": False,
                        "error": f"Could not parse dates. Use YYYY-MM-DD format.",
                    }

                diff = (d2 - d1).days

                return {
                    "success": True,
                    "operation": operation,
                    "date1": d1.strftime("%Y-%m-%d"),
                    "date2": d2.strftime("%Y-%m-%d"),
                    "days": abs(diff),
                    "direction": "after" if diff > 0 else "before" if diff < 0 else "same day",
                }

            elif operation == "days_until":
                if not date1:
                    return {
                        "success": False,
                        "error": "date1 is required for days_until",
                    }

                target = self._parse_date(date1)
                if not target:
                    return {
                        "success": False,
                        "error": f"Could not parse date: {date1}",
                    }

                today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                diff = (target - today).days

                return {
                    "success": True,
                    "operation": operation,
                    "today": today.strftime("%Y-%m-%d"),
                    "target_date": target.strftime("%Y-%m-%d"),
                    "days_until": diff,
                    "description": f"{abs(diff)} days {'from now' if diff > 0 else 'ago' if diff < 0 else '(today)'}",
                }

            elif operation == "add_days":
                if not date1:
                    date1 = "today"
                if days is None:
                    return {
                        "success": False,
                        "error": "days parameter is required for add_days",
                    }

                base_date = self._parse_date(date1)
                if not base_date:
                    return {
                        "success": False,
                        "error": f"Could not parse date: {date1}",
                    }

                result_date = base_date + timedelta(days=days)

                return {
                    "success": True,
                    "operation": operation,
                    "start_date": base_date.strftime("%Y-%m-%d"),
                    "days_added": days,
                    "result_date": result_date.strftime("%Y-%m-%d"),
                    "day_of_week": result_date.strftime("%A"),
                }

            elif operation == "day_of_week":
                if not date1:
                    date1 = "today"

                target = self._parse_date(date1)
                if not target:
                    return {
                        "success": False,
                        "error": f"Could not parse date: {date1}",
                    }

                return {
                    "success": True,
                    "operation": operation,
                    "date": target.strftime("%Y-%m-%d"),
                    "day_of_week": target.strftime("%A"),
                    "day_number": target.weekday(),  # 0 = Monday
                    "is_weekend": target.weekday() >= 5,
                }

            elif operation == "is_leap_year":
                check_year = year if year else datetime.utcnow().year

                is_leap = calendar.isleap(check_year)

                return {
                    "success": True,
                    "operation": operation,
                    "year": check_year,
                    "is_leap_year": is_leap,
                    "days_in_february": 29 if is_leap else 28,
                }

            elif operation == "days_in_month":
                check_year = year if year else datetime.utcnow().year
                check_month = month if month else datetime.utcnow().month

                if not 1 <= check_month <= 12:
                    return {
                        "success": False,
                        "error": "Month must be between 1 and 12",
                    }

                days_count = calendar.monthrange(check_year, check_month)[1]
                month_name = calendar.month_name[check_month]

                return {
                    "success": True,
                    "operation": operation,
                    "year": check_year,
                    "month": check_month,
                    "month_name": month_name,
                    "days_in_month": days_count,
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "supported_operations": [
                        "current_time",
                        "days_between",
                        "days_until",
                        "add_days",
                        "day_of_week",
                        "is_leap_year",
                        "days_in_month",
                    ],
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"DateTime operation error: {str(e)}",
            }
