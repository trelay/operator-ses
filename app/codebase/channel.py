#############################################################################
# Channel
#############################################################################
class Channel(object):
    def __init__(self):
        pass

    def send(self, cmd, hint=None):
        raise NotImplementedError("Virtual Method!")

#############################################################################
# Channel Map
#############################################################################

# @todo implement singleton
class ChannelMap(object):
    def __init__(self):
        self.channels = {}

    def get_channel(self, channel_name):
        return self.channels.get(channel_name)

    def add_channel(self, channel_name, channel):
        self.channels[channel_name] = channel

channel_map = ChannelMap()

def get_channel(channel_name):
    return channel_map.get_channel(channel_name)

def add_channel(channel_name, channel):
    channel_map.add_channel(channel_name, channel)

