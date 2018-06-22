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


BEEHIVE_ID = 3


# Timestamp
def get_timestamp():
	ts = time.time()
	st = datetime.datetime.fromtimestamp( ts ).strftime( '%Y-%m-%d %H:%M:%S' )
	return st

# Reboot from python
def reboot():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


start_time = get_timestamp()


# Serial
ser = serial.Serial( '/dev/ttyACM0', 115200 )

# PiCamera
camera = picamera.PiCamera()
IMG_PATH = 'capture.gif'

# Imgur
image_link = ""
IMGUR_CLIENT_ID = ""
with open( 'imgur_credits.json' ) as imgur_credits_file:
	imgur_credits = json.load( imgur_credits_file )
	IMGUR_CLIENT_ID = imgur_credits[ 'imgurClientID' ]

# Spreadsheets
scope = [ 'https://spreadsheets.google.com/feeds' ]

while True :
	serial_string = ser.readline()
	# print( '>>>> incoming serial_string: %s' % serial_string )

	timestamp = get_timestamp()
	print( "[%s]" % timestamp )

	try :
		# Check if incoming data is parsable
		serial_data = json.loads( serial_string )
		print( '>>>> parsed serial_data: %s' % serial_data )

		# Check hour ( no night vision )
		if serial_data[ 'light' ] != '0.00Lux' :
			# Capture sequence
			for i in range( 20 ) :
				img_title = str( i ) + '.jpg'
				# Capture image
				camera.capture( img_title )
				print( '>>>> image %d captured' % i )

				sleep( 0.5 )

			# Convert sequence to gif
			call( [ 'mogrify', '-resize', '800x600', '*.jpg' ] )
			print( '>>>> images resized' )
			call( [ 'convert', '-delay', '25', '-loop', '0', '*.jpg', IMG_PATH ] )
			print( '>>>> gif created' )

			# Upload image to imgur
			imgur = pyimgur.Imgur( IMGUR_CLIENT_ID )
			image_title = 'MakersBeehive ' + str( BEEHIVE_ID ) + ' | ' + timestamp
			uploaded_image = imgur.upload_image( IMG_PATH, title = image_title )
			image_link = uploaded_image.link
			print( '>>>> image uploaded at %s' % image_link )

		# Upload data to spreadsheet
		creds = ServiceAccountCredentials.from_json_keyfile_name( 'spreadsheet_credits.json', scope )
		client = gspread.authorize( creds )
		sheet = client.open( 'beehives' ).get_worksheet( BEEHIVE_ID )
		row = [ timestamp, serial_string, image_link ]
		index = 1
		sheet.insert_row( row, index )

		print( '>>>> data uploaded: ' + str( row ) )

		call( [ 'sudo', 'shutdown', '-h', 'now' ] )

		# Wait 30 minutes
		sleep( 1800 )
		ser.flush()

	except :
		print( '>>>> SOMETHING WENT WRONG' )
		reboot()

		# Wait 10 minute
		sleep( 600 )
		ser.flush()
		pass
