// Reading light from LDR on Energy Meter LED
// Depending on the blinking of the LED detected the charging is Restarted
// Multiple BT modes: PrintModes, ChargingModes

int energyMeterLED_LDR = D8;  // Energy Meter LED reader LDR module input pin
int chargerRelayModule = D7;  // Charger power circuit relay module output pin



// Charging status checking per sec
int energyMeterLedNoIndication = 0;   // Count when energy meter led not blinked
int chargingStopSecCnt = 0;
// int chargingStopSecLimit = 60;      // Wait for chargingStopSecLimit iterations i.e 1 min
String printMode = "Default";       // Default: Print values after chargingStopSecLimit crossed
                                    // NoDefault: Print values periodically i.e after loopDelay
String chargingMode = "Resume";     // Resume: Charging on
                                    // Stop: Charging stop

int loopDelay = 100;               // in mS

// Charging status checking per min
// bool chargingStatus = false;
int batteryPercentageCharging = 0;      // Battery Percentage while charging
int batteryPercentageInitial = 0;       // Battery percentage before charging starts
int batteryPercentageTotal = 0;         // Battery percentage total = initial + while charging
int chargingTime = 0;                   // Time (in min) for charging
int chargedTime = 0;                    // Convert initial battery percentage into charged time
int ETA = 0;

int cntChargingRestarted = 0;     // Count no of times the charging is restart

int minPercentage = 0;
int maxPercentage = 100;
int minTime = 0;
int maxTime = 270;                      // 4.5 hr to minutes

unsigned long startTime;
unsigned long currentTime;
unsigned long elapsedTime;

// int chargingStopMinCnt = 0;             // For how min chargingStatus is stopped;


bool stateEnergyMeterLED_LDR = 0; // Status of the energy meter LED read by LDR


//For Debuging
bool debug02 = 0; // For showing function names
bool debug03 = 0; // For inside function

void setup() {
  Serial.begin(9600);               // initialize serial monitor
  if(debug02) Serial.println("setup()");
  delay(1000);
  Serial.println("Initialized");

  pinMode(energyMeterLED_LDR, INPUT);
  pinMode(chargerRelayModule, OUTPUT);
  digitalWrite(chargerRelayModule, LOW);   // Start the charging

  // ConnectWifi();

  startTime = millis();
}


void loop() {
  if(debug02) Serial.println("loop()");
  delay(loopDelay);
  
  currentTime = millis();
  elapsedTime = currentTime - startTime;

  // ChargingStatusPerSec();
  EnergyMeterLedChecking();
  ReadBTInput();
  CheckChargingMode();
  
  // Checking for 1 min
  if(elapsedTime >= 60000){            
    startTime = millis();
    elapsedTime = 0;

    ChargingStatusPerMin();
    
  }
  PrintValues(); // Print values according to print mode
  // Serial.print("elapsedTime: ");
  // Serial.println(elapsedTime);
  
} 

void CheckChargingMode(){
	
  if(chargingMode == "Stop"){
    digitalWrite(chargerRelayModule, HIGH);  // Stop the charging
  }
  else{
    digitalWrite(chargerRelayModule, LOW);   // Start the charging
  }
}
void EnergyMeterLedChecking(){
  if(debug02) Serial.println("EnergyMeterLedChecking()");

  stateEnergyMeterLED_LDR = digitalRead(energyMeterLED_LDR);

  // check the state of the LED of Energy Meter through LDR Module:
  if (stateEnergyMeterLED_LDR == LOW) {
    // Energy Meter LED is on:
    // digitalWrite(LED_BUILTIN, HIGH);
    if(printMode == "NoDefault") Serial.println("Energy Meter LED ON");
    energyMeterLedNoIndication = 0;
  } else {
    // Energy Meter LED is off:
    // digitalWrite(LED_BUILTIN, LOW);
    if(printMode == "NoDefault") Serial.println("Energy Meter LED OFF");
    energyMeterLedNoIndication += 1;
  }
}

void EnergyMeterLedBlinkingStatusChecking(){
  if(debug02) Serial.println("EnergyMeterLedBlinkingStatusChecking()");
  // Considering loop delay 100 the max energyMeterLedNoIndication = 40 (i.e max 4 Sec between each blink)
  if(energyMeterLedNoIndication >= 200){
    energyMeterLedNoIndication = 0;
    RestartCharging();
  }
  
}

void RestartCharging(){
  if(debug02) Serial.println("RestartCharging()");

  Serial.println("RestartCharging");
  cntChargingRestarted += 1;
  
  digitalWrite(chargerRelayModule, HIGH);  // Stop the charging
  delay(5000);
  digitalWrite(chargerRelayModule, LOW);   // Start the charging
}

void ChargingStatusPerMin(){
  if(debug02) Serial.println("ChargingStatusPerMin()");

  // Serial.println("**ChargingStatusPerMin**");
  EnergyMeterLedBlinkingStatusChecking();
  // if(chargingStatus){
  chargingTime++;
  // }
  // else{
  //   chargingStopMinCnt++;
  // }

  batteryPercentageCharging = map(chargingTime, minTime, maxTime, minPercentage, maxPercentage);
  chargedTime = map(batteryPercentageInitial, minPercentage, maxPercentage, minTime, maxTime);


  ETA = maxTime - (chargingTime + chargedTime);
  batteryPercentageTotal = batteryPercentageInitial + batteryPercentageCharging;

  if(batteryPercentageTotal >= 95){
    chargingMode = "Stop";
    PrintValuesSummary();
  }

  
  // Checking for 10% increment in batteryPercentageCharging
  if(batteryPercentageTotal % 10 == 0 && batteryPercentageTotal != 0){
    PrintValuesSummary();
  }
  // PrintValues();

}

// Read BT input from serial comm pins
void ReadBTInput(){
  if(debug02) Serial.println("ReadBTInput()");

  // Serial.println("*ReadBTInput*");
  if (Serial.available() > 0){
    // Serial.println("*Serial.available()*");
    String bt_in = Serial.readStringUntil('\n');
    // Serial.print("bt_in: ");
    // Serial.println(bt_in);
    bt_in.remove(bt_in.length() - 1);
    String bt_in_processed = bt_in;
    Serial.print("bt_in_processed: ");
    Serial.println(bt_in_processed);
    
    // char bt_in = Serial.read();
    if(bt_in == "N"){
      printMode = "NoDefault";
      Serial.println("printMode: NoDefault");
    }
    else if(bt_in == "D"){
      printMode = "Default";
      Serial.println("printMode: Default");
    }
    else if(bt_in == "S"){
      chargingMode = "Stop";
      Serial.println("chargingMode: Stop");
    }
    else if(bt_in == "R"){
      chargingMode = "Resume";
      Serial.println("chargingMode: Resume");
    }
    else{
      batteryPercentageInitial = bt_in.toInt();
      // chargingTime = map(batteryPercentageCharging, minPercentage, maxPercentage, minTime, maxTime);
      Serial.print("batteryPercentageCharging: ");
      Serial.print(batteryPercentageCharging);
      // Serial.print(" :chargingTime: ");
      // Serial.println(chargingTime);
    }
  }
}

// Print Values according to the print Mode
void PrintValues(){
  if(debug02) Serial.println("PrintValues()");

  if(printMode == "NoDefault"){
    // PrintValuesDetailNoAwsCalling();
    PrintValuesDetail();
  }
}
void PrintWarning(){
  if(debug02) Serial.println("PrintWarning()");

  Serial.print("Warning:: ");
  PrintValuesSummary();
}
void PrintValuesSummary(){
  if(debug02) Serial.println("PrintValuesSummary()");

  Serial.print("%: ");
  Serial.print(batteryPercentageTotal);
  Serial.print(" :ETA:");
  Serial.print(ETA);
  Serial.println("");
}


void PrintValuesDetail(){
  if(debug02) Serial.println("PrintValuesDetail()");

  String message = "";  // Initialize an empty string to store the message

  message += "OnMin:";
  message += String(chargingTime);  
  message += " :energyMeterLedNoIndication:";
  message += String(energyMeterLedNoIndication);  
  message += " :cntChargingRestarted:";
  message += String(cntChargingRestarted);  
  message += " :chargingMode:";
  message += String(chargingMode);  
  
  message += " :%25I:"; // %25 => % in url parameter
  message += String(batteryPercentageInitial);
  message += ":%25C:";
  message += String(batteryPercentageCharging);
  message += ":%25T:";
  message += String(batteryPercentageTotal);
  message += " :ETA:";
  message += String(ETA);

  Serial.println(message);

}
