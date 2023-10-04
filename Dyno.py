import time
import datetime
import csv
import pprint
import argparse
from pylibftdi import Device

Start_Date = datetime.datetime.now()
parser = argparse.ArgumentParser()
pp = pprint.PrettyPrinter(indent=2)

parser.add_argument('--measurment', dest='measurement', type=str, help='add measurement (Default is torque, rpm, and power)')
parser.add_argument('-m', dest='measurement', type=str, help='add measurement (Default is torque(t), rpm(r), and power(p))',)
parser.add_argument('--interval', dest='interval', type=float, help='specify interval (Default is 0.125s. Must be greater than 0.1s)')
parser.add_argument('-i', dest='interval', type=float, help='specify interval (Default is 0.125s. Must be greater than 0.1s)')
parser.add_argument('--filename', dest='filename', type=str, help='specify filename (Default is output(<time>) You don\'t have to include .csv)')
parser.add_argument('-f', dest='filename', type=str, help='specify filename (Default is output(<time>) You don\'t have to include .csv)')
args = parser.parse_args()

measurement = args.measurement
if measurement == None: measurement = 'trp'
interval_time = args.interval
if interval_time == None: interval_time = 0.125
filename = f'{args.filename}.csv'
if args.filename == None: filename = f'output({Start_Date})'


print(f'Measurment(s): {measurement}')
print(f'Interval: {interval_time}')
print(f'Filename: {filename}')

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
    # Define the Modbus request bytes
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
    # Log Times
        wait_time = 0.1 # must be less than interval time
        T0 = time.time()

    # Get Raw Data
        hex_data = []
        try:
            print('Collecting Data...  (CTRL+C when done)\n')
            while True:
                for req in request_with_crc.items():
                    T1 = time.time()
                    dev.write(req[1])
                    time.sleep(wait_time)
                    T2 = time.time()
                    response = dev.read(64)
                    response_hex = response.hex() if isinstance(response, bytes) else response
                    response_hex = utf8_to_hex(response)
                    hex_data += [response_hex, T2,],
                    T3 = time.time()
                    time.sleep(interval_time - wait_time - (T1-T3))
        except KeyboardInterrupt:
            pass

        
    # Format Data    
    l = []
    for resp in hex_data:
        value = resp[0][10:14]
        #print(value)
        measurement = hex_to_decimal(value)
        l += measurement, (resp[1]-hex_data[0][1]),
    measurements = [l[x:x+(2*len(modbus_request))] for x in range(0, len(l),(2*len(modbus_request)))]

    fields = []
    for request in modbus_request:
        fields += [request,f"{request}(time)"]

    print(fields)
    pp.pprint(measurements)
    print('\nDone!')
    with open(f'data/{filename}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(fields)
        writer.writerows(measurements)
    print(f'File saved at data/{filename}.csv')


if __name__ == "__main__":
    main()

"""
TODO:
xAdd timers
xAdd Timestamps
xAdd loops
xFormat for csv properly
xSetup Intervals
Add command line arguments
    ex.
    --measurement trp -m trp
    --filename <filename> -f <filename> (auto .csv)
    --interval <time> -i <time> 
"""
