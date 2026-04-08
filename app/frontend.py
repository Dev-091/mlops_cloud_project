import streamlit as st
import requests
import cv2
from datetime import datetime
import time
import os

try:
    from app.detector import count_fingers
except ImportError:
    from detector import count_fingers

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="OpsVision | Cloud Controller",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism Title */
    .header-container {
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-title {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 1rem !important;
    }

    /* History Cards */
    .history-card {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #38bdf8;
        margin-bottom: 0.8rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
API_URL = "http://localhost:8000"

# --- STATE INITIALIZATION ---
def init_state():
    state_mapping = {
        "launch_history": [],
        "total_launched": 0,
        "last_auto_deploy_time": 0,
        "detected_count": 0,
        "system_status": "Ready",
        "api_healthy": False
    }
    for key, val in state_mapping.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# --- BACKEND HELPERS ---
def handle_deploy(count):
    if count <= 0:
        st.warning("No fingers detected! Please show your gesture.")
        return False
    try:
        resp = requests.post(f"{API_URL}/auto-scale", json={"count": count}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            rec = {
                "time": datetime.now().strftime("%I:%M:%S %p"),
                "count": data.get("count", 0),
                "ids": ", ".join(data.get("instance_ids", [])),
            }
            st.session_state.launch_history.insert(0, rec)
            st.session_state.total_launched += rec["count"]
            st.session_state.system_status = f"Success: {rec['count']} Deployed"
            st.toast(f"✅ Mission Success: {rec['count']} Instances Online")
            return True
        st.error(f"Backend Error: {resp.text}")
    except Exception as e:
        st.error(f"Connection Failed: {e}")
    return False

# --- UI HEADER ---
with st.container():
    st.markdown("""
        <div class="header-container">
            <h1 class="main-title">OpsVision Controller</h1>
            <p style="color: #64748b; margin-top: 5px;">⚡ Cloud Automation & Gesture Intel</p>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/cloud-checked.png", width=120)
    st.title("Control Center")
    st.divider()
    
    run_camera = st.toggle("🎥 Vision System", value=False)
    auto_deploy = st.toggle("🤖 Autonomous Mode", value=False)
    
    st.divider()
    
    # RELOCATED ACTION BUTTON: Always clickable if camera is on
    st.subheader("Action Manual")
    
    # We use a static label but handle the count from session state inside the function
    # This prevents the button from being "stuck" due to loop-blocking
    deploy_btn = st.button(
        "🚀 Deploy Gesture",
        disabled=(not run_camera),
        use_container_width=True,
        type="primary",
        help="Launches instances based on the current finger gesture detected."
    )
    
    if deploy_btn:
        eff_count = min(st.session_state.detected_count, 2)
        handle_deploy(eff_count)
        # Note: We don't call st.rerun here as the button click already triggered it
        # The script will continue to the end and restart.

    st.divider()
    st.info(f"**Status:** {st.session_state.system_status}")

# --- MAIN DASHBOARD LAYOUT ---
col_vision, col_ops = st.columns([1.6, 1])

with col_vision:
    st.markdown("### 👁️ Vision Intelligence")
    vision_frame = st.empty()
    if not run_camera:
        vision_frame.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=640", use_container_width=True, caption="Vision system offline")

with col_ops:
    st.markdown("### 📊 Operational Ops")
    
    # Metrics Row
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Active Assets", st.session_state.total_launched)
    
    # Targeting metric that updates live
    targeting_val = min(st.session_state.detected_count, 2)
    m_col2.metric("Targeting", f"{targeting_val} Unit" if targeting_val > 0 else "None")
    
    st.markdown("#### 📜 Launch Log")
    log_container = st.container(height=350)
    if not st.session_state.launch_history:
        log_container.caption("No recent operations found.")
    for record in st.session_state.launch_history:
        with log_container:
            st.markdown(f"""
                <div class="history-card">
                    <span style="font-size: 0.8rem; color: #94a3b8;">{record['time']}</span><br>
                    <strong>Deployed {record['count']} Instance(s)</strong><br>
                    <code style="font-size: 0.7rem;">{record['ids'][:40]}...</code>
                </div>
            """, unsafe_allow_html=True)

# --- COMPUTER VISION LOOP ---
def main_vision_loop():
    cap = cv2.VideoCapture(0)
    # Default camera settings for speed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    cooldown = 10
    frame_n = 0
    
    while run_camera and cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame_n += 1
        if frame_n % 2 == 0:
            count, landmarks = count_fingers(frame)
            st.session_state.detected_count = count
            
            # Interactive feedback in UI
            for _, cx, cy in landmarks:
                cv2.circle(frame, (cx, cy), 4, (248, 189, 56), -1) 
                
        # Simple Overlay for Camera
        cv2.rectangle(frame, (10, 10), (220, 60), (15, 23, 42), -1)
        cv2.putText(frame, f"G-ID: {st.session_state.detected_count}", (20, 45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (56, 189, 248), 2)
        
        vision_frame.image(frame, channels="BGR", use_container_width=True)
        
        # Autonomous Logic (Only if Mode is ON and detection is > 0)
        if auto_deploy and st.session_state.detected_count > 0:
            now = time.time()
            if (now - st.session_state.last_auto_deploy_time) > cooldown:
                eff = min(st.session_state.detected_count, 2)
                if handle_deploy(eff):
                    st.session_state.last_auto_deploy_time = now
        
        # This small sleep allows Streamlit to process UI events (like button clicks)
        time.sleep(0.01)
    
    cap.release()

if run_camera:
    main_vision_loop()
    # If the loop ends (e.g. user toggles off), we rerun to clear the vision_frame
    st.rerun()
