# Micropython Windows 开发环境搭建

## 1 软件环境

1. Python: 3.7.9
2. Python Pakcage

> * pip
> * mpfsshell
> * mpfsshell-lite
> * mpy_cross

3. Git
4. IDE：VSCode

> * Pymkar 插件
> * Mpfsshell
> * Python
> * Better Comment
> * Bracket Pair Colorizer 2
> * Prettify JSON
> * SonarLint
> * Visual Studio IntelliCode
> * Pylance

5. Micropython

* https://micropython.org/
* Firmware: https://micropython.org/download/esp32/ 

6. Micropython lib

* https://github.com/micropython/micropython-lib

7. Micropython async/coro

* https://github.com/peterhinch/micropython-async

8. Micropython Stub

* https://github.com/Josverl/micropython-stubs 
* 按说明配置 VSCode 代码自动完成和检查

9. 产品手册，烧录工具，参考供应商提供的手册

* 零一科技（01Studio）MicroPython开发套件配套资料_2020-8-5

## 2 编译Pyhton源文件

### 2.1 为什么要编译

* 保护源代码
* 减少内存使用
* 提高载入性能

### 2.2 编译方法

#### 2.2.1 单个文件

```bash
python -m mpy_cross my.py -march=xtensawin -X emit=native
```

#### 2.2.2 一组文件

```bash
for f in $( ls *.py ); do python -m mpy_cross $f -march=xtensawin; done
```

#### 2.2.3 上传

编译后的文件可以像源文件一样上传

## 3 开发中的注意事项和经验教训

### 3.1 异步编程问题

* 不要遗忘 `async`, `await` 关键字

> * 异步函数定义头需要用 `async` 关键字修饰
> * 异步函数的调用语需要 `await` 关键子修饰

* 如果某个异步函数内部没有调用任何其他异步函数，建议添加 `await uasync.sleep(0)` 语句，可以避免某些情况下的问题
* 异步锁在 `ESP32` 下的正确使用方式，Lock 不要定义为类成员，使用 `async with lock:`

```python
op_lock = Lock()

class Controller:

    async def op(self, path, command, param):
        async with op_lock:
            return await self.__op(path, command, param)

```

### 3.2 Python 问题

* Python 是弱类型语言，注意数据类型的使用和转换
* Python 的函数可以作为变量传递，注意 `func`, `func()` 是不同的
* IDE 对 Python 的语法支持非常弱：

> * 自动语法检查非常弱，写代码需要更加小心
> * 代码重构支持非常弱，大部分需要手工完成

* 面向对象支持很不严格，使用时需要注意继承关系

> * 支持多重继承，注意不要由冲突的类
> * 没有接口机制，需要定义空函数
> * 成员保护比较差，容易发生冲突
> * 没有类似 `java` `@override` 的机制帮助重载，需要仔细检查，避免冲突
> * 重载的函数，请严格使用一致函数头，如果父类中使用了`async` 修饰，子类必须使用，返回值类型也需要一致。异步函数，
> * 单实例请使用 `utils.singleton`

### 3.3 Micropython 和嵌入系统问题

* Micropython 是 Python 的子集，功能有限，使用特殊功能前请查阅文档
* 嵌入系统内存有限，必须时刻考虑内存使用
* 执行大操作前，调用内存垃圾收集释放更多内存
* 执行大测试后，建议重启系统，然后再上传和测试
* 每次修改库后，需要重启，因为 `python` 不会载入新代码
* `mpfs` 出现死进程，需要插拔 USB 电源重启
* `mpfs` 出现内存问题，可以使用软件重启 `machine.reset()`，如果没法执行软重启，可以插拔 USB 电源重启
