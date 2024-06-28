import threading
import paho.mqtt.client as mqtt
import time
import csv
import traceback
import ast
import requests

# Define the field names
mpu_fieldnames = ["time", "Ax", "Ay", "Az", "Gx", "Gy", "Gz"]


timeout_for_closeconnection = 360  # in seconds


last_message_time = time.time()



def start_writing_mpu():
    with open('mpu_data.csv', mode='w', newline='') as file:
        mpu_writer = csv.DictWriter(file, fieldnames=mpu_fieldnames)

        global mpu_buffer
        mpu_buffer= []  # Buffer to accumulate rows before writing to the file

        def write_buffer(mpu_buffer):
            if mpu_buffer:
                # Iterate over each data dictionary in the buffer
                for data_dict in mpu_buffer:
                    # Write the data dictionary to the file along with the timestamp
                    mpu_writer.writerow(data_dict)

                # Clear the GPS buffer after writing
                mpu_buffer.clear()

                # Flush the file to ensure data is written immediately
                file.flush()

        def on_message(client, userdata, msg):
            # Split the payload into individual values
            values = msg.payload.decode("utf-8").split(",")

            # Create a dictionary to store the values with their corresponding field names
            data = {mpu_fieldnames[i]: values[i] for i in range(len(mpu_fieldnames))}

            # Write the data to the CSV file
            mpu_writer.writerow(data)

            print("Received message:", data)
            try:
                # Split the payload into individual values
                values = msg.payload.decode("utf-8").split(",")
                global waiting, last_message_time
                waiting = False
                last_message_time = time.time()
                # Check if fieldnames and values have the same length
                if len(mpu_fieldnames) != len(values):
                    print("Error: Length of fieldnames and values lists don't match")
                else:
                    # Create data dictionary
                    data = {mpu_fieldnames[i]: values[i] for i in range(len(mpu_fieldnames))}

                    # Write the data to the CSV file
                    mpu_writer.writerow(data)

                    print("Received message:", data)
            except Exception as e:
                print("Error processing message:", e)
                traceback.print_exc()  # Print traceback for detailed error information



        def timer_write():
                while True:
                    time.sleep(1)  # Adjust the interval as needed
                    write_buffer(mpu_buffer)

        mqttBroker = "test.mosquitto.org"
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        try:
            client.connect(mqttBroker)
        except Exception as e:
            print("Error connecting to MQTT broker:", e)
            traceback.print_exc()
            exit(1)

        client.loop_start()
        client.subscribe("mpu_data")
        client.on_message = on_message

        # Start the timer thread for periodic writing
        timer_thread = threading.Thread(target=timer_write)
        timer_thread.daemon = True  # Daemonize the thread to terminate it with the main thread
        timer_thread.start()

        

        while True:
            waiting_time = time.time() - last_message_time
            if waiting_time > timeout_for_closeconnection:
                write_buffer(mpu_buffer)  # Write remaining data in the buffer
                print("No messages received for", timeout_for_closeconnection, "seconds. Closing CSV file.")
                break
            time.sleep(0.1)

        client.loop_stop()

start_writing_mpu()