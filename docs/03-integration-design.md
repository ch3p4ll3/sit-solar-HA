# sitSolar Integration Design

## End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Home Assistant                               │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │  Config Flow  │───▶│  SitSolar API    │───▶│  Sensor      │  │
│  │  (username/   │    │  Client (api.py) │    │  Entities    │  │
│  │   password)   │    │                  │    │  (sensor.py) │  │
│  └──────────────┘    │  ┌────────────┐  │    └──────────────┘  │
│                      │  │ Token Mgmt │  │                       │
│                      │  │ (login,    │  │    ┌──────────────┐  │
│                      │  │  refresh)  │  │    │  Energy      │  │
│                      │  └────────────┘  │    │  Dashboard   │  │
│                      └──────────────────┘    │  Sensors     │  │
│                               │              └──────────────┘  │
│                               ▼                                 │
│                      ┌──────────────────┐                      │
│                      │ DataUpdateCoord  │                      │
│                      │ (coordinator.py) │                      │
│                      │ Default: 30s     │                      │
│                      └──────────────────┘                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              sitSolar Cloud API                                  │
│              https://enjoysolar.si-neng.com/prod-api             │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ /auth/login      │  │ /business/.../  │  │ /appMonitor    │  │
│  │ (token)          │  │ stationEnergy   │  │ RelTime        │  │
│  │                  │  │ FlowDiagram     │  │ (device RT)    │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ /auth/aesKey     │  │ /dev/info/.../  │                      │
│  │ (password enc)   │  │ appGetStation   │                      │
│  │                  │  │ DetailV2        │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

## Entity Mapping

### Energy Dashboard Sensors (total_increasing, kWh)

| Sensor | API Endpoint | Response Field | Unit | Notes |
|---|---|---|---|---|
| PV Production Total | `stationEnergyFlowDiagram` | Computed from `mppt_day_cap` | kWh | Daily total |
| Grid Import Total | `stationEnergyFlowDiagram` | `ammeter_electricity_consumption` | kWh | Cumulative |
| Grid Export Total | `stationEnergyFlowDiagram` | `ammeter_cap` | kWh | Cumulative |
| Battery Charge Total | `stationEnergyFlowDiagram` | Inferred from battery power integral | kWh | Needs runtime verification |
| Battery Discharge Total | `stationEnergyFlowDiagram` | Inferred from battery power integral | kWh | Needs runtime verification |

### Power Sensors (measurement, W)

| Sensor | API Endpoint | Response Field | Unit | Notes |
|---|---|---|---|---|
| PV Production Power | `stationEnergyFlowDiagram` | `pvPower` | kW → W | Convert kW to W |
| Grid Power | `stationEnergyFlowDiagram` | `activePower` or `buyPower`/`ongridPower` | kW → W | Signed or split |
| Battery Power | `stationEnergyFlowDiagram` | `batteryPower` | kW → W | +discharge, -charge |
| House Load Power | `stationEnergyFlowDiagram` | `loadPower` | kW → W | Computed: PV + Grid - Battery |

### Battery Sensors

| Sensor | API Endpoint | Response Field | Unit | Notes |
|---|---|---|---|---|
| Battery SOC | `socSohAndPower` | `soc` | % | State of charge |
| Battery SOH | `socSohAndPower` | `soh` | % | State of health |
| Battery Voltage | `appMonitorRelTime` | `uwBatVolt_BMS` | V | From device |
| Battery Current | `appMonitorRelTime` | `uwBatCurr_BMS` | A | From device |
| Battery Temperature | `appMonitorRelTime` | `swBatTemp` | °C | From device |

### Extra Sensors (if available)

| Sensor | API Endpoint | Response Field | Unit | Notes |
|---|---|---|---|---|
| Inverter Temperature | `appMonitorRelTime` | `temperature` | °C | — |
| Grid Frequency | `appMonitorRelTime` | `ammeter_r_f` | Hz | Per-phase |
| Grid Voltage (R) | `appMonitorRelTime` | `ammeter_r_u` | V | Per-phase |
| Grid Current (R) | `appMonitorRelTime` | `ammeter_r_i` | A | Per-phase |
| Battery Cycle Count | `appMonitorRelTime` | `uw_bat_cycle_times` | — | Lifetime cycles |

## Auth Strategy

### Login Flow

1. User provides username/email + password via config flow
2. Attempt `POST /auth/login` with `loginType: 2` (password)
3. If server requires encrypted password:
   a. Fetch key from `GET /auth/aesKey`
   b. Encrypt password with Blowfish
   c. Retry login with encrypted password
4. Store token in HA config entry
5. On subsequent requests, use `Authorization: Bearer <token>`

### Token Refresh / Expiry

- Tokens appear to be long-lived (the app doesn't implement explicit refresh)
- On error codes `50008`, `50012`, `50014`, `50016`: re-login automatically
- The `DataUpdateCoordinator` will handle re-login on auth failures

### Session Expiry Handling

```python
async def _handle_auth_error(self, error_code: int) -> None:
    """Handle authentication errors by re-logging in."""
    if error_code in (50008, 50012, 50014, 50016):
        await self._login()
```

## Polling Strategy

| Data | App Polling Interval | Recommended HA Interval | Rationale |
|---|---|---|---|
| Energy flow (power) | 10 seconds | 30 seconds | App uses 10s; 30s is safe margin |
| Station overview | On demand | 5 minutes | Summary data, not real-time |
| Device details | On demand | 5 minutes | Static-ish device info |
| Alarms | WebSocket push | 5 minutes | Compensate for no WS in HA |
| SOC/SOH | On demand | 5 minutes | Battery state changes slowly |

**Default coordinator interval: 30 seconds** (configurable in config flow).

## Known / Likely Constraints

1. **Rate limits:** Not explicitly found in code. The app polls energy flow every 10 seconds. Conservative recommendation: don't poll faster than every 15 seconds. We use 30 seconds as default.

2. **Token expiry:** Not documented. The app handles error codes 50008/50012/50014/50016 as token invalidation. No refresh token mechanism found — re-login is the recovery path.

3. **Single-session:** Error code `50012` ("Another client logged in") suggests the API may only allow one active session per user. This is critical: if the user opens the sitSolar app while HA is running, HA may get logged out. This is a common pattern in solar monitoring apps.

4. **Custom URL support:** The app allows users to set a custom API URL. If the user's installation uses a non-default server, they'll need to configure this in the HA integration.

## Verification Steps (Post-Deployment)

Since no live traffic was captured, here's how to verify the integration works:

1. **Basic connectivity:** Configure the integration with real credentials. Check HA logs for successful login (token received).

2. **Data validation:** Compare HA sensor values with the sitSolar app running side-by-side. Values should match within ±1 (accounting for timing differences).

3. **If MITM becomes available later:**
   - Capture a single login request to verify exact payload format
   - Capture `stationEnergyFlowDiagram` response to verify exact JSON nesting
   - Capture `appMonitorRelTime` response to verify field availability

4. **Quick test with curl:**
   ```bash
   # Login
   curl -X POST https://enjoysolar.si-neng.com/prod-api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"your-email","password":"your-password","loginType":2,"app":true}'
   
   # Use returned token
   curl https://enjoysolar.si-neng.com/prod-api/business/single/overview/stationEnergyFlowDiagram \
     -H "Authorization: Bearer <token>" \
     -G --data-urlencode "stationCode=YOUR_STATION_CODE"
   ```
