import time
import datetime
import csv
import pprint
import argparse
import sys
from pylibftdi import Device


### Define All Variables ###
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

Start_Date = datetime.datetime.now()
parser = argparse.ArgumentParser() # creates command line arguments for Dyno.py
pp = pprint.PrettyPrinter(indent=2)

#For argparse documentation go here: https://docs.python.org/3/library/argparse.html
#For argparse tutorial go here: https://docs.python.org/3/howto/argparse.html
parser.add_argument('-m','--measurement', dest='measurement', type=str, help='add measurement (Default is torque(t), rpm(r), and power(p))')
parser.add_argument('-i','--interval', dest='interval', type=float, help='specify interval (Default is 0.125s. Must be greater than 0.1s)')
parser.add_argument('-f','--filename', dest='filename', type=str, help='specify filename (Default is output(<time>) You don\'t have to include .csv)')
args = parser.parse_args()

measurement = args.measurement
if measurement == None: measurement = 'tr'
INTERVAL_TIME = args.interval
if INTERVAL_TIME == None: INTERVAL_TIME = 0.015
filename = f'{args.filename}'
if args.filename == None: filename = f'output({Start_Date})'

print(f'Measurment(s): {measurement}')
print(f'Interval: {INTERVAL_TIME}')
print(f'Filename: {filename}.csv')
WAIT_TIME = 0.08 # lowest tested success was 0.08s

measurement_dict = {'t':b"\x01\x03\x00\x00\x00\x02", 
                    'r':b"\x01\x03\x00\x02\x00\x02", 
                    'p':b"\x01\x03\x00\x04\x00\x02"}

# Define the Modbus request bytes
modbus_request = [0] * len(measurement)
for i in range(len(measurement)):
    modbus_request[i] = measurement_dict[measurement[i]]
print(modbus_request)
# Add checksum to modbus requests
request_with_crc = [0] * len(measurement)
i = 0
for req in modbus_request:
    crc = calculate_crc(req)
    request_with_crc[i] = req + crc 
    i += 1
print(request_with_crc) 

# Initialize the FTDI device for RS485 communication
try:
    dev = Device(mode='t') # Device is a pylibftdi class
    dev.baudrate = 9600
except:
    print("\nDynomometer not detected!\nPlease check connection and try again.")
    sys.exit(1)

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


def Get_Measurement_In_Hex(Device, request):
    Device.write(request)
    t1 = time.time()
    time.sleep(WAIT_TIME)
    response = Device.read(64)
    t2 = time.time()
    response_hex = response.hex() if isinstance(response, bytes) else response
    response_hex = utf8_to_hex(response)
    return response_hex,t1,t2


def main():
    ### Retrieve Data ###
    # Log Times
    t0 = time.time()

    # Get Raw Data
    hex_data = []
    try:
        print('Collecting Data...  (CTRL+C when done)\n')
        while True:
            for req in request_with_crc:
                response_hex,t1,t2 = Get_Measurement_In_Hex(dev,req)
                """
                # for negative values
                if response_hex[6] == 'c':
                    response_hex = response_hex.encode('utf-8')
                    #response_hex = bytes([~byte & 0xFF for byte in response_hex])
                    
                    response_hex = str(response_hex)
                """
                hex_data += [response_hex, t2,],
                t3 = time.time()
                time.sleep(INTERVAL_TIME) #- WAIT_TIME - (t1-t3))
    except KeyboardInterrupt:
        pass

    
    # Format Data    
    l = []
    for resp in hex_data:
        value = resp[0][10:14]
        measurement = hex_to_decimal(value)
        l += measurement, (resp[1]-hex_data[0][1]),
    measurements = [l[x:x+(2*len(modbus_request))] for x in range(0, len(l),(2*len(modbus_request)))]

    fields = []
    for request in modbus_request:
        
        fields += [request,f"{request}(time)"]


    ### Save to CSV Files ###
    print()
    print(fields)
    pp.pprint(measurements)
    print('\nDone!\n')
    with open(f'data/{filename}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(fields)
        writer.writerows(measurements)
    print(f'File saved at data/{filename}.csv')

    with open(f'.logs/{filename}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(fields)
        writer.writerows(hex_data)

if __name__ == "__main__":
    main()

"""
TODO:
fix time drift
Add command line arguments
    ex.
    --measurement trp -m trp
    --filename <filename> -f <filename> (auto .csv)
    --interval <time> -i <time> 
"""
