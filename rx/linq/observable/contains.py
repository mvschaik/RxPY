from six import add_metaclass

from rx import Observable
from rx.internal.basic import default_comparer
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableContains(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    def contains(self, value, comparer=None):
        """Determines whether an observable sequence contains a specified 
        element with an optional equality comparer.
        
        Example
        1 - res = source.contains(42)
        2 - res = source.contains({ "value": 42 }, lambda x, y: x["value"] == y["value")
     
        Keyword parameters:
        value -- The value to locate in the source sequence.
        comparer -- {Function} [Optional] An equality comparer to compare elements.
     
        Returns an observable {Observable} sequence containing a single element
        determining whether the source sequence contains an element that has 
        the specified value."""
        
        comparer = comparer or default_comparer
        return self.where(lambda v: comparer(v, value)).any()