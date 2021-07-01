from gc import collect, mem_free
config = None

def callback(cfg):
    global config
    config = cfg
    print(cfg)


def setup():
    import MicroSetup
    settings = [
        MicroSetup.Parameter("ssid", "Wifi SSID", MicroSetup.PARAMETER_STRING),
        MicroSetup.Parameter("pw", "Wifi password", MicroSetup.PARAMETER_STRING),
        MicroSetup.Parameter("log_interval", "Log interval", MicroSetup.PARAMETER_INT, min=5000, max=600000),
        MicroSetup.Parameter("led", "Enable LED", MicroSetup.PARAMETER_BOOL),
        MicroSetup.Parameter("floaty", "Float value", MicroSetup.PARAMETER_FLOAT, decimals=2)
    ]
    ms = MicroSetup.MicroSetup(settings, "Test Device", callback, debug=True) # debug=True regnerates the html and config every time
    ms.start_server()
    ms.cleanup() # Clean up starts here
    del MicroSetup
    from sys import modules # Local imports should theoretically lower memory footprint
    del modules["MicroSetup"]


print(mem_free())
setup()
print(mem_free())
collect() # Calling collect is important, even after cleanup
print(mem_free())
print(config["ssid"]) # Get your config parameters as defined in settings