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
        ref.update({
            'people_count': people_count,
            'crowd_density': crowd_density,
            'location': location,
            'timestamp': t.strftime("%Y-%m-%dT%H:%M:%S"),
            'send_alert': crowd_density == 'dense'
        })
    except Exception as e:
        print(f"Error updating Firebase: {e}")

# Inference function for a single camera, checking if it's active
def inference(camera_id, url, location):
    boxlist = []
    box = [0]

    while not stopflag.is_set():
        try:
            # Check if camera is active
            isactive_ref = db.reference(f'cameras/{camera_id}/isactive')
            isactive = isactive_ref.get()
            
            if not isactive:
                print(f"Camera {camera_id} is inactive. Skipping inference.")
                # Update Firebase status
                update_firebase(camera_id, 0, "Under Maintenance", location)
                t.sleep(5)  # Sleep for a while before checking again
                continue
            
            # Fetch the image from the camera
            img_resp = requests.get(url, timeout=1)
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

# Start inference for cameras in separate threads
camera_data = {
    "camera1": {"url": "http://10.9.0.41:8080/shot.jpg", "location": "Placement Office"},
    "camera2": {"url": "http://10.9.10.108:8080/shot.jpg", "location": "Placement Office"},
    "camera3": {"url": "http://10.9.77.123:8080/shot.jpg", "location": "I Mac Lab"},
    "camera4": {"url": "http://10.9.80.97:8080/shot.jpg", "location": "I Mac Lab"},
}

# Dynamically create threads for each camera
for camera_id, camera_info in camera_data.items():
    threading.Thread(target=inference, args=(camera_id, camera_info["url"], camera_info["location"])).start()

# Main server loop (no client required)
try:
    while not stopflag.is_set():
        t.sleep(1)
except KeyboardInterrupt:
    print("Shutting down server...")
    stopflag.set()
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            thread.join()
print("Server stopped.")

