# -*- coding: utf-8 -*-

import randoh
from bs4 import BeautifulSoup
import os
import requests
import pytesseract
from pytesseract import image_to_string
from PIL import Image
import time

def write(data):
    file = open("output.html",'w');
    file.write(data)
    file.close
    return(0)


def grabSession(dept):
    try:
        #Some randmoness for both seesion Id and file name
        randomness = randoh.randoo()
        header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.','Cookies':'ASP.NET_SessionId='+randomness}
        #initialize session
        sess = requests.session()
        sess.headers.update(header)
        a=sess.get('http://result.rgpv.ac.in/Result/ProgramSelect.aspx')

        soup = BeautifulSoup(a.text,'lxml')
        deptid =  'radlstProgram_'+ str(dept)

        value = soup.find('input',{'id':deptid})['value']

        deptid = deptid.replace('_','$')
        viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
        viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
        EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']
        postdata = {'__EVENTTARGET':deptid,'__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'radlstProgram':value}
        resp=sess.post('http://result.rgpv.ac.in/Result/ProgramSelect.aspx',data=postdata,allow_redirects=True)
        return({'session':sess,'response':resp})
    except:
        return(0)

def getResult(grabbedSession,url,roll,semester):
    sess = grabbedSession
    resp=sess.get(url)
    soup = BeautifulSoup(resp.text,'lxml')
    imageURL="http://result.rgpv.ac.in/Result/"+soup.findAll('img')[1]['src']
    randomness = randoh.randoo()
    cap = sess.get(imageURL, allow_redirects=True)
    open(randomness + '.jpg', 'wb').write(cap.content) #Write to file

    #config = ('-l eng --oem 2 --psm 13')
    solution = pytesseract.image_to_string(Image.open(randomness+'.jpg')).replace(" ","")
    os.remove(randomness + '.jpg')
    time.sleep(5)
    viewState = soup.find('input',{'id':'__VIEWSTATE'})['value']
    viewStateGen = soup.find('input',{'id':'__VIEWSTATEGENERATOR'})['value']
    EvenValidation = soup.find('input',{'id':'__EVENTVALIDATION'})['value']
    postdata = {'__EVENTTARGET':'','__EVENTARGUMENT':'','__LASTFOCUS':'','__VIEWSTATE':viewState,'__VIEWSTATEGENERATOR':viewStateGen,'__EVENTVALIDATION':EvenValidation,'ctl00$ContentPlaceHolder1$txtrollno':roll,'ctl00$ContentPlaceHolder1$drpSemester':str(semester),'ctl00$ContentPlaceHolder1$rbtnlstSType':'G','ctl00$ContentPlaceHolder1$TextBox1':solution,'ctl00$ContentPlaceHolder1$btnviewresult':'View Result'}
    result=sess.post(url,data=postdata,allow_redirects=True)

    resultFound='<td class="resultheader">'
    notFound='<script language=JavaScript>alert("Result for this Enrollment No. not Found");</script>'
    if resultFound in result.text:
        processResult(result.text)
        return(0)
    elif notFound in result.text:
        return(0)
    else:
        return(1)


def processResult(html):
    soup=BeautifulSoup(html)
    
