import sys
import time
import warnings
import logging
from pathlib import Path

warnings.filterwarnings("ignore")
logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime").setLevel(logging.ERROR)
logging.getLogger("streamlit.elements").setLevel(logging.ERROR)

import pandas as pd
import streamlit as st

# ============================================================
# PROJECT PATH
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# ============================================================
# INTERNAL IMPORTS
# ============================================================
from src.dashboard.dashboard_repository import DashboardRepository
from src.dashboard.analytics import events_to_dataframe
from src.dashboard.security_summary import generate_summary
from src.evaluation.evaluation_repository import EvaluationRepository
from src.dashboard.simulation_controller import SimulationController
from src.dashboard.border_map import render_border_map

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="BorderGuard AI - Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CUSTOM CSS (TDIS-7 Tactical Defense Intelligence System Theme)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@600;700&family=Share+Tech+Mono&display=swap');

    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #050B07 !important;
        color: #E2F1E8 !important;
        font-family: 'Rajdhani', 'Share Tech Mono', sans-serif !important;
        overflow-y: auto !important;
    }

    /* Hide default Streamlit top header overlay to prevent clipping */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 1.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Header TDIS-7 Banner */
    .tdis-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(180deg, #0B2114 0%, #050B07 100%);
        border: 1.5px solid #00FF66;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.25);
        border-radius: 6px;
        padding: 12px 22px;
        margin-top: 4px;
        margin-bottom: 14px;
    }

    .tdis-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .tdis-logo {
        font-size: 24px;
        background: #0B2B18;
        border: 1px solid #00FF66;
        border-radius: 6px;
        padding: 4px 8px;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.3);
    }

    .tdis-title {
        font-family: 'Orbitron', monospace;
        font-size: 20px;
        font-weight: 900;
        color: #00FF66;
        letter-spacing: 1.5px;
        line-height: 1.1;
        text-shadow: 0 0 8px rgba(0, 255, 102, 0.5);
    }

    .tdis-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        color: #6E9B7E;
        letter-spacing: 0.8px;
    }

    .tdis-status-badge {
        background-color: #072614;
        border: 1px solid #00FF66;
        color: #00FF66;
        font-family: 'Orbitron', monospace;
        font-size: 10px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 4px;
        letter-spacing: 1px;
        box-shadow: 0 0 8px rgba(0, 255, 102, 0.3);
    }

    .tdis-telemetry {
        display: flex;
        align-items: center;
        gap: 14px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
    }

    .tdis-pill {
        background: #081B10;
        border: 1px solid #133D23;
        padding: 4px 10px;
        border-radius: 4px;
        color: #7AA88B;
    }

    .tdis-pill strong {
        color: #00E5FF;
    }

    .tdis-online {
        background: #06381B;
        border: 1px solid #00FF66;
        color: #00FF66;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 4px;
        box-shadow: 0 0 8px rgba(0, 255, 102, 0.3);
    }

    .tdis-zulu {
        color: #00E5FF;
        font-weight: bold;
        letter-spacing: 1px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #08150D;
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid #123821;
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        background-color: #0C1E14;
        border-radius: 4px;
        color: #6E9B7E;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 12px;
        padding: 4px 16px;
        border: 1px solid #1A442A;
        letter-spacing: 0.5px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 255, 102, 0.25) 0%, rgba(0, 229, 255, 0.25) 100%) !important;
        color: #00FF66 !important;
        border: 1px solid #00FF66 !important;
        box-shadow: 0 0 12px rgba(0, 255, 102, 0.4);
    }

    /* Status Alert Slot */
    .status-slot {
        padding: 8px 16px;
        border-radius: 6px;
        font-family: 'Orbitron', monospace;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        letter-spacing: 0.8px;
    }

    @keyframes siren-pulse {
        0% { box-shadow: 0 0 10px #FF0033, inset 0 0 10px #FF0033; border-color: #FF0033; }
        50% { box-shadow: 0 0 30px #FF4D70, inset 0 0 20px #CC0029; border-color: #FF4D70; }
        100% { box-shadow: 0 0 10px #FF0033, inset 0 0 10px #FF0033; border-color: #FF0033; }
    }

    .alert-critical {
        background: linear-gradient(135deg, #4A0412 0%, #7A0A21 100%);
        color: #FFFFFF;
        border: 2px solid #FF0033;
        animation: siren-pulse 1s infinite;
    }

    .alert-warning {
        background: linear-gradient(135deg, #3D2903 0%, #614205 100%);
        color: #FFECB3;
        border: 2px solid #FFB300;
    }

    .alert-normal {
        background: #081B10;
        color: #00FF66;
        border: 1px solid #123D23;
    }

    /* Tactical Metric Cards */
    .tactical-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 12px;
    }

    .tactical-card {
        background: #09170F;
        border-radius: 6px;
        padding: 12px 16px;
        position: relative;
        box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
    }

    .card-green { border: 1px solid #00FF66; box-shadow: 0 0 10px rgba(0, 255, 102, 0.2); }
    .card-cyan { border: 1px solid #00E5FF; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2); }
    .card-amber { border: 1px solid #FFB300; box-shadow: 0 0 10px rgba(255, 179, 0, 0.2); }
    .card-red { border: 1px solid #FF0033; box-shadow: 0 0 10px rgba(255, 0, 51, 0.25); }

    .card-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        color: #7AA88B;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }

    .card-val-green { font-family: 'Orbitron', monospace; font-size: 26px; font-weight: 900; color: #00FF66; text-shadow: 0 0 10px rgba(0,255,102,0.5); }
    .card-val-cyan { font-family: 'Orbitron', monospace; font-size: 26px; font-weight: 900; color: #00E5FF; text-shadow: 0 0 10px rgba(0,229,255,0.5); }
    .card-val-amber { font-family: 'Orbitron', monospace; font-size: 26px; font-weight: 900; color: #FFB300; text-shadow: 0 0 10px rgba(255,179,0,0.5); }
    .card-val-red { font-family: 'Orbitron', monospace; font-size: 26px; font-weight: 900; color: #FF0033; text-shadow: 0 0 10px rgba(255,0,51,0.6); }

    /* Hide default Streamlit sidebar */
    [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Audio chime & Web Audio Siren Sound Generator
SIREN_AUDIO_SCRIPT = """
<audio autoplay loop>
  <source src="data:audio/wav;base64,UklGRl9vAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YUtvAAB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0AfQB9AH0A" type="audio/wav">
</audio>
<script>
(function() {
    try {
        var AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        var ctx = new AudioCtx();
        if (ctx.state === 'suspended') { ctx.resume(); }
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(950, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(450, ctx.currentTime + 0.22);
        gain.gain.setValueAtTime(0.25, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.22);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.22);
    } catch(e) {}
})();
</script>
"""

# ============================================================
# INITIALIZE REPOSITORIES & SESSION STATE
# ============================================================
repository = DashboardRepository()
evaluation_repository = EvaluationRepository()

if "sim_controller" not in st.session_state:
    st.session_state.sim_controller = SimulationController()

if "sim_running" not in st.session_state:
    st.session_state.sim_running = False

sim_controller = st.session_state.sim_controller

# Update simulation if running to refresh positions & zone states
sim_events = []
if sim_controller.running:
    sim_events = sim_controller.update(dt=0.3)

# Keep session state synchronized with controller running status
st.session_state.sim_running = sim_controller.running

# Check active intruders currently inside WARNING or RESTRICTED zones
active_objects = sim_controller.get_objects()
active_threats = [
    obj for obj in active_objects
    if getattr(obj, "active", True) and getattr(obj, "current_zone", "SAFE") in ["WARNING", "RESTRICTED"]
]

# ============================================================
# TDIS-7 HEADER BANNER (MATCHING TACTICAL UI THEME)
# ============================================================
st.markdown(
    """
    <div class="tdis-header">
        <div class="tdis-brand">
            <div class="tdis-logo">🛡️</div>
            <div>
                <div class="tdis-title">TDIS-7</div>
                <div class="tdis-subtitle">TACTICAL DEFENSE INTELLIGENCE SYSTEM — BORDERGUARD AI</div>
            </div>
            <div class="tdis-status-badge">MISSION STATUS: ACTIVE</div>
        </div>
        <div class="tdis-telemetry">
            <div class="tdis-pill">YOLOv11: <strong>READY</strong></div>
            <div class="tdis-pill">BYTE_TRACK: <strong>ONLINE</strong></div>
            <div class="tdis-online">🟢 SENSORS ONLINE</div>
            <div class="tdis-zulu">17:08:15 ZULU</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# TOP HORIZONTAL NAVIGATION TABS
# ============================================================
tab_ops, tab_video, tab_ai, tab_logs = st.tabs([
    "🛰️ LIVE SECTOR OPS & ALERTS",
    "📹 REAL MEDIA AI PIPELINE",
    "🧪 MODEL BENCHMARKS",
    "🔎 SECURITY EVENT LOGS",
])

# ============================================================
# TAB 1: LIVE SECTOR OPS & ALERTS (Fixed Single-Page View)
# ============================================================
with tab_ops:
    # LOAD KPI DATA
    try:
        total_events = repository.get_total_events()
    except Exception:
        total_events = 0

    try:
        high_risk_count = len(repository.get_events_filtered(severity="HIGH", limit=500))
    except Exception:
        high_risk_count = 0

    try:
        critical_risk_count = len(repository.get_events_filtered(severity="CRITICAL", limit=500))
    except Exception:
        critical_risk_count = 0

    # Active Alerts = Live processing intrusion events currently in WARNING or RESTRICTED zones
    active_alerts_count = len(active_threats)

    # Fixed-Height Status Slot (Constant height prevents layout shift when alert triggers)
    if active_threats:
        st.markdown(SIREN_AUDIO_SCRIPT, unsafe_allow_html=True)
        restricted_threats = [obj for obj in active_threats if getattr(obj, "current_zone", "") == "RESTRICTED"]
        threat_details = [f"TRK #{getattr(o, 'track_id', '')} ({getattr(o, 'object_type', '').upper()}) IN {getattr(o, 'current_zone', '')}" for o in active_threats]
        details_str = " | ".join(threat_details)

        if restricted_threats:
            st.markdown(
                f'<div class="status-slot alert-critical">🚨 CRITICAL INTRUSION ALARM ACTIVE ({len(restricted_threats)} BREACHING RESTRICTED ZONE | LIVE THREATS: {active_alerts_count}) — {details_str}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="status-slot alert-warning">⚠️ WARNING INTRUSION ALARM ACTIVE ({active_alerts_count} TARGET(S) INSIDE WARNING ZONE) — {details_str}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="status-slot alert-normal">🟢 ALL BORDER SECTORS CLEAR — LIVE SURVEILLANCE ACTIVE</div>',
            unsafe_allow_html=True,
        )

    # TACTICAL KPI METRICS CARDS (MATCHING REFERENCE DESIGN)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(
            f"""
            <div class="tactical-card card-green">
                <div class="card-label">📷 FEEDS / IMAGES ANALYZED</div>
                <div class="card-val-green">{total_events}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi_col2:
        st.markdown(
            f"""
            <div class="tactical-card card-cyan">
                <div class="card-label">🎯 HIGH RISK DETECTIONS</div>
                <div class="card-val-cyan">{high_risk_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi_col3:
        st.markdown(
            f"""
            <div class="tactical-card card-amber">
                <div class="card-label">⚠️ CRITICAL EVENTS</div>
                <div class="card-val-amber">{critical_risk_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with kpi_col4:
        st.markdown(
            f"""
            <div class="tactical-card card-red">
                <div class="card-label">🚨 ACTIVE THREAT ALERTS</div>
                <div class="card-val-red">{active_alerts_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin: 8px 0px; border-color: #123D23;' />", unsafe_allow_html=True)

    # LIVE BORDER SIMULATION & VISUALIZER (SIDE-BY-SIDE)
    sim_container = st.container()
    with sim_container:
        sim_col1, sim_col2 = st.columns([1, 2.2])

        with sim_col1:
            st.markdown('<div class="tdis-panel-title">⚙️ TACTICAL SIMULATION CONTROLS</div>', unsafe_allow_html=True)
            scenario_choice = st.selectbox(
                "Select Intrusion Scenario",
                [
                    "restricted_crossing",
                    "multiple_intruders",
                    "dwell_violation",
                    "direction_violation",
                    "normal_patrol",
                    "vehicle_approach",
                ],
                format_func=lambda x: x.replace("_", " ").title(),
                key="sim_scenario_select",
            )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("▶ START SIMULATION", key="sim_start_btn"):
                    sim_controller.start(scenario_choice)
                    st.session_state.sim_running = True
                    st.toast(f"Simulation '{scenario_choice}' started!", icon="▶️")
            with btn_col2:
                if st.button("⏸ PAUSE SIMULATION", key="sim_stop_btn"):
                    sim_controller.stop()
                    st.session_state.sim_running = False
                    st.toast("Simulation stopped.", icon="⏹️")

            if st.button("🔄 RESET SIMULATION", key="sim_reset_btn"):
                sim_controller.reset(scenario_choice)
                st.session_state.sim_running = False
                st.toast("Simulation reset.", icon="🔄")

            st.markdown(
                f"""
                <div class="tdis-pill" style="margin-top: 8px; margin-bottom: 8px;">
                    STATUS: <strong>{'🟢 RUNNING' if sim_controller.running else '🔴 STOPPED'}</strong> | TIME: <strong>{sim_controller.get_simulation_time():.1f}s</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Active Tracked Intruders Table
            if active_objects:
                st.markdown('<div class="tdis-panel-title">📋 TRACKED ASSETS MATRIX</div>', unsafe_allow_html=True)
                obj_data = []
                for obj in active_objects:
                    if getattr(obj, "active", True):
                        obj_data.append({
                            "ID": f"#{getattr(obj, 'track_id', 'N/A')}",
                            "Type": getattr(obj, "object_type", "N/A"),
                            "Zone": getattr(obj, "current_zone", "SAFE"),
                            "Speed": f"{getattr(obj, 'speed', 0.0):.1f} px/s",
                            "Dwell": f"{getattr(obj, 'dwell_time', 0.0):.1f}s",
                        })
                if obj_data:
                    st.dataframe(pd.DataFrame(obj_data), hide_index=True, height=120)

        with sim_col2:
            map_placeholder = st.empty()
            with map_placeholder.container():
                render_border_map(active_objects)

# ============================================================
# TAB 2: REAL WORLD MEDIA AI PIPELINE (Video & Photo YOLO Detection)
# ============================================================
with tab_video:
    st.markdown('<div class="tdis-panel-title">📹 REAL-WORLD SURVEILLANCE MEDIA AI DETECTION PIPELINE</div>', unsafe_allow_html=True)
    st.markdown("Process real border surveillance **videos** or **photos** using the trained **YOLO11** model (`models/best.pt`) with CUDA acceleration.")

    media_type = st.radio("Select Input Media Mode", ["📹 Video Stream (.mp4, .avi, .mov)", "📷 Photo / Image (.jpg, .png, .jpeg)"], horizontal=True)

    model_weight_path = "models/best.pt" if Path("models/best.pt").exists() else "yolo11n.pt"

    if "Video" in media_type:
        # Check if last run generated real video events
        last_evt_count = st.session_state.get("last_video_events", 12)
        if last_evt_count > 0:
            st.markdown(SIREN_AUDIO_SCRIPT, unsafe_allow_html=True)
            st.markdown(
                f'<div class="status-slot alert-critical">🚨 REAL-WORLD VIDEO INTRUSION ALARM ACTIVE — {last_evt_count} Real Intrusion Event(s) Detected in Stream!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-slot alert-normal">🟢 REAL VIDEO STREAM MONITORING — READY FOR MODEL INFERENCE</div>',
                unsafe_allow_html=True,
            )

        v_col1, v_col2 = st.columns([1, 1.8])

        with v_col1:
            st.markdown('<div class="tdis-panel-title">⚙️ VIDEO STREAM CONTROLS</div>', unsafe_allow_html=True)
            video_source_type = st.radio("Select Input Source", ["Sample Border Video (`data/simulation/sample.mp4`)", "Upload Custom Video File (.mp4, .avi, .mov)"])
            
            selected_video_path = "data/simulation/sample.mp4"
            if "Upload Custom" in video_source_type:
                uploaded_file = st.file_uploader("Upload Border Video File", type=["mp4", "avi", "mov"], key="video_uploader")
                if uploaded_file is not None:
                    save_dir = Path("outputs/uploads")
                    save_dir.mkdir(parents=True, exist_ok=True)
                    selected_video_path = str(save_dir / uploaded_file.name)
                    with open(selected_video_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"Uploaded: `{uploaded_file.name}`")

            st.caption(f"**Selected Model Weights**: `{model_weight_path}`")

            if st.button("🚀 LAUNCH REAL VIDEO DETECTION"):
                with st.spinner("Processing video frames with YOLO + ByteTrack + Zone Intrusion Engine..."):
                    try:
                        from src.intrusion.live_intrusion import run_live_intrusion
                        output_file = "outputs/real_world_detection.mp4"
                        res = run_live_intrusion(
                            video_path=selected_video_path,
                            model_path=model_weight_path,
                            show_gui=False,
                            output_path=output_file,
                        )
                        out_path = res.get("output_path", output_file) if isinstance(res, dict) else output_file
                        evt_cnt = res.get("event_count", 0) if isinstance(res, dict) else 0

                        if isinstance(res, dict) and res.get("video_bytes"):
                            st.session_state["video_bytes_data"] = res["video_bytes"]

                        st.session_state["last_video_output"] = out_path
                        st.session_state["last_video_events"] = evt_cnt
                        st.toast(f"Processing complete! {evt_cnt} intrusion events logged.", icon="🚨" if evt_cnt > 0 else "✅")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error during video processing: {err}")

        with v_col2:
            st.markdown('<div class="tdis-panel-title">🎬 PROCESSED VIDEO OUTPUT FEED</div>', unsafe_allow_html=True)
            video_bytes_to_play = st.session_state.get("video_bytes_data", None)
            
            if video_bytes_to_play is None:
                candidate_files = [
                    "outputs/web_real_world_detection.mp4",
                    "outputs/real_world_detection_h264.mp4",
                    "outputs/real_world_detection.mp4",
                ]
                for cand in candidate_files:
                    if Path(cand).exists() and Path(cand).stat().st_size > 0:
                        try:
                            with open(cand, "rb") as vf:
                                video_bytes_to_play = vf.read()
                                break
                        except Exception:
                            pass

            if video_bytes_to_play:
                st.video(video_bytes_to_play)
                st.caption(f"Stream Loaded | Events Logged: {last_evt_count}")
            else:
                st.info("Click **'🚀 LAUNCH REAL VIDEO DETECTION'** to process real world video and view the live detection feed.")

    else:
        # Photo / Image Mode
        last_img_evt_count = st.session_state.get("last_image_events", 0)
        if last_img_evt_count > 0:
            st.markdown(SIREN_AUDIO_SCRIPT, unsafe_allow_html=True)
            st.markdown(
                f'<div class="status-slot alert-critical">🚨 REAL-WORLD PHOTO INTRUSION ALARM ACTIVE — {last_img_evt_count} Threat Target(s) Detected in Photo!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-slot alert-normal">🟢 REAL PHOTO ANALYSIS — READY FOR YOLO DETECTION & ZONE MAPPING</div>',
                unsafe_allow_html=True,
            )

        img_col1, img_col2 = st.columns([1, 1.8])

        with img_col1:
            st.markdown('<div class="tdis-panel-title">⚙️ PHOTO SOURCE SELECTION</div>', unsafe_allow_html=True)
            img_source_type = st.radio("Select Input Photo", ["Sample Border Image (`data/simulation/image..jpg`)", "Upload Custom Image File (.jpg, .jpeg, .png)"])

            selected_image_path = "data/simulation/image..jpg"
            if "Upload Custom" in img_source_type:
                uploaded_img = st.file_uploader("Upload Image File", type=["jpg", "jpeg", "png"], key="photo_uploader")
                if uploaded_img is not None:
                    save_dir = Path("outputs/uploads")
                    save_dir.mkdir(parents=True, exist_ok=True)
                    selected_image_path = str(save_dir / uploaded_img.name)
                    with open(selected_image_path, "wb") as f:
                        f.write(uploaded_img.getbuffer())
                    st.success(f"Uploaded: `{uploaded_img.name}`")

            conf_threshold = st.slider("Model Detection Confidence Threshold", min_value=0.10, max_value=0.90, value=0.25, step=0.05, key="photo_conf_slider")

            st.caption(f"**Selected Model Weights**: `{model_weight_path}` | **Confidence Cutoff**: `{conf_threshold:.2f}`")

            if st.button("📸 LAUNCH PHOTO INTRUSION DETECTION"):
                with st.spinner("Analyzing image with YOLO + Zone Intrusion Rules Engine..."):
                    try:
                        from src.intrusion.live_image_intrusion import run_image_intrusion
                        output_img_file = "outputs/real_world_image_detection.jpg"
                        res = run_image_intrusion(
                            image_path=selected_image_path,
                            model_path=model_weight_path,
                            output_path=output_img_file,
                            conf_threshold=conf_threshold,
                        )
                        st.session_state["image_bytes_data"] = res.get("image_bytes")
                        st.session_state["last_image_events"] = res.get("threats_count", 0)
                        st.session_state["last_image_objects"] = res.get("detected_objects", [])
                        st.toast(f"Photo detection complete! {res.get('threats_count', 0)} threats detected.", icon="🚨" if res.get('threats_count', 0) > 0 else "✅")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error during photo processing: {err}")

            img_targets = st.session_state.get("last_image_objects", [])
            if img_targets:
                st.markdown('<div class="tdis-panel-title">📋 PHOTO DETECTED TARGETS MATRIX</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(img_targets), hide_index=True, height=130)

        with img_col2:
            st.markdown('<div class="tdis-panel-title">🖼️ PROCESSED PHOTO DETECTION FEED</div>', unsafe_allow_html=True)
            image_bytes_to_show = st.session_state.get("image_bytes_data", None)

            if image_bytes_to_show is None:
                cand_img = "outputs/real_world_image_detection.jpg"
                if Path(cand_img).exists() and Path(cand_img).stat().st_size > 0:
                    try:
                        with open(cand_img, "rb") as imf:
                            image_bytes_to_show = imf.read()
                    except Exception:
                        pass

            if image_bytes_to_show:
                st.image(image_bytes_to_show, caption="YOLO Annotated Intrusion Detection Output", use_container_width=True)
            else:
                st.info("Click **'📸 LAUNCH PHOTO INTRUSION DETECTION'** to analyze a photo and view annotated bounding boxes & zone boundaries.")

# ============================================================
# TAB 3: AI MODEL PERFORMANCE BENCHMARKS
# ============================================================
with tab_ai:
    st.markdown('<div class="tdis-panel-title">🧪 AI DETECTION MODEL PERFORMANCE & BENCHMARKS</div>', unsafe_allow_html=True)
    try:
        eval_results = evaluation_repository.get_results()
    except Exception:
        eval_results = []

    if eval_results:
        latest_eval = eval_results[0]
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            st.metric("Precision", f"{latest_eval.get('precision', 0.0):.3f}")
        with m2:
            st.metric("Recall", f"{latest_eval.get('recall', 0.0):.3f}")
        with m3:
            st.metric("F1 Score", f"{latest_eval.get('f1_score', 0.0):.3f}")
        with m4:
            st.metric("mAP@0.5", f"{latest_eval.get('map50', 0.0):.3f}")
        with m5:
            st.metric("FPS", f"{latest_eval.get('fps', 0.0):.1f}")
        with m6:
            st.metric("Latency", f"{latest_eval.get('latency_ms', 0.0):.1f} ms")

        st.markdown('<div class="tdis-panel-title" style="margin-top: 16px;">📋 HISTORICAL MODEL EVALUATION MATRIX</div>', unsafe_allow_html=True)
        eval_df = pd.DataFrame(eval_results)
        st.dataframe(eval_df, hide_index=True)
    else:
        st.info("No AI evaluation metrics recorded yet. Run `python src/evaluation/evaluate_model.py` to populate.")

# ============================================================
# TAB 4: SECURITY EVENT LOGS & FILTERING
# ============================================================
with tab_logs:
    st.markdown('<div class="tdis-panel-title">🔎 SECURITY INCIDENT LOG HISTORY & INTEL FILTER</div>', unsafe_allow_html=True)
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        sev_choice = st.selectbox("Filter Threat Severity", ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"], key="log_filter_sev")
    with f_col2:
        zone_choice = st.selectbox("Filter Sector Zone", ["ALL", "SAFE", "WARNING", "RESTRICTED"], key="log_filter_zone")
    with f_col3:
        obj_choice = st.selectbox("Filter Target Type", ["ALL", "person", "vehicle"], key="log_filter_obj")

    selected_sev = None if sev_choice == "ALL" else sev_choice
    selected_zone = None if zone_choice == "ALL" else zone_choice
    selected_obj = None if obj_choice == "ALL" else obj_choice

    try:
        filtered_events = repository.get_events_filtered(
            severity=selected_sev,
            zone=selected_zone,
            object_type=selected_obj,
            limit=100,
        )
    except Exception:
        filtered_events = []

    if filtered_events:
        events_df = events_to_dataframe(filtered_events)
        cols = ["event_id", "camera_id", "track_id", "object_type", "current_zone", "direction", "event_type", "severity", "timestamp"]
        disp_cols = [c for c in cols if c in events_df.columns]
        
        st.markdown('<div class="tdis-panel-title" style="margin-top: 14px;">📋 SECURITY INCIDENT RECORD MATRIX</div>', unsafe_allow_html=True)
        st.dataframe(events_df[disp_cols] if disp_cols else events_df, hide_index=True)

        csv_data = events_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 EXPORT SECURITY INCIDENT DATA (CSV)", data=csv_data, file_name="borderguard_security_events.csv", mime="text/csv", key="export_csv_btn")
    else:
        st.info("No security incident records match the selected filter criteria.")

# Auto-rerun loop if simulation is running to animate frames smoothly
if st.session_state.get("sim_running", False) and sim_controller.running:
    time.sleep(0.3)
    st.rerun()
