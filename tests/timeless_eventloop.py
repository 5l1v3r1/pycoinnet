import asyncio
import time

from asyncio.unix_events import _UnixSelectorEventLoop


class TimelessEventLoop(_UnixSelectorEventLoop):
    def __init__(self, *args, **kwargs):
        super(TimelessEventLoop, self).__init__(*args, **kwargs)
        self._fake_time_offset = 0.0

    def time(self):
        return self._fake_time_offset + time.time()

    def _fast_forward_time(self):
        if not self._scheduled:
            return
        now = self.time()
        when = self._scheduled[0]._when
        if when > now:
            self._fake_time_offset += when - now
    
    def _run_once(self):
        """Run one full iteration of the event loop.

        This calls all currently ready callbacks, polls for I/O,
        schedules the resulting callbacks, and finally schedules
        'call_later' callbacks.

        It uses the "_fake_time" value.
        """
        self._fast_forward_time()
        super(TimelessEventLoop, self)._run_once()


TIMELESS_EVENT_LOOP = TimelessEventLoop()


def use_timeless_eventloop():
    asyncio.set_event_loop(TIMELESS_EVENT_LOOP)
