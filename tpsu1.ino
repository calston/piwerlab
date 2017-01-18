#include <SPI.h>
#include <EEPROM.h>
#include <DAC_MCP49xx.h>

#define DAC_P 9
#define OE_P 8
#define DAC_N 7
#define OE_N 6
#define ITE 5

#define AC_1 10
#define AC_2 12
#define AC_3 4
#define AC_4 3

#define Vsense_P 0
#define Vsense_N 1
#define Asense_P 2
#define Asense_N 3

int setVP = 0;
int setAP = 0;
int setVN = 0;
int setAN = 0;

int dacValP = 0;
int dacValN = 0;

byte stateOEP = 0;
byte stateOEN = 0;
byte stateITE = 0;
byte stateAC1 = 0;
byte stateAC2 = 0;
byte stateAC3 = 0;
byte stateAC4 = 0;

int vSenseP = 0;
int aSenseP = 0;
int vSenseN = 0;
int aSenseN = 0;

unsigned long previousMillis = 0;
const long interval = 200;

DAC_MCP49xx PosDac(DAC_MCP49xx::MCP4921, DAC_P);
DAC_MCP49xx NegDac(DAC_MCP49xx::MCP4921, DAC_N);

int readAddress(int addr) {
  byte value = EEPROM.read(addr);
  if (value >= 0 && value <= 1) {
    return int(value);
  } else {
    return 0;
  }
}

void readEEPROM() {
  stateOEP = readAddress(0);
  digitalWrite(OE_P, stateOEP);
  stateOEN = readAddress(1);
  digitalWrite(OE_N, stateOEN);
  stateITE = readAddress(2);
  digitalWrite(ITE, stateITE);
  stateAC1 = readAddress(3);
  digitalWrite(AC_1, stateAC1);
  stateAC2 = readAddress(4);
  digitalWrite(AC_2, stateAC2);
  stateAC3 = readAddress(5);
  digitalWrite(AC_3, stateAC3);
  stateAC4 = readAddress(6);
  digitalWrite(AC_4, stateAC4);
}

void writeEEPROM() {
  EEPROM.write(0, stateOEP);
  EEPROM.write(1, stateOEN);
  EEPROM.write(2, stateITE);
  EEPROM.write(3, stateAC1);
  EEPROM.write(4, stateAC2);
  EEPROM.write(5, stateAC3);
  EEPROM.write(6, stateAC4);
}

void setup() {
   PosDac.setSPIDivider(SPI_CLOCK_DIV16);
   NegDac.setSPIDivider(SPI_CLOCK_DIV16);

   Serial.begin(9600);

   pinMode(OE_P, OUTPUT);
   pinMode(OE_N, OUTPUT);
   pinMode(ITE, OUTPUT);
   pinMode(AC_1, OUTPUT);
   pinMode(AC_2, OUTPUT);
   pinMode(AC_3, OUTPUT);
   pinMode(AC_4, OUTPUT);

   readEEPROM();

   Serial.println("PSUOS 1.0 READY");
}

void setPin(int pin, int param) {
  if (param==0){
    digitalWrite(pin, LOW);
  } else {
    digitalWrite(pin, HIGH);
  }
  Serial.println("ACK");
}

void setAC(int param, int val) {
  switch (param) {
    case 1:
      digitalWrite(AC_1, val);
      stateAC1 = val;
      writeEEPROM();
      break;
    case 2:
      digitalWrite(AC_2, val);
      stateAC2 = val;
      writeEEPROM();
      break;
    case 3:
      digitalWrite(AC_3, val);
      stateAC3 = val;
      writeEEPROM();
      break;
    case 4:
      digitalWrite(AC_4, val);
      stateAC4 = val;
      writeEEPROM();
      break;
  }
  Serial.println("ACK");
}

void setV_P(int param) {
  // Set positive voltage
  setVP = param;
  Serial.println("ACK");
}

void setA_P(int param) {
  // Set positive current
  setAP = param;
  Serial.println("ACK");
}

void setV_N(int param) {
  // Set negative voltage
  setVN = param;
  Serial.println("ACK");
}

void setA_N(int param) {
  // Set negative current
  setAN = param;
  Serial.println("ACK");
}

void getVals(int param) {
  Serial.println(String("V:") + vSenseP + "," + vSenseN +
                 " A:" + aSenseP + "," + aSenseN +
                 " S:" + setVP + "," + setVN + "," + setAP + "," + setAN +
                 " R:" + stateITE + "," + stateOEP + "," + stateOEN + "," +
                 stateAC1 + "," + stateAC2 + "," + stateAC3 + "," + stateAC4);
}

void checkSerial() {
  while (Serial.available() > 0) {
    int cmd = Serial.parseInt();
    int param = Serial.parseInt();
    if (Serial.read() == '\n') {
      switch (cmd) {
        case 1:
          // Toggle regulator input transformer
          setPin(ITE, param);
          stateITE = param;
          writeEEPROM();
          break;
        case 2:
          // Toggle positive output
          setPin(OE_P, param);
          stateOEP = param;
          writeEEPROM();
          break;
        case 3:
          // Toggle negative output
          setPin(OE_N, param);
          stateOEN = param;
          writeEEPROM();
          break;
        case 4:
          // Set positive voltage
          setV_P(param);
          break;
        case 5:
          // Set positive current
          setA_P(param);
          break;
        case 6:
          // Set negative voltage
          setV_N(param);
          break;
        case 7:
          // Set negative current
          setA_N(param);
          break;
        case 8:
          // Get current readings and settings
          getVals(param);
          break;
        case 9:
          // Turn on AC plug
          setAC(param, HIGH);
          break;
        case 10:
          // Turn off AC plug
          setAC(param, LOW);
          break;
        case 20:
          // Diagnostic function - set DAC1
          PosDac.output(param);
          break;
        case 21:
          // Diagnostic function - set DAC2
          NegDac.output(param);
          break;
      }
    }
  }
}

void tick() {
  // Async clock loopf
  long adcVal = 0;
  int cval = 0;

  // Read positive voltage
  adcVal = (long(analogRead(Vsense_P)) * 4 * 5545)/1000;
  vSenseP = adcVal;

  // Read negative voltage
  // Gets a bit complicated now... 
  // RX = 0.819672131147541
  // ((vout * 1.8) - 5*RX)/(-1*RX + 1) = Vin
  // Simplified down to.. 
  adcVal = (10 * (long(analogRead(Vsense_N)) * 4)) - 22727;
  vSenseN = adcVal;f

  // Read positive current
  adcVal = analogRead(Asense_P);
  cval =  (adcVal * 4) - 2500;
  if (cval >= 0) {
    aSenseP = (cval * 1000) / 185;
  }
  
  // Read negative current
  adcVal = analogRead(Asense_P);
  cval =  (adcVal * 4) - 2500;
  if (cval > 0) {
    aSenseN = (cval * 1000) / 185;
  }

  // Set DACS
  if (vSenseP != setVP) {
    
  }
}

void loop() {
  checkSerial();
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    tick();
  }
}
