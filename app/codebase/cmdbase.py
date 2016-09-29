import traceback
from errors import *
class CmdHandler(object):
    def __init__(self, successor=None, cmd=None):
        self.successor = successor
        self.cmd = cmd
        if successor is None and cmd is None:
            raise ValueError("No successor or cmd is set.")

    def handler(self):
        if self.successor is not None:
            self.successor.handler()

    def get_cmd(self):
        if self.cmd is not None:
            return self.cmd
        else:
            return self.successor.get_cmd()

class NoneHandler(CmdHandler):
    def __init__(self, cmd):
        CmdHandler.__init__(self, cmd=cmd)

class ChannelHandler(CmdHandler):
    def __init__(self, successor=None):
        CmdHandler.__init__(self, successor)

    def handler(self):
        # Do not call this function directly,
        # It doesn't have error handler here
        # Call this from class Cmd defined below instead
        cmd = self.get_cmd()
        if cmd.status.is_fail():
            raise SikpHandlerError("Skip ChannelHandler")

        cmd.data = cmd.channel.send(cmd.device, cmd.command, cmd.hints)
        if self.successor is not None:
            self.successor.handler()

class Cmd(object):
    def __init__(self, channel=None, request=None):
        self.request = request
        self.command = None
        self.hints = {}
        self.channel = channel
        self.handler = None
        self.status = Status()
        self.data = None

    def __str__(self):
        return str(self.cmd)

    def run(self):
        try:
            self.handler.handler()
        except Error, err:
            formatted_lines = traceback.format_exc().splitlines()
            err.set_trace_message(formatted_lines)
            self.status.append_error(err)
        except Exception, err:
            print "error: %s" % (err)
            formatted_lines = traceback.format_exc().splitlines()
            error = ChannelRuntimeError(mesg=str(err))
            error.set_trace_message(formatted_lines)
            self.status.append_error(error)
        return {"response": self.data, "status": self.status.dict()}

