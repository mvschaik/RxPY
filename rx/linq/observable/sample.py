from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableSample(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def _sample_observable(self, sampler):
        source = self

        def subscribe(observer):
            at_end = [None]
            has_value = [None]
            value = [None]

            def sample_subscribe(x):
                if has_value[0]:
                    has_value[0] = False
                    observer.on_next(value[0])

                if at_end[0]:
                    observer.on_completed()

            def on_next(new_value):
                has_value[0] = True
                value[0] = new_value

            def on_completed():
                at_end[0] = True

            return CompositeDisposable(
                source.subscribe(on_next, observer.on_error, on_completed),
                sampler.subscribe(sample_subscribe, observer.on_error, sample_subscribe)
            )
        return AnonymousObservable(subscribe)


    def sample(self, interval=None, sampler=None, scheduler=None):
        """Samples the observable sequence at each interval.

        1 - res = source.sample(sample_observable) # Sampler tick sequence
        2 - res = source.sample(5000) # 5 seconds
        2 - res = source.sample(5000, rx.scheduler.timeout) # 5 seconds

        Keyword arguments:
        source -- Source sequence to sample.
        interval -- Interval at which to sample (specified as an integer
            denoting milliseconds).
        scheduler -- [Optional] Scheduler to run the sampling timer on. If not
            specified, the timeout scheduler is used.

        Returns sampled observable sequence.
        """
        scheduler = scheduler or timeout_scheduler
        if not interval is None:
            return self._sample_observable(Observable.interval(interval, scheduler=scheduler))

        return self.sample_observable(sampler)
