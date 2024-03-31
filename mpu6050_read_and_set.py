#!/bin/usr/env python3
# -*- coding: utf-8 -*-
# 
# 
# 
# author csunking@gmail.com
# version: v 0.1.0
# date 2024-03-31 00:50
#
# noinspection PyUnresolvedReferences
import smbus
import math
from time import sleep
import numpy as np


class MPU6050:
    # 一些MPU6050寄存器及其地址
    PWR_MGMT_1 = 0x6B  # 电源控制寄存器地址
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    INT_ENABLE = 0x38

    ACC_X_OUT_H = 0x3B
    ACC_Y_OUT_H = 0x3D
    ACC_Z_OUT_H = 0x3F
    GYR_X_OUT_H = 0x43
    GYR_Y_OUT_H = 0x45
    GYR_Z_OUT_H = 0x47

    def __init__(self):
        self.bus = smbus.SMBus(1)  # MPU6050 Sensor bus, I2C模块初始化
        self.address = 0x68  # 外接I2C设备的地址

        self.bus.write_byte_data(self.address, self.SMPLRT_DIV, 7)  # 写入采样速率寄存器
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 1)  # 写入电源管理寄存器
        self.bus.write_byte_data(self.address, self.CONFIG, 0)  # 写入配置寄存器
        self.bus.write_byte_data(self.address, self.INT_ENABLE, 1)  # 写中断使能寄存器

        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0)  # 写入陀螺配置寄存器
        # ACCEL_CONFIG write 16 就是将 AFS_SEL 设置为 2。此时scale就不是 1 /(16384 LSB/g)了，而是 1/(4096 LSB/g)。
        # 16 的二进制为 0x 0001 0000。 x86为小端存储，内存中为 0000 1000 （ 低地址 -- 高地址位），
        # 直接写入的话，对应于打端存储的嵌入式设备的值为  0000 1000  （ 高地址 -- 低地址位），
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 8)  # 写入ACC配置寄存器.

    def mpu6050_read_data(self, addr):
        """
        读取MPU6050数据寄存器, 加速度值和陀螺值为16位

        通过 bus 调用 read_byte_data 方法来读取 MPU6050 传感器的数据寄存器值。
        addr 参数指定要读取的寄存器地址，high 和 low 分别存储高位和低位的字节值。
        :param addr:
        :return:
        """
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        # 这一行代码将高位和低位的字节值合并为一个 16 位的值。 通过位运算符 << 左移 8 位，然后通过位运算符 | 进行位或操作。
        value = ((high << 8) | low)
        # 这个条件判断用于检查 16 位的值是否超过了有符号数的最大范围（32768）。如果超过了，就将其减去 65536，以得到有符号的值。
        if value > 32768:
            value = value - 65536

        return value

    def read_word(self, adr):
        """
        封装一些读职数据的功能函徵数
        读取一个字长度的数据(16位)
        :param adr:
        :return:
        """
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr + 1)
        val = (high << 8) + low
        return val

    # 将读取到的数据转换为原码(有符号数本身是采用补码方式存储的)
    def read_word_real(self, adr):
        val = self.read_word(adr)
        x = 0xffff
        if val >= 0x8000:  # 首位为1表示是负数
            return -((x - val) + 1)  # 求原码
        else:
            return val

    def demo_read_mpu6050(self) -> None:
        # 设置电源模式
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)
        acc_scale = 9.8 / 8192  # 0, 16384; 8,8192; 16, 4096; 24, 2048;
        gyr_scale = 1 / 131 / 180 * math.pi

        while True:
            sleep(0.1)
            acc_x = self.mpu6050_read_data(self.ACC_X_OUT_H) * acc_scale  # read_word_real 等效于 mpu6050_read_data
            acc_y = self.mpu6050_read_data(self.ACC_Y_OUT_H) * acc_scale
            acc_z = self.mpu6050_read_data(self.ACC_Z_OUT_H) * acc_scale

            gyro_x = self.mpu6050_read_data(self.GYR_X_OUT_H) * gyr_scale  # 原始数据 * gyr_scale
            gyro_y = self.mpu6050_read_data(self.GYR_Y_OUT_H) * gyr_scale
            gyro_z = self.mpu6050_read_data(self.GYR_Z_OUT_H) * gyr_scale

            temp = self.mpu6050_read_data(0x41) / 340 + 36.53  # 摄氏温度数据

            # 把获取整理后的值存储到字典里
            # sensor_data = {
            #     "Ax" : Ax,
            # ...
            # }

            acc_norm = np.linalg.norm([acc_x, acc_y, acc_z], ord=2)
            print("temp, acc, gyr: %.3f \033[1;34m %.6f, %.6f, %.6f, %.3f \033[1;32m %.6f, %.6f, %.6f\033[0m"
                  % (temp, acc_x, acc_y, acc_z, acc_norm, gyro_x, gyro_y, gyro_z))  # "{:.2f}".format(value)


if __name__ == "__main__":
    print("hello config.")
    mpu_obj = MPU6050()
    mpu_obj.demo_read_mpu6050()
