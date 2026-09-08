import matplotlib.pyplot as plt
import matplotlib.patches as patches
import streamlit as st


def render_border_map(objects=None):
    """
    Renders 2D Border-Sector Visualization canvas displaying active simulated objects.
    """
    if objects is None:
        objects = []

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=100)
    fig.patch.set_facecolor("#1A1D24")
    ax.set_facecolor("#1A1D24")

    # Sector Zone Boundaries (Video resolution 960x540)
    # SAFE Zone (Y: 0 to 180)
    safe_box = patches.Rectangle((0, 0), 960, 180, linewidth=1, edgecolor="#28A745", facecolor="#28A745", alpha=0.25)
    ax.add_patch(safe_box)
    ax.text(480, 90, "🟢 SAFE ZONE", color="#28A745", fontsize=12, fontweight="bold", ha="center", va="center")

    # WARNING Zone (Y: 180 to 350)
    warn_box = patches.Rectangle((0, 180), 960, 170, linewidth=1, edgecolor="#FFC107", facecolor="#FFC107", alpha=0.25)
    ax.add_patch(warn_box)
    ax.text(480, 265, "⚠️ WARNING ZONE", color="#FFC107", fontsize=12, fontweight="bold", ha="center", va="center")

    # RESTRICTED Zone (Y: 350 to 540)
    rest_box = patches.Rectangle((0, 350), 960, 190, linewidth=1, edgecolor="#DC3545", facecolor="#DC3545", alpha=0.25)
    ax.add_patch(rest_box)
    ax.text(480, 445, "🚨 RESTRICTED ZONE", color="#DC3545", fontsize=12, fontweight="bold", ha="center", va="center")

    # Plot Active Tracked Objects
    for obj in objects:
        if not getattr(obj, "active", True):
            continue

        x = getattr(obj, "x", 0.0)
        y = getattr(obj, "y", 0.0)
        track_id = getattr(obj, "track_id", "N/A")
        obj_type = getattr(obj, "object_type", "person")
        vx = getattr(obj, "vx", 0.0)
        vy = getattr(obj, "vy", 0.0)

        color = "#00D2FF" if obj_type == "person" else "#E040FB"
        marker = "o" if obj_type == "person" else "s"

        ax.scatter(x, y, color=color, s=140, marker=marker, edgecolors="#FFFFFF", linewidths=1.5, zorder=5)
        ax.text(x + 12, y - 10, f"TRK-{track_id} ({obj_type})", color="#FFFFFF", fontsize=9, fontweight="bold", zorder=6)

        # Velocity direction arrow
        if abs(vx) > 0.1 or abs(vy) > 0.1:
            ax.arrow(x, y, vx * 0.4, vy * 0.4, head_width=12, head_length=10, fc=color, ec=color, zorder=5)

    ax.set_xlim(0, 960)
    ax.set_ylim(540, 0)  # Inverted Y for image coordinate standard
    ax.set_title("🛡️ Live Border Sector Monitoring Canvas", color="#FFFFFF", fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("Sector Distance X (meters)", color="#8E9AA8", fontsize=9)
    ax.set_ylabel("Sector Depth Y (meters)", color="#8E9AA8", fontsize=9)
    ax.tick_params(colors="#8E9AA8", labelsize=8)

    for spine in ax.spines.values():
        spine.set_color("#2A2F3D")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
