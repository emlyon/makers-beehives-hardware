#include <avr/sleep.h>

#define awakeMinute 5
#define sleepMinute 60
#define ONE_SEC 1000

void setup() {
  pinMode( 4, OUTPUT );
  ADCSRA &= ~(1 << ADEN);//Disable ADC, saves ~230uA
  
  setup_watchdog(6);
}

void loop() {
  digitalWrite( 4, LOW );
  for ( int minute = 0; minute < awakeMinute; minute ++ ) {
    for ( int seconde = 0; seconde < 60; seconde ++ ) {
      sleep_mode();
    }
  }
  
  digitalWrite( 4, HIGH );
  for ( int minute = 0; minute < sleepMinute; minute ++ ) {
    for ( int seconde = 0; seconde < 60; seconde ++ ) {
      sleep_mode();
    }
  }
}

// 0=16ms, 1=32ms, 2=64ms, 3=128ms, 4=250ms, 5=500ms
// 6=1sec, 7=2sec, 8=4sec, 9=8sec
// From: http://interface.khm.de/index.php/lab/experiments/sleep_watchdog_battery/
void setup_watchdog(int timerPrescaler) {

  if (timerPrescaler > 9 ) timerPrescaler = 9; //Correct incoming amount if need be

  byte bb = timerPrescaler & 7;
  if (timerPrescaler > 7) bb |= (1 << 5); //Set the special 5th bit if necessary

  //This order of commands is important and cannot be combined
  MCUSR &= ~(1 << WDRF); //Clear the watch dog reset
  WDTCR |= (1 << WDCE) | (1 << WDE); //Set WD_change enable, set WD enable
  WDTCR = bb; //Set new watchdog timeout value
  WDTCR |= _BV(WDIE); //Set the interrupt enable, this will keep unit from resetting after each int
}
