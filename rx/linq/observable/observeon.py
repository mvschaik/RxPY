from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod
from rx.observeonobserver import ObserveOnObserver

@add_metaclass(ExtensionMethod)
class ObservableObserveOn(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def observe_on(self, scheduler):
        """Wraps the source sequence in order to run its observer callbacks on 
        the specified scheduler.
        
        Keyword arguments:
        scheduler -- Scheduler to notify observers on.</param>
        
        Returns the source sequence whose observations happen on the specified 
        scheduler.

        This only invokes observer callbacks on a scheduler. In case the 
        subscription and/or unsubscription actions have side-effects
        that require to be run on a scheduler, use subscribeOn.
        """        
        source = self

        def subscribe(observer):
            return source.subscribe(ObserveOnObserver(scheduler, observer))
     
        return AnonymousObservable(subscribe)

