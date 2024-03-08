//function for creating periodic block code
//returns true if period has passed, resetting the timer
bool CheckTimer(unsigned long &timer, const unsigned long period){
   if((unsigned long)(millis() - timer) >= period){//protected from rollover by type conversion
    timer = millis();
    return true;
   }else{
    return false;
   }
}
void ResetTimer(unsigned long &timer){
  timer = millis();
}
// function to print a device address
void PrintAddress(DeviceAddress deviceAddress) {
  for (uint8_t i = 0; i < 8; i++) {
    if (deviceAddress[i] < 16) Serial.print("0");
      Serial.print(deviceAddress[i], HEX);
  }
}

void OneWireDevicesPrintAddr(){
  Serial.println(F("Scanning started"));
  int oneWireDeviceCnt = oneWireSensors.getDeviceCount();

  DeviceAddress tempDeviceAddress;
  for(int i=0;i<oneWireDeviceCnt; i++) {
    // Search the wire for address
    if(oneWireSensors.getAddress(tempDeviceAddress, i)) {
      Serial.print("Found device with address: ");
      PrintAddress(tempDeviceAddress);
      Serial.println();
    } else {
      Serial.print("Found ghost device at ");
      Serial.print(i, DEC);
      Serial.print(" but could not detect address. Check power and cabling");
    }
  }
}

bool ReadTemperature(DeviceAddress address, TempSensor *tempS){

  if(tempS == NULL) return false;
  float tempC = oneWireSensors.getTempC(address);
  if(tempC==-127){
    errorFlags |= 1UL << tempS->errorCode;
    tempS->error = true;
    tempS->rawValue = 0.0;
    tempS->value = 0.0;
    return false;
  }else{
    errorFlags &= ~(1UL << tempS->errorCode);
    tempS->error = true;
    tempS->rawValue = tempC;
    tempS->value = CalibrateTemp(tempS->rawValue, tempS->calib_triplePointBath, tempS->calib_boilingPoint);
    return true;
  }
}

bool ReadTemperatures(){
  bool res = true;
  int cnt = oneWireSensors.getDeviceCount();
  //check if all sensors are connected
  if(cnt != REQ_CNT_OF_TEMPSENSORS){
    oneWireSensors.begin();//try to scan
    if(cnt != oneWireSensors.getDeviceCount())//if not success, return false
      res = false;
  }

  oneWireSensors.requestTemperatures();

  bool res1 = ReadTemperature(addrTempSensor_HLT, &HLT_tempSensor);
  bool res2 = ReadTemperature(addrTempSensor_RVK, &RVK_tempSensor);
  bool res3 = ReadTemperature(addrTempSensor_SCZ, &SCZ_tempSensor);

  //temp_HLT_      = CalibrateTemp(temp_HLT_,0.4,97.1);
  //temp_RVK_ = CalibrateTemp(temp_RVK_,0.7,98.8);//not calibrated yet
  //temp_scezovaciKad = CalibrateTemp(temp_scezovaciKad,0.7,98.8);
  //temp_mrazak         = CalibrateTemp(temp_mrazak,0.0,96.0);
  
  return res&&res1&&res2&&res3;
}

float CalibrateTemp(float raw, float triplePointBath, float boilingPoint){
  //boiling point 99.2°C for 254 m.n.m
  const float ref_boilingPoint = 99.2;
  const float ref_triplePointBath = 0.0;


  return ((raw - triplePointBath)*(ref_boilingPoint-ref_triplePointBath))/(boilingPoint-triplePointBath) + ref_triplePointBath;
}

void AlternateOutputs(Alternator *alternator, PercToDO *outBlock){
  //rewrite signals from outblock
  alternator->in1 = outBlock->out1;
  alternator->in2 = outBlock->out2;
  alternator->in3 = outBlock->out3;

  switch(alternator->state){
      case 0:
        alternator->out1 = alternator->in1;
        alternator->out2 = alternator->in2;
        alternator->out3 = alternator->in3;
      break;
      case 1:
        alternator->out1 = alternator->in2;
        alternator->out2 = alternator->in1;
        alternator->out3 = alternator->in3;
      break;
      case 2:
        alternator->out1 = alternator->in2;
        alternator->out2 = alternator->in3;
        alternator->out3 = alternator->in1;
      break;
      case 3:
        alternator->out1 = alternator->in3;
        alternator->out2 = alternator->in2;
        alternator->out3 = alternator->in1;
      break;
      case 4:
        alternator->out1 = alternator->in3;
        alternator->out2 = alternator->in1;
        alternator->out3 = alternator->in2;
      break;
      case 5:
        alternator->out1 = alternator->in1;
        alternator->out2 = alternator->in3;
        alternator->out3 = alternator->in2;
      break;
  }

  if(CheckTimer(alternator->tmr, alternator->period)){
    alternator->state ++;
    if(alternator->state>5)
      alternator->state = 0;
  }
}
