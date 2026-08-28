# sitSolar Home Assistant Integration

A custom Home Assistant integration for monitoring solar PV systems via the **sitSolar** (EnjoySolar) cloud platform by **Sineng Electric**.

## Features

- **Real-time power monitoring**: PV production, grid import/export, battery charge/discharge, house load
- **Battery monitoring**: State of charge (SOC), state of health (SOH)
- **Energy Dashboard compatible**: Proper `device_class` and `state_class` for HA Energy Dashboard
- **Automatic re-login**: Handles token expiry gracefully
- **Multi-station support**: Configure multiple solar stations

## Supported Entities

### Power Sensors (kW)
| Sensor | Description |
|---|---|
| `sensor.sitsolar_pv_production_power` | Total PV inverter output power |
| `sensor.sitsolar_grid_power` | Net grid power (positive = export) |
| `sensor.sitsolar_grid_import_power` | Power imported from grid |
| `sensor.sitsolar_grid_export_power` | Power exported to grid |
| `sensor.sitsolar_battery_power` | Battery power (+discharge, -charge) |
| `sensor.sitsolar_house_load_power` | Home/consumption power |
| `sensor.sitsolar_eps_backup_power` | EPS backup power |

### Battery Sensors
| Sensor | Description |
|---|---|
| `sensor.sitsolar_battery_state_of_charge` | Battery SOC (%) |
| `sensor.sitsolar_battery_state_of_health` | Battery SOH (%) |

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** → **Custom repositories**
3. Add this repository URL: `https://github.com/ch3p4ll3/sit-solar-ha`
4. Select **Integration** as the category
5. Click **Install**
6. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/sitsolar` folder from this repository
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **sitSolar**
3. Enter your credentials:
   - **Username**: Email or phone number used in the sitSolar app
   - **Password**: Your sitSolar password
   - **Base URL**: (Optional) Default is `https://enjoysolar.si-neng.com`
4. Select your station from the list (if you have multiple)
5. The integration will start polling data every 30 seconds

## Configuration Options

After setup, you can configure:
- **Polling interval**: Default is 30 seconds. The sitSolar app polls every 10 seconds, but 30 seconds is recommended to avoid rate limiting.

## Troubleshooting

### "Invalid username or password"
- Verify your credentials by logging into the sitSolar app
- If you use phone+SMS login, you may need to create a password via the app's "forgot password" flow

### "Failed to connect"
- Check your internet connection
- Verify the base URL is correct (default: `https://enjoysolar.si-neng.com`)
- The server may be temporarily down

### Entities showing "Unavailable"
- The integration will automatically re-login when the token expires
- If persistent, try reloading the integration or restarting Home Assistant

### "Another client logged in" errors
- The sitSolar API may only allow one active session
- If you open the sitSolar app while HA is running, HA may get logged out temporarily
- The integration will automatically re-login on the next poll

## API Notes

This integration was built through **static analysis** of the sitSolar APK (decompiled with jadx/apktool). The API endpoints and data models were extracted from the compiled JavaScript bundle of the DCloud UniApp framework.

### Confidence Levels

| Component | Confidence |
|---|---|
| Authentication flow | **High** — extracted from clear JS code |
| Base URL and API prefix | **High** — hardcoded in source |
| Endpoint paths | **High** — extracted from request module |
| Response field names | **High** — extracted from signal model definitions |
| Response JSON structure | **Medium** — inferred from field usage patterns |
| Rate limits | **Unknown** — not documented, conservatively set to 30s polling |

### Verification

To verify the integration works correctly:
1. Compare HA sensor values with the sitSolar app running side-by-side
2. Check HA logs for any API errors
3. If you have MITM proxy access, capture a single request to verify exact JSON structure

## Privacy & Security

- Credentials are stored in Home Assistant's encrypted config storage
- Passwords are never logged
- All communication uses HTTPS
- The integration only reads data — no write/control operations

## License

MIT License
