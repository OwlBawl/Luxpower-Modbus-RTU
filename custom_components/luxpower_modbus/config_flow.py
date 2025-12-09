"""Config flow for Luxpower Modbus RTU."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT, CONF_SCAN_INTERVAL, CONF_SLAVE
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from .const import (
    DEFAULT_BAUDRATE,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PORT, default="/dev/ttyUSB0"): TextSelector(),
        vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE_ID): NumberSelector(
            NumberSelectorConfig(min=1, max=255, mode=NumberSelectorMode.BOX)
        ),
        vol.Required("baudrate", default=DEFAULT_BAUDRATE): NumberSelector(
            NumberSelectorConfig(min=2400, max=115200, mode=NumberSelectorMode.BOX)
        ),
        vol.Required(
            CONF_SCAN_INTERVAL, default=DEFAULT_POLL_INTERVAL
        ): NumberSelector(
            NumberSelectorConfig(min=5, max=300, mode=NumberSelectorMode.BOX)
        ),
    }
)


class LuxpowerModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luxpower Modbus RTU."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Using slave_id as part of the unique ID
            unique_id = f"luxpower_modbus_{user_input[CONF_SLAVE]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Luxpower Inverter (Slave {user_input[CONF_SLAVE]})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
