#include <Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <qrcode.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
Servo myServo1;
Servo myServo2;

int servoPin1 = 5;  // First servo pin
int servoPin2 = 6;  // Second servo pin
int adjustVal = 90; // Adjust this for desired speed/power

unsigned long commandTime = 0;
bool isMoving = false;

void generateAndDisplayQR(const char *text) {
  QRCode qrcode;
  uint8_t qrcodeData[qrcode_getBufferSize(1)];  // Version 1 QR (21x21)

  qrcode_initText(&qrcode, qrcodeData, 1, ECC_LOW, text);

  int scale = 3;
  int qrSize = qrcode.size;
  int quietZone = 4;
  int totalSize = (qrSize + 2 * quietZone) * scale;

  int xOffset = (SCREEN_WIDTH - totalSize) / 2;
  int yOffset = (SCREEN_HEIGHT - totalSize) / 2;

  display.clearDisplay();

  for (int y = -quietZone; y < qrSize + quietZone; y++) {
    for (int x = -quietZone; x < qrSize + quietZone; x++) {
      int color = WHITE;
      if (x >= 0 && y >= 0 && x < qrSize && y < qrSize) {
        color = qrcode_getModule(&qrcode, x, y) ? BLACK : WHITE;
      }
      display.fillRect(xOffset + x * scale, yOffset + y * scale, scale, scale, color);
    }
  }

  display.display();
}

void setup() {
  Serial.begin(9600);

  myServo1.attach(servoPin1);
  myServo2.attach(servoPin2);

  myServo1.write(90); // Stop
  myServo2.write(90);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    while (1);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
  display.println("Waiting for input...");
  display.display();

  Serial.println("System Ready: Send 1 or 0 via Serial");
}

void loop() {
  if (Serial.available() > 0) {
    char received = Serial.read();

    if (received == '1') {
      // Show Recyclable QR & move flap to 'open' direction
      generateAndDisplayQR("Recyclable");
      myServo1.write(90 + adjustVal);
      myServo2.write(90 - adjustVal);
      Serial.println("Recyclable: Opening flap");
      commandTime = millis();
      isMoving = true;
    } 
    else if (received == '0') {
      // Show Non-Recyclable QR & move flap to 'close' direction
      generateAndDisplayQR("Non-Recyclable");
      myServo1.write(90 - adjustVal);
      myServo2.write(90 + adjustVal);
      Serial.println("Non-Recyclable: Closing flap");
      commandTime = millis();
      isMoving = true;
    } 
    else {
      // Show unknown input
      display.clearDisplay();
      display.setTextSize(1);
      display.setTextColor(WHITE);
      display.setCursor(0, 10);
      display.println("Unknown Input");
      display.display();
      myServo1.write(90); // Stop
      myServo2.write(90);
      Serial.println("Unknown input: Flap stopped");
      isMoving = false;
    }
  }

    // Auto-stop after 0.5 seconds (1000 ms)
  if (isMoving && (millis() - commandTime >= 1000)) {
    Serial.println("Flap returning slowly to initial position...");
    
    int currentPos1 = myServo1.read();  // Get current position
    int currentPos2 = myServo2.read();
    
    // Move servo1 towards 90 slowly
    while (currentPos1 != 90 || currentPos2 != 90) {
      if (currentPos1 > 90) currentPos1--;
      else if (currentPos1 < 90) currentPos1++;
      
      if (currentPos2 > 90) currentPos2--;
      else if (currentPos2 < 90) currentPos2++;

      myServo1.write(currentPos1);
      myServo2.write(currentPos2);

      delay(15); // Smooth movement delay (you can adjust this if needed)
    }

    Serial.println("Flap returned to initial position.");
    isMoving = false;
  }

}