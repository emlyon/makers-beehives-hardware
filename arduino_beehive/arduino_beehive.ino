//Temperature & Humidity DHT11 sensor:
//- libraries: https://github.com/adafruit/Adafruit_Sensor & https://github.com/adafruit/DHT-sensor-library
//- code: http://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/ & https://www.instructables.com/id/Arduino-DHT11-Sensor/

//Light TSL2561 sensor:
//- library: http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/: Digital Light Sensor Library
//- code: http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/ & http://www.ardumotive.com/lux-sensor-en.html

//Air quality sensor:
//- library: https://github.com/Seeed-Studio/Mutichannel_Gas_Sensor/archive/master.zip
//- code: http://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor/

//Sound sensor:
//- code: http://wiki.seeedstudio.com/Grove-Sound_Sensor/

//Format data:https://docs.google.com/spreadsheets/d/1cJRaDxrSRpd754ncW69N8Kk84PlfYFvD9PlvOZIjPls/edit#gid=0

#include "DHT.h"
#include "Wire.h"
#include "Digital_Light_TSL2561.h"
#include "MutichannelGasSensor.h"

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int sound = A0;

// Data JSON structure
static char* KEYS[9] = {
    "{\"temp\":\"",
    "\",\"hum\":\"",
    "\",\"light\":\"",
    "\",\"bat\":\"",
    "\",\"panel\":\"",
    "\",\"co\":\"",
    "\",\"no2\":\"",
    "\",\"noise\":\"",
    "\"}"
};

static char* UNITS[8] = {
    "C",
    "%",
    "Lux",
    "%",
    "mV",
    "ppm",
    "ppm",
    "dB"
};

void setup() {
  Serial.begin(115200);
  
  //Temperature & Humidity 
  dht.begin();

  //Light
  Wire.begin();
  TSL2561.init();

  // Air quality
  gas.begin(0x04);//the default I2C address of the slave is 0x04
  gas.powerOn();
}

void loop() {
    float temp = dht.readTemperature(); // temperature
    float hum = dht.readHumidity(); // humidity
    float light = TSL2561.readVisibleLux(); // light
    float bat = 100; //battery
    unsigned int panel = 0; // solar panel
    float co = gas.measure_CO(); // carbon monxide
    float no2 = gas.measure_NO2(); // nitrogen dioxide
    float dec = 0;
    long noise = 0;
    
    for(int i=0; i<32; i++){
        noise += analogRead(sound);
    }
    noise >>= 5;

    for(int i=0; i<8; i++){
        Serial.print(KEYS[i]);
        switch(i){
            case 0: // Temperature
                dec = 1;
                Serial.print(temp);
                break;
            case 1: // Humidity
                dec = 1;
                Serial.print(hum);
                break;
            case 2: // Light
                dec = 10;
                Serial.print(light);
                break;
            case 3: // Battery
                dec = 10;
                Serial.print(bat);
                break;
            case 4: // Solar Panel
                dec = 1;
                Serial.print(panel);
                break;
            case 5: // Carbon Monxide
                dec = 1000;
                Serial.print(co);
                break;
            case 6: // Nitrogen Dioxide
                dec = 1000;
                Serial.print(no2);
                break;
            case 7: // Noise
                dec = 1;
                Serial.print(noise);
                break;
        }
        Serial.print(UNITS[i]);
    }
    Serial.println(KEYS[8]);
    delay(5000);
}
