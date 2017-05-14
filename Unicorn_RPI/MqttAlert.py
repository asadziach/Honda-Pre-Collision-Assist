#!/usr/bin/env python

from random import randint
from time import sleep

import unicornhat as unicorn

import paho.mqtt.client as mqtt

#setup the unicorn hat
unicorn.set_layout(unicorn.AUTO)
unicorn.brightness(0.5)

#get the width and height of the hardware
width, height = unicorn.get_shape()

def turnon(r, g, b, msg):
        #print the relevant message
        print(msg,r,g,b)
        #set the LEDs to the relevant lighting (all on/off)
        for y in range(height):
                for x in range(width):
                        unicorn.set_pixel(x,y,r,g,b)
                        unicorn.show()


# if __name__ == "__main__":
#         #program starts here
#         print_header()
#         #this is the starting state (True=ON)
#         bToggle = True
#         #indefinite loop
#         while True:
#                 #call the toggle function with a given state and it will return the inverse
#                 bToggle = toggle(bToggle)
#                 #pause and await input from keyboard i.e. <enter> no characters are checked
#                 raw_input("")

import paho.mqtt.client as mqtt
bToggle = True
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("walabot/alert")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    turnon(255, 0, 0, "ON")
    sleep(.5)
    turnon(0, 0, 0, "OFF")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
