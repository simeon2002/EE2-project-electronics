import ast
import csv
import datetime
import math
import threading
import time
import os
import traceback
import requests
import json

# Path to the CSV file
mpu_filename = "mpu_data.csv"
gps_filename = "gps_data.csv"

cam1 = 50.5284050
cam2 = 4.4248647
GNGGA_camera = ['$GNGGA', '194848.000', '5052.84050', 'N', '00442.48647', 'E', '1', '11', '0.9', '15.1', 'M', '45.4', 'M', '', '*73']
gps_fieldnames = ["time","GNGGA", "GNRMC", "GNGSA", "HDOP","azimuth"]

def calculate_azimuth_from_coordinates(lat1, lon1, lat2, lon2):
    print("math")
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    print("math")
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


#   This function will reformat the relative orientation between the camera and the horse.
#   First we calculated the azimuth based on the given coördinates by the gps.
#   But we can only use these if the camera's start position is oriented to the north.
#   So we will recalculate the azimuth so that the azimuth angle of 0 degrees is equal to the start position of the camera.
#   Additionally, we rebase the azimuth from -90 degrees to 90 degrees, not from 0 to 360 degrees. 
#   This because the current servomotor has a range of 180 degrees.
#   Then we round up to multiples of 5.
def calculate_servo_angle(original_azi_camera, relative_azi_cam_to_horse):
    print("angle")
    relative = (relative_azi_cam_to_horse - original_azi_camera)%360

    #Horse in physical range camera:
    if abs(relative)<90 or abs(relative)>270:
        if abs(relative)>270:
            relative = relative-360
        
    
    #Horse not in physical range camera, move to limit closest to the actual location:
    else:
        if relative>180:
            relative = -90

        else: 
            relative = 90

    #round up to multiples of 5        
    relative = math.ceil(relative/5)*5

    return relative

# Function to read accelerometer data from CSV file
def read_accelerometer_data_from_csv(mpu_filename):
    with open(mpu_filename, 'r') as file:
        reader = csv.reader(file)
        # Skip header if present
        next(reader, None)
        for row in reader:
            yield float(row[1])  # Assuming Ax values are in the second column


def push_mpu_data_to_database(row):
    try:
        # Define the URL and parameters
        url = 'http://127.0.0.1:5000/import_mpu_data'
        if row[-1].startswith('"') and row[-1].endswith('"'):
            row[-1] = row[-1][1:-1]

        # Convert timestamp to datetime object
        timestamp = float(row[0])  # Convert timestamp string to float
        datetime_obj = datetime.datetime.fromtimestamp(timestamp)  # Convert timestamp to datetime object

        # Format datetime object as string in MySQL datetime format with milliseconds
        datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Trim microseconds to milliseconds

        # Trim double quotes from the 'Gz' value if present
        gz_value = row[6].strip('"') if row[6].startswith('"') or row[6].endswith('"') else row[6]

        # Construct params dictionary
        params = {
            't': datetime_str,
            'Ax': row[1],
            'Ay': row[2],
            'Az': row[3],
            'Gx': row[4],
            'Gy': row[5],
            'Gz': gz_value
        }

        # Make the GET request
        response = requests.get(url, params=params)


        # Check if the request was successful (status code 200)d
        if response.status_code == 200:
            print("Data imported successfully.")
        else:
            print("Error:", response.text)

    except Exception as e:
        print("Error:", e)
        traceback.print_exc()  # Print traceback for detailed error information


def push_gps_data_to_database(row):
    try:

        #row consists of : row = [[]]
        # Define the URL and parameters
        url = 'http://127.0.0.1:5000/import_gps_data'
        if row[-1].startswith('"') and row[-1].endswith('"'):
            row[-1] = row[-1][1:-1]

        # Convert timestamp to datetime object
        timestamp = float(row[0])  # Convert timestamp string to float
        datetime_obj = datetime.datetime.fromtimestamp(timestamp)  # Convert timestamp to datetime object

        # Format datetime object as string in MySQL datetime format with milliseconds
        datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Trim microseconds to milliseconds

        # Trim double quotes from the 'Gz' value if present
        gz_value = row[6].strip('"') if row[6].startswith('"') or row[6].endswith('"') else row[6]

        # Construct params dictionary
        params = {
            't': datetime_str,
            'Ax': row[1],
            'Ay': row[2],
            'Az': row[3],
            'Gx': row[4],
            'Gy': row[5],
            'Gz': gz_value
        }

        # Make the GET request
        response = requests.get(url, params=params)


        # Check if the request was successful (status code 200)d
        if response.status_code == 200:
            print("Data imported successfully.")
        else:
            print("Error:", response.text)

    except Exception as e:
        print("Error:", e)
        traceback.print_exc()  # Print traceback for detailed error information

def read_last_accelerometer_data_from_csv(mpu_filename):
    with open(mpu_filename, 'r') as mpu_file:
        # Initialize variables for the last row
        last_ax = 0
        last_row = None
        # Read each line in reverse until a complete row is found
        for line in reversed(list(mpu_file)):
            # Strip trailing whitespace and split by comma
            row = line.strip().split(',')
            # Check if the row contains the expected number of elements
            if len(row) == 7:
                last_row = row
                last_ax = float(last_row[1])  # Assuming Ax values are in the second column
                break
        if last_row is not None:
            print(last_row)
            push_mpu_data_to_database(last_row)
        return last_ax

def read_last_row_from_gpsfile(filename):
    last_row = None
    
    # Open the file in read mode
    with open(filename, 'r') as file:
        # Read each line in reverse order
        for line in reversed(list(file)):
            try:
                # Split the payload by commas
                payload_parts = line.strip().split(",")
                
                # Decode the payload and safely evaluate the string representation of the tuple
                data = ast.literal_eval(",".join(payload_parts))  # Skipping timestamp part
                             
                      # Set last_row to the extracted dictionary
                last_row = data
                break     
                
            except Exception as e:
                print("Error processing message:", e)
                traceback.print_exc()
        
    
    return last_row
    

# URL of the API endpoint (change the base URL to match your actual Flask app's URL)
get_call = "http://localhost:5000/get_servo_values/1"
push_call = "http://localhost:5000/push_servo_values"


def get_servo_values():
    try:
        # Send a GET request to the API
        response = requests.get(get_call)
        
        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Convert the response JSON content to a Python dictionary and print it
            data = response.json()
            print("Servo Values for CameraID 1:", data)
        else:
            # If the response status code is not 200, print an error message with the status code
            print("Failed to get servo values. Status code:", response.status_code)

        return data
    
    except Exception as e:
        # If an exception occurred during the request, print the error
        print("An error occurred:", str(e))

def push_servo_values(camera_id, alpha, beta, origin_azimuth):
    # Construct the full URL with parameters

    print("pushed")
    API_URL = f"{push_call}?cameraID={camera_id}&alpha={alpha}&beta={beta}&origin_azimuth={origin_azimuth}"
    
    try:
        # Send a GET request to the API
        response = requests.get(API_URL)
        
        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Convert the response JSON content to a Python dictionary and print it
            data = response.json()
            print("Response from server:", data)
            return data
        else:
            # If the response status code is not 200, print an error message with the status code
            print("Failed to push servo values. Status code:", response.status_code)
    except Exception as e:
        # If an exception occurred during the request, print the error
        print("An error occurred:", str(e))

def extract_float_value(s):
    # Remove non-numeric characters and convert to float
    numeric_chars = [c for c in s if c.isdigit() or c == '.']
    comma_index = s.find(',')
    if comma_index != -1:
        numeric_chars.insert(comma_index, ',')  # Reinsert comma at original position
    return float(''.join(numeric_chars))

def get_latitude_longitude(array):
    
    latitude = extract_float_value(array[2])/100
    longitude = extract_float_value(array[4])/100

    latlon = [latitude, longitude]
    return latlon

def set_alarm(ID):
    try:
        horseID = ID
        # Define the URL with the horse ID as part of the path
        url = f'http://127.0.0.1:5000/set_alarm/{horseID}'
        
        #this module will move the camera to the horse
        row = read_last_row_from_gpsfile(gps_filename)
        GNGGA_array = row[1]
        GNGGA_array = GNGGA_array.split(",")
        latlon = get_latitude_longitude(GNGGA_array)

        
        print("latitude1:",latlon[0])
        print("longitude1",latlon[1])

        cam_latlon = get_latitude_longitude(GNGGA_camera)
        print("latitude2",cam1)
        print("longitude2", cam2)
        
        azimuth = calculate_azimuth_from_coordinates(cam1, cam2, latlon[0], latlon[1])
        print("azimuth", azimuth)
        old_servo_values = get_servo_values()
        origin_azimuth = old_servo_values.get("origin_azimuth")

        alpha = calculate_servo_angle(float(origin_azimuth), azimuth)

        push_servo_values(1,float(alpha),0,origin_azimuth)

        # Make the GET request without query parameters
        response = requests.get(url)

        # Check the response status code
        if response.status_code == 200:
            print("Alarm set successfully for horse with ID:", horseID)
        else:
            print("Failed to set alarm for horse with ID:", horseID)

    

    except requests.exceptions.RequestException as e:
        print("Error making the request:", str(e))
    except Exception as e:
        print("Other error occurred:", str(e))
 
server_url = "http://localhost:5000/import_lat_lon/1"
def push_latlon_loop():
    """
    This function reads latitude and longitude from a GPS file and pushes them to a server continuously.

    Args:
    gps_filename (str): The filename of the GPS file.
    server_url (str): The URL of the server to push latitude and longitude.

    Returns:
    None

    """
    while True:    
        try:
            # Read latitude and longitude from the GPS file
            row = read_last_row_from_gpsfile(gps_filename)
            GNGGA_array = row[1].split(",")
            latlon = get_latitude_longitude(GNGGA_array)
            latitude = latlon[0]
            longitude = latlon[1]

            # Make a GET request to the server with latitude and longitude parameters
            response = requests.get(server_url, params={"lat": latitude, "lon": longitude})
            if response.status_code == 200:
                print("Latitude and longitude pushed successfully to the server.")
            else:
                print("Failed to push latitude and longitude to the server:", response.text)

        except Exception as e:
            print("Error:", e)
            traceback.print_exc()

        time.sleep(3)  # Adjust the sleep time as needed

last_ax_value = read_last_accelerometer_data_from_csv(mpu_filename)
    # Initialize last modified time of the file
last_modified_time = os.path.getmtime(mpu_filename)
# Print the last Ax value
print("Last Ax value:", last_ax_value)            

last_gps_value = read_last_row_from_gpsfile(gps_filename)



print("Last gps value",last_gps_value[1])
# Constants
threshold_lower = -4.5
threshold_upper = 4.5
detection_duration = 10  # in seconds


start_time = None
detected = False


set_alarm(1)
push_thread = threading.Thread(target=push_latlon_loop)
push_thread.daemon = True  # Daemonize the thread to terminate it with the main thread
push_thread.start()


# Main loop
while True:
    # Check if the file has been modified
    
    current_modified_time = os.path.getmtime(mpu_filename)
    if current_modified_time != last_modified_time:
        last_modified_time = current_modified_time  # Update last modified time

        

        # Read accelerometer data from CSV file
        # Read the last Ax value from the CSV file
        last_ax_value = read_last_accelerometer_data_from_csv(mpu_filename)
        
        # Print the last Ax value
        print("Last Ax value:", last_ax_value)  
        print("Last gps value:", last_gps_value)
            # Check if the last_ax_value is within the threshold
        if threshold_lower <= last_ax_value <= threshold_upper: 
            if start_time is None:
                start_time = time.time()  # Start timer
            elif time.time() - start_time >= detection_duration:
                # Alarm condition met, print alarm
                print("Alarm: Ax value remained within range for {} seconds.".format(detection_duration))
                horseID = 1
                set_alarm(horseID)

                
                # Reset start_time to avoid continuous alarms
                start_time = None
        else:
            start_time = None  # Reset timer if value is out of range

     # Check file modification every second


