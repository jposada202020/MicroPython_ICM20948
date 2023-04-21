# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`icm20948`
================================================================================

MicroPython Driver for the ICM20948 Accelerometer/Gyro Sensor


* Author(s): Jose D. Montoya

Implementation Notes
--------------------

**Software and Dependencies:**

This library depends on Micropython

"""

# pylint: disable=too-many-arguments, line-too-long, too-many-instance-attributes

from micropython import const
from micropython_icm20948.i2c_helpers import CBits, RegisterStruct


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_ICM20948.git"

_REG_WHOAMI = const(0x69)
_DEVICE_ID = const(0x00)

_PWR_MGMT_1 = const(0x06)

# ICM20948
CLK_SELECT_INTERNAL = const(0b000)
CLK_SELECT_BEST = const(0b001)
CLK_SELECT_STOP = const(0b111)
# End
clk_values = (CLK_SELECT_INTERNAL, CLK_SELECT_BEST, CLK_SELECT_STOP)


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

    # Register PWR_MGMT_1 (0x06)
    # | DEVICE RESET | SLEEP |  TMP_RDY | PRS_RDY | ---- | CLKSEL(2) | CLKSEL(1) | CLKSEL(0) |
    _clock_select = CBits(3, _PWR_MGMT_1, 0)
    _reset = CBits(1, _PWR_MGMT_1, 7)

    def __init__(self, i2c, address=_REG_WHOAMI):
        self._i2c = i2c
        self._address = address

        if self._device_id != 0xEA:
            raise RuntimeError("Failed to find the ICM20948 sensor!")

        # print(bin(self._pwr_mgt_1), hex(self._pwr_mgt_1))
        # print(self.clock_select)

    @property
    def clock_select(self):
        """
        CLK_SELECT_INTERNAL: Internal 20 MHz oscillator
        CLK_SELECT_BEST: Auto selects the best available clock source – PLL if ready, else use the Internal oscillator
        CLK_SELECT_STOP: Stops the clock and keeps timing generator in reset
        NOTE: CLKSEL should be set to :attr:`CLK_SELECT_BEST` to achieve full gyroscope performance.
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
    def reset(self):
        """
        Reset the Sensor
        """

        self._reset = 1
