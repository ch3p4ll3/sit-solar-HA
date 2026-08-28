"""Sensor platform for sitSolar."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfEnergy, UnitOfElectricPotential, UnitOfElectricCurrent, UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import EnergyFlow, StationOverview
from .const import DOMAIN
from .coordinator import SitSolarDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SitSolarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    station_code = entry.data["station_code"]

    entities = [
        SitSolarSensor(coordinator, station_code, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities, True)


class SitSolarSensor(CoordinatorEntity[SitSolarDataUpdateCoordinator], SensorEntity):
    def __init__(
        self,
        coordinator: SitSolarDataUpdateCoordinator,
        station_code: str,
        description: Any,
    ) -> None:
        super().__init__(coordinator)
        self._station_code = station_code
        self.entity_description = description
        self._attr_unique_id = f"{station_code}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, station_code)},
            "name": "sitSolar Station",
            "manufacturer": "Sineng Electric",
        }

    @property
    def native_value(self) -> float | None:
        energy_flow: EnergyFlow = self.coordinator.data.get("energy_flow")
        overview: StationOverview = self.coordinator.data.get("overview")

        if self.entity_description.value_fn:
            try:
                return self.entity_description.value_fn(energy_flow, overview)
            except (AttributeError, TypeError):
                return None
        return None


from dataclasses import dataclass


@dataclass(frozen=True)
class SitSolarSensorDescription:
    key: str
    name: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    value_fn: Any = None


SENSOR_DESCRIPTIONS = [
    # --- Real-time power (from energy flow) ---
    SitSolarSensorDescription(
        key="pv_power",
        name="PV Power",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.mppt_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="grid_power",
        name="Grid Power",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: (ef.grid_export - ef.grid_import) if ef else None,
    ),
    SitSolarSensorDescription(
        key="grid_export",
        name="Grid Export",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.grid_export if ef else None,
    ),
    SitSolarSensorDescription(
        key="grid_import",
        name="Grid Import",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.grid_import if ef else None,
    ),
    SitSolarSensorDescription(
        key="house_load",
        name="House Load",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.load_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="battery_power",
        name="Battery Power",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.battery_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="battery_soc",
        name="Battery SOC",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, ov: (ef.battery_soc if ef else None) or (ov.battery_soc if ov else None),
    ),
    SitSolarSensorDescription(
        key="battery_soh",
        name="Battery SOH",
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, ov: ov.battery_soh if ov else None,
    ),
    SitSolarSensorDescription(
        key="eps_power",
        name="EPS Power",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.eps_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="ac_coupled_power",
        name="AC Coupled Power",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.ac_coupled_power if ef else None,
    ),
    # --- Today's energy (from overview) ---
    SitSolarSensorDescription(
        key="today_production",
        name="Today Production",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_product_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_self_use",
        name="Today Self-Use",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_self_use_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_grid_export",
        name="Today Grid Export",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_grid_export if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_grid_import",
        name="Today Grid Import",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_grid_import if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_battery_charge",
        name="Today Battery Charge",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_battery_charge if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_battery_discharge",
        name="Today Battery Discharge",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_battery_discharge if ov else None,
    ),
    # --- Total energy (from overview) ---
    SitSolarSensorDescription(
        key="total_production",
        name="Total Production",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_product_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_grid_export",
        name="Total Grid Export",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_grid_export if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_grid_import",
        name="Total Grid Import",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_grid_import if ov else None,
    ),
]
