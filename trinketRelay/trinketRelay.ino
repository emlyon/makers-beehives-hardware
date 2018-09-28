/*
Trinket ----> Relay
     5V ----> VCC
    GND ----> GND
     #4 ----> IN
     
Le relais s'allume quand le pin 4 est sur LOW
*/
void setup() {
  pinMode( 4, OUTPUT );
}

void loop() {
  digitalWrite( 4, HIGH );
  delay( 3300000 );
  digitalWrite( 4, LOW );
  delay( 300000 );
}
