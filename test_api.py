"""sitSolar API Test Script — standalone, no HA dependency."""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path
from typing import Any

import aiohttp

RESULTS_DIR = Path("api_results")

BASE_URL = "https://enjoysolar.si-neng.com"
API_BASE = f"{BASE_URL}/prod-api"


def _encrypt_password_aes(password: str, key_b64: str) -> str:
    """AES-128-ECB with CryptoJS-compatible output (WordArray key = raw Base64)."""
    from Crypto.Cipher import AES

    key = base64.b64decode(key_b64)  # 16 bytes

    cipher = AES.new(key, AES.MODE_ECB)
    bs = AES.block_size
    data = password.encode("utf-8")
    padding_len = bs - (len(data) % bs)
    data += bytes([padding_len] * padding_len)
    ciphertext = cipher.encrypt(data)
    return base64.b64encode(ciphertext).decode("ascii")


def _save(name: str, data: object) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    filepath = RESULTS_DIR / name
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  → {filepath}")


def _headers(token: str | None = None) -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


async def get(session: aiohttp.ClientSession, path: str, token: str | None = None) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    async with session.get(url, headers=_headers(token), ssl=False, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        return await resp.json()


async def post(session: aiohttp.ClientSession, path: str, body: dict, token: str | None = None) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    async with session.post(url, json=body, headers=_headers(token), ssl=False, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        return await resp.json()


async def main() -> None:
    parser = argparse.ArgumentParser(description="sitSolar API test")
    parser.add_argument("--username", "-u", help="Username/email")
    parser.add_argument("--password", "-p", help="Password")
    parser.add_argument("--station", "-s", help="Station code (auto-detect if omitted)")
    args = parser.parse_args()

    username = args.username or input("Username (email): ").strip()
    password = args.password or input("Password: ").strip()
    station_code = args.station or input("Station code (leave empty to auto-detect): ").strip() or None

    async with aiohttp.ClientSession() as session:
        # --- AES Key ---
        print("\n[1] GET /auth/aesKey")
        resp = await get(session, "/auth/aesKey")
        aes_key = resp.get("data")
        if aes_key:
            print(f"  OK — key: {aes_key[:8]}...")
            _save("01_aes_key.json", resp)
        else:
            print(f"  FAIL — {resp}")

        # --- Encrypt ---
        print("\n[2] Encrypt password (AES-128-ECB)")
        encrypted = password
        if aes_key:
            try:
                encrypted = _encrypt_password_aes(password, aes_key)
                print(f"  OK — {encrypted[:40]}...")
            except ImportError:
                print("  WARN — pycryptodome not installed, using plaintext")
            except Exception as e:
                print(f"  WARN — encryption failed: {e}, using plaintext")

        # --- Login (encrypted) ---
        print("\n[3] POST /auth/login (encrypted)")
        body = {"username": username, "password": encrypted, "loginType": "2", "app": True}
        login_resp = await post(session, "/auth/login", body)
        _save("02_login_encrypted.json", login_resp)

        token = login_resp.get("data")
        if isinstance(token, dict):
            token = token.get("data") or token.get("token")

        # --- Login (plaintext) fallback ---
        if not token or len(str(token)) < 10:
            print(f"  FAIL — {login_resp.get('msg')}")
            print("\n[3b] POST /auth/login (plaintext)")
            body2 = {"username": username, "password": password, "loginType": 2, "app": True}
            login_resp = await post(session, "/auth/login", body2)
            _save("03_login_plaintext.json", login_resp)
            token = login_resp.get("data")
            if isinstance(token, dict):
                token = token.get("data") or token.get("token")

        if not token or len(str(token)) < 10:
            print(f"  FAIL — no valid token")
            return

        token = str(token)
        print(f"  OK — token: {token[:30]}...")
        _save("04_token.json", {"token": token})

        # --- User info ---
        print("\n[4] GET /auth/info")
        resp = await get(session, "/auth/info", token)
        _save("05_user_info.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            print(f"  OK — user_id: {data.get('id')}")
        else:
            print(f"  FAIL — {resp}")

        # --- Current user station info ---
        print("\n[5] GET current user station info")
        resp = await get(session, "/dev/info/app/v1/station/info/appCurrentUserStationInfo", token)
        _save("06_current_user_station.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            print(f"  OK — {data}")
        else:
            print(f"  FAIL — {resp}")

        # --- Station list (POST) ---
        print("\n[6] POST station list (appPageStationBusinessNew)")
        resp = await post(session, "/dev/info/app/v1/station/info/appPageStationBusinessNew",
                          {"current": 1, "size": 20}, token)
        _save("07_station_list.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            records = data.get("records", data.get("list", [])) if isinstance(data, dict) else data
            count = len(records) if isinstance(records, list) else "?"
            print(f"  OK — {count} station(s)")
            if isinstance(records, list) and records:
                for i, r in enumerate(records):
                    sc = r.get("stationCode", "?")
                    sn = r.get("stationName", "?")
                    print(f"    [{i}] code={sc}  name={sn}")
                if not station_code:
                    station_code = records[0].get("stationCode")
                    print(f"  Auto-detected: {station_code}")
        else:
            print(f"  FAIL — {resp}")

        if not station_code:
            print("\nNo station code found. Exiting.")
            return

        print(f"\n  Using station: {station_code}")

        # --- Station detail ---
        print("\n[7] GET station detail")
        resp = await get(session, f"/dev/info/app/v1/station/info/appGetStationDetailV2?stationCode={station_code}", token)
        _save("08_station_detail.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            print(f"  OK — name: {data.get('stationName', 'N/A')}")
        else:
            print(f"  FAIL — {resp.get('msg')}")

        # --- Single station overview ---
        print("\n[8] GET single station overview")
        resp = await get(session, f"/business/app/v1/single/overview/appSingleStationOverviewData?stationCode={station_code}", token)
        _save("09_single_overview.json", resp)
        if resp.get("code") == 20000:
            print(f"  OK")
        else:
            print(f"  FAIL — {resp.get('msg')}")

        # --- Energy flow ---
        print("\n[9] GET energy flow diagram")
        resp = await get(session, f"/business/single/overview/stationEnergyFlowDiagram?stationCode={station_code}", token)
        _save("10_energy_flow.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            keys = list(data.keys()) if isinstance(data, dict) else "list"
            print(f"  OK — keys: {keys}")
        else:
            print(f"  FAIL — {resp.get('msg')}")

        # --- Energy flow realtime ---
        print("\n[10] GET energy flow real-time")
        resp = await get(session, f"/business/single/overview/stationEnergyFlowDiagramReTime?stationCode={station_code}", token)
        _save("11_energy_flow_realtime.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            keys = list(data.keys()) if isinstance(data, dict) else "list"
            print(f"  OK — keys: {keys}")
        else:
            print(f"  FAIL — {resp.get('msg')}")

        # --- SOC/SOH/Power (may return no data, SOC/SOH is in single overview) ---
        print("\n[11] GET SOC/SOH/Power")
        resp = await get(session, f"/business/single/overview/socSohAndPower?stationCode={station_code}", token)
        _save("12_soc_soh_power.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            keys = list(data.keys()) if isinstance(data, dict) else "list"
            print(f"  OK — keys: {keys}")
        else:
            print(f"  SKIP — {resp.get('msg')} (SOC/SOH data available in single overview)")

        # --- Inverter list (POST) ---
        print("\n[12] POST inverter list")
        resp = await post(session, "/dev/info/app/v1/devmonitor/appPageInverterMoniterList",
                          {"stationCode": station_code, "devTypeId": 1, "current": 1}, token)
        _save("13_inverter_list.json", resp)
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            records = data.get("records", data) if isinstance(data, dict) else data
            count = len(records) if isinstance(records, list) else "?"
            print(f"  OK — {count} inverter(s)")
            # Save first inverter devId for device realtime
            if isinstance(records, list) and records:
                inv = records[0]
                dev_id = inv.get("devId") or inv.get("id")
                if dev_id:
                    print(f"  First inverter devId: {dev_id}")
        else:
            print(f"  FAIL — {resp.get('msg', resp)}")

        # --- Storage inverter list (POST) ---
        print("\n[13] POST storage inverter list")
        resp = await post(session, "/dev/info/app/v1/devmonitor/appPageStoredInverterMoniterList",
                          {"stationCode": station_code, "devTypeId": 51, "current": 1}, token)
        _save("14_storage_list.json", resp)
        storage_dev_id = None
        if resp.get("code") == 20000:
            data = resp.get("data", {})
            records = data.get("records", data) if isinstance(data, dict) else data
            count = len(records) if isinstance(records, list) else "?"
            print(f"  OK — {count} storage device(s)")
            if isinstance(records, list) and records:
                storage_dev_id = records[0].get("devId")
                print(f"  devId: {storage_dev_id}")
        else:
            print(f"  FAIL — {resp.get('msg', resp)}")

        # --- Device realtime (storage inverter) ---
        if storage_dev_id:
            print(f"\n[14] POST device realtime (devId={storage_dev_id})")
            keys = "active_power,pv_total_power,mppt_day_cap,mppt_total_cap,temperature,uwBatPower_BMS,eps_total_active_power,devStatus,alarmed,uwRunMode,ammeter_active_power,ammeter_active_power_grid,ammeter_active_power_buy,ammeter_cap,ammeter_electricity_consumption,ammeter_r_u,ammeter_r_i,ammeter_r_f,ammeter2_active_power,ammeter2_cap,uwBatVolt_BMS,uwBatCurr_BMS,swBatTemp,BMS_status,uw_bat_cycle_times"
            resp = await post(session, "/dev/info/app/v1/devmonitor/appMonitorRelTime",
                              {"devId": storage_dev_id, "relTimeList": keys.split(",")}, token)
            _save("15_device_realtime.json", resp)
            if resp.get("code") == 20000:
                data = resp.get("data", {})
                print(f"  OK — keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
            else:
                print(f"  FAIL — {resp.get('msg')}")

    print(f"\n{'='*50}")
    print(f"Results: {RESULTS_DIR}/")
    print(f"Station: {station_code}")


if __name__ == "__main__":
    asyncio.run(main())
