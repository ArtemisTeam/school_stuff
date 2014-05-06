__author__ = 'halfcrazy'

#-*- coding: utf-8 -*-

from flask import Flask, request
import xml.etree.ElementTree as ET
from school import schedule, grades
from kuaidi import getposturl

app = Flask(__name__)
# app.debug=True


@app.route('/')
def index():
    return "query interface for cyjw.dlut.edu.cn"


@app.route('/kuaidi', methods=['GET'])
def kuaidichaxun():
    postid = request.args.get('postid')
    resp = getposturl(postid)
    if resp:
        return resp
    else:
        return ''


@app.route('/grades', methods=['GET'])
def parse_grades_get():
    name = request.args.get('name')
    password = request.args.get('password')
    password = password.replace(' ', '+')
    term = request.args.get('term')
    if term == None:
        term = 13
    flag, json_string = grades(name, password, term)
    return json_string


@app.route('/schedule', methods=['GET'])
def parse_schedule_get():
    name = request.args.get('name')
    password = request.args.get('password')
    password = password.replace(' ', '+')
    flag, json_string = schedule(name, password)
    return json_string


def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

if __name__ == "__main__":
    app.run()
