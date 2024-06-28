import threading
import paho.mqtt.client as mqtt
import time 
import traceback
import os

mqttBroker = "test.mosquitto.org"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

 
try:
    client.connect(mqttBroker)
except Exception as e:
    print("Error connecting to MQTT broker:", e)
    traceback.print_exc()  # Print traceback for detailed error information


# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'gps_data_raw.csv')

def start_gps():
    try:
        with open(file_path, 'r') as gps_file:
            
            for line in gps_file:
                try:
                    client.publish("gps_data", line)  # Publish data to MQTT topic
                    print("Published:", line)
                except Exception as e:
                    print("Error publishing message to MQTT topic:", e)
                    traceback.print_exc()  # Print traceback for detailed error information
                time.sleep(0.05)  # Adjust sleep time as needed
            global current_gps_position
            current_gps_position = gps_file.tell()    
    except Exception as e:
        print("Error reading gps_file:", e)
        traceback.print_exc()  # Print traceback for detailed error information



def wait_for_newline_gps():
    try:
        global current_gps_position
        while True:
            with open(file_path, 'r') as gps_file:
                # Move to the next line after the current position
                gps_file.seek(current_gps_position)
                line = gps_file.readline().strip()
                if not line:
                    # No new data, wait and continue
                    time.sleep(0.1)
                    continue
                
                # Publish the line to the MQTT topic
                client.publish("gps_data", line)  # Publish data to MQTT topic
                print("Published:", line)

                # Update current_gps_position
                current_gps_position = gps_file.tell()

                time.sleep(0.05)  # Adjust sleep time as needed
    except Exception as e:
        print("Error reading gps_file or publishing message to MQTT topic:", e)
        traceback.print_exc()  # Print traceback for detailed error information





start_gps()
wait_for_newline_gps()
            



