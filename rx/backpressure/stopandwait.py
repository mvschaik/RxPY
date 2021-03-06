from six import add_metaclass

from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

from .controlledobservable import ControlledObservable
from .stopandwaitobservable import StopAndWaitObservable

@add_metaclass(ExtensionMethod)
class ControlledObservableStopAndWait(ControlledObservable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def stop_and_wait(self, scheduler):
        """Attaches a stop and wait observable to the current observable.
   
        scheduler -- {Scheduler} [Optional] Optional scheduler used for yielding
            values.
        
        Returns a stop and wait observable {Observable}."""

        scheduler = scheduler or current_thread_scheduler
        return StopAndWaitObservable(self, scheduler)
