import sys, traceback # FIXME: remove after debug

from rx.disposables import SingleAssignmentDisposable

from .abstractobserver import AbstractObserver

class AutoDetachObserver(AbstractObserver):

    def __init__(self, observer):
        super(AutoDetachObserver, self).__init__()

        self.observer = observer
        self.m = SingleAssignmentDisposable()

    def next(self, value):
        try:
            self.observer.on_next(value)
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            self.dispose()

    def error(self, exn):
        try:
            self.observer.on_error(exn)
        finally:
            self.dispose()

    def completed(self):
        try:
            self.observer.on_completed()
        finally:
            self.dispose()

    def set_disposable(self, value):
        self.m.disposable = value

    disposable = property(fset=set_disposable)

    def dispose(self):
        super(AutoDetachObserver, self).dispose()
        self.m.dispose()
