#define INA_1_pin 3
#define INB_1_pin 5
#define PWM_1_pin 6
#define INA_2_pin 9
#define INB_2_pin 10
#define PWM_2_pin 11
#define BAUD_RATE 9600
#define motorOneSpeed 50
#define motorTwoSpeed 55

#define ULTRASONIC_1_TRIG 12
#define ULTRASONIC_2_TRIG 7
#define ULTRASONIC_3_TRIG 2
#define ULTRASONIC_1_ECHO 13
#define ULTRASONIC_2_ECHO 8
#define ULTRASONIC_3_ECHO 4

#define FRONT_DIST 30
#define SIDE_DIST 20

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

long generic_ping(int trig, int echo) 
{
  // Clears the trigPin
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  long duration = pulseIn(echo, HIGH);
  // Calculating the distance
  return duration*0.034/2;
}

long ping_1() 
{
  pinMode(ULTRASONIC_1_TRIG, OUTPUT); // Sets the trigPin as an Output
  pinMode(ULTRASONIC_1_ECHO, INPUT); // Sets the echoPin as an Input
  return generic_ping(ULTRASONIC_1_TRIG, ULTRASONIC_1_ECHO);
}

long ping_2() 
{
  pinMode(ULTRASONIC_2_TRIG, OUTPUT); // Sets the trigPin as an Output
  pinMode(ULTRASONIC_2_ECHO, INPUT); // Sets the echoPin as an Input
  return generic_ping(ULTRASONIC_2_TRIG, ULTRASONIC_2_ECHO);
}

long ping_3() 
{
  pinMode(ULTRASONIC_3_TRIG, OUTPUT); // Sets the trigPin as an Output
  pinMode(ULTRASONIC_3_ECHO, INPUT); // Sets the echoPin as an Input
  return generic_ping(ULTRASONIC_3_TRIG, ULTRASONIC_3_ECHO);
}

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
  spinMotor(motorOne);
  spinMotor(motorTwo);

  Serial.begin(BAUD_RATE);
}

void loop()
{ 
  if((int)ping_1() < FRONT_DIST)
  {
    if(ping_2() <= ping_3())
    {
      motorOne.INA_dir = LOW;
      motorOne.INB_dir = HIGH;
      motorTwo.INA_dir = LOW;
      motorTwo.INB_dir = HIGH;
    }
    else
    {
      motorOne.INA_dir = HIGH;
      motorOne.INB_dir = LOW;
      motorTwo.INA_dir = HIGH;
      motorTwo.INB_dir = LOW;
    }
    
    spinMotor(motorOne);
    spinMotor(motorTwo);

    while(ping_1() < FRONT_DIST)
    {
      Serial.println((int)ping_1());
      delay(100);
    }
  }
  /*
  if((int)ping_2() < SIDE_DIST)
  {
    motorOne.INA_dir = LOW;
    motorOne.INB_dir = HIGH;
    motorTwo.INA_dir = LOW;
    motorTwo.INB_dir = HIGH;

    spinMotor(motorOne);
    spinMotor(motorTwo);

    while(ping_2() < SIDE_DIST)
    {
      delay(50);
    }
  }
  
  if((int)ping_3() < SIDE_DIST)
  {
    motorOne.INA_dir = HIGH;
    motorOne.INB_dir = LOW;
    motorTwo.INA_dir = HIGH;
    motorTwo.INB_dir = LOW;

    spinMotor(motorOne);
    spinMotor(motorTwo);

    while(ping_3() < SIDE_DIST)
    {
      delay(50);
    }
  }
  */
  motorOne.INA_dir = LOW;
  motorOne.INB_dir = HIGH;
  motorTwo.INA_dir = HIGH;
  motorTwo.INB_dir = LOW;
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
