from datetime import datetime

from rx.internal.basic import default_sub_comparer

from .virtualtimescheduler import VirtualTimeScheduler

class HistoricalScheduler(VirtualTimeScheduler):
    """Provides a virtual time scheduler that uses datetime for absolute time
    and timedelta for relative time."""

    def __init__(self, initial_clock=None, comparer=None):
        """Creates a new historical scheduler with the specified initial clock
        value.

        Keyword arguments:
        initial_clock -- {Number} Initial value for the clock.
        comparer -- {Function} Comparer to determine causality of events based
            on absolute time."""

        def compare_datetimes(a, b):
            return (a > b) - (a < b)

        clock = initial_clock or datetime.fromtimestamp(0)
        comparer = comparer or compare_datetimes

        super(HistoricalScheduler, self).__init__(clock, comparer)

    def now(self):
        return self.clock

    @staticmethod
    def add(absolute, relative):
        """Adds a relative time value to an absolute time value.

        Keyword arguments:
        absolute -- {datetime} Absolute virtual time value.
        relative -- {timedelta} Relative virtual time value to add.

        Returns resulting absolute virtual time sum value."""

        return absolute + relative

    def to_datetime_offset(self, absolute):
        """Converts the absolute time value to a datetime value."""

        # datetime -> datetime
        return absolute

    def to_relative(self, timespan):
        """Converts the timespan value to a relative virtual time value.

        Keyword arguments:
        timespan -- {timedelta} Time_span value to convert.

        Returns corresponding relative virtual time value."""

        # timedelta -> timedelta
        return timespan
