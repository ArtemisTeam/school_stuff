__author__ = 'halfcrazy'
#!usr/bin/env python

#-*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
import urllib2
import urllib
import gzip
import cookielib
import json
import StringIO
import string
import re
from Recognize import recognize, binary

#-----------------------------------------------------------------------------
# Login inhttp://cityjw.dlut.edu.cn:7001


def Login2school(username, password):
    # Enable cookie support for urllib2
    url = 'http://cityjw.dlut.edu.cn:7001/ACTIONLOGON.APPPROCESS?mode=4'
    cookiejar = cookielib.CookieJar()
    urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(urlopener)

    urlopener.addheaders.append(
        ('Referer', r'http://cityjw.dlut.edu.cn:7001/ACTIONLOGON.APPPROCESS?mode=3'))
    urlopener.addheaders.append(
        ('Accept-Language', r'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'))
    urlopener.addheaders.append(('Accept-Encoding', r'gzip,deflate'))
    urlopener.addheaders.append(('Host', r'http://cityjw.dlut.edu.cn:7001'))
    urlopener.addheaders.append(
        ('User-Agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0'))
    urlopener.addheaders.append(('Connection', 'Keep-Alive'))

    # print 'crawler Login......'

    imgurl = r'http://cityjw.dlut.edu.cn:7001/ACTIONVALIDATERANDOMPICTURE.APPPROCESS'
    # download captcha
    isDownOK, img = DownloadFile(imgurl, urlopener)
    # recognize the captcha
    authcode = recognize(binary(img))
    # Send login/password to the site and get the session cookie
    values = {'WebUserNO': username, 'Password': password,
              'Agnomen': authcode, 'submit.x': 0, 'submit.y': 0}
    urlcontent = urlopener.open(
        urllib2.Request(url, urllib.urlencode(values).replace('%2A', '*')))
    page = urlcontent.read()
    page = unpack(page, urlcontent)
    page = page.decode('gb2312').encode('utf-8')
    # Make sure we are logged in, check the returned page content
    if 'ACTIONLOGOUT' not in page:
        # print 'Login failed with username=%s, password=%s and authcode=%s' \
              #% (username, password, authcode)
        return None, urlopener
    else:
        # print 'Login succeeded! with username=%s, password=%s and authcode=%s' \
        #     % (username, password, authcode)
        pattern = re.compile(r'<td align="left">(.*)</td>')
        name = pattern.search(page).groups()
        name = name[0]
        return name, urlopener


#------------------------------------------------------------------------------
# unzip module
def unpack(page, urlcontent):
    if urlcontent.headers.get('content-encoding') == 'deflate':
        try:
            page = zlib.decompress(page, -zlib.MAX_WBITS)
        except zlib.error:
            page = zlib.decompress(page)
    elif urlcontent.headers.get('content-encoding') == 'gzip':
        obj = StringIO.StringIO(page)
        page = gzip.GzipFile(fileobj=obj, mode="r").read()
    return page


#------------------------------------------------------------------------------
# Grade module


def grades(username, password, term):
    name, urlopener = Login2school(username, password)
    if name == None:
        output = {}
        output["status"] = "error"
        json_string = json.dumps(output, indent=4, ensure_ascii=False)
        return False, json_string
    else:
        score_url = 'http://cityjw.dlut.edu.cn:7001/ACTIONQUERYSTUDENTSCORE.APPPROCESS'
        score_resp = urlopener.open(
            urllib2.Request(score_url, urllib.urlencode({'YearTermNO': term})))
        scorehtml = score_resp.read()
        scorehtml = unpack(scorehtml, score_resp)
        json_string = generate_grades_json(scorehtml, term)
        return True, json_string.encode('utf-8')

#------------------------------------------------------------------------------
# Schedule module


def schedule(username, password):
    name, urlopener = Login2school(username, password)
    if name == None:
        output = {}
        output["status"] = "error"
        json_string = json.dumps(output, indent=4, ensure_ascii=False)
        return False, json_string.encode('uft-8')
    else:
        schedule_url = 'http://cityjw.dlut.edu.cn:7001/ACTIONQUERYSTUDENTSCHEDULEBYSELF.APPPROCESS'
        schedule_resp = urlopener.open(schedule_url)
        # .decode('gb2312').encode('utf-8')
        schedulehtml = schedule_resp.read()
        # .decode('gb2312').encode('utf-8')
        schedule = unpack(schedulehtml, schedule_resp)
        # print schedule
        json_string = generate_shedule_json(schedule)
        return True, json_string.encode('utf-8')

def post(url, data):  
    req = urllib2.Request(url)  
    data = urllib.urlencode(data)  
    #enable cookie  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read()  

def teacher_schedule(id):
    data={
          "DepartmentNO":None,
          "StaffroomNO":None,
          "TeacherNO":id
          }
    url="http://cityjw.dlut.edu.cn:7001/ACTIONQUERYTEACHERSCHEDULEBYPUBLIC.APPPROCESS"
    page=post(url,data)
    json_string=generate_shedule_json(page)
    return True,json_string.encode('utf-8')
#------------------------------------------------------------------------------
# Generate grades json


def generate_grades_json(scorehtml, term):
    soup = BeautifulSoup(scorehtml, "lxml")
    ctt = soup.get_text("|", strip=True)[220:-24]
    ctt = ctt.replace("|", "\n")[346:]
    it = ctt.split('\n')
    output = {}
    courseinfo = []
    subdict = {}
    cnt = 0
    for i in it:
        if cnt == 0:
            cnt = cnt + 1
            continue

        if cnt == 1:
            subdict["category"] = i
        elif cnt == 2:
            subdict["id"] = i
        elif cnt == 3:
            subdict["name"] = i
        elif cnt == 4:
            subdict["examining_method"] = i
        elif cnt == 5:
            subdict["credit_hours"] = i
        elif cnt == 6:
            subdict["credit"] = i
        elif cnt == 7:
            subdict["general_grades"] = i
        elif cnt == 8:
            subdict["final_grades"] = i
        elif cnt == 9:
            subdict["average_grades"] = i
        cnt = cnt + 1
        # print i
        if cnt == 10:
            courseinfo.append(subdict)
            subdict = {}
            cnt = 1
            # print
    output["status"] = "ok"
    output["term"] = term
    output["info"] = courseinfo
    json_string = json.dumps(output, indent=4, ensure_ascii=False)
    return json_string

#-----------------------------------------------------------------------------
# Generate schedule json


def generate_shedule_json(page):
    page = page.replace('<', ' <')
    soup = BeautifulSoup(page, "lxml")
    tr_tag = soup.find_all('tr', limit=14)
    # print tr_tag
    arr = []
    arr.append(tr_tag[8].get_text())  # 1-2
    arr.append(tr_tag[9].get_text())  # 3-4
    arr.append(tr_tag[10].get_text())  # 5-6
    arr.append(tr_tag[11].get_text())  # 7-8
    arr.append(tr_tag[12].get_text())  # 9-10
    arr.append(tr_tag[13].get_text())  # 11-12

    output = {}
    info = []
    for row in arr:
        subdict = {}
        lst = map(string.strip, row.split('\n'))
        # lst=row.split('\n')
        subdict['monday'] = lst[2]
        subdict['tuesday'] = lst[3]
        subdict['wednesday'] = lst[4]
        subdict['thursday'] = lst[5]
        subdict['friday'] = lst[6]
        subdict['saturday'] = lst[7]
        subdict['sunday'] = lst[8]
        info.append(subdict)
    output['info'] = info
    json_string = json.dumps(output, indent=4, ensure_ascii=False)
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
            isDownOk = False
    except:
        isDownOK = False

    return isDownOK, output


def testlogin(username, password):
    name, urlopener = Login2school(username, password)
    if name == None:
        print "failed"
    else:
        print "success"


if __name__ == "__main__":
    pass
