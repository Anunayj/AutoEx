# -*- coding: utf-8 -*-

import randoh
from bs4 import BeautifulSoup
import os
import requests
import pytesseract
from pytesseract import image_to_string
from PIL import Image
import time
import opencsv
import re
from io import BytesIO
import threading
from concurrent.futures import ThreadPoolExecutor
import sys, getopt

executor = ThreadPoolExecutor(max_workers=100)

class processFile:
    def __init__(self,filename):
        self.firstEntry=True
        self.worksheet=opencsv.opencsv(filename)


    def processResult(self,html):

        list=[]
        soup=BeautifulSoup(html,'html5lib')

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
            self.worksheet.append(header)
            self.firstEntry=False


        for tableNumber in range(1,len(tables)):
            list.append(tables[tableNumber].findAll('td')[3].text.replace("\n",'').replace("##","*").strip())
        result_des=soup.find("th", text=re.compile(".*CGPA.*")).parent.findNext("td")
        SGPA=result_des.findNext("td")
        CGPA=SGPA.findNext("td")
        list.append(SGPA.text.replace("\n",'').strip())
        list.append(CGPA.text.replace("\n",'').strip())
        list.append('"'+result_des.text.replace("\n",'').strip()+'"')
        self.worksheet.append(list)
        print("Done: "+roll)


class extract:
    def __init__(self,dept):
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


    def getResult(self,roll,semester):
        #get session and captcha
        resp=self.sess.get(self.url)
        soup = BeautifulSoup(resp.text,'html5lib')
        imageURL="http://result.rgpv.ac.in/Result/"+soup.findAll('img')[1]['src']
        #randomness = randoh.randoo()
        cap = self.sess.get(imageURL, allow_redirects=True)

        config = '-l eng --oem 0 --psm 13 -c tessedit_char_whitelist=2346789AcCDeEFgGHjJkKlLnNpPqQRTuUvVxXYyzZ'
        #solve the Captcha
        solution = pytesseract.image_to_string(Image.open(BytesIO(cap.content)), config=config).replace(" ","")
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
            self.file.processResult(result.text)
            return(0)
        elif notFound in result.text:
            return(0)
        else:
            return(1)
    def driver(self,roll,semester):
        for retryNumber in range(10):
            try:
                while self.getResult(roll,semester) is 1:
                    pass
            except Exception as e:
                print(e)
                continue
            break

    def loop(self,rollPrefix,totalStudents,semester,fileName,x):
        self.file=processFile(fileName)
        for roll in range(1,totalStudents+1):
            print(rollPrefix+str(roll).zfill(x))
            executor.submit(self.driver,rollPrefix+str(roll).zfill(x),semester)


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
    if opt == '-h':
        print('AutoEx.py -d <DepartmentCode> -p <rollPrefix> -t <totalStudents> -s <semester> -o <fileName> -z <NumberOftrailingZero>')
        sys.exit()
    elif opt in ("-d", "--dept"):
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

    obj=extract(int(dept))
    obj.loop(prefixs,int(total),int(sem),output,int(zfill))


if __name__ == "__main__":
   main(sys.argv[1:])
