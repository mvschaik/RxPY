from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableScan(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    def scan(self, accumulator, seed=None):
        """Applies an accumulator function over an observable sequence and 
        returns each intermediate result. The optional seed value is used as 
        the initial accumulator value. For aggregation behavior with no 
        intermediate results, see Observable.aggregate.
        
        1 - scanned = source.scan(lambda acc, x: acc + x)
        2 - scanned = source.scan(lambda acc, x: acc + x, 0)
        
        Keyword arguments:
        accumulator -- An accumulator function to be invoked on each element.
        seed -- [Optional] The initial accumulator value.
        
        Returns an observable sequence containing the accumulated values.        
        """
        has_seed = False
        if not seed is None:
            has_seed = True

        source = self

        def defer():
            has_accumulation = [False]
            accumulation = [None]

            def projection(x):
                if has_accumulation[0]:
                    accumulation[0] = accumulator(accumulation[0], x)
                else:
                    accumulation[0] =  accumulator(seed, x) if has_seed else x
                    has_accumulation[0] = True
                
                return accumulation[0]
            return source.select(projection)
        return Observable.defer(defer)
