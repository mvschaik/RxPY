from threading import Timer
from datetime import timedelta

from rx.disposables import Disposable, CompositeDisposable
from rx.internal.basic import default_now

class Scheduler(object):
    """Provides a set of static properties to access commonly used schedulers."""

    def schedule(self, action, state=None):
        raise NotImplementedError

    def schedule_relative(self, duetime, action, state=None):
        raise NotImplementedError

    def schedule_absolute(self, duetime, action, state=None):
        raise NotImplementedError

    def invoke_action(self, action, state=None):
        action(self, state)
        return Disposable.empty()

    def schedule_periodic(self, period, action, state=None):
        """Schedules a periodic piece of work by dynamically discovering the
        scheduler's capabilities.

        Keyword parameters:
        period -- Period for running the work periodically.
        action -- Action to be executed.
        state -- [Optional] Initial state passed to the action upon the first
            iteration.

        Returns the disposable object used to cancel the scheduled recurring
        action (best effort).
        """

        period /= 1000.0
        timer = [None]
        s = [state]

        def interval():
            s[0] = action(s[0])

            timer[0] = Timer(period, interval)
            timer[0].start()

        timer[0] = Timer(period, interval)
        timer[0].start()

        def dispose():
            timer[0].cancel()

        return Disposable(dispose)

    def invoke_rec_immediate(self, scheduler, pair):
        state = pair.get('state')
        action = pair.get('action')
        group = CompositeDisposable()

        def recursive_action(state1):
            # FIXME: need a better name for this function
            def action2(state2=None):
                is_added = False
                is_done = [False]

                def action(scheduler, state=None):
                    if is_added:
                        group.remove(d)
                    else:
                        is_done[0] = True

                    recursive_action(state)
                    return Disposable.empty()

                d = scheduler.schedule(action, state2)

                if not is_done[0]:
                    group.add(d)
                    is_added = True

            action(action2, state1)

        recursive_action(state)
        return group

    def invoke_rec_date(self, scheduler, pair, method):
        state = pair.get('first')
        action = pair.get('second')
        group = CompositeDisposable()

        def recursive_action(state1):
            def action1(state2, duetime1):
                is_added = False
                is_done = [False]

                def action2(scheduler1, state3):
                    if is_added:
                        group.remove(d)
                    else:
                        is_done[0] = True

                    recursive_action(state3)
                    return Disposable.empty()

                d = getattr(scheduler, method)(duetime=duetime1, action=action2, state=state2)
                if not is_done[0]:
                    group.add(d)
                    is_added = True

            action(state1, action1)
        recursive_action(state)
        return group

    def schedule_recursive(self, action, state=None):
        """Schedules an action to be executed recursively.

        Keyword parameters:
        action -- {Function} Action to execute recursively. The parameter passed
            to the action is used to trigger recursive scheduling of the action.
        Returns the disposable {Disposable} object used to cancel the scheduled
        action (best effort)."""

        def action2(scheduler, pair):
            return self.invoke_rec_immediate(scheduler, pair)

        return self.schedule(action2, dict(state=state, action=action))

    def schedule_recursive_with_relative(self, duetime, action):
        """Schedules an action to be executed recursively after a specified 
        relative due time.     
        
        Keyword arguments:
        action -- {Function} Action to execute recursively. The parameter passed 
            to the action is used to trigger recursive scheduling of the action 
            at the specified relative time.
         duetime - {Number} Relative time after which to execute the action for 
            the first time.
        
        Returns the disposable {Disposable} object used to cancel the scheduled 
        action (best effort)."""
        
        def action1(_action, this=None):
            def func(dt):
                this(_action, dt)
            _action(func)
        return self.schedule_recursive_with_relative_and_state(duetime, action1, state=action)

    def schedule_recursive_with_relative_and_state(self, duetime, action, state):
        """Schedules an action to be executed recursively after a specified
        relative due time.

        Keyword arguments:
        state  -- {Mixed} State passed to the action to be executed.
        action -- {Function} Action to execute recursively. The last parameter
            passed to the action is used to trigger recursive scheduling of the
            action, passing in the recursive due time and invocation state.
        duetime - {Number} Relative time after which to execute the action for
            the first time.

        Returns the disposable {Disposable} object used to cancel the scheduled
        action (best effort)."""

        def action1(s, p):
            return self.invoke_rec_date(s, p, 'schedule_relative')

        return self.schedule_relative(duetime, action1, state={ "first": state, "second": action })

    def schedule_recursive_with_absolute(self, duetime, action):
        """Schedules an action to be executed recursively at a specified
        absolute due time.

        Keyword arguments:
        action -- {Function} Action to execute recursively. The parameter
            passed to the action is used to trigger recursive scheduling of
            the action at the specified absolute time.
        duetime {Number} Absolute time at which to execute the action for
            the first time.

        Returns the disposable {Disposable} object used to cancel the
        scheduled action (best effort)."""

        def action1(_action, this=None):
            def func(dt):
                this(_action, dt)
            _action(func)
        return self.schedule_recursive_with_absolute_and_state(duetime=duetime, action=action1, state=action)

    def schedule_recursive_with_absolute_and_state(self, duetime, action, state):
        """Schedules an action to be executed recursively at a specified
        absolute due time.

        Keyword arguments:
        state -- {Mixed} State passed to the action to be executed.
        action -- {Function} Action to execute recursively. The last parameter
            passed to the action is used to trigger recursive scheduling of the
            action, passing in the recursive due time and invocation state.
        duetime -- {Number} Absolute time at which to execute the action for the
            first time.
        Returns the disposable {Disposable} object used to cancel the scheduled
        action (best effort)."""

        def action2(scheduler, pair):
            return self.invoke_rec_date(scheduler, pair, method='schedule_absolute')

        return self.schedule_absolute(
            duetime=duetime, action=action2,
            state={ "first": state, "second": action })

    def now(self):
        return self.default_now()

    def default_now(self):
        return default_now()

    @classmethod
    def normalize(cls, timespan):
        """Normalizes the specified Timespan value to a positive value.
        
        Keyword Arguments:
        timeSpan -- {Number} The time span value to normalize.
        
        Returns {Number} The specified Timespan value if it is zero or positive; 
            otherwise, 0"""
    
        nospan = 0 if isinstance(timespan, int) else timedelta(0)
        if not timespan or timespan < nospan:
            timespan = nospan

        return timespan
