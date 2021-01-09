from micropython import const
'''
硬件配置文件 - 只读
'''
# 设备类型
TYPE = "ybb-switch"

# 是否启用WIFI
WIFI = True
# Wifi 检查间隔（秒）- 检查 WIFI 设备是否连接，并且本地网关Ping, 允许值: 0 - 300
WIFI_CHECK_INTVAL = const(30)
# Wifi 检查方式，0-不检查，1-只检查设备Wifi连接，2-Ping本地网关，3-Ping外部地址
WIFI_CHECK_TYPE = const(3)
WIFI_CHECK_HOST = "8.8.8.8" # 外部地址，可以通过config.json 里的 wifi_check_host覆盖

# 是否启用低功耗蓝牙
BLE_UART = True

# 是否启用 MQTT（必须启用WIFI）。该设置是硬件层面设置。用户可以通过 dat/mqtt.json 启用或关闭
MQTT = True

# 是否启用 Scheduler
SCHEDULER = True

# 是否启用 HTTP服务（必须启用WIFI）
HTTP = True
HTTP_PORT = const(8080)

# WIFI 信号 LED Pin 脚号
WIFI_LED_PIN = const(2)
# 系统按钮 Pin 脚号
SYS_BUTTON_PIN = const(32)

# 是否启用 NTP 时间
NTP = True
# NTP服务器域名或IP
NTP_HOST = "pool.ntp.org"
# NTP同步间隔（秒）
NTP_INTERVAL = const(30)

# 在日志里打印每次收集到的传感器数据
PRINT_SENSOR_DATA = True

# 垃圾收间隔
GC_INTERVAL = const(60)

import logging
log = logging.getLogger("ybb")

from machine import unique_id
from struct import unpack
x = unique_id()
MAC = "%x:%x:%x:%x:%x:%x" % unpack("BBBBBB",x)
UNIQUE_ID =  "%x%x%x%x%x%x" % unpack("BBBBBB",x)
DEVICE_NAME = TYPE + '-' + UNIQUE_ID

# 硬件码，需要在烧录时使用，八位字母和数字
HW_PIN = '12345678'