    def _async_schedule_or_call_now(self) -> bool:
        """Check if a call should be scheduled.

        Returns True if the function should be called immediately.

        Returns False if there is nothing to do.
        """
        if self._shutdown_requested:
            self.logger.debug("Debouncer call ignored as shutdown has been requested.")
            return False

        if self._timer_task:
            if not self._execute_at_end_of_timer:
                self._execute_at_end_of_timer = True

            return False

        # Locked means a call is in progress. Any call is good, so abort.
        if self._execute_lock.locked():
            return False

        if not self.immediate:
            self._execute_at_end_of_timer = True
            self._schedule_timer()
            return False

        return True
    async def async_call(self) -> None:
        """Call the function."""
        if not self._async_schedule_or_call_now():
            return

        async with self._execute_lock:
            # Abort if timer got set while we're waiting for the lock.
            if self._timer_task:
                return

            assert self._job is not None
            try:
                if task := self.hass.async_run_hass_job(
                    self._job, background=self._background
                ):
                    await task
            finally:
                self._schedule_timer()
