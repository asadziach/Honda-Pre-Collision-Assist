from __future__ import print_function # WalabotAPI works on both Python 2 an 3.
from sys import platform
from os import system
from imp import load_source
from os.path import join

import paho.mqtt.client as mqtt

if platform == 'win32':
	modulePath = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK',
		'python', 'WalabotAPI.py')
elif platform.startswith('linux'):
    modulePath = join('/usr', 'share', 'walabot', 'python', 'WalabotAPI.py')     

wlbt = load_source('WalabotAPI', modulePath)
wlbt.Init()

def SendSensorTargets(targets, mqttc):
    system('cls' if platform == 'win32' else 'clear')
    #ignore too low amplitude targets because its mostly noise
    lowLimit = 0.003
    if targets:
        for i, target in enumerate(targets):
            if target.amplitude > lowLimit:
                #we are only interested in the y for Pedestrian Detection.
                mqttc.publish("walabot", target.yPosCm)
                print('Target #{}:\nx: {}\ny: {}\nz: {}\namplitude: {}\n'.format(
                    i + 1, target.xPosCm, target.yPosCm, target.zPosCm,
                    target.amplitude))
    else:
        print('No Target Detected')

def PedestrianDetect():

    mqttc = mqtt.Client()
    #defaults to local host
    mqttc.connect("localhost")
    mqttc.loop_start()

    # input parameters found by Trial and Error
    minInCm, maxInCm, resInCm = 10, 100, 2
    minIndegrees, maxIndegrees, resIndegrees = -20, 20, 10
    minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees = -45, 45, 2

    # Set MTI mode
    mtiMode = False
    # Configure Walabot database install location (for windows)
    wlbt.SetSettingsFolder()
    # 1) Connect : Establish communication with walabot.
    wlbt.ConnectAny()
    # 2) Configure: Set scan profile and arena
    # Set Profile - to Sensor.
    wlbt.SetProfile(wlbt.PROF_SENSOR)
    # Setup arena - specify it by Cartesian coordinates.
    wlbt.SetArenaR(minInCm, maxInCm, resInCm)
    # Sets polar range and resolution of arena (parameters in degrees).
    wlbt.SetArenaTheta(minIndegrees, maxIndegrees, resIndegrees)
    # Sets azimuth range and resolution of arena.(parameters in degrees).
    wlbt.SetArenaPhi(minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees)
    # Moving Target Identification: standard dynamic-imaging filter
    filterType = wlbt.FILTER_TYPE_MTI if mtiMode else wlbt.FILTER_TYPE_NONE
    wlbt.SetDynamicImageFilter(filterType)
    # 3) Start: Start the system in preparation for scanning.
    wlbt.Start()
    if not mtiMode: # if MTI mode is not set - start calibrartion
        # calibrates scanning to ignore or reduce the signals
        wlbt.StartCalibration()
        while wlbt.GetStatus()[0] == wlbt.STATUS_CALIBRATING:
            wlbt.Trigger()
    while True:
        appStatus, calibrationProcess = wlbt.GetStatus()
        # 5) Trigger: Scan(sense) according to profile and record signals
        # to be available for processing and retrieval.
        wlbt.Trigger()
        # 6) Get action: retrieve the last completed triggered recording
        targets = wlbt.GetSensorTargets()
        rasterImage, _, _, sliceDepth, power = wlbt.GetRawImageSlice()
 
        SendSensorTargets(targets, mqttc)
    # 7) Stop and Disconnect.
    wlbt.Stop()
    wlbt.Disconnect()
    print('Terminate successfully')

if __name__ == '__main__':
    PedestrianDetect()
