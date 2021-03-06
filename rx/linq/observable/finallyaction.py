from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.disposables import Disposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableForIn(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def finally_action(self, action):
        """Invokes a specified action after the source observable sequence
        terminates gracefully or exceptionally.

        Example:
        res = observable.finally(function () { console.log('sequence ended'; });

        Keyword arguments:
        action -- {Function} Action to invoke after the source observable sequence
            terminates.
        Returns {Observable} Source sequence with the action-invoking
        termination behavior applied."""

        source = self

        def subscribe(observer):
            try:
                subscription = source.subscribe(observer)
            except Exception as ex:
                action()
                raise

            def dispose():
                try:
                    subscription.dispose()
                finally:
                    action()

            return Disposable(dispose)
        return AnonymousObservable(subscribe)
