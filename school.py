__author__ = 'Sylar'
#!usr/bin/env python

#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import urllib
import cookielib
import json
import StringIO
from Recognize import recognize,binary
#-----------------------------------------------------------------------------
# Login inhttp://cityjw.dlut.edu.cn:7001
def Login2school(username, password):
    # Enable cookie support for urllib2
    url = 'http://cityjw.dlut.edu.cn:7001/ACTIONLOGON.APPPROCESS?mode=4'
    cookiejar = cookielib.CookieJar()
    urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(urlopener)

    urlopener.addheaders.append(('Referer', r'http://cityjw.dlut.edu.cn:7001/ACTIONLOGON.APPPROCESS?mode=3'))
    urlopener.addheaders.append(('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'))
    urlopener.addheaders.append(('Host', r'http://cityjw.dlut.edu.cn:7001'))
    urlopener.addheaders.append(
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0'))
    urlopener.addheaders.append(('Connection', 'Keep-Alive'))

    print 'crawler Login......'

    imgurl = r'http://cityjw.dlut.edu.cn:7001/ACTIONVALIDATERANDOMPICTURE.APPPROCESS'
    isDownOK,img=DownloadFile(imgurl, urlopener)
    # file("./doing/code.jpg", "wb").write( urllib.urlopen(url).read())
    # authcode=raw_input('Please enter the authcode:')
    authcode = recognize(binary(img))

    # Send login/password to the site and get the session cookie
    values = {'WebUserNO': username, 'Password': password, 'Agnomen': authcode, 'submit.x': 0, 'submit.y': 0}
    urlcontent = urlopener.open(urllib2.Request(url, urllib.urlencode(values)))
    page = urlcontent.read()
    print type(page)
    page=page.decode('gb2312').encode('utf-8')
    print type(page)
    # Make sure we are logged in, check the returned page content
    if 'ACTIONLOGOUT' not in page:
        print 'Login failed with username=%s, password=%s and authcode=%s' \
              % (username, password, authcode)
        output={}
        output["status"]="error"
        json_string=json.dumps(output,indent=4,ensure_ascii=False)
        return False,json_string
    else:
        print 'Login succeeded! with username=%s, password=%s and authcode=%s' \
              % (username, password, authcode)
        # print page.decode('gb2312')
        # scheduleurl='http://cityjw.dlut.edu.cn:7001/ACTIONQUERYSTUDENTSCHEDULEBYSELF.APPPROCESS'
        # schedule=urlopener.open(urllib2.Request(scheduleurl, urllib.urlencode({'YearTermNO':14})))
        # schedulecontent=schedule.read()
        # print schedulecontent.decode('gb2312')
        scoreurl = 'http://cityjw.dlut.edu.cn:7001/ACTIONQUERYSTUDENTSCORE.APPPROCESS'
        score = urlopener.open(urllib2.Request(scoreurl, urllib.urlencode({'YearTermNO': 13})))
        scorehtml = score.read()
        json_string=GenerateJson(scorehtml)
        return True,json_string

#------------------------------------------------------------------------------
# Generate json output
def GenerateJson(scorehtml):
    soup = BeautifulSoup(scorehtml)
    ctt = soup.get_text("|", strip=True)[220:-24]
    ctt = ctt.replace("|", "\n")[346:]
    it=ctt.split('\n')
    output={}
    courseinfo=[]
    subdict={}
    cnt=0
    for i in it:
        if cnt==0:
            cnt=cnt+1
            continue

        if cnt==1:
            subdict["category"]=i
        elif cnt==2:
            subdict["id"]=i
        elif cnt==3:
            subdict["name"]=i
        elif cnt==4:
            subdict["examining_method"]=i
        elif cnt==5:
            subdict["credit_hours"]=i
        elif cnt==6:
            subdict["credit"]=i
        elif cnt==7:
            subdict["general_grades"]=i
        elif cnt==8:
            subdict["final_grades"]=i
        elif cnt==9:
            subdict["average_grades"]=i
        cnt=cnt+1
        # print i
        if cnt==10:
            courseinfo.append(subdict)
            subdict={}
            cnt=1
            # print
    output["status"]="ok"
    output["info"]=courseinfo
    json_string=json.dumps(output,indent=4,ensure_ascii=False)
    return json_string


#-----------------------------------------------------------------------------
# Download from fileUrl then save to fileToSave
# Note: the fileUrl must be a valid file
def DownloadFile(fileUrl, urlopener):
    isDownOk = False
    output = StringIO.StringIO()
    try:
        if fileUrl:
            output.write(urlopener.open(urllib2.Request(fileUrl)).read())
            isDownOK = True
        else:
            print 'ERROR: fileUrl is NULL!'
    except:
        isDownOK = False

    return isDownOK,output
#
#
# #------------------------------------------------------------------------------
# def main():
#     isLoginOK=False
#     isLoginOK,json_string=Login2school("201212143", 'wanghe')
#     if isLoginOK:
#         print "OK\n",json_string
#     else:
#         print "Fail\n",json_string
    # Login2school(201212201,19931008)
#
# if __name__ == '__main__':
#     main()