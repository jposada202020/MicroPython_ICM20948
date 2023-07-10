# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
icm = icm20948.ICM20948(i2c)

icm.clock_select = icm20948.CLK_SELECT_INTERNAL

while True:
    for clock_select in icm20948.clk_values:
        print("Current Clock select setting: ", icm.clock_select)
        for _ in range(10):
            accx, accy, accz = icm.acceleration
            print("x:{:.2f}m/s2, y:{:.2f}m/s2, z:{:.2f}m/s2".format(accx, accy, accz))
            print()
            time.sleep(0.5)
        icm.clock_select = clock_select
