#include <SPI.h>
#include <EEPROM.h>
#include <DAC_MCP49xx.h>

// Reference voltage measured from device
#define Vref 4881
// Vsense1 ratio
#define VDRP 4950

// Maximum deviation
#define MaxDev 100
// Acceptable deviation
#define PDev 20

#define AC_2 12
#define AC_1 10
#define DAC_P 9
#define OE_P 8
#define DAC_N 7
#define OE_N 6
#define ITE 5
#define AC_3 4
#define AC_4 3
#define TS1 2

#define Vsense_P 0
#define Vsense_N 1
#define Asense_P 2
#define Asense_N 3

int setVP = 5000;
int setAP = 0;
int setVN = -5000;
int setAN = 0;

int dacValP = 0;
int dacValN = 0;

bool limitingP = false;
bool limitingN = false;

bool vlockP = false;
bool vlockN = false;

bool vresetP = false;
bool vresetN = false;

byte stateOEP = 0;
byte stateOEN = 0;
byte stateITE = 0;
byte stateAC1 = 0;
byte stateAC2 = 0;
byte stateAC3 = 0;
byte stateAC4 = 0;

long vSenseP = 0;
long aSenseP = 0;
long vSenseN = 0;
long aSenseN = 0;

int offsetP = 320;
int offsetN = 200;

unsigned long previousMillis = 0;
const long interval = 1;

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

void EEPROMWriteInt(int addr, int p_value) {
  EEPROM.write(addr, ((p_value >> 0) & 0xFF));
  EEPROM.write(addr + 1, ((p_value >> 8) & 0xFF));
}

unsigned int EEPROMReadInt(int addr) {
  byte lowByte = EEPROM.read(addr);
  byte highByte = EEPROM.read(addr + 1);
  return ((lowByte << 0) & 0xFF) + ((highByte << 8) & 0xFF00);
}

void readEEPROM() {
  stateOEP = readAddress(0);
  digitalWrite(OE_P, !stateOEP);
  stateOEN = readAddress(1);
  digitalWrite(OE_N, !stateOEN);
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
  offsetP = EEPROMReadInt(7);
  offsetN = EEPROMReadInt(9);
}

void writeEEPROM() {
  // Remove these later XXX - we should never boot with the outputs enabled.
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

  Serial.begin(57600);

  pinMode(OE_P, OUTPUT);
  pinMode(OE_N, OUTPUT);
  pinMode(ITE, OUTPUT);
  pinMode(AC_1, OUTPUT);
  pinMode(AC_2, OUTPUT);
  pinMode(AC_3, OUTPUT);
  pinMode(AC_4, OUTPUT);

  readEEPROM();
  dacValP = 200;
  PosDac.output(dacValP);
  NegDac.output(1024);
  Serial.println("PSUOS 1.0 READY");
}

void setPin(int pin, int param) {
  if (param == 0) {
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
  dacValP = (4095.0 / 20000.0) * setVP;
  setPin(OE_P, LOW);
  PosDac.output(dacValP);
  delay(5); // Wait for DAC to settle a bit
  updateReadings();
  // Allow recalibration
  vlockP = false;
  // Wait for vlock before setting OE_P to desired state
  vresetP = true;
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
  dacValN = (4095.0 / 20000.0) * -1 * setVN;
  setPin(OE_N, LOW);
  NegDac.output(dacValN);
  delay(5); // Wait for DAC to settle a bit
  updateReadings();
  // Allow recalibration
  vlockN = false;
  // Wait for vlock before setting OE_P to desired state
  vresetN = true;
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
          Serial.println("ACK");
          break;

        case 21:
          // Diagnostic function - set DAC2
          NegDac.output(param);
          Serial.println("ACK");
          break;

        case 22:
          // Diagnostic function - raw ADC voltages
          {
            int vsp = analogRead(Vsense_P);
            int vsn = analogRead(Vsense_N);
            int asp = analogRead(Asense_P);
            int asn = analogRead(Asense_N);
            Serial.println(String("ADC:") + vsp + ", " + vsn + ", " + asp + ", " + asn);
          }
          break;

        case 23:
          // Diagnostic function - change offset calibration
          offsetP = param;
          EEPROMWriteInt(7, offsetP);
          Serial.println("ACK");
          break;

        case 24:
          // Diagnostic function - change negative offset calibration
          offsetN = param;
          EEPROMWriteInt(9, offsetN);
          Serial.println("ACK");
          break;
      }
    }
  }
}

long analogReadV(int samples, int adc) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(adc);
  }
  return ((sum / samples) * Vref) / 1000;
}

void updateReadings() {
  long cval = 0;

  // Read positive voltage
  vSenseP = (analogReadV(10, Vsense_P) * (VDRP + offsetP)) / 1000;

  // Read negative voltage
  vSenseN = (((Vref / 2) - offsetN) - analogReadV(10, Vsense_N)) * -10;

  // Read positive current
  cval =  analogReadV(10, Asense_P) - 2500;
  if (cval >= 0) {
    aSenseP = (cval * 1000) / 185;
  }

  // Read negative current
  cval =  analogReadV(10, Asense_N) - 2500;
  if (cval > 0) {
    aSenseN = (cval * 1000) / 185;
  }
}

void tick() {
  // Async clock loopf
  updateReadings();

  // Set DACS
  if (!limitingP) {
    if (vlockP) {
      // If we drift more than 150mv then readjust
      if ((vSenseP > (setVP + MaxDev)) || (vSenseP < (setVP - MaxDev))) {
        vlockP = false;
      }
    } else {
      // Adjust voltage within 20mv
      if (vSenseP > (setVP + PDev)) {
        dacValP--;
        PosDac.output(dacValP);
      }
      else if (vSenseP < (setVP - PDev)) {
        dacValP++;
        PosDac.output(dacValP);
      }
      else {
        // Lock DAC value when reading is within spec
        vlockP = true;
        if (vresetP) {
          vresetP = false;
          setPin(OE_P, stateOEP);
        }
      }
    }
  }
  if (!limitingN) {
    if (vlockN) {
      if ((vSenseN > (setVN - MaxDev)) || (vSenseN < (setVN + MaxDev))) {
        vlockN = false;
      }
    }
    else {
      // Adjust to within 20mv
      if (vSenseN > (setVN + PDev)) {
        dacValN++;
        NegDac.output(dacValN);
      }
      else if (vSenseN < (setVN - PDev)) {
        dacValN--;
        NegDac.output(dacValN);
      }
      else {
        // Lock DAC changes
        vlockN = true;
        if (vresetN) {
          vresetN = false;
          setPin(OE_N, stateOEN);
        }
      }
    }
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

