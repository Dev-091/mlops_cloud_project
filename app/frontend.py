import streamlit as st
import requests
import cv2
from datetime import datetime
import time

# Set a professional wide layout
st.set_page_config(page_title="Finger-to-EC2 Ops", page_icon="☁️", layout="wide")

# Custom CSS for a beautiful look
st.markdown(
    """
<style>
    .main-header {
        font-family: 'Inter', sans-serif;
        color: #1e3a8a;
        font-weight: 700;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .status-text {
        color: #059669;
        font-weight: 600;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 class='main-header'>🖐️ Finger-to-EC2 Ops Console</h1>", unsafe_allow_html=True
)

API_URL = "http://localhost:8000"

# Initialize Session State
if "launch_history" not in st.session_state:
    st.session_state.launch_history = []
if "total_launched" not in st.session_state:
    st.session_state.total_launched = 0
if "last_auto_deploy_time" not in st.session_state:
    st.session_state.last_auto_deploy_time = 0
if "detected_count" not in st.session_state:
    st.session_state.detected_count = 0

col1, col2 = st.columns([1.5, 1])


def handle_deploy(count):
    if count <= 0:
        return False
    try:
        launch_resp = requests.post(f"{API_URL}/auto-scale", json={"count": count})
        if launch_resp.status_code == 200:
            launch_data = launch_resp.json()
            rec = {
                "time": datetime.now().strftime("%I:%M:%S %p"),
                "count": launch_data.get("count", 0),
                "ids": ", ".join(launch_data.get("instance_ids", [])),
                "status": launch_data.get("status", "success"),
            }
            st.session_state.launch_history.insert(0, rec)
            st.session_state.total_launched += rec["count"]
            return True
        else:
            st.error(f"Launch failed: {launch_resp.text}")
            return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False


with col1:
    st.subheader("📷 Live Camera Feed")
    run_camera = st.toggle("Activate Tracking Camera", value=False, key="run_cam")
    auto_deploy = st.toggle("⚡ Enable Auto Deploy Mode", value=False, key="auto_dep")

    frame_placeholder = st.empty()
    status_placeholder = st.empty()

    # Manual Deploy Button (Outside the loop to avoid Duplicate ID error)
    if not auto_deploy:
        if st.button(
            f"🚀 Deploy {st.session_state.detected_count} Instance(s)",
            key="manual_deploy",
            type="primary",
        ):
            if handle_deploy(st.session_state.detected_count):
                st.rerun()


def app_loop():
    cap = cv2.VideoCapture(0)
    auto_deploy_cooldown = 10  # seconds

    while st.session_state.run_cam and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Send frame for detection
        _, encoded = cv2.imencode(".jpg", frame)
        try:
            resp = requests.post(
                f"{API_URL}/detect",
                files={"file": ("img.jpg", encoded.tobytes(), "image/jpeg")},
            )
            if resp.status_code == 200:
                data = resp.json()
                count = data["finger_count"]
                st.session_state.detected_count = (
                    count  # Update session state for the manual button
                )

                # Visuals
                cv2.putText(
                    frame,
                    f"Fingers: {count}",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 255, 100),
                    3,
                )
                frame_placeholder.image(frame, channels="BGR", use_container_width=True)

                # Auto Deploy Logic
                if auto_deploy and count > 0:
                    current_time = time.time()
                    if (
                        current_time - st.session_state.last_auto_deploy_time
                    ) > auto_deploy_cooldown:
                        status_placeholder.warning(
                            f"⚡ Auto-Triggering {count} instances!"
                        )
                        if handle_deploy(count):
                            st.session_state.last_auto_deploy_time = current_time
                            # We can't st.rerun here as it kills the loop process
                            # But the state is updated, so next loop or interaction will show it.
                    else:
                        wait = int(
                            auto_deploy_cooldown
                            - (current_time - st.session_state.last_auto_deploy_time)
                        )
                        status_placeholder.info(
                            f"Targeting {count} | Cooldown: {wait}s"
                        )
                else:
                    status_placeholder.empty()

            else:
                frame_placeholder.error("API Error")
        except Exception:
            frame_placeholder.error("Backend unreachable")
            break

        time.sleep(0.05)

    cap.release()


with col2:
    st.subheader("📊 Deployment Overview")
    st.markdown(
        f"""
    <div class="metric-card">
        <h4 style="margin: 0; color: #475569;">Total Servers Deployed</h4>
        <h1 style="margin: 0; color: #2563eb; font-size: 3rem;">{st.session_state.total_launched}</h1>
        <span class="status-text">● System operational</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("🕒 Launch History")
    history_container = st.container(height=500)
    for idx, record in enumerate(st.session_state.launch_history):
        with history_container.expander(
            f"Deploy [{record['time']}] - {record['count']} instance(s)",
            expanded=(idx == 0),
        ):
            st.code(f"Instance IDs:\n{record['ids']}", language="text")

# Execution Entry Point
if run_camera:
    app_loop()
else:
    frame_placeholder.info("Ready. Activate camera to start.")
