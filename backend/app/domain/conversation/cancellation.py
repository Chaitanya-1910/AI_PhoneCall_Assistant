import asyncio

class CancellationToken:
    """Cooperative cancellation and pausing token for streaming tasks."""
    def __init__(self):
        self._is_cancelled = False
        self._is_paused = False
        self._cancel_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set() # Set initially means "not paused"

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    def cancel(self):
        self._is_cancelled = True
        self._cancel_event.set()
        # Resume anything waiting so it can observe the cancellation
        self._pause_event.set()

    def pause(self):
        self._is_paused = True
        self._pause_event.clear()

    def resume(self):
        self._is_paused = False
        self._pause_event.set()

    async def wait_for_cancel(self):
        await self._cancel_event.wait()
        
    async def wait_if_paused(self):
        """Blocks if paused. If cancelled while paused, it returns."""
        if self._is_paused:
            await self._pause_event.wait()
