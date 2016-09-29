class Error(Exception):
    def __init__(self, error_type=None, mesg=None):
        self.error_type = error_type
        self.mesg = mesg
        self.trace = None

    def __str__(self):
        return "%s: %s" % (self.error_type, self.mesg)

    def set_trace_message(self, trace):
        self.trace = trace

    def dict(self):
        dictinfo = {"error-type": self.error_type,
                    "message": self.mesg,
                    "trace": self.trace}
        return dictinfo

class CommandLineError(Error):
    def __init__(self, mesg, data=None):
        Error.__init__(self, "CLI-Error", mesg)
        self.data = data

class SubprocessTimeoutError(Error):
    def __init__(self, mesg, data=None):
        Error.__init__(self, "Timeout-Error", mesg)
        self.data = data

class DEVNotaccessError(Error):
    def __init__(self, mesg, data=None):
        Error.__init__(self, "DEV-not-found-Error", mesg)
        self.data = data

class ChannelRuntimeError(Error):
    def __init__(self, mesg=None):
        Error.__init__(self, "Channel-Runtime-Error", mesg)

class SikpHandlerError(Error):
    def __init__(self, mesg=None):
        Error.__init__(self, "SikpHandlerError", mesg)

class InvalidCmdError(Error):
    def __init__(self, mesg=None):
        Error.__init__(self, "Invalid-Command", mesg)

class Status(object):
    def __init__(self, cmd=None):
        self.result = "success"
        self.errors = []

    def append_error(self, err):
        if isinstance(err, Error):
            self.errors.append(err)
            self.result = "fail"
            print self.errors

    def set_success(self):
        self.result = "success"
        self.errors = []

    def set_fail(self):
        self.result = "fail"

    def is_success(self):
        if self.result == "success":
            return True
        else:
            return False

    def is_fail(self):
        if self.result == "fail":
            return True
        else:
            return False

    def dict(self):
        dictinfo = {"result": self.result,
                    "errors": [error.dict() for error in self.errors]}
        return dictinfo
