from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableBuffer(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def buffer(self, buffer_openings=None, closing_selector=None, buffer_closing_selector=None):
        """Projects each element of an observable sequence into zero or more 
        buffers.
         
        Keyword arguments:
        buffer_openings -- Observable sequence whose elements denote the 
            creation of windows.
        closing_selector -- Or, a function invoked to define the boundaries of 
            the produced windows (a window is started when the previous one is 
            closed, resulting in non-overlapping windows).
        buffer_closing_selector -- [optional] A function invoked to define the 
            closing of each produced window. If a closing selector function is 
            specified for the first parameter, self parameter is ignored.
        
        Returns an observable sequence of windows."""
        
        if buffer_openings and not buffer_closing_selector:
            return self.observable_window_with_bounaries(buffer_openings).select_many(lambda item: item.to_array())
        
        if closing_selector:
            return self.observable_window_with_closing_selector(closing_selector).select_many(lambda item: item.to_array())
        else:
            return self.observable_window_with_openings(closing_selector, buffer_closing_selector).select_many(lambda item: item.to_array())
    
    def buffer_with_count(self, count, skip=None):
        """Projects each element of an observable sequence into zero or more 
        buffers which are produced based on element count information.
   
        Example:
        res = xs.buffer_with_count(10)
        res = xs.buffer_with_count(10, 1)
   
        Keyword parameters:
        count -- {Number} Length of each buffer.
        skip -- {Number} [Optional] Number of elements to skip between creation
            of consecutive buffers. If not provided, defaults to the count.
        
        Returns an observable {Observable} sequence of buffers."""

        if skip is None:
            skip = count
        
        def selector(x):
            return x.to_array()  

        def predicate(x):
            return len(x) > 0

        return self.window_with_count(count, skip).select_many(selector).where(predicate)
