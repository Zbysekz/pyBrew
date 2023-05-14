
void ProcessPID(PID *block){
  if(block == NULL)
    return;
  if(!block->active){
    block->output = 0.0;
    block->integr_e = 0.0;
    block->last_e = 0.0;
    return;
  }

  
  float e = block->setpoint - block->input;
  block->output = block->params.Kp*e + block->params.Ki*block->integr_e + block->params.Kd*(e - block->last_e);

  if (block->output >100.0){//saturation
    block->output = 100.0;
  }else if(block->output < 0.0){
    block->output = 0.0;
  }else{
    block->integr_e += e;
  }
}
///////////////////////////////////conversion of percent value to one or more digital outputs
void ProcessPercToDO(PercToDO *block){

  if(!block->active){
    block->out1 = false;
    block->out2 = false; 
    block->out3 = false; 
    ResetTimer(block->tmr1);
    ResetTimer(block->tmr2);
    ResetTimer(block->tmr3);
    ResetTimer(block->tmrMain);
    return;
  }
  //takes input only in range 0-100
  if(block->input>100.0){
    block->input = 100.0;
  }else if (block->input < 0.0){
    block->input = 0.0;
  }
  
  /*if(block->nOfOutputs == 1){
    if(block->input > (100.0/2) + block->hysteresis){
      block->out = 1;  
    }else if(block->input < (100.0/2) - block->hysteresis){
      block->out = 0;  
    }
  }else if(block->nOfOutputs == 2){
    if(block->input > (100.0*2/3) + block->hysteresis){
      block->out = 2;  
    }else if(block->input < (100.0*2/3) - block->hysteresis && block->input > (100.0/3) + block->hysteresis){
      block->out = 1;  
    }else if(block->input < (100.0/3) - block->hysteresis){
      block->out = 0;  
    }
  }else */
  if(block->nOfOutputs == 3){
    if(block->input > (100.0*2/3) + block->hysteresis){
      block->out = 3;  
    }else if(block->input < (100.0*2/3) - block->hysteresis && block->input > (100.0/3) + block->hysteresis){
      block->out = 2;  
    }else if(block->input < (100.0/3) - block->hysteresis && block->input > block->hysteresis){
      block->out = 1;  
    }else if(block->input < block->hysteresis){
      block->out = 0;  
    }else{
      //we are in hysteresis band, check where we are - this must be handled, consider jumping directly into this band without smooth increase
      if(block->input > 100.0/2){
        if(block->out < 2){
          block->out = 2;
        }
      }else if(block->out!=1 && block->out!=2){ //lesser than half
        block->out = 1;
      }
    }
  }
  /*Serial.print(F("in:"));
  Serial.println(block->input);
  Serial.println(block->input < (100.0*2/3) - block->hysteresis);*/
  //Serial.print(F("outN:"));
 // Serial.println(block->out);
  float remainder;
  switch(block->out){
    case 3:
      remainder = block->input - (100.0*2/3);
      break;
    case 2:
      remainder = block->input - (100.0/3);
      break;
    case 1:
      remainder = block->input;
    break;
    default:
      remainder = 0.0;
  }
  //normalize to <0-100> and limit
  remainder = remainder * 3;
  remainder = remainder>95.0?100.0:remainder;
  remainder = remainder<5.0?0.0:remainder;

  /*Serial.print(F("remainder:"));
  Serial.println(remainder);*/


  
  if(CheckTimer(block->tmrMain, block->period)){
    block->out1 = true;
    block->out2 = true; 
    block->out3 = true; 
    ResetTimer(block->tmr1);
    ResetTimer(block->tmr2);
    ResetTimer(block->tmr3);
  }
  if(block->out < 1){
    block->out1 = false;
  }else if(block->out == 1){
    if(block->out1 && CheckTimer(block->tmr1, (unsigned long)(block->period * remainder / 100.0))){
      block->out1 = false;
    }
  }else{
    block->out1 = true;
  }
  //
  if(block->out < 2){
    block->out2 = false;
  }else if(block->out == 2){
    if(block->out2 && CheckTimer(block->tmr2, (unsigned long)(block->period * remainder / 100.0))){
      block->out2 = false;
    }
  }else{
    block->out2 = true;
  }
  //
  if(block->out < 3){
    block->out3 = false;
  }else if(block->out == 3){
    if(block->out3 && CheckTimer(block->tmr3, (unsigned long)(block->period * remainder / 100.0))){
      block->out3 = false;
    }
  }else{
    block->out3 = true;
  }
 
}

//////////////////////////////////
