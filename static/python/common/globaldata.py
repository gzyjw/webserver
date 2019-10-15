class globel():
    def __init__(self):
        self.__dict__['author'] = 'gzyjw'

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return item + 'is not exist'