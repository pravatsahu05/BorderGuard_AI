import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR / "src" / "zones"))
sys.path.append(str(BASE_DIR))

import time

import cv2
import numpy as np

try:
    from zones.zone_manager import ZoneManager
    from zones.border_config import ZONES
except ImportError:
    from zone_manager import ZoneManager
    from border_config import ZONES



class SimulationRenderer:
    """
    Renders the software border simulation.
    """

    def __init__(
        self,
        width=960,
        height=540,
    ):

        self.width = width

        self.height = height

        self.zone_manager = ZoneManager(ZONES)

    def create_frame(self):

        frame = cv2.imread("data/simulation/background.jpg")

        if frame is None:

            frame = 30 * np.ones(
                (
                    self.height,
                    self.width,
                    3,
                ),
                dtype=np.uint8,
            )

        frame = cv2.resize(
            frame,
            (
                self.width,
                self.height,
            ),
        )

        return frame

    def draw_objects(
        self,
        frame,
        objects,
        zone_states,
    ):

        for obj in objects:

            x = int(obj.x)

            y = int(obj.y)

            # ------------------------------------------------
            # Draw simulated object.
            # ------------------------------------------------

            radius = 14

            cv2.circle(
                frame,
                (x, y),
                radius,
                (255, 255, 255),
                -1,
            )

            cv2.circle(
                frame,
                (x, y),
                radius,
                (0, 0, 0),
                2,
            )

            # ------------------------------------------------
            # Track ID.
            # ------------------------------------------------

            cv2.putText(
                frame,
                (f"{obj.object_type} " f"#{obj.track_id}"),
                (x + 20, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            # ------------------------------------------------
            # Zone information.
            # ------------------------------------------------

            state = zone_states.get(obj.track_id)

            if state:

                zone = state.current_zone

                dwell = zone_states.get_dwell_time(
                    obj.track_id,
                    __import__("time").time(),
                )

                cv2.putText(
                    frame,
                    f"Zone: {zone}",
                    (x + 20, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                cv2.putText(
                    frame,
                    f"Dwell: {dwell:.1f}s",
                    (x + 20, y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

    def draw_header(
        self,
        frame,
        scenario_name,
    ):

        cv2.putText(
            frame,
            "BORDERGUARD AI",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "SOFTWARE BORDER SIMULATION",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        cv2.putText(
            frame,
            f"Scenario: {scenario_name}",
            (650, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

    def render(
        self,
        objects,
        zone_states,
        scenario_name,
    ):

        frame = self.create_frame()

        self.zone_manager.draw_zones(frame)

        self.draw_header(
            frame,
            scenario_name,
        )

        self.draw_objects(
            frame,
            objects,
            zone_states,
        )

        return frame
