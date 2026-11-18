    def async_create_task[_R](
        self,
        target: Coroutine[Any, Any, _R],
        name: str | None = None,
        eager_start: bool = True,
    ) -> asyncio.Task[_R]:
        """Create a task from within the event loop.

        This method must be run in the event loop. If you are using this in your
        integration, use the create task methods on the config entry instead.

        target: target to call.
        """
        if self.loop_thread_id != threading.get_ident():
            from .helpers import frame  # pylint: disable=import-outside-toplevel

            frame.report_non_thread_safe_operation("hass.async_create_task")
        return self.async_create_task_internal(target, name, eager_start)

    @callback
    def async_create_task_internal[_R](
        self,
        target: Coroutine[Any, Any, _R],
        name: str | None = None,
        eager_start: bool = True,
    ) -> asyncio.Task[_R]:
        """Create a task from within the event loop, internal use only.

        This method is intended to only be used by core internally
        and should not be considered a stable API. We will make
        breaking changes to this function in the future and it
        should not be used in integrations.

        This method must be run in the event loop. If you are using this in your
        integration, use the create task methods on the config entry instead.

        target: target to call.
        """
        if eager_start:
            task = create_eager_task(target, name=name, loop=self.loop)
            if task.done():
                return task
        else:
