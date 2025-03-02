import cv2
from ultralytics import YOLO
# Load YOLO Model
model = YOLO("yolo11n.pt")  # Ensure your model file is correct

# RTSP Cameras
CAMS = {
    "cam0": 0,
    "cam1": "rtsp://admin:admin@192.168.235.148:1935",
    "cam2": "rtsp://admin:admin@192.168.235.254:1935",
    "test": "test.mp4",
}



def generate_frames(rtsp_url):
    """Function to capture RTSP video and apply YOLO object detection."""
    cap = cv2.VideoCapture(rtsp_url)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Run YOLO on Frame
        results = model(frame)

        # Draw Bounding Boxes and Labels
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()  # Convert to NumPy for indexing
            classes = r.boxes.cls.cpu().numpy()  # Extract class indices
            confs = r.boxes.conf.cpu().numpy()  # Extract confidence scores

            for box, cls, conf in zip(boxes, classes, confs):
                x1, y1, x2, y2 = map(int, box)  # Bounding box coordinates
                label = f"{model.names[int(cls)]} ({conf:.2f})"  # Class name + confidence
                
                # Draw Bounding Box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw Label
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Encode Frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
