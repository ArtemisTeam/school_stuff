from urllib2 import urlopen
from json import load


def buildurl(postid):
    baseurl = 'http://www.kuaidi100.com/autonumber/auto?num='
    url = baseurl + postid
    return url


def getcom(postid):
    url = buildurl(postid)
    response = urlopen(url)
    j = load(response)
    if j:
        return j[0]['comCode']
    else:
        return None


def getposturl(postid):
    postid = str(postid)
    com = getcom(postid)
    if com:
        resp = 'http://m.kuaidi100.com/index_all.html?type=%s&postid=%s' % (com, postid)
        return resp
    else:
        return None

if __name__ == '__main__':
    resp = getposturl(905220573038)
    print resp
