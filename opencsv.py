import os
class opencsv:
    def __init__(self):
        #self.file = open(filename+".csv","a+")
        self.file = ''

    def append(self,data):
        for entry in data:
            self.file = self.file + entry

            if entry is data[-1]:
                self.file = self.file + "\n"
            else:
                self.file = self.file+ ","

    def bulkappend(self,listoflists):
        for roll, lists in listoflists:
            self.append(lists)

    def getcsv(self):
        return self.file
