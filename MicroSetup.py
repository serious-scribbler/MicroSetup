from uos import listdir
from time import sleep
from gc import collect, mem_free

PARAMETER_FLOAT = 1
PARAMETER_INT = 2
PARAMETER_STRING = 3
PARAMETER_BOOL = 4

_body_start = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/purecss/base-min.css">
    <link rel="stylesheet" href="/purecss/pure-min.css">
	<link rel="stylesheet" href="/purecss/grids-responsive-min.css">
    <link rel="stylesheet" href="/purecss/forms-min.css">
    <link rel="stylesheet" href="/purecss/buttons-min.css">
    <link rel="stylesheet" href="/style.css">
    <title>Device Setup</title>
</head>
<body>
    <div class="pure-g">
        <div class="pure-u-1">
            <div class="pure-menu menu">
                <a href="#" class="pure-menu-heading logo">Device Setup</a>
            </div>
        </div>
        <div class="pure-u-1">
            <div class="pure-g content-wrapper">
"""
_body_end = """\
            </div>
        </div>
        
        <div class="footer pure-u-1">
            Powered by <a href="https://github.com/serious-scribbler/MicroSetup">MicroSetup</a>
        </div>
    </div>
</body>
</html> 
"""

_form_start = """\
<div class="pure-u-1">
<form action="/setup" method="post" class="pure-form pure-form-stacked">
<fieldset>
"""
_form_end = """\
<button type="submit" class="pure-button submit">Submit</button>
</fieldset>
</form>
</div>
"""

_error_body = """\
<h1 style="color: red;">{msg} - <u>Reload this page to correct the setup</u></h1>
"""

_number_input = """\
<label for="{param_name}">{label}</label>
<input type="number" name="{param_name}" id="{param_name}" min="{min}" max="{max}" step="{step}"/>
"""

_string_input = """\
<label for="{param_name}">{label}</label>
<input type="text" name="{param_name}" id="{param_name}" />
"""

_bool_input = """\
<label for="{param_name}">{label}</label>
<input type="checkbox" name="{param_name}" id="{param_name}" /><br>
"""

_validation_in_progress = """\
<h1>
Setup in progress. This devices access point is unavailable during setup.<br>
This access point will restart if your provided configuration is invalid.
</h1>
"""


class Parameter():
    param_type: int
    param_name: str
    decimals: int
    display_name: str = "Parameter"

    def __init__(self, param_name: str, display_name: str, param_type:int=PARAMETER_STRING, decimals:int=0, min=0, max=100):
        self.param_name = param_name
        self.param_type = param_type
        self.decimals = decimals
        self.min = min
        self.max = max
        self.display_name = display_name

class MicroSetup():

    wifi = None
    device_name = "MicroPython Device"
    settings = {}
    validator = None
    callback = None
    cfg = {}
    mws = None
    error_message = "Validation failed!"
    validation_error = False
    done = False

    def __init__(self, device_settings: list, device_name:str, callback, debug=False):
        self.device_name = device_name
        self.validator = self._none_validator
        self.callback = callback

        for p in device_settings:
            if isinstance(p, Parameter):
                self.settings[p.param_name] = p
            else:
                raise AttributeError("Invalid device_settings list, list entry is not an instance of Parameter!")
        if "settings.cfg" in listdir(".") and not debug:
            self._load_settings()
        else:
            global MicroWebSrv
            from microWebSrv import MicroWebSrv
            if "form.htm" not in listdir("www") or debug:
                self._generate_body()


    def _generate_body(self):
        print("Generating form.htm")
        with open("www/form.htm", "w") as f:
            f.write(_body_start)
            f.write(_form_start)
            for key in self.settings:
                p = self.settings[key]
                if p.param_type == PARAMETER_STRING:
                    f.write(_string_input.format(param_name=p.param_name, label=MicroWebSrv.HTMLEscape(p.display_name)) + "\n")
                elif p.param_type == PARAMETER_BOOL:
                    f.write(_bool_input.format(param_name=p.param_name, label=MicroWebSrv.HTMLEscape(p.display_name)) + "\n")
                else:
                    step = ""
                    if p.decimals == 0:
                        step = 1
                    else:
                        step = "0."
                        for i in range(p.decimals-1):
                            step += "0"
                        step += "1"
                    f.write(_number_input.format(param_name=p.param_name, label=MicroWebSrv.HTMLEscape(p.display_name), min=p.min, max=p.max, step=step) + "\n")
            f.write(_form_end)
            f.write(_body_end)


    def index(self, httpClient, httpResponse, routeArgs=None):
        if self.validation_error:
            content = _error_body.format(msg=MicroWebSrv.HTMLEscape(self.error_message))
            self.validation_error = False
            self.cfg = {}
            httpResponse.WriteResponseOk(headers = None,
            contentType = "text/html",
            contentCharset = "UTF-8",
            content = content
            )
        else:
            httpResponse.WriteResponseFile("www/form.htm", contentType="text/html")
        

    def _setup_handler(self, httpClient, httpResponse, routeArgs=None):
        formData = httpClient.ReadRequestPostedFormData()
        if not self._internal_validator(formData):
            self.validation_error = True
            httpResponse.WriteResponseRedirect("/")
            return
        content = _validation_in_progress
        httpResponse.WriteResponseOk(headers = None,
            contentType = "text/html",
            contentCharset = "UTF-8",
            content = content
        )
        sleep(1)
        self._stop_server()
        if self.validator(self.cfg):
            self._write_settings()
            self.callback(self.cfg)
            self.done = True
        else:
            self.error_message = "Validation failure"
            self.validation_error = True
            self.start_server()


    def _load_settings(self):
        import ujson
        with open("settings.cfg") as f:
            self.cfg = ujson.load(f)
        self.callback(self.cfg)
        self.done = True


    def _write_settings(self):
        import ujson
        with open("settings.cfg", "w") as f:
            ujson.dump(self.cfg, f)


    def start_server(self):
        if self.done:
            return
        import network
        self.wifi = network.WLAN(network.AP_IF)
        self.wifi.active(True)
        self.wifi.config(essid=self.device_name, password="setupnow")
        route_handlers = [
            ("/", "GET", self.index),
            ("/setup", "POST", self._setup_handler)
        ]

        self.mws = MicroWebSrv(routeHandlers=route_handlers, webPath="/www/")
        print("Starting MicroSetup server, wifi password: setupnow")
        self.mws.Start(threaded=False)


    def _stop_server(self):
        self.mws.Stop()
        self.wifi.active(False)


    def _internal_validator(self, data):
        for key in self.settings:
            if key not in data:
                self.error_message = "Missing setting: " + self.settings[key].display_name
                return False
            else:
                setting = self.settings[key]
                if setting.param_type == PARAMETER_STRING:
                    if data[key] != "":
                        self.cfg[key] = data[key]
                    else:
                        self.error_message = "Invalid settings: " + setting.display_name
                        return False
                elif setting.param_type == PARAMETER_INT:
                    try:
                        int(data[key])
                    except:
                        self.error_message = "Invalid settings: " + setting.display_name
                        return False
                    else:
                        val = int(data[key])
                        if self._validate_number(val, setting.min, setting.max):
                            self.cfg[key] = val
                        else:
                            self.error_message = "Setting out of bounds: " + setting.display_name
                            return False
                elif setting.param_type == PARAMETER_FLOAT:
                    try:
                        float(data[key])
                    except:
                        self.error_message = "Invalid settings: " + setting.display_name
                        return False
                    else:
                        val = float(data[key])
                        if self._validate_number(val, setting.min, setting.max):
                            self.cfg[key] = val
                        else:
                            self.error_message = "Setting out of bounds: " + setting.display_name
                            return False
                else:
                    try:
                        bool(data[key])
                    except:
                        self.error_message = "Invalid settings: " + setting.display_name
                        return False
                    else:
                        self.cfg[key] = bool(data[key])
        return True


    def _validate_number(self, number, min, max):
        if number < min or number > max:
            return False
        else:
            return True


    # This is the default validator for settings
    def _none_validator(self, config):
        return True
