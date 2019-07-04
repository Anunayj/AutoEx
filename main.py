#!/usr/bin/env3 pyhton
# -*- coding: utf-8 -*-
import requests
import random
import string
from bs4 import BeautifulSoup
import os
import solve_with_neurons
import opencsv
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import re
import threading
#executor = ThreadPoolExecutor(max_workers=200)


class probar:
    def __init__(self):
        self.lock = threading.Lock()
        self.progress = 0
    def increment(self):
        with self.lock:
            self.progress = self.progress + 1



def randomString():
    #24 character random string for cookie
    randoh = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(24)])
    return(randoh)


class resultProcessor:

    def __init__(self, department, semester, maxroll, rollPrefix):

        #save all args as class variables
        self.lock = threading.Lock()
        self.progress = probar()
        self.department = department
        self.fail = False # Tracks if Script failed somewhere, returns Internal error if so.
        self.semester = semester
        self.maxroll = int(maxroll)
        self.rollPrefix = rollPrefix
        #File Management
        self.firstEntry=True
        self.worksheet=opencsv.opencsv()
        self.tables = {}
        self.numberOfColumns = False
        self.passStudents = 0
        self.totalStudents = 0

        if len(rollPrefix) == 10:
            self.zfill = 2
        elif len(rollPrefix) == 9:
            self.zfill = 3

    def start(self):
        sessurl = self.setCookie(self.department)
        if self.fail:
            return()
        self.sess, self.url = sessurl
        self.loop(wait=True)

    def loop(self,wait=False):
        with ThreadPoolExecutor(max_workers=200) as executor:
            for roll in range(1,self.maxroll+1):
                executor.submit(self.tryandfail,roll)
            executor.shutdown(wait=wait)

    def tryandfail(self,roll):
        while self.getResult(roll) == 1:
            pass

    def setCookie(self, department):
        for _ in range(3):
            #headers
            try:
                #Some randmoness for both seesion Id
                randomness = randomString()

                header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.','Cookies':'ASP.NET_SessionId='+randomness}
                #initialize session

                sess = requests.session()
                sess.headers.update(header)

                #get page and  select appropriate box
                a=sess.get('http://result.rgpv.ac.in/Result/ProgramSelect.aspx')

                soup = BeautifulSoup(a.text,'html5lib')
                deptid =  'radlstProgram_'+ str(department)

                value = soup.find('input',{'id':deptid})['value']
                #post data
                deptid = deptid.replace('_','$')
                viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
                viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
                EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']
                postdata = {'__EVENTTARGET':deptid,'__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'radlstProgram':value}
                resp=sess.post('http://result.rgpv.ac.in/Result/ProgramSelect.aspx',data=postdata,allow_redirects=True)

                url=resp.url
                return((sess, url))

            except Exception as e:
                print(e) # error on console
                self.fail = True
                continue
            else:
                break
        else:
            self.fail = True
    def getResult(self, roll):
        for _ in range(10):
            try:
                #get session and captcha
                with self.lock:
                    resp=self.sess.get(self.url)
                soup = BeautifulSoup(resp.text,'html5lib')
                imageURL="http://result.rgpv.ac.in/Result/"+soup.findAll('img')[1]['src']
                #randomness = randoh.randoo()
                with self.lock:
                    cap = self.sess.get(imageURL, allow_redirects=True)

                #solve the Captcha
                solution = solve_with_neurons.Solve(cap.content)
                if not solution:
                    return(1)
                sleep(5)
                viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
                viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
                EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']

                #Post the data
                fullroll = self.rollPrefix + str(roll).zfill(self.zfill)
                postdata = {'__EVENTTARGET':'','__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'ctl00$ContentPlaceHolder1$txtrollno':fullroll,'ctl00$ContentPlaceHolder1$drpSemester':str(self.semester),'ctl00$ContentPlaceHolder1$rbtnlstSType':'G','ctl00$ContentPlaceHolder1$TextBox1':solution,'ctl00$ContentPlaceHolder1$btnviewresult':'View Result'}
                with self.lock:
                    result=self.sess.post(self.url,data=postdata, allow_redirects=True)

                #process data
                resultFound='<td class="resultheader">'
                wrong='<script language="JavaScript">alert("you have entered a wrong text");</script>'
                notFound='<script language=JavaScript>alert("Result for this Enrollment No. not Found");</script>'
                if resultFound in result.text:
                    self.processResult(result.text,roll)
                    self.progress.increment()
                    return(0)
                elif wrong in result.text:
                    return(1)
                elif "EnableEventValidation" in result.text:
                    self.progress.increment()
                    return(0)
                elif notFound in result.text:
                    self.progress.increment()
                    return(0)
                else:
                    return(1)
                #FIXME HackFIX 2000!
            except Exception as e:
                print(e)
                self.fail = True
                continue
            else:
                break
        else:
            self.fail = True
    def processResult(self,html,rollSuffix):
        list = []
        soup=BeautifulSoup(html,'html5lib')
        with self.lock:
            self.totalStudents = self.totalStudents + 1

        name=soup.find('td',text=re.compile("Name")).findNext().text.replace("\n",'').strip()
        roll=soup.find('td',text=re.compile("Roll")).findNext().text.replace("\n",'').strip()
        with self.lock:
            list.append(roll)
            list.append(name)
        tables=soup.findAll("table")[0].findAll("table")[2].findAll("tr")[6].findAll("table")
        with self.lock:
            if self.firstEntry is True:
                self.firstEntry=False
                header=[]
                header.append("Roll Number")
                header.append("Name")
                for tableNumber in range(1,len(tables)):
                    header.append(tables[tableNumber].findAll('td')[0].text.replace("\n",'').strip())
                header.append("SGPA")
                header.append("CGPA")
                header.append("Result Decision")
                self.tables[0] = header
                self.numberOfColumns = len(header)


        for tableNumber in range(1,len(tables)):
            list.append(tables[tableNumber].findAll('td')[3].text.replace("\n",'').replace("##","*").strip())
        result_des=soup.find("th", text=re.compile(".*CGPA.*")).parent.findNext("td")
        if(result_des.text.replace("\n",'').strip() == "PASS" or result_des.text.replace("\n",'').strip() == "PASS WITH GRACE"):
            with self.lock:
                self.passStudents = self.passStudents + 1
        SGPA=result_des.findNext("td")
        CGPA=SGPA.findNext("td")
        list.append(SGPA.text.replace("\n",'').strip())
        list.append(CGPA.text.replace("\n",'').strip())
        list.append('"'+result_des.text.replace("\n",'').strip()+'"')
        with self.lock:
            self.tables[int(rollSuffix)] = list



    def package(self):
        if self.fail:
            return(500) # Internal server error
        if self.maxroll != self.progress.progress :
            return(601) ## Not 100% progress
        list = sorted(self.tables.items())
        if self.numberOfColumns:
            entry = []
            for t in range(self.numberOfColumns-1):
                entry.append("")
            entry.append(str(self.passStudents)+"/"+str(self.totalStudents)+" = "+ "{0:.2f}".format(self.passStudents*100/self.totalStudents) + "%")
            list.append((0,entry))
            list.append((1,[]))
            self.worksheet.bulkappend(list)
            return(self.worksheet.getcsv())
        else:
            return(701) ## No result Found

    def __del__(self):
        pass

def DoAll(department, semester, maxroll, rollPrefix, filename):
    obj = resultProcessor(department, semester, maxroll, rollPrefix)
    obj.start()
    resp = obj.package()
    assert(resp not in [500,701,601]),resp
    if filename[-4:] != ".csv":
        filename = filename + ".csv"
    with open(filename,'w+') as file:
        file.write(resp)
if __name__ == "__main__":
    department = input("Enter Department: ")
    semester = input("Enter Semester: ")
    rollPrefix = input("Enter Roll Prefix: ")
    maxroll = input("Enter Maximum Roll Number: ")
    filename = input("Enter Filename: ")
    DoAll(department, semester, maxroll, rollPrefix, filename)
