import streamlit as st
import pandas as pd
from dashboard.border_map import render_border_map


def render_simulation(objects=None):
    """
    Renders border sector canvas and table of active objects.
    """
    if objects is None:
        objects = []

    st.markdown("### 🛰️ Live Border Sector Visualizer")
    render_border_map(objects)

    st.markdown("### 📋 Active Tracked Objects")
    active_list = [obj for obj in objects if getattr(obj, "active", True)]

    if active_list:
        data = []
        for obj in active_list:
            data.append(
                {
                    "Track ID": getattr(obj, "track_id", "N/A"),
                    "Object Type": getattr(obj, "object_type", "N/A"),
                    "X Pos": f"{getattr(obj, 'x', 0.0):.1f}",
                    "Y Pos": f"{getattr(obj, 'y', 0.0):.1f}",
                    "Zone": getattr(obj, "current_zone", "NONE"),
                    "Direction": getattr(obj, "direction", "STATIONARY"),
                    "Speed": f"{getattr(obj, 'speed', 0.0):.1f} px/s",
                }
            )
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("No active objects currently present in the sector.")
