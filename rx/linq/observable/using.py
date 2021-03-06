from six import add_metaclass
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableUsing(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def using(cls, resource_factory, observable_factory):
        """Constructs an observable sequence that depends on a resource object,
        whose lifetime is tied to the resulting observable sequence's lifetime.
      
        1 - res = rx.Observable.using(function () { return new AsyncSubject(); }, function (s) { return s; });
    
        Keyword arguments:
        resource_factory -- Factory function to obtain a resource object.
        observable_factory -- Factory function to obtain an observable sequence
            that depends on the obtained resource.
     
        Returns an observable sequence whose lifetime controls the lifetime of 
        the dependent resource object.
        """
        def subscribe(observer):
            disposable = Disposable.empty()
            try:
                resource = resource_factory()
                if resource:
                    disposable = resource
                
                source = observable_factory(resource)
            except Exception as exception:
                d = Observable.throw_exception(exception).subscribe(observer)
                return CompositeDisposable(d, disposable)
            
            return CompositeDisposable(source.subscribe(observer), disposable)
        return AnonymousObservable(subscribe)
