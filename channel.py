from pprint import pprint
from collections import OrderedDict

from nodegraph.function import generate_id
from nodegraph.error import NotUniqueError, CircularGraphError


class ChannelValue(object):
    
    def __init__(self, value=None):
        self.__value = value
        
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        self.__value = value
    
    def serialize(self):
        return self.__value
    
class Channel(object):
    
    def __init__(self, name, node):
        """
        name: Name of this channel
        node: Node that this channel belongs to
        """
        self.__name = name
        self.__node = node
        self.__id = generate_id()
        self.__value = ChannelValue()
        self.__in_channel = None
        self.__out_channels = OrderedDict()
        self.__in_value = None

    @property
    def id(self):
        return self.__id
    
    @property
    def node(self):
        return self.__node
        
    @property
    def name(self):
        return self.__name
    
    def rename(self, name):
        if self.__name != name:
            if name in self.__node:
                raise KeyError('Cannot rename %s to %s because it already exists Node %s.' % (
                        self.__name,
                        name,
                        self.__node.name
                        ))
            self.__name = name

    @property
    def value(self):
        return self.__value.serialize()
    
    @value.setter
    def value(self, value):
        if isinstance(value, ChannelValue):
            self.__value = value
        else:
            self.__value = ChannelValue(value=value)
    
    @property
    def in_channel(self):
        return self.__in_channel
    
    @in_channel.setter
    def in_channel(self, channel):
        assert channel != self, 'Channel %s: Cannot add self to in stream channel.' % self.__name
        assert isinstance(channel, Channel), '%s is not Channel type.' % str(channel)
        if self.__in_channel != channel:
            self.__in_channel = channel
            channel.add_out_channel(self)
            self.walk_up_along_in_channels()
        
    def remove_in_channel(self):
        self.__in_channel = None

    @property
    def out_channels(self):
        return self.__out_channels
    
    def add_out_channel(self, channel):
        assert channel != self, 'Channel %s: Cannot add self to out stream channels.' % self.__name
        # Using name to ensure uniqueness is not sufficient here, because multiple nodes with same
        # channel names may be added to out streams. Only id is truly unique.
        self.__out_channels[channel.id] = channel
        channel.in_channel = self
        self.walk_up_along_in_channels()
    
    def delete_out_channel(self, channel):
        for id in self.__out_channels:
            if id == channel.id:
                del self.__out_channels[id]
                break

    def walk_up_along_in_channels(self, _channels=None):
        """
        _channels: Private argument. Do not use publicly.
        """
        if _channels is None:
            _channels = []

        up = self.__in_channel       
        if up:
            if up in _channels:
                chain = [ch.name for ch in _channels]
                chain.append(up.name)
                chain = '->'.join(chain)
                raise CircularGraphError('Circular reference found: %s' % chain)

            _channels.append(up)
            up.walk_up_along_in_channels(_channels)

        return _channels
    
    def __str__(self):
        return self.__name

    def connect_to(self, channel):
        channel.in_channel = self
        
    def connect_from(self, channel):
        self.in_channel = channel
    
    def serialize(self, _root=True):
        """
        _root: Private argument. Do not use publicly.
        """
        
        s = {
            'id': self.__id,
            'name': self.__name,
            'value': self.__value.serialize()
        }
        
        if self.__in_channel and _root:
            s['in_channel'] = self.__in_channel.serialize(_root=False)
        
        if self.__out_channels:
            s['out_channels'] = [ch.serialize(_root=False) for ch in self.__out_channels.itervalues()]
        
        return s
    
    def dump(self):
        pprint(self.serialize())
