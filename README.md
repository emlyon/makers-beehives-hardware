# MakersBeehives-PI
Raspberry pi script for uploading data from Makers'Beehives

Based on Smart Citizen Kit: https://smartcitizen.me/


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
