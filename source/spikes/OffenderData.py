__author__ = 'k0emt'

class OffenderData:

    def __init__(self,rawDataLine=None):
        self.rawDataLine = rawDataLine
        self.lastName = rawDataLine[8:26].strip()
        self.firstName = rawDataLine[26:39].strip()

    def rawData(self):
        return self.rawDataLine
