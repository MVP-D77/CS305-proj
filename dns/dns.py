import socket
import sys

import flask
from flask import Flask

app = Flask(__name__)

fileName = None
previousPortIndex = None

# 这个方法也是东拼西凑
# 参考1：https://blog.csdn.net/wuzhongqiang/article/details/121809324
@app.route('/dnsRequest')
def dnsRequest():
    global previousPortIndex
    with open(fileName, encoding='utf-8') as f:
        allAvailablePort = [s.strip() for s in f.readlines()]
        if previousPortIndex is None:
            previousPortIndex = -1
        for i in range(1, len(allAvailablePort), 1):
            newPort = (previousPortIndex + i) % len(allAvailablePort)
            if isPortFree(int(allAvailablePort[newPort])):
                # 对于可以直接访问到的端口号，直接返回该端口号的response
                previousPortIndex = newPort
                re = flask.make_response(str(allAvailablePort[previousPortIndex]))
                return re

        # 如果找了一圈都没找到，那就执行RR(Round Robin)
        previousPortIndex = (previousPortIndex + 1) % len(allAvailablePort)
        return flask.make_response((allAvailablePort[previousPortIndex]))


def isPortFree(port: int, host: str = '127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(1)
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        return False
    except Exception as e:
        # print(e.args)
        pass
    return True


def dnsServer(debug: bool, host: str, dnsServerPort: int, threaded: bool, dnsFileName: str):
    global fileName
    fileName = dnsFileName
    app.run(debug=debug, host=host, port=dnsServerPort, threaded=threaded)


if __name__ == '__main__':
    fileName = sys.argv[1]
    port = sys.argv[2]
    dnsServer(debug=True, host='127.0.0.1', dnsServerPort=port, threaded=True, dnsFileName=fileName)
