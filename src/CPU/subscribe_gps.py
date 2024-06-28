import threading
import paho.mqtt.client as mqtt
import time
import csv
import traceback
import ast
import requests


gps_fieldnames = ["time","GNGGA", "GNRMC", "GNGSA", "HDOP","azimuth"]

timeout_for_closeconnection = 20  # in seconds


last_message_time = time.time()


def start_writing_gps(): 
    with open('gps_data.csv', mode='w', newline='') as file:
        # Create a DictWriter object
        gps_writer = csv.DictWriter(file, fieldnames=gps_fieldnames)
        gps_buffer =[]
        # Define the function to write GPS data to the file
        def write_gps_buffer(gps_buffer):
            if gps_buffer:
                # Iterate over each data dictionary in the buffer
                for data_dict in gps_buffer:
                    # Write the data dictionary to the file along with the timestamp
                    gps_writer.writerow(data_dict)

                # Clear the GPS buffer after writing
                gps_buffer.clear()

                # Flush the file to ensure data is written immediately
                file.flush()



        def on_message(client, userdata, msg):
            try:
                global last_message_time
                last_message_time = time.time()
                
                # Decode the payload and safely evaluate the string representation of the tuple
                data = ast.literal_eval(msg.payload.decode("utf-8"))
                # Split the payload by commas
                payload_parts = msg.payload.decode("utf-8").split(",")

                # Extract the timestamp (first part of the payload)
                timestamp = float(payload_parts[0])
                if isinstance(data, tuple):
                    # Assuming the first element of the tuple is a timestamp, and the rest are data points
                    data_points = data[0:]

                    # Construct a dictionary with field names as keys and data points as values
                    data_dict = {"time": timestamp}  # Add timestamp to the dictionary
                    data_dict.update({gps_fieldnames[i]: data_point for i, data_point in enumerate(data_points)})


                    gps_buffer.append(data_dict)  # Append data to the gps_buffer

                    # If gps_buffer size exceeds a certain threshold, write to the file
                    print(len(gps_buffer))
                    if len(gps_buffer) >= 100:  # Adjust the threshold as needed
                        write_gps_buffer(gps_buffer)

                    print("Received message:", data_dict)
                else:
                    print("Received message is not in the expected format:", data)
            except Exception as e:
                print("Error processing message:", e)
                traceback.print_exc()



        def timer_write():
                while True:
                    time.sleep(1)  # Adjust the interval as needed
                    write_gps_buffer(gps_buffer)

        mqttBroker = "test.mosquitto.org"
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        try:
            client.connect(mqttBroker)
        except Exception as e:
            print("Error connecting to MQTT broker:", e)
            traceback.print_exc()
            exit(1)

        client.loop_start()
        client.subscribe("gps_data")
        client.on_message = on_message

        # Start the timer thread for periodic writing
        timer_thread = threading.Thread(target=timer_write)
        timer_thread.daemon = True  # Daemonize the thread to terminate it with the main thread
        timer_thread.start()

        

        while True:
            waiting_time = time.time() - last_message_time
            if waiting_time > timeout_for_closeconnection:
                write_gps_buffer(gps_buffer)  # Write remaining data in the gps_buffer
                print("No messages received for", timeout_for_closeconnection, "seconds. Closing CSV file.")
                break
            time.sleep(0.1)

        client.loop_stop()


start_writing_gps()
