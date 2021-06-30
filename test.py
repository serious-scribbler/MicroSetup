import MicroSetup

print("Main")

settings = []
settings.append(MicroSetup.Parameter("ssid", "Wifi SSID", MicroSetup.PARAMETER_STRING))
settings.append(MicroSetup.Parameter("pw", "Wifi password", MicroSetup.PARAMETER_STRING))
settings.append(MicroSetup.Parameter("log_interval", "Log interval", MicroSetup.PARAMETER_INT, min=5000, max=600000))
settings.append(MicroSetup.Parameter("led", "Enable LED", MicroSetup.PARAMETER_BOOL))
settings.append(MicroSetup.Parameter("floaty", "Float", MicroSetup.PARAMETER_FLOAT, decimals=2))

def callback(settings):
    print(settings)

ms = MicroSetup.MicroSetup(settings, "Test Device", callback, debug=True)

print("Starting server")
ms.start_server()
print("Done")