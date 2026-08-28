# sitSolar API — Received Payloads Documentation

> **Status:** Verified against live API responses
>
> All example values are sanitized. Real data removed.

---

## 1. AES Key — `GET /auth/aesKey`

```json
{
  "code": 20000,
  "data": "<base64-encoded-16-byte-key>",
  "success": true
}
```

---

## 2. Login — `POST /auth/login`

```json
{
  "code": 20000,
  "data": "<uuid-token>",
  "success": true
}
```

---

## 3. User Info — `GET /auth/info`

```json
{
  "code": 20000,
  "data": {
    "id": 12345,
    "loginName": "username",
    "userName": "User Name",
    "email": "user@example.com",
    "phone": "1234567890",
    "type": "appUser"
  },
  "success": true
}
```

---

## 4. Station Count — `GET /dev/info/app/v1/station/info/appStationCount`

```json
{
  "code": 20000,
  "data": 1,
  "success": true
}
```

---

## 5. Station List — `POST /dev/info/app/v1/station/info/appPageStationBusinessNew`

```json
{
  "code": 20000,
  "data": {
    "records": [
      {
        "stationName": "My Solar Plant",
        "stationAddr": "Address, City, Country",
        "stationCode": "<uuid-station-code>",
        "installedCapacity": 6.0,
        "communicateStatus": 1,
        "alarmStatus": 0,
        "activePower": -0.738,
        "operatingDay": 46,
        "stationStatus": 1,
        "equivalentHour": 1.02,
        "stationType": 2,
        "onlineType": 4,
        "enterpriseName": "OEM Name",
        "disEnterpriseName": "Distributor Name",
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

---

## 6. Station Detail — `GET /dev/info/app/v1/station/info/appGetStationDetailV2`

```json
{
  "code": 20000,
  "data": {
    "stationInfo": {
      "id": 12345,
      "stationCode": "<uuid-station-code>",
      "stationName": "My Solar Plant",
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
      "enterpriseName": "OEM Name",
      "disEnterpriseName": "Distributor Name"
    },
    "attention": 0,
    "communicateStatus": 1,
    "alarmStatus": 0
  },
  "success": true
}
```

---

## 7. Single Station Overview — `GET /business/app/v1/single/overview/appSingleStationOverviewData`

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

| Field | Description | Unit |
|---|---|---|
| `activePower` | Net power (+ export, - import) | kW |
| `todayProductPower` | Today's PV production | kWh |
| `todaySelfUsePower` | Today's self-consumption | kWh |
| `todayOngridPower` | Today's grid export | kWh |
| `todayBuyGridPower` | Today's grid import | kWh |
| `todayCellCharge` | Today's battery charge | kWh |
| `todayCellDischarge` | Today's battery discharge | kWh |
| `todayLoadUsePower` | Today's total load | kWh |
| `uwBatSoc` | Battery state of charge | % |
| `batterySoh` | Battery state of health | % |
| `cellChargePower` | Current battery charge power | kW |
| `cellDisChargePower` | Current battery discharge power | kW |
| `ammeterActivePowerToGrid` | Current grid export power | kW |
| `ammeterActivePowerFromGrid` | Current grid import power | kW |

---

## 8. Energy Flow Diagram — `GET /business/single/overview/stationEnergyFlowDiagram`

```json
{
  "code": 20000,
  "data": {
    "stationCode": "<uuid-station-code>",
    "stationName": "My Solar Plant",
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
| `mpptPower` | Total PV power | kW |
| `batteryPower` | Battery power (- charge, + discharge) | kW |
| `batterySocAver` | Battery SOC average | % |
| `ongridPower` | Grid export power | kW |
| `buyPower` | Grid import power | kW |
| `loadPower` | Home load power | kW |
| `acCoupleGfActivePower` | AC-coupled inverter power | kW |
| `uwEPS_P_R` | EPS backup power | kW |
| `remainAvailEnergy` | Remaining battery energy | kWh |
| `remainChargeFullTime` | Time to full charge | hours |

---

## 9. Storage Inverter List — `POST /dev/info/app/v1/devmonitor/appPageStoredInverterMoniterList`

```json
{
  "code": 20000,
  "data": {
    "records": [
      {
        "devId": 1234567,
        "devName": "device-serial",
        "sn": "device-serial",
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

---

## 10. SOC/SOH/Power — `GET /business/single/overview/socSohAndPower`

> **Note:** This endpoint may return `10055: 无数据` (no data) for some stations.
> SOC/SOH data is available in the Single Station Overview endpoint instead.

```json
{
  "code": 10055,
  "msg": "无数据",
  "success": false
}
```

---

## Error Responses

### Dynamic Error (10008)
```json
{
  "code": 10008,
  "msg": "{\"deCode\":80010,\"phvList\":[4]}",
  "success": false
}
```
- `deCode 80010`: Username or password error, 4 attempts remaining

### No Station Access (10039)
```json
{
  "code": 10039,
  "msg": "无电站访问权限",
  "success": false
}
```

### Station Not Found (11218)
```json
{
  "code": 11218,
  "msg": "电站信息不存在",
  "success": false
}
```
