import get_result
import csv
import time

while True:
    file = open("transfer.csv",'r+')
    csv_reader = csv.reader(file, delimiter=',')
    for row in csv_reader:
        print(row[1])
        k = get_result.extract(int(row[0]))
        k.loop(row[1],int(row[2]),int(row[3]),row[4])
        del k
    file.truncate(0)
    time.sleep(10)
