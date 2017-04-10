/*
 Smart Citizen Kit
 Ambient Board Beta Firmware v. 0.9.4

 http://smartcitizen.me/


 Compatible:
 Smart Citizen Kit v.1.1( Kickstarter ) ( ATMEGA32U4 @ 8Mhz - Lylipad Arduino USB )

 Structure:
 sck_ruches_firmware.ino - Core Runtime.

 SCKAmbient.h - Supports the sensor reading and calibration functions.
 SCKBase.h - Supports the data management functions( WiFi, RTClock and EEPROM storage )
 Constants.h - Defines pins configuration and other static parameters.
*/

#include <Wire.h>
#include <EEPROM.h>
#include "SCKAmbient.h"

#define DELAY_TIME_BETWEEN_POST 10*60*1000

SCKAmbient ambient;

void setup(){
    ambient.begin();
    ambient.ini();
}

void loop(){
    ambient.execute( true );
    delay( DELAY_TIME_BETWEEN_POST );
}
