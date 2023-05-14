//forward declaration of method using struct
void ProcessPID(PID *block);
void ProcessPercToDO(PercToDO *block);
void PrintAddress(DeviceAddress deviceAddress);
bool ReadTemperature(DeviceAddress address, TempSensor *tempS);
void AlternateOutputs(Alternator *alternator, PercToDO *outBlock);
