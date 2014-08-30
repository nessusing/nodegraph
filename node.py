from pprint import pprint
from collections import OrderedDict

from nodegraph.function import generate_id
from nodegraph.channel import Channel
from nodegraph.error import NotUniqueError

class Node(object):
    def __init__(self, name):
        self.__name = name
        self.__id = generate_id()
        self.__channels = OrderedDict()

    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name
    
    def rename(self, name):
        self.__name = name
        
    @property
    def channels(self):
        return self.__channels

    def add_channel(self, channel):
        assert isinstance(channel, Channel), '%s is not Channel type.' % str(channel)
        # Ensure all channels have unqiue names
        self.__channels[channel.name] = channel
        
    def create_channel(self, name, value=None):
        if name in self.__channels:
            raise NotUniqueError('Channel %s already exists in Node %s.' % (name, self.__name))
        ch = Channel(name, self)
        ch.value = value
        self.add_channel(ch)
        return ch
        
    def remove_channel(self, name):
        try:
            del self.__channels[name]
        except KeyError:
            pass
    
    def get_channel(self, name):
        try:
            return self.__channels[name]
        except KeyError:
            print 'Channel %s is not defined in Node %s.' % (name, self.__name)
    
    def __str__(self):
        return self.__name
    
    def __getattr__(self, name):
        return self.get_channel(name)
    
#    def __setattr__(self, name, value):
#        self.create_channel(name, value)
    
    def __delattr__(self, name):
        self.remove_channel(name)
        
    def __contains__(self, item):
        key = None
        if isinstance(item, basestring):
            key = item
        elif isinstance(item, Channel):
            key = item.name
        return key in self.__channels
    
    def serialize(self):
        return {
            'id': self.__id,
            'name': self.__name,
            'channels': [ch.serialize() for ch in self.__channels.itervalues()]
        }
    
    def dump(self):
        pprint(self.serialize())

if __name__ == '__main__':
    node1 = Node('node1')
    node1foo1 = node1.create_channel('foo1', 'foo2')
    node1bar1 = node1.create_channel('bar1', 'bar2')
    
    node1.foo1.add_out_channel(node1.bar1)
#    node1.bar1.add_out_channel(node1.foo1)
    node1.dump()
