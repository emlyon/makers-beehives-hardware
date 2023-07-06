// Temperature & Humidity DHT11 sensor:
//- libraries: https://github.com/adafruit/Adafruit_Sensor & https://github.com/adafruit/DHT-sensor-library
//- code: http://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/ & https://www.instructables.com/id/Arduino-DHT11-Sensor/

// Light TSL2561 sensor:
//- library: http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/: Digital Light Sensor Library
//- code: http://wiki.seeedstudio.com/Grove-Digital_Light_Sensor/ & http://www.ardumotive.com/lux-sensor-en.html

// Air quality sensor:
//- library: https://github.com/Seeed-Studio/Mutichannel_Gas_Sensor/archive/master.zip
//- code: http://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor/

// Sound sensor:
//- code: http://wiki.seeedstudio.com/Grove-Sound_Sensor/

// Format data:https://docs.google.com/spreadsheets/d/1cJRaDxrSRpd754ncW69N8Kk84PlfYFvD9PlvOZIjPls/edit#gid=0

// Weight Sensor
// https://github.com/bogde/HX711

#include "DHT.h"
#include "Wire.h"
#include "Digital_Light_TSL2561.h"
#include "MutichannelGasSensor.h"
#include "HX711.h"

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int sound = A0;

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 4;
HX711 scale;

// Data JSON structure
static const char *KEYS[10] = {
    "{\"temperature\":",
    ",\"humidity\":",
    ",\"light\":",
    ",\"co\":",
    ",\"no2\":",
    ",\"noise\":",
    ",\"weight\":",
    "}"};

static const char *UNITS[10] = {
    "C",
    "%",
    "Lux",
    "ppm",
    "ppm",
    "dB",
    "Kg"};

float calibration_factor = -5000; // in kg

void setup()
{
    // General init
    Serial.begin(115200);
    Wire.begin();

    // Temperature & Humidity
    dht.begin();

    // Light
    TSL2561.init();

    // Air quality
    gas.begin(0x04); // the default I2C address of the slave is 0x04
    gas.powerOn();

    // Scale
    scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
    scale.set_scale(-23436.0f); // This parameter needs to be adjusted for your weight sensors. Look at the library documentation to find how to calculate it.
                                // scale.tare(); //no tare absolute weight used
}

void loop()
{

    float temp = dht.readTemperature();     // temperature
    float hum = dht.readHumidity();         // humidity
    float light = TSL2561.readVisibleLux(); // light
    float bat = 100;                        // battery
    unsigned int panel = 0;                 // solar panel
    float co = gas.measure_CO();            // carbon monxide
    float no2 = gas.measure_NO2();          // nitrogen dioxide
    long noise = 0;
    float weight = scale.get_units(5);

    for (int i = 0; i < 32; i++)
    {
        noise += analogRead(sound);
    }
    noise >>= 5;

    while (Serial.available() <= 0)
    {
        delay(100);
    }

    String sCALIB = "CALIB\n";
    String sDATA = "DATA?\n";

    String incomingString = Serial.readString();
    // Serial.println(incomingString);
    //   ser.write(unicode("DATA?\n")) in pyton script file
    if (incomingString == sDATA)
    {
        for (int i = 0; i < 7; i++)
        {
            Serial.print(KEYS[i]);
            switch (i)
            {
            case 0: // Temperature
                Serial.print("\"" + String(temp));
                break;
            case 1: // Humidity
                Serial.print("\"" + String(hum));
                break;
            case 2: // Light
                Serial.print("\"" + String(light));
                break;
            case 3: // Carbon Monxide
                Serial.print("\"" + String(co));
                break;
            case 4: // Nitrogen Dioxide
                Serial.print("\"" + String(no2));
                break;
            case 5: // Noise
                Serial.print("\"" + String(noise));
                break;
            case 6: // Weight
                Serial.print("\"" + String(weight));
                break;
            default:
                break;
            }
            Serial.print(String(UNITS[i]) + "\"");
        }
        Serial.println(KEYS[7]);
    }
    else if (incomingString == sCALIB)
    {

        scale.set_scale();
        scale.tare(); // Reset the scale to 0

        long zero_factor = scale.read_average(); // Get a baseline reading
        Serial.print("Zero factor: ");           // This can be used to remove the need to tare the scale. Useful in permanent scale projects.
        Serial.println(zero_factor);

        boolean exit_calibration_loop = false;
        while (exit_calibration_loop == false)
        {
            scale.set_scale(calibration_factor); // Adjust to this calibration factor

            Serial.print("Reading: ");
            Serial.print(scale.get_units(10), 1);
            // Serial.print(scale.read());
            Serial.print(" kg"); // Change this to kg and re-adjust the calibration factor if you follow SI units like a sane person
            Serial.print(" calibration_factor: ");
            Serial.print(calibration_factor);
            Serial.println();

            if (Serial.available())
            {
                char temp = Serial.read();
                if (temp == '+' || temp == 'a')
                    calibration_factor += 10;
                else if (temp == '-' || temp == 'z')
                    calibration_factor -= 10;
                else if (temp == 'q')
                    exit_calibration_loop = true;
            }
            delay(500);
        }
    }
    else
    {
        Serial.println("Error, try again");
    }
    delay(5000);
}