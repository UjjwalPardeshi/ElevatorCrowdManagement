import cv2
import imutils
import requests
import time as t
import numpy as np
import threading
import firebase_admin
from firebase_admin import credentials, db
from openvino.runtime import Core
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Use environment variables for sensitive data
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
database_url = os.getenv("DATABASE_URL")
detection_model_xml = os.getenv("MODEL_XML_PATH")

# Initialize Firebase
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})

# Initialize OpenVINO model
core = Core()
detection_model = core.read_model(model=detection_model_xml)
compiled_model = core.compile_model(model=detection_model, device_name="CPU")
input_layer = compiled_model.input(0)
output_layer = compiled_model.output(0)

# Variables for crowd detection
box_lock = threading.Lock()  # Thread-safe access to 'box' and 'boxlist'
stopflag = threading.Event()  # Use an event to stop the inference thread gracefully

# Firebase update function
def update_firebase(camera_id, people_count, crowd_density, location):
    try:
        print(f"Updating Firebase for {camera_id} with {people_count} people and {crowd_density} crowd density")
        ref = db.reference(f'cameras/{camera_id}')
        ref.set({
            'people_count': people_count,
            'crowd_density': crowd_density,
            'location': location,  # Add location to Firebase
            'timestamp': t.strftime("%Y-%m-%dT%H:%M:%S"),
            'send_alert': crowd_density == 'dense'  # Trigger Firebase function if crowd is dense

        })
    except Exception as e:
        print(f"Error updating Firebase: {e}")

# Inference function for a single camera
def inference(camera_id, url, location):
    boxlist = []
    box = [0]

    while not stopflag.is_set():
        try:
            # Fetch the image from the camera
            img_resp = requests.get(url, timeout=1)  # Timeout reduced for faster retries
            if img_resp.status_code == 200:
                img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
                img = cv2.imdecode(img_arr, -1)
                img = imutils.resize(img, width=input_layer.shape[3], height=input_layer.shape[2])
                resized_image = cv2.resize(src=img, dsize=(input_layer.shape[3], input_layer.shape[2]))
                input_data = np.expand_dims(np.transpose(resized_image, (2, 0, 1)), 0).astype(np.float32)

                # Run inference
                request = compiled_model.create_infer_request()
                request.infer(inputs={input_layer.any_name: input_data})
                result = request.get_output_tensor(output_layer.index).data

                # Post-process results
                boxes = []
                frame_height, frame_width = img.shape[:2]
                for detection in result[0][0]:
                    label = int(detection[1])
                    conf = float(detection[2])
                    if conf > 0.3:
                        xmin = int(detection[3] * frame_width)
                        ymin = int(detection[4] * frame_height)
                        xmax = int(detection[5] * frame_width)
                        ymax = int(detection[6] * frame_height)
                        boxes.append([xmin, ymin, xmax, ymax])
                        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 255), 3)
                        cv2.putText(img, f"Person {len(boxes)}", (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                # Update box list for crowd detection
                with box_lock:
                    boxlist.append(len(boxes))
                    box = [max(boxlist, default=0)]
            else:
                print(f"Error fetching image from {camera_id}, status: {img_resp.status_code}")
        except Exception as e:
            print(f"Error during inference for {camera_id}: {e}")

        # Push data to Firebase every second
        with box_lock:
            numberofpeople = max(box)
        crowd_density = "dense" if numberofpeople >= 20 else "medium" if 10 <= numberofpeople < 20 else "low"
        update_firebase(camera_id=camera_id, people_count=numberofpeople, crowd_density=crowd_density, location=location)

        # Reset box and boxlist for the next iteration
        with box_lock:
            box = [0]
            boxlist = []

        # Sleep to avoid overwhelming the server with requests
        t.sleep(1)


# Start inference for two cameras in separate threads
camera1_url = "http://10.9.0.41:8080/shot.jpg"  # Camera 1 URL
camera2_url = "http://192.168.29.35:8080/shot.jpg"  # Camera 2 URL
camera3_url = "http://192.168.29.34:8080/shot.jpg"  # Camera 3 URL
camera4_url = "http://192.168.29.52:8080/shot.jpg"  # Camera 4 URL

# Assign locations to each camera
location_camera1_2 = "Placement Office"
location_camera3_4 = "I Mac Lab"

# Start inference threads with location
infr_thread_camera1 = threading.Thread(target=inference, args=("camera1", camera1_url, location_camera1_2))
infr_thread_camera2 = threading.Thread(target=inference, args=("camera2", camera2_url, location_camera1_2))
infr_thread_camera3 = threading.Thread(target=inference, args=("camera3", camera3_url, location_camera3_4))
infr_thread_camera4 = threading.Thread(target=inference, args=("camera4", camera4_url, location_camera3_4))

infr_thread_camera1.start()
infr_thread_camera2.start()
infr_thread_camera3.start()
infr_thread_camera4.start()

# Main server loop (no client required)
try:
    while not stopflag.is_set():
        t.sleep(1)  # Server can run continuously and handle shutdown via KeyboardInterrupt

except KeyboardInterrupt:
    print("Shutting down server...")
    stopflag.set()
    infr_thread_camera1.join()
    infr_thread_camera2.join()
    infr_thread_camera3.join()
    infr_thread_camera4.join()
print("Server stopped.")