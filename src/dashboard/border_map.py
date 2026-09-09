import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import streamlit as st


def render_border_map(objects=None, container=None):
    """
    Renders TDIS-7 Tactical 2D Border-Sector Visualization canvas.
    """
    if objects is None:
        objects = []

    fig, ax = plt.subplots(figsize=(7.8, 3.1), dpi=100)
    fig.patch.set_facecolor("#050B07")
    ax.set_facecolor("#050B07")

    # Tactical Sector Grid Overlay
    ax.grid(True, which="both", color="#0E2E1B", linestyle="--", linewidth=0.7, alpha=0.7, zorder=1)

    # Sector Zone Boundaries (Video resolution 960x540)
    # SAFE Zone (Y: 0 to 180)
    safe_box = patches.Rectangle((0, 0), 960, 180, linewidth=1.5, edgecolor="#00FF66", facecolor="#032110", alpha=0.4, zorder=2)
    ax.add_patch(safe_box)
    ax.text(480, 90, "SAFE ZONE (SECTOR PATROL)", color="#00FF66", fontsize=11, fontweight="bold", family="monospace", ha="center", va="center", zorder=3)

    # WARNING Zone (Y: 180 to 350)
    warn_box = patches.Rectangle((0, 180), 960, 170, linewidth=1.5, edgecolor="#FFB300", facecolor="#291F03", alpha=0.4, zorder=2)
    ax.add_patch(warn_box)
    ax.text(480, 265, "WARNING ZONE (BUFFER PERIMETER)", color="#FFB300", fontsize=11, fontweight="bold", family="monospace", ha="center", va="center", zorder=3)

    # RESTRICTED Zone (Y: 350 to 540)
    rest_box = patches.Rectangle((0, 350), 960, 190, linewidth=1.5, edgecolor="#FF0033", facecolor="#300812", alpha=0.45, zorder=2)
    ax.add_patch(rest_box)
    ax.text(480, 445, "RESTRICTED ZONE (CRITICAL BREACH)", color="#FF0033", fontsize=11, fontweight="bold", family="monospace", ha="center", va="center", zorder=3)

    # Threat Assessment Level Badge (Top Left of Radar Canvas)
    restricted_count = sum(1 for o in objects if getattr(o, "active", True) and getattr(o, "current_zone", "") == "RESTRICTED")
    warning_count = sum(1 for o in objects if getattr(o, "active", True) and getattr(o, "current_zone", "") == "WARNING")

    if restricted_count > 0:
        badge_text = f"● THREAT: CRITICAL ({restricted_count} BREACH)"
        badge_color = "#FF0033"
        badge_bg = "#3A0512"
    elif warning_count > 0:
        badge_text = f"● THREAT: WARNING ({warning_count} ACTIVE)"
        badge_color = "#FFB300"
        badge_bg = "#3A2805"
    else:
        badge_text = "● THREAT: NOMINAL (CLEAR)"
        badge_color = "#00FF66"
        badge_bg = "#052912"

    badge = patches.FancyBboxPatch((20, 15), 230, 32, boxstyle="round,pad=3,rounding_size=5", edgecolor=badge_color, facecolor=badge_bg, linewidth=1.5, zorder=10)
    ax.add_patch(badge)
    ax.text(135, 31, badge_text, color=badge_color, fontsize=9.5, fontweight="bold", family="monospace", ha="center", va="center", zorder=11)

    # Plot Active Tracked Objects with Radar Rings
    active_objs = [o for o in objects if getattr(o, "active", True)]
    for obj in active_objs:
        x = getattr(obj, "x", 0.0)
        y = getattr(obj, "y", 0.0)
        track_id = getattr(obj, "track_id", "N/A")
        obj_type = getattr(obj, "object_type", "person").upper()
        current_zone = getattr(obj, "current_zone", "SAFE")
        vx = getattr(obj, "vx", 0.0)
        vy = getattr(obj, "vy", 0.0)

        if current_zone == "RESTRICTED":
            color = "#FF0033"
        elif current_zone == "WARNING":
            color = "#FFB300"
        else:
            color = "#00E5FF"

        # Outer radar target halo
        ax.scatter(x, y, color=color, s=260, alpha=0.35, zorder=5)
        ax.scatter(x, y, color=color, s=120, marker="o", edgecolors="#FFFFFF", linewidths=1.5, zorder=6)
        
        # Crosshair ring
        circle = patches.Circle((x, y), radius=22, linewidth=1, edgecolor=color, facecolor="none", linestyle=":", zorder=6)
        ax.add_patch(circle)

        # Label tag
        ax.text(x + 14, y - 10, f"TRK-{track_id} | {obj_type}", color="#FFFFFF", fontsize=8.5, fontweight="bold", family="monospace", zorder=7)

        # Velocity direction arrow
        if abs(vx) > 0.1 or abs(vy) > 0.1:
            ax.arrow(x, y, vx * 0.45, vy * 0.45, head_width=14, head_length=12, fc=color, ec=color, linewidth=1.2, zorder=6)

    ax.set_xlim(0, 960)
    ax.set_ylim(540, 0)  # Inverted Y for image coordinate standard
    ax.set_title("LIVE BORDER SECTOR VISUALIZER — REAL-TIME ASSET TRACKING", color="#00FF66", fontsize=11, fontweight="bold", family="monospace", pad=12)
    ax.set_xlabel("Sector Distance X (meters)", color="#00E5FF", fontsize=8.5, family="monospace")
    ax.set_ylabel("Sector Depth Y (meters)", color="#00E5FF", fontsize=8.5, family="monospace")
    ax.tick_params(colors="#6A8F76", labelsize=8)

    for spine in ax.spines.values():
        spine.set_color("#0E3A20")
        spine.set_linewidth(1.2)

    plt.tight_layout()
    if container is not None:
        container.pyplot(fig)
    else:
        st.pyplot(fig)
    plt.close(fig)
