import serial
import time
import math
import csv

# Initialize variables to store latest values of each data type as arrays
latest_GPGGA_data = []
latest_GNRMC_data = []
latest_GNGSA_data = []
latest_hdop_factor = None

# CSV file fieldnames
fieldnames = ["time","GNGGA", "GNRMC", "GNGSA", "HDOP","azimuth"]

camera_data = ['$GNGGA', '202447.000', '5052.83535', 'N', '00442.47824', 'E', '1', '13', '1.1', '53.1', 'M', '45.4', 'M', '', '*70']

def calculate_horizontal_dilution(hdop):
    # Conversion factor to estimate horizontal error from HDOP
    conversion_factor = 3  # Adjust this value as needed
    
    # Calculate horizontal error in meters
    horizontal_error = hdop * conversion_factor
    
    return horizontal_error


def calculate_azimuth(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences in longitude and latitude
    delta_lon = lon2_rad - lon1_rad
    
    # Calculate azimuth (bearing)
    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    # Convert azimuth from radians to degrees
    azimuth_rad = math.atan2(y, x)
    azimuth_deg = math.degrees(azimuth_rad)
    
    # Ensure azimuth is in the range [0, 360)
    azimuth_deg = (azimuth_deg + 360) % 360
    
    return azimuth_deg




while True:
    time.sleep(2)
    
    # Open serial connection
    ser = serial.Serial("/dev/serial0", 9600, timeout=1)
    
    # Read data from GPS module
    newdata = ser.read(1000)
    
    try:
        newdata_str = newdata.decode('ASCII')
    except UnicodeDecodeError as e:
        print("Error decoding data:", e)
        continue  # Skip processing this batch of data

    lines = newdata_str.split('\r\n')
    
    # Parse each line to identify the type of NMEA sentence
    for line in lines:
        if line.startswith("$GNGSA"):
            # Split the GNGSA sentence by commas
            parts = line.split(',')
            # Extract the HDOP value (index 16)
            if len(parts) > 16:
                latest_hdop_factor = float(parts[16])
                horizontal_error = calculate_horizontal_dilution(latest_hdop_factor)
                #print("Estimated Horizontal Positioning Error (meters):", horizontal_error)
                
            # Update the latest GNGSA data as an array parsed by ','
            latest_GNGSA_data = parts
                
        elif line.startswith("$GNGGA"):
            # Update the latest GPGGA data as an array parsed by ','
            latest_GNGGA_data = line.split(',')
            
        elif line.startswith("$GNRMC"):
            # Update the latest GNRMC data as an array parsed by ','
            latest_GNRMC_data = line.split(',')
            
    # Close serial connection
    ser.close()
    
        # Example coordinates for two points
    lat1 = float(camera_data[2])/100  # Latitude of point 1
    lon1 = float(camera_data[4])/100 # Longitude of point 1
    lat2 = float(latest_GNGGA_data[2])/100  # Latitude of point 2
    lon2 = float(latest_GNGGA_data[4])/100  # Longitude of point 2

    # Calculate azimuth between the two points
    azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
    print("Azimuth (bearing) between the two coordinates:", azimuth)

    t = time.time()

    try:
        with open('gps_data_raw.csv', 'a', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writerow({
                "time": t,
                "GNGGA": latest_GNGGA_data,
                "GNRMC": latest_GNRMC_data,
                "GNGSA": latest_GNGSA_data,
                "HDOP": latest_hdop_factor,
                "azimuth":azimuth,
            })
    except ValueError as e:
        print("Error decoding data:", e)
        continue  # Skip processing this batch of data