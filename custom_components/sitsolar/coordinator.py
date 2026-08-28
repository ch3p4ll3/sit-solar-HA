"""DataUpdateCoordinator for sitSolar."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    SitSolarApiClient,
    SitSolarApiError,
    SitSolarAuthError,
    SitSolarConnectionError,
    EnergyFlow,
    StationOverview,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, CONF_STATION_CODE

_LOGGER = logging.getLogger(__name__)


class SitSolarDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch data from sitSolar API."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_data: dict[str, Any],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._entry_data = entry_data
        self._client: SitSolarApiClient | None = None
        self._station_code = entry_data[CONF_STATION_CODE]

    async def _async_setup(self) -> None:
        session = async_get_clientsession(self.hass)
        self._client = SitSolarApiClient(
            session=session,
            username=self._entry_data["username"],
            password=self._entry_data["password"],
            base_url=self._entry_data.get("base_url", "https://enjoysolar.si-neng.com"),
        )
        await self._client.login()

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if self._client is None or not self._client.authenticated:
                await self._async_setup()

            energy_flow = await self._client.get_energy_flow_realtime(self._station_code)
            overview = await self._client.get_single_overview(self._station_code)

            return {
                "energy_flow": energy_flow,
                "overview": overview,
                "station_code": self._station_code,
            }

        except SitSolarAuthError as err:
            _LOGGER.warning("Authentication failed, re-logging in: %s", err)
            try:
                await self._client.login()
            except SitSolarApiError as login_err:
                raise UpdateFailed(f"Re-login failed: {login_err}") from login_err
            try:
                energy_flow = await self._client.get_energy_flow_realtime(self._station_code)
                overview = await self._client.get_single_overview(self._station_code)
                return {
                    "energy_flow": energy_flow,
                    "overview": overview,
                    "station_code": self._station_code,
                }
            except SitSolarApiError as retry_err:
                raise UpdateFailed(f"Retry after re-login failed: {retry_err}") from retry_err

        except SitSolarApiError as err:
            raise UpdateFailed(f"API error: {err}") from err

        except SitSolarConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

    async def async_login(self) -> None:
        await self._async_setup()
