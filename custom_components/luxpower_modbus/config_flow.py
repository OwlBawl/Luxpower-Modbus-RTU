"""Config flow for Luxpower Modbus RTU."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT, CONF_SCAN_INTERVAL, CONF_SLAVE
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


class LuxpowerModbusConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Luxpower Modbus RTU."""

    VERSION = 1
    DOMAIN = DOMAIN

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(f"luxpower_{user_input[CONF_SLAVE]}")
            self._abort_if_unique_id_configured()

            if not errors:
                return self.async_create_entry(
                    title=f"Luxpower Inverter (Slave {user_input[CONF_SLAVE]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
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
            ),
            errors=errors,
        )
