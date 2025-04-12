import cv2
import numpy as np
from openvino.runtime import Core

# Initialize the video capture object (0 for default camera)
cap = cv2.VideoCapture(1)

# Load OpenVINO model
ie = Core()
model_path = "/var/home/ujjain/Desktop/Smart_lift/ElevatorCrowdManagement/server/person-detection-retail-0013.xml"  # Replace with the path to your model
model = ie.read_model(model_path)
compiled_model = ie.compile_model(model=model, device_name="CPU")

# Get input and output layer information
input_layer = compiled_model.input(0)
output_layer = compiled_model.output(0)

# Define the queue area as ROI (adjust the coordinates based on your queue position)
queue_roi_x, queue_roi_y, queue_roi_w, queue_roi_h = 150, 1, 400, 850  # Adjusted values

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Draw the ROI rectangle around the queue area (for visualization)
    cv2.rectangle(frame, (queue_roi_x, queue_roi_y), 
                  (queue_roi_x + queue_roi_w, queue_roi_y + queue_roi_h), 
                  (146, 255, 0), 2)

    # Crop the frame to the queue ROI
    queue_roi = frame[queue_roi_y:queue_roi_y + queue_roi_h, queue_roi_x:queue_roi_x + queue_roi_w]

    # Preprocess the ROI to match the model's input requirements (height=320, width=544)
    input_image = cv2.resize(queue_roi, (544, 320))  # Note the order: (width, height)
    input_image = input_image.transpose(2, 0, 1)  # Change from HWC to CHW format
    input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension
    input_image = input_image.astype(np.float32)  # Ensure data type is correct

    # Run inference
    results = compiled_model([input_image])[output_layer]

    # Initialize the people count
    people_count = 0

    # Parse results and draw bounding boxes (adjust based on your model's output format)
    for detection in results[0][0]:
        # Each detection is usually in the format: [batch_id, class_id, confidence, x_min, y_min, x_max, y_max]
        confidence = detection[2]
        if confidence > 0.5:  # Adjust the threshold as needed
            people_count += 1  # Increment count for each detected person
            
            x_min = int(detection[3] * queue_roi_w) + queue_roi_x
            y_min = int(detection[4] * queue_roi_h) + queue_roi_y
            x_max = int(detection[5] * queue_roi_w) + queue_roi_x
            y_max = int(detection[6] * queue_roi_h) + queue_roi_y

            # Draw the bounding box on the original frame
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

    # Display the number of detected people on the frame
    cv2.putText(frame, f'People in Queue: {people_count}', (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the result
    cv2.imshow('Queue Detection in ROI with OpenVINO', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
