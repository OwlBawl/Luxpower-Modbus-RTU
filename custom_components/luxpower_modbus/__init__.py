"""The Luxpower Modbus RTU integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
import struct

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, CONF_SCAN_INTERVAL, CONF_SLAVE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from .const import (
    DOMAIN,
    HOLDING_REGISTERS_NUMBERS,
    HOLDING_REGISTERS_SELECTS,
    HOLDING_REGISTERS_SWITCHES,
    INPUT_REGISTERS_SENSORS,
    INPUT_REGISTERS_SENSORS_32BIT,
    LuxpowerModbus32bitSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.SELECT, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Luxpower Modbus RTU from a config entry."""
    port = entry.data[CONF_PORT]
    slave_id = entry.data[CONF_SLAVE]
    baudrate = entry.data["baudrate"]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    client = ModbusSerialClient(
        port=port,
        baudrate=baudrate,
        stopbits=1,
        bytesize=8,
        parity="N",
        timeout=3,
    )

    coordinator = LuxpowerModbusDataCoordinator(
        hass, client, slave_id, timedelta(seconds=scan_interval)
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: LuxpowerModbusDataCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.client.close()
    return unload_ok


class LuxpowerModbusDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the inverter."""

    def __init__(self, hass: HomeAssistant, client: ModbusSerialClient, slave_id: int, update_interval: timedelta) -> None:
        """Initialize."""
        self.client = client
        self.slave_id = slave_id
        self.data: dict[str, any] = {}
        self.lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    def _read_registers(self, register_type: str, descriptions: list) -> dict | None:
        """Read a range of registers."""
        if not descriptions:
            return {}
            
        all_addresses = set()
        for d in descriptions:
            all_addresses.add(d.register_address)
            if isinstance(d, LuxpowerModbus32bitSensorEntityDescription):
                all_addresses.add(d.register_address + 1)
        
        if not all_addresses:
            return {}
            
        min_addr = min(all_addresses)
        max_addr = max(all_addresses)
        count = max_addr - min_addr + 1

        try:
            if register_type == "input":
                result = self.client.read_input_registers(min_addr, count, unit=self.slave_id)
            else:  # holding
                result = self.client.read_holding_registers(min_addr, count, unit=self.slave_id)

            if result.isError():
                raise ConnectionException(f"Modbus error: {result}")
            
            data: dict[str, any] = {}
            for desc in descriptions:
                idx = desc.register_address - min_addr
                
                # For switches, we store the raw register value keyed by register address
                if hasattr(desc, 'bit'): 
                    data[f"register_{desc.register_address}"] = result.registers[idx]
                    continue

                if isinstance(desc, LuxpowerModbus32bitSensorEntityDescription):
                    if (idx + 1) < len(result.registers):
                        low_word = result.registers[idx]
                        high_word = result.registers[idx + 1]
                        # Inverter uses L/H byte order, so pack high word then low word for big-endian
                        raw_val = struct.unpack('>I', struct.pack('>HH', high_word, low_word))[0]
                    else:
                        continue
                else:
                    raw_val = result.registers[idx]
                
                value = float(raw_val)
                if hasattr(desc, 'value_fn') and desc.value_fn:
                    value = desc.value_fn(raw_val)
                else:
                    value *= desc.scale
                
                data[desc.key] = value

            return data
        except ConnectionException as e:
            _LOGGER.error("Error reading modbus registers: %s", e)
            return None  # Indicate error

    async def _async_update_data(self) -> dict:
        """Fetch data from inverter."""
        async with self.lock:
            try:
                if not await self.hass.async_add_executor_job(self.client.connect):
                    raise UpdateFailed("Failed to connect to Modbus device")

                all_input_sensors = list(INPUT_REGISTERS_SENSORS) + list(INPUT_REGISTERS_SENSORS_32BIT)
                all_holding_entities = list(HOLDING_REGISTERS_NUMBERS) + list(HOLDING_REGISTERS_SELECTS) + list(HOLDING_REGISTERS_SWITCHES)

                input_data = await self.hass.async_add_executor_job(
                    self._read_registers, "input", all_input_sensors
                )
                holding_data = await self.hass.async_add_executor_job(
                    self._read_registers, "holding", all_holding_entities
                )

                if input_data is None or holding_data is None:
                    raise UpdateFailed("Failed to read registers")

                return {**input_data, **holding_data}
            except Exception as e:
                raise UpdateFailed(f"Error communicating with inverter: {e}") from e
            finally:
                if self.client.is_socket_open():
                    await self.hass.async_add_executor_job(self.client.close)
