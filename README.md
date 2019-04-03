# MakersBeehives-Phardware

![](beehive-diagram.png)

## Raspberry Pi config
remove auto-start from /etc/rc.local
```
sudo nano /etc/rc.local
```
(add a `#` at the beginning of `su bee -c 'cd /home/bee/makersbeehives-pi/ && python beehives.py < /$`)

auto start and git pull using crontab
```
crontab -e
```
select nano `2`  
and add:
```
@reboot sleep 10 && cd /home/bee/makers-beehives-hardware && echo `{ git pull && echo '{"result":"up to date"}' > /home/bee/git_status.json ; } || echo '{"result":"could not update"}' > /home/bee/git_status.json` && python beehives.py
```

config wifi:
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

```
network={
    ssid="makerslab"
    psk="makerslab"
}

network={
	ssid="EMLIOT"
	psk="48hgu@Gw8!"
}
```

git clone:
```
cd && git clone https://github.com/emlyon/makers-beehives-hardware.git
```


Raspberry pi script for uploading data from Makers'Beehives

Based on Smart Citizen Kit: https://smartcitizen.me/  
Upload `sck_ruches_firmware` to Smart Citizen Kit via Arduino software

### Enable RaspiCam
Type ```sudo raspi-config``` and enable RaspiCam


### Install dependencies
```
sudo apt-get update
sudo apt-get install git python-picamera imagemagick
sudo pip install pyserial pyimgur gspread oauth2client
cd
git clone https://github.com/emlyon/MakersBeehives-PI.git
```
- [pySerial](http://pythonhosted.org/pyserial/shortintro.html)
- [PiCamera](https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
- [imagemagick](http://makio135.tumblr.com/post/159262507202/resize-image-from-cli-with-imagemagick)
- [PyImgur](https://github.com/Damgaard/PyImgur)
- [gspread: Google Spreadsheets Python API](https://github.com/burnash/gspread)
    - Google Spreadsheets and Python: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html


### Imgur & Google spreadsheets credits:
Go to https://api.imgur.com/oauth2/addclient to register an app then create `imgur_credits.json` formatted as follows:
```
{
	"imgurClientID": "xxxxxxxxxxxxxxx",
	"imgurClientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Download Spreadsheet credits as documented on https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html and save them as `spreadsheet_credits.json`


### Run script on Boot
```sudo nano /etc/rc.local```  
Add this line before exit  
```su pi -c 'python /home/pi/MakersBeehives-PI/beehives.py < /dev/null &'```


### Reference
- [Raspberry Pi / Python: install pip for Python modules dependencies installation](http://makio135.tumblr.com/post/84826991967/raspberry-pi-python-install-pip-for-python)
- [How to mount a USB flash drive on Raspberry Pi](http://raspi.tv/2012/mount-a-usb-flash-drive-on-raspberry-pi)
- [How to setup multiple WiFi networks?](http://raspberrypi.stackexchange.com/questions/11631/how-to-setup-multiple-wifi-networks#11738)
- [imagemagick/mogrify](https://www.imagemagick.org/script/mogrify.php)
- [Camera Module](https://www.raspberrypi.org/documentation/hardware/camera/README.md)
- [Scheduling tasks with Cron](https://www.raspberrypi.org/documentation/linux/usage/cron.md)
- [Change default username](http://raspberrypi.stackexchange.com/questions/12827/change-default-username)
- [Execute sudo without Password](http://askubuntu.com/questions/147241/execute-sudo-without-password#147265)


## Arduino config

### Load sensors
![](https://cdn.instructables.com/F36/2JAR/J822Y1NX/F362JARJ822Y1NX.LARGE.jpg)
Based on https://www.instructables.com/id/Arduino-Bathroom-Scale-With-50-Kg-Load-Cells-and-H/

### Seed Studio Base Shield wiring

- [Base Shield Grove](https://www.ebay.fr/itm/Shield-base-GROVE-pou-Arduino-compatible-Arduino-SEESHIEV2-/282741493252)
- [Temperature & Humidity Sensor](https://www.seeedstudio.com/Grove-Temperature-Humidity-Sensor-DHT11-p-745.html) on D2
	- libraries: https://github.com/adafruit/Adafruit_Sensor & https://github.com/adafruit/DHT-sensor-library
	- code: http://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/ & https://www.instructables.com/id/Arduino-DHT11-Sensor/
- [Grove Sound Sensor](https://www.seeedstudio.com/Grove-Sound-Sensor-p-752.html) on A0
	- code: http://wiki.seeedstudio.com/Grove-Sound_Sensor/
- [Digital Light Sensor](https://www.seeedstudio.com/Grove-Digital-Light-Sensor-p-1281.html) on I2C
	- library: http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/: Digital Light Sensor Library
	- code: http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/ & http://www.ardumotive.com/lux-sensor-en.html
- [Multichannel Gas Sensor](https://www.seeedstudio.com/Grove-Multichannel-Gas-Sensor-p-2502.html) on I2C
	- library: https://github.com/Seeed-Studio/Mutichannel_Gas_Sensor/archive/master.zip
	- code: http://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor/
