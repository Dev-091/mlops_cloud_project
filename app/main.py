# app/main.py
import os
import time
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from app.detector import count_fingers
from app.ec2_manager import launch_ec2_instances
from app.mlflow_setup import log_inference

app = FastAPI(title="Finger-to-EC2 MLOps API")

class InstanceRequest(BaseModel):
    count: int

@app.get("/health")
def health():
    return {"status": "ok", "service": "finger-ec2-mlops"}

@app.post("/detect")
async def detect_fingers(file: UploadFile = File(...)):
    start = time.time()
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        count, _ = count_fingers(frame)
        latency = round((time.time() - start) * 1000, 2)
        log_inference(count, latency)
        return {"finger_count": count, "latency_ms": latency}
    except Exception as e:
        log_inference(-1, -1, "error")
        raise HTTPException(400, str(e))

@app.post("/auto-scale")
async def auto_scale(req: InstanceRequest):
    count = max(1, min(req.count, int(os.getenv("MAX_INSTANCES", "2"))))
    start_time = time.time()
    instance_ids = []
    status = "success"
    
    try:
        result = launch_ec2_instances(count)
        instance_ids = result.get("instance_ids", [])
        latency = round((time.time() - start_time) * 1000, 2)
        log_inference(count, latency, status, instance_ids)
        return result
    except Exception as e:
        latency = round((time.time() - start_time) * 1000, 2)
        log_inference(count, latency, "failed", [])
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)