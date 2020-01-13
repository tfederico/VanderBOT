import time
from robot import Robot


def test():
    nao = Robot()
    nao.standup()
    time.sleep(5)
    start = time.time()

    for i in range(30):
        nao.get_camera_image()

    print("Time to capture 30 frames: {}".format(time.time - start))


if __name__ == "__main__":
    test()