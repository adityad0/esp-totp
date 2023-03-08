# ESP-TOTP

## About

The ESP-TOTP is a Time-based one-time password (TOTP) generator written in Python (CircuitPython) for the SEEED XIAO ESP32-C3. TOTP is an extension for HMAC-based one-time passwords (HOTP). TOTPs are generated at regular intervals, have a fixed length and change with time. They can be generated offline, unlike traditional OTPs and eliminate the need for an active internet or mobile connection.

## Components
1. A microcontroller such as the SEEED XIAO ESP32-C3
2. SSD1306 OLED display
3. Rotary encoder
4. Wires
5. Li-ion battery

## Getting started
### 1. Installing CircuitPython
  a. Connect your microcontroller to your computer and find the port name or number. On Windows, use Device Manager to find the port.
  b. Use PIP to install 'esptool' by running the command, `pip install esptool.`
  c. Use `esptool --port COM10 erase_flash` to erase the flash on your microcontroller and replace 10 with the port of your device. Prefix `python -m ` if the above command does not work.
  d. Use `esptool --port COM10 write_flash -z 0x0 firmware_file_name.bin` to install the firmware to the microcontroller flash.
  e. Once CircuitPython is installed, use a software like Putty to connect to the Python shell with the correct port name/number and baud rate (Default baud 115200).
### 2. Connecting to Wi-Fi
  a. You can connect to Wi-Fi from the Python shell by importing the 'wifi' module or by creating a file called 'settings.toml'.
  b. Create a filled called 'settings.toml' using the Python shell by running the following commands, 'f = open("settings.toml", "w+");'.
  c. Now, write the Wi-Fi SSID, password and API password to the file by using, `f.write('CIRCUITPY_WIFI_SSID = "SSID"\n')`, `f.write('CIRCUITPY_WIFI_PASSWORD = "password"\n')` and `f.write('CIRCUITPY_WEB_API_PASSWORD = "api password"\n')`.
  d. Save and close the file by using `f.close()`. The device will now automatically connect to the specified Wi-Fi network.
### 3. Finding the IP address and getting getting started with the web server
  a. Use `import wifi` and `print(wifi.radio.ipv4_address)` to print the device IPv4 address. Use this IP on your browser to connect to the microcontroller's inbuilt web server.
  b. Use the password which you set in the 'settings.toml' file under `CIRCUITPY_WEB_API_PASSWORD` but leave the username field blank.
  c. You can now upload your code directly from your browser. Name the program 'code.py' to automatically run the program on device startup.
### 4. Uploading and running the program
  a. Clone the repository or download a zip file containing all files available here, https://github.com/adityad0/esp-totp/
  b. Upload all the files to the microcontroller in the appropriate directories.

## Program working and description

The program has been broken down into 9 essential sections followed by an explanation of every section below.

1.	Display & I2C controller
2.	App secret handler
3.	Rotary Encoder controller
4.	BASE32 decoder
5.	HMAC generator
6.	HOTP & TOTP generator
7.	Wi-Fi controller
8.	Real-Time Clock (RTC) controller
9.	SHA1 Hash generator

The above program sections are described below,

### 1. Display & I2C Controller
  The OLED display used in this project, is based on the SSD1306 controller, and is controlled using the Adafruit-SSD1306 module which is included in the CircuitPython library bundle. This program only uses the following methods, the 'Fill' method, used to fill all the pixels with 0 for off and 1 for on, 'Text' method, to draw a string to the display at any given coordinates of the display between (0,0) and (64,128). The 'show' method pushes all changes and refreshes the display.
	The Inter-Integrated Circuit (I2C or I squared C) connection, initialized with the 'busio' module, uses 'board.SCL' and 'board.SDA' for the default clock and data pins of the built-in I2C bus.
  
### 2.	App-Secret Handler
  All apps and their secret keys are saved in a file called `app.data,` which contains the hashing algorithm, refresh time, and a Boolean flag to indicate whether the secret is BASE32 encoded. The file is opened and is read using the `readlines()` method, which returns a list with each line of the file as an item in the list.
  
### 3.	Rotary Encoder Controller
  The CLK pin, DT pin and SW pins of the rotary encoder are connected to pins D10, D9 and D8 respectively. 'board.PIN' is used to refer to the pins on the microcontroller, and the 'digitalio' module is used to get the status of the used pins.
	The rotary encoder is powered by 3.3 volts. When rotated clockwise, `the CLK pin connects to GND before the DT pin, and anti-clockwise when the DT pin connects to GND before the CLK pin. When rotated, the rotary encoder generates a square wave 90° out of phase and can be determined in programming when `B != A` for clockwise and `B = A` for anti-clockwise, where `B` is DT and `A` is CLK. Repeatedly checking the pins for a change in the voltage (HIGH or LOW) allows us to determine the rotation of the rotary encoder, and can easily be accomplished with a `while` loop.

### 4.	BASE32 Decoder
  The BASE32 decoder function, defined as `b32decode()`, is used to convert binary to text. BASE32 uses a set of 32 characters represented as a 5-bit binary value. Each character represents one of 32 characters (A-Z & 2-7). Base32 representation is done by dividing a string into groups of 5 characters each and adding zero bits (=) at the end of the string if the length of the string is not divisible by 5, before encoding.
The `b32decode` function in this program first converts the encoded string back into its 5-bit binary representation by looking up the value of each character. Then, the binary string is divided into groups of 8-bit binary values and is then interpreted as ASCII codes for the original binary data.

### 5.	HMAC Generator
  Short for "keyed-Hash Message Authentication Code" is a type of message authentication code that uses a secret key to authenticate a message and detect any tampering. It combines the cryptographic hash function, SHA-1 in this case with a secret key to produce a fixed-length message digest that can be used to verify the authenticity of a message.
	In the `hmac` function of this program, the length of the SHA-1 (Secure Hash Algorithm) is fixed to a length of 64 bytes and a null character `\0` is appended until the length of the is equal to 64 bytes. The function generates an inner and outer key by performing an XOR of X and the fixed value of 0x36 and 0x5C and produces the inner and outer message to provide an additional layer of security against certain types of attacks. The SHA-1 of the outer message is returned which is the HMAC of the key and message.

### 6.	HOTP and TOTP Generator
  HMAC-based One-Time Password (HOTP) is a one-time password algorithm based on HMAC to generate a One-Time Password (OTP) valid only for a single authentication attempt by combining a secret key and a counter value.
  •	A secret key and counter value are generated and shared between the authentication server and the user.
  •	The HMAC value is truncated to generate a 6-digit one-time password.

### 7.	Wi-Fi Controller
  The `radio` class of the `wifi` module is used to connect to a Wi-Fi using the `connect` method. The `ipv4_address` and `ap_info.ssid` methods are used to get the IPv4 address and SSID/Name (Service Set ID) of the device when connected to a Wi-Fi network. The device runs a simple web server on port 80 and can be used to add new secret keys to the device or program the device. The web server also provides a serial connection to the inbuilt Python interpreter which allows you to restart the program on the device or to update the libraries.

### 8.	Real-Time Clock (RTC) Controller
  The SEEED XIAO ESP32-C3 contains a built-in RTC which counts the time in real-time to very accurate levels. However, this RTC resets itself when the power to the device is reset or disconnected. Network Time Protocol (NTP) is a pool of computers around the world used to count time and retrieve it when requested. Using the internet connection, the RTC on the device is set to the current time and can be accessed with the `time` module.
	The `time` module contains a method `time()`, used to get the number of seconds which have passed since January 1st, 1970 and is called Epoch or Unix time. This time is used to generate the TOTP.

### 9.	SHA-1 Hash Generator
  SHA-1 is a one-time hashing algorithm, it produces a unique and fixed-length string for the input and can be used for verifying the authenticity of data. Although SHA-1 is not considered as secure as SHA-256 or SHA-512, it is, but not always used to generate a TOTP. The `adafruit_hashlib` contains an SHA-1 library to generate an SHA-1 of the input string. This string is then used in the previous functions to generate HMAC and HOTP.

## Future updates
1. An app to connect to the device over Bluetooth/Wi-Fi to add new TOTP secrets and sync time.

## Resources
1. https://learn.adafruit.com/circuitpython-totp-otp-2fa-authy-authenticator-friend/software
2. https://medium.com/analytics-vidhya/understanding-totp-in-python-bbe994606087
3. https://totp.danhersam.com/
4. https://github.com/adityad0/hacktag
5. https://learn.adafruit.com/circuitpython-with-esp32-quick-start/command-line-esptool
6. https://circuitpython.org/board/seeed_xiao_esp32c3/
7. https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/
8. https://stackoverflow.com/questions/8529265/google-authenticator-implementation-in-python
9. https://lastminuteengineers.com/rotary-encoder-arduino-tutorial/

## License
This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International Lincense. Read the license here: https://github.com/adityad0/esp-totp/blob/main/LICENSE
