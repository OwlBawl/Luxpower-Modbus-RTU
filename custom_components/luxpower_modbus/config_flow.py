"""Config flow for Luxpower Modbus RTU."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT, CONF_SCAN_INTERVAL, CONF_SLAVE
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import (
    DEFAULT_BAUDRATE,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class LuxpowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luxpower Modbus RTU."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate that we can at least parse the input
            try:
                port = user_input.get(CONF_PORT)
                slave_id = user_input.get(CONF_SLAVE, DEFAULT_SLAVE_ID)
                baudrate = user_input.get("baudrate", DEFAULT_BAUDRATE)
                
                if not port:
                    errors["base"] = "invalid_port"
                elif not isinstance(slave_id, int) or slave_id < 1 or slave_id > 255:
                    errors["base"] = "invalid_slave_id"
                elif not isinstance(baudrate, int) or baudrate < 2400 or baudrate > 115200:
                    errors["base"] = "invalid_baudrate"
                else:
                    # Create a unique ID based on port and slave ID
                    await self.async_set_unique_id(f"{port}_{slave_id}")
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"Luxpower Inverter ({port}, Slave {slave_id})",
                        data=user_input,
                    )
            except Exception as err:
                _LOGGER.error("Unexpected error in config flow: %s", err)
                errors["base"] = "unknown"

        # Define the data schema
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_PORT,
                    default="/dev/ttyUSB0",
                ): TextSelector(TextSelectorConfig()),
                vol.Required(
                    CONF_SLAVE,
                    default=DEFAULT_SLAVE_ID,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=255,
                        mode=NumberSelectorMode.BOX,
                    ),
                ),
                vol.Required(
                    "baudrate",
                    default=DEFAULT_BAUDRATE,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=2400,
                        max=115200,
                        mode=NumberSelectorMode.BOX,
                    ),
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_POLL_INTERVAL,
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=5,
                        max=300,
                        mode=NumberSelectorMode.BOX,
                    ),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )
