import traceback
from subprocess import Popen, PIPE
from threading import Timer
from channel import Channel, add_channel
from errors import *
from .. import config
from config import *
import re
from copy import deepcopy

#############################################################################
# SES cmd output formatter
#############################################################################
VERSION_RE= re.compile(r'(.*Revision|.*Version|.*revision|.*version) *(\d\.\d\.\d)')
BUILD_RE= re.compile(r'(Built r\d+).*(\w{3} \d{2} \d{4} \d{2}:\d{2}:\d{2})')
RE_LIST=[VERSION_RE, BUILD_RE]

def get_dict_2(value):
    dict_list={}
    for kv_line in value.split('\n'):
        if kv_line.count(":") == 1:
            dict_list[kv_line.split(':')[0].strip()] = kv_line.split(':')[1].strip()
        elif kv_line.count("=") == 1:
            dict_list[kv_line.split('=')[0].strip()] = kv_line.split('=')[1].strip()
        elif kv_line !="":
            for RE_COM in RE_LIST:
                match_RE = RE_COM.match(kv_line)
                if match_RE:
                    dict_list[match_RE.group(1).strip()] = match_RE.group(2).strip()

    return dict_list

def get_dict_1(value):
    dict_1line={}
    for kv_line in value.split('\n'):
        if ":" in kv_line:
            dict_1line[kv_line.split(':')[0].strip()]=kv_line.split(':')[1].strip()
    return dict_1line

def get_key_1(value_1):
  dict_list={}
  dict1 = value_1.split('[')
  for dictx in dict1:
    if ']' in dictx :
        sub_key=dictx.split(']')[0]
        sub_value=get_dict_2(dictx.split(']')[1])
        dict_list[sub_key.strip()]=sub_value
    elif ":" in dictx:
        dict_list.update(get_dict_1(dictx))
    elif dictx.strip() != "":
        dict_list.update(dictx)
  return dict_list

def convert2dict(cmd_out):
   dict_list={}
   for key_value in cmd_out.split('--- '):
     try:
        key=key_value.split(' ---')[0]
        value=key_value.split(' ---')[1]
        if "]" in value or ":" in value:
            value_1=get_key_1(value)
        else:
            value_1= value
        dict_list[key]= value_1
     except:
        pass
   return dict_list

def convert2array(cmd_out):
    out_list_o = cmd_out.split('\n')
    out_list = []
    for line in out_list_o:
        if line.count('-')< count_hyphen and len(line)>count_hyphen:
            out_list.append(line)

    colum_index=[]
    for colum_name in filter(lambda a: a != '', out_list[0].split(' ')):
        colum_index.append(out_list[0].index(colum_name))

    response_list=[]
    for line_string in out_list:
        line_x=[]
        i=0
        while True:
            try:
                line_x.append((line_string[colum_index[i]:colum_index[i+1]]).strip())
            except IndexError:
                line_x.append((line_string[colum_index[i]:]).strip())
                break
            i+=1
        response_list.append(line_x)
    return response_list


#############################################################################
# Channel Adapter
#############################################################################

class SASChannelAdapter(Channel):
    def __init__(self):
        
        Channel.__init__(self)
        self.cmd_output=None

    def send(self, device, cmd, hint=None):
        self.openses_cmd=deepcopy(openses_cmd)
        self.openses_cmd.append(device)

        try:
            timeout = hint['timeout']
        except:
            # try to get timeout from hint or get it from config.py
            timeout = time_out
            pass
            
        proc = Popen(self.openses_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        def kill_proc():
            timer.expired = True
            proc.kill()

        timer = Timer(timeout, kill_proc)
        timer.expired = False
        timer.start()
        proc.stdin.write(cmd+'\n')
        proc.stdin.write(ses_quit)
        self.returncode = proc.returncode

        all_data = proc.stdout.read()

        if "ESCE A $ " in all_data:
            ses_prompt = "ESCE A $ "
        elif "ESCE B $ " in all_data:
            ses_prompt = "ESCE B $ "
        else:
            timer.cancel()
            raise DEVNotaccessError('Device %s is not available' % self.openses_cmd[2])

        cmd_out = all_data.split(ses_prompt)[1]

        if timer.expired:
            raise SubprocessTimeoutError('Timeout to execute' % cmd)
        timer.cancel()
        self.returncode = proc.returncode

        if "-"*count_hyphen in all_data:
            self.cmd_output = convert2array(cmd_out)
        elif "--- " in all_data and " ---" in all_data:
            self.cmd_output = convert2dict(cmd_out)

        return self.cmd_output


class MockChannelAdapter(Channel):
    def __init__(self):
        Channel.__init__(self)

    def send(self, cmd, hint=None):
        return "This is debug"
	
#############################################################################
# SES communicator
#############################################################################

def init_channels():
    add_channel("mock", MockChannelAdapter())
    add_channel("sas", SASChannelAdapter())
    #add_channel("serial", SerialChannelAdapter())
