
void setup(){

  Serial.begin(9600);

  Serial.println(F("Program start"));

  
  //setup onewire temperature sensors
  oneWireSensors.begin();

  pinMode(PIN_HEAT_HLT_1, OUTPUT);
  pinMode(PIN_HEAT_HLT_2, OUTPUT);
  pinMode(PIN_HEAT_HLT_3, OUTPUT);

  pinMode(PIN_HEAT_RVK_1, OUTPUT);
  pinMode(PIN_HEAT_RVK_2, OUTPUT);
  pinMode(PIN_HEAT_RVK_3, OUTPUT);
  
  pinMode(PIN_LEDNICE, OUTPUT);
      

  // LCD
  //for ESP: D1-SCL; D2-SDA
  // for ESP display.begin(SSD1306_SWITCHCAPVCC, 0x3C);  // initialize with the I2C addr 0x3D (for the 128x64)
/*  if(display.begin()){
    
    // Clear the buffer.
    display.clearDisplay();
    display.setFont(u8x8_font_chroma48medium8_r);
  }*/
  //Serial.println(F("Setup finished"));

  OneWireDevicesPrintAddr(); // to find address of dallas temperature sensors


  SetPIDParams();

  //error entanglement
  HLT_tempSensor.errorCode = ERROR_CODE_HLT_SENSOR;
  RVK_tempSensor.errorCode = ERROR_CODE_RVK_SENSOR;
  SCZ_tempSensor.errorCode = ERROR_CODE_SCZ_ENSOR;

  HLT_tempSensor.calib_triplePointBath = 0.1;
  HLT_tempSensor.calib_boilingPoint = 100.0;
  RVK_tempSensor.calib_triplePointBath = 0.7;
  RVK_tempSensor.calib_boilingPoint = 100.0;
  SCZ_tempSensor.calib_triplePointBath = 0.3;
  SCZ_tempSensor.calib_boilingPoint = 100.0;
  
  
  HLT_alternator.period = 300000UL;//HLT alternate each 5mins 
}

void SetPIDParams(){
  PID_temp_HLT.params.Kp = 15.0;
  PID_temp_HLT.params.Ki = 0.05;
  PID_temp_HLT.params.Kd = 0.0;

  PercToDO_temp_HLT.hysteresis = 2.0;
  PercToDO_temp_HLT.nOfOutputs = 3;


  PID_temp_RVK.params.Kp = 15.0;
  PID_temp_RVK.params.Ki = 0.05;
  PID_temp_RVK.params.Kd = 0.0;

  PercToDO_temp_RVK.hysteresis = 2.0;
  PercToDO_temp_RVK.nOfOutputs = 3;
}
