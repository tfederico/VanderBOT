import socket

from requests import ConnectionError
from ast import literal_eval
from messages import Request, Response
import base64
import cv2 as cv
import numpy as np
import cStringIO as csio
import PIL.Image as Image
try:
    import cPickle as pickle
except ImportError:
    import pickle
pickle.HIGHEST_PROTOCOL = 2


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

        self.socket.send(data_out)
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

if __name__ == "__main__":
    client = Client()

    response = client.send_image_request(Request("CAMERA", None))
    print(response)
    img_value = literal_eval(response)['values']
    print(type(img_value))
    buff = base64.b64decode(img_value)
    print(type(buff))
    buff_arr = np.fromstring(buff, dtype=np.uint8)
    print(type(buff_arr))
    img = cv.imdecode(buff_arr, cv.IMREAD_UNCHANGED)
    print(type(img))
    cv.imshow("", img)
    cv.waitKey(0)
    client.connection_close()