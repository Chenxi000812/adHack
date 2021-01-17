import requests
import base64, hashlib
import json
import re
import time
from pyquery import PyQuery as pq
import random

session = None


class session:
    s = None

    def __init__(self):
        self.s = login()

    def post(self, url, headers, data):
        res = self.s.post(url, headers=headers, data=data)
        if "antispiderShowVerify.ac" in res.url:
            self.s = login()
            return self.post(url, headers, data)
        return res

    def get(self, url, headers):
        res = self.s.get(url, headers=headers)
        if "antispiderShowVerify.ac" in res.url:
            self.s = login()
            return self.get(url, headers)
        return res


def getUpdateUrl(cpi, dtoken, clazzid, userid, jobid, objectid, duration, otherInfo, playingtime):
    enc = hashlib.md5(("[%s][%s][%s][%s][%s][%s][%s][%s]" % (
        clazzid, userid, jobid, objectid, playingtime * 1000, "d_yHJ!$pdA~5", duration * 1000,
        "0_" + str(duration))).encode("utf-8"))
    r = "https://mooc1-3.chaoxing.com/multimedia/log/a/" + str(cpi) + "/" + str(dtoken) + "?clazzId=" + str(
        clazzid) + "&playingTime=" + str(playingtime) + "&duration=" + str(duration) + "&clipTime=0_" + str(
        duration) + "&objectId=" + str(objectid) + "&otherInfo=" + otherInfo + "&jobid=" + str(
        jobid) + "&userid=" + str(
        userid) + "&isdrag=0&view=pc&enc=" + enc.hexdigest() + "&rt=0.9&dtype=Video&_t=" + str(int(time.time()))
    return r


userangts = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
             "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"]


def getheaders():
    return {
        'User-Agent': random.choice(userangts),
        "Referer": "https://mooc1-3.chaoxing.com/mycourse/studentstudy?chapterId=332164971&courseId=214389597&clazzid=34705159&enc=66624bbafd8967d241e28dc09857bf21",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }


data = {
    "fid": 3107,
    "uname": "17621780046",
    "password": base64.b64encode("wjk12345".encode("utf-8")),
    "refer": "https%3A%2F%2Fmooc1-3.chaoxing.com%2Fknowledge%2Fcards%3Fclazzid%3D34705159%26courseid%3D214389597%26knowledgeid%3D332165098%26num%3D0%26ut%3Ds%26cpi%3D166900117%26v%3D20160407-1",
    "t": "true"
}
courseid = None
answers = {}
knowledgeid = None


def getone(url):
    headers = getheaders()
    res = session.get(url % ('0'), headers=headers)
    ob = re.match("[\s\S]*?try{\\\n.*?mArg = (.*?);", res.text, re.M | re.I)
    mArg = None
    try:
        mArg = json.loads(ob.group(1))
    except:
        login()
        return False
    if len(mArg["attachments"]) is not 0:
        jobid = mArg["attachments"][0]["jobid"]
        objectId = mArg["attachments"][0]["objectId"]
        otherInfo = mArg["attachments"][0]["otherInfo"]
        fid = mArg["defaults"]["fid"]
        global cpi
        cpi = mArg["defaults"]["cpi"]
        userid = mArg["defaults"]["userid"]
        mDetail = json.loads(session.get(
            "https://mooc1-3.chaoxing.com/ananas/status/%s?k=%s&flag=normal&_dc=" % (objectId, fid) + str(
                int(time.time())), headers=headers).text)
        duration = mDetail["duration"]
        dtoken = mDetail["dtoken"]
        ##检查点信息获取
        ##res = session.get("https://mooc1-3.chaoxing.com/richvideo/initdatawithviewer?mid="+mid+"&_dc="+str(int(time.time())),headers = headers)

        res = session.get(
            getUpdateUrl(cpi, dtoken, clazzId, userid, jobid, objectId, duration, otherInfo, duration + 100),
            headers=headers)
        print(res.text)


def exWorkUrl(url):
    res = session.get(url % ('1'),
                      headers=getheaders())
    headers = getheaders()
    ob = re.match("[\s\S]*?try{\\\n.*?mArg = (.*?);", res.text, re.M | re.I)
    mArg = None
    try:
        mArg = json.loads(ob.group(1))
    except:
        login()
        return exWorkUrl(url)
    jobId = mArg["attachments"][0]["jobid"]
    workId = str.replace(jobId, "work-", "")
    ktoken = mArg["defaults"]["ktoken"]
    enc = mArg["attachments"][0]["enc"]
    res = session.get("https://mooc1-3.chaoxing.com/api/work?api=1&workId=" + str(workId) + "&jobid=" + str(
        jobId) + "&needRedirect=true&knowledgeid=" + str(knowledgeid) + "&ktoken=" + str(
        ktoken) + "&ut=s&clazzId=" + str(clazzId) + "&type=&enc=" + str(enc) + "&courseid=" + str(courseid),
                      headers=headers)
    return res


possibleD = ["AB", "ABCD", "AC", "AD", "BC", "BD", "CD", "ABC", "BCD", "A", "B", "C", "D", "E", "AE", "BE", "CE", "DE",
             "ABE", "BCE", "CDE", "ABCE", "BCDE", "ABCDE", "F", "AF", "BF", "CF", "DF", "EF", "ABF", "BCF", "CDF",
             "DEF", "ABCF", "BCDF", "CDEF", "ABCDF", "BCDEF", "ABCDEF"]


def tryAnswer(an):
    i = possibleD.index(an)
    if i < possibleD.__len__() - 1:
        return possibleD[i + 1]


def exeAnswer(url):
    res = exWorkUrl(url)
    dom = pq(res.text)
    ##答过的记录
    if dom("#form1").attr("action") is None:
        return True

    d = {
        "pyFlag": None,
        "courseId": dom("#courseId").attr("value"),
        "classId": dom("#classId").attr("value"),
        "api": dom("#api").attr("value"),
        "workAnswerId": dom("#workAnswerId").attr("value"),
        "totalQuestionNum": dom("#totalQuestionNum").attr("value"),
        "fullScore": dom("#fullScore").attr("value"),
        "knowledgeid": dom("#knowledgeid").attr("value"),
        "oldSchoolId": None,
        "oldWorkId": dom("#oldWorkId").attr("value"),
        "jobid": dom("#jobid").attr("value"),
        "workRelationId": dom("#workRelationId").attr("value"),
        "enc": None,
        "enc_work": dom("#enc_work").attr("value"),
        "userId": dom("#userId").attr("value"),
        "cpi": dom("#cpi").attr("value"),
        "answerwqbid": ""
    }
    trueurl = res.url
    for x in dom(".TiMu").items():
        title = x.children(".Zy_TItle").children(".clearfix").text().replace("\n", "").strip(" ")
        notin = True
        if answers.__contains__(knowledgeid):
            if not answers[str(knowledgeid)].__contains__(title):
                print(title)
            else:
                answers[str(knowledgeid)][title] = answers[str(knowledgeid)][title].replace("我的答案：", "")
                notin = False
        x = x.children(".clearfix").children("input")
        if len(x) is 2:
            x = x.next("input")
        if "type" in x.attr("id"):
            d[x.attr("id")] = x.attr("value")
            d["answerwqbid"] += (x.attr("id").replace("answertype", "") + ",")
            ##单选题
            if x.attr("value") is '0':
                k = x.attr("id")
                if notin:
                    d[k.replace("type", "")] = 'A'
                else:
                    d[k.replace("type", "")] = answers[str(knowledgeid)][title]
            elif x.attr("value") is '1':  ##多选
                k = x.attr("id")
                if notin:
                    d[k.replace("type", "check")] = ["A", "B"]
                    d[k.replace("type", "")] = "AB"
                else:
                    d[k.replace("type", "check")] = []
                    for x in answers[str(knowledgeid)][title]:
                        d[k.replace("type", "check")].append(x)
                    d[k.replace("type", "")] = answers[str(knowledgeid)][title]
            elif x.attr("value") is '3':
                k = x.attr("id")
                if notin:
                    d[k.replace("type", "")] = 'true'
                else:
                    if answers[str(knowledgeid)][title].strip() is "√":
                        d[k.replace("type", "")] = 'true'
                    else:
                        d[k.replace("type", "")] = 'false'
    print(d)
    res = session.post("https://mooc1-3.chaoxing.com/work/" + dom("#form1").attr(
        "action") + "&ua=pc&formType=post&saveStatus=1&pos=&version=1", headers=getheaders(), data=d)
    responseJson = json.loads(res.text)
    if responseJson["stuStatus"] is 5:
        collectWrongAnswer(trueurl, d)


def collectWrongAnswer(url, d):
    res = session.get(url, headers=getheaders())
    print(res.url)
    dom = pq(res.text)
    for x in dom("#ZyBottom").find(".TiMu").items():
        inpu = x.children(".clearfix").children("input")
        if len(inpu) is 2:
            inpu = inpu.next("input")
        dc = x.children(".Py_answer").children("i").attr("class")
        an = x.children(".Py_answer").find("span").text().replace("我的答案：", "").replace("\n", "").strip(" ")
        if " dui" not in dc:
            typ = inpu.attr("value")
            if typ is '1':
                an = tryAnswer(an)
                d[inpu.attr("id").replace("type", "check")] = []
                for x in an:
                    d[inpu.attr("id").replace("type", "check")].append(x)
            elif typ is '3':
                if '√' in an:
                    an = "false"
                else:
                    an = "true"
            else:
                an = tryAnswer(an)
            d[inpu.attr("id").replace("type", "")] = an
    print(d)
    res = session.post("https://mooc1-3.chaoxing.com/work/" + dom("#form1").attr(
        "action") + "&ua=pc&formType=post&saveStatus=1&pos=&version=1", headers=getheaders(), data=d)
    print(res.text)
    responseJson = json.loads(res.text)
    if responseJson["stuStatus"] is 5:
        collectWrongAnswer(url, d)
    elif responseJson["stuStatus"] is 4:
        collectAnswer("https://mooc1-3.chaoxing.com/knowledge/cards?clazzid=" + str(clazzId) + "&courseid=" + str(
            courseid) + "&knowledgeid=" + str(knowledgeid) + "&num=%s&ut=s&v=20160407-1")


def login():
    session = requests.session()
    res = session.post("http://passport2.chaoxing.com/fanyalogin", headers=getheaders(), data=data)
    resJson = json.loads(res.text)
    if resJson["status"]:
        res = session.get('https://mooc1-3.chaoxing.com/mycourse/', headers=getheaders())
        global clazzId
        clazzId = None
        try:
            resJson = json.loads(res.text)
            clazzId = resJson["channelList"][0]["key"]
            return session
        except:
            time.sleep(5)
            return login()


c = []


def collectAnswer(url):
    res = exWorkUrl(url)
    dom = pq(res.text)
    if not answers.__contains__(knowledgeid):
        answers[knowledgeid] = {}
    if dom("#form1").attr("action") is None:
        for x in dom("#ZyBottom").children(".TiMu").items():
            title = x.find(".Zy_TItle").find(".clearfix").text().replace("\n", "")
            if answers[knowledgeid].__contains__(title):
                continue
            answers[knowledgeid][title] = x.find(".Py_answer").children("span:first-child").text().replace("我的答案: ", "")
            print(title)


##
# res = session.get("https://mooc1-3.chaoxing.com/mycourse/studentstudycourselist?courseId=" + str(courseid) + "&clazzid=" + str(clazzId), headers=headers)
# dom = pq(res.text)
#         cell = dom(".cells").items().__next__()
#         for ncell in cell.children(".ncells").items():
#             for yncell in ncell.children(".ncells").items():
#                 kownledgeid = yncell("h5").attr("id").replace("cur", "")
#                 c.append(kownledgeid)
#         open("1.json", "w").write(json.dumps(c))
# ##

if __name__ == '__main__':
    courseid = '214389597'
    # res = session.get(
    # "https://mooc1-3.chaoxing.com/mycourse/studentstudycourselist?courseId=" + str(courseid) + "&clazzid=" + str(
    # clazzId), headers=getheaders())
    # dom = pq(res.text)

    c = []
    # for cell in dom(".cells").items():
    # for ncell in cell.children(".ncells").items():
    # for yncell in ncell.children(".ncells").items():
    # kownledgeid = yncell("h5").attr("id").replace("cur", "")
    # c.append(kownledgeid)
    # open("2.json", "w").write(json.dumps(c))
    session = session()
    answers = json.loads(open("answer.json").read())
    for x in json.loads(open("2.json", "r").read()):
        knowledgeid = x
        exeAnswer("https://mooc1-3.chaoxing.com/knowledge/cards?clazzid=" + str(clazzId) + "&courseid=" + str(
            courseid) + "&knowledgeid=" + str(knowledgeid) + "&num=%s&ut=s&v=20160407-1")
    open("answer.json", "w").write(json.dumps(answers))
    ##getone("https://mooc1-3.chaoxing.com/knowledge/cards?clazzid=34705159&courseid=214389597&knowledgeid=332165100&num=%s&ut=s&cpi=166900117&v=20160407-1")
