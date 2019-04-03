/*
  Based on rocketscream/Low-Power library: https://github.com/rocketscream/Low-Power

  Trinket Pro 5v ----> Relay
              5V ----> VCC
             GND ----> GND
              #4 ----> IN

  Relay turns ON when pin 4 is LOW
*/
#include <LowPower.h>

#define awakeTime 5
#define sleepTime 55

void setup() {
  pinMode(4, OUTPUT);
}

void loop() {
  digitalWrite(4, LOW);
  sleep(awakeTime);

  digitalWrite(4, HIGH);
  sleep(sleepTime);
}

void sleep(int minutes) {
  for (int minute = 0; minute < minutes; minute ++) {
    for (int seconde = 0; seconde < 60; seconde += 8) {
      LowPower.idle(SLEEP_8S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF, SPI_OFF, USART0_OFF, TWI_OFF);
    }
  }
}
