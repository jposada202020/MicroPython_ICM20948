# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
icm = icm20948.ICM20948(i2c)

icm.accelerometer_range = icm20948.RANGE_2G

while True:
    for accelerometer_range in icm20948.acc_range_values:
        print("Current Accelerometer range setting: ", icm.accelerometer_range)
        for _ in range(10):
            accx, accy, accz = icm.acceleration
            print(f"x:{accx:.2f}m/s², y:{accy:.2f}m/s², z:{accz:.2f}m/s²")
            print()
            time.sleep(0.5)
        icm.accelerometer_range = accelerometer_range
