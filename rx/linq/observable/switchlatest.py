from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableSwitchLatest(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def switch_latest(self):
        """Transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.

        Returns the observable sequence that at any point in time produces the
        elements of the most recent inner observable sequence that has been received.
        """

        sources = self

        def subscribe(observer):
            has_latest = [False]
            inner_subscription = SerialDisposable()
            is_stopped = [False]
            latest = [0]

            def on_next(inner_source):
                d = SingleAssignmentDisposable()
                latest[0] += 1
                _id = latest[0]
                has_latest[0] = True
                inner_subscription.disposable = d

                # Check if Future or Observable
                inner_source = Observable.from_future(inner_source)

                def on_next(x):
                    if latest[0] == _id:
                        observer.on_next(x)

                def on_error(e):
                    if latest[0] == _id:
                        observer.on_error(e)

                def on_completed():
                    if latest[0] == _id:
                        has_latest[0] = False
                        if is_stopped[0]:
                            observer.on_completed()

                d.disposable = inner_source.subscribe(on_next, on_error, on_completed)

            def on_completed():
                is_stopped[0] = True
                if not has_latest[0]:
                    observer.on_completed()

            subscription = sources.subscribe(on_next, observer.on_error, on_completed)
            return CompositeDisposable(subscription, inner_subscription)
        return AnonymousObservable(subscribe)
