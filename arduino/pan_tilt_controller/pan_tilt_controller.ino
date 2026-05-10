#include <Servo.h>

// Pan servo on D9, tilt servo on D10.
// Protocol: ASCII line "P<angle>,T<angle>\n", angles 0..180.
// Replies "OK <pan>,<tilt>\n" on each accepted command.

Servo panServo;
Servo tiltServo;

const int PAN_PIN  = 9;
const int TILT_PIN = 10;
const int CENTER   = 90;

const int ANGLE_MIN = 0;
const int ANGLE_MAX = 180;

int panAngle  = CENTER;
int tiltAngle = CENTER;

const size_t BUF_SIZE = 32;
char buf[BUF_SIZE];
size_t bufLen = 0;

void setup() {
  Serial.begin(115200);
  panServo.attach(PAN_PIN);
  tiltServo.attach(TILT_PIN);
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      buf[bufLen] = '\0';
      handleCommand(buf);
      bufLen = 0;
    } else if (c != '\r' && bufLen < BUF_SIZE - 1) {
      buf[bufLen++] = c;
    }
  }
}

void handleCommand(const char* cmd) {
  // Parse "P<int>,T<int>"
  if (cmd[0] != 'P') return;
  const char* comma = strchr(cmd, ',');
  if (!comma || *(comma + 1) != 'T') return;

  int p = atoi(cmd + 1);
  int t = atoi(comma + 2);

  panAngle  = constrain(p, ANGLE_MIN, ANGLE_MAX);
  tiltAngle = constrain(t, ANGLE_MIN, ANGLE_MAX);

  panServo.write(panAngle);
  tiltServo.write(tiltAngle);

  Serial.print("OK ");
  Serial.print(panAngle);
  Serial.print(",");
  Serial.println(tiltAngle);
}
