


class Connection(object):
    
    def __init__(self, source, destination):
        self.__source = source
        self.__destination = destination

    @property
    def source(self):
        return self.__source
    
    @property
    def destination(self):
        return self.__destination
    
    
    