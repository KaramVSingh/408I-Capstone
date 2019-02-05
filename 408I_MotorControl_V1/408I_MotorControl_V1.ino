#define INA_1_pin 3
#define INB_1_pin 5
#define PWM_1_pin 6
#define INA_2_pin 9
#define INB_2_pin 10
#define PWM_2_pin 11
#define BAUD_RATE 9600
#define motorOneSpeed 50
#define motorTwoSpeed 40

// relevant motor control parameters
struct motorControl
{
  byte INA_pin;
  byte INB_pin;
  byte PWM_pin;

  byte INA_dir;
  byte INB_dir;
  int PWM_val;
};

// motor control variables for each motor
struct motorControl motorOne;
struct motorControl motorTwo;

void setup()
{
  int pinArray[] = {INA_1_pin,INB_1_pin,PWM_1_pin,INA_2_pin,INB_2_pin,PWM_2_pin};

  //initializes all relevant pins
  for(int i=0; i<sizeof(pinArray); i++)
  {
    pinMode(pinArray[i],OUTPUT);
  }

  // sets initial state for each motor
  motorOne = {INA_1_pin,INB_1_pin,PWM_1_pin,LOW,HIGH,motorOneSpeed};
  motorTwo = {INA_2_pin,INB_2_pin,PWM_2_pin,HIGH,LOW,motorTwoSpeed};

  Serial.begin(BAUD_RATE);
}

void loop()
{
  spinMotor(motorOne);
  spinMotor(motorTwo);
}

// writes relevant parameters from motor control to the motor using the motor controller
void spinMotor(struct motorControl &motor)
{
  digitalWrite(motor.INA_pin,motor.INA_dir);
  digitalWrite(motor.INB_pin,motor.INB_dir);
  analogWrite(motor.PWM_pin,motor.PWM_val);
}
