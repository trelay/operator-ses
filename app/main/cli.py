from . import main
from .. import codebase
from flask import request, abort

import re
import json


class SESErrorHandler(codebase.CmdHandler):
    def __init__(self, successor=None):
        codebase.CmdHandler.__init__(self, successor)
        self.re_completion_code = re.compile(
                "Unable to send RAW command \(.*rsp=(0x[0-9a-f]+)\)")
        self.re_invalid_request = re.compile("Given data .* is invalid.")

    def handler(self):
        cmd = self.get_cmd()
        output = cmd.data
        match_completion_code = self.re_completion_code.match(output)
        match_invalid_request = self.re_invalid_request.match(output)
        cmd.data = []
        cc = None
        if match_completion_code:
            cc = int(match_completion_code.group(1), 16)
            cmd.data.append(cc)
            raise codebase.IpmiInvalidCCError(cc)
        elif match_invalid_request:
            raise codebase.IpmiInvalidRequestError(match_invalid_request.group(0))
        elif cmd.status.is_success():
            cc = 0
            cmd.data.append(cc)
        if cc == 0 and self.successor is not None:
            self.successor.handler()

class SESDataHandler(codebase.CmdHandler):
    def __init__(self, successor=None):
        codebase.CmdHandler.__init__(self, successor)
        
    def handler(self):
        cmd = self.get_cmd()
        output_lines = cmd.rawdata.split('\n')
        output_lines = [ l for l in output_lines
                if not l.startswith('Close Session command failed') ]
        output = ''.join(output_lines).replace('\r','').strip()
        print output
        if len(output):
            for x in output.split(' '):
                print "x: %s" % (x)
                cmd.data.append(int(x, 16))
        if self.successor is not None:
            self.successor.handler()


class SES_CLI(codebase.Cmd):
    def __init__(self, channel, device, request):
        codebase.Cmd.__init__(self, channel, request)

        self.device = device

        if request.get("command") == None or not request.get("command").strip():
            command = None
        else:
            command = request.get("command")

        if request.get("Sub_cmd") == None or not request.get("Sub_cmd").strip():
            Sub_cmd = None
        else:
            Sub_cmd = request.get("Sub_cmd")

        if request.get("Option") == None or not request.get("Option").strip():
            Option = None
        else:
            Option = request.get("Option")

        if request.get("Parameter") == None or not request.get("Parameter").strip():
            Parameter = None
        else:
            Parameter = request.get("Parameter")

        # Build Command
        if command != None and Sub_cmd != None:
            command_list=[]
            command_list.append(command)
            command_list.append(Sub_cmd)
            if Option != None:
                command_list.append(Option)
            if Parameter != None:
                command_list.append(Parameter)
        self.command = " ".join(command_list)

        # Set handler
        #FIXME: Add return formatter or error handler
        self.handler = codebase.ChannelHandler(codebase.NoneHandler(self))

def run_cli_command(channel, dev_name, request):
    cmd = SES_CLI(channel, dev_name, request)
    res = cmd.run()
    return res

@main.route("/test-operator-ses/<channel_name>/<dev_name>/cli", methods=["POST"])
def raw_resource(channel_name, dev_name):
    device = dev_name.replace('.','/')
    print "*"*40
    print request.json
    print "*"*40

    if not request.is_json:
        print "request: %s" % (request.json)
        abort(400)
    channel = codebase.get_channel(channel_name)
    res = run_cli_command(channel, device, request.json)
    return json.dumps(res)
