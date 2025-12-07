# Luxpower Modbus RTU Home Assistant Integration

This is a custom component for Home Assistant to integrate Luxpower inverters using Modbus RTU via an RS485-to-USB adapter.

## Installation

### HACS (Recommended)

1.  This integration is not in the default HACS repository yet. You can add it as a custom repository.
2.  Go to HACS -> Integrations -> Click the 3 dots in the top right -> Custom repositories.
3.  Add the URL to this repository and select `Integration` as the category.
4.  Click `ADD`. You should now see "Luxpower Modbus RTU" in your HACS integrations list.
5.  Click `INSTALL` and follow the instructions.
6.  Restart Home Assistant.

### Manual Installation

1.  Copy the `custom_components/luxpower_modbus` directory to your Home Assistant `custom_components` directory.
2.  Restart Home Assistant.

## Configuration

1.  Go to Settings -> Devices & Services -> Add Integration.
2.  Search for "Luxpower Modbus RTU" and click on it.
3.  Follow the on-screen instructions to configure the integration:
    -   **Serial Port**: The path to your RS485-to-USB adapter (e.g., `/dev/ttyUSB0`).
    -   **Slave ID**: The Modbus slave ID of your inverter (usually `1`).
    -   **Baud Rate**: The communication speed (usually `9600`).
    -   **Polling Interval**: How often to poll the inverter for data in seconds.

## Customization

To add or change sensors and controls, you need to edit the entity descriptions in `custom_components/luxpower_modbus/const.py`. You will need the Modbus register map for your specific Luxpower inverter model.
