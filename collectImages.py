from ast import literal_eval
from messages.messages import Request
from client.client import Client
import base64
import cv2 as cv
import numpy as np

if __name__ == "__main__":
    client = Client()

    response = client.send_image_request(Request("CAMERA", None)).decode('utf-8')
    print(type(response))
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