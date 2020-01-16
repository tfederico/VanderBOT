from server import Server
from robot import Robot
from simulatedRobot import SimulatedRobot
from messages import Response
import cv2 as cv
import base64


class SimulatedNaoServer(Server):
    def __init__(self, nao_ip="nao.local", nao_port=9559, ip="127.0.0.1", port=54321):
        self.nao_ip = nao_ip
        self.nao_port = nao_port
        self.nao = SimulatedRobot(nao_ip, nao_port)
        print("Connected to Nao")
        super(SimulatedNaoServer, self).__init__(ip, port)
    
    # Manages the request, based on the command tag
    def route_request(self, request):

        if request.command == "PING":
            response = super(SimulatedNaoServer, self).ping()
        elif request.command == "CAMERA":
            response = self.get_camera_image()
        elif request.command == "LED":
            response = self.set_led_color(request.parameters)
        elif request.command == "LISTEN":
            response = self.listen_for_words(request.parameters)
        elif request.command == "STAND":
            response = self.standup()
        elif request.command == "SIT":
            response = self.sitdown()
        elif request.command == "SAY":
            response = self.say(request.parameters)
        elif request.command == "CLOSE":
            response = super(SimulatedNaoServer, self).close()
        else:
            # Command not recognized
            response = Response(False, "Invalid command code")
        return response

    # Sets the color of the head leds
    def set_led_color(self, *params):
        self.nao.set_led_color(params[0], params[1])
        return Response(True, None)

    # Text-to-Speech wrapper
    def say(self, words):
        self.nao.say(words)
        return Response(True, None)

    # Captures a single image frame from the cameras
    def get_camera_image(self):
        img = self.nao.get_camera_image()
        retval, buff = cv.imencode(".jpg", img)
        data = base64.b64encode(buff)
        return Response(True, data)

    # Listen to speech in order to recognize a word in a list of given words
    def listen_for_words(self, vocabulary):
        return Response(True, self.nao.listen_for_words(vocabulary))

    # Makes the robot stand up
    def standup(self):
        self.nao.standup()
        return Response(True, None)

    # Makes the robot sit down
    def sitdown(self):
        self.nao.sitdown()
        return Response(True, None)


if __name__ == "__main__":
    server = SimulatedNaoServer()
