#!/bin/bash

echo "Running mining_raw_data.py in the background..."
python3 mining_raw_data.py &


echo "Running publish_mpu.py in the background..."
python3 publish_mpu.py &

echo "Running publish_gps.py in the background..."
python3 publish_gps.py &
 
echo "Running gps_module2.py in the background..."
python3 gps_module2.py &

echo "Running mine_data.sh in the background..."
python3 temperature_sens.py &

echo "All scripts have been started in separate processes."

sleep 360

pkill -f "python3"