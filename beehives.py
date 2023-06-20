#!/bin/env python

import time
import datetime
import serial
import json
import re
import picamera
import pyimgur
import getpass
import os
from subprocess import call
from time import sleep

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

BEEHIVE_ID = getpass.getuser()


# Timestamp
def get_timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return st


# Use absolute path to enable access from outside the script's directory
def filepath(relative_path):
    return os.path.join(os.path.dirname(__file__), relative_path)


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


# Firebase init
cred = credentials.Certificate(filepath("firebase-secrets.json"))

firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://makerslab-beehives-default-rtdb.europe-west1.firebasedatabase.app/"
    },
)


# Upload data to firebase
def upload_data(data):
    print(">>>> trying to push data to firebase")
    beehive_data = db.reference("beehives/{0}/data".format(BEEHIVE_ID))
    beehive_data.push(data)
    print(">>>> data pushed to firebase")


# Init Serial
try:
    ser = serial.Serial("/dev/ttyACM0", 115200)
except:
    try:
        ser = serial.Serial("/dev/ttyACM1", 115200)
    except:
        print("Unable to comunicate with arduino on Serial port")
        shutdown()


def read_serial_data():
    ser.flush()
    serial_string = ser.readline()  # read complete line from serial output
    # while not "\\r\\n" in str(serial_string):  # check if full data is received.
    # Matching end of line was not enough :
    # Sometimes the serial output is not complete and the beginning of the string is missing.
    while not re.search("\{.*}", str(serial_string)):
        time.sleep(0.001)  # delay of 1ms
        serial_string = ser.readline()
    print(">>>> incoming serial_string: %s" % serial_string)
    serial_string = serial_string.decode("utf-8").rstrip()
    serial_data = json.loads(serial_string)
    print(">>>> parsed serial_data: %s" % serial_data)
    return serial_data


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
with open(filepath("imgur-secrets.json")) as imgur_secrets_file:
    imgur_secrets = json.load(imgur_secrets_file)
    IMGUR_CLIENT_ID = imgur_secrets["imgurClientID"]

# Read and upload data
capture_done = False
images_resized = False
gif_created = False
gif_uploaded = False
while True:
    try:
        timestamp = get_timestamp()
        print("[%s]" % timestamp)
        # Check if incoming data is parsable
        serial_data = read_serial_data()

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
        beehive_data = {
            "dateTime": timestamp,
            "imageLink": image_link,
            "sensors": serial_data,
        }
        upload_data(beehive_data)

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
