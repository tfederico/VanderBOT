import time
from robot import Robot


def test():
    nao = Robot(ip="192.168.0.104")
    nao.video_service_subscribe()
    nao.standup()

    start = time.time()

    for i in range(30):
        nao.get_camera_image()

    print("Time to capture 30 frames: {}".format(time.time() - start))

    nao.video_service_subscribe()
    nao.sitdown()


if __name__ == "__main__":
    test()
