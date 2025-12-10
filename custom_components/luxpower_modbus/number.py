"""Number platform for Luxpower Modbus RTU."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOLDING_REGISTERS_NUMBERS
from . import LuxpowerModbusDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        LuxpowerModbusNumber(coordinator, entry, description)
        for description in HOLDING_REGISTERS_NUMBERS
    ]
    async_add_entities(entities)


class LuxpowerModbusNumber(CoordinatorEntity[LuxpowerModbusDataCoordinator], NumberEntity):
    """Luxpower Modbus number."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the number."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{config_entry.data['slave_id']}_{description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data['slave_id'])},
            name=f"Luxpower Inverter (Slave {config_entry.data['slave_id']})",
            manufacturer="Luxpower",
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the number."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            return self.coordinator.data[self.entity_description.key]
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        client = self.coordinator.client
        address = self.entity_description.register_address
        scaled_value = int(value / self.entity_description.scale)
        
        def write_value():
            try:
                if not client.connect():
                    _LOGGER.error("Failed to connect to Modbus device for writing")
                    return False
                client.write_register(address, scaled_value, slave=self.coordinator.slave_id)
                return True
            except Exception as e:
                _LOGGER.error("Error writing to modbus register %s: %s", address, e)
                return False
            finally:
                if client.is_socket_open():
                    client.close()

        if await self.hass.async_add_executor_job(write_value):
            await self.coordinator.async_request_refresh()
