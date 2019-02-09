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

firstEntry=True

class processFile:
    def __init__(self,filename):
        self.worksheet=opencsv.opencsv(filename)


    def processResult(self,html):
        global firstEntry
        list=[]
        soup=BeautifulSoup(html,'html5lib')

        name=soup.find('td',text=re.compile("Name")).findNext().text.replace("\n",'').strip()
        roll=soup.find('td',text=re.compile("Roll")).findNext().text.replace("\n",'').strip()
        list.append(roll)
        list.append(name)
        tables=soup.findAll("table")[0].findAll("table")[2].findAll("tr")[6].findAll("table")
        if firstEntry is True:
            header=[]
            header.append("Name")
            header.append("Roll Number")
            for tableNumber in range(1,len(tables)):
                header.append(tables[tableNumber].findAll('td')[0].text.replace("\n",'').strip())
            header.append("SGPA")
            header.append("CGPA")
            header.append("Result Decision")
            self.worksheet.append(header)
            firstEntry=False


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

def grabSession(dept):
    try:
        #Some randmoness for both seesion Id and file name
        randomness = randoh.randoo()
        header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.','Cookies':'ASP.NET_SessionId='+randomness}
        #initialize session
        sess = requests.session()
        sess.headers.update(header)
        #get page
        a=sess.get('http://result.rgpv.ac.in/Result/ProgramSelect.aspx')

        soup = BeautifulSoup(a.text,'html5lib')
        deptid =  'radlstProgram_'+ str(dept)

        value = soup.find('input',{'id':deptid})['value']
        #post data
        deptid = deptid.replace('_','$')
        viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
        viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
        EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']
        postdata = {'__EVENTTARGET':deptid,'__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'radlstProgram':value}
        resp=sess.post('http://result.rgpv.ac.in/Result/ProgramSelect.aspx',data=postdata,allow_redirects=True)
        return({'session':sess,'response':resp})
    except:
        return(0)

def getResult(grabbedSession,url,roll,semester,file):
    #get session and captcha
    sess = grabbedSession
    resp=sess.get(url)
    soup = BeautifulSoup(resp.text,'html5lib')
    imageURL="http://result.rgpv.ac.in/Result/"+soup.findAll('img')[1]['src']
    #randomness = randoh.randoo()
    cap = sess.get(imageURL, allow_redirects=True)
    #open(randomness + '.jpg', 'wb').write(cap.content) #Write to file

    config = '-l eng --oem 2 --psm 13 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqurstuvwxyz'
    #solve the Captcha
    #solution = pytesseract.image_to_string(Image.open(randomness+'.jpg'), config=config).replace(" ","")
    solution = pytesseract.image_to_string(Image.open(BytesIO(cap.content)), config=config).replace(" ","")
    #os.remove(randomness + '.jpg')
    time.sleep(5)
    viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
    viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
    EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']

    #Post the data
    postdata = {'__EVENTTARGET':'','__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'ctl00$ContentPlaceHolder1$txtrollno':roll,'ctl00$ContentPlaceHolder1$drpSemester':str(semester),'ctl00$ContentPlaceHolder1$rbtnlstSType':'G','ctl00$ContentPlaceHolder1$TextBox1':solution,'ctl00$ContentPlaceHolder1$btnviewresult':'View Result'}
    result=sess.post(url,data=postdata,allow_redirects=True)

    #process data
    resultFound='<td class="resultheader">'
    notFound='<script language=JavaScript>alert("Result for this Enrollment No. not Found");</script>'
    if resultFound in result.text:
        file.processResult(result.text)
        return(0)
    elif notFound in result.text:
        return(0)
    else:
        return(1)
