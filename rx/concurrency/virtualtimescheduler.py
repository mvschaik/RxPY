import logging

from rx.internal import PriorityQueue, ArgumentOutOfRangeException

from .scheduler import Scheduler
from .scheduleditem import ScheduledItem
from .scheduleperiodicrecursive import SchedulePeriodicRecursive

log = logging.getLogger("Rx")

class VirtualTimeScheduler(Scheduler):
    """Virtual Scheduler. This scheduler should work with either
    datetime/timespan or ticks as int/int"""

    def __init__(self, initial_clock=0, comparer=None):
        """Creates a new virtual time scheduler with the specified initial
        clock value and absolute time comparer.

        Keyword arguments:
        initial_clock -- Initial value for the clock.
        comparer -- Comparer to determine causality of events based on absolute time.
        """

        self.clock = initial_clock
        self.comparer = comparer
        self.is_enabled = False
        self.queue = PriorityQueue(1024)

        super(VirtualTimeScheduler, self).__init__()

    def local_now(self):
        return self.to_datetime_offset(self.clock)

    def schedule_now(self, state, action):
        return self.schedule_absolute_with_state(state, self.clock, action)

    def now(self):
        """Gets the scheduler's absolute time clock value as datetime offset."""

        return self.to_datetime_offset(self.clock)

    def schedule(self, action, state=None):
        return self.schedule_absolute(self.clock, action, state)

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime. Return the disposable
        object used to cancel the scheduled action (best effort)

        Keyword arguments:
        due_time -- Relative time after which to execute the action.
        action -- Action to be executed.
        state -- [Optional] State passed to the action to be executed.
        """
        log.debug("VirtualTimeScheduler.schedule_relative(duetime=%s, state=%s)" % (duetime, state))

        runat = self.add(self.clock, self.to_relative(duetime))
        return self.schedule_absolute(duetime=runat, action=action, state=state)

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime."""

        def run(scheduler, state1):
            self.queue.remove(si)

            return action(scheduler, state1)

        si = ScheduledItem(self, state, run, duetime, self.comparer)
        self.queue.enqueue(si)
        return si.disposable

    def schedule_periodic(self, period, action, state=None):
        scheduler = SchedulePeriodicRecursive(self, period, action, state)
        return scheduler.start()

    def start(self):
        """Starts the virtual time scheduler."""
        next = None
        if not self.is_enabled:
            self.is_enabled = True
            while self.is_enabled:
                next = self.get_next()
                if next:
                    if self.comparer(next.duetime, self.clock) > 0:
                        self.clock = next.duetime
                        log.info("VirtualTimeScheduler.start(), clock: %s",
                                 self.clock)
                    next.invoke()
                else:
                    self.is_enabled = False

    def stop(self):
        """Stops the virtual time scheduler."""
        self.is_enabled = False

    def advance_to(self, time):
        """Advances the scheduler's clock to the specified time, running all
        work til that point.

        Keyword arguments:
        time -- Absolute time to advance the scheduler's clock to.
        """
        next = None

        due_to_clock = self.comparer(self.clock, time)
        if due_to_clock > 0:
            raise ArgumentOutOfRangeException()

        if not due_to_clock:
            return

        if not self.is_enabled:
            self.is_enabled = True
            while self.is_enabled:
                next = self.get_next()
                if next and self.comparer(next.duetime, time) <= 0:
                    if self.comparer(next.duetime, self.clock) > 0:
                        self.clock = next.duetime

                    next.invoke()
                else:
                    self.is_enabled = False

            self.clock = time

    def advance_by(self, time):
        """Advances the scheduler's clock by the specified relative time,
        running all work scheduled for that timespan.

        Keyword arguments:
        time -- Relative time to advance the scheduler's clock by.
        """
        log.debug("VirtualTimeScheduler.advance_by(time=%s)", time)

        dt = self.add(self.clock, time)
        if self.comparer(self.clock, dt) > 0:
            raise ArgumentOutOfRangeException()
        return self.advance_to(dt)

    def sleep(self, time):
        """Advances the scheduler's clock by the specified relative time.

        Keyword arguments:
        time -- Relative time to advance the scheduler's clock by.
        """
        dt = self.add(self.clock, time)

        if self.comparer(self.clock, dt) >= 0:
            raise ArgumentOutOfRangeException()

        self.clock = dt

    def get_next(self):
        """Returns the next scheduled item to be executed."""
        while self.queue.length > 0:
            next = self.queue.peek()
            if next.is_cancelled():
                self.queue.dequeue()
            else:
                return next

        return None

    def add(self, absolute, relative):
        raise NotImplementedError

    def to_datetime_offset(self, absolute):
        """Converts the absolute time value to a datetime value."""

        raise NotImplementedError

    def to_relative(self, timespan):
        """Converts the TimeSpan value to a relative time value."""

        raise NotImplementedError
