import time
import datetime
import csv
from pylibftdi import Device

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        #print(crc)
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')


def utf8_to_hex(input_string):
    # Encode the input string as UTF-8
    utf8_bytes = input_string.encode('utf-8')
    
    # Convert the UTF-8 bytes to a hexadecimal string
    hex_string = utf8_bytes.hex()
    
    return hex_string

    # Example usage:
"""
    input_string = "Hello, World!"
    hex_result = utf8_to_hex(input_string)
    print(hex_result)
"""


def hex_to_decimal(hex_string):
    try:
        decimal_number = int(hex_string, 16)
        decimal_string = str(decimal_number)
        return decimal_string
    except ValueError:
        return "Invalid hex string"


def main():
    ### Variables ###
    # Define the Modbus request bytes "\x01\x03\x00\x00\x00\x02"
    modbus_request = {
        "torque" : b"\x01\x03\x00\x00\x00\x02",
        "rpm" : b"\x01\x03\x00\x02\x00\x02",
        "power" : b"\x01\x03\x00\x04\x00\x02"
    }
    # Add checksum to requests
    request_with_crc = {}
    for req in modbus_request.items():
        crc = calculate_crc(req[1])
        request_with_crc[req[0]] = req[1] + crc    
    print(request_with_crc)    
   
    # Initialize the FTDI device for RS485 communication
    with Device(mode='t') as dev:
        dev.baudrate = 9600

    ### Retrieve Data ###
        #  Get Raw Data
        Start_Time = datetime.datetime.now()
        print(Start_Time)
        T0 = time.time()
        hex_data = ()
        for req in request_with_crc.items():
            print(req[1])
            dev.write(req[1])
            time.sleep(0.1)
            response = dev.read(64)
            #print(response)
            response_hex = response.hex() if isinstance(response, bytes) else response
            response_hex = utf8_to_hex(response)
            #print(response_hex)
            hex_data = hex_data + (response_hex,)
        print(hex_data)

        
        # Format Raw Data    
        l = ()
        for resp in hex_data:
            value = resp[10:14]
            measurement = hex_to_decimal(value)
            l = l + (measurement,)
        print(l)
        measurements = [l[x:x+3] for x in range(0, len(l),3)]
        print(measurements)

"""
TODO:
Add timers
Add Timestamps
Add loops
Format for csv properly
Setup Intervals
Add command line arguments
"""

"""
        ### Print Formatted Data to CSV File ###
        #f = open("measurments.csv", "x")    
        with open("measurments.csv", 'x') as file:
            writer = csv.writer(file)
            writer.writerow(measurements)
"""
            




    #modbus_request = request["torque"]
    
    # Start a timer used to calculate intervals
    #T0 = time()
   
    
"""
    # Calculate CRC16 checksum
    #crc = calculate_crc(modbus_request)
    
    # Combine the request and CRC16
    #request_with_crc = modbus_request + crc
        


        # Send the request
        
        # Wait for a response (adjust this as needed)
        #time.sleep(0.05)
        
        # Read the response (adjust the number of bytes to read as needed)
        response = dev.read(256)  # Adjust the read size according to your device's response
        print(response, type(response))
        # Print the response as hex
        print("Response:", response_hex, type(response_hex))
"""    



if __name__ == "__main__":
    main()
