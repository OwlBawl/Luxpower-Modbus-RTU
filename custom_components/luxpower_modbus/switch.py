"""Switch platform for Luxpower Modbus RTU."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOLDING_REGISTERS_SWITCHES
from . import LuxpowerModbusDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        LuxpowerModbusSwitch(coordinator, entry, description)
        for description in HOLDING_REGISTERS_SWITCHES
    ]
    async_add_entities(entities)


class LuxpowerModbusSwitch(CoordinatorEntity[LuxpowerModbusDataCoordinator], SwitchEntity):
    """Luxpower Modbus switch."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{config_entry.data['slave_id']}_{description.key}"
        self._attr_is_on = None

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data['slave_id'])},
            name=f"Luxpower Inverter (Slave {config_entry.data['slave_id']})",
            manufacturer="Luxpower",
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        register_key = f"register_{self.entity_description.register_address}"
        if self.coordinator.data and register_key in self.coordinator.data:
            register_val = self.coordinator.data[register_key]
            self._attr_is_on = bool(int(register_val) & (1 << self.entity_description.bit))
        self.async_write_ha_state()

    async def _async_set_bit(self, state: bool) -> None:
        """Set a single bit in a holding register using read-modify-write."""
        client = self.coordinator.client
        address = self.entity_description.register_address
        bit = self.entity_description.bit

        async with self.coordinator.lock:
            try:
                if not client.connect():
                    _LOGGER.error("Failed to connect to Modbus device for writing")
                    return

                # Read current value
                read_result = await self.hass.async_add_executor_job(
                    client.read_holding_registers, address, 1, self.coordinator.slave_id
                )
                if read_result.isError():
                    _LOGGER.error("Failed to read register %s before writing", address)
                    return

                current_value = read_result.registers[0]

                # Modify bit
                if state:
                    new_value = current_value | (1 << bit)
                else:
                    new_value = current_value & ~(1 << bit)
                
                # Write new value
                if new_value != current_value:
                    await self.hass.async_add_executor_job(
                        client.write_register, address, new_value, self.coordinator.slave_id
                    )

            except Exception as e:
                _LOGGER.error("Error writing to modbus register %s: %s", address, e)
            finally:
                if client.is_socket_open():
                    client.close()
        
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._async_set_bit(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._async_set_bit(False)
