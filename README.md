# MLOps Cloud Project

> Finger-to-EC2 is a hands-on MLOps demo that detects finger counts from a webcam frame, logs inference metrics with MLflow, and can launch EC2 instances based on the result through a FastAPI backend.

## At a Glance

| Layer | Tech |
| --- | --- |
| Computer Vision | OpenCV, MediaPipe |
| API | FastAPI, Uvicorn |
| Cloud | AWS EC2, Boto3 |
| MLOps | MLflow |
| Frontend | Streamlit |
| Testing | Pytest, Moto |

## What You Can Do

- Detect hand or finger count from an uploaded image or webcam frame.
- Send the detected count to an EC2 autoscaling flow.
- Track inference latency and deployment events with MLflow.
- Use a Streamlit dashboard for live camera interaction and manual or automatic deployment.

## Project Layout

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI service with `/health`, `/detect`, and `/auto-scale` endpoints |
| `app/detector.py` | Finger-counting logic powered by MediaPipe and OpenCV |
| `app/ec2_manager.py` | EC2 launch helper with dry-run validation |
| `app/frontend.py` | Streamlit interface for camera capture and deployment control |
| `app/mlflow_setup.py` | MLflow logging utilities |
| `tests/` | Unit and integration-style tests |
| `.github/workflows/ci.yml` | CI pipeline for linting, tests, and Docker build |

## Quick Start

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure Environment

Create a `.env` file if you want to use AWS-backed deployment:

```env
AWS_DEFAULT_REGION=us-east-1
EC2_IMAGE_ID=ami-xxxxxxxxxxxxxxxxx
EC2_INSTANCE_TYPE=t2.micro
AUTO_TERMINATE_MINUTES=30
MAX_INSTANCES=2
```

Keep cloud credentials and other secrets out of version control.

## Run the Backend

```powershell
uvicorn app.main:app --reload
```

Available API endpoints:

- `GET /health`
- `POST /detect`
- `POST /auto-scale`

## Run the Frontend

```powershell
streamlit run app/frontend.py
```

The frontend expects the API to be available at `http://localhost:8000`.

## Run Tests

```powershell
pytest
```

## Docker

Build the image:

```powershell
docker build -t mlops-cloud-project .
```

Run with Docker Compose:

```powershell
docker compose up --build
```

## Notes

- `mlruns/`, `mlflow.db`, `venv/`, and `.env` are ignored so local artifacts and secrets stay out of GitHub.
- The EC2 launch flow performs a dry-run first, then launches for real when permissions and quotas allow it.
- The UI is designed to support both manual deployment and auto-deploy behavior from the detected finger count.
