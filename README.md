# MicroSetup

A wireless setup module for MicroPython



## How to use MicroSetup

### General use

This section has not been written yet

### Best practices for memory efficiency

Only import MicroSetup locally if possible and run `gc.collect()` when it isn't in use anymore. MicroSetup only requires a lot of memory when it generates a new config file. Reading an existing configuration only uses 2-4KB of RAM.



## How to install MicroSetup on the ESP8266

### Step 1: Precompile the module and it's dependency

*(You can skip this part if you downloaded the precompiled libraries)*


1. Install mpy-cross if you don't have it already:
   
   `pip install mpy-cross`
   
   *You might need to use `pip3` in replacement of `pip` depending on your operating system.*

2. Clone this repository and cd into it's directory:
   
   `git clone https://github.com/serious-scribbler/MicroSetup.git; cd MicroSetup`

3. Compile the included version of MicroWebSrv and MicroSetup:
   
   *Note that MicroSetup uses a modified version of MicroWebSrv, the original version is incompatible to MicroSetup on ESP8266*
   
   ```shell
   python -m mpy_cross -march=xtensa MicroSetup.py
   
   python -m mpy_cross -march=xtensa microWebSrv.py
   ```
   
   If you are not using Windows, replace `python`with `python3`



### Step 2: Copy the module to your ESP

Copy `MicroSetup.mpy`, `microWebSrv.mpy`  and the `www/`-directory and it's contents to your ESP with your tool of choice.



I use ampy for this purpose:

```shell
ampy -p <port> put MicroSetup.mpy
ampy -p <port> put microWebSrv.mpy
ampy -p <port> put www/
```

**Do not forget the www folder, it is very important!**



### Step 3: Ready to use

You can now use MicroSetup like you would use any other module



## MicroSetup on other devices

MicroSetup has only been tested on ESP8266, other devices might be compatible.



### ESP32

MicroSetup should be compatible to ESP32, I will test this as soon as possible. I would expect the performance to be quite a bit better than on the ESP8266



## Credits

MicroSetup is built on a customized version of [MicroWebSrv](https://github.com/jczic/MicroWebSrv) by [jczic (Jean-Christophe Bos)](https://github.com/jczic) licensed under the MIT License (included as MicroWebSrv LICENSE.md)

I removed `_threading` from MicroWebSrv, modified `_serverProcess()` and `Stop()` and added better Exception handling to `WriteResponseFile`for debugging purposes.
