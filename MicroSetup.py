import os
import ujson
import network
from microWebSrv import MicroWebSrv

PARAMETER_FLOAT = 1
PARAMETER_INT = 2
PARAMETER_STRING = 3
PARAMETER_BOOL = 4

_body = """\
    
"""

_form = """\

"""

_error_body = """\

"""

_number_iput = """\

"""

_string_input = """\
"""

_bool_input = """\
    
"""

class Parameter():
    param_type: int
    param_name: str
    decimals: int
    display_name: str = "Parameter"

    def __init__(self, param_name: str, display_name: str, param_type:int=PARAMETER_STRING, decimals:int=2, min=None, max=None):
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
    settings: list
    validator = None
    callback = None
    cfg = None
    mws = None
    error_message = "Validation failed!"
    validation_error = False

    def __init__(self, settings: list, device_name:str):
        self.device_name = device_name
        self.settings = settings
        self.validator = self._none_validator
        self.callback = self._none_callback

        if os.isfile("settings.cfg"):
            self._load_settings()
        else:
            self._generate_form()
            self._setup_and_start_server()


    def _generate_form(self):
        formdata = ""
        for p in self.settings:
            if isinstance(p, Parameter):
                if p.param_type == PARAMETER_STRING:
                    pass
                elif p.param_type == PARAMETER_BOOL:
                    pass
                elif p.param_type == PARAMETER_INT:
                    pass
                elif p.param_type == PARAMETER_FLOAT:
                    pass

        self.form = _form % formdata

    @MicroWebSrv.route("/")
    def index(self, httpClient, httpResponse):
        content =" Internal Server Error"
        if self.validation_error:
            error = _error_body % MicroWebSrv.HTMLEscape(self.error_message)
            content = _body % (MicroWebSrv.HTMLEscape(self.device_name + " Setup"), error)
        else:
            content = _body % (MicroWebSrv.HTMLEscape(self.device_name + " Setup"), self.form)
        
        httpResponse.WriteResponseOk(headers = None,
            contentType = "text/html",
            contentCharset = "UTF-8",
            content = content
        )


    @MicroWebSrv.route("/setup", "POST")
    def _setup_handler(self, httpClient, httpResponse):
        formData = httpClient.ReadRequestPostedFormData()
        # TODO: handle

        if self.validator(cfg):
            self.callback(cfg)
        else:
            self.validation_error = True
            self._setup_and_start_server()


    def _load_settings(self):
        with open("settings.cfg") as f:
            cfg = ujson.load(f)
        self.callback(cfg)


    def _write_settings(self):
        with open("settings.cfg", "w") as f:
            ujson.dump(self.cfg, f)


    def _setup_and_start_server(self):
        self.wifi = network.WLAN(network.AP_IF)
        self.wifi.active(True)
        self.wifi.config(essid=self.device_name, password="setup")
        self.mws = MicroWebSrv(webPath="/www/")
        self.mws.start(threaded=False)


    def _stop_server(self):
        self.mws.stop()
        self.wifi.active(False)

    
    # This is the default validator for settings
    def _none_validator(self, config):
        return True


    # This is called when the settings where successfully loaded
    def _none_callback(self, settings):
        pass