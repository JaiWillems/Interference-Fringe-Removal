"""
"""


class Apodization(object):

    def triangle(self, IS, TS, CB):
        pass

    def cosine(self, IS, TS, CB):
        pass

    def bessel(self, IS, TS, CB):
        pass

class DataOperations(Apodization):

    def __init__(self):
        super().__init__()

    def mertz(self, dataBlock):
        pass

    def FFT(self, dataBlock):
        pass

    def IFFT(self, dataBlock):
        pass
