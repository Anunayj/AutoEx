import get_result
import threading
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=25)

class driver:
    def __init__(self,fileName,deptID):
        self.file=get_result.processFile(fileName)
        self.dict=get_result.grabSession(deptID)
    def result(self,roll,semester):
        for retryNumber in range(10):
            try:
                while get_result.getResult(self.dict['session'],self.dict['response'].url,roll,semester,self.file) is 1:
                    pass
            except Exception as e:
                print(e)
                continue
            break


def loop(rollPrefix,rollLast,semester):
    for roll in range(1,rollLast+1):
        print(rollPrefix+str(roll).zfill(3))
        executor.submit(steering.result,rollPrefix+str(roll).zfill(3),semester)

steering=driver("SIRTS_Civil",0)
loop("0186CE151",120,7)
