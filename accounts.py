"""
  # AUTHOR: @adityad0 [https://github.com/adityad0/]
  # ESP-PHONE https://github.com/adityad0/esp-totp/
  # LICENSE: https://github.com/adityad0/esp-totp/blob/main/LICENSE
  # A basic TOTP generator written in Python (CircuitPython) and built for the SEEED XIAO ESP32-C3.
"""

# This file contains a dictionary containing all the users accounts with app name and secret key.
# Set flag 'SAVE_AS_HASH = True' to save all the secret keys as a SHA-1 hash insted of plain text.

SAVE_AS_HASH = False

accounts = {
  "APP_NAME" : "SECRET_KEY"
}
