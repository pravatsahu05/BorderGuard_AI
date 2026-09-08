import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# INTERNAL IMPORTS
# ============================================================

from src.dashboard.dashboard_repository import (
    DashboardRepository,
)

from src.dashboard.analytics import (
    events_to_dataframe,
    risk_distribution_dataframe,
    zone_distribution_dataframe,
    event_type_dataframe,
)

from src.dashboard.security_summary import (
    generate_summary,
)

from src.evaluation.evaluation_repository import (
    EvaluationRepository,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BorderGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 16px;
        opacity: 0.75;
        margin-bottom: 20px;
    }

    .status-box {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INITIALIZE REPOSITORIES
# ============================================================

repository = DashboardRepository()

evaluation_repository = EvaluationRepository()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛡️ BorderGuard AI")

st.sidebar.caption("Security Command Center")

st.sidebar.divider()


page = st.sidebar.radio(
    "Select View",
    [
        "Command Center",
        "Security Events",
        "Alerts",
        "AI Evaluation",
        "System Status",
    ],
)


st.sidebar.divider()

st.sidebar.caption("MODE: SOFTWARE SIMULATION")

st.sidebar.caption("Automated Border Intrusion Detection")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">' "🛡️ BORDERGUARD AI" "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Automated Border Intrusion Detection "
    "using Thermal-Visible Fusion"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# LOAD KPI DATA
# ============================================================

try:

    total_events = repository.get_total_events()

except Exception:

    total_events = 0


try:

    high_risk = repository.get_high_risk_events()

except Exception:

    high_risk = 0


try:

    critical_risk = repository.get_critical_events()

except Exception:

    critical_risk = 0


try:

    active_alerts = repository.get_active_alerts()

except Exception:

    active_alerts = 0


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":

    st.header("🎯 Security Command Center")

    # --------------------------------------------------------
    # SYSTEM SUMMARY
    # --------------------------------------------------------

    summary = generate_summary(
        total_events=total_events,
        high_risk=high_risk,
        critical_events=critical_risk,
        active_alerts=active_alerts,
    )

    st.info(summary)

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Security Events",
            total_events,
        )

    with col2:

        st.metric(
            "High Risk Events",
            high_risk,
        )

    with col3:

        st.metric(
            "Critical Events",
            critical_risk,
        )

    with col4:

        st.metric(
            "Active Alerts",
            active_alerts,
        )

    # --------------------------------------------------------
    # SYSTEM MODE
    # --------------------------------------------------------

    st.divider()

    mode_col1, mode_col2 = st.columns(2)

    with mode_col1:

        st.success("🟢 Simulation Engine")

    with mode_col2:

        st.info("ℹ️ Software Simulation Mode")

    # --------------------------------------------------------
    # RISK ANALYTICS
    # --------------------------------------------------------

    st.divider()

    st.subheader("📊 Risk Analytics")

    try:

        risk_distribution = repository.get_risk_distribution()

        risk_df = risk_distribution_dataframe(risk_distribution)

        if not risk_df.empty:

            st.bar_chart(risk_df.set_index("Severity"))

        else:

            st.info("No risk data available.")

    except Exception as error:

        st.warning("Unable to load risk analytics.")

        st.caption(str(error))

    # --------------------------------------------------------
    # ZONE ANALYTICS
    # --------------------------------------------------------

    st.subheader("🗺️ Zone Activity")

    try:

        zone_distribution = repository.get_zone_distribution()

        zone_df = zone_distribution_dataframe(zone_distribution)

        if not zone_df.empty:

            st.bar_chart(zone_df.set_index("Zone"))

        else:

            st.info("No zone activity recorded.")

    except Exception as error:

        st.warning("Unable to load zone analytics.")

        st.caption(str(error))

    # --------------------------------------------------------
    # EVENT TYPE ANALYTICS
    # --------------------------------------------------------

    st.subheader("📈 Event Type Distribution")

    try:

        event_type_distribution = repository.get_event_type_distribution()

        event_type_df = event_type_dataframe(event_type_distribution)

        if not event_type_df.empty:

            st.bar_chart(event_type_df.set_index("Event Type"))

        else:

            st.info("No event-type data available.")

    except Exception as error:

        st.warning("Unable to load event-type analytics.")

        st.caption(str(error))

    # --------------------------------------------------------
    # EVENT TIMELINE
    # --------------------------------------------------------

    st.subheader("⏱️ Security Event Timeline")

    try:

        timeline = repository.get_event_timeline()

        timeline_df = pd.DataFrame(timeline)

        if not timeline_df.empty:

            timeline_df["timestamp"] = pd.to_datetime(timeline_df["timestamp"])

            timeline_df = timeline_df.set_index("timestamp")

            st.line_chart(timeline_df["event_count"])

        else:

            st.info("No event timeline available.")

    except Exception as error:

        st.warning("Unable to load event timeline.")

        st.caption(str(error))


# ============================================================
# SECURITY EVENTS
# ============================================================

elif page == "Security Events":

    st.header("🔎 Security Event History")

    # --------------------------------------------------------
    # FILTER VALUES
    # --------------------------------------------------------

    try:

        severity_values = repository.get_distinct_values("severity")

    except Exception:

        severity_values = []

    try:

        zone_values = repository.get_distinct_values("current_zone")

    except Exception:

        zone_values = []

    try:

        object_values = repository.get_distinct_values("object_type")

    except Exception:

        object_values = []

    # --------------------------------------------------------
    # FILTER UI
    # --------------------------------------------------------

    filter1, filter2, filter3 = st.columns(3)

    with filter1:

        severity_filter = st.selectbox(
            "Severity",
            ["ALL"] + severity_values,
        )

    with filter2:

        zone_filter = st.selectbox(
            "Current Zone",
            ["ALL"] + zone_values,
        )

    with filter3:

        object_filter = st.selectbox(
            "Object Type",
            ["ALL"] + object_values,
        )

    # --------------------------------------------------------
    # CONVERT FILTER VALUES
    # --------------------------------------------------------

    selected_severity = None if severity_filter == "ALL" else severity_filter

    selected_zone = None if zone_filter == "ALL" else zone_filter

    selected_object = None if object_filter == "ALL" else object_filter

    # --------------------------------------------------------
    # LOAD FILTERED EVENTS
    # --------------------------------------------------------

    try:

        filtered_events = repository.get_events_filtered(
            severity=(selected_severity),
            zone=(selected_zone),
            object_type=(selected_object),
            limit=100,
        )

    except Exception as error:

        st.error("Unable to load security events.")

        st.exception(error)

        filtered_events = []

    # --------------------------------------------------------
    # EVENT COUNT
    # --------------------------------------------------------

    st.divider()

    count_col1, count_col2 = st.columns(2)

    with count_col1:

        st.metric(
            "Matching Events",
            len(filtered_events),
        )

    with count_col2:

        st.metric(
            "Total Events",
            total_events,
        )

    # --------------------------------------------------------
    # EVENT TABLE
    # --------------------------------------------------------

    filtered_events_df = events_to_dataframe(filtered_events)

    if filtered_events_df.empty:

        st.info("No events match the " "selected filters.")

    else:

        display_columns = [
            "event_id",
            "camera_id",
            "track_id",
            "object_type",
            "previous_zone",
            "current_zone",
            "direction",
            "event_type",
            "severity",
            "timestamp",
        ]

        available_columns = [
            column for column in display_columns if column in filtered_events_df.columns
        ]

        if available_columns:

            st.dataframe(
                filtered_events_df[available_columns],
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.dataframe(
                filtered_events_df,
                use_container_width=True,
                hide_index=True,
            )

        # ----------------------------------------------------
        # CSV EXPORT
        # ----------------------------------------------------

        csv_data = filtered_events_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=("📥 Export Events as CSV"),
            data=csv_data,
            file_name=("borderguard_events.csv"),
            mime="text/csv",
        )


# ============================================================
# ALERTS
# ============================================================

elif page == "Alerts":

    st.header("🚨 Alert Center")

    # --------------------------------------------------------
    # ALERT KPI
    # --------------------------------------------------------

    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:

        st.metric(
            "Active Alerts",
            active_alerts,
        )

    with alert_col2:

        st.metric(
            "Critical Events",
            critical_risk,
        )

    st.divider()

    # --------------------------------------------------------
    # ALERT EVENTS
    # --------------------------------------------------------

    try:

        alert_events = repository.get_events_filtered(
            severity="CRITICAL",
            limit=100,
        )

    except Exception:

        alert_events = []

    if not alert_events:

        st.success("🟢 No critical alerts " "currently recorded.")

    else:

        st.warning("🚨 Critical security " "events detected.")

        alert_df = events_to_dataframe(alert_events)

        st.dataframe(
            alert_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# AI EVALUATION
# ============================================================

elif page == "AI Evaluation":

    st.header("🧪 AI Model Evaluation")

    st.caption("Performance evaluation of the " "BorderGuard AI detection system")

    st.divider()

    # --------------------------------------------------------
    # LOAD RESULTS
    # --------------------------------------------------------

    try:

        evaluation_results = evaluation_repository.get_results()

    except Exception as error:

        st.error("Unable to load evaluation results.")

        st.exception(error)

        evaluation_results = []

    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

    if not evaluation_results:

        st.info("No model evaluation results " "are available yet.")

        st.markdown(
            """
            ### Evaluation pipeline

            Once the actual detection model
            is evaluated, this page will show:

            - Precision
            - Recall
            - F1 Score
            - Mean IoU
            - mAP@0.5
            - mAP@0.5:0.95
            - FPS
            - Latency

            The values should come from actual
            model experiments rather than manually
            entered or estimated values.
            """
        )

    else:

        evaluation_df = pd.DataFrame(evaluation_results)

        # ----------------------------------------------------
        # LATEST RESULT
        # ----------------------------------------------------

        latest = evaluation_results[0]

        st.subheader("📊 Latest Evaluation")

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:

            value = latest.get("precision")

            st.metric(
                "Precision",
                (
                    f"{value:.3f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with metric2:

            value = latest.get("recall")

            st.metric(
                "Recall",
                (
                    f"{value:.3f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with metric3:

            value = latest.get("f1_score")

            st.metric(
                "F1 Score",
                (
                    f"{value:.3f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with metric4:

            value = latest.get("mean_iou")

            st.metric(
                "Mean IoU",
                (
                    f"{value:.3f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        # ----------------------------------------------------
        # MAP / SPEED
        # ----------------------------------------------------

        st.subheader("⚡ Detection & Runtime Performance")

        metric5, metric6, metric7, metric8 = st.columns(4)

        with metric5:

            value = latest.get("map50")

            st.metric(
                "mAP@0.5",
                (
                    f"{value:.3f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with metric6:

            value = latest.get("map5095")

            st.metric(
                "mAP@0.5:0.95",
                (
                    f"{value:.3f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with metric7:

            value = latest.get("fps")

            st.metric(
                "FPS",
                (
                    f"{value:.2f}"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        with metric8:

            value = latest.get("latency_ms")

            st.metric(
                "Latency",
                (
                    f"{value:.2f} ms"
                    if isinstance(
                        value,
                        (int, float),
                    )
                    else "N/A"
                ),
            )

        # ----------------------------------------------------
        # COMPLETE EVALUATION HISTORY
        # ----------------------------------------------------

        st.divider()

        st.subheader("📋 Evaluation History")

        st.dataframe(
            evaluation_df,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # MODEL COMPARISON
        # ----------------------------------------------------

        if "model_name" in evaluation_df.columns:

            st.subheader("📈 Model Comparison")

            comparison_columns = [
                "model_name",
                "precision",
                "recall",
                "f1_score",
                "mean_iou",
                "map50",
                "map5095",
                "fps",
                "latency_ms",
            ]

            available_comparison_columns = [
                column
                for column in comparison_columns
                if column in evaluation_df.columns
            ]

            if available_comparison_columns:

                st.dataframe(
                    evaluation_df[available_comparison_columns],
                    use_container_width=True,
                    hide_index=True,
                )

        # ----------------------------------------------------
        # EVALUATION CSV
        # ----------------------------------------------------

        evaluation_csv = evaluation_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=("📥 Export Evaluation Results"),
            data=evaluation_csv,
            file_name=("borderguard_evaluation.csv"),
            mime="text/csv",
        )


# ============================================================
# SYSTEM STATUS
# ============================================================

elif page == "System Status":

    st.header("⚙️ System Status")

    st.caption("Current software pipeline status")

    st.divider()

    # --------------------------------------------------------
    # STATUS CARDS
    # --------------------------------------------------------

    status1, status2 = st.columns(2)

    with status1:

        st.success("🟢 Database")

    with status2:

        st.success("🟢 Event Pipeline")

    status3, status4 = st.columns(2)

    with status3:

        st.success("🟢 Dashboard")

    with status4:

        st.info("🟡 Simulation Mode")

    st.divider()

    # --------------------------------------------------------
    # PROJECT PIPELINE
    # --------------------------------------------------------

    st.subheader("🔗 Processing Pipeline")

    pipeline = [
        "1. Input / Simulation",
        "2. Detection",
        "3. Tracking",
        "4. Zone Analysis",
        "5. Intrusion Detection",
        "6. Risk Assessment",
        "7. Alert Generation",
        "8. Event Storage",
        "9. Analytics",
        "10. Dashboard",
    ]

    for stage in pipeline:

        st.write(f"✅ {stage}")

    st.divider()

    # --------------------------------------------------------
    # DATABASE STATISTICS
    # --------------------------------------------------------

    st.subheader("📊 Database Statistics")

    db1, db2, db3 = st.columns(3)

    with db1:

        st.metric(
            "Total Events",
            total_events,
        )

    with db2:

        st.metric(
            "High Risk",
            high_risk,
        )

    with db3:

        st.metric(
            "Critical",
            critical_risk,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "BorderGuard AI • Automated Border "
    "Intrusion Detection • "
    "Software Simulation Prototype"
)
