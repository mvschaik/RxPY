from rx import AnonymousObservable, Observable
from rx.disposables import Disposable, CompositeDisposable

class ConnectableObservable(Observable):

    def __init__(self, source, subject):
        self.subject = subject
        self.source = source.as_observable()
        self.has_subscription = False
        self.subscription = None

        def subscribe(observer):
            return self.subject.subscribe(observer)
        super(ConnectableObservable, self).__init__(subscribe)

    def connect(self):
        if not self.has_subscription:
            self.has_subscription = True

            def dispose():
                self.has_subscription = False

            disposable = self.source.subscribe(self.subject)
            self.subscription = CompositeDisposable(disposable, Disposable.create(dispose))

        return self.subscription

    def ref_count(self):
        connectable_subscription = [None]
        count = [0]
        source = self

        def subscribe(observer):
            count[0] += 1
            should_connect = count[0] == 1
            subscription = source.subscribe(observer)
            if should_connect:
                connectable_subscription[0] = source.connect()

            def dispose():
                subscription.dispose()
                count[0] -= 1
                if not count[0]:
                    connectable_subscription[0].dispose()

            return Disposable.create(dispose)
        return AnonymousObservable(subscribe)
