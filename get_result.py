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


executor = ThreadPoolExecutor(max_workers=200)


class processFile:

    def __init__(self,filename,email,rollPrefix):
        self.firstEntry=True
        self.worksheet=opencsv.opencsv(filename,email,rollPrefix)
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
            print('\nResult Downloaded Sucessfully, Result Precentage = ' + "{0:.2f}".format(self.passStudents*100/self.totalStudents) + "%")
            list.append((0,entry))
            list.append((1,[]))
            self.worksheet.bulkappend(list)
        else:
            self.worksheet.isEmpty = True
            print("\nNo result Found, Check your arguments")

class extract:
    def __init__(self,dept):
        for temp in range(3):
            try:
                #Some randmoness for both seesion Id and file name
                self.randomness = randoh.randoo()
                header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.','Cookies':'ASP.NET_SessionId='+self.randomness}
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


    def getResult(self,roll,semester,file,rollSuffix):
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
            file.processResult(result.text,rollSuffix)
            return(0)
        elif notFound in result.text:
            return(0)
        else:
            return(1)
    def driver(self,roll,semester,file,rollSuffix):
        for retryNumber in range(10):
            try:
                while self.getResult(roll,semester,file,rollSuffix) is 1:
                    pass

            except Exception as e:
                print(e)
                continue
            break

    def loop(self,rollPrefix,totalStudents,semester,email):
        #Validation and auto zfill

        if len(rollPrefix) == 10:
            x = 2
        elif len(rollPrefix) == 9:
            x = 3
        else:
            print("Roll prefix must be 10 or 9 character long")
            sys.exit()
        if x == 2 and totalStudents > 99:
            print("Are you really sure you have that many students, unbelievable ")
            sys.exit()
        if semester < 1 or semester > 8:
            print("Really, How many semester do you think you have?")
            sys.exit()
        filename = self.randomness + '.csv'
        file=processFile(filename,email,rollPrefix)
        for roll in range(1,totalStudents+1):
            executor.submit(self.driver,rollPrefix+str(roll).zfill(x),semester,file,roll)
