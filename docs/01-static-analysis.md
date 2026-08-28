# Phase 1 — Static Analysis of sitSolar APK

## 1. App Identity

| Field | Value |
|---|---|
| Package name | `com.sitneng.solar` |
| App name | sitSolar |
| App ID (DCloud UniApp) | `__UNI__5F80E0E` |
| OEM / Manufacturer | **Si-Neng (SINENG Electric)** — `com.sineng.*` native modules |
| Framework | **DCloud UniApp** (cross-platform JS framework, compiled to native) |
| Apple App Store | `https://apps.apple.com/us/app/sit-solar/id6449988865` |
| Company website | `http://www.sitneng.com` |

**Key insight:** The entire business logic lives in a single 12MB compiled JavaScript bundle (`app-service.js`), not in native Java code. The native layer only provides BLE/WiFi/NFC plugins and push notification bridges. This means the API discovery was done entirely from the JS bundle, not from Retrofit/OkHttp.

---

## 2. Hosts / Base URLs

| Purpose | URL | Confidence |
|---|---|---|
| **Production API** | `https://enjoysolar.si-neng.com` | Confirmed from code |
| **Production API prefix** | `https://enjoysolar.si-neng.com/prod-api` | Confirmed |
| Test API | `https://testenjoysolar.si-neng.com` | Confirmed |
| Test CIM (chat/messaging) | `https://testcim.si-neng.com` | Confirmed |
| Bugfix server | `https://bugfixenjoysolar.si-neng.com` | Confirmed |
| Custom URL support | User-configurable via `setUrl` page | Confirmed |

The `setApiUrlPrefix` function allows users to override the base URL. The `getRequestUrlPrefix()` function resolves the full API base (defaults to `https://enjoysolar.si-neng.com/prod-api`).

---

## 3. Networking Libraries

| Layer | Library | Notes |
|---|---|---|
| HTTP client | **UniApp `uni.request`** | Built-in HTTP client, not OkHttp/Retrofit |
| WebSocket | **UniApp `uni.connectSocket`** | For real-time device data |
| Encryption | **CryptoJS Blowfish** | Password encryption before transmission |
| Serialization | **JSON** (native) | Request/response bodies |

**No Retrofit, no OkHttp, no Volley.** The entire networking layer is UniApp's built-in `uni.request` wrapper.

---

## 4. Authentication

### 4.1 Login Flow

The app supports **three login methods**:

| Method | `loginType` | Payload fields |
|---|---|---|
| Phone + SMS code | `0` | `{ loginType: 0, verCode, phoneOrEmail, app: true, phoneAreaCode }` |
| Email + SMS code | `1` | `{ loginType: 1, verCode, phoneOrEmail, app: true, phoneAreaCode }` |
| Username + Password | `2` | `{ username, password (encrypted), loginType: 2, app: true }` |

### 4.2 Auth API Endpoints

| Endpoint | Method | Purpose | Confidence |
|---|---|---|---|
| `/auth/login` | POST | Login (all methods) | Confirmed |
| `/auth/loginExperience` | POST | Demo/guest login | Confirmed |
| `/auth/logout` | POST | Logout | Confirmed |
| `/auth/info` | GET | Get current user info | Confirmed |
| `/auth/logOff` | POST | Cancel account | Confirmed |
| `/auth/aesKey` | GET | Get AES encryption key for passwords | Confirmed |
| `/auth/checkOff` | POST | Check if session is invalidated by another client | Confirmed |

### 4.3 Token Management

- **Token storage key:** `ids-app-token` (in device local storage)
- **Token format:** Bearer token
- **Authorization header:** `Authorization: Bearer <token>`
- **Token errors:**
  - `50008` — Token illegal
  - `50012` — Another client logged in
  - `50014` — Token expired
  - `50016` — Unauthorized

On token error, the app:
1. Calls `/auth/checkOff?checkInfo=<base64-encoded-token>&loginType=true`
2. If `data === 1`, the session was invalidated by another client
3. Otherwise, clears token and redirects to login

### 4.4 Password Encryption

Passwords are encrypted using **CryptoJS Blowfish** before being sent to the server:

1. App calls `GET /auth/aesKey` to get an encryption key (returned as Base64-encoded string)
2. Password is encrypted: `encryptedPassword = CryptoJS.Blowfish.encrypt(password, aesKey)`
3. The encrypted password is sent in the login request body

**Important:** The encryption key is fetched fresh from the server each time, so there is no hardcoded key to extract.

---

## 5. API Endpoints (Complete Catalog)

### 5.1 Core Station Endpoints

| Endpoint | Method | Purpose | Confidence |
|---|---|---|---|
| `/business/app/v1/total/overview/appStationOverviewData` | GET | Dashboard overview (all stations) | Confirmed |
| `/business/app/v1/single/overview/appSingleStationOverviewData` | GET | Single station overview | Confirmed |
| `/business/single/overview/stationEnergyFlowDiagram` | GET | Energy flow diagram data | Confirmed |
| `/business/single/overview/stationEnergyFlowDiagramReTime` | GET | Real-time energy flow refresh | Confirmed |
| `/business/single/overview/generatePowerAndPowerStatistic` | GET | Power generation statistics | Confirmed |
| `/business/single/overview/socSohAndPower` | GET | Battery SOC/SOH and power data | Confirmed |
| `/business/single/overview/singleStationKpiData` | GET | Station KPI data | Confirmed |
| `/business/single/overview/radiationAndPower` | GET | Solar radiation and power curve | Confirmed |
| `/business/total/overview/stationOverviewData` | GET | Total overview data | Confirmed |
| `/business/total/overview/getPowerCurve` | GET | Power curve data | Confirmed |
| `/dev/info/app/v1/station/info/appGetStationDetailV2` | GET | Station detail info | Confirmed |
| `/dev/info/app/v1/station/info/appPageStationBusinessNew` | GET | Station list with business data | Confirmed |
| `/dev/info/app/v1/station/info/appStationStatistic` | GET | Station statistics | Confirmed |
| `/dev/info/app/v1/station/info/appStationStatusCount` | GET | Station status counts | Confirmed |
| `/dev/info/station/info/singleOverviewStationData` | GET | Single station overview data | Confirmed |

### 5.2 Device Monitoring Endpoints

| Endpoint | Method | Purpose | Confidence |
|---|---|---|---|
| `/appMonitorRelTime` | GET | Real-time device monitoring data | Confirmed |
| `/dev/info/app/v1/devmonitor/appPageInverterMoniterList` | GET | Inverter monitoring list | Confirmed |
| `/dev/info/app/v1/devmonitor/appPageStoredInverterMoniterList` | GET | Storage inverter monitoring | Confirmed |
| `/dev/info/devmonitor/getStoredInverterDevMonitorDetailMonitor` | GET | Storage inverter detail | Confirmed |
| `/dev/info/devmonitor/getStoredInverterBatteryMonitor` | GET | Battery monitoring detail | Confirmed |
| `/dev/info/devmonitor/getStoredInverterAmmeterMonitor` | GET | Ammeter monitoring | Confirmed |
| `/getAppInverterDevMonitorDetailInfo/` | GET | Inverter detail info | Confirmed |
| `/getAppInverterDevMonitorDetailMonitor/` | GET | Inverter real-time monitor | Confirmed |
| `/dev/info/devmonitor/getBatteryClusterMonitorDetailInfo/` | GET | Battery cluster detail | Confirmed |
| `/dev/info/devmonitor/pageBatteryClusterMoniterList` | GET | Battery cluster list | Confirmed |
| `/dev/info/devmonitor/pageEnergyQualityMoniterList` | GET | Power quality monitoring | Confirmed |
| `/dev/info/devmonitor/centralizedInverterRelTime` | GET | Centralized inverter real-time | Confirmed |

### 5.3 Alarm Endpoints

| Endpoint | Method | Purpose | Confidence |
|---|---|---|---|
| `/dev/info/app/v1/alarm/appAlarmMessageNum` | GET | Unread alarm count | Confirmed |
| `/dev/info/app/v1/alarm/appPageDevAlarmDeadly` | GET | Critical alarms | Confirmed |
| `/dev/info/app/v1/alarm/appMonitorCompletePercent` | GET | Monitor completion % | Confirmed |
| `/alarm/deadly/push/getByUserId` | GET | User alarm notifications | Confirmed |

### 5.4 User / Account Endpoints

| Endpoint | Method | Purpose | Confidence |
|---|---|---|---|
| `/sm/user/info/getCode` | GET | Get user info | Confirmed |
| `/dev/info/dev/user/unit/getUnitByUserId` | GET | User unit preferences | Confirmed |
| `/appGetCurrentUserInfo` | GET | Current user info | Confirmed |
| `/appUpdateCurrentUserInfo` | POST | Update user info | Confirmed |
| `/appUdateCurrentUserPassword` | POST | Change password | Confirmed |

### 5.5 Miscellaneous Endpoints

| Endpoint | Method | Purpose | Confidence |
|---|---|---|---|
| `/dev/info/weather/getWeatherDailyHf` | GET | Weather data | Confirmed |
| `/dev/info/app/v1/alarm/appGetAlarmMessageList` | GET | Alarm message list | Confirmed |
| `/sm/cim/room/getRoom` | GET | Chat room (customer service) | Confirmed |
| `/sm/cim/message/getPushPrefix` | GET | Push notification prefix | Confirmed |
| `/fs/upload` | POST | File upload | Confirmed |
| `/station/share/page` | GET | Shared stations | Confirmed |
| `/dev/info/station/flow/getByUserId` | GET | Energy flow mode settings | Confirmed |
| `/dev/info/charge/record/getAppRecordList` | GET | Charge/discharge records | Confirmed |
| `/business/station/report/pageMonthReportByCurrentUser` | GET | Monthly reports | Confirmed |

---

## 6. Data Models (Signal Fields)

### 6.1 Inverter Real-Time Fields (`keyMonitor`)

| Field Key | Description | Unit | Auth ID |
|---|---|---|---|
| `active_power` | Inverter active power | kW | 4277 |
| `pv_total_power` | Total PV power | kW | 4228 |
| `uwBatPower_BMS` | Battery power (from BMS) | kW | — |
| `eps_total_active_power` | EPS total active power | kW | — |
| `mppt_day_cap` | MPPT daily energy | kWh | 4243 |
| `mppt_total_cap` | MPPT total energy | kWh | 4257 |

### 6.2 Inverter Extended Fields (`stMonitor`)

| Field Key | Description | Unit | Auth ID |
|---|---|---|---|
| `activePowerProduct` | Active power (product) | kW | 4277 |
| `activePowerInner` | Active power (inner) | kW | 4278 |
| `reactive_power` | Reactive power | kVar | 4279 |
| `mppt_power` | MPPT power | kW | 4228 |
| `pvCapacitys` | PV capacity | kWp | 4212 |
| `temperature` | Temperature | °C | 4281 |
| `uwINVSink_Temp` | Inverter sink temperature | °C | 4282 |
| `uwBatSink1_Temp` | Battery sink temperature | °C | 4283 |
| `buckboost_tempure` | Buck-boost temperature | °C | 4284 |

### 6.3 Grid/Ammeter Fields (`ammerOnlineCommon`)

| Field Key | Description | Unit | Auth ID |
|---|---|---|---|
| `ammeter_active_power_grid` | Grid export power (positive = export) | kW | 4313 |
| `ammeter_active_power_buy` | Grid import power (absolute value when importing) | kW | 4314 |
| `ammeter_active_power` | Raw grid power (signed: positive=export, negative=import) | kW | — |
| `ammeter_cap` | Grid meter cumulative energy | kWh | 4317 |
| `ammeter_electricity_consumption` | Total electricity consumption | kWh | 4318 |

### 6.4 Grid Per-Phase Fields (3-phase)

| Field Key | Description | Unit |
|---|---|---|
| `ammeter_r_u` / `ammeter_s_u` / `ammeter_t_u` | Phase voltage (R/S/T) | V |
| `ammeter_r_i` / `ammeter_s_i` / `ammeter_t_i` | Phase current (R/S/T) | A |
| `ammeter_r_f` / `ammeter_s_f` / `ammeter_t_f` | Phase frequency (R/S/T) | Hz |
| `ammeter_r_p` / `ammeter_s_p` / `ammeter_t_p` | Phase power (R/S/T) | kW |

### 6.5 Load/Home Consumption Fields (`ammerLoadCommon`)

| Field Key | Description | Unit | Auth ID |
|---|---|---|---|
| `ammeter2_active_power` | Load/home consumption power | kW | 4323 |
| `ammeter2_cap` | Load meter cumulative energy | kWh | 4326 |

### 6.6 Battery Fields (`batteryInfoTop`)

| Field Key | Description | Unit | Auth ID |
|---|---|---|---|
| `uwBatVolt_BMS` | Battery voltage | V | 4300 |
| `uwBatCurr_BMS` | Battery current | A | 4301 |
| `uwBatPower_BMS` | Battery power | kW | — |
| `swBatTemp` | Battery temperature | °C | 4298 |
| `uw_bat_volt_max_chg` | Max charge voltage | V | — |
| `uw_bat_volt_max_dis` | Max discharge voltage | V | — |

### 6.7 Status Fields

| Field Key | Description | Auth ID |
|---|---|---|
| `devStatus` | Device running status | 4216 |
| `alarmed` | Alarm status | 4217 |
| `uwRunMode` | Run mode | 4218 |
| `BMS_status` | Battery management status | 4295 |
| `bat_err_flag` | Battery error flag | — |

### 6.8 Weather Station Fields

| Field Key | Description | Unit |
|---|---|---|
| `today_radiant_total` | Today's solar radiation total | MJ/m² |
| `wind_speed` | Wind speed | m/s |
| `wind_direction` | Wind direction | ° |
| `humidity` | Humidity | %RH |
| `temperature` | Temperature | °C |
| `nw_radiant_total` | Radiation power | W/m² |
| `pressure` | Atmospheric pressure | kPa |
| `day_rainfall` | Daily rainfall | mm |

---

## 7. WebSocket (Real-Time Data)

### 7.1 Connection

```
WebSocket URL: wss://{host}/prod-ws/ws/dev/{userId}?access_token={token}
```

| Component | Source |
|---|---|
| `host` | Extracted from API base URL |
| `userId` | From `myinfo.id` (stored in local storage) |
| `token` | From `ids-app-token` |

The WebSocket provides real-time device data updates. The app polls via HTTP every ~10 seconds for the energy flow diagram, and uses WebSocket for push notifications (alarms, status changes).

### 7.2 Chat WebSocket (CIM)

A separate WebSocket is used for customer service chat:
```
wss://{host}/prod-ws/ws/dev/{userId}?access_token={token}
```

---

## 8. Push Notifications

| Service | Keys |
|---|---|
| JPush | `b288d921a42a547848869d48` (app key) |
| Xiaomi MiPush | App ID: `2882303761520126016` |
| OPPO Push | App ID: `30720883`, Secret: `5d1e04e8525d4abf8e86c22a9fd12ceb` |
| Vivo Push | API Key: `1f6c62a92001b42ddbbc711e2b140fb4`, App ID: `105642849` |
| Huawei Push | Via JPush plugin |
| FCM | Via JPush plugin |

**Not relevant for the HA integration** (push notifications are not needed for polling).

---

## 9. Hardcoded Secrets / API Keys

| Key | Value | Purpose |
|---|---|---|
| DCloud AppKey | `9d6f7739d8397839990d93db358bfc7d` | DCloud platform |
| WeChat AppID | `wx188d723d528ae736` | WeChat login (not needed for HA) |
| Google Maps API Key | Referenced as `mapKey.gmapWeb` (value not hardcoded in JS) | Geocoding |
| Tianditu Map Key | Referenced as `mapKey.Tmap` (value not hardcoded in JS) | Geocoding (China) |

**No API keys are needed for the core REST API** — authentication is purely token-based via username/password.

---

## 10. Error Codes (Relevant)

| Code | Meaning |
|---|---|
| `20000` | Success |
| `50008` | Token illegal |
| `50012` | Another client logged in |
| `50014` | Token expired |
| `50016` | Unauthorized |
| `10005` | User not logged in |
| `11000` | Username or password error |
| `11001` | Login system error |
| `11002` | Token does not exist |
| `11003` | Account disabled |

---

## 11. Summary

**What we know with high confidence (from code analysis):**
- Complete authentication flow (login, token, logout, AES encryption)
- Base URL and API prefix
- All endpoint paths and HTTP methods
- All data model field names and types for inverter, battery, grid, load, weather
- WebSocket URL pattern for real-time data
- Token storage and refresh mechanism

**What we cannot determine without live traffic:**
- Exact JSON response shapes (we have field names but not the nesting structure)
- Whether endpoints use GET query params or POST body for some requests
- Rate limits and minimum safe polling intervals
- Exact behavior of some error handling paths
- Whether some endpoints require specific query parameters (e.g., `stationCode`)

**Confidence level:** ~85% — The code analysis gives us a very solid foundation. The remaining gaps can be filled by testing the generated integration against a real account.
