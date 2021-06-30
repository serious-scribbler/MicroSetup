# MicroSetup

A wireless setup module for MicroPython

## Screenshots
![ConfigurationPage](https://github.com/serious-scribbler/MicroSetup/raw/main/screenshots/ConfigurationPage.png)

## How to use MicroSetup

The best way to learn how to use MicroSetup is to read `example.py`.

### General use

**DON'T FORGET TO COPY THE `WWW`-DIRECTORY!**

#### Access Point SSID, password and IP address

The access point is named as defined in `device_name` during the initialization of the MicroSetup object.
**Password**: `setupnow`

**IP**: `192.168.4.1`

Connect your Wifi compatible device with the access point and enter the IP address into your browser to change the configuration.

#### Create configuration parameters

MicroSetup uses the Parameter object to store parameters and constraints.

Parameter accepts the following arguments:

- **param_name**: The value for each parameter is loaded into a dict with this value as it's key

- **display_name**: This is the name of the parameter that is shown on the configuration web page

- **param_type**: The data type of your parameter. Default is `MicroSetup.PARAMETER_STRING` additional supported values are:
  
  - `MicroSetup.PARAMETER_FLOAT`
  
  - `MicroSetup.PARAMETER_INT`
  
  - `MicroSetup.PARAMETER_BOOL`

- **decimals**: The number of decimals for float types default: 0

- **min**: The lowest allowed value for int and float types

- **max**: The highest

Put all your configuration parametes into a list. This list is later passed to MicroSetup.



#### Using the MicroSetup object

Import MicroSetup locally if possible.

Create an instance of MicroSetup using the follwoing parameters:

- **device_settings**: A list of parameters, as described in the previous section

- **device_name**: This name is used as the *SSID* of the device

- **callback**: A function that accepts 1 parameter (a dict with all your settings).
  
  This function is called after the settings where loaded.

- **debug**: Set debug to `True` to regenerate the HTML files and ignore and overwrite the stored settings. This can be used during development or to *reset* the devices configuration.

Your settings.cfg file will be loaded automatically if it is present duriong initialization.



##### Adding a custom validator for your configuration

You can validate the configuration before it is stored by setting a validator.

Assuming your instance of MicroSetup is called *ms* you can set your validator function using `ms.validator = function_name` before you start the server.

You validator has to accept a dict as an argument (this will contain the configuration for you to validate) and **return** `True` when the validation was successfull or `False` when the validation failed.

The server is shutdown during validation, so you can freely use wifi during your validation, as long as you disable it after your use.



#### Starting the server

Assuming your MicroSetup object is called `ms` call `ms.start_server()`, this call is blocking.

**I strongly advice to follow the section about memory efficiency or you will run yourself out of memory very easily!**



### Best practices for memory efficiency

Only import MicroSetup locally if possible and run `gc.collect()` when it isn't in use anymore. Take a look at `example.py` for an efficient example.

 Call the following after MicroSetup.start_server():

```python
# ms would be your MicroSetup object
ms.cleanup()
del MicroSetup
from sys import modules
del modules["MicroSetup"]
# Call the following in a different scope where the import of MicroSetup isn't used
gc.collect() # Use example.py to learn where to put this
```

MicroSetup only requires a lot of memory (about 25-30KB) when it generates a new config file. **Reading an existing configuration only uses 4-6KB of RAM.**

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
