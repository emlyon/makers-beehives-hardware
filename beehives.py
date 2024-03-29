#!/bin/env python

import time
import datetime
import serial
import serial.tools.list_ports
import json
import re
import picamera
import pyimgur
import getpass
import os
import sys
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


# Upload data to firebase
def upload_data(data):
    print(">>>> trying to push data to firebase")
    beehive_data = db.reference("beehives/{0}/data".format(BEEHIVE_ID))
    beehive_data.push(data)
    print(">>>> data pushed to firebase")


# Send error to firebase
def upload_error(error_data):
    print(">>>> sending error to firebase")
    db.reference("errors").push(error_data)
    print(">>>> error sent to firebase")


# Log error in file and if possible upload it to firebase
def log_error(error, upload=True):
    timestamp = get_timestamp()
    errorType = type(error).__name__
    errorMessage = str(error)
    print(">>>> logging error")
    print(f"Type: {errorType}\nMessage: {errorMessage}\nDateTime: {timestamp}")
    error_data = {"type": errorType, "message": errorMessage, "dateTime": timestamp}
    with open(filepath("error.log"), "a") as error_log:
        error_log.write(str(error_data) + "\n")
    print(">>>> error logged")
    if upload is True:
        try:
            upload_error(error_data)
        except Exception as e:
            print(">>>> unable to upload error to firebase")
            log_error(e, False)


def read_serial_data():
    ser.flush()
    ser.write(str.encode("DATA?\n"))
    serial_string = ser.readline()  # read complete line from serial output
    # while not "\\r\\n" in str(serial_string):  # check if full data is received.
    # Matching end of line was not enough :
    # Sometimes the serial output is not complete and the beginning of the string is missing.
    while not re.search("\{.*}", str(serial_string)):
        print(f">>>> reading serial_string: {serial_string}")
        time.sleep(0.1)  # delay of 100ms
        ser.write(str.encode("DATA?\n"))
        serial_string = ser.readline()
    print(">>>> incoming serial_string: %s" % serial_string)
    serial_string = serial_string.decode("utf-8").rstrip()
    print(">>>> decoded serial_string: %s" % serial_string)
    serial_data = json.loads(serial_string)
    print(">>>> parsed serial_data: %s" % serial_data)
    return serial_data


def check_internet_connection():
    command = ["ping", "-c", "1", "google.com"]
    return call(command) == 0


def remove_images():
    print(">>>> removing images")
    os.system("rm *.jpg *.gif")


def update_source_code():
    # Update code from distant repository
    print(">>>> updating code")
    # Ensure that the script is executed from the repository's directory
    repository_path = filepath("")
    os.system(f"cd {repository_path} && git pull")
    print(">>>> code updated")


def end_operation():
    remove_images()
    update_source_code()
    print("Exiting after end of cycle...")
    shutdown()
    # While working on the code, it is more practical to exist instead of shutting down the Pi :
    # sys.exit("Exiting after end of cycle...")


def init_serial_communication():
    available_ports = list(serial.tools.list_ports.comports())
    ports_names = [port.name for port in available_ports]

    # Try to connect to the Arduino on each port and return serial object if successful
    for port_name in ports_names:
        ser = connect_to_serial_port(port_name)
        if ser:
            break

    # return serial object or log error and exit if no port is available
    if not ser:
        log_error("Unable to connect to Arduino on any port")
    else:
        print(f"Connected to Arduino on port {port_name}")
        return ser


def connect_to_serial_port(port_name):
    print(f"Trying to connect to Arduino on port {port_name}")
    port_path = "/dev/" + port_name
    try:
        ser = serial.Serial(port_path, 115200)
    except serial.SerialException as e:
        print(str(e))
        return False
    return ser


def wait_for_arduino_setup():
    ser.flush()
    serial_string = ser.readline()
    print(f">>>> reading serial_string: {serial_string}")
    while not re.search("Arduino setup is complete.", str(serial_string)):
        ser.flush()
        print(f">>>> reading serial_string: {serial_string}")
        time.sleep(0.1)
        serial_string = ser.readline()
    print("serial communication is ready")


def take_picture(img_nb, nb_retries=0):
    img_title = str(img_nb) + ".jpg"
    try:
        camera.capture(img_title)
        print(">>>> image %s captured" % img_title)
    except picamera.PiCameraError as e:
        print("Something went wrong with the camera")
        log_error(e)
        nb_retries += 1
        if nb_retries < 3:
            take_picture(img_title, nb_retries)
        else:
            print("Unable to take picture")


while True:
    if check_internet_connection() is True:
        print(">>>> internet connection")
        break
    else:
        print(">>>> no internet connection")
        sleep(5)

# Firebase init
cred = credentials.Certificate(filepath("firebase-secrets.json"))

firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://makerslab-beehives-default-rtdb.europe-west1.firebasedatabase.app/"
    },
)

ser = init_serial_communication()
wait_for_arduino_setup()

# PiCamera
try:
    camera = picamera.PiCamera()
except:
    print("Unable to start camera")
    sys.exit("Exiting after error...")

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
        print(">>>> checking incoming data")
        serial_data = read_serial_data()

        # Check light before taking pics (no night vision)
        if serial_data["light"] != "0.00Lux":
            # Capture sequence
            if capture_done is not True:
                print(">>>> capturing sequence")
                for img_nb in range(1, 21):
                    take_picture(img_nb)
                    sleep(0.5)
                capture_done = True
                print(">>>> sequence captured")

            # Convert sequence to gif
            if images_resized is not True:
                print(">>>> resizing images")
                call(["mogrify", "-resize", "800x600", "*.jpg"])
                print(">>>> images resized")
                images_resized = True

            # Create gif
            if gif_created is not True:
                print(">>>> creating gif")
                call(["convert", "-delay", "25", "-loop", "0", "*.jpg", GIF_PATH])
                print(">>>> gif created")
                gif_created = True

            # Upload image to imgur
            if gif_uploaded is not True:
                print(">>>> uploading gif to imgur")
                imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)
                image_title = "MakersBeehive " + str(BEEHIVE_ID) + " | " + timestamp
                uploaded_image = imgur.upload_image(GIF_PATH, title=image_title)
                image_link = uploaded_image.link
                print(">>>> gif uploaded at %s" % image_link)
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

        end_operation()

    except Exception as e:
        print(">>>> SOMETHING WENT WRONG")
        print(str(e))
        log_error(e)
        remove_images()

        # Shutdown if error is not due to incomplete JSON parsing
        if e.__class__ != ValueError:
            sys.exit("Exiting after error...")

        pass
