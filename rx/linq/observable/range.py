from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableRange(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    @classmethod
    def range(cls, start, count, scheduler=None):
        """Generates an observable sequence of integral numbers within a 
        specified range, using the specified scheduler to send out observer 
        messages.
     
        1 - res = Rx.Observable.range(0, 10);
        2 - res = Rx.Observable.range(0, 10, Rx.Scheduler.timeout);
    
        Keyword arguments:
        start -- The value of the first integer in the sequence.
        count -- The number of sequential integers to generate.
        scheduler -- [Optional] Scheduler to run the generator loop on. If not 
            specified, defaults to Scheduler.currentThread.
    
        Returns an observable sequence that contains a range of sequential 
        integral numbers.
        """
        scheduler = scheduler or current_thread_scheduler
        
        def subscribe(observer):
            def action(scheduler, i):
                #print("Observable:range:subscribe:action", scheduler, i)
                if i < count:
                    observer.on_next(start + i)
                    scheduler(i + 1)
                else:
                    #print "completed"
                    observer.on_completed()
                
            return scheduler.schedule_recursive(action, 0)
        return AnonymousObservable(subscribe)
