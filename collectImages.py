import time
from simulatedRobot import SimulatedRobot
import cv2 as cv

def get_nao():
    nao = SimulatedRobot()
    return nao 

def capture_image(bot):
    
    #nao.video_service_subscribe()

    start = time.time()
    img = bot.get_camera_image()
    print("Time: {}".format(time.time() - start))

    #nao.video_service_subscribe()
    return img

if __name__ == "__main__":
    img = capture_image(get_nao())
    cv.imshow("test", img)
    cv.waitKey(0)