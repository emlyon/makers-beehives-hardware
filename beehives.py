#!/bin/env python

import time
import datetime
import serial
import json
import picamera
import pyimgur
import socket
import os
from subprocess import call
from time import sleep

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

hostname = socket.gethostname()
BEEHIVE_ID = int(hostname[-1])


# Timestamp
def get_timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return st


# Reboot from python
def reboot():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess

    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)


def shutdown():
    call("sudo shutdown -h now".split())
    sleep(10)


# Init Serial
try:
    ser = serial.Serial("/dev/ttyACM0", 115200)
except:
    try:
        ser = serial.Serial("/dev/ttyACM1", 115200)
    except:
        print("Unable to comunicate with arduino on Serial port")
        shutdown()

# PiCamera
try:
    camera = picamera.PiCamera()
except:
    print("Unable to start camera")
    shutdown()

GIF_PATH = "capture.gif"

# Imgur
image_link = ""
IMGUR_CLIENT_ID = ""
with open("imgur_credits.json") as imgur_credits_file:
    imgur_credits = json.load(imgur_credits_file)
    IMGUR_CLIENT_ID = imgur_credits["imgurClientID"]

# Read and upload data
capture_done = False
images_resized = False
gif_created = False
gif_uploaded = False
while True:
    ser.flush()
    serial_string = ser.readline()
    print(">>>> incoming serial_string: %s" % serial_string)

    timestamp = get_timestamp()
    print("[%s]" % timestamp)

    try:
        # Check if incoming data is parsable
        serial_data = json.loads(serial_string)
        print(">>>> parsed serial_data: %s" % serial_data)

        # Check light before taking pics (no night vision)
        if serial_data["light"] != "0.00Lux":
            # Capture sequence
            if capture_done is not True:
                for i in range(20):
                    img_title = str(i) + ".jpg"
                    # Capture image
                    camera.capture(img_title)
                    print(">>>> image %d captured" % i)

                    sleep(0.5)
                capture_done = True

            # Convert sequence to gif
            if images_resized is not True:
                call(["mogrify", "-resize", "800x600", "*.jpg"])
                print(">>>> images resized")
                images_resized = True

            # Create gif
            if gif_created is not True:
                call(["convert", "-delay", "25", "-loop", "0", "*.jpg", GIF_PATH])
                print(">>>> gif created")
                gif_created = True

            # Upload image to imgur
            if gif_uploaded is not True:
                imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)
                image_title = "MakersBeehive " + str(BEEHIVE_ID) + " | " + timestamp
                uploaded_image = imgur.upload_image(GIF_PATH, title=image_title)
                image_link = uploaded_image.link
                print(">>>> image uploaded at %s" % image_link)
                gif_uploaded = True

        else:
            image_link = "http://placehold.it/800x533/000000/444444?text=No+Light"

        # Upload data to firebase
        cred = credentials.Certificate("firebase-secrets.json")

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://makerslab-beehives-default-rtdb.europe-west1.firebasedatabase.app/"
            },
        )

        print(">>>> trying to push data to firebase")
        beehive_data = db.reference("beehives/{0}/data".format(BEEHIVE_ID))
        data = {
            "dateTime": timestamp,
            "imageLink": image_link,
            **serial_data,
            "serialString": serial_string,
        }
        beehive_data.push(data)
        print(">>>> data pushed to firebase")

        os.system("cd /home/bee/makers-beehives-hardware && git pull")
        sleep(10)

        shutdown()

    except Exception as e:
        print(">>>> SOMETHING WENT WRONG")
        print(str(e))
        template = "An exception of type {0} occured"
        message = template.format(type(e).__name__)
        print(message)

        # Shutdown if error is not due to incomplete JSON parsing
        if e.__class__ != ValueError:
            shutdown()

        pass
