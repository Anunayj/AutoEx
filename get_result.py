import randoh
from bs4 import BeautifulSoup
import os
import requests
def write(data):
    file = open("output.html",'w');
    file.write(data)
    file.close
    return(0)


def get_result_page(dept):
    #Some randmoness for both seesion Id and file name
    randomness = randoh.randoo()
    header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.','Cookies':'ASP.NET_SessionId='+randomness}
    #initialize session
    sess = requests.session()
    sess.headers.update(header)
    a=sess.get('http://result.rgpv.ac.in/Result/ProgramSelect.aspx')

    #GET request for Captha image
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

print(get_result_page(2)['response'].text)
