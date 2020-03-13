from typing import Iterable, Union, Set, Optional, Any, Callable
from asyncio import (get_event_loop, ensure_future, Future, run, Handle,
                    AbstractEventLoop, coroutine, set_event_loop)
from asyncio.tasks import FIRST_COMPLETED, ALL_COMPLETED, FIRST_EXCEPTION, _release_waiter
from asyncio import sleep as async_wait

class AGenerator():
    def __init__(self, data:Union[Iterable[Union["coroutine", Future]], "coroutine", Future]=[],
                        loop:AbstractEventLoop=None,
                        *, return_future:bool=False, flush:bool=True):
        if(loop is None):
            self.loop = get_event_loop()
        else:
            self.loop = loop

        if(isinstance(data, Iterable) and len(data) and not isinstance(data[0], Future)):
            self._data = [ensure_future(corout, loop=self.loop) for corout in data]
        elif(isinstance(data, Iterable) and not len(data)):
            self._data = []
        elif(not isinstance(data, Future)):
            self._data = ensure_future(data, loop=self.loop)
        else:
            self._data = data

        self.done = set()
        self.pending = set(self._data)

        self.return_futures = return_future
        self.flush = flush

        self.counter = 0
        self.uncollected = 0
        self.waiter = self.loop.create_future()

    def __call__(self, *, all:bool=False):
        if(all):
            return self.loop.run_until_complete(self.__async_iter())
        return self.loop.run_until_complete(self.__async_next())

    def __next__(self) -> Iterable[Optional[Union[Future, Any]]]:
        if(self.uncollected):
            return self.loop.run_until_complete(self.__async_next())
        
        return []

    def __iter__(self) -> Iterable[Optional[Union[Future, Any]]]:
        if(self.uncollected):
            return self.loop.run_until_complete(self.__async_iter())
        
        return []

    def __len__(self) -> int:
        return self.uncollected

    def append(self, element:Union["coroutine", Future]):
        if(not isinstance(element, Future)):
            element = ensure_future(element, loop=self.loop)

        self.loop.run_until_complete(self._wait([element], add=True))

        self.uncollected += 1
        self.pending.add(element)

    def extend(self, iterable:Iterable[Union["coroutine", Future]]):
        if(not isinstance(iterable[0], Future)):
            iterable = [ensure_future(corout, loop=self.loop) for corout in iterable]

        self.loop.run_until_complete(self._wait(iterable, add=True))

        self.uncollected += len(iterable)
        self.pending.update(iterable)

    async def __async_next(self) -> Iterable[Optional[Union[Future, Any]]]:
        done, pending = await self._wait(self.pending, return_when=FIRST_COMPLETED, loop=self.loop)

        if(self.flush):
            self.done = done
            self.pending = pending
        else:
            self.done.update(done)
            self.pending = pending

        self.uncollected -= len(done)

        if(not self.return_futures):
            return [future.result() for future in done]

        return done

    async def __async_iter(self) -> Iterable[Optional[Union[Future, Any]]]:
        done, pending = await self._wait(self.pending, return_when=ALL_COMPLETED, loop=self.loop)

        if(self.flush):
            self.done = done
            self.pending = pending
        else:
            self.done.update(done)
            self.pending = pending

        self.uncollected -= len(done)

        if(not self.return_futures):
            return iter([future.result() for future in done])

        return iter(done)

    async def _wait(self, fs, return_when=FIRST_COMPLETED, *, add:bool=False, loop:AbstractEventLoop=None, 
                            timeout:int=None):
        """A modified version of _wait in asyncio.

        The fs argument must be a collection of Futures.
        """
        if(not len(fs)): return [], self.pending

        timeout_handle = None
        if(loop is None):
            loop = self.loop

        if timeout is not None:
            timeout_handle = loop.call_later(timeout, _release_waiter, self.waiter)
        
        if(add):
            self.counter += len(fs)
        else:
            self.counter = len(fs)

        def __on_completion(f):
            self.counter -= 1
            if (self.counter <= 0 or
                return_when == FIRST_COMPLETED or
                return_when == FIRST_EXCEPTION and (not f.cancelled() and
                                                    f.exception() is not None)):
                if timeout_handle is not None:
                    timeout_handle.cancel()
                if not self.waiter.done():
                    self.waiter.set_result(None)

        for f in fs:
            f.add_done_callback(__on_completion)

        try:
            await self.waiter
        finally:
            if timeout_handle is not None:
                timeout_handle.cancel()
            for f in fs:
                f.remove_done_callback(__on_completion)

        if(not add):
            done, pending = set(), set()
            for f in fs:
                if f.done():
                    done.add(f)
                else:
                    pending.add(f)
                
            return done, pending

    
async def async_sleep(seconds:float, *, _return:Any=None):
    # _return as a kwarg for readability's sake
    await async_wait(seconds)

    return _return

async def do_async(funct, *args, **kwargs):
    return funct(*args, **kwargs)