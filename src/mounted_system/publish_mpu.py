import threading
import paho.mqtt.client as mqtt
import time 
import traceback

mqttBroker = "test.mosquitto.org"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

 
try:
    client.connect(mqttBroker)
except Exception as e:
    print("Error connecting to MQTT broker:", e)
    traceback.print_exc()  # Print traceback for detailed error information


def start_mpu():
    try:
        
        with open('mpu_data_raw.csv', 'r') as mpu_file:
            for line in mpu_file:
                try:
                    client.publish("mpu_data", line)  # Publish data to MQTT topic
                    print("Published:", line)
                    
                except Exception as e:
                    print("Error publishing message to MQTT topic:", e)
                    traceback.print_exc()  # Print traceback for detailed error information
                time.sleep(0.05)  # Adjust sleep time as needed
            global current_mpu_position
            current_mpu_position = mpu_file.tell()

            
    except Exception as e:
        print("Error reading mpu_file:", e)
        traceback.print_exc()  # Print traceback for detailed error information


def wait_for_newline_mpu():
    try:
        global current_mpu_position
        while True:
            with open('mpu_data_raw.csv', 'r') as mpu_file:
                # Move to the next line after the current position
                mpu_file.seek(current_mpu_position)
                line = mpu_file.readline().strip()
                if not line:
                    # No new data, wait and continue
                    time.sleep(0.1)
                    continue
                
                # Publish the line to the MQTT topic
                client.publish("mpu_data", line)  # Publish data to MQTT topic
                print("Published:", line)

                # Update current_gps_position
                current_mpu_position = mpu_file.tell()

                time.sleep(0.05)  # Adjust sleep time as needed
    except Exception as e:
        print("Error reading gps_file or publishing message to MQTT topic:", e)
        traceback.print_exc()  # Print traceback for detailed error information





start_mpu()
wait_for_newline_mpu()




