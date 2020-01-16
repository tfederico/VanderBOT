import qi

import numpy as np
import time
import os


"""
This class models a physical Softbank robot (NAO or Pepper).
Programmed on NAOqi version 2.5.5.
"""


class Robot():
    def __init__(self, ip="nao.local", port=9559):
        self.IP = ip
        self.PORT = port
        self.session = qi.Session()
        try:
            self.session.connect("tcp://" + self.IP + ":" + str(self.PORT))
        except RuntimeError:
            print("Can't connect to Naoqi at ip \"" + self.IP + "\" on port " + str(self.PORT) + ".\n")
            quit(-1)
        self.video_service = None
        self.camera_name_id = None
        self.cam_h = None
        self.cam_w = None
        self.tts_service = None
        self.motion_service = None
        self.posture_service = None
        #self.tracker_service = None
        self.led_service = None
        #self.training_data = TrainingData()
        self.informants = 0
        #self.beliefs = []
        #self.landmark_service = None
        self.memory_service = None
        self.speech_service = None
        self.time = None
        self.load_time()
        #self.animation_service = None
        self.audio_service = None
        self.service_setup()

    # Initializes the services
    def service_setup(self):
        self.video_service = self.session.service("ALVideoDevice")
        # Merely text-to-speech, with no motion
        # self.tts_proxy = self.session.service("ALTextToSpeech")
        self.tts_service = self.session.service("ALAnimatedSpeech")
        self.motion_service = self.session.service("ALMotion")
        self.posture_service = self.session.service("ALRobotPosture")
        self.led_service = self.session.service("ALLeds")
        self.memory_service = self.session.service("ALMemory")
        self.speech_service = self.session.service("ALSpeechRecognition")
        self.speech_service.setLanguage("English")
        self.audio_service = self.session.service("ALAudioPlayer")

    # Sets the color of the head leds
    def set_led_color(self, color, speed=0.5):
        color = str.upper(color)
        self.led_service.on("FaceLeds")
        if color == "YELLOW":
            hexcolor = 0x00ffff00
        elif color == "GREEN":
            hexcolor = 0x0000ff00
        elif color == "BLUE":
            hexcolor = 0x000000ff
        elif color == "RED":
            hexcolor = 0x00ff0000
        elif color == "WHITE":
            hexcolor = 0x00ffffff
        elif color == "OFF":
            self.led_service.off("FaceLeds")
            hexcolor = None
        else:
            print("color " + str(color) + " not recognized")
            hexcolor = None
        if color != "OFF":
            self.led_service.fadeRGB("FaceLeds", hexcolor, speed)

    # Text-to-Speech wrapper
    def say(self, words):
        self.tts_service.say(words)

    # Subscribes the video service to retrieve data from cameras
    def video_service_subscribe(self):
        try:
            # "Trust_Video", CameraIndex=1, Resolution=1, ColorSpace=0, Fps=5
            # CameraIndex= 0(Top), 1(Bottom)
            # Resolution= 0(160*120), 1(320*240), VGA=2(640*480), 3(1280*960)
            # ColorSpace= AL::kYuvColorSpace (index=0, channels=1),
            #             AL::kYUV422ColorSpace (index=9,channels=3),
            #             AL::kRGBColorSpace RGB (index=11, channels=3),
            #             AL::kBGRColorSpace BGR (to use in OpenCV) (index=13, channels=3)
            # Fps= OV7670 VGA camera can only run at 30, 15, 10 and 5fps. The MT9M114 HD camera run from 1 to 30fps.
            resolution_type = 2
            fps = 15
            self.cam_w = 320
            self.cam_h = 240
            self.camera_name_id = self.video_service.subscribeCamera("Trust_Video", 1, resolution_type, 11, fps)
        except BaseException as err:
            print("[ERROR] video_proxy_subscribe: catching error " + str(err))
            quit(-1)

    # Unsubscribes to the video service
    def video_service_unsubscribe(self):
        self.video_service.unsubscribe(self.camera_name_id)

    # Captures a single image frame from the cameras
    def get_camera_image(self):
        # Gets the raw image
        result = self.video_service.getImageRemote(self.camera_name_id)
        if result is None:
            print('cannot capture.')
        elif result[6] is None:
            print('no image data string.')
        else:
            # Translates the value to mat
            values = map(ord, list(str(result[6])))
            i = 0
            image = np.zeros((self.cam_h, self.cam_w, 3), np.uint8)
            for y in range(0, self.cam_h):
                for x in range(0, self.cam_w):
                    image.itemset((y, x, 0), values[i + 0])
                    image.itemset((y, x, 1), values[i + 1])
                    image.itemset((y, x, 2), values[i + 2])
                    i += 3
        return image

    # Listen to speech in order to recognize a word in a list of given words
    def listen_for_words(self, vocabulary):
        self.speech_service.setVocabulary(vocabulary, False)
        try:
            self.speech_service.subscribe("ListenWord")
        except BaseException as err:
            print("[ERROR] speech_proxy_subscribe: catching error " + str(err))
            quit(-1)
        while True:
            words = self.memory_service.getData("WordRecognized")
            if words[0] != '':
                break
        self.speech_service.unsubscribe("ListenWord")
        # The first element is always the most probable one
        word = words[0]
        return word

    # Makes the robot stand up
    def standup(self):
        try:
            self.motion_service.setStiffnesses("Body", 1.0)
            self.posture_service.goToPosture("Stand", 1.0)
        except BaseException as err:
            print(err)

    # Makes the robot sit down
    def sitdown(self):
        # Inizializza i motori
        try:
            self.motion_service.setStiffnesses("Body", 1.0)
            self.posture_service.goToPosture("Sit", 1.0)
            self.motion_service.setStiffnesses("Body", 0.0)
        except BaseException as err:
            print(err)
