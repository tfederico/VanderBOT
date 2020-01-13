import time
from simulatedRobot import SimulatedRobot


def test():
    nao = SimulatedRobot()
    #nao.video_service_subscribe()
    #nao.standup()

    start = time.time()

    for i in range(30):
        img = nao.get_camera_image()
        print(img)

    print("Time to capture 30 frames: {}".format(time.time() - start))

    #nao.video_service_subscribe()
    #nao.sitdown()


if __name__ == "__main__":
    test()
