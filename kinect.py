#####################################################################
#
# kinect.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################


# from .OSC import OSCServer, ThreadingOSCServer, OSCClient, OSCMessage
from pythonosc import osc_server, dispatcher, udp_client
import time
import threading
import numpy as np
import math
from . import core
import socket



# This class assumes that Synapse is running.
# It handles communications with Synapse and presents joint data to
# the app.
class Kinect(threading.Thread):
    kRightHand = "/righthand"
    kLeftHand = "/lefthand"
    kRightElbow = "/rightelbow"
    kLeftElbow = "/leftelbow"
    kRightFoot = "/rightfoot"
    kLeftFoot = "/leftfoot"
    kRightKnee = "/rightknee"
    kLeftKnee = "/leftknee"
    kHead = "/head"
    kTorso = "/torso"
    kLeftShoulder = "/leftshoulder"
    kRightShoulder = "/rightshoulder"
    kLeftHip = "/lefthip"
    kRightHip = "/righthip"
    kClosestHand = "/closesthand"

    # position coordinate system type
    kBody  = '_pos_body'
    kWorld = '_pos_world'
    kScreen = '_pos_screen'

    kPosNum = { kBody: 1, kWorld: 2, kScreen: 3 }

    def __init__(self, remote_ip = None, pos_type = kBody):
        super(Kinect, self).__init__()

        self.pos_type = pos_type

        # Synapse is running on a remote machine:
        if remote_ip:
            listen_ip = socket.gethostbyname(socket.gethostname())
            listen_port = 12345

            send_ip = remote_ip
            send_port = 12321

        # Synapse is running locally on this machine, using localhost
        else:
            listen_ip = 'localhost'
            listen_port = 12345

            send_ip = 'localhost'
            send_port = 12346

        # create a dispatcher and server, which handles incoming messages from Synapse
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map( '/tracking_skeleton', self.callback_tracking_skeleton )
        self.server = osc_server.ThreadingOSCUDPServer( (listen_ip, listen_port), self.dispatcher)

        # create the client, which sends control messages to Synapse
        self.client = udp_client.SimpleUDPClient(send_ip, send_port)

        # member vars
        self.active_joints = {}
        self.last_heartbeat_time = 0

        # start the server listening for messages
        self.start()

        core.register_terminate_func(self.close)

    # close must be called before app termination or the app will hang
    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def run(self):
        print("Worker thread entry point")
        self.server.serve_forever()

    def add_joint(self, joint):
        self.dispatcher.map( joint + self.pos_type, self.callback )        
        self.active_joints[joint] = np.array([0.0, 0.0, 0.0])

    def on_update(self):
        now = time.time()
        send_heartbeat = now - self.last_heartbeat_time > 3.0
        if send_heartbeat:
            self.last_heartbeat_time = now

        try:
            if send_heartbeat:
                for j in self.active_joints:
                    msg = (j + "_trackjointpos", Kinect.kPosNum[self.pos_type])
                    self.client.send_message(*msg)
        except Exception as x:
            print(x, 'sending to', self.client._address, self.client._port)

    def get_joint(self, joint) :
        return np.copy(self.active_joints[joint])

    def callback(self, addr, x, y, z):
        joint_name = addr.replace(self.pos_type, "")
        self.active_joints[joint_name] = np.array((x,y,z))

    def callback_tracking_skeleton(self, addr, args):
        print('tracking_skeleton', args)

