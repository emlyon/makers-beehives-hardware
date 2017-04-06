# MakersBeehives-PI
Raspberry pi script for uploading data from Makers'Beehives

Based on Smart Citizen Kit: https://smartcitizen.me/


### Enable RaspiCam
Type ```sudo raspi-config``` and enable RaspiCam 


### Install dependencies
```
sudo apt-get update
sudo apt-get install python-picamera imagemagick
sudo pip install pyserial pyimgur gspread
```
- [pySerial](http://pythonhosted.org/pyserial/shortintro.html)
- [PiCamera](https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
- [imagemagick](http://makio135.tumblr.com/post/159262507202/resize-image-from-cli-with-imagemagick)
- [PyImgur](https://github.com/Damgaard/PyImgur)
- [gspread: Google Spreadsheets Python API](https://github.com/burnash/gspread)
    - Google Spreadsheets and Python: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
    
    
### Run script on Boot
```sudo nano /etc/rc.local```  
Add this line before exit  
```su pi -c 'python /home/pi/MakersBeehives-PI/beehives.py < /dev/null &'```
