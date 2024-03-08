

#define REQ_CNT_OF_TEMPSENSORS 3 // how many temperature sensors are connected

DeviceAddress addrTempSensor_RVK = {0x28,0xC5,0x60,0x94,0x97,0x0C,0x03,0x69};
DeviceAddress addrTempSensor_HLT = {0x28,0xFF,0x64,0x1F,0x76,0x6A,0x2F,0x05};
DeviceAddress addrTempSensor_SCZ = {0x28,0xFF,0x64,0x1E,0x15,0x18,0xE4,0x06};

//timers
unsigned long tmrControlLoop,tmrDataComm, tmrPrint;
//manual setpoints
float manSP_HLT_temp, manSP_RVK_temp;
//flags
bool HLT_HeatingEnabled,RVK_HeatingEnabled,HLT_PIDEnabled,RVK_PIDEnabled;
    
//communication
#define RXBUFFSIZE 20
#define RXQUEUESIZE 3
uint8_t errorCnt_dataCorrupt, errorCnt_CRCmismatch, errorCnt_BufferFull;
uint8_t rxBuffer[RXQUEUESIZE][RXBUFFSIZE];//for first item if >0 command is inside, 0 after it is proccessed
bool rxBufferMsgReady[RXQUEUESIZE];
uint8_t rxLen,crcH,crcL,readState,rxPtr,rxBufPtr=0;
uint8_t driver1Run;
/////// MACROS

#define getH(x) (uint8_t(round(x*100)/256))
#define getL(x) (uint8_t(round(x*100)%256))

#define getValue(x,y) (((long)x*256 +y)/100.0)

/////// ERRORS

#define ERROR_CODE_UNKNOWN 0
#define ERROR_CODE_HLT_SENSOR 1
#define ERROR_CODE_RVK_SENSOR 2
#define ERROR_CODE_SCZ_ENSOR 3

unsigned long errorFlags;

#define PIN_ONE_WIRE_EXT_PULLUP 29
#define PIN_ONE_WIRE_POWER 27
#define PIN_ONE_WIRE_BUS 31

#define PIN_HEAT_RVK_1 45
#define PIN_HEAT_RVK_2 43
#define PIN_HEAT_RVK_3 41

#define PIN_HEAT_HLT_1 39
#define PIN_HEAT_HLT_2 37
#define PIN_HEAT_HLT_3 35

#define PIN_DRIVER1_RUN 53
#define PIN_PUMP 51
#define PIN_RESERVE1 49
#define PIN_RESERVE2 47




// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(PIN_ONE_WIRE_BUS);

DallasTemperature oneWireSensors(&oneWire);

//U8X8_SSD1306_128X64_NONAME_HW_I2C display; //U8X8_SSD1306_128X64_NONAME_HW_I2C

typedef struct{
  float Kp,Ki,Kd;
}PID_params;


typedef struct PID_struct{
  float input, output, setpoint;
  bool active;
  PID_params params;

  //internals
  float integr_e, last_e;
  
  PID_struct(){
    params = {0.0,0.0,0.0};
    input = 0.0;
    output = 0.0;
    active = false;
  }
}PID;

typedef struct PercToDO_struct{
  float input, hysteresis;
  uint8_t out,nOfOutputs;
  bool active,out1,out2,out3;
  unsigned long tmr1,tmr2,tmr3,tmrMain;
  const unsigned int period = 10000UL;
  
  PercToDO_struct(){
    input = 0.0;
    out = 0;
    nOfOutputs = 0;
    out1 = false;
    out2 = false;
    out3 = false;
    active = false;
  }
}PercToDO;

typedef struct TempSensor_struct{
  float rawValue, value;

  //calibrations
  float calib_triplePointBath, calib_boilingPoint;
  bool error;
  uint32_t errorCode;
  
  TempSensor_struct(){
    value = 0.0;
    rawValue = 0.0;
    error = false;
    calib_triplePointBath = 0.0;
    calib_boilingPoint = 100.0;
    errorCode = ERROR_CODE_UNKNOWN;
  }
}TempSensor;

typedef struct Alternator_struct{
  bool out1,out2,out3;
  bool in1, in2, in3;
  unsigned long tmr;
  unsigned long period;
  unsigned int state;
  
  Alternator_struct(){
    out1 = false;
    out2 = false;
    out3 = false;
    in1 = false;
    in2 = false;
    in3 = false;
    tmr = 0L;
    state = 0;
    period = 60000UL;
  }
}Alternator;

//alternator for changing outputs
Alternator HLT_alternator, RVK_alternator;

//temperature sensors
TempSensor HLT_tempSensor, RVK_tempSensor, SCZ_tempSensor;
  
//blocks definitions
PID PID_temp_HLT;
PercToDO PercToDO_temp_HLT;
PID PID_temp_RVK;
PercToDO PercToDO_temp_RVK;
