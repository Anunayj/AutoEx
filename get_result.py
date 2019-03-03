# -*- coding: utf-8 -*-

import randoh
from bs4 import BeautifulSoup
import os
import requests
import time
import opencsv
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import sys, getopt
import solve_with_neurons
import progressbar


executor = ThreadPoolExecutor(max_workers=200)

class probar:
    def __init__(self,maxvalue):
        self.progress = 0
        self.probar = progressbar.ProgressBar(max_value=maxvalue)
    def increment(self):
        self.progress = self.progress + 1
        self.probar.update(self.progress)

class processFile:

    def __init__(self,filename):
        self.firstEntry=True
        self.worksheet=opencsv.opencsv(filename)
        self.tables = {}
        self.numberOfColumns = False
        self.passStudents = 0
        self.totalStudents = 0
    def processResult(self,html,rollSuffix):
        list = []
        soup=BeautifulSoup(html,'html5lib')
        self.totalStudents = self.totalStudents + 1
        name=soup.find('td',text=re.compile("Name")).findNext().text.replace("\n",'').strip()
        roll=soup.find('td',text=re.compile("Roll")).findNext().text.replace("\n",'').strip()
        list.append(roll)
        list.append(name)
        tables=soup.findAll("table")[0].findAll("table")[2].findAll("tr")[6].findAll("table")
        if self.firstEntry is True:
            header=[]
            header.append("Name")
            header.append("Roll Number")
            for tableNumber in range(1,len(tables)):
                header.append(tables[tableNumber].findAll('td')[0].text.replace("\n",'').strip())
            header.append("SGPA")
            header.append("CGPA")
            header.append("Result Decision")
            self.tables[0] = header
            self.firstEntry=False
            self.numberOfColumns = len(header)


        for tableNumber in range(1,len(tables)):
            list.append(tables[tableNumber].findAll('td')[3].text.replace("\n",'').replace("##","*").strip())
        result_des=soup.find("th", text=re.compile(".*CGPA.*")).parent.findNext("td")
        if(result_des.text.replace("\n",'').strip() == "PASS" or result_des.text.replace("\n",'').strip() == "PASS WITH GRACE"):
            self.passStudents = self.passStudents + 1
        SGPA=result_des.findNext("td")
        CGPA=SGPA.findNext("td")
        list.append(SGPA.text.replace("\n",'').strip())
        list.append(CGPA.text.replace("\n",'').strip())
        list.append('"'+result_des.text.replace("\n",'').strip()+'"')
        self.tables[int(rollSuffix)] = list
    def __del__(self):
        list = sorted(self.tables.items())
        if self.numberOfColumns:
            entry = []
            for t in range(self.numberOfColumns-1):
                entry.append("")
            entry.append(str(self.passStudents)+"/"+str(self.totalStudents)+" = "+ "{0:.2f}".format(self.passStudents*100/self.totalStudents) + "%")
            print('Result Downloaded Sucessfully Result Precentage = ' + "{0:.2f}".format(self.passStudents*100/self.totalStudents) + "%")
            list.append((0,entry))
            list.append((1,[]))
            self.worksheet.bulkappend(list)
        else:
            print("No result Found, Check your arguments")

class extract:
    def __init__(self,dept):
        for temp in range(3):
            try:
                #Some randmoness for both seesion Id and file name
                randomness = randoh.randoo()
                header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.','Cookies':'ASP.NET_SessionId='+randomness}
                #initialize session
                self.sess = requests.session()
                self.sess.headers.update(header)
                #get page
                a=self.sess.get('http://result.rgpv.ac.in/Result/ProgramSelect.aspx')

                soup = BeautifulSoup(a.text,'html5lib')
                deptid =  'radlstProgram_'+ str(dept)

                value = soup.find('input',{'id':deptid})['value']
                #post data
                deptid = deptid.replace('_','$')
                viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
                viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
                EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']
                postdata = {'__EVENTTARGET':deptid,'__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'radlstProgram':value}
                resp=self.sess.post('http://result.rgpv.ac.in/Result/ProgramSelect.aspx',data=postdata,allow_redirects=True)
                self.url=resp.url
            except Exception as e:
                print(e)
                continue
            break


    def getResult(self,roll,semester,file,rollSuffix,bar):
        #get session and captcha
        resp=self.sess.get(self.url)
        soup = BeautifulSoup(resp.text,'html5lib')
        imageURL="http://result.rgpv.ac.in/Result/"+soup.findAll('img')[1]['src']
        #randomness = randoh.randoo()
        cap = self.sess.get(imageURL, allow_redirects=True)

        #solve the Captcha
        solution = solve_with_neurons.Solve(cap.content)
        if not solution:
            return(1)
        time.sleep(5)
        viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
        viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
        EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']

        #Post the data
        postdata = {'__EVENTTARGET':'','__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'ctl00$ContentPlaceHolder1$txtrollno':roll,'ctl00$ContentPlaceHolder1$drpSemester':str(semester),'ctl00$ContentPlaceHolder1$rbtnlstSType':'G','ctl00$ContentPlaceHolder1$TextBox1':solution,'ctl00$ContentPlaceHolder1$btnviewresult':'View Result'}
        result=self.sess.post(self.url,data=postdata,allow_redirects=True)

        #process data
        resultFound='<td class="resultheader">'
        notFound='<script language=JavaScript>alert("Result for this Enrollment No. not Found");</script>'
        if resultFound in result.text:
            bar.increment()
            file.processResult(result.text,rollSuffix)
            return(0)
        elif notFound in result.text:
            bar.increment()
            return(0)
        else:
            return(1)
    def driver(self,roll,semester,file,rollSuffix,bar):
        for retryNumber in range(10):
            try:
                while self.getResult(roll,semester,file,rollSuffix,bar) is 1:
                    pass
            except Exception as e:
                print(e)
                continue
            break

    def loop(self,rollPrefix,totalStudents,semester,fileName,x):
        file=processFile(fileName)
        bar = probar(totalStudents)
        for roll in range(1,totalStudents+1):
            executor.submit(self.driver,rollPrefix+str(roll).zfill(x),semester,file,roll,bar)


def main(argv):
  prefixs=''
  total=0
  sem=1
  output='output'
  zfill=2
  try:
      opts, args = getopt.getopt(argv,"d:p:t:f:s:o:z:",["dept=","prefix=","total=","sem=","output=","zfill="])
  except getopt.GetoptError as p:
      print('AutoEx.py -d <DepartmentCode> -p <rollPrefix> -t <totalStudents> -s <semester> -o <fileName> -z <NumberOftrailingZero>')
      sys.exit(2)
  for opt, arg in opts:
    if opt in ("-d", "--dept"):
        dept = arg
    elif opt in ("-p", "--prefix"):
        prefixs = arg
    elif opt in ("-t", "--total"):
        total = arg
    elif opt in ("-s", "--sem"):
        sem = arg
    elif opt in ("-o", "--output"):
        output = arg
    elif opt in ("-z", "--zfill"):
        zfill = arg
    else:
        print('AutoEx.py -d <DepartmentCode> -p <rollPrefix> -t <totalStudents> -s <semester> -o <fileName> -z <NumberOftrailingZero>')
        sys.exit()

    obj=extract(int(dept))
    obj.loop(prefixs,int(total),int(sem),output,int(zfill))


if __name__ == "__main__":
   main(sys.argv[1:])
