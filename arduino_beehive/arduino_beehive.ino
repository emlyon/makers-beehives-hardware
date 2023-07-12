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

#include <Dictionary.h>
#include <DictionaryDeclarations.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define SOUND_PIN A0

DHT dht(DHTPIN, DHTTYPE);

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 4;
HX711 scale;

Dictionary *data;
Dictionary *units;
Dictionary *error_device;

float calibration_factor = -22000.0; // in kg

void setup()
{
    // General init
    Serial.begin(115200);
    Wire.begin();

    data = new Dictionary();
    units = new Dictionary();
    error_device = new Dictionary();

    units->insert("temperature", "°C");
    units->insert("humidity", "%");
    units->insert("light", "lux");
    units->insert("co", "ppm");
    units->insert("no2", "ppm");
    // The actual unit is not dB
    // It is proportional to the sound intensity on a 1024 scale.
    units->insert("noise", "dB");
    units->insert("weight", "kg");

    // Check if all devices are available and ready

    // Sound sendor
    // nothing to do
    Serial.println("Sound sensor is ready");

    // Temperature & Humidity
    dht.begin();
    if (dht.isReady() == false)
        Serial.println("ERROR, DHT not found");
    else
        Serial.println("DHT is ready");

    // Light
    TSL2561.init();
    if (TSL2561.isReady() == false)
        Serial.println("ERROR, TSL2561 not found");
    else
        Serial.println("TSL2561 is ready");

    // Air quality
    gas.begin(0x04); // the default I2C address of the slave is 0x04
    if (gas.isReady() == false)
        Serial.println("ERROR, gas sensor not found");
    else
    {
        gas.powerOn();
        Serial.println("Gas sensor is ready");
    }

    // Scale
    scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
    delay(50);
    if (scale.wait_ready_retry(10, 50) == false)
        Serial.println("ERROR, scale not found");
    else
        Serial.println("Scale is ready");

    scale.set_scale(calibration_factor); // This parameter needs to be adjusted for your weight sensors. Look at the library documentation to find how to calculate it.
                                         // scale.tare(); //no tare absolute weight used
    Serial.println("Arduino setup is complete.");
}

void loop()
{

    String sCALIB = "CALIB\n";
    String sDATA = "DATA?\n";

    // Wait for serial input
    while (Serial.available() <= 0)
        delay(10);
    String incomingString = Serial.readString();

    // Data request
    if (incomingString == sDATA)
    {
        float temp = 0.0;
        float hum = 0.0;
        float light = 0.0;
        float co = 0.0;
        float no2 = 0.0;
        float weight = 0.0;
        int noise = 0;

        // If sensor is ready, add reading to the data dictionnary
        // Else, add the sensor to the error_device dictionnary

        if (dht.isReady())
        {
            temp = dht.readTemperature(); // temperature
            hum = dht.readHumidity();     // humidity
            data->insert("temperature", String(temp, 1));
            data->insert("humidity", String(hum, 2));
        }
        else
        {
            error_device->insert("temperature", "true");
            error_device->insert("humidity", "true");
        }

        if (TSL2561.isReady())
        {
            light = TSL2561.readVisibleLux(); // light
            data->insert("light", String(light, 0));
        }
        else
        {
            error_device->insert("light", "true");
        }

        if (gas.isReady())
        {
            co = gas.measure_CO();   // carbon monxide
            no2 = gas.measure_NO2(); // nitrogen dioxide
            data->insert("co", String(co, 3));
            data->insert("no2", String(no2, 3));
        }
        else
        {
            error_device->insert("co", "true");
            error_device->insert("no2", "true");
        }

        if (scale.wait_ready_retry(10, 50) != false)
        {
            weight = scale.get_units(5);
            data->insert("weight", String(weight, 1));
        }
        else
        {
            error_device->insert("weight", "true");
        }

        for (int i = 0; i < 32; i++)
        {
            noise += analogRead(SOUND_PIN);
        }
        noise >>= 5;
        data->insert("noise", String(noise));

        // Print data in JSON format
        // Open JSON
        Serial.print("{");
        int nbData = data->count();
        int nbError = error_device->count();

        // Add an error key if there is at least one error
        if (nbError > 0)
        {
            Serial.print("\"error\" : \"");
            for (int i = 0; i < nbError; i++)
            {
                // Device errors are separated by a comma
                Serial.print(error_device->key(i));
                if (i + 1 < nbError)
                    Serial.print(",");
            }
            Serial.print("\",");
        }

        for (int i = 0; i < nbData; i++)
        {
            // For each data, print the key, the value and the unit
            Serial.print("\"");
            Serial.print(data->key(i));
            Serial.print("\" : \"");
            Serial.print(data->search(data->key(i)));
            Serial.print(units->search(data->key(i)));

            Serial.print("\"");
            if (i + 1 < nbData)
                Serial.print(",");
        }
        // Close JSON
        Serial.println("}");
    }
    // Calibration request
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
                else if (temp == 'p')
                    calibration_factor += 250;
                else if (temp == '-' || temp == 'z')
                    calibration_factor -= 10;
                else if (temp == 'q')
                    exit_calibration_loop = true;
                else if (temp == 'm')
                    calibration_factor -= 250;
            }
            delay(500);
        }
    }
    else
    {
        Serial.println("Error, try again");
        Serial.println(incomingString);
    }

    delay(10);
}
