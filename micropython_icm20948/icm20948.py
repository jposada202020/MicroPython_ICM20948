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

# pylint: disable=line-too-long

from time import sleep
from micropython import const
from micropython_icm20948.i2c_helpers import CBits, RegisterStruct

try:
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_ICM20948.git"

_REG_WHOAMI = const(0x69)
_DEVICE_ID = const(0x00)

_PWR_MGMT_1 = const(0x06)
_PWR_MGMT_2 = const(0x07)
_REG_BANK_SEL = const(0x7F)
_ACCEL_CONFIG = const(0x14)
_GYRO_CONFIG_1 = const(0x01)
_GYRO_SMPLRT_DIV = const(0x00)
_ACCEL_SMPLRT_DIV_1 = const(0x10)

_ACCEL_XOUT_H = const(0x2D)  # first byte of accel data
_GYRO_XOUT_H = const(0x33)  # first byte of accel data
_TEMP_OUT = const(0x3A)

# ICM20948
CLK_SELECT_INTERNAL = const(0b000)
CLK_SELECT_BEST = const(0b001)
CLK_SELECT_STOP = const(0b111)
clk_values = (CLK_SELECT_INTERNAL, CLK_SELECT_BEST, CLK_SELECT_STOP)

# ICM20948
ACC_DISABLED = const(0b111)
GYRO_DISABLED = const(0b111)
ACC_ENABLED = const(0b000)
GYRO_ENABLED = const(0b000)
TEMP_ENABLED = const(0b0)
TEMP_DISABLED = const(0b1)
gyro_en_values = (GYRO_DISABLED, GYRO_ENABLED)
acc_en_values = (ACC_DISABLED, ACC_ENABLED)
temperature_en_values = (TEMP_DISABLED, TEMP_ENABLED)

# ICM20948 USer Bank
USER_BANK_0 = const(0)
USER_BANK_1 = const(1)
USER_BANK_2 = const(2)
USER_BANK_3 = const(3)
user_bank_values = (USER_BANK_0, USER_BANK_1, USER_BANK_2, USER_BANK_3)

# ACC Range ICM20948
RANGE_2G = const(0b00)
RANGE_4G = const(0b01)
RANGE_8G = const(0b10)
RANGE_16G = const(0b11)
acc_range_values = (RANGE_2G, RANGE_4G, RANGE_8G, RANGE_16G)
acc_range_sensitivity = (16384, 8192, 4096, 2048)

# Acceleration Rate Divisor Values
acc_rate_values = {
    140.6: 7,
    102.3: 10,
    70.3: 15,
    48.9: 22,
    35.2: 31,
    17.6: 63,
    8.8: 127,
    4.4: 255,
    2.2: 513,
    1.1: 1022,
    0.55: 2044,
    0.27: 4095,
}
acc_data_rate_values = (
    140.6,
    102.3,
    70.3,
    48.9,
    35.2,
    17.6,
    8.8,
    4.4,
    2.2,
    1.1,
    0.55,
    0.27,
)
acc_rate_divisor_values = (7, 10, 15, 22, 31, 63, 127, 255, 513, 1022, 2044, 4095)

FREQ_246_0 = const(0b001)
FREQ_111_4 = const(0b010)
FREQ_50_4 = const(0b011)
FREQ_23_9 = const(0b100)
FREQ_11_5 = const(0b101)
FREQ_5_7 = const(0b110)
FREQ_473 = const(0b111)
acc_filter_values = (
    FREQ_246_0,
    FREQ_111_4,
    FREQ_50_4,
    FREQ_23_9,
    FREQ_11_5,
    FREQ_5_7,
    FREQ_473,
)


# Gyro Full Scale
FS_250_DPS = const(0b00)
FS_500_DPS = const(0b01)
FS_1000_DPS = const(0b10)
FS_2000_DPS = const(0b11)
gyro_full_scale_values = (FS_250_DPS, FS_500_DPS, FS_1000_DPS, FS_2000_DPS)
gyro_full_scale_sensitivity = (131, 65.5, 32.8, 16.4)

# Gyro Rate Divisor Values
gyro_rate_values = {
    562.5: 1,
    375.0: 2,
    281.3: 3,
    225.0: 4,
    187.5: 5,
    140.6: 7,
    125.0: 8,
    102.3: 10,
    70.3: 15,
    66.2: 16,
    48.9: 22,
    35.2: 31,
    34.1: 32,
    17.6: 63,
    17.3: 64,
    4.4: 255,
}
gyro_data_rate_values = (
    562.5,
    375.0,
    281.3,
    225.0,
    187.5,
    140.6,
    125.0,
    102.3,
    70.3,
    66.2,
    48.9,
    35.2,
    34.1,
    17.6,
    17.3,
    4.4,
)
gyro_rate_divisor_values = (1, 2, 3, 4, 5, 7, 8, 10, 15, 16, 22, 31, 32, 63, 64, 255)

G_FREQ_196_6 = const(0b000)
G_FREQ_151_8 = const(0b001)
G_FREQ_119_5 = const(0b010)
G_FREQ_51_2 = const(0b011)
G_FREQ_23_9 = const(0b100)
G_FREQ_11_6 = const(0b101)
G_FREQ_5_7 = const(0b110)
G_FREQ_361_4 = const(0b111)
gyro_filter_values = (
    G_FREQ_196_6,
    G_FREQ_151_8,
    G_FREQ_119_5,
    G_FREQ_51_2,
    G_FREQ_23_9,
    G_FREQ_11_6,
    G_FREQ_5_7,
    G_FREQ_361_4,
)


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

        i2c = I2C(1, sda=Pin(2), scl=Pin(3))
        icm = icm20948.ICM20948(i2c)

    Now you have access to the :attr:`acceleration` attribute and :attr:`gyro` attribute

    .. code-block:: python

        accx, accy, accz = icm.accelerometer
        gyro = icm.gyro

    """

    # Register definitions
    _device_id = RegisterStruct(_DEVICE_ID, "B")
    _pwr_mgt_1 = RegisterStruct(_PWR_MGMT_1, "B")
    _pwr_mgt_2 = RegisterStruct(_PWR_MGMT_2, "B")

    # Register PWR_MGMT_1 (0x06)
    # | DEVICE RESET | SLEEP |  LP_EN | ---- | TEMP_DIS | CLKSEL(2) | CLKSEL(1) | CLKSEL(0) |
    _clock_select = CBits(3, _PWR_MGMT_1, 0)
    _temp_enabled = CBits(1, _PWR_MGMT_1, 3)
    _sleep = CBits(1, _PWR_MGMT_1, 6)
    _reset = CBits(1, _PWR_MGMT_1, 7)

    # Register PWR_MGMT_2 (0x07)
    # |----|----|DISABLE_ACCEL(2)|DISABLE_ACCEL(1)|DISABLE_ACCEL(0)|DISABLE_GYRO(2)|DISABLE_GYRO(1)|DISABLE_GYRO(0)|
    _gyro_enable = CBits(3, _PWR_MGMT_2, 0)
    _acc_enable = CBits(3, _PWR_MGMT_2, 3)

    _raw_accel_data = RegisterStruct(_ACCEL_XOUT_H, ">hhh")
    _raw_gyro_data = RegisterStruct(_GYRO_XOUT_H, ">hhh")
    _raw_temp_data = RegisterStruct(_GYRO_XOUT_H, ">hhhh")

    # Register REG_BANK_SEL (0x7F)
    # | ---- | ---- |  USER_BANK(1) | USER_BANK(0) | ---- | ---- | ---- | ---- |
    _user_bank = CBits(2, _REG_BANK_SEL, 4)

    # BANK 2
    _gyro_rate_divisor = RegisterStruct(_GYRO_SMPLRT_DIV, ">B")
    _acc_rate_divisor = RegisterStruct(_ACCEL_SMPLRT_DIV_1, ">H")

    # ACCEL_CONFIG (0x14)
    # |----|----|ACCEL_DLPFCFG(2)|ACCEL_DLPFCFG(1)|ACCEL_DLPFCFG(0)|ACCEL_FS_SEL[(1)|ACCEL_FS_SEL[(0)|ACCEL_FCHOICE|
    _acc_choice = CBits(1, _ACCEL_CONFIG, 0)
    _acc_data_range = CBits(2, _ACCEL_CONFIG, 1)
    _acc_dplcfg = CBits(3, _ACCEL_CONFIG, 3)

    # _GYRO_CONFIG_1 (0x01)
    # |----|----|GYRO_DLPFCFG(2)|GYRO_DLPFCFG(1)|GYRO_DLPFCFG(0)|GYRO_FS_SEL[(1)|GYRO_FS_SEL[(0)|GYRO_FCHOICE|
    _gyro_choice = CBits(0, _GYRO_CONFIG_1, 0)
    _gyro_full_scale = CBits(2, _GYRO_CONFIG_1, 1)
    _gyro_dplcfg = CBits(3, _GYRO_CONFIG_1, 3)

    def __init__(self, i2c, address=0x69):
        self._i2c = i2c
        self._address = address

        if self._device_id != 0xEA:
            raise RuntimeError("Failed to find the ICM20948 sensor!")

        self.reset = True
        self._sleep = 0
        self._bank = 0
        self.accelerometer_range = RANGE_2G
        self.gyro_full_scale = FS_500_DPS

        self.acc_data_rate_divisor = 22
        self.gyro_data_rate_divisor = 10

    @property
    def clock_select(self):
        """
        CLK_SELECT_INTERNAL: Internal 20 MHz oscillator
        CLK_SELECT_BEST: Auto selects the best available clock source - PLL if
        ready, else use the Internal oscillator
        CLK_SELECT_STOP: Stops the clock and keeps timing generator in reset
        NOTE: CLKSEL should be set to ``CLK_SELECT_BEST`` to achieve full
        gyroscope performance.

        +------------------------------------------+-------------------+
        | Mode                                     | Value             |
        +==========================================+===================+
        | :py:const:`icm20948.CLK_SELECT_INTERNAL` | :py:const:`0b000` |
        +------------------------------------------+-------------------+
        | :py:const:`icm20948.CLK_SELECT_BEST`     | :py:const:`0b001` |
        +------------------------------------------+-------------------+
        | :py:const:`icm20948.CLK_SELECT_STOP`     | :py:const:`0b111` |
        +------------------------------------------+-------------------+


        """

        values = {0: "CLK_SELECT_INTERNAL", 1: "CLK_SELECT_BEST", 7: "CLK_SELECT_STOP"}
        return values[self._clock_select]

    @clock_select.setter
    def clock_select(self, value):
        if value not in clk_values:
            raise ValueError("Select a valid Clock Select setting")
        self._clock_select = value

    @property
    def reset(self) -> int:
        """
        Reset the internal registers and restores the default settings. Write a 1 to set the
        reset, the bit will auto clear
        """

        return self._reset

    @reset.setter
    def reset(self, value: int = 1) -> None:
        self._reset = value
        sleep(1)

    @property
    def gyro_enabled(self) -> str:
        """
        Gyro Enabled

        +------------------------------------+------------------------------------------------------+
        | Mode                               | Value                                                |
        +====================================+======================================================+
        | :py:const:`icm20948.GYRO_ENABLED`  | :py:const:`0b000` Gyroscope (all axes) on            |
        +------------------------------------+------------------------------------------------------+
        | :py:const:`icm20948.GYRO_DISABLED` | :py:const:`0b111` Gyroscope (all axes) disabled      |
        +------------------------------------+------------------------------------------------------+

        """
        values = {0: "GYRO_DISABLED", 7: "GYRO_ENABLED"}
        return values[self._gyro_enable]

    @gyro_enabled.setter
    def gyro_enabled(self, value: int) -> None:
        if value not in gyro_en_values:
            raise ValueError("Value must be a valid Gyro Enabled setting")
        self._gyro_enable = value

    @property
    def acc_enabled(self) -> str:
        """
        Accelerometer enabled

        +------------------------------------+------------------------------------------------------+
        | Mode                               | Value                                                |
        +====================================+======================================================+
        | :py:const:`icm20948.ACC_ENABLED`   | :py:const:`0b000` Accelerometer (all axes) on        |
        +------------------------------------+------------------------------------------------------+
        | :py:const:`icm20948.ACC_DISABLED`  | :py:const:`0b111` Accelerometer (all axes) disabled  |
        +------------------------------------+------------------------------------------------------+

        """
        values = {0: "ACC_DISABLED", 7: "ACC_ENABLED"}
        return values[self._acc_enable]

    @acc_enabled.setter
    def acc_enabled(self, value: int) -> None:
        if value not in acc_en_values:
            raise ValueError("Value must be a valid Accelerometer Enabled setting")
        self._acc_enable = value

    @property
    def temperature_enabled(self) -> str:
        """
        Temperature Enabled. When set to 1, this bit disables the temperature sensor.

        +------------------------------------+----------------------------------------+
        | Mode                               | Value                                  |
        +====================================+========================================+
        | :py:const:`icm20948.TEMP_ENABLED`  | :py:const:`0b0` Temperature on         |
        +------------------------------------+----------------------------------------+
        | :py:const:`icm20948.TEMP_DISABLED` | :py:const:`0b1` Temperature disabled   |
        +------------------------------------+----------------------------------------+

        """
        values = ("TEMP_DISABLED", "TEMP_ENABLED")
        return values[self._temp_enabled]

    @temperature_enabled.setter
    def temperature_enabled(self, value: int) -> None:
        if value not in temperature_en_values:
            raise ValueError("Value must be a valid Temperature Enabled setting")
        self._temp_enabled = value

    @property
    def acceleration(self) -> Tuple[float, float, float]:
        """
        Acceleration Property. The x, y, z acceleration values returned in a 3-tuple
        and are in :math:`m / s ^ 2.`
        :return: Acceleration Values
        """
        raw_measurement = self._raw_accel_data
        # sleep(0.005)
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
    def gyro(self) -> Tuple[float, float, float]:
        """
        Gyro Property. The x, y, z angular velocity values returned in a 3-tuple and
        are in :math:`degrees / second`
        :return: Angular velocity Values
        """
        raw_measurement = self._raw_gyro_data
        # sleep(0.005)
        x = (
            raw_measurement[0]
            / gyro_full_scale_sensitivity[self._memory_gyro_fs]
            * 0.017453293
        )
        y = (
            raw_measurement[1]
            / gyro_full_scale_sensitivity[self._memory_gyro_fs]
            * 0.017453293
        )
        z = (
            raw_measurement[2]
            / gyro_full_scale_sensitivity[self._memory_gyro_fs]
            * 0.017453293
        )

        return x, y, z

    @property
    def power_bank(self) -> int:
        """
        Power bank selected
        """
        return self._user_bank

    @power_bank.setter
    def power_bank(self, value: int) -> None:
        self._user_bank = value
        sleep(0.005)

    @property
    def accelerometer_range(self) -> str:
        """
        Sensor acceleration_range

        +--------------------------------+------------------+
        | Mode                           | Value            |
        +================================+==================+
        | :py:const:`icm20948.RANGE_2G`  | :py:const:`0b00` |
        +--------------------------------+------------------+
        | :py:const:`icm20948.RANGE_4G`  | :py:const:`0b01` |
        +--------------------------------+------------------+
        | :py:const:`icm20948.RANGE_8G`  | :py:const:`0b10` |
        +--------------------------------+------------------+
        | :py:const:`icm20948.RANGE_16G` | :py:const:`0b11` |
        +--------------------------------+------------------+

        """
        values = ("RANGE_2G", "RANGE_4G", "RANGE_8G", "RANGE_16G")
        return values[self._memory_accel_range]

    @accelerometer_range.setter
    def accelerometer_range(self, value: int) -> None:
        if value not in acc_range_values:
            raise ValueError("Value must be a valid Accelerometer Range Setting")
        self._user_bank = 2
        self._acc_data_range = value
        self._memory_accel_range = value
        self._user_bank = 0

    @property
    def gyro_full_scale(self) -> str:
        """
        Sensor gyro_full_scale

        +----------------------------------+------------------+
        | Mode                             | Value            |
        +==================================+==================+
        | :py:const:`icm20948.FS_250_DPS`  | :py:const:`0b00` |
        +----------------------------------+------------------+
        | :py:const:`icm20948.FS_500_DPS`  | :py:const:`0b01` |
        +----------------------------------+------------------+
        | :py:const:`icm20948.FS_1000_DPS` | :py:const:`0b10` |
        +----------------------------------+------------------+
        | :py:const:`icm20948.FS_2000_DPS` | :py:const:`0b11` |
        +----------------------------------+------------------+
        """
        values = ("FS_250_DPS", "FS_500_DPS", "FS_1000_DPS", "FS_2000_DPS")
        return values[self._memory_gyro_fs]

    @gyro_full_scale.setter
    def gyro_full_scale(self, value: int) -> None:
        if value not in gyro_full_scale_values:
            raise ValueError("Value must be a valid gyro_full_scale setting")
        self._user_bank = 2
        self._gyro_full_scale = value
        # sleep(0.005)
        self._memory_gyro_fs = value
        self._user_bank = 0
        # sleep(0.1)

    @property
    def temperature(self) -> float:
        """
        Temperature Value. In the setup tested, there is the need to read either the values
        from acceleration, gyro and temperature or gyro and temperature at the same time
        in order to have a logic temperature value.

        """
        return (self._raw_temp_data[3] / 333.87) + 21

    @property
    def gyro_data_rate(self):
        """The rate at which gyro measurements are taken in Hz"""
        return list(gyro_rate_values.keys())[
            list(gyro_rate_values.values()).index(self.gyro_data_rate_divisor)
        ]

    @gyro_data_rate.setter
    def gyro_data_rate(self, value: int) -> None:
        """
        .. note::

            The data rates are set indirectly by setting a rate divisor according to the
            following formula:

            .. math::

                \\text{gyro_data_rate } = \\frac{1125}{1 + divisor}

        However, this library will accept only data rates specified in the following list to match the
        right divisor.

        Accepted values are:

        | * 562.5
        | * 375.0
        | * 281.3
        | * 225.0
        | * 187.5
        | * 140.6
        | * 125.0
        | * 102.3
        | * 70.3
        | * 66.2
        | * 48.9
        | * 35.2
        | * 34.1
        | * 17.6
        | * 17.3
        | * 4.4

        """
        if value not in gyro_data_rate_values:
            raise ValueError("Gyro data rate must be a valid setting")

        self.gyro_data_rate_divisor = gyro_rate_values[value]

    @property
    def gyro_data_rate_divisor(self) -> int:
        """
        Accepted values are:

        | * 1
        | * 2
        | * 3
        | * 4
        | * 5
        | * 7
        | * 8
        | * 10
        | * 15
        | * 16
        | * 22
        | * 31
        | * 32
        | * 63
        | * 64
        | * 255

        """

        self._user_bank = 2
        raw_rate_divisor = self._gyro_rate_divisor
        # sleep(0.005)
        self._user_bank = 0
        return raw_rate_divisor

    @gyro_data_rate_divisor.setter
    def gyro_data_rate_divisor(self, value: int) -> None:
        if value not in gyro_rate_divisor_values:
            raise ValueError("Value must be a valid gyro data rate divisor setting")
        self._user_bank = 2
        # sleep(0.005)
        self._gyro_rate_divisor = value
        self._user_bank = 0
        # sleep(0.005)

    @property
    def acc_data_rate(self):
        """The rate at which accelerometer measurements are taken in Hz"""
        return list(acc_rate_values.keys())[
            list(acc_rate_values.values()).index(self.acc_data_rate_divisor)
        ]

    @acc_data_rate.setter
    def acc_data_rate(self, value: int) -> None:
        """
        .. note::

            The data rates are set indirectly by setting a rate divisor according to the
            following formula:

            .. math::

                \\text{acc_data_rate } = \\frac{1125}{1 + divisor}

        However, this library will accept only data rates specified in the following list to match the
        right divisor.

        Accepted values are:

        | * 140.6
        | * 102.3
        | * 70.3
        | * 48.9
        | * 35.2
        | * 17.6
        | * 8.8
        | * 4.4
        | * 2.2
        | * 1.1
        | * 0.55
        | * 0.27

        """
        if value not in acc_data_rate_values:
            raise ValueError("Accelerometer data rate must be a valid setting")

        self.acc_data_rate_divisor = acc_rate_values[value]

    @property
    def acc_data_rate_divisor(self) -> int:
        """
        Accepted values are:

        | * 7
        | * 10
        | * 15
        | * 22
        | * 31
        | * 63
        | * 127
        | * 255
        | * 513
        | * 1022
        | * 2044
        | * 4095

        """

        self._user_bank = 2
        raw_rate_divisor = self._acc_rate_divisor
        # sleep(0.005)
        self._user_bank = 0
        return raw_rate_divisor

    @acc_data_rate_divisor.setter
    def acc_data_rate_divisor(self, value: int) -> None:
        if value not in acc_rate_divisor_values:
            raise ValueError(
                "Value must be a valid acceleration data rate divisor setting"
            )
        self._user_bank = 2
        # sleep(0.005)
        self._acc_rate_divisor = value
        self._user_bank = 0
        # sleep(0.005)

    @property
    def acc_dlpf_cutoff(self) -> int:
        """The cutoff frequency for the accelerometer's digital low pass filter. Signals
        above the given frequency will be filtered out.

        .. note::
            Readings immediately following setting a cutoff frequency will be
            inaccurate due to the filter "warming up"

        +---------------------------------+-------------------+
        | Mode                            | Value             |
        +=================================+===================+
        | :py:const:`icm20948.FREQ_246_0` | :py:const:`0b001` |
        +---------------------------------+-------------------+
        | :py:const:`icm20948.FREQ_111_4` | :py:const:`0b010` |
        +---------------------------------+-------------------+
        | :py:const:`icm20948.FREQ_50_4`  | :py:const:`0b011` |
        +---------------------------------+-------------------+
        | :py:const:`icm20948.FREQ_23_9`  | :py:const:`0b100` |
        +---------------------------------+-------------------+
        | :py:const:`icm20948.FREQ_11_5`  | :py:const:`0b101` |
        +---------------------------------+-------------------+
        | :py:const:`icm20948.FREQ_5_7`   | :py:const:`0b110` |
        +---------------------------------+-------------------+
        | :py:const:`icm20948.FREQ_473`   | :py:const:`0b111` |
        +---------------------------------+-------------------+
        """
        values = (
            "FREQ_246_0",
            "FREQ_111_4",
            "FREQ_50_4",
            "FREQ_23_9",
            "FREQ_11_5",
            "FREQ_5_7",
            "FREQ_473",
        )
        self._user_bank = 2
        # sleep(0.005)
        raw_value = self._acc_dplcfg
        print(raw_value)
        self._user_bank = 0
        return values[raw_value - 1]

    @acc_dlpf_cutoff.setter
    def acc_dlpf_cutoff(self, value: int) -> None:
        if value not in acc_filter_values:
            raise ValueError("Value must be a valid dlpf setting")
        self._user_bank = 2
        # sleep(0.005)
        self._acc_dplcfg = value
        self._user_bank = 0
        # sleep(0.005)

    @property
    def acc_filter_choice(self) -> int:
        """Enables accelerometer DLPF"""
        self._user_bank = 2
        # sleep(0.005)
        raw_value = self._acc_choice
        self._user_bank = 0
        return raw_value

    @acc_filter_choice.setter
    def acc_filter_choice(self, value: int) -> None:
        self._user_bank = 2
        # sleep(0.005)
        self._acc_choice = value
        self._user_bank = 0
        # sleep(0.05)

    @property
    def gyro_dlpf_cutoff(self) -> int:
        """The cutoff frequency for the gyro's digital low pass filter. Signals
        above the given frequency will be filtered out.

        .. note::
            Readings immediately following setting a cutoff frequency will be
            inaccurate due to the filter "warming up"

        +-----------------------------------+-------------------+
        | Mode                              | Value             |
        +===================================+===================+
        | :py:const:`icm20948.G_FREQ_196_6` | :py:const:`0b000` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_151_8` | :py:const:`0b001` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_119_5` | :py:const:`0b010` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_51_2`  | :py:const:`0b011` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_23_9`  | :py:const:`0b100` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_11_6`  | :py:const:`0b101` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_5_7`   | :py:const:`0b110` |
        +-----------------------------------+-------------------+
        | :py:const:`icm20948.G_FREQ_361_4` | :py:const:`0b111` |
        +-----------------------------------+-------------------+
        """
        values = (
            "G_FREQ_196_6",
            "G_FREQ_151_8",
            "G_FREQ_119_5",
            "G_FREQ_51_2",
            "G_FREQ_23_9",
            "G_FREQ_11_6",
            "G_FREQ_5_7",
            "G_FREQ_361_4",
        )
        self._user_bank = 2
        # sleep(0.005)
        raw_value = self._gyro_dplcfg
        self._user_bank = 0
        return values[raw_value]

    @gyro_dlpf_cutoff.setter
    def gyro_dlpf_cutoff(self, value: int) -> None:
        if value not in gyro_filter_values:
            raise ValueError("Value must be a valid dlpf setting")
        self._user_bank = 2
        # sleep(0.005)
        self._gyro_dplcfg = value
        self._user_bank = 0
        # sleep(0.005)

    @property
    def gyro_filter_choice(self) -> int:
        """Enables gyro DLPF"""
        self._user_bank = 2
        # sleep(0.005)
        raw_value = self._gyro_choice
        self._user_bank = 0
        return raw_value

    @gyro_filter_choice.setter
    def gyro_filter_choice(self, value: int) -> None:
        self._user_bank = 2
        # sleep(0.005)
        self._gyro_choice = value
        self._user_bank = 0
        # sleep(0.05)
