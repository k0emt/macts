#!python
# OffenderDataSerial.py
# data formats in OneNote (Web Journal)

__author__ = 'k0emt'

import sys
import datetime
from OffenderData import OffenderData

DATAFILENAME = "mo_offender_fak930_first_200.txt"

class OffenderDataSerial:

    def __init__(self):
        counter = 0
        runStart = datetime.datetime.now()

        print runStart
        print 'Processing: ', DATAFILENAME

        # read through a datafile
        try:
            dataFile = open(DATAFILENAME, 'r')
            try:
                for dataLine in dataFile:
                    counter += 1
                    offenderData = OffenderData(dataLine)

                    # print offenderData.rawDataLine
                    
                    # parse and JSONify the dataLine
                    # offenderData.getJson()
                    # save it to MongoDb -- how long to run w/out doing this part first?

            finally:
                dataFile.close()

        except IOError:
            print"*** AN IO ERROR OCCURRED ***"
            pass

        # report overall run-time
        print counter, ' lines processed.'
        runEnd = datetime.datetime.now()
        print runEnd
        print runEnd - runStart

# run as stand alone program
def main():
    offenderImport = OffenderDataSerial()

main()