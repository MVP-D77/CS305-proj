import argparse
import sys
import threading
import time
# sys.path.append('/home/CS305-proj')
import xml.dom.minidom

import requests
from flask import Flask, Response

app = Flask(__name__)
lock = threading.Lock()
class Proxy():
    def __init__(self, parser):
        # parse中得到的
        self.log_file = parser.log
        self.alpha = parser.alpha
        self.listen_port = parser.listen_port
        self.dns_port = parser.dns_port
        self.default_port = parser.default_port
        self.allBits = dict()
        self.low_rate = 0
        self.T_current = dict()

    def storeVideoRate(self):
        port = request_dns().decode()
        url = 'http://localhost:' + port + '/vod/big_buck_bunny.f4m'
        response = requests.get(url)
        content = response.content
        DOMTree = xml.dom.minidom.parseString(content)
        collection = DOMTree.documentElement
        apis = collection.getElementsByTagName("media") # 获取所有的api标签

        for api in apis: 
            # print(api.childNodes[0].data) # 获取api标签内的值
            if 'bitrate' in api.attributes.keys():
                self.allBits[int(api.attributes['bitrate'].value)] = api.attributes['url'].value
        sorted(self.allBits.keys())
        self.low_rate = int(self.allBits[list(self.allBits.keys())[0]])

proxy = None

@app.route('/')
@app.route('/<resource>')
def GetResources(resource=None):
    port = request_dns().decode()
    url = 'http://localhost:' + port
    if resource:
        url = url + '/' + resource
    return Response(requests.get(url))


@app.route('/vod/big_buck_bunny.f4m')
def BecomeNoList():
    port = request_dns().decode()
    url = 'http://localhost:' + port + '/vod/big_buck_bunny_nolist.f4m'
    return Response(requests.get(url))

@app.route('/vod/<message>')
def video_request(message):
    port = request_dns().decode()
    message_m, rate = modify_request(message, port)
    url = 'http://localhost:' + port + '/vod/' + message_m
    ts = time.time()

    response = requests.get(url)
    tf = time.time()
    print(url)
    length = response.headers['Content-Length']
    calculate_throughput(port, ts, tf, length)
    return Response(response)

def modify_request(message, port):
    """
    Here you should change the requested bit rate according to your computation of throughput.
    And if the request is for big_buck_bunny.f4m, you should instead request big_buck_bunny_nolist.f4m 
    for client and leave big_buck_bunny.f4m for the use in proxy.
    """
    if message == 'big_buck_bunny.f4m':
        return 'big_buck_bunny_nolist.f4m'
    else:
        position = message.index("Seg")
        if port not in proxy.T_current.keys():
            lock.acquire()
            proxy.T_current[port] = proxy.low_rate
            lock.release()
            chunk = str(proxy.low_rate) + message[position:]
            return chunk, proxy.low_rate
        else:
            max_rate = 0
            temp_T_current = proxy.T_current[port]
            for rate in proxy.allBits.keys():
                if temp_T_current >= 1.5* rate:
                    max_rate = rate
                else:
                    break
            chunk = str(max_rate) + message[position:]
            print(proxy.T_current[port], max_rate)
            return chunk, max_rate

def request_dns():
    """
    Request dns server here.
    """
    if proxy.default_port:
        return str(proxy.default_port)
    url = 'http://localhost:' + str(proxy.dns_port) + '/dnsRequest'
    return requests.get(url).content

def calculate_throughput(port, ts, tf, length):
    """
    Calculate throughput here.
    """
    # T_new = int(length)/(tf - ts)/1024 * 10000
    T_new = float(length)*8/1024/(tf-ts)
    print(proxy.T_current[port], proxy.alpha, T_new , tf-ts)

    lock.acquire()
    proxy.T_current[port] = proxy.T_current[port] * (1 - proxy.alpha) + proxy.alpha * T_new
    lock.release()

if __name__ == '__main__':
     # Parse training configuration
    parser = argparse.ArgumentParser()

    #params
    parser.add_argument('--log', type=str, default='../logs/log1.txt',  help='Log file to store information')
    parser.add_argument('--alpha', type=float, default=0.1,  help='the coefficient in throughput estimate')
    parser.add_argument('--listen_port', type=int, default=6600,  help='the proxy server listen on')
    parser.add_argument('--dns_port', type=int, default=5000,  help='the dns server listen on')
    parser.add_argument('--default_port', type=int, default = None,  help='specifying the port of the web server')

    config = parser.parse_args()
    
    proxy = Proxy(config)
    proxy.storeVideoRate()
    app.run(debug=True, host='127.0.0.1', port=config.listen_port, threaded=True)
