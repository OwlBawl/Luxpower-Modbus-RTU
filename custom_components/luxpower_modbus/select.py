"""Select platform for Luxpower Modbus RTU."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOLDING_REGISTERS_SELECTS
from . import LuxpowerModbusDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        LuxpowerModbusSelect(coordinator, entry, description)
        for description in HOLDING_REGISTERS_SELECTS
    ]
    async_add_entities(entities)


class LuxpowerModbusSelect(CoordinatorEntity[LuxpowerModbusDataCoordinator], SelectEntity):
    """Luxpower Modbus select."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the select."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{config_entry.data['slave_id']}_{description.key}"
        self._value_map_inv = {v: k for k, v in description.value_map.items()}

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data['slave_id'])},
            name=f"Luxpower Inverter (Slave {config_entry.data['slave_id']})",
            manufacturer="Luxpower",
        )

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data and self.entity_description.key in self.coordinator.data:
            value = self.coordinator.data[self.entity_description.key]
            return self.entity_description.value_map.get(int(value))
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._value_map_inv:
            _LOGGER.warning("Invalid option selected: %s", option)
            return

        value_to_write = self._value_map_inv[option]
        client = self.coordinator.client
        address = self.entity_description.register_address

        def write_value():
            try:
                if not client.connect():
                    _LOGGER.error("Failed to connect to Modbus device for writing")
                    return False
                client.write_register(address, value_to_write, slave=self.coordinator.slave_id)
                return True
            except Exception as e:
                _LOGGER.error("Error writing to modbus register %s: %s", address, e)
                return False
            finally:
                if client.is_socket_open():
                    client.close()

        if await self.hass.async_add_executor_job(write_value):
            await self.coordinator.async_request_refresh()
