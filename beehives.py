#!/bin/env python

import time
import datetime
import serial
import json
import picamera
import pyimgur
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from subprocess import call
from time import sleep

BEEHIVE_ID = 0

# Timestamp
def get_timestamp():
	ts = time.time()
	st = datetime.datetime.fromtimestamp( ts ).strftime( '%Y-%m-%d %H:%M:%S' )
	return st

# Serial
ser = serial.Serial( '/dev/ttyACM0', 115200 )

# PiCamera
camera = picamera.PiCamera()
IMG_PATH = 'capture.jpg'

# imgur
IMGUR_CLIENT_ID = ""
with open( 'imgur_credits.json' ) as imgur_credits_file:
	imgur_credits = json.load( imgur_credits_file )
	IMGUR_CLIENT_ID = imgur_credits[ 'imgurClientID' ]

# Spreadsheets
scope = [ 'https://spreadsheets.google.com/feeds' ]

while True:
	serial_string = ser.readline()

	timestamp = get_timestamp()
	print( "[%s]" % timestamp )

	print( '>>>> incoming serial_string: %s' % serial_string )

	try:
		# check if incoming data is parsable
		serial_data = json.loads( serial_string )
		print( '>>>> parsed serial_data: %s' % serial_data )

		# Capture image
		camera.capture( IMG_PATH )
		print( '>>>> image captured' )

		# Resize image with imagemagick
		call( [ 'mogrify', '-resize', '50%', IMG_PATH ] )
		print( '>>>> image resized' )

		# Upload image to imgur
		imgur = pyimgur.Imgur( IMGUR_CLIENT_ID )
		image_title = 'MakersBeehive ' + str( BEEHIVE_ID ) + ' | ' + timestamp
		uploaded_image = imgur.upload_image( IMG_PATH, title = image_title )
		print( '>>>> image uploaded at %s' % uploaded_image.link )

		# Upload data to spreadsheet
		creds = ServiceAccountCredentials.from_json_keyfile_name( 'spreadsheet_credits.json', scope )
		client = gspread.authorize( creds )
		sheet = client.open( 'beehives' ).get_worksheet( BEEHIVE_ID )
		row = [ timestamp, serial_data, uploaded_image.link ]
		index = 1
		sheet.insert_row( row, index )

		print( '>>>> data uploaded: ' + str( row ) )

	except:
		print( '>>>> SOMETHING WENT WRONG' )
		pass
