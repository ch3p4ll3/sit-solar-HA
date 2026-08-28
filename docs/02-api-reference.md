# sitSolar API Reference

> **Confidence key:**
> - **Confirmed** = extracted from decompiled code AND verified against live API
> - **Inferred** = reconstructed from code patterns, not yet verified

## Base Configuration

| Field | Value |
|---|---|
| Base URL | `https://enjoysolar.si-neng.com` |
| API Prefix | `/prod-api` |
| Full Base | `https://enjoysolar.si-neng.com/prod-api` |
| Auth Header | `Authorization: Bearer <token>` |
| Content-Type | `application/json` |
| Token Storage Key | `ids-app-token` |

---

## Authentication

### POST `/auth/login`

Login with username+password.

**Request Body:**
```json
{
  "username": "your-username",
  "password": "<aes-encrypted-password>",
  "loginType": 2,
  "app": true
}
```

| Field | Type | Notes |
|---|---|---|
| `loginType` | int | Always `2` for password login |
| `username` | string | Username |
| `password` | string | AES-128-ECB encrypted password |
| `app` | bool | Always `true` |

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": "ea6ba5c4-be0f-4cd6-8c38-784394ea5b8d",
  "success": true
}
```

> **Password Encryption (REQUIRED):**
>
> 1. Fetch key: `GET /auth/aesKey` → Base64-encoded 16-byte key
> 2. Decode key from Base64
> 3. Encrypt with **AES-128-ECB/PKCS7** (no IV)
> 4. Output: raw Base64 ciphertext (no "Salted__" prefix)
> 5. Send encrypted password in login request
>
> Matches `CryptoJS.AES.encrypt(password, CryptoJS.enc.Utf8.parse(key))` with `mode: ECB, padding: Pkcs7`.

### GET `/auth/aesKey`

Get AES encryption key for password.

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": "RjVNV1l5UVNCRGpiV0RhMw==",
  "success": true
}
```

### GET `/auth/info`

Get current user information.

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "id": 81322,
    "loginName": "username",
    "userName": "User Name",
    "email": "user@example.com",
    "phone": "3478838002",
    "type": "appUser"
  },
  "success": true
}
```

### POST `/auth/logout`

Logout (invalidate token).

---

## Station Endpoints

### POST `/dev/info/app/v1/station/info/appPageStationBusinessNew`

Get paginated station list.

**Request Body:**
```json
{
  "current": 1,
  "size": 20
}
```

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "records": [
      {
        "stationName": "Vidoni Lorenzo",
        "stationAddr": "Via Sornico Superiore, 21/1, 33011 Sornico Superiore UD, Italia",
        "stationCode": "38f5971efa0346708b06ec0ac4cbdf8b",
        "installedCapacity": 6.0,
        "communicateStatus": 1,
        "alarmStatus": 0,
        "activePower": -0.738,
        "operatingDay": 46,
        "stationStatus": 1,
        "equivalentHour": 1.02,
        "stationType": 2,
        "onlineType": 4,
        "enterpriseId": 40020,
        "enterpriseName": "FuturaSun Srl",
        "disEnterpriseId": 40161,
        "disEnterpriseName": "ENERSOLARE",
        "produceDate": "2026-07-13 00:00:00",
        "batteryStatus": 1,
        "todayProductPower": 6.1,
        "totalProductPower": 271.6,
        "mpptPower": 2.36,
        "mpptDayCap": 3.4,
        "mpptTotalCap": 270.2
      }
    ],
    "total": 1,
    "size": 20,
    "current": 1,
    "pages": 1
  },
  "success": true
}
```

### GET `/dev/info/app/v1/station/info/appCurrentUserStationInfo`

Get current user's station count and type info.

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "stationCount": 1,
    "type": "appUser"
  },
  "success": true
}
```

### GET `/dev/info/app/v1/station/info/appGetStationDetailV2`

Get detailed station information.

**Query params:** `stationCode=<station-code>`

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "stationInfo": {
      "id": 52910,
      "stationCode": "38f5971efa0346708b06ec0ac4cbdf8b",
      "stationName": "Vidoni Lorenzo",
      "installedCapacity": 6.0,
      "installedCapacityGc": 10.65,
      "stationType": 2,
      "onlineType": 4,
      "produceDate": "2026-07-13 00:00:00",
      "latitude": 46.25914,
      "longitude": 13.155078,
      "country": "Italy",
      "timeZone": "Europe/Amsterdam",
      "moneyType": "USD",
      "enterpriseName": "FuturaSun Srl",
      "disEnterpriseName": "ENERSOLARE"
    },
    "attention": 0,
    "communicateStatus": 1,
    "alarmStatus": 0
  },
  "success": true
}
```

### GET `/business/app/v1/total/overview/appStationOverviewData`

Get dashboard overview for all stations.

**Query params:** `queryMoneyCode=false`

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "installedCapacity": 6.0,
    "activePower": -0.782,
    "todayProductPower": 4.5,
    "todayIncome": 0.0,
    "todayEquivalentHour": 0.75,
    "todayBuyGridPower": 0.0,
    "todayOngridPower": 0.1,
    "todaySelfUsePower": 3.7,
    "thisMonthProductPower": 510.5,
    "thisMonthBuyGridPower": 3.8,
    "thisMonthOngridPower": 135.4,
    "thisMonthSelfUsePower": 344.4,
    "thisYearProductPower": 873.6,
    "thisYearBuyGridPower": 0.0,
    "thisYearOngridPower": 241.5,
    "thisYearSelfUsePower": 582.2,
    "totalProductPower": 271.6,
    "totalBuyGridPower": 7.2,
    "totalOngridPower": 241.5,
    "totalSelfUsePower": 582.2,
    "uwBatSoc": 60.0,
    "batterySoh": 60.0,
    "todayCellDischarge": 2.5,
    "todayCellCharge": 2.7,
    "cellChargePower": 2.884,
    "cellDisChargePower": 0.0,
    "ammeterActivePowerToGrid": 0.0,
    "ammeterActivePowerFromGrid": 0.022
  },
  "success": true
}
```

### GET `/business/app/v1/single/overview/appSingleStationOverviewData`

Get single station overview (includes power, energy, SOC, SOH).

**Query params:** `stationCode=<station-code>`

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "installedCapacity": 6.0,
    "activePower": -0.738,
    "todayProductPower": 6.1,
    "todayEquivalentHour": 1.02,
    "todayBuyGridPower": 0.0,
    "todayOngridPower": 0.1,
    "todaySelfUsePower": 5,
    "todayCellDischarge": 2.5,
    "todayCellCharge": 3.9,
    "todayLoadUseGridPower": 0.0,
    "todayLoadUseBatteryPower": 2.5,
    "todayLoadUsePvPower": 2.2,
    "todayLoadUsePower": 4.7,
    "todayPvToGridProductPower": 0,
    "todayPvToBatteryProductPower": 2.8,
    "todayGfToLoadProductPower": 2.2,
    "totalProductPower": 271.6,
    "totalBuyGridPower": 7.2,
    "totalOngridPower": 241.5,
    "totalSelfUsePower": 583.5,
    "uwBatSoc": 71,
    "batterySoh": 71,
    "safeRunDatetime": 45,
    "cellChargePower": 3.004,
    "cellDisChargePower": 0,
    "ammeterActivePowerToGrid": 0.114,
    "ammeterActivePowerFromGrid": 0,
    "electricityConsumption": 58.1,
    "timeZone": "Europe/Amsterdam",
    "updateTime": "2026-08-28 06:10:02"
  },
  "success": true
}
```

---

## Real-Time Energy Flow

### GET `/business/single/overview/stationEnergyFlowDiagram`

Get real-time power flow between PV, battery, grid, and load.

**Query params:** `stationCode=<station-code>`

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "stationCode": "38f5971efa0346708b06ec0ac4cbdf8b",
    "stationName": "Vidoni Lorenzo",
    "stationType": 2,
    "onlineType": 4,
    "stationStatus": 1,
    "dataUpdateTime": 1787909700000,
    "mpptPower": 2.36,
    "batteryPower": -3.004,
    "batterySocAver": 71.0,
    "ongridPower": 0.114,
    "buyPower": 0,
    "loadPower": 0.975,
    "batteryStatus": 1,
    "evChargerStatus": 0,
    "uwEPS_P_R": 0,
    "acCoupleGfActivePower": 1.733,
    "ammeterEnableSign": true,
    "remainAvailEnergy": 7.0,
    "remainChargeFullTime": 1.03
  },
  "success": true
}
```

| Field | Description | Unit |
|---|---|---|
| `mpptPower` | Total PV inverter power | kW |
| `batteryPower` | Battery power (negative=charging) | kW |
| `batterySocAver` | Battery SOC average | % |
| `ongridPower` | Grid export power | kW |
| `buyPower` | Grid import power | kW |
| `loadPower` | Home/load consumption | kW |
| `acCoupleGfActivePower` | AC-coupled inverter power | kW |
| `uwEPS_P_R` | EPS backup power | kW |
| `remainAvailEnergy` | Remaining available battery energy | kWh |
| `remainChargeFullTime` | Time to full charge | hours |

### GET `/business/single/overview/stationEnergyFlowDiagramReTime`

Real-time refresh of energy flow data. Same response shape.

**Query params:** `stationCode=<station-code>`

> **Polling:** App refreshes every **10 seconds**. HA integration recommends **30 seconds**.

---

## Device Monitoring

### POST `/dev/info/app/v1/devmonitor/appPageStoredInverterMoniterList`

Get storage inverter monitoring list.

**Request Body:**
```json
{
  "stationCode": "<station-code>",
  "devTypeId": 51,
  "current": 1
}
```

**Response (Confirmed):**
```json
{
  "code": 20000,
  "data": {
    "records": [
      {
        "devId": 3019048,
        "devName": "300017941261010166",
        "sn": "300017941261010166",
        "devStatus": 1,
        "alarmed": 0,
        "pvTotalPower": 2.36,
        "dayCap": 3.4,
        "uwRunMode": 2,
        "devTypeId": 51
      }
    ],
    "total": 1
  },
  "success": true
}
```

### POST `/dev/info/app/v1/devmonitor/appMonitorRelTime`

Get real-time device monitoring data.

**Request Body:**
```json
{
  "devId": 3019048,
  "relTimeList": ["active_power", "pv_total_power", "uwBatPower_BMS"]
}
```

> **Polling:** App refreshes every **10 seconds**.

---

## WebSocket (Notifications Only)

### `wss://{host}/prod-ws/ws/dev/{userId}?access_token={token}`

WebSocket for notification badges only — **not** for solar data.

**Pushes:**
- `businessType: 100` → notification count updates

**Heartbeat:** Every 5 minutes (`{heartbeatCheck: true}`)

---

## Polling Rates Summary

| Data Type | App Polling | HA Recommendation |
|---|---|---|
| Energy flow (real-time power) | 10 seconds | 30 seconds |
| Device realtime (voltage, current) | 10 seconds | 30 seconds |
| Station overview | 120 seconds | 300 seconds |
| Notification counts | 60 seconds | N/A (use WebSocket) |

> **Note:** All solar monitoring data is pulled via REST polling. WebSocket is only for notification badges. No MQTT in the mobile app.

---

## Error Codes

| Code | Meaning | Action |
|---|---|---|
| `20000` | Success | Process data |
| `10008` | Dynamic error | Parse `msg` JSON for `deCode` |
| `10039` | No station access | Check station permissions |
| `10055` | No data | Endpoint has no data for this station |
| `11000` | Username/password error | Show error |
| `11218` | Station info not found | Check station code |
| `50008` | Token illegal | Re-login |
| `50012` | Another client logged in | Re-login |
| `50014` | Token expired | Re-login |
| `50016` | Unauthorized | Re-login |

---

## Data Model Reference

### Energy Flow Fields

| Field | Description | Unit |
|---|---|---|
| `mpptPower` | Total PV power | kW |
| `batteryPower` | Battery power (- charge, + discharge) | kW |
| `batterySocAver` | Battery SOC | % |
| `ongridPower` | Grid export | kW |
| `buyPower` | Grid import | kW |
| `loadPower` | Home load | kW |
| `acCoupleGfActivePower` | AC-coupled inverter | kW |
| `uwEPS_P_R` | EPS backup power | kW |

### Device Realtime Fields

| Field | Description | Unit |
|---|---|---|
| `active_power` | Inverter active power | kW |
| `pv_total_power` | Total PV power | kW |
| `uwBatPower_BMS` | Battery power (BMS) | kW |
| `uwBatVolt_BMS` | Battery voltage | V |
| `uwBatCurr_BMS` | Battery current | A |
| `swBatTemp` | Battery temperature | °C |
| `BMS_status` | BMS status | — |
| `uw_bat_cycle_times` | Battery cycle count | — |
| `ammeter_active_power` | Grid power (signed) | kW |
| `ammeter_active_power_grid` | Grid export | kW |
| `ammeter_active_power_buy` | Grid import | kW |
| `ammeter2_active_power` | Load power | kW |
| `devStatus` | Device status | — |
| `temperature` | Inverter temperature | °C |
