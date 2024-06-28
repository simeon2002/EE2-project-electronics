from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

# Connect to MySQL database
try:
    db = mysql.connector.connect(
        host="mysql.studev.groept.be",
        user="a23ib2d03",
        password="secret",
        database="a23ib2d03"
    )
    print("Connection to MySQL database successful.")
except mysql.connector.Error as e:
    print("Error connecting to MySQL database:", e)

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/import_mpu_data', methods=['GET'])
def import_mpu_data():
    try:
        # Extract variables from the request URL
        t = request.args.get('t')
        Ax = request.args.get('Ax')
        Ay = request.args.get('Ay')
        Az = request.args.get('Az')
        Gx = request.args.get('Gx')
        Gy = request.args.get('Gy')
        Gz = request.args.get('Gz')
        
        # Insert data into the MySQL database
        cursor = db.cursor()

        #
        sql = "INSERT INTO mpu_data (horseID, t, Ax, Ay, Az, Gx, Gy, Gz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (1, t, Ax, Ay, Az, Gx, Gy, Gz)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        
        print("Data imported successfully into MySQL database.")
        
        # Return a success message
        return jsonify({"message": "Data imported successfully into MySQL database."}), 200
    except Exception as e:
        # Return an error message
        return jsonify({"error": str(e)}), 500




@app.route('/set_alarm/<int:horse_id>', methods=['GET'])
def set_alarm(horse_id):
    try:
        # Insert data into the MySQL database
        cursor = db.cursor()

        # Update the alarm status for the specified horse
        sql = "UPDATE Horse SET alarm = 1 WHERE horseID = %s;"
        cursor.execute(sql, (horse_id,))  # Convert horse_id to tuple explicitly
        db.commit()
        cursor.close()
        
        # Log a success message
        print("Alarm set successfully for horse with ID:", horse_id)
        
        # Return a success message
        return jsonify({"message": f"Alarm set successfully for horse with ID: {horse_id}"}), 200
    
    except Exception as e:
        # Log any errors that occur
        print("An error occurred:", str(e))
        
        # Return an error message
        return jsonify({"error": "An error occurred while setting the alarm."}), 500

@app.route('/import_gps_data', methods=['GET'])
def import_gps_data(camera_id):
    try:

        GNGGA = request.args.get("GNGGA")
        GNRMC = request.args.get("GNRMC")
        GNGSA = request.args.get("GNGSA")
        HDOP = request.args.get("HDOP")
        azimuth = request.args.get("azimuth")
        
        # Insert data into the MySQL database
        cursor = db.cursor()

        #
        sql = "INSERT INTO gps_data (horseID, GNGGA, GNRMC,GNGSA, HDOP, azimuth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (1, GNGGA, GNRMC, GNGSA, HDOP, azimuth)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        
        print("Data imported successfully into MySQL database.")
        
        # Return a success message
        return jsonify({"message": "Data imported successfully into MySQL database."}), 200
    except Exception as e:
        # Return an error message
        return jsonify({"error": str(e)}), 500
    
@app.route('/import_lat_lon/<int:camera_id>', methods=['GET'])
def import_latlon_data(camera_id):
    try:

        lat = request.args.get("lat")
        lon = request.args.get("lon")
        
        
        # Insert data into the MySQL database
        cursor = db.cursor()

        #
        sql = "UPDATE Horse SET latitude = %s, longitude = %s WHERE horseID = %s"
        val = (lat, lon, camera_id)
        cursor.execute(sql, val)
        db.commit()     
        cursor.close()
        
        print("Data imported successfully into MySQL database.")
        
        # Return a success message
        return jsonify({"message": "Data imported successfully into MySQL database."}), 200
    except Exception as e:
        # Return an error message
        return jsonify({"error": str(e)}), 500


@app.route('/get_servo_values/<int:camera_id>', methods=['GET'])
def get_servo_values(camera_id):
    try:
        cursor = db.cursor(dictionary=True)
        # Query to select alpha, beta, and origin_azimuth columns from the servo table for a specific cameraID
        sql = "SELECT alpha, beta, origin_azimuth FROM a23ib2d03.servo WHERE cameraID = %s;"
        cursor.execute(sql, (camera_id,))
        
        row = cursor.fetchone()
        cursor.close()

        if row:
            # Return the found row as JSON
            return jsonify(row), 200
        else:
            # Return a message indicating no data was found for the provided cameraID
            return jsonify({"message": "No data found for the provided cameraID."}), 404
    except Exception as e:
        # Log any errors that occur
        print("An error occurred:", str(e))
        
        # Return an error message
        return jsonify({"error": "An error occurred while fetching servo values."}), 500


@app.route('/push_servo_values', methods=['GET'])
def update_servo_values():
    try:
        # Extract the cameraID, alpha, and beta values from the query parameters
        camera_id = request.args.get('cameraID', type=int)
        alpha = request.args.get('alpha', type=float)
        beta = request.args.get('beta', type=float)
        
        # Check if all required parameters are provided
        if camera_id is None or alpha is None or beta is None:
            return jsonify({"error": "Missing data for cameraID, alpha, or beta"}), 400

        # Update the servo table with the new alpha and beta values for the given cameraID
        cursor = db.cursor()
        sql = "UPDATE a23ib2d03.servo SET alpha = %s, beta = %s WHERE cameraID = %s;"
        cursor.execute(sql, (alpha, beta, camera_id))
        db.commit()
        affected_rows = cursor.rowcount
        cursor.close()

        # Check if the update was successful
        if affected_rows > 0:
            return jsonify({"message": f"Successfully updated servo values for cameraID {camera_id}"}), 200
        else:
            return jsonify({"message": "No rows updated. Please check if the cameraID exists."}), 404

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({"error": "An error occurred while updating servo values."}), 500



if __name__ == "__main__":
    app.run(debug=True)
