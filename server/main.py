from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from yolo_utils import generate_frames, CAMS
import torch

app = FastAPI()

@app.post("/add_camera/{cam_id}")
async def add_camera(cam_id: str, rtsp_url: str):
    """API route to add a new RTSP camera to the server."""
    if cam_id in CAMS:
        return {"error": "Camera ID already exists"}
    
    CAMS[cam_id] = rtsp_url
    return {"message": "Camera added successfully"}

@app.delete("/remove_camera/{cam_id}")
async def remove_camera(cam_id: str):
    """API route to remove an RTSP camera from the server."""
    if cam_id not in CAMS:
        return {"error": "Invalid camera ID"}
    
    del CAMS[cam_id]
    return {"message": "Camera removed successfully"}

@app.get("/cameras")
async def get_cameras():
    """API route to get all available cameras."""
    return CAMS



@app.get("/video/{cam_id}")
async def video_feed(cam_id: str):
    """API route to stream YOLO-processed video from RTSP camera."""
    if cam_id not in CAMS:
        return {"error": "Invalid camera ID"}
    
    return StreamingResponse(generate_frames(CAMS[cam_id]), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/")
async def root():
    """Root endpoint to verify server is running."""
    return {"message": "YOLO RTSP Stream Running", 
            "gpu_status": "GPU Available" if torch.cuda.is_available() else "GPU Not Available", 
            "model_status": "Model Loaded",
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

