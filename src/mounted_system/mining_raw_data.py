import smbus
import time
import csv
import RPi.GPIO as GPIO

# Some MPU6050 Registers and their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# Function to initialize MPU6050
def MPU_Init():
    # Write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

# Function to read raw data from MPU6050
def read_raw_data(addr):
    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)

    # Concatenate higher and lower value
    value = ((high << 8) | low)

    # To get signed value from MPU6050
    if value > 32768:
        value -= 65536
    return value

bus = smbus.SMBus(1)
Device_Address = 0x68



MPU_Init()


deltaT = 0.1
TIMETORUN = 1000

# CSV file fieldnames
fieldnames = ["time", "Ax", "Ay", "Az", "Gx", "Gy", "Gz"]

# Open CSV file for writing
with open('mpu_data_raw.csv', 'w', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

# Main loop

    while True:
        t = time.time()
        timestamp = time.time()
        # Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        # Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0

        # Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x / 16384.0 * 9.81
        Ay = acc_y / 16384.0 * 9.81
        Az = acc_z / 16384.0 * 9.81

        # Write data to CSV file
        
        csv_writer.writerow({
            "time": round(t, 3),
            "Ax": round(Ax, 3),
            "Ay": round(Ay, 3),
            "Az": round(Az, 3),
            "Gx": round(Gx, 3),
            "Gy": round(Gy, 3),
            "Gz": round(Gz, 3),
        })

        # Sleep for deltaT seconds
        time.sleep(deltaT)
        
        # Break loop if elapsed time exceeds TIMETORUN
        if time.time() - timestamp > TIMETORUN:
            break
