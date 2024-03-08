
void loop(){

  if(CheckTimer(tmrControlLoop, 100L)){

    digitalWrite(PIN_DRIVER1_RUN, driver1Run);

    if (!ReadTemperatures()){
      RVK_tempSensor.error = true;
      SCZ_tempSensor.error = true;
      HLT_tempSensor.error = true;
    }

    ////////--RVK--/////

    PID_temp_RVK.active = !RVK_tempSensor.error && RVK_HeatingEnabled && RVK_PIDEnabled;
    PID_temp_RVK.input = RVK_tempSensor.value;
    PID_temp_RVK.setpoint = manSP_RVK_temp;
    
   if(RVK_PIDEnabled){
      PercToDO_temp_RVK.active = PID_temp_RVK.active;
      PercToDO_temp_RVK.input = PID_temp_RVK.output;
    }else{
      PercToDO_temp_RVK.active = RVK_HeatingEnabled;
      PercToDO_temp_RVK.input = manSP_RVK_temp;
    }

    ////////--HLT--/////
    
    PID_temp_HLT.active = !HLT_tempSensor.error && HLT_HeatingEnabled && HLT_PIDEnabled;
    PID_temp_HLT.input = HLT_tempSensor.value;
    PID_temp_HLT.setpoint = manSP_HLT_temp;

    if(HLT_PIDEnabled){
      PercToDO_temp_HLT.active = PID_temp_HLT.active;
      PercToDO_temp_HLT.input = PID_temp_HLT.output;
    }else{
      PercToDO_temp_HLT.active = HLT_HeatingEnabled;
      PercToDO_temp_HLT.input = manSP_HLT_temp;
    }
    
     // method for processing of blocks
    ProcessPID(&PID_temp_HLT);
    ProcessPID(&PID_temp_RVK);
    ProcessPercToDO(&PercToDO_temp_HLT);
    ProcessPercToDO(&PercToDO_temp_RVK);


    /////////////////// OUTPUTS ///////////////////////////////
    AlternateOutputs(&RVK_alternator, &PercToDO_temp_RVK);
    digitalWrite(PIN_HEAT_RVK_1, RVK_alternator.out1);
    digitalWrite(PIN_HEAT_RVK_2, RVK_alternator.out2);
    digitalWrite(PIN_HEAT_RVK_3, RVK_alternator.out3);

    if(PercToDO_temp_RVK.out3 && PercToDO_temp_HLT.out3)//blockation due to max immediate power limitation
      PercToDO_temp_HLT.out3 = false;
      
    AlternateOutputs(&HLT_alternator, &PercToDO_temp_HLT);
    digitalWrite(PIN_HEAT_HLT_1, HLT_alternator.out1);
    digitalWrite(PIN_HEAT_HLT_2, HLT_alternator.out2);
    digitalWrite(PIN_HEAT_HLT_3, HLT_alternator.out3);
    
    ///////////////
  }

  if(CheckTimer(tmrDataComm, 1000L)){
    HandleDataComm();
    ProcessReceivedData();
  }
    
}


//regulace na teplotu (nádoby + mrazák)
// teploměr přes komunikaci -> PID -> výstup relátka (1-3x)

//regulace čerpadel
// regulace dle tepoloty, výstup je třeba PWM nebo relé



//konfigurace:
// poslání PID parametrů


// procesní data:
// zapnutí/vypnutí regulátorů
// setpointy
