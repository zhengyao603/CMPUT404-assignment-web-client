#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")
    return


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    #def get_host_port(self,url):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return

    def get_code(self, data):
        data_list = data.split('\r\n')
        code = data_list[0].split(' ')[1]
        return int(code)

    def get_headers(self,data):
        header = []
        data_list = data.split('\r\n')
        for item in data_list:
            if item == '':
                break
            header.append(item)
        return '\r\n'.join(header)

    def get_body(self, data):
        data_list = data.split('\r\n')
        index = 0
        for item in data_list:
            if item == '':
                break
            index += 1
        body = data_list[index + 1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()
        return

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # send GET request and recieve response from server
        addr = urllib.parse.urlparse(url).netloc.split(':')[0]
        if (urllib.parse.urlparse(url).port):
            port = urllib.parse.urlparse(url).port
        else:
            if (urllib.parse.urlparse(url).scheme == 'https'):
                port = 443
            elif (urllib.parse.urlparse(url).scheme == 'http'):
                port = 80
        path = urllib.parse.urlparse(url).path
        if not path:
            path = '/'
        self.connect(addr, port)
        self.sendall("GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, urllib.parse.urlparse(url)[1]))
        response = self.recvall(self.socket)
        self.close()

        # parse the response info
        code = self.get_code(response)
        body = self.get_body(response)
        header = self.get_headers(response)

        print(header)
        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # send POST request and recieve response from server
        addr = urllib.parse.urlparse(url).netloc.split(':')[0]
        if (urllib.parse.urlparse(url).port):
            port = urllib.parse.urlparse(url).port
        else:
            if (urllib.parse.urlparse(url).scheme == 'https'):
                port = 443
            elif (urllib.parse.urlparse(url).scheme == 'http'):
                port = 80
        path = urllib.parse.urlparse(url).path
        if not path:
            path = '/'
        # parse args and calculate length
        length = 0
        if args:
            args = urllib.parse.urlencode(args)
            length = len(args)
        self.connect(addr, port)
        self.sendall("POST %s HTTP/1.1\r\nHost: %s\r\nContent-type:application/x-www-form-urlencoded\r\nContent-length:%d\r\n\r\n" % (path, urllib.parse.urlparse(url)[1], length))
        if args:
            self.sendall(args)
        response = self.recvall(self.socket)
        self.close()

        # parse the response info
        code = self.get_code(response)
        body = self.get_body(response)
        header = self.get_headers(response)

        print(header)
        print(body)

        return HTTPResponse(code, body)


    # processing http requests
    def command(self, url, command="GET", args=None):
        # if it is http POST
        if (command == "POST"):
            return self.POST(url, args)
        # if it is http GET
        else:
            return self.GET(url, args)
    
if __name__ == "__main__":
    client = HTTPClient()
    # command = "GET"

    # if no argument provided
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)

    # if http method and url are both provided
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))

    # if only url provided
    else:
        print(client.command(sys.argv[1]))
