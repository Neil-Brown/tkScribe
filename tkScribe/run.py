import itertools
from tkinter import font

counter = itertools.count(1)
font_params = ["family", "size", "weight", "slant", "underline", "overstrike"]

class Run(font.Font):
    def __init__(self, **kwargs):
        font.Font.__init__(self,
                           name="r{}".format(next(counter)),
                           **{k: v for k, v in kwargs.items()
                                if k in font_params})
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name in font_params:
            self.__setitem__(name, value)

    def __setitem__(self, key, value):
        self.configure(**{key: value})
        if self.__getattribute__(key) != value:
            self.__setattr__(key, value)

    def make_dict(self):
        d = {}
        for op in font_params:
            d[op] = self.__getattribute__(op)
        d["foreground"] = self.__getattribute__("foreground")
        d["background"] = self.__getattribute__("background")
        return d

    def copy(self):
        d = self.make_dict()
        return Run(**d)

    def __eq__(self, other):
        for param in font_params:
            if self.__getattribute__(param) != other.__getattribute__(param):
                return False
            for param in ["foreground", "background"]:
                if self.__getattribute__(param) != other.__getattribute__(
                        param):
                    return False
        return True


