"""Constants for the Luxpower Modbus RTU integration."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import struct

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.number import NumberEntityDescription, NumberMode
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import (
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

DOMAIN = "luxpower_modbus"

DEFAULT_SLAVE_ID = 1
DEFAULT_BAUDRATE = 19200  # As per protocol document
DEFAULT_POLL_INTERVAL = 30

# NOTE: The register addresses below are from 'modbus_protocol_updated_on_2025.06.14.md'.
# You must consult the Modbus documentation for your specific Luxpower inverter model
# and update these values if they differ.


def signed_int(val: int) -> int:
    """Convert 16-bit unsigned integer to signed integer."""
    if val > 32767:
        return val - 65536
    return val


@dataclass(kw_only=True)
class LuxpowerModbusSensorEntityDescription(SensorEntityDescription):
    """A class that describes sensor entities."""
    register_address: int | None = None
    scale: float = 1.0
    value_fn: Callable[[int], float] | None = None


@dataclass(kw_only=True)
class LuxpowerModbus32bitSensorEntityDescription(LuxpowerModbusSensorEntityDescription):
    """A class that describes 32-bit sensor entities."""


@dataclass(kw_only=True)
class LuxpowerModbusNumberEntityDescription(NumberEntityDescription):
    """A class that describes number entities."""
    register_address: int | None = None
    scale: float = 1.0


@dataclass(kw_only=True)
class LuxpowerModbusSelectEntityDescription(SelectEntityDescription):
    """A class that describes select entities."""
    register_address: int | None = None
    # Map modbus value to HA option
    value_map: dict[int, str] | None = None


@dataclass(kw_only=True)
class LuxpowerModbusSwitchEntityDescription(SwitchEntityDescription):
    """A class that describes switch entities."""
    register_address: int
    bit: int


# Input Registers (Read Only)
# Note: 32-bit registers (marked with L/H) are now supported and defined in a separate list.
INPUT_REGISTERS_SENSORS: tuple[LuxpowerModbusSensorEntityDescription, ...] = (
    # General & Status
    LuxpowerModbusSensorEntityDescription(key="operational_mode", name="Operational Mode", register_address=0),
    LuxpowerModbusSensorEntityDescription(key="internal_fault", name="Internal Fault", register_address=6),
    LuxpowerModbusSensorEntityDescription(key="ac_input_type", name="AC Input Type", register_address=77),
    LuxpowerModbusSensorEntityDescription(key="switch_state", name="Switch State", register_address=174),
    LuxpowerModbusSensorEntityDescription(key="battery_type", name="Battery Type", register_address=80),
    LuxpowerModbusSensorEntityDescription(key="master_slave_state", name="Master/Slave State", register_address=113),
    LuxpowerModbusSensorEntityDescription(key="on_grid_load_power", name="On-Grid Load Power (12k)", register_address=114),
    LuxpowerModbusSensorEntityDescription(key="exception_reason_1", name="Exception Reason 1", register_address=176),
    LuxpowerModbusSensorEntityDescription(key="exception_reason_2", name="Exception Reason 2", register_address=177),
    LuxpowerModbusSensorEntityDescription(key="charge_discharge_disable_reason", name="Charge/Discharge Disable Reason", register_address=178),


    # PV
    LuxpowerModbusSensorEntityDescription(key="pv1_voltage", name="PV1 Voltage", register_address=1, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv2_voltage", name="PV2 Voltage", register_address=2, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv3_voltage", name="PV3 Voltage", register_address=3, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv1_power", name="PV1 Power", register_address=7, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="pv2_power", name="PV2 Power", register_address=8, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="total_pv_power", name="Total PV Power", register_address=9, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT), # Doc says Ppv3, but note says Total
    LuxpowerModbusSensorEntityDescription(key="pv4_voltage", name="PV4 Voltage", register_address=217, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv5_voltage", name="PV5 Voltage", register_address=218, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv6_voltage", name="PV6 Voltage", register_address=219, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv4_power", name="PV4 Power", register_address=220, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="pv5_power", name="PV5 Power", register_address=221, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="pv6_power", name="PV6 Power", register_address=222, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="reactive_power", name="Reactive Power", register_address=139, device_class=SensorDeviceClass.REACTIVE_POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement="var"),
    LuxpowerModbusSensorEntityDescription(key="ac_couple_power", name="AC Couple Power", register_address=153, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),

    # Battery
    LuxpowerModbusSensorEntityDescription(key="battery_voltage", name="Battery Voltage", register_address=4, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="battery_soc", name="Battery SOC", register_address=5, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=PERCENTAGE),
    LuxpowerModbusSensorEntityDescription(key="battery_charge_power", name="Battery Charge Power", register_address=10, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="battery_discharge_power", name="Battery Discharge Power", register_address=11, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="battery_temperature", name="Battery Temperature", register_address=67, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    LuxpowerModbusSensorEntityDescription(key="battery_current", name="Battery Current", register_address=98, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, value_fn=lambda v: signed_int(v) * 0.01),
    LuxpowerModbusSensorEntityDescription(key="inverter_sampled_battery_voltage", name="Inverter Sampled Battery Voltage", register_address=107, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),

    # Grid
    LuxpowerModbusSensorEntityDescription(key="grid_voltage_r", name="Grid Voltage R", register_address=12, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="grid_voltage_s", name="Grid Voltage S", register_address=13, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="grid_voltage_t", name="Grid Voltage T", register_address=14, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="grid_frequency", name="Grid Frequency", register_address=15, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfFrequency.HERTZ, scale=0.01),
    LuxpowerModbusSensorEntityDescription(key="inverter_power_r", name="Inverter Power R", register_address=16, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="ac_charge_power_r", name="AC Charging Power R", register_address=17, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="inverter_current_r", name="Inverter Current R", register_address=18, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, scale=0.01),
    LuxpowerModbusSensorEntityDescription(key="power_factor", name="Power Factor", register_address=19, device_class=SensorDeviceClass.POWER_FACTOR, scale=0.001), # Note: value > 1 represents leading/lagging
    LuxpowerModbusSensorEntityDescription(key="power_to_grid_r", name="Power to Grid R", register_address=26, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="power_from_grid_r", name="Power from Grid R", register_address=27, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT), # Note: doc says 'Grid power capacity'
    LuxpowerModbusSensorEntityDescription(key="inverter_power_s", name="Inverter Power S", register_address=180, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="inverter_power_t", name="Inverter Power T", register_address=181, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="ac_charge_power_s", name="AC Charging Power S", register_address=182, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="ac_charge_power_t", name="AC Charging Power T", register_address=183, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="power_to_grid_s", name="Power to Grid S", register_address=184, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="power_to_grid_t", name="Power to Grid T", register_address=185, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="power_from_grid_s", name="Power from Grid S", register_address=186, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="power_from_grid_t", name="Power from Grid T", register_address=187, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="load_power", name="Load Power", register_address=170, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="smart_load_power", name="Smart Load Power", register_address=232, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),

    # EPS (Off-Grid)
    LuxpowerModbusSensorEntityDescription(key="eps_voltage_r", name="EPS Voltage R", register_address=20, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="eps_voltage_s", name="EPS Voltage S", register_address=21, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="eps_voltage_t", name="EPS Voltage T", register_address=22, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="eps_frequency", name="EPS Frequency", register_address=23, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfFrequency.HERTZ, scale=0.01),
    LuxpowerModbusSensorEntityDescription(key="eps_power_r", name="EPS Power R", register_address=24, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="eps_apparent_power_r", name="EPS Apparent Power R", register_address=25, device_class=SensorDeviceClass.APPARENT_POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE),
    LuxpowerModbusSensorEntityDescription(key="eps_power_l1n", name="EPS Power L1N/S", register_address=129, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="eps_power_l2n", name="EPS Power L2N/T", register_address=130, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
    LuxpowerModbusSensorEntityDescription(key="eps_apparent_power_l1n", name="EPS Apparent Power L1N/S", register_address=131, device_class=SensorDeviceClass.APPARENT_POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE),
    LuxpowerModbusSensorEntityDescription(key="eps_apparent_power_l2n", name="EPS Apparent Power L2N/T", register_address=132, device_class=SensorDeviceClass.APPARENT_POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE),
    LuxpowerModbusSensorEntityDescription(key="eps_daily_energy_l1n", name="EPS Daily Energy L1N/S", register_address=133, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="eps_daily_energy_l2n", name="EPS Daily Energy L2N/T", register_address=134, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),

    # Energy - Today
    LuxpowerModbusSensorEntityDescription(key="pv1_energy_today", name="PV1 Energy Today", register_address=28, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv2_energy_today", name="PV2 Energy Today", register_address=29, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="total_pv_energy_today", name="Total PV Energy Today", register_address=30, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="inverter_energy_today", name="Inverter Energy Today", register_address=31, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="ac_charge_energy_today", name="AC Charge Energy Today", register_address=32, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="battery_charge_energy_today", name="Battery Charge Energy Today", register_address=33, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="battery_discharge_energy_today", name="Battery Discharge Energy Today", register_address=34, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="eps_energy_today", name="EPS Energy Today", register_address=35, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="energy_to_grid_today", name="Energy to Grid Today", register_address=36, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="energy_from_grid_today", name="Energy from Grid Today", register_address=37, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="load_energy_today", name="Load Energy Today", register_address=171, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="generator_energy_today", name="Generator Energy Today", register_address=124, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv4_energy_today", name="PV4 Energy Today", register_address=223, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv5_energy_today", name="PV5 Energy Today", register_address=226, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="pv6_energy_today", name="PV6 Energy Today", register_address=229, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),

    # Temperatures & Internals
    LuxpowerModbusSensorEntityDescription(key="vbus1", name="Bus Voltage 1", register_address=38, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="vbus2", name="Bus Voltage 2", register_address=39, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="inverter_temperature_inner", name="Inverter Temperature (Inner)", register_address=64, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    LuxpowerModbusSensorEntityDescription(key="inverter_temperature_radiator1", name="Inverter Temperature (Radiator 1)", register_address=65, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    LuxpowerModbusSensorEntityDescription(key="inverter_temperature_radiator2", name="Inverter Temperature (Radiator 2)", register_address=66, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    LuxpowerModbusSensorEntityDescription(key="one_click_charge_remaining_s", name="One Click Charge Remaining", register_address=210, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTime.SECONDS),
    
    # BMS
    LuxpowerModbusSensorEntityDescription(key="bms_max_charge_current", name="BMS Max Charge Current", register_address=81, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, scale=0.01),
    LuxpowerModbusSensorEntityDescription(key="bms_max_discharge_current", name="BMS Max Discharge Current", register_address=82, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, scale=0.01),
    LuxpowerModbusSensorEntityDescription(key="bms_charge_voltage_ref", name="BMS Charge Voltage Reference", register_address=83, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="bms_discharge_cutoff_voltage", name="BMS Discharge Cutoff Voltage", register_address=84, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="bms_fault_code", name="BMS Fault Code", register_address=99),
    LuxpowerModbusSensorEntityDescription(key="bms_warning_code", name="BMS Warning Code", register_address=100),
    LuxpowerModbusSensorEntityDescription(key="bms_max_cell_voltage", name="BMS Max Cell Voltage", register_address=101, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.001),
    LuxpowerModbusSensorEntityDescription(key="bms_min_cell_voltage", name="BMS Min Cell Voltage", register_address=102, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.001),
    LuxpowerModbusSensorEntityDescription(key="bms_max_cell_temperature", name="BMS Max Cell Temperature", register_address=103, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTemperature.CELSIUS, value_fn=lambda v: signed_int(v) * 0.1),
    LuxpowerModbusSensorEntityDescription(key="bms_min_cell_temperature", name="BMS Min Cell Temperature", register_address=104, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfTemperature.CELSIUS, value_fn=lambda v: signed_int(v) * 0.1),
    LuxpowerModbusSensorEntityDescription(key="bms_cycle_count", name="BMS Cycle Count", register_address=106, state_class=SensorStateClass.TOTAL_INCREASING),
    LuxpowerModbusSensorEntityDescription(key="bms_parallel_count", name="BMS Parallel Count", register_address=96),
    LuxpowerModbusSensorEntityDescription(key="bms_capacity", name="BMS Capacity", register_address=97, native_unit_of_measurement="Ah"),

    # Generator
    LuxpowerModbusSensorEntityDescription(key="generator_voltage", name="Generator Voltage", register_address=121, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, scale=0.1),
    LuxpowerModbusSensorEntityDescription(key="generator_frequency", name="Generator Frequency", register_address=122, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfFrequency.HERTZ, scale=0.01),
    LuxpowerModbusSensorEntityDescription(key="generator_power", name="Generator Power", register_address=123, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT),
)

# 32-bit Input Registers (L/H byte order)
INPUT_REGISTERS_SENSORS_32BIT: tuple[LuxpowerModbus32bitSensorEntityDescription, ...] = (
    LuxpowerModbus32bitSensorEntityDescription(key="fault_code", name="Fault Code", register_address=60),
    LuxpowerModbus32bitSensorEntityDescription(key="warning_code", name="Warning Code", register_address=62),
    LuxpowerModbus32bitSensorEntityDescription(key="running_time", name="Running Time", register_address=69, device_class=SensorDeviceClass.DURATION, native_unit_of_measurement=UnitOfTime.SECONDS, state_class=SensorStateClass.TOTAL_INCREASING),
    LuxpowerModbus32bitSensorEntityDescription(key="pv1_energy_total", name="PV1 Energy Total", register_address=40, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="pv2_energy_total", name="PV2 Energy Total", register_address=42, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="total_pv_energy_total", name="Total PV Energy Total", register_address=44, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="inverter_energy_total", name="Inverter Energy Total", register_address=46, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="ac_charge_energy_total", name="AC Charge Energy Total", register_address=48, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="battery_charge_energy_total", name="Battery Charge Energy Total", register_address=50, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="battery_discharge_energy_total", name="Battery Discharge Energy Total", register_address=52, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="eps_energy_total", name="EPS Energy Total", register_address=54, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="energy_to_grid_total", name="Energy to Grid Total", register_address=56, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="energy_from_grid_total", name="Energy from Grid Total", register_address=58, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="load_energy_total", name="Load Energy Total", register_address=172, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1), # Note: PDF says 172 is High, 173 is Low. Assuming 172 is start addr.
    LuxpowerModbus32bitSensorEntityDescription(key="generator_energy_total", name="Generator Energy Total", register_address=125, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="eps_energy_l1n_total", name="EPS Energy L1N/S Total", register_address=135, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="eps_energy_l2n_total", name="EPS Energy L2N/T Total", register_address=137, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="pv4_energy_total", name="PV4 Energy Total", register_address=224, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="pv5_energy_total", name="PV5 Energy Total", register_address=227, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
    LuxpowerModbus32bitSensorEntityDescription(key="pv6_energy_total", name="PV6 Energy Total", register_address=230, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, scale=0.1),
)

# Holding Registers (Read/Write)
HOLDING_REGISTERS_NUMBERS: tuple[LuxpowerModbusNumberEntityDescription, ...] = (
    # Power Control
    LuxpowerModbusNumberEntityDescription(key="active_power_percent", name="Active Power Percentage", register_address=60, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="reactive_power_percent", name="Reactive Power Percentage", register_address=61, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=60, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="charge_power_percent", name="Charge Power Percentage", register_address=64, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="discharge_power_percent", name="Discharge Power Percentage", register_address=65, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="ac_charge_power_percent", name="AC Charge Power Percentage", register_address=66, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="max_feed_in_grid_power", name="Max Feed-in Grid Power", register_address=103, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="max_grid_import_power", name="Max Grid Import Power", register_address=176, native_unit_of_measurement=UnitOfPower.WATT, mode=NumberMode.BOX, native_min_value=0, native_max_value=20000, native_step=100),

    # Battery Settings
    LuxpowerModbusNumberEntityDescription(key="ac_charge_soc_limit", name="AC Charge SOC Limit", register_address=67, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="charge_current", name="Charge Current", register_address=101, device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, mode=NumberMode.BOX, native_min_value=0, native_max_value=140, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="discharge_current", name="Discharge Current", register_address=102, device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, mode=NumberMode.BOX, native_min_value=0, native_max_value=140, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="end_of_discharge_soc", name="End of Discharge SOC (On-Grid)", register_address=105, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=10, native_max_value=90, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="eps_discharge_soc_limit", name="EPS Discharge SOC Limit", register_address=125, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="ac_charge_start_soc", name="AC Charge Start SOC", register_address=160, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=90, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="battery_low_soc_alarm", name="Battery Low SOC Alarm Point", register_address=164, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=90, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="battery_low_soc_recovery", name="Battery Low SOC Recovery Point", register_address=165, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=20, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="on_grid_eod_voltage", name="On-Grid End of Discharge Voltage", register_address=169, device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.VOLT, mode=NumberMode.BOX, native_min_value=40.0, native_max_value=56.0, native_step=0.1, scale=0.1),
    LuxpowerModbusNumberEntityDescription(key="stop_charging_soc", name="Stop Charging SOC", register_address=227, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=10, native_max_value=101, native_step=1),

    # Smart Load
    LuxpowerModbusNumberEntityDescription(key="smart_load_on_soc", name="Smart Load ON SOC", register_address=215, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
    LuxpowerModbusNumberEntityDescription(key="smart_load_off_soc", name="Smart Load OFF SOC", register_address=216, device_class=SensorDeviceClass.BATTERY, native_unit_of_measurement=PERCENTAGE, mode=NumberMode.SLIDER, native_min_value=0, native_max_value=100, native_step=1),
)

HOLDING_REGISTERS_SELECTS: tuple[LuxpowerModbusSelectEntityDescription, ...] = (
    LuxpowerModbusSelectEntityDescription(key="reactive_power_command", name="Reactive Power Command", register_address=59, options=["Unit PF", "Fixed PF", "Default Q(P)", "Custom PF", "Capacitive", "Inductive", "QV", "QV Dynamic"], value_map={0: "Unit PF", 1: "Fixed PF", 2: "Default Q(P)", 3: "Custom PF", 4: "Capacitive", 5: "Inductive", 6: "QV", 7: "QV Dynamic"}),
    LuxpowerModbusSelectEntityDescription(key="eps_voltage_set", name="EPS Voltage Set", register_address=90, options=["208", "220", "230", "240", "277"], value_map={208: "208", 220: "220", 230: "230", 240: "240", 277: "277"}),
    LuxpowerModbusSelectEntityDescription(key="eps_frequency_set", name="EPS Frequency Set", register_address=91, options=["50", "60"], value_map={50: "50", 60: "60"}),
    LuxpowerModbusSelectEntityDescription(key="output_priority_config", name="Output Priority Config", register_address=145, options=["Battery First", "PV First", "AC First"], value_map={0: "Battery First", 1: "PV First", 2: "AC First"}),
    LuxpowerModbusSelectEntityDescription(key="line_mode", name="Line Mode", register_address=146, options=["APL", "UPS", "GEN"], value_map={0: "APL", 1: "UPS", 2: "GEN"}),
)

# Bitmask Switches (Holding Registers)
HOLDING_REGISTERS_SWITCHES: tuple[LuxpowerModbusSwitchEntityDescription, ...] = (
    # FuncEn (Register 21)
    LuxpowerModbusSwitchEntityDescription(key="eps_enable", name="EPS Enable", register_address=21, bit=0),
    LuxpowerModbusSwitchEntityDescription(key="ac_charge_enable", name="AC Charge Enable", register_address=21, bit=7),
    LuxpowerModbusSwitchEntityDescription(key="forced_discharge_enable", name="Forced Discharge Enable", register_address=21, bit=10),
    LuxpowerModbusSwitchEntityDescription(key="feed_in_grid_enable", name="Feed-in Grid Enable", register_address=21, bit=15),
    # uFunctionEn2 (Register 179)
    LuxpowerModbusSwitchEntityDescription(key="grid_peak_shaving_enable", name="Grid Peak Shaving Enable", register_address=179, bit=7),
    LuxpowerModbusSwitchEntityDescription(key="smart_load_enable", name="Smart Load Enable", register_address=179, bit=13),
    LuxpowerModbusSwitchEntityDescription(key="on_grid_always_on", name="On-Grid Always On", register_address=179, bit=15),
    # uFunction4En (Register 233)
    LuxpowerModbusSwitchEntityDescription(key="quick_charge_start", name="Quick Charge Start", register_address=233, bit=0),
    LuxpowerModbusSwitchEntityDescription(key="battery_backup_mode", name="Battery Backup Mode", register_address=233, bit=1),
)
