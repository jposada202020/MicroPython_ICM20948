# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`ICM20948`
================================================================================

MicroPython Driver for the ICM20948 Accelerometer/Gyro Sensor


* Author(s): Jose D. Montoya

Implementation Notes
--------------------

**Software and Dependencies:**

This library depends on Micropython

"""

# pylint: disable=too-many-arguments, line-too-long, too-many-instance-attributes

from time import sleep
from micropython import const
from micropython_icm20948.i2c_helpers import CBits, RegisterStruct

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_ICM20948.git"

_REG_WHOAMI = const(0x69)
_DEVICE_ID = const(0x00)

_PWR_MGMT_1 = const(0x06)
_PWR_MGMT_2 = const(0x07)
_REG_BANK_SEL = const(0x7F)
_ACCEL_CONFIG = const(0x14)

_ACCEL_XOUT_H = 0x2D  # first byte of accel data
_GYRO_XOUT_H = 0x33  # first byte of accel data

# ICM20948
CLK_SELECT_INTERNAL = const(0b000)
CLK_SELECT_BEST = const(0b001)
CLK_SELECT_STOP = const(0b111)
# End
clk_values = (CLK_SELECT_INTERNAL, CLK_SELECT_BEST, CLK_SELECT_STOP)

# ICM20948
ACC_DISABLED = const(0b000)
GYRO_DISABLED = const(0b000)
ACC_ENABLED = const(0b111)
GYRO_ENABLED = const(0b111)
# End
gyro_en_values = (GYRO_DISABLED, GYRO_ENABLED)
acc_en_values = (ACC_DISABLED, ACC_ENABLED)

# ICM20948
USER_BANK_0 = const(0)
USER_BANK_1 = const(1)
USER_BANK_2 = const(2)
USER_BANK_3 = const(3)
# End
user_bank_values = (USER_BANK_0, USER_BANK_1, USER_BANK_2, USER_BANK_3)

# ICM20948
RANGE_2G = const(0b00)
RANGE_4G = const(0b01)
RANGE_8G = const(0b10)
RANGE_16G = const(0b11)
# End
acc_range_values = (RANGE_2G, RANGE_4G, RANGE_8G, RANGE_16G)
acc_range_sensitivity = (16384, 8192, 4096, 2048)


class ICM20948:
    """Main class for the Sensor

    :param ~machine.I2C i2c: The I2C bus the ICM20948 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x69`

    :raises RuntimeError: if the sensor is not found


    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`micropython_icm20948.ICM20948` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        from machine import Pin, I2C
        import micropython_icm20948.icm20948 as icm20948

    Once this is done you can define your `machine.I2C` object and define your sensor object

    .. code-block:: python

        i2c = I2C(sda=Pin(8), scl=Pin(9))
        icm = icm20948.ICM20948(i2c)

    Now you have access to the :attr:`acceleration` attribute

    .. code-block:: python

        accx, accy, accz = icm.accelerometer

    """

    # Register definitions
    _device_id = RegisterStruct(_DEVICE_ID, "B")
    _pwr_mgt_1 = RegisterStruct(_PWR_MGMT_1, "B")
    _pwr_mgt_2 = RegisterStruct(_PWR_MGMT_2, "B")

    # Register PWR_MGMT_1 (0x06)
    # | DEVICE RESET | SLEEP |  TMP_RDY | PRS_RDY | ---- | CLKSEL(2) | CLKSEL(1) | CLKSEL(0) |
    _clock_select = CBits(3, _PWR_MGMT_1, 0)
    _sleep = CBits(1, _PWR_MGMT_1, 6)
    _reset = CBits(1, _PWR_MGMT_1, 7)

    # Register PWR_MGMT_2 (0x07)
    # | ---- | ---- |  DISABLE_ACCEL(2) | DISABLE_ACCEL(1) | DISABLE_ACCEL(0) | DISABLE_GYRO(2) | DISABLE_GYRO(1) | DISABLE_GYRO(0) |
    _gyro_enable = CBits(3, _PWR_MGMT_2, 0)
    _acc_enable = CBits(3, _PWR_MGMT_2, 3)

    _raw_accel_data = RegisterStruct(_ACCEL_XOUT_H, ">hhh")
    _raw_gyro_data = RegisterStruct(_GYRO_XOUT_H, ">hhh")

    # Register REG_BANK_SEL (0x7F)
    # | ---- | ---- |  USER_BANK(1) | USER_BANK(0) | ---- | ---- | ---- | ---- |
    _user_bank = CBits(2, _REG_BANK_SEL, 4)

    # BANK 2
    # ACCEL_CONFIG (0x14)
    # | ---- | ---- |  ACCEL_DLPFCFG(2) | ACCEL_DLPFCFG(1) | ACCEL_DLPFCFG(0) | ACCEL_FS_SEL[(1) | ACCEL_FS_SEL[(0) | ACCEL_FCHOICE |
    _acc_data_range = CBits(2, _ACCEL_CONFIG, 1)

    def __init__(self, i2c, address=_REG_WHOAMI):
        self._i2c = i2c
        self._address = address

        if self._device_id != 0xEA:
            raise RuntimeError("Failed to find the ICM20948 sensor!")

        self.reset = True
        self._sleep = 0
        self._bank = 0
        self.accelerometer_range = RANGE_2G
        # print("bank", self._bank)
        # print("accelerometer", self.accelerometer_range)
        # print(self.acceleration)

    @property
    def clock_select(self):
        """
        * CLK_SELECT_INTERNAL Internal 20 MHz oscillator
        * CLK_SELECT_BEST Auto selects the best available clock source – PLL if ready, else use the Internal oscillator
        * CLK_SELECT_STOP Stops the clock and keeps timing generator in reset
        * NOTE CLKSEL should be set to ``CLK_SELECT_BEST`` to achieve full gyroscope performance.
        """

        values = {0: "CLK_SELECT_INTERNAL", 1: "CLK_SELECT_BEST", 7: "CLK_SELECT_STOP"}
        return values[self._clock_select]

    @clock_select.setter
    def clock_select(self, value):
        if value not in clk_values:
            raise ValueError("Select a valid Clock Select setting")
        self._clock_select = value

    @property
    def reset(self):
        """
        Reset the Sensor
        """

        return self._reset

    @reset.setter
    def reset(self, value=1):
        """
        Reset the Sensor
        """
        self._reset = value
        sleep(0.1)

    @property
    def gyro_enabled(self):
        """
        Enables the Gyro
        """
        values = {0: "GYRO_DISABLED", 7: "GYRO_ENABLED"}
        return values[self._gyro_enable]

    @gyro_enabled.setter
    def gyro_enabled(self, value):
        if value not in gyro_en_values:
            raise ValueError("Value must be a valid Gyro Enabled setting")
        self._gyro_enable = value

    @property
    def acc_enabled(self):
        """
        Enables the Accelerometer
        """
        values = {0: "ACC_DISABLED", 7: "ACC_ENABLED"}
        return values[self._acc_enable]

    @acc_enabled.setter
    def acc_enabled(self, value):
        if value not in acc_en_values:
            raise ValueError("Value must be a valid Accelerometer Enabled setting")
        self._acc_enable = value

    @property
    def acceleration(self):
        """
        Return the Sensor Acceleration
        """
        raw_measurement = self._raw_accel_data
        sleep(0.005)
        x = (
            raw_measurement[0]
            / acc_range_sensitivity[self._memory_accel_range]
            * 9.80665
        )
        y = (
            raw_measurement[1]
            / acc_range_sensitivity[self._memory_accel_range]
            * 9.80665
        )
        z = (
            raw_measurement[2]
            / acc_range_sensitivity[self._memory_accel_range]
            * 9.80665
        )

        return x, y, z

    @property
    def gyro(self):
        """
        Gyro information
        """
        raw_gyro_data = self._raw_gyro_data
        sleep(0.005)
        return raw_gyro_data

    @property
    def _power_bank(self):
        return self._power_bank

    @_power_bank.setter
    def _power_bank(self, value):
        self._power_bank = value
        sleep(0.005)

    @property
    def accelerometer_range(self):
        """
        Accelerometer Range
        """
        values = ("RANGE_2G", "RANGE_4G", "RANGE_8G", "RANGE_16G")
        return values[self._memory_accel_range]

    @accelerometer_range.setter
    def accelerometer_range(self, value):
        if value not in acc_range_values:
            raise ValueError("Value must be a valid Accelerometer Range Setting")
        self._bank = 2
        self._acc_data_range = value
        sleep(0.005)
        self._memory_accel_range = value
        self._bank = 0
