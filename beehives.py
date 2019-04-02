#!/bin/env python

import time
import datetime
import serial
import json
import picamera
import pyimgur
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import socket
from subprocess import call
from time import sleep

hostname = socket.gethostname()
BEEHIVE_ID = hostname[-1]

# Timestamp
def get_timestamp():
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	return st

# Reboot from python
def reboot():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output

# Init Serial
try:
	ser = serial.Serial('/dev/ttyACM0', 115200)
except: 
	try:
		ser = serial.Serial('/dev/ttyACM1', 115200)
	except:
		print('Unable to comunicate with arduino on Serial port')
		reboot()
		sleep(10)

# PiCamera
camera = picamera.PiCamera()
GIF_PATH = 'capture.gif'

# Imgur
image_link = ""
IMGUR_CLIENT_ID = ""
with open('imgur_credits.json') as imgur_credits_file:
	imgur_credits = json.load(imgur_credits_file)
	IMGUR_CLIENT_ID = imgur_credits['imgurClientID']

# Spreadsheets
scope = ['https://spreadsheets.google.com/feeds']

start_time = get_timestamp()
while True :
	ser.flush()
	serial_string = ser.readline()
	# print('>>>> incoming serial_string: %s' % serial_string)

	timestamp = get_timestamp()
	print("[%s]" % timestamp)

	try :
		# Check if incoming data is parsable
		serial_data = json.loads(serial_string)
		print('>>>> parsed serial_data: %s' % serial_data)

		# Check hour (no night vision)
		if serial_data['light'] != '0.00Lux' :
			# Capture sequence
			for i in range(20) :
				img_title = str(i) + '.jpg'
				# Capture image
				camera.capture(img_title)
				print('>>>> image %d captured' % i)

				sleep(0.5)

			# Convert sequence to gif
			call(['mogrify', '-resize', '800x600', '*.jpg'])
			print('>>>> images resized')
			call(['convert', '-delay', '25', '-loop', '0', '*.jpg', GIF_PATH])
			print('>>>> gif created')

			# Upload image to imgur
			imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)
			image_title = 'MakersBeehive ' + str(BEEHIVE_ID) + ' | ' + timestamp
			uploaded_image = imgur.upload_image(GIF_PATH, title = image_title)
			image_link = uploaded_image.link
			print('>>>> image uploaded at %s' % image_link)

		# Upload data to spreadsheet
		creds = ServiceAccountCredentials.from_json_keyfile_name('spreadsheet_credits.json', scope)
		client = gspread.authorize(creds)
		sheet = client.open('beehives').get_worksheet(BEEHIVE_ID)
		row = [timestamp, serial_string, image_link]
		index = 1
		sheet.insert_row(row, index)

		print('>>>> data uploaded: ' + str(row))

		call(['sudo', 'shutdown', '-h', 'now'])

		# Wait 30 minutes
		# sleep(1800)
		# ser.flush()

	except Exception as e:
		if e.__class__ != ValueError:
			print('>>>> SOMETHING WENT WRONG')
			print(str(e))
			# reboot()
			
			template = "An exception of type {0} occured"
			message = template.format(type(e).__name__)
			print message
			# Wait 1 minute
			sleep(60)
			ser.flush()
		pass
