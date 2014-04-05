__author__ = 'Sylar'
from flask import Flask,request
import xml.etree.ElementTree as ET
from school import Login2school
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'
@app.route('/hello')
def hello():
    return 'Hello World'
@app.route('/grades', methods=['GET'])
def post_msg():
    name = request.args.get('name')
    password=request.args.get('password')
    flag,json_string=Login2school(name,password)
    return json_string

def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

if __name__ == "__main__":
    # app.debug=True
    app.run()