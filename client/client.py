import socket

from requests import ConnectionError

from messages.messages import Response

import time


class Client():
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.PORT = 54321
        self.socket = None

    def connect_to_proxy(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10.0)
        try:
            value = self.socket.connect((self.HOST, self.PORT))
            return True
        except ConnectionError:
            print("[ERROR] Cannot contact remote SawyerProxy server! Is it up and running?")
            return False

    # Sends a network request to the ROS workstation and receives an answer back
    def send_image_request(self, request):
        camera_op = "CAMERA" in request.command     # Indicates if a camera image was requested
        data_out = str(request.__dict__) #pickle.dumps(request, protocol=2)    # Explicitly requests Python2 protocol

        while not self.connect_to_proxy():   # Open connection
            time.sleep(1)       # In case server is offline, continues to try

        self.socket.send(data_out.encode('utf-8'))
        # Now wait for response
        try:
            if camera_op:            # If it's an image, incrementally receive all the data chunks
                data_in = b''
                while True:
                    block = self.socket.recv(4096)
                    if block:
                        data_in += block
                    else:
                        break
            else:
                data_in = self.socket.recv(4096)
            self.connection_close()   # Close the connection
            response = data_in

        except EOFError:
            response = Response(False, "Reception error")
        return response

    def connection_close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
