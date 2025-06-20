import serial
import time
import os

print("Current Working Directory:", os.getcwd())  # To confirm path

COM_PORT = 'COM6'  # Your Arduino COM port
BAUD_RATE = 9600   # Must match Arduino sketch
# FILE_PATH = r"C:\AAYUSH\5_College\2024_25 FY CE D\FY sem 2\ASEP 2\Model making\Arduino\arduinooledqrcode\prediction.txt"
FILE_PATH = r"E:/ASEP2/waste_classifier/final/prediction.txt"

arduino = serial.Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=1)
time.sleep(2)  # Allow Arduino to reset

last_content = None  # To store last read value

try:
    while True:
        try:
            with open(FILE_PATH, "r") as file:
                content = file.read().strip().lower()

            # Check if file content has changed
            if content != last_content:
                last_content = content  # Update last content
                if content == "recyclable":
                    arduino.write(b'1')
                    print("Sent: 1 (Recyclable)")
                elif content == "non-recyclable":
                    arduino.write(b'0')
                    print("Sent: 0 (Non-Recyclable)")
                else:
                    print("Warning: Unknown content in prediction.txt:", content)

        except FileNotFoundError:
            print("Error: prediction.txt not found.")

        time.sleep(1)  # Check every 1 second (you can reduce if needed)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    arduino.close()
    print("Serial connection closed.")