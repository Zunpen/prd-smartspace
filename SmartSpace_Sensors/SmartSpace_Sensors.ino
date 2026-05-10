#include <DHT.h>

const int TRIG_PIN  = 9;   
const int ECHO_PIN  = 10;  
const int DHT_PIN   = 2;  
#define DHT_TYPE DHT11


const int BIN_EMPTY_CM = 30;
const int BIN_FULL_CM  = 3;

DHT dht(DHT_PIN, DHT_TYPE);

long duration;
int  distanceCm;
float temperature;
float humidity;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  dht.begin();
  Serial.println("SMARTSPACE_READY");
  delay(2000); 
}

void loop() {
  // Read Ultrasonic
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration    = pulseIn(ECHO_PIN, HIGH);
  distanceCm  = duration * 0.034 / 2;

  // Convert distance to fill percentage
  int fillPercent = 0;
  if (distanceCm <= BIN_FULL_CM) {
    fillPercent = 100;
  } else if (distanceCm >= BIN_EMPTY_CM) {
    fillPercent = 0;
  } else {
    fillPercent = map(distanceCm, BIN_EMPTY_CM, BIN_FULL_CM, 0, 100);
  }

  // Read DHT11 
  temperature = dht.readTemperature();   // Celsius
  humidity    = dht.readHumidity();

  // Output as CSV on Serial (Python will parse this) 
  // Format: DATA,<fill_percent>,<temperature>,<humidity>
  if (isnan(temperature) || isnan(humidity)) {
    // DHT read failed, still send trash data with error flag
    Serial.print("DATA,");
    Serial.print(fillPercent);
    Serial.println(",ERR,ERR");
  } else {
    Serial.print("DATA,");
    Serial.print(fillPercent);
    Serial.print(",");
    Serial.print(temperature, 1);
    Serial.print(",");
    Serial.println(humidity, 1);
  }

  delay(2000); // send every 2 seconds
}
