"""Sensor platform for sitSolar."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfEnergy, PERCENTAGE
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
        description: SitSolarSensorDescription,
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


@dataclass(frozen=True, kw_only=True)
class SitSolarSensorDescription(SensorEntityDescription):
    """Describes a sitSolar sensor."""
    value_fn: Any = None


SENSOR_DESCRIPTIONS = [
    SitSolarSensorDescription(
        key="pv_power",
        name="PV Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: (ef.mppt_power + ef.ac_coupled_power) if ef else None,
    ),
    SitSolarSensorDescription(
        key="grid_power",
        name="Grid Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: (ef.grid_export - ef.grid_import) if ef else None,
    ),
    SitSolarSensorDescription(
        key="grid_export",
        name="Grid Export",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.grid_export if ef else None,
    ),
    SitSolarSensorDescription(
        key="grid_import",
        name="Grid Import",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.grid_import if ef else None,
    ),
    SitSolarSensorDescription(
        key="house_load",
        name="House Load",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.load_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="battery_power",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.battery_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="battery_charge_power",
        name="Battery Charge Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, ov: ov.battery_charge_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="battery_discharge_power",
        name="Battery Discharge Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, ov: ov.battery_discharge_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, ov: (ef.battery_soc if ef else None) or (ov.battery_soc if ov else None),
    ),
    SitSolarSensorDescription(
        key="battery_soh",
        name="Battery SOH",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, ov: ov.battery_soh if ov else None,
    ),
    SitSolarSensorDescription(
        key="eps_power",
        name="EPS Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.eps_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="ac_coupled_power",
        name="AC Coupled Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ef, _: ef.ac_coupled_power if ef else None,
    ),
    SitSolarSensorDescription(
        key="today_production",
        name="Today Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_product_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_self_use",
        name="Today Self-Use",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_self_use_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_grid_export",
        name="Today Grid Export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_grid_export if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_grid_import",
        name="Today Grid Import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_grid_import if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_battery_charge",
        name="Today Battery Charge",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_battery_charge if ov else None,
    ),
    SitSolarSensorDescription(
        key="today_battery_discharge",
        name="Today Battery Discharge",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.today_battery_discharge if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_production",
        name="Total Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_product_power if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_grid_export",
        name="Total Grid Export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_grid_export if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_grid_import",
        name="Total Grid Import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_grid_import if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_battery_charge",
        name="Total Battery Charge",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_battery_charge if ov else None,
    ),
    SitSolarSensorDescription(
        key="total_battery_discharge",
        name="Total Battery Discharge",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda ef, ov: ov.total_battery_discharge if ov else None,
    ),
]
