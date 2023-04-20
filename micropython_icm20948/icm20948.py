# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`icm20948`
================================================================================

MicroPython Driver for the Accelerometer and Gyro ICM20948 Sensor


* Author(s): Jose D. Montoya


"""

# pylint: disable=too-many-arguments, line-too-long, too-many-instance-attributes

import time
import math
from micropython import const
from micropython_icm20948.i2c_helpers import CBits, RegisterStruct

try:
    import struct
except ImportError:
    import ustruct as struct

_REG_WHOAMI = const(0x69)
_DEVICE_ID = const(0x00)


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

    def __init__(self, i2c, address=_REG_WHOAMI):
        self._i2c = i2c
        self._address = address

        if self._device_id != 0xEA:
            raise RuntimeError("Failed to find the ICM20948 sensor!")

        print(bin(self._device_id), hex(self._device_id))
