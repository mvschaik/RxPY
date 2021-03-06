from six import add_metaclass

from rx.observable import Observable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableDelaySubscription(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def delay_subscription(self, duetime, scheduler):
        """Time shifts the observable sequence by delaying the subscription.

        1 - res = source.delay_subscription(5000) # 5s
        2 - res = source.delay_subscription(5000, Scheduler.timeout) # 5 seconds

        duetime -- Absolute or relative time to perform the subscription at.
        scheduler [Optional] Scheduler to run the subscription delay timer on.
            If not specified, the timeout scheduler is used.

        Returns time-shifted sequence.
        """
        scheduler = scheduler or timeout_scheduler

        def selector(_):
            return Observable.empty()
        return self.delay_with_selector(Observable.timer(duetime, scheduler), selector)
