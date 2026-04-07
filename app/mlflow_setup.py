# app/mlflow_setup.py
import os
import mlflow

# Point MLflow to a local folder (creates mlruns/ in project root)
MLFLOW_TRACKING_URI = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mlruns")
mlflow.set_tracking_uri(f"file:///{MLFLOW_TRACKING_URI}")
mlflow.set_experiment("finger-ec2-mlops")

def log_inference(count: int, latency_ms: float, status: str = "success", instance_ids: list = None):
    with mlflow.start_run():
        mlflow.log_param("finger_count", count)
        mlflow.log_param("ec2_launch_status", status)
        mlflow.log_metric("inference_latency_ms", latency_ms)
        if instance_ids:
            mlflow.log_param("launched_instance_ids", ",".join(instance_ids))