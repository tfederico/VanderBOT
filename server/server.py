#!/usr/bin/env python

import socket
from messages.messages import Request, Response
from datetime import datetime
import time as t

from ast import literal_eval

class Server(object):
    def __init__(self, host, port):
        self.close_request = False
        self.latest_frame = None
        self.HOST = host
        self.PORT = port
        # Start
        self.listen_and_respond()

    def route_request(self, request):
        pass

    # Waits for a request, processes it and responds
    def listen_and_respond(self):
        format_width = 55
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(None)
        try:
            s.bind((self.HOST, self.PORT))
        except socket.error as msg:
            print(str(msg) + ". Bind failed.")
            quit(-1)
        print("Listening...\n")
        s.listen(5)
        while not self.close_request:
            # Accepts the connection
            conn, addr = s.accept()
            _, time = self.get_datetime()
            print('+-' + '-' * format_width + '-+')
            # print('| {0:^{1}} |'.format('Connected by ' + str(addr) + ' on ' + time, format_width))
            print('| {0:^{1}} |'.format('Connection from ' + str(addr[0]) + ":" + str(addr[1]) +
                                        ' at ' + time, format_width))
            try:
                start_time = t.time()
                # Reads the request

                data = conn.recv(4096)
                request = literal_eval(data.decode('utf-8'))
                request = Request(request['command'], request['parameters'])

                print('+-' + '-' * format_width + '-+')
                print('| {0:^{1}} |'.format(request, format_width))
                camera_op = "CAMERA" in request.command
                # Performs an operation
                response = self.route_request(request)  # Routing function, returns a Response
                # Sends back the data
                data = str(response.__dict__).encode('utf-8')

                if camera_op:
                    conn.sendall(data)
                else:
                    conn.send(data)
                # conn.shutdown(socket.SHUT_WR)
                elapsed = t.time() - start_time
                #print('| {0:^{1}} |'.format(response, format_width))
                print('| {0:^{1}} |'.format("Time elapsed: " + str(round(elapsed, 2)) + "s", format_width))
                print('+-' + '-' * format_width + '-+')
                # Closes the connection
                conn.close()
            except KeyboardInterrupt:
                break
        # Terminate the server process
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print('\nTerminated')

    # Fetches current date and time, in string format
    def get_datetime(self):
        ts = datetime.utcfromtimestamp(t.time())
        date = ts.strftime('%d/%m/%Y')
        time = ts.strftime('%H:%M:%S')
        return date, time

    # Returns the current time, for latency tests
    def ping(self):
        return Response(True, t.time())

    def close(self):
        self.close_request = True
        return Response(True, None)
