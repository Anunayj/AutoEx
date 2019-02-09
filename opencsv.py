import os
class opencsv:
    def __init__(self,filename):
        self.file = open(filename+".csv","a+")

    def append(self,data):
        for entry in data:
            self.file.write(entry)
            if entry is data[-1]:
                self.file.write("\n")
            else:
                self.file.write(",")
                
    def close(self):
        self.file.close()
