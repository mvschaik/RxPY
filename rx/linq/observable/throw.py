from six import add_metaclass
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable
from rx.concurrency import immediate_scheduler, current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableThrow(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def throw(cls, exception, scheduler=None):
        """Returns an observable sequence that terminates with an exception, 
        using the specified scheduler to send out the single OnError message.
    
        1 - res = rx.Observable.throw_exception(Exception('Error'))
        2 - res = rx.Observable.throw_exception(Exception('Error'), 
                                                rx.Scheduler.timeout)
     
        Keyword arguments:
        exception -- An object used for the sequence's termination.
        scheduler -- Scheduler to send the exceptional termination call on. If
            not specified, defaults to ImmediateScheduler.
    
        Returns the observable sequence that terminates exceptionally with the 
        specified exception object.
        """
        scheduler = scheduler or immediate_scheduler
        
        exception = Exception(exception) if type(exception) is Exception else exception

        def subscribe(observer):
            def action(scheduler, state):
                observer.on_error(exception)

            return scheduler.schedule(action)
        return AnonymousObservable(subscribe)

    throw_exception = throw
