import gc
gc.collect()
print(gc.mem_free())
from microWebSrv import MicroWebSrv
import ujson
import network
from os import ispath

PARAMETER_FLOAT = 1
PARAMETER_INT = 2
PARAMETER_STRING = 3
PARAMETER_BOOL = 4

_body = """\
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
    <title>{device_name} Setup</title>
</head>
<body>
    <div class="pure-g">
        <div class="pure-u-1">
            <div class="pure-menu menu">
                <a href="#" class="pure-menu-heading logo">{device_name} Setup</a>
            </div>
        </div>
        <div class="pure-u-1">
            <div class="pure-g content-wrapper">
                {content}
            </div>
        </div>
        
        <div class="footer pure-u-1">
            Powered by <a href="https://github.com/serious-scribbler/MicroSetup">MicroSetup</a>
        </div>
    </div>
</body>
</html> 
"""

_form = """\
<div class="pure-u-1">
<form action="/setup" method="post" class="pure-form pure-form-stacked">
<fieldset>
{formcontent}
<button type="submit" class="pure-button submit">Submit</button>
</fieldset>
</form>
</div>
"""

_error_body = """\
<div class="pure-u-1 error">
{msg}
</div>
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
<div class="pure-u-1 info">
Setup in progress. This devices access point is unavailable during setup.<br>
This access point will restart if your provided configuration is invalid.
</div>
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
    form:str = ""
    settings = {}
    validator = None
    callback = None
    cfg = {}
    mws = None
    error_message = "Validation failed!"
    validation_error = False

    def __init__(self, device_settings: list, device_name:str):
        self.device_name = device_name
        self.validator = self._none_validator
        self.callback = self._none_callback

        for p in device_settings:
            if isinstance(p, Parameter):
                self.settings[p.param_name] = p
            else:
                raise AttributeError("Invalid device_settings list, list entry is not an instance of Parameter!")

        if os.isfile("settings.cfg"):
            self._load_settings()
        else:
            self._generate_form()


    def _generate_form(self):
        formdata = ""
        for key in self.settings:
            p = self.settings[key]
            if p.param_type == PARAMETER_STRING:
                formdata += _string_input.format(param_name=p.param_name, label=p.display_name) + "\n"
            elif p.param_type == PARAMETER_BOOL:
                formdata += _bool_input.format(param_name=p.param_name, label=p.display_name) + "\n"
            else:
                step = ""
                if p.decimals == 0:
                    step = 1
                else:
                    step = "0."
                    for i in range(p.decimals-1):
                        step += "0"
                    step += 1
                formdata += _number_input.format(param_name=p.param_name, label=p.display_name, min=p.min, max=p.max, step=step) + "\n"

        self.form = _form.format(formcontent=formdata)

    @MicroWebSrv.route("/")
    def index(self, httpClient, httpResponse):
        content =" Internal Server Error"
        if self.validation_error:
            error = _error_body.format(msg=MicroWebSrv.HTMLEscape(self.error_message))
            content = _body.format(device_name=MicroWebSrv.HTMLEscape(self.device_name), content=error+"\n"+self.form)
        else:
            content = _body,format(device_name=MicroWebSrv.HTMLEscape(self.device_name), content=self.form)
        
        httpResponse.WriteResponseOk(headers = None,
            contentType = "text/html",
            contentCharset = "UTF-8",
            content = content
        )


    @MicroWebSrv.route("/setup", "POST")
    def _setup_handler(self, httpClient, httpResponse):
        formData = httpClient.ReadRequestPostedFormData()
        if not self._internal_validator(formData):
            error = _error_body.format(msg=MicroWebSrv.HTMLEscape(self.error_message))
            content = _body.format(device_name=MicroWebSrv.HTMLEscape(self.device_name), content=error+"\n"+self.form)

            httpResponse.WriteResponseOk(headers = None,
            contentType = "text/html",
            contentCharset = "UTF-8",
            content = content
            )
            return
        content = _body.format(device_name=MicroWebSrv.HTMLEscape(self.device_name), content=_validation_in_progress)
        self._stop_server()
        if self.validator(self.cfg):
            self._write_settings()
            self.callback(self.cfg)
        else:
            self.validation_error = True
            self.start_server()


    def _load_settings(self):
        with open("settings.cfg") as f:
            cfg = ujson.load(f)
        self.callback(cfg)


    def _write_settings(self):
        with open("settings.cfg", "w") as f:
            ujson.dump(self.cfg, f)


    def start_server(self):
        self.wifi = network.WLAN(network.AP_IF)
        self.wifi.active(True)
        self.wifi.config(essid=self.device_name, password="setup")
        self.mws = MicroWebSrv(webPath="/www/")
        self.mws.start(threaded=False)


    def _stop_server(self):
        self.mws.stop()
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
                        if self.validate_number(val, setting.min, setting.max):
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
                        if self.validate_number(val, setting.min, setting.max):
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


    # This is called when the settings where successfully loaded
    def _none_callback(self, settings):
        pass