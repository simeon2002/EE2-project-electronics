import requests

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
    except Exception as e:
        # If an exception occurred during the request, print the error
        print("An error occurred:", str(e))


def push_servo_values(camera_id, alpha, beta, origin_azimuth):
    # Construct the full URL with parameters
    API_URL = f"{push_call}?cameraID={camera_id}&alpha={alpha}&beta={beta}&origin_azimuth={origin_azimuth}"
    
    try:
        # Send a GET request to the API
        response = requests.get(API_URL)
        
        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Convert the response JSON content to a Python dictionary and print it
            data = response.json()
            print("Response from server:", data)
        else:
            # If the response status code is not 200, print an error message with the status code
            print("Failed to push servo values. Status code:", response.status_code)
    except Exception as e:
        # If an exception occurred during the request, print the error
        print("An error occurred:", str(e))

if __name__ == "__main__":
    get_servo_values()

    camera_id = 1
    alpha = 0.0
    beta = 0.0
    origin_azimuth = 0
    push_servo_values(camera_id, alpha, beta, origin_azimuth)


