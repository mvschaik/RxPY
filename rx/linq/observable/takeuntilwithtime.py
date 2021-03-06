from datetime import datetime, timedelta

from six import add_metaclass

from rx.internal import noop
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableTakeUntilWithTime(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def take_until_with_time(self, end_time, scheduler=None):
        """Takes elements for the specified duration until the specified end
        time, using the specified scheduler to run timers.

        Examples:
        1 - res = source.take_until_with_time(dt, [optional scheduler])
        2 - res = source.take_until_with_time(5000, [optional scheduler])

        Keyword Arguments:
        end_time -- {Number | Date} Time to stop taking elements from the source
            sequence. If this value is less than or equal to Date(), the
            result stream will complete immediately.
        scheduler -- {Scheduler} Scheduler to run the timer on.

        Returns an observable {Observable} sequence with the elements taken
        until the specified end time."""

        scheduler = scheduler or timeout_scheduler
        source = self

        if isinstance(end_time, datetime):
            scheduler_method = scheduler.schedule_absolute
        else:
            scheduler_method = scheduler.schedule_relative

        print(scheduler_method)
        def subscribe(observer):
            def action(scheduler, state):
                observer.on_completed()

            task = scheduler_method(end_time, action)
            return CompositeDisposable(task,  source.subscribe(observer))
        return AnonymousObservable(subscribe)

