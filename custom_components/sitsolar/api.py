"""sitSolar API Client with AES password encryption."""
from __future__ import annotations

import base64
import logging
from typing import Any

import aiohttp
from pydantic import BaseModel

from .const import (
    DEFAULT_BASE_URL,
    DEFAULT_API_PREFIX,
    ENDPOINT_AES_KEY,
    ENDPOINT_LOGIN,
    ENDPOINT_LOGOUT,
    ENDPOINT_AUTH_INFO,
    ENDPOINT_STATION_LIST,
    ENDPOINT_STATION_DETAIL,
    ENDPOINT_STATION_OVERVIEW,
    ENDPOINT_SINGLE_STATION_OVERVIEW,
    ENDPOINT_ENERGY_FLOW,
    ENDPOINT_ENERGY_FLOW_REALTIME,
    ENDPOINT_STORAGE_INVERTER_LIST,
    ENDPOINT_DEVICE_REALTIME,
    ERROR_TOKEN_EXPIRED,
    ERROR_SUCCESS,
)

_LOGGER = logging.getLogger(__name__)


# --- Pydantic Models ---

class StationInfo(BaseModel):
    """Station list item."""
    station_code: str = ""
    station_name: str = ""
    installed_capacity: float = 0.0
    active_power: float = 0.0
    station_type: int = 0
    online_type: int = 0
    communicate_status: int = 0
    alarm_status: int = 0
    today_product_power: float = 0.0
    total_product_power: float = 0.0
    mppt_power: float = 0.0
    battery_status: int = 0

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StationInfo:
        return cls(
            station_code=data.get("stationCode", ""),
            station_name=data.get("stationName", ""),
            installed_capacity=data.get("installedCapacity", 0),
            active_power=data.get("activePower", 0),
            station_type=data.get("stationType", 0),
            online_type=data.get("onlineType", 0),
            communicate_status=data.get("communicateStatus", 0),
            alarm_status=data.get("alarmStatus", 0),
            today_product_power=data.get("todayProductPower", 0),
            total_product_power=data.get("totalProductPower", 0),
            mppt_power=data.get("mpptPower", 0),
            battery_status=data.get("batteryStatus", 0),
        )


class EnergyFlow(BaseModel):
    """Real-time energy flow data."""
    mppt_power: float = 0.0
    battery_power: float = 0.0
    battery_soc: float = 0.0
    grid_export: float = 0.0
    grid_import: float = 0.0
    load_power: float = 0.0
    ac_coupled_power: float = 0.0
    eps_power: float = 0.0
    remain_available_energy: float = 0.0
    remain_charge_full_time: float = 0.0
    data_update_time: int = 0

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnergyFlow:
        return cls(
            mppt_power=data.get("mpptPower", 0),
            battery_power=data.get("batteryPower", 0),
            battery_soc=data.get("batterySocAver", 0),
            grid_export=data.get("ongridPower", 0),
            grid_import=data.get("buyPower", 0),
            load_power=data.get("loadPower", 0),
            ac_coupled_power=data.get("acCoupleGfActivePower", 0),
            eps_power=data.get("uwEPS_P_R", 0),
            remain_available_energy=data.get("remainAvailEnergy", 0),
            remain_charge_full_time=data.get("remainChargeFullTime", 0),
            data_update_time=data.get("dataUpdateTime", 0),
        )


class StationOverview(BaseModel):
    """Station overview with energy stats and battery info."""
    installed_capacity: float = 0.0
    active_power: float = 0.0
    today_product_power: float = 0.0
    today_self_use_power: float = 0.0
    today_grid_export: float = 0.0
    today_grid_import: float = 0.0
    today_battery_charge: float = 0.0
    today_battery_discharge: float = 0.0
    today_load_power: float = 0.0
    total_product_power: float = 0.0
    total_grid_export: float = 0.0
    total_grid_import: float = 0.0
    total_self_use_power: float = 0.0
    battery_soc: float = 0.0
    battery_soh: float = 0.0
    battery_charge_power: float = 0.0
    battery_discharge_power: float = 0.0
    grid_power_to_grid: float = 0.0
    grid_power_from_grid: float = 0.0
    update_time: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StationOverview:
        return cls(
            installed_capacity=data.get("installedCapacity", 0),
            active_power=data.get("activePower", 0),
            today_product_power=data.get("todayProductPower", 0),
            today_self_use_power=data.get("todaySelfUsePower", 0),
            today_grid_export=data.get("todayOngridPower", 0),
            today_grid_import=data.get("todayBuyGridPower", 0),
            today_battery_charge=data.get("todayCellCharge", 0),
            today_battery_discharge=data.get("todayCellDischarge", 0),
            today_load_power=data.get("todayLoadUsePower", 0),
            total_product_power=data.get("totalProductPower", 0),
            total_grid_export=data.get("totalOngridPower", 0),
            total_grid_import=data.get("totalBuyGridPower", 0),
            total_self_use_power=data.get("totalSelfUsePower", 0),
            battery_soc=data.get("uwBatSoc", 0),
            battery_soh=data.get("batterySoh", 0),
            battery_charge_power=data.get("cellChargePower", 0),
            battery_discharge_power=data.get("cellDisChargePower", 0),
            grid_power_to_grid=data.get("ammeterActivePowerToGrid", 0),
            grid_power_from_grid=data.get("ammeterActivePowerFromGrid", 0),
            update_time=data.get("updateTime", ""),
        )


# --- Encryption ---

def _encrypt_password_aes(password: str, key_b64: str) -> str:
    """AES-128-ECB with CryptoJS-compatible output (WordArray key = raw Base64)."""
    try:
        from Crypto.Cipher import AES
    except ImportError:
        raise ImportError(
            "pycryptodome is required for sitSolar password encryption. "
            "Install with: pip install pycryptodome"
        )

    key = base64.b64decode(key_b64)  # 16 bytes

    cipher = AES.new(key, AES.MODE_ECB)

    # PKCS7 padding
    bs = AES.block_size
    data = password.encode("utf-8")
    padding_len = bs - (len(data) % bs)
    data += bytes([padding_len] * padding_len)

    ciphertext = cipher.encrypt(data)
    return base64.b64encode(ciphertext).decode("ascii")


# --- Exceptions ---

class SitSolarApiError(Exception):
    """Base exception for sitSolar API errors."""

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(f"API error {code}: {msg}")
        self.code = code
        self.msg = msg


class SitSolarAuthError(SitSolarApiError):
    """Authentication error."""


class SitSolarConnectionError(SitSolarApiError):
    """Connection error."""


# --- API Client ---

class SitSolarApiClient:
    """sitSolar API client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._base_url = base_url.rstrip("/")
        self._api_base = f"{self._base_url}{DEFAULT_API_PREFIX}"
        self._token: str | None = None
        self._user_id: int | None = None
        self._aes_key: str | None = None

    @property
    def authenticated(self) -> bool:
        return self._token is not None

    async def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._api_base}{path}"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with self._session.request(
                method,
                url,
                json=data if method in ("POST", "PUT") else None,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
                ssl=False,
            ) as resp:
                result = await resp.json()

                if resp.status == 401:
                    code = result.get("code", 0)
                    if code in ERROR_TOKEN_EXPIRED:
                        raise SitSolarAuthError(code, result.get("msg", "Token expired"))
                    raise SitSolarAuthError(401, "Unauthorized")

                if resp.status != 200:
                    raise SitSolarConnectionError(
                        resp.status,
                        f"HTTP {resp.status}: {result.get('msg', 'Unknown error')}",
                    )

                code = result.get("code", 0)
                if code != ERROR_SUCCESS:
                    raise SitSolarApiError(code, result.get("msg", f"Error code {code}"))

                return result.get("data", {})

        except aiohttp.ClientError as err:
            raise SitSolarConnectionError(0, f"Connection error: {err}") from err

    async def _fetch_aes_key(self) -> str | None:
        if self._aes_key is not None:
            return self._aes_key

        try:
            data = await self._request("GET", ENDPOINT_AES_KEY)
            if data:
                self._aes_key = data if isinstance(data, str) else str(data)
                return self._aes_key
        except Exception:
            _LOGGER.debug("Could not fetch AES key", exc_info=True)

        return None

    async def _encrypt_password(self) -> str:
        aes_key = await self._fetch_aes_key()
        if aes_key:
            try:
                return _encrypt_password_aes(self._password, aes_key)
            except ImportError:
                _LOGGER.warning(
                    "pycryptodome not installed, sending password in plaintext. "
                    "Install with: pip install pycryptodome"
                )
            except Exception:
                _LOGGER.warning(
                    "AES encryption failed, sending password in plaintext",
                    exc_info=True,
                )

        return self._password

    async def login(self) -> dict[str, Any]:
        encrypted_pw = await self._encrypt_password()
        try:
            data = await self._request(
                "POST",
                ENDPOINT_LOGIN,
                data={
                    "username": self._username,
                    "password": encrypted_pw,
                    "loginType": 2,
                    "app": True,
                },
            )
            self._token = data if isinstance(data, str) else str(data)
        except SitSolarApiError as err:
            if encrypted_pw != self._password:
                _LOGGER.debug("Encrypted login failed (%s), trying plaintext", err.msg)
                data = await self._request(
                    "POST",
                    ENDPOINT_LOGIN,
                    data={
                        "username": self._username,
                        "password": self._password,
                        "loginType": 2,
                        "app": True,
                    },
                )
                self._token = data if isinstance(data, str) else str(data)
            else:
                raise

        try:
            user_info = await self.get_user_info()
            self._user_id = user_info.get("id")
        except SitSolarApiError:
            _LOGGER.debug("Could not fetch user info after login")

        return {"token": self._token}

    async def logout(self) -> None:
        try:
            await self._request("POST", ENDPOINT_LOGOUT)
        except SitSolarApiError:
            pass
        finally:
            self._token = None

    async def get_user_info(self) -> dict[str, Any]:
        return await self._request("GET", ENDPOINT_AUTH_INFO)

    async def get_station_list(self) -> list[StationInfo]:
        data = await self._request(
            "POST", ENDPOINT_STATION_LIST, data={"current": 1, "size": 20}
        )
        if isinstance(data, dict):
            records = data.get("records", data.get("list", []))
            if isinstance(records, list):
                return [StationInfo.from_api(r) for r in records]
        return []

    async def get_station_detail(self, station_code: str) -> dict[str, Any]:
        return await self._request(
            "GET", ENDPOINT_STATION_DETAIL, params={"stationCode": station_code}
        )

    async def get_energy_flow(self, station_code: str) -> EnergyFlow:
        data = await self._request(
            "GET", ENDPOINT_ENERGY_FLOW, params={"stationCode": station_code}
        )
        return EnergyFlow.from_api(data if isinstance(data, dict) else {})

    async def get_energy_flow_realtime(self, station_code: str) -> EnergyFlow:
        data = await self._request(
            "GET", ENDPOINT_ENERGY_FLOW_REALTIME, params={"stationCode": station_code}
        )
        return EnergyFlow.from_api(data if isinstance(data, dict) else {})

    async def get_single_overview(self, station_code: str) -> StationOverview:
        data = await self._request(
            "GET",
            ENDPOINT_SINGLE_STATION_OVERVIEW,
            params={"stationCode": station_code},
        )
        return StationOverview.from_api(data if isinstance(data, dict) else {})

    async def get_storage_inverter_list(
        self, station_code: str
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "POST",
            ENDPOINT_STORAGE_INVERTER_LIST,
            data={"stationCode": station_code, "devTypeId": 51, "current": 1},
        )
        if isinstance(data, dict):
            records = data.get("records", data.get("list", []))
            if isinstance(records, list):
                return records
        return []

    async def get_device_realtime(
        self, dev_id: int, rel_time_list: list[str]
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            ENDPOINT_DEVICE_REALTIME,
            data={"devId": dev_id, "relTimeList": rel_time_list},
        )
