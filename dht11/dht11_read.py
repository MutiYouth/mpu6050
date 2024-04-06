#!/bin/usr/env python3
# -*- coding: utf-8 -*-
#
#
#
# author weng
# version: v 0.1.0
# date 2024-04-06 22:28
#
# noinspection PyUnresolvedReferences
import RPi.GPIO as GPIO
import time

# import serial

# ser = serial.Serial("/dev/ttyAMA0", 9600)

tmp0 = []  # Used to store the read data
tmp1 = []
tmp2 = []

data0 = 12  # 17, DHT11 BCM

a, b = 0, 0


def delay_us(t):
    start, end = 0, 0
    start = time.time()
    t = (t - 3) / 1000000
    while end - start < t:
        end = time.time()


def loop_until_is_not_low_or_high(low_or_high_flag, time_out_s=0.1, channel=data0):
    """
    :param low_or_high_flag: 0, low; 1, high
    :param time_out_s:
    :param channel:
    :return:
    """
    a = time.time()
    while GPIO.input(channel) == low_or_high_flag:
        b = time.time()  # time the record ended
        if (b - a) > time_out_s:
            break


def dht11_survey(gpio_channel=data0):
    GPIO.setup(gpio_channel, GPIO.OUT)  # GPIO OUTPUT

    # 1. MCU initiates read ( Start Condition )

    GPIO.output(gpio_channel, GPIO.HIGH)
    delay_us(10 * 1000)  # delay 10ms

    # mcu pulls low to send start
    GPIO.output(gpio_channel, GPIO.LOW)
    delay_us(25 * 1000)  # delay 25ms

    # mcu pulls high and waits for response (20 ~ 40us)
    GPIO.output(gpio_channel, GPIO.HIGH)
    GPIO.setup(gpio_channel, GPIO.IN)  # GPIO INPUT


    # 2. DHT Responds and pulls LOW、HIGH

    # Recording cycle start time
    # Determine whether the cycle time exceeds 0.1 seconds to avoid
    # the program from entering an infinite loop and getting stuck
    loop_until_is_not_low_or_high(1, 0.1, gpio_channel)  # 确保已经从高电平下来了

    # DHT responds and pulls low  (80us)
    loop_until_is_not_low_or_high(0, 0.1, gpio_channel)  # 80us
    # pulls high to indicate get ready (80us)
    loop_until_is_not_low_or_high(1, 0.1, gpio_channel)  # 80us



    # 3. DHT sends 40 data bits (DATA Transfer)

    for bit_i in range(40):
        loop_until_is_not_low_or_high(0, 0.1, gpio_channel)  # 50us

        delay_us(28)  # delay 28 microseconds

        if GPIO.input(gpio_channel):  # After more than 28 microseconds, it is judged whether it is still at a high level
            tmp0.append(1)  # Record the received bit as 1

            loop_until_is_not_low_or_high(1, 0.1, gpio_channel)  # Loop until the input is low
        else:
            tmp0.append(0)  # Record the received bit as 0


if __name__ == "__main__":

    while True:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        del tmp0[0:]  # delete list

        time.sleep(1)  # Delay 1 second

        dht11_survey()

        humidity0_bit = tmp0[0:8]  # Delimited list, bits 0 to 7 are humidity integer data
        humidity0_point_bit = tmp0[8:16]  # Humidity Decimals
        temperature0_bit = tmp0[16:24]  # Integer temperature
        temperature0_point_bit = tmp0[24:32]  # temperature decimal
        check0_bit = tmp0[32:40]  # check data

        humidity0_int = 0
        humidity0_point = 0
        temperature0_int = 0
        temperature0_point = 0

        check0 = 0

        for i in range(8):  # convert binary to decimal
            humidity0_int += humidity0_bit[i] * 2 ** (7 - i)
            humidity0_point += humidity0_point_bit[i] * 2 ** (7 - i)
            temperature0_int += temperature0_bit[i] * 2 ** (7 - i)
            temperature0_point += temperature0_point_bit[i] * 2 ** (7 - i)
            check0 += check0_bit[i] * 2 ** (7 - i)

        humidity0 = humidity0_int + humidity0_point / 10
        temperature0 = temperature0_int + temperature0_point / 10
        check0_tmp0 = humidity0_int + humidity0_point + temperature0_int + temperature0_point

        if check0 == check0_tmp0 and temperature0 != 0 and temperature0 != 0:  # Determine if the data is normal
            print("Temperature, Humidity: ", temperature0, "C, ", humidity0, "%")  # Print the temperature and humidity data

            temperature00 = str(temperature0)
            humidity00 = str(humidity0)

            th = temperature00 + ";" + humidity00 + ";"
            # ser.write(th.encode())
        else:
            print("error")

        time.sleep(1)
        GPIO.cleanup()
