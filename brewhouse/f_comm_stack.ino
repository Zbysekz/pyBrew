void ProcessReceivedData(uint8_t data[]){
  int res=0;//aux temp
  int len = data[0];
  uint16_t auxVal = 0;

  switch(data[1]){//by ID
    case 1:
      HLT_HeatingEnabled = (data[2] & (1 << 0))!=0;
      HLT_PIDEnabled = (data[2] & (1 << 1))!=0;
      RVK_HeatingEnabled = (data[2] & (1 << 2))!=0;
      RVK_PIDEnabled = (data[2] & (1 << 3))!=0;

      manSP_HLT_temp = getValue(data[4],data[5]);
      manSP_RVK_temp = getValue(data[6],data[7]);
      
    break;
    default:
    ;
  }
}
    
    
    

void ProcessReceivedData(){
  for(int i=0;i<RXQUEUESIZE;i++)
    if(rxBufferMsgReady[i]==true){
      ProcessReceivedData(rxBuffer[i]);
      rxBufferMsgReady[i]=false;//mark as processed
    }
}

void Receive(uint8_t rcv){
   //Serial.write(rcv);
    //Serial.write(rxLen);
    //Serial.write(rxPtr);
    //Serial.write(readState);
    
    switch(readState){
    case 0:
      if(rcv==111){readState=1;}//start token
      break;
    case 1:
      if(rcv==222)readState=2;else { //second start token
        if(errorCnt_dataCorrupt<255)errorCnt_dataCorrupt++; 
        readState=0;
      }
      break;
    case 2:
      rxLen = rcv;//length
      if(rxLen>RXBUFFSIZE){//should not be so long
        readState=0;
        if(errorCnt_dataCorrupt<255)errorCnt_dataCorrupt++;
      }else{ 
        readState=3;
        rxPtr=0;
        //choose empty stack
        rxBufPtr=99;
        for(int i=0;i<RXQUEUESIZE;i++){
          if(rxBufferMsgReady[i]==false)
            rxBufPtr=i;
        }
        if(rxBufPtr==99){
          if(errorCnt_BufferFull<255)errorCnt_BufferFull++;
          readState=0;
        }else{
          rxBuffer[rxBufPtr][rxPtr++]=rxLen;//at the start is length
        }
      }
      break;
    case 3://receiving data itself
      rxBuffer[rxBufPtr][rxPtr++] = rcv;
      
      if(rxPtr>=RXBUFFSIZE || rxPtr>=rxLen+1){
        readState=4;
      }
      break;
    case 4:
      crcH=rcv;//high crc
      readState=5;
      break;
    case 5:
      crcL=rcv;//low crc

      //Serial.print(crcL+(uint16_t)crcH*256);
      //Serial.print(CRC16(rxBuffer[rxBufPtr], rxLen+1));
      if(CRC16(rxBuffer[rxBufPtr], rxLen+1) == crcL+(uint16_t)crcH*256){//crc check
        readState=6;
      }else {
        readState=0;//CRC not match
        if(errorCnt_CRCmismatch<255)errorCnt_CRCmismatch++;
      }
      break;
    case 6:
      if(rcv==222){//end token
        rxBufferMsgReady[rxBufPtr]=true;//mark this packet as complete
      }else{
        if(errorCnt_dataCorrupt<255)errorCnt_dataCorrupt++; 
      }
      readState=0;
      break;
    }
}
void HandleDataComm(){
   uint8_t outputs = ((uint8_t)(RVK_alternator.out1)<<0) + ((uint8_t)(RVK_alternator.out2)<<1) + ((uint8_t)(RVK_alternator.out3)<<2) +
                      ((uint8_t)(HLT_alternator.out1)<<3) + ((uint8_t)(HLT_alternator.out2)<<4) + ((uint8_t)(HLT_alternator.out3)<<5);
   uint8_t sbuf[] = {1,
                       getH(HLT_tempSensor.value),getL(HLT_tempSensor.value),
                       getH(RVK_tempSensor.value),getL(RVK_tempSensor.value),
                       getH(SCZ_tempSensor.value),getL(SCZ_tempSensor.value),
                       getH(errorFlags),getL(errorFlags),
                       getH((errorFlags>>16)),getL((errorFlags>>16)),outputs
                       };

    int cnt = Send(sbuf,12);
    
    while(Serial.available()){
      int rcv = Serial.read();
      Receive((uint8_t)rcv);
    } 
}

int Send(uint8_t d[],uint8_t d_len){
  uint8_t data[6+d_len];
 
  data[0]=111;//start byte
  data[1]=222;//start byte

  data[2]=d_len;//delka

  for(int i=0;i<d_len;i++)
    data[3+i]=d[i];//data
  
  uint16_t crc = CRC16(data+2, d_len+1);

  data[3+d_len]=crc/256;
  data[4+d_len]=crc%256;
  data[5+d_len]=222;//end byte

  return Serial.write(data,6+d_len);
}


//calculation of CRC16, corresponds to CRC-16/XMODEM on https://crccalc.com/﻿
uint16_t CRC16(uint8_t* bytes, uint8_t length)
{
    const uint16_t generator = 0x1021; // divisor is 16bit 
    uint16_t crc = 0; // CRC value is 16bit 

    for (int b=0;b<length;b++)
    {
        crc ^= (uint16_t)(bytes[b] << 8); // move byte into MSB of 16bit CRC

        for (int i = 0; i < 8; i++)
        {
            if ((crc & 0x8000) != 0) // test for MSb = bit 15
            {
                crc = (uint16_t)((crc << 1) ^ generator);
            }
            else
            {
                crc <<= 1;
            }
        }
    }
    return crc;
}
