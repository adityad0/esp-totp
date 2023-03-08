# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #
  # AUTHOR: @adityad0 [https://github.com/adityad0/]
  # ESP-PHONE https://github.com/adityad0/esp-totp/
  # LICENSE: https://github.com/adityad0/esp-totp/blob/main/LICENSE
  # A basic TOTP generator written in Python (CircuitPython) and built for the SEEED XIAO ESP32-C3.
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #

''' Including all the required modules'''
# Display modules
import adafruit_ssd1306, adafruit_framebuf

# Time, NTP and RTC modules
import time, socketpool, adafruit_ntp, rtc

# WiFi modules
import wifi

# Hashing modules
import struct, adafruit_hashlib as hashlib

# CircuitPython modules
import board, busio, digitalio


# Variable Declarations
NUM_CHARS = 6
TOKEN_PERIOD = 30
HASH_ALGO = 'SHA1'

# Enable the display
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
# Display the startup message
display.fill(0)
display.text("ESP-TOTP", 0, 0, 1)
display.text("github.com/adityad0", 0, 20, 1)
display.text("Initializing..", 0, 45, 1)
display.show()

# Read the app.data file containing information about the apps
try:
    app_data_file = open("app.data", "r")
except Exception as e:
    print("Error: " + str(e))
    display.fill(0)
    display.text("Unable to open app.data", 0, 20, 1)
    display.show()
    app_data_file = open("app.data", "a+")
    app_data_file.write("app_name,secretkey,is_b32_encoded,display_app_name,otp_len,otp_type,otp_alg,refresh_time_secs")
    app_data_file.close()
    print("New app.data created.")
    display.fill(0)
    display.text("Unable to open app.data", 0, 20, 1)
    display.show()
    app_data_file = open("app.data", "r")

# Variables for handling the app.data file
app_data_lines = app_data_file.readlines()
num_apps = len(app_data_lines)
app_data_file.close()

# Connect to WiFi & get date/time
print("Connecting to WiFi..")
display.fill(0)
display.text("Connecting to WiFi..", 0, 20, 1)
display.show()

wifi.radio.connect("Wifi_SSID", "Wifi_password") # Replace with your WiFi SSID and PSK
time.sleep(1) # Wait for the connection to be established

print("Connected to WiFi!")
display.fill(0)
display.text("WiFi connected", 0, 20, 1)
display.show()

pool = socketpool.SocketPool(wifi.radio) # Create a socket pool
ntp = adafruit_ntp.NTP(pool, tz_offset=0) # Get the current time from the NTP server

# Set the RTC
try:
    rtc.RTC().datetime = ntp.datetime # Set the inbuilt RTC to the current time
except Exception as e:
    print("Could not set time!")
# Print current time
print("Current time (UTC/UNIX): " + str(time.time()))
display.text("Unix Time: " + str(time.time()), 0, 30, 1)
display.show()

time.sleep(1)

# Writing a custom b32decode function to decode base32 encoded strings
def b32decode(encoded_string):
    base32_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    padding_char = '='
    bits_per_character = 5
    encoded_string = encoded_string.strip().upper()
    padding = encoded_string.count(padding_char)
    if padding > 0:
        encoded_string = encoded_string[:-padding]
    bits = ''
    for c in encoded_string:
        num = base32_chars.index(c)
        bin_str = ''
        for i in range(bits_per_character):
            bin_str = str(num % 2) + bin_str
            num //= 2
        bits += bin_str
    num_bytes = (len(bits) // 8)
    byte_string = b''
    for i in range(num_bytes):
        byte_string += int(bits[i*8:(i+1)*8], 2).to_bytes(1, 'utf-8')
    return byte_string

# Function to generate the HMAC-SHA1 hash
def hmac(key, message):
    # Set the size of the SHA block
    sha1_block_size = 64
    key_block = bytes(key) + (b'\0' * (sha1_block_size - len(key)))
    # Generate the inner and outer keys
    inner_key_bytes = []
    outer_key_bytes = []
    for x in key_block:
        inner_key_byte = x ^ 0x36
        outer_key_byte = x ^ 0x5C
        inner_key_bytes.append(inner_key_byte)
        outer_key_bytes.append(outer_key_byte)
    inner_key = bytes(inner_key_bytes)
    outer_key = bytes(outer_key_bytes)
    inner_message = inner_key + message
    outer_message = outer_key + hashlib.sha1(inner_message).digest()
    return hashlib.sha1(outer_message).digest()

def get_hotp_token(secret, intervals_no):
    key = b32decode(secret)
    msg = struct.pack(">Q", intervals_no)
    h = hmac(key, msg)
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h

def get_totp_token(secret, unix_time):
    x = str(get_hotp_token(secret, intervals_no = int(unix_time)//30))
    while len(x) != 6:
        x += '0'
    return x


# Configure the rotary encoder
encoder_counter = 0
currentStateCLK = 0
lastStateCLK = 0
currentDir = ""
lastButtonPress = 0

CLK = digitalio.DigitalInOut(board.D10)
CLK.direction = digitalio.Direction.INPUT
CLK.pull = digitalio.Pull.UP

DT = digitalio.DigitalInOut(board.D9)
DT.direction = digitalio.Direction.INPUT
DT.pull = digitalio.Pull.UP

SW = digitalio.DigitalInOut(board.D8)
SW.direction = digitalio.Direction.INPUT
SW.pull = digitalio.Pull.UP
lastStateCLK = CLK.value



def display_menu():
    display.fill(0)
    display.text("ESP-TOTP (adityad.me)", 0, 0, 1)
    display.text(f"IP: {str(wifi.radio.ipv4_address)}", 0, 20, 1)
    display.text(f"SSID: {str(wifi.radio.ap_info.ssid)}", 0, 30, 1)
    lt = time.localtime()
    display.text(f"UTC Date: {str(lt[0])}/{str(lt[1])}/{str(lt[2])}", 0, 40, 1)
    display.text(f"UTC Time: {str(lt[3])}:{str(lt[4])}:{str(lt[5])}", 0, 50, 1)
    display.show()

display_menu()


current_app_count = 0
screen_last_update_time = 0


def update_display(current_app):
    if current_app[0] == 'menu':
        display_menu()
        return

    unix_time = str(time.time())
    print("Time: " + unix_time)
    totp = str(get_totp_token(current_app[1], str(unix_time)))
    print("OTP: " + totp)
    app_name = str(current_app[3])
    counter = str(int(unix_time) % int(current_app[7]))
    screen_last_update_time = time.time()

    display.fill(0)
    display.text(str(app_name), 0, 0, 1)
    # display.text(f"Counter: {counter}", 0, 20, 1)
    display.text(f"OTP: {totp}", 0, 20, 1)
    display.text(f"UTC: {unix_time}", 0, 30, 1)
    display.show()

    print("Display updated")


while True:
    # Get the current app
    current_app = app_data_lines[current_app_count].split(',')

    unix_time = str(time.time())

    # Handle the rotary encoder
    rotary_encoder_moved = False
    currentStateCLK = CLK.value
    if(currentStateCLK != lastStateCLK and currentStateCLK == 1):
        if(DT.value != currentStateCLK):
            current_app_count += 1
            currentDir ="CW"
            rotary_encoder_moved = True
            if current_app_count > num_apps - 1:
                current_app_count = 0
        else:
            current_app_count -= 1
            currentDir ="CCW"
            rotary_encoder_moved = True
            if current_app_count < 0:
                current_app_count = num_apps - 1
        print("Direction: " + currentDir)
        print("Counter: " + str(current_app_count))
    lastStateCLK = currentStateCLK

    if rotary_encoder_moved:
        update_display(current_app)
    elif int(unix_time) % 30 == 0:
        update_display(current_app)
    else:
        continue
