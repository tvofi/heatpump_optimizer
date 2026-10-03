        This method is irreversible.
        """
        self._read_only = True

    async def async_load(self) -> _T | None:
        """Load data.

        If the expected version and minor version do not match the given
        versions, the migrate function will be invoked with
        migrate_func(version, minor_version, config).

        Will ensure that when a call comes in while another one is in progress,
        the second call will wait and return the result of the first call.
        """
        if self._load_future:
            return await self._load_future

        self._load_future = self.hass.loop.create_future()
        try:
            result = await self._async_load()
        except BaseException as ex:
            self._load_future.set_exception(ex)
            # Ensure the future is marked as retrieved
            # since if there is no concurrent call it
            # will otherwise never be retrieved.
            self._load_future.exception()
            raise
        else:
            self._load_future.set_result(result)
        finally:
            self._load_future = None

        return result

    async def _async_load(self) -> _T | None:
        """Load the data and ensure the task is removed."""
        if STORAGE_SEMAPHORE not in self.hass.data:
            self.hass.data[STORAGE_SEMAPHORE] = asyncio.Semaphore(MAX_LOAD_CONCURRENTLY)
        async with self.hass.data[STORAGE_SEMAPHORE]:
            return await self._async_load_data()

    async def _async_load_data(self):
        """Load the data."""
        # Check if we have a pending write
        if self._data is not None:
            data = self._data

            # If we didn't generate data yet, do it now.
            if "data_func" in data:
                data["data"] = data.pop("data_func")()

            # We make a copy because code might assume it's safe to mutate loaded data
            # and we don't want that to mess with what we're trying to store.
            data = deepcopy(data)
        elif cache := self._manager.async_fetch(self.key):
            exists, data = cache
            if not exists:
                return None
        else:
            try:
                data = await self.hass.async_add_executor_job(
                    json_util.load_json, self.path
                )
            except HomeAssistantError as err:
                if isinstance(err.__cause__, JSONDecodeError):
                    # If we have a JSONDecodeError, it means the file is corrupt.
                    # We can't recover from this, so we'll log an error, rename the file and
                    # return None so that we can start with a clean slate which will
                    # allow startup to continue so they can restore from a backup.
                    isotime = dt_util.utcnow().isoformat()
                    corrupt_postfix = f".corrupt.{isotime}"
                    corrupt_path = f"{self.path}{corrupt_postfix}"
                    await self.hass.async_add_executor_job(
                        os.rename, self.path, corrupt_path
                    )
                    storage_key = self.key
                    _LOGGER.error(
                        "Unrecoverable error decoding storage %s at %s; "
                        "This may indicate an unclean shutdown, invalid syntax "
                        "from manual edits, or disk corruption; "
                        "The corrupt file has been saved as %s; "
                        "It is recommended to restore from backup: %s",
                        storage_key,
                        self.path,
                        corrupt_path,
                        err,
                    )
                    from .issue_registry import (  # pylint: disable=import-outside-toplevel
                        IssueSeverity,
                        async_create_issue,
                    )

                    issue_domain = HOMEASSISTANT_DOMAIN
                    if (
                        domain := (storage_key.partition(".")[0])
                    ) and domain in self.hass.config.components:
                        issue_domain = domain

                    async_create_issue(
                        self.hass,
                        HOMEASSISTANT_DOMAIN,
                        f"storage_corruption_{storage_key}_{isotime}",
                        is_fixable=True,
                        issue_domain=issue_domain,
                        translation_key="storage_corruption",
                        is_persistent=True,
                        severity=IssueSeverity.CRITICAL,
                        translation_placeholders={
                            "storage_key": storage_key,
                            "original_path": self.path,
                            "corrupt_path": corrupt_path,
                            "error": str(err),
                        },
                    )
                    return None
                raise

            if data == {}:
                return None

        # Add minor_version if not set
        if "minor_version" not in data:
            data["minor_version"] = 1

        if (
            data["version"] == self.version
            and data["minor_version"] == self.minor_version
        ):
            stored = data["data"]
        else:
            _LOGGER.info(
                "Migrating %s storage from %s.%s to %s.%s",
                self.key,
                data["version"],
                data["minor_version"],
                self.version,
                self.minor_version,
            )
            if len(inspect.signature(self._async_migrate_func).parameters) == 2:
                stored = await self._async_migrate_func(data["version"], data["data"])
            else:
                try:
                    stored = await self._async_migrate_func(
                        data["version"], data["minor_version"], data["data"]
                    )
                except NotImplementedError:
                    if data["version"] != self.version:
                        raise
                    stored = data["data"]
            await self.async_save(stored)

        return stored

    async def async_save(self, data: _T) -> None:
        """Save data."""
        self._data = {
