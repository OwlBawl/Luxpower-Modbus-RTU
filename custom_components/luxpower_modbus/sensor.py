"""Sensor platform for Luxpower Modbus RTU."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INPUT_REGISTERS_SENSORS, INPUT_REGISTERS_SENSORS_32BIT
from . import LuxpowerModbusDataCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    all_sensors = list(INPUT_REGISTERS_SENSORS) + list(INPUT_REGISTERS_SENSORS_32BIT)

    entities = [
        LuxpowerModbusSensor(coordinator, entry, description)
        for description in all_sensors
    ]
    async_add_entities(entities)


class LuxpowerModbusSensor(CoordinatorEntity[LuxpowerModbusDataCoordinator], SensorEntity):
    """Luxpower Modbus sensor."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{config_entry.data['slave_id']}_{description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data['slave_id'])},
            name=f"Luxpower Inverter (Slave {config_entry.data['slave_id']})",
            manufacturer="Luxpower",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            return self.coordinator.data[self.entity_description.key]
        return None
