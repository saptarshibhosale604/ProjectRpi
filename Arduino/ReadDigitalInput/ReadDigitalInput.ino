int energyMeterLED_LDR = D8;  // Energy Meter LED reader LDR module input pin
bool stateEnergyMeterLED_LDR = 0;


void setup() {
  Serial.begin(9600);               // initialize serial monitor
  delay(1000);
  Serial.println("Initialized");

  pinMode(energyMeterLED_LDR, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  stateEnergyMeterLED_LDR = digitalRead(energyMeterLED_LDR);

  Serial.println(stateEnergyMeterLED_LDR);

}
