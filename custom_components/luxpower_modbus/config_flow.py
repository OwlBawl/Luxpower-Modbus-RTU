"""Config flow for Luxpower Modbus RTU."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT, CONF_SCAN_INTERVAL, CONF_SLAVE
from homeassistant.core import callback
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

# You might need to import a test function from a client library
# For now, we'll just assume connection works if no exception is raised.
# from .modbus_client import test_connection


class LuxpowerModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luxpower Modbus RTU."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Here you would ideally test the connection to the inverter
            # For simplicity, we are skipping a live test. A real implementation should have one.
            # try:
            #     await self.hass.async_add_executor_job(
            //         test_connection, user_input[CONF_PORT], user_input[CONF_SLAVE]
            //     )
            # except Exception:
            #     errors["base"] = "cannot_connect"
            
            if not errors:
                return self.async_create_entry(title=f"Luxpower Inverter (Slave {user_input[CONF_SLAVE]})", data=user_input)

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
