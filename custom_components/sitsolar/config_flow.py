"""Config flow for sitSolar integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SitSolarApiClient, SitSolarAuthError, SitSolarConnectionError
from .const import (
    DEFAULT_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    CONF_STATION_CODE,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Optional("base_url", default=DEFAULT_BASE_URL): str,
    }
)


async def _validate_credentials(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate credentials and return user info."""
    session = async_get_clientsession(hass)
    client = SitSolarApiClient(
        session=session,
        username=data["username"],
        password=data["password"],
        base_url=data.get("base_url", DEFAULT_BASE_URL),
    )
    await client.login()
    user_info = await client.get_user_info()
    return {"client": client, "user_info": user_info}


class SitSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sitSolar."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._base_url: str = DEFAULT_BASE_URL
        self._username: str = ""
        self._password: str = ""
        self._stations: list[dict[str, Any]] = []
        self._client: SitSolarApiClient | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._username = user_input["username"]
            self._password = user_input["password"]
            self._base_url = user_input.get("base_url", DEFAULT_BASE_URL)

            try:
                result = await _validate_credentials(self.hass, user_input)
                self._client = result["client"]
            except SitSolarAuthError:
                errors["base"] = "invalid_auth"
            except SitSolarConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during login")
                errors["base"] = "unknown"
            else:
                # Fetch station list
                try:
                    self._stations = await self._client.get_station_list()
                except Exception:
                    _LOGGER.exception("Failed to fetch station list")
                    self._stations = []

                if not self._stations:
                    errors["base"] = "cannot_connect"
                elif len(self._stations) == 1:
                    # Only one station, auto-select
                    station_code = self._stations[0].get(
                        "stationCode",
                        self._stations[0].get("station_code", ""),
                    )
                    return await self._create_entry(station_code)
                else:
                    # Multiple stations, let user choose
                    return await self.async_step_station()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_station(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle station selection."""
        if user_input is not None:
            station_code = user_input[CONF_STATION_CODE]
            return await self._create_entry(station_code)

        # Build station options
        station_options = {}
        for station in self._stations:
            code = station.get("stationCode", station.get("station_code", ""))
            name = station.get("stationName", station.get("station_name", code))
            station_options[code] = name

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_CODE): vol.In(station_options),
            }
        )

        return self.async_show_form(
            step_id="station",
            data_schema=schema,
        )

    async def _create_entry(self, station_code: str) -> FlowResult:
        """Create the config entry."""
        await self.async_set_unique_id(self._username)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"sitSolar ({station_code})",
            data={
                "username": self._username,
                "password": self._password,
                "base_url": self._base_url,
                CONF_STATION_CODE: station_code,
            },
        )
