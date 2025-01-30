# Chickadee Embedded IoT Framework

## 0 Key Features

* Based on MicroPython
* Supports communication methods and protocols:

> * Bluetooth and WIFI communication,
> * WIFI configuration via Bluetooth or AP
> * Automatic detection of WIFI and Internet connection, automatic reconnection or waiting for external Internet recovery
> * MQTT for pushing sensor data or receiving commands
> * MQTT automatic reconnection
> * External data and operation interfaces provided via HTTP Rest / Bluetooth / MQTT topics
> * Unified data format across all communication methods (Bluetooth/MQTT/HTTP)

* Communication authentication and encryption protection
* Supports scheduled tasks similar to Unix Cron/AT
* Uses asynchronous programming model for clear and efficient code
* Object-oriented programming, providing standard interfaces for easy addition of various sensors and components, only requiring read/write logic, with the rest handled by the framework
* Works with the Puffin app framework for an integrated solution
* Built-in logging service, accessible via hw.log

## 1 Architecture

### 1.1 Core Components

* Main control board.py
* Sensor and information processing framework lib/sensor.py, lib/consumer.py, lib/irq_procuder.py
* Device operation processing framework lib/op.py

### 1.2 Other Components

* WIFI component lib/wifi.py
* Low-power Bluetooth component lib/blu*.py
* Scheduled task component lib/scheduler.py
* MQTT component lib/mqtt*.py
* HTTP component lib/http.py + lib/tinyweb
* Various sensors and controller devices

#### 1.3 Main Control

The main control program integrates all other components to coordinate and implement the full functionality of the device.

The main control is responsible for the following functions:

1. System startup, launching components based on configuration and status
2. System status check and display (via status LED)
3. System button check and entering corresponding states
4. Other system tasks, such as NTP time synchronization, memory garbage collection, etc.

The main control program obtains various system information through hw.py, dev.py, and sys_op.py (configuration program of dat/config.json), assembles components, and runs the system.

### 1.4 Sensor and Information Processing Framework

This framework provides a unified sensor processing framework. Developers only need to focus on developing read/write programs for specific sensors, with communication and data processing handled by the framework.

#### 1.4.1 Architecture Diagram

![Image](docs/Sensor Workflow.png "Sensor Workflow")

#### 1.4.2 Main Files and Classes

* sensor.py, consumer.py, irq_producer.py
* Sensor - Encapsulates sensor data and operations
* Producer - Sensor data producer, related sensor classes must inherit this class. This class internally polls data at regular intervals
* IrqProducer - Interrupt-type sensor data producer, activated by system interrupts, such as human infrared detection sensors
* Consumer - Sensor data consumer, all consumers must inherit this class
* DefaultConsumer - Default consumer, temporarily stores the latest sensor data and provides read operations externally
* SensorProcess - Framework main control, responsible for the following functions

> * Sensor registration
> * Data consumer registration
> * Unified data collection and distribution, using asynchronous queues to collect data and distribute it to all registered consumers

### 1.5 Device Operation Processing Framework

This framework provides a consistent operation call interface, using similar data structures to unify various device operations, facilitating subsequent development. The framework is based on asynchronous locks to avoid conflicts and performance competition.

### 1.5.1 Architecture Diagram

![Image](docs/Controller Diagram.png "Controller Diagram")

### 1.5.2 Main Files, Classes, Methods, and Structures

* op.py
* Controller - Main controller program, performs the following functions

> * Operation registration
> * Unified operation call interface, distributing operations to controlled devices. Uses asynchronous locks to avoid conflicts and performance competition

* Operator - Operator abstract class, all controlled devices must inherit this class and complete internal operation registration
* request method generates request structure
* [request structure](#request) contains parameters needed to call operations
* result method generates result structure
* [result structure](#result) contains operation results and status. Status codes follow HTTP for easy understanding and processing

### 1.5.3 Operation Types

Currently supports three abstract operation types:

1. get - Read information, maps to HTTP GET
2. set - Modify content, maps to HTTP POST, PUT
3. delete - Delete content, maps to HTTP DELETE

### 1.5.4 Operation Matching

Since each controlled device can contain sub-devices, hierarchical path interfaces are needed to match operations, similar to `URL` paths. `Operator.add_command` provides a method to register operations.

```python
    def add_command(self, handler, op = GET, path = None):
```

* `handler` - Operation function, must accept an input parameter
* `op` - Operation, must be one of the three operation types
* `path` - Internal path. Each operation class has a name, the final path is the operation class name + `/` + path

For example, in `sys_op.py` there is the following code:

```python
@singleton
class SysOp(ConfigOp):
    def __init__(self, opc):
        self.__opc = opc
        self.__config = None
        ConfigOp.__init__(self, 'sys', CONFIG_FILE)
        self.commands.pop('sys/config:set') # Cancel set function
        self.add_command(self.__info, GET, 'info')
        self.add_command(self.__commands, GET, 'commands')
        self.add_command(self.__echo, SET, 'echo')
        self.add_command(self.__reboot, SET, 'reboot')
```

This code will provide the following `URL` paths and corresponding `HTTP Methods` to external clients in the HTTP Rest service

```bash
/sys/info, GET
/sys/commands, GET
/sys/echo, POST/PUT
/sys/reboot, POST/PUT
/sys/config, GET/POST/PUT - Introduced via ConfigOp
```

When `Controller.op` is called internally, the path and command parameters correspond to the above content

```python
    async def op(self, path, command, param):
```

If using `Controller.op_request`, the `request` structure needs to include `path`, `command`, `param`. See data structure [request](#request)

```python
    async def op_request(self, request):
```

## 2 Device Configuration

### 2.1 Fixed/Default Configuration

* hw.py - Contains all default factory settings, can be modified by the program during runtime but cannot be saved
* dev.py - Contains various hardware configurations, mainly used to configure sensors and controlled devices, not recommended for program modification, cannot be saved

### 2.2 User Configuration

* [dat/config.json](#datconfigjson) - System user settings, including custom device name, device secret, etc. Can be reset, after reset external applications need to re-authenticate and establish connections
* [dat/cron.json](#datcronjson) - Repeatable scheduled tasks, can be modified via interface
* [dat/wifi.json](#datwifijson) - Wifi connection information, can be modified via interface
* [dat/mqtt.json](#datmqttjson) - MQTT connection information, can be modified via interface

### 2.3 WIFI Configuration

WIFI configuration has two security modes:

1. With system secret, can configure at any time
2. Without system secret, must first enter special configuration mode, then configure via system `PIN`

In either mode, configuration is done via the `set` operation registered in the Wifi class, and read via the `get` operation. All operations can be implemented via any physical interface and protocol supported by the device, such as: Bluetooth, MQTT, HTTP Rest.

The `set` operation only needs to upload a valid wifi.json file, after configuration the system will reconnect to wifi, if successful, the wifi LED will light up. The `Wifi` running status can be read via system status calls. System calls can be made via Bluetooth, MQTT, HTTP (both AP and regular network available)

If wifi fails and there is no low-power Bluetooth, the system must enter special configuration mode for configuration. Currently, only in special configuration mode will the system establish an AP

### 2.4 MQTT Configuration

MQTT configuration only needs to use the `set` operation registered in mqtt.py, upload a valid configuration file. Also read via the `get` operation. MQTT running status can be read via system status calls. All operations can be performed via Bluetooth, MQTT, HTTP (both AP and regular network available).

### 2.5 Scheduled Task Configuration

Scheduled task configuration only needs to use the `set` operation registered in the Scheduler class, upload a valid configuration file. Also read via the `get` operation. System calls can be made via Bluetooth, MQTT, HTTP (both AP and regular network available)

### 2.6 One-time Scheduled Task Configuration

One-time scheduled task configuration only needs to use the `at:set` operation registered in the Scheduler class, upload a valid configuration file. Also delete unexecuted tasks via the `at:delete` operation. All can be done via Bluetooth, MQTT, HTTP (both AP and regular network available)

## 3 System Status

### 3.1 System Status, Prompts, and Functions

* Restart confirmation: Fast blinking at 300 ms intervals, user can double-click to confirm restart
* Special configuration mode confirmation: Blinking at 200 ms intervals, user can double-click to enter special configuration mode
* Reset confirmation: Faster blinking at 100 ms intervals, user can double-click to confirm system reset. Reset will restore user-defined device name to default and regenerate device secret
* WIFI connecting: Blinking, 300ms interval, see wifi.py, no user operations available
* Error status: Very slow blinking, on for 100ms, off for 5 seconds
* Running mode: Normal operation, if WIFI is connected successfully, the WIFI indicator light is on, if WIFI has issues reconnecting, the indicator light follows WIFI connecting status

### 3.2 System Status Entry Methods

* System enters normal mode after startup
* If normal startup fails, automatically enters error mode
* At any time, can switch between different modes by long-pressing the system function key
* In each mode, double-click to confirm

### 3.3 System Button Operations

* Enter system operation status: Long press (hold for more than 5 seconds), if no operation is performed, returns to normal status after 10 seconds
* Continuous long press, will enter different confirmation states in sequence: restart confirmation -> special configuration -> reset confirmation
* Double-click only works in confirmation modes

### 3.4 Special Configuration Mode

* In special configuration mode, system authentication and encryption are done via system PIN
* Request Token does not include timestamp
* Other parts are the same as regular mode

## 4 Writing Device Drivers

### 4.1 Regular Sensor Drivers

* Need to inherit the Producer class in sensor and add related sensors.
* If reading data requires preheating, need to add prepare_handler

Refer to dht11 temperature and humidity sensor

```python
from machine import Pin
from sensor import Producer
import dht

class Dht11(Producer):
    def __init__(self, pin, name = 'dht11'):
        self._pin = pin
        Producer.__init__(self, name, 60000, 1000)
        self._dht = dht.DHT11(Pin(self._pin))
        self.add_sensor("temperature", self.get_temperature)
        self.add_sensor("humidity", self.get_humidity)
        self.set_prepare_handler(self.measure)
```

### 4.2 Interrupt-type Sensors

* Need to inherit IrqProducer and add related sensor data

Refer to pir.py human motion detection

```python
from utils import time_stamp
from irq_producer import IrqProducer
from machine import Pin

class Pir(IrqProducer):
    def __init__(self, pin, name = 'pir'):
        IrqProducer.__init__(self, name)
        self.__irq = Pin(pin, Pin.IN, Pin.PULL_UP) #NOSONAR

    def _get_data(self, b):
        self.__handler_data = { #NOSONAR
            'd': self.name,
            'tm': time_stamp(),
            's': [{
                'n': 'alert',
                'v': 1
            }]
        }
```

## 5 Final System Assembly

### 5.1 Performance Optimization and Testing

* Consolidate all test code into the test directory, strictly separate test code and functional code
* Remove unnecessary functions
* Classes use public members, remove `get`, `set` methods
* Use constants const as much as possible
* Use as few variables as possible
* Use small data structures and small amounts of data to save every byte
* Use memory garbage collection before calling complex operations
* Optimize and simplify code, remove data checking code through strict calling methods between modules

### 5.2 Final System Configuration

* Configure parameters in hw.py
* Add various sensors and control devices to dev.py

### 5.3 Code Protection

Use mpy_cross to compile binary code and copy to the corresponding mpy directory

### 5.4 Firmware Creation

TODO

## 6 External Communication

### 6.1 Basic Design

The [Device Operation Processing Framework](#15-Device-Operation-Processing-Framework) has a unified operation center based on asynchronous methods. All operations must first be registered in the operation center, then through the operation center, provide consistent operation protocols to different external communication methods (HTTP Rest/MQTT/Bluetooth).

All external operations are implemented via `JSON` format, with slight differences in communication protocols for different communication methods

### 6.2 HTTP Rest API

#### 6.2.1 Operation Mapping

* All operations will generate corresponding `URL` paths based on `path`. External clients can operate the device via this path and `HTTP Method`. For example, the following operation can be used to get all device operation paths

```bash
$ curl -X GET -H 'token: testdata' -H 'Content-Type: application/json' 'http://192.168.0.123:8080/sys/commands'
["mqtt/reconnect:set", "mqtt/config:get", "wifi/reconnect:set", "sys/commands:get", "wifi:get", "cron/at:delete", "sys/config:get", "mqtt/config:set", "cron/config:set", "cron/config:get", "relay:get", "wifi/config:set", "relay:set", "cron/at:set", "wifi/config:get", "sys/info:get", "sys/echo:set", "sensors:get", "cron:delete", "mqtt:get", "sys/reboot:set"]
```

* All paths currently do not support `URL Query` parameters

#### 6.2.2 Token and Input Data

* In `HTTP Rest` communication, `Token` is passed via the HTTP header `token`.
* Parameters must conform to the [request structure](#request)

#### 6.2.3 Return Results

* If successful, returns the operation result, which can be any value or empty, with `HTTP` status code `200`
* If failed, returns the [result structure](#result) and corresponding `HTTP` status code

### 6.3 MQTT

#### 6.3.1 MQTT Topics

* Operation command topic - Fixed topic, format: c/device-name, the device will automatically subscribe to this topic, commands sent to this topic will be executed after authentication.
* Operation log topic - Fixed topic, format: o/device-name, the device will automatically send the result of each operation to this topic, `qos=0`. This is the only way to check internal operations (such as scheduled tasks)/MQTT operation results.
* Sensor topic - Sensor topics can be configured by the user. See [dat/mqtt.json](#datmqttjson)

#### 6.3.2 Token and Input Data

* When transmitting operation commands via MQTT, the `Token` must be inserted into the [request structure](#request) via the `"t"` attribute

#### 6.3.3 Return Results

Return results are sent via the `operation log topic`:

* Returns the entire [result structure](#result), and
* Inserts the device name via `"i"`

### 6.4 Bluetooth

#### 6.4.1 Bluetooth UART Connection

* Simulates a Bluetooth UART for bidirectional communication
* Only one connection at a time
* The system sets an authentication limit, if a device cannot complete authentication within 20 seconds, it will be disconnected to allow other devices to connect

#### 6.4.2 Token and Input Data

* Must be `UTF-8` encoded `JSON` format data
* When transmitting operation commands via Bluetooth, the `Token` must be inserted into the [request structure](#request) via the `"t"` attribute

#### 6.4.3 Return Results

* Bluetooth return results are immediately returned via UART.
* If successful, the operation result can be any value or empty
* If failed, returns the [result structure](#result) and corresponding `HTTP` status code

#### 6.4.4 Sensor Data

* The system defaults to using Bluetooth as a sensor data consumer, if the device has an authenticated Bluetooth connection, sensor data will be sent to the connected device
* If there are simultaneous Bluetooth command returns, the receiving end must handle both Bluetooth command returns and sensor data separately. This can be done by distinguishing data formats

## Appendix 1 Common System Operation Interface List

### MQTT

* mqtt/reconnect:set - MQTT reconnect
* mqtt/config:get - MQTT configuration read
* mqtt/config:set - MQTT configuration modify
* mqtt:get - MQTT status read

### WIFI

* wifi:get - Get WIFI connection information
* wifi/reconnect:set - WIFI reconnect
* wifi/config:set - Get WIFI configuration
* wifi/config:get - Get WIFI configuration

### System

* sys/commands:get  - Get system command list
* sys/config:get - Get custom device name and secret
* sys/info:get - Get various system configuration information
* sys/echo:set - Test command
* sys/reboot:set - Reboot device

### Scheduled Tasks

* cron/at:delete - Delete all one-time scheduled tasks
* cron/config:set - Set scheduled tasks
* cron/config:get - Get scheduled tasks
* cron/at:set - Add a one-time task
* cron:delete - Delete all scheduled tasks

### Sensors

* sensors:get - Get the latest sensor data

### Switches

* relay:get - Get relay (switch) status
* relay:set - Set relay (switch) status

## Appendix 2 Common Data Structures

### dat/config.json

```json
{
    "label": "ybb-switch",
    "secret": "1234567890123456"
}
```

### dat/cron.json

```json
[
    {
        "name": "test 1",
        "schedule": "0 * * * * *",
        "params": {
            "p": "sys",
            "c": "echo",
            "a": "Hi"
        }
    }
]
```

### One-time Scheduled Task Format

```json
{
    "name": "test 1",
    "schedule": "0 * * * * *",
    "params": {
        "p": "sys",
        "c": "echo",
        "a": "Hi"
    }
}
```

### dat/mqtt.json

```json
{
    "host": "192.168.1.123",
    "port": 1833,
    "user": "test",
    "password": "test",
    "topic": "sensors",
    "enabled": true
}
```

### dat/wifi.json

```json
{
    "ssid": "SSID",
    "password": "SSID-password",
    "timeout": 15
}
```

### request

```python
def request(p, c, p):
    return {
        PATH: p,
        COMMAND: c,
        ARGS: p
    }
```

### result

```python
def result(c = 0, m = '', v = None):
    return {
        CODE: c,
        MESSAGE: m,
        VALUE: v
    }
```

### Token

#### Token Format

Token is used for authentication and encryption confirmation, with two formats

* Get timestamp - `get_tm`, this `Token` indicates that the request is only used to get the current timestamp of the device, the system automatically ignores the content of the request
* Normal mode - `salt:hash:timestamp` indicates that the request uses the device secret for encryption and needs to verify the timestamp
* Special configuration mode - `salt:hash` indicates that the request uses the device `PIN`, if the system is in special configuration mode, uses `PIN` for decryption, does not verify the timestamp. If the system is in normal mode, returns system mode error

The meanings are as follows:

* `salt` - 4-byte random number or letter
* `hash` - SHA256 hash value
* `timstamp` - epoch seconds

#### Token Calculation and Verification

##### Get Timestamp

Directly fill in the `get-tm` string.

##### Normal Mode

tm = epoch to numeric string
hash = Base64(SHA256(key + salt + tm))
token = salt + ":" + hash + ":" + tm

Verification method: Recalculate `hash` based on `tm`, `salt`, `key` and compare

##### Special Configuration Mode

hash = Base64(SHA256(key + salt))
token = salt + ":" + hash

Verification method: Recalculate `hash` based on `salt`, `pin` and compare

## Appendix 3 Common Questions

### Q1 How to achieve internal linkage between sensors and controlled devices (without external)

The controlled device class inherits the Consumer class, then performs related operations based on specific sensor data

### Q2 How to modify embedded scheduled tasks

Need to download the entire scheduled task configuration cron.json via the interface, modify it in the APP, then upload

### Q3 How to add one-time scheduled tasks

Need to calculate the cron string, then upload via the interface, although it is a cron type, it will only be executed once at the closest time

### Q4 Will unexecuted one-time tasks be retained after restart

No

### Q5 Configure Wifi via Bluetooth

Just call `wifi/config:set` according to the format, upload the content of `dat/wifi.json`

### Q6 How to get the system secret

The system secret can be obtained using the `sys/config:get` operation. The first time it is obtained, need to enter special configuration mode

### Q7 Use different time servers

The default time server address is `pool.ntp.org`. Developers can modify the `NTP_HOST` setting in the `hw.py` file. Users can set `ntphost` in the system configuration `dat/config.json`.

### Q8 The system returns a timestamp from 30 years ago

The embedded system timestamp starts from `January 1, 2000`, which is 946684800 seconds different from normal/Unix, use as needed. The framework has already processed the timestamp in external communications such as Token.

## Appendix 4 Length Limits for Various Communications

* HTTP - 1024 bytes, including all HTTP headers, PATH, Query String, Body
* BlueTooth - The entire Payload must be less than 1024 bytes
* MQTT - The entire Payload must be less than 1024 bytes

## Appendix 5 Project Directory Structure

* / - Entry, configuration, and main control program, main README.md
* /lib - All functional classes and third-party libraries
* /devices - All device-related classes and drivers
* /docs - Documentation and images
* /test - Test programs
* /test/lib - Functional class test programs
* /test/devices - Device test programs
* /mpy - Compiled bytecode files, can be used to generate firmware
* /mpy/lib - Bytecode files for all libraries
* /mpy/devices - Bytecode files for all devices
